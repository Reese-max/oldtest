#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF處理器
負責從PDF檔案中提取文字內容
"""

import os
import pdfplumber
from typing import Optional, List
from ..utils.logger import logger
from ..utils.exceptions import PDFProcessingError

# PDF processing constants
DEFAULT_MAX_PAGES = 200  # Default maximum pages to process (防止大文件記憶體溢出)
MEMORY_CLEANUP_INTERVAL = 50  # Trigger garbage collection every N pages
MAX_PAGES_WARNING_THRESHOLD = 10000  # Warn if max_pages exceeds this value


class PDFProcessor:
    """PDF處理器"""
    
    def __init__(self):
        self.logger = logger
    
    def extract_text(self, pdf_path: str, max_pages: int = DEFAULT_MAX_PAGES) -> str:
        """
        從PDF檔案中提取文字內容

        Args:
            pdf_path: PDF檔案路徑
            max_pages: 最大處理頁數，預設為 DEFAULT_MAX_PAGES（防止大文件記憶體溢出）

        Returns:
            提取的文字內容

        Raises:
            PDFProcessingError: PDF處理失敗時拋出
        """
        # 輸入驗證
        self._validate_pdf_path(pdf_path)
        self._validate_max_pages(max_pages)

        if not os.path.exists(pdf_path):
            raise PDFProcessingError(f"PDF檔案不存在: {pdf_path}")

        try:
            self.logger.info(f"開始處理PDF檔案: {pdf_path}")

            with pdfplumber.open(pdf_path) as pdf:
                text = ""
                total_pages = len(pdf.pages)

                # 警告大文件
                if total_pages > max_pages:
                    self.logger.warning(
                        f"⚠️  PDF檔案過大（{total_pages} 頁），僅處理前 {max_pages} 頁"
                    )

                # 限制處理頁數
                pages_to_process = min(total_pages, max_pages)

                for page_num, page in enumerate(pdf.pages[:pages_to_process], 1):
                    try:
                        page_text = page.extract_text()
                        if page_text:
                            # 處理特殊 Unicode 字符，避免編碼錯誤
                            try:
                                page_text = page_text.encode('utf-8', errors='ignore').decode('utf-8')
                                # 移除常見的問題字符
                                page_text = page_text.replace('\x00', '').replace('\ufeff', '')
                            except UnicodeError as ue:
                                self.logger.warning(f"第 {page_num} 頁 Unicode 清理失敗: {ue}")
                            text += page_text + "\n"

                        # 每處理 MEMORY_CLEANUP_INTERVAL 頁釋放一次記憶體
                        if page_num % MEMORY_CLEANUP_INTERVAL == 0:
                            import gc
                            gc.collect()
                            self.logger.debug(f"已處理 {page_num} 頁，觸發記憶體清理")

                        self.logger.debug(f"處理第 {page_num}/{pages_to_process} 頁")
                    except Exception as e:
                        self.logger.warning(f"第 {page_num} 頁處理失敗: {e}")
                        continue

                self.logger.success(
                    f"✅ PDF文字提取完成，共處理 {pages_to_process}/{total_pages} 頁，{len(text)} 字元"
                )
                return text

        except Exception as e:
            error_msg = f"PDF處理失敗: {e}"
            self.logger.failure(error_msg)
            raise PDFProcessingError(error_msg) from e
    
    def extract_text_from_pages(self, pdf_path: str, page_numbers: List[int]) -> str:
        """
        從指定頁面提取文字內容

        Args:
            pdf_path: PDF檔案路徑
            page_numbers: 要提取的頁面編號列表

        Returns:
            提取的文字內容
        """
        # 輸入驗證
        self._validate_pdf_path(pdf_path)
        self._validate_page_numbers(page_numbers)

        if not os.path.exists(pdf_path):
            raise PDFProcessingError(f"PDF檔案不存在: {pdf_path}")
        
        try:
            self.logger.info(f"從指定頁面提取文字: {page_numbers}")
            
            with pdfplumber.open(pdf_path) as pdf:
                text = ""
                total_pages = len(pdf.pages)
                
                for page_num in page_numbers:
                    if 1 <= page_num <= total_pages:
                        try:
                            page_text = pdf.pages[page_num - 1].extract_text()
                            if page_text:
                                # 處理特殊 Unicode 字符，避免編碼錯誤
                                try:
                                    page_text = page_text.encode('utf-8', errors='ignore').decode('utf-8')
                                    # 移除常見的問題字符
                                    page_text = page_text.replace('\x00', '').replace('\ufeff', '')
                                except UnicodeError as ue:
                                    self.logger.warning(f"第 {page_num} 頁 Unicode 清理失敗: {ue}")
                                text += page_text + "\n"
                            self.logger.debug(f"處理第 {page_num} 頁")
                        except Exception as e:
                            self.logger.warning(f"第 {page_num} 頁處理失敗: {e}")
                    else:
                        self.logger.warning(f"頁面編號 {page_num} 超出範圍 (1-{total_pages})")
                
                self.logger.success(f"指定頁面文字提取完成，{len(text)} 字元")
                return text
                
        except Exception as e:
            error_msg = f"指定頁面PDF處理失敗: {e}"
            self.logger.failure(error_msg)
            raise PDFProcessingError(error_msg) from e
    
    def get_page_count(self, pdf_path: str) -> int:
        """
        取得PDF頁數

        Args:
            pdf_path: PDF檔案路徑

        Returns:
            PDF頁數
        """
        # 輸入驗證
        self._validate_pdf_path(pdf_path)

        if not os.path.exists(pdf_path):
            raise PDFProcessingError(f"PDF檔案不存在: {pdf_path}")
        
        try:
            with pdfplumber.open(pdf_path) as pdf:
                page_count = len(pdf.pages)
                self.logger.info(f"PDF頁數: {page_count}")
                return page_count
        except Exception as e:
            error_msg = f"取得PDF頁數失敗: {e}"
            self.logger.failure(error_msg)
            raise PDFProcessingError(error_msg) from e

    def _validate_pdf_path(self, pdf_path: str) -> None:
        """
        驗證 PDF 檔案路徑

        Args:
            pdf_path: PDF 檔案路徑

        Raises:
            PDFProcessingError: 參數無效時拋出
        """
        # 驗證類型
        if not isinstance(pdf_path, str):
            raise PDFProcessingError(f"pdf_path 必須是字串，收到類型: {type(pdf_path).__name__}")

        # 驗證非空
        if not pdf_path or not pdf_path.strip():
            raise PDFProcessingError("pdf_path 不能為空字串")

        # 驗證副檔名
        if not pdf_path.lower().endswith('.pdf'):
            raise PDFProcessingError(f"pdf_path 必須是 PDF 檔案（.pdf），收到: {pdf_path}")

        # 驗證不是目錄
        if os.path.exists(pdf_path) and os.path.isdir(pdf_path):
            raise PDFProcessingError(f"pdf_path 不能是目錄: {pdf_path}")

    def _validate_max_pages(self, max_pages: int) -> None:
        """
        驗證最大頁數參數

        Args:
            max_pages: 最大頁數

        Raises:
            PDFProcessingError: 參數無效時拋出
        """
        # 驗證類型
        if not isinstance(max_pages, int):
            raise PDFProcessingError(f"max_pages 必須是整數，收到類型: {type(max_pages).__name__}")

        # 驗證範圍
        if max_pages < 1:
            raise PDFProcessingError(f"max_pages 必須大於 0，收到: {max_pages}")

        if max_pages > MAX_PAGES_WARNING_THRESHOLD:
            self.logger.warning(f"max_pages 設定過大（{max_pages}），可能導致記憶體不足")

    def _validate_page_numbers(self, page_numbers: List[int]) -> None:
        """
        驗證頁碼列表

        Args:
            page_numbers: 頁碼列表

        Raises:
            PDFProcessingError: 參數無效時拋出
        """
        # 驗證類型
        if not isinstance(page_numbers, list):
            raise PDFProcessingError(f"page_numbers 必須是列表，收到類型: {type(page_numbers).__name__}")

        # 驗證非空
        if not page_numbers:
            raise PDFProcessingError("page_numbers 不能為空列表")

        # 驗證列表內容
        for i, page_num in enumerate(page_numbers):
            if not isinstance(page_num, int):
                raise PDFProcessingError(
                    f"page_numbers[{i}] 必須是整數，收到類型: {type(page_num).__name__}"
                )
            if page_num < 1:
                raise PDFProcessingError(f"page_numbers[{i}] 必須大於 0，收到: {page_num}")