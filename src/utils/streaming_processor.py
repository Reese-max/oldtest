#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
流式處理器
實現記憶體高效的流式PDF處理，避免大文件記憶體溢出
"""

import gc
import os
from contextlib import contextmanager
from dataclasses import dataclass
from typing import Any, Callable, Dict, Iterator, List, Optional

import pdfplumber
import psutil

from ..utils.exceptions import PDFProcessingError
from .logger import logger

# Memory monitoring constants
DEFAULT_MEMORY_LIMIT_MB = 512  # Default memory limit in MB
MEMORY_CHECK_INTERVAL = 10  # Check memory every N pages
GC_THRESHOLD_MB = 256  # Trigger GC when memory exceeds this


@dataclass
class StreamConfig:
    """流式處理配置"""

    chunk_size: int = 10  # 每次處理的頁數
    memory_limit_mb: int = DEFAULT_MEMORY_LIMIT_MB  # 記憶體限制（MB）
    enable_monitoring: bool = True  # 啟用記憶體監控
    auto_gc: bool = True  # 自動垃圾回收
    gc_interval: int = MEMORY_CHECK_INTERVAL  # GC 觸發間隔


@dataclass
class PageChunk:
    """頁面區塊"""

    pages: List[int]  # 頁面編號列表
    text: str  # 提取的文字
    metadata: Dict[str, Any]  # 元數據


class MemoryMonitor:
    """記憶體監控器"""

    def __init__(self, limit_mb: int = DEFAULT_MEMORY_LIMIT_MB):
        """
        初始化記憶體監控器

        Args:
            limit_mb: 記憶體限制（MB）
        """
        self.limit_mb = limit_mb
        self.limit_bytes = limit_mb * 1024 * 1024
        self.process = psutil.Process(os.getpid())
        self.peak_memory = 0

    def get_current_memory_mb(self) -> float:
        """
        獲取當前記憶體使用量（MB）

        Returns:
            當前記憶體使用量（MB）
        """
        memory_info = self.process.memory_info()
        current_mb = memory_info.rss / 1024 / 1024
        self.peak_memory = max(self.peak_memory, current_mb)
        return current_mb

    def check_memory_limit(self) -> bool:
        """
        檢查是否超過記憶體限制

        Returns:
            是否超過限制
        """
        current_mb = self.get_current_memory_mb()
        exceeded = current_mb > self.limit_mb

        if exceeded:
            logger.warning(f"⚠️  記憶體使用超過限制: {current_mb:.1f}MB / {self.limit_mb}MB")

        return exceeded

    def should_trigger_gc(self, threshold_mb: int = GC_THRESHOLD_MB) -> bool:
        """
        判斷是否應該觸發垃圾回收

        Args:
            threshold_mb: 觸發閾值（MB）

        Returns:
            是否應該觸發 GC
        """
        return self.get_current_memory_mb() > threshold_mb

    def force_gc(self):
        """強制執行垃圾回收"""
        before_mb = self.get_current_memory_mb()
        gc.collect()
        after_mb = self.get_current_memory_mb()
        freed_mb = before_mb - after_mb

        logger.debug(f"🧹 執行垃圾回收: {before_mb:.1f}MB → {after_mb:.1f}MB " f"(釋放 {freed_mb:.1f}MB)")

        return freed_mb

    def get_stats(self) -> Dict[str, float]:
        """
        獲取記憶體統計信息

        Returns:
            統計信息字典
        """
        current_mb = self.get_current_memory_mb()
        return {
            "current_mb": current_mb,
            "peak_mb": self.peak_memory,
            "limit_mb": self.limit_mb,
            "usage_percent": (current_mb / self.limit_mb) * 100 if self.limit_mb > 0 else 0,
        }


class StreamingPDFProcessor:
    """流式 PDF 處理器 - 記憶體高效的頁面處理"""

    def __init__(self, config: Optional[StreamConfig] = None):
        """
        初始化流式處理器

        Args:
            config: 流式處理配置
        """
        self.config = config or StreamConfig()
        self.memory_monitor = MemoryMonitor(self.config.memory_limit_mb)
        self.logger = logger

    def stream_pages(self, pdf_path: str, start_page: int = 1, end_page: Optional[int] = None) -> Iterator[PageChunk]:
        """
        流式處理 PDF 頁面（生成器）

        Args:
            pdf_path: PDF 檔案路徑
            start_page: 起始頁碼（從 1 開始）
            end_page: 結束頁碼（None 表示處理到最後）

        Yields:
            PageChunk: 頁面區塊

        Example:
            ```python
            processor = StreamingPDFProcessor()
            for chunk in processor.stream_pages("large.pdf"):
                # 處理每個區塊
                process_text(chunk.text)
                # chunk 被處理後會自動釋放記憶體
            ```
        """
        if not os.path.exists(pdf_path):
            raise PDFProcessingError(f"PDF檔案不存在: {pdf_path}")

        self.logger.info(f"開始流式處理PDF: {pdf_path}")

        try:
            with pdfplumber.open(pdf_path) as pdf:
                total_pages = len(pdf.pages)
                end_page = end_page or total_pages
                end_page = min(end_page, total_pages)

                self.logger.info(f"PDF總頁數: {total_pages}, " f"處理範圍: {start_page}-{end_page}")

                # 按區塊處理
                for chunk_start in range(start_page - 1, end_page, self.config.chunk_size):
                    chunk_end = min(chunk_start + self.config.chunk_size, end_page)

                    # 記憶體檢查
                    if self.config.enable_monitoring:
                        if self.memory_monitor.check_memory_limit():
                            self.logger.warning("記憶體限制達到，停止處理")
                            break

                        # 自動 GC
                        if self.config.auto_gc and self.memory_monitor.should_trigger_gc():
                            self.memory_monitor.force_gc()

                    # 提取區塊文字
                    chunk_text = ""
                    chunk_pages = []

                    for page_idx in range(chunk_start, chunk_end):
                        page_num = page_idx + 1
                        chunk_pages.append(page_num)

                        try:
                            page = pdf.pages[page_idx]
                            page_text = page.extract_text() or ""

                            # Unicode 處理
                            page_text = self._clean_text(page_text)
                            chunk_text += page_text + "\n"

                            self.logger.debug(f"處理頁面 {page_num}/{total_pages}")

                        except Exception as e:
                            self.logger.warning(f"頁面 {page_num} 處理失敗: {e}")
                            continue

                    # 生成區塊
                    chunk = PageChunk(
                        pages=chunk_pages,
                        text=chunk_text,
                        metadata={
                            "total_pages": total_pages,
                            "chunk_start": chunk_start + 1,
                            "chunk_end": chunk_end,
                            "memory_mb": self.memory_monitor.get_current_memory_mb(),
                        },
                    )

                    yield chunk

                    # 顯式清理
                    del chunk_text

                # 最終統計
                stats = self.memory_monitor.get_stats()
                self.logger.success(
                    f"✅ 流式處理完成 - "
                    f"峰值記憶體: {stats['peak_mb']:.1f}MB, "
                    f"當前記憶體: {stats['current_mb']:.1f}MB"
                )

        except Exception as e:
            error_msg = f"流式處理失敗: {e}"
            self.logger.failure(error_msg)
            raise PDFProcessingError(error_msg) from e

    def process_with_callback(
        self, pdf_path: str, callback: Callable[[PageChunk], Any], start_page: int = 1, end_page: Optional[int] = None
    ) -> List[Any]:
        """
        使用回調函數處理 PDF

        Args:
            pdf_path: PDF 檔案路徑
            callback: 處理回調函數
            start_page: 起始頁碼
            end_page: 結束頁碼

        Returns:
            處理結果列表

        Example:
            ```python
            def process_chunk(chunk):
                # 從區塊提取題目
                return extract_questions(chunk.text)

            results = processor.process_with_callback(
                "exam.pdf",
                process_chunk
            )
            ```
        """
        results = []

        for chunk in self.stream_pages(pdf_path, start_page, end_page):
            try:
                result = callback(chunk)
                results.append(result)
            except Exception as e:
                self.logger.error(f"回調處理失敗: {e}")
                results.append(None)

        return results

    def extract_text_streaming(self, pdf_path: str, output_callback: Optional[Callable[[str], None]] = None) -> str:
        """
        流式提取文字（適合大文件）

        Args:
            pdf_path: PDF 檔案路徑
            output_callback: 輸出回調（接收每個區塊的文字）

        Returns:
            完整文字（如果記憶體允許）

        Note:
            如果文件非常大，建議使用 output_callback 將文字寫入文件，
            而不是返回完整字串
        """
        full_text = []

        for chunk in self.stream_pages(pdf_path):
            if output_callback:
                # 使用回調處理，不累積在記憶體中
                output_callback(chunk.text)
            else:
                # 累積文字
                full_text.append(chunk.text)

        return "".join(full_text) if full_text else ""

    def _clean_text(self, text: str) -> str:
        """
        清理文字中的特殊字符

        Args:
            text: 原始文字

        Returns:
            清理後的文字
        """
        try:
            text = text.encode("utf-8", errors="ignore").decode("utf-8")
            text = text.replace("\x00", "").replace("\ufeff", "")
        except UnicodeError as e:
            self.logger.warning(f"Unicode 清理失敗: {e}")

        return text


@contextmanager
def memory_efficient_processing(memory_limit_mb: int = DEFAULT_MEMORY_LIMIT_MB):
    """
    記憶體高效處理上下文管理器

    Args:
        memory_limit_mb: 記憶體限制（MB）

    Example:
        ```python
        with memory_efficient_processing(memory_limit_mb=512):
            # 在此區塊內的處理會受記憶體限制保護
            process_large_pdf("huge.pdf")
        ```
    """
    monitor = MemoryMonitor(memory_limit_mb)
    before_mb = monitor.get_current_memory_mb()

    logger.info(f"開始記憶體高效處理 - 限制: {memory_limit_mb}MB")

    try:
        yield monitor
    finally:
        # 清理
        monitor.force_gc()
        after_mb = monitor.get_current_memory_mb()
        stats = monitor.get_stats()

        logger.info(
            f"記憶體處理完成 - "
            f"開始: {before_mb:.1f}MB, "
            f"結束: {after_mb:.1f}MB, "
            f"峰值: {stats['peak_mb']:.1f}MB"
        )


def create_streaming_processor(
    chunk_size: int = 10, memory_limit_mb: int = DEFAULT_MEMORY_LIMIT_MB, enable_monitoring: bool = True
) -> StreamingPDFProcessor:
    """
    創建流式處理器的便捷函數

    Args:
        chunk_size: 區塊大小（頁數）
        memory_limit_mb: 記憶體限制（MB）
        enable_monitoring: 啟用記憶體監控

    Returns:
        流式處理器實例
    """
    config = StreamConfig(chunk_size=chunk_size, memory_limit_mb=memory_limit_mb, enable_monitoring=enable_monitoring)
    return StreamingPDFProcessor(config)
