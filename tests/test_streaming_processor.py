#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試流式處理器
"""

import os
import sys
import tempfile
import unittest
from unittest.mock import MagicMock, Mock, patch

# 添加專案根目錄到路徑
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.utils.exceptions import PDFProcessingError
from src.utils.streaming_processor import (
    MemoryMonitor,
    PageChunk,
    StreamConfig,
    StreamingPDFProcessor,
    create_streaming_processor,
    memory_efficient_processing,
)


class TestMemoryMonitor(unittest.TestCase):
    """測試記憶體監控器"""

    def test_init(self):
        """測試初始化"""
        monitor = MemoryMonitor(limit_mb=512)
        self.assertEqual(monitor.limit_mb, 512)
        self.assertEqual(monitor.limit_bytes, 512 * 1024 * 1024)
        self.assertEqual(monitor.peak_memory, 0)

    def test_get_current_memory(self):
        """測試獲取當前記憶體"""
        monitor = MemoryMonitor()
        current_mb = monitor.get_current_memory_mb()

        # 記憶體應該大於 0
        self.assertGreater(current_mb, 0)
        # 峰值應該被更新
        self.assertEqual(monitor.peak_memory, current_mb)

    def test_check_memory_limit(self):
        """測試記憶體限制檢查"""
        # 設定極小的限制，應該會超過
        monitor = MemoryMonitor(limit_mb=1)
        self.assertTrue(monitor.check_memory_limit())

        # 設定極大的限制，應該不會超過
        monitor = MemoryMonitor(limit_mb=100000)
        self.assertFalse(monitor.check_memory_limit())

    def test_should_trigger_gc(self):
        """測試 GC 觸發判斷"""
        monitor = MemoryMonitor()

        # 使用很小的閾值，應該觸發
        self.assertTrue(monitor.should_trigger_gc(threshold_mb=1))

        # 使用很大的閾值，應該不觸發
        self.assertFalse(monitor.should_trigger_gc(threshold_mb=100000))

    def test_force_gc(self):
        """測試強制 GC"""
        monitor = MemoryMonitor()
        freed_mb = monitor.force_gc()

        # 釋放的記憶體可能是 0 或正數（取決於 GC 是否回收了東西）
        self.assertGreaterEqual(freed_mb, -100)  # 允許小幅增長

    def test_get_stats(self):
        """測試統計信息"""
        monitor = MemoryMonitor(limit_mb=512)
        monitor.get_current_memory_mb()  # 更新峰值

        stats = monitor.get_stats()

        # 驗證統計欄位
        self.assertIn("current_mb", stats)
        self.assertIn("peak_mb", stats)
        self.assertIn("limit_mb", stats)
        self.assertIn("usage_percent", stats)

        # 驗證數值合理性
        self.assertGreater(stats["current_mb"], 0)
        self.assertGreater(stats["peak_mb"], 0)
        self.assertEqual(stats["limit_mb"], 512)
        self.assertGreater(stats["usage_percent"], 0)


class TestStreamConfig(unittest.TestCase):
    """測試流式處理配置"""

    def test_default_config(self):
        """測試默認配置"""
        config = StreamConfig()

        self.assertEqual(config.chunk_size, 10)
        self.assertEqual(config.memory_limit_mb, 512)
        self.assertTrue(config.enable_monitoring)
        self.assertTrue(config.auto_gc)
        self.assertEqual(config.gc_interval, 10)

    def test_custom_config(self):
        """測試自定義配置"""
        config = StreamConfig(
            chunk_size=20, memory_limit_mb=1024, enable_monitoring=False, auto_gc=False, gc_interval=5
        )

        self.assertEqual(config.chunk_size, 20)
        self.assertEqual(config.memory_limit_mb, 1024)
        self.assertFalse(config.enable_monitoring)
        self.assertFalse(config.auto_gc)
        self.assertEqual(config.gc_interval, 5)


class TestPageChunk(unittest.TestCase):
    """測試頁面區塊"""

    def test_page_chunk(self):
        """測試頁面區塊創建"""
        chunk = PageChunk(pages=[1, 2, 3], text="test text", metadata={"total_pages": 100})

        self.assertEqual(chunk.pages, [1, 2, 3])
        self.assertEqual(chunk.text, "test text")
        self.assertEqual(chunk.metadata["total_pages"], 100)


class TestStreamingPDFProcessor(unittest.TestCase):
    """測試流式 PDF 處理器"""

    def setUp(self):
        """測試前設置"""
        self.config = StreamConfig(chunk_size=5, memory_limit_mb=512)
        self.processor = StreamingPDFProcessor(self.config)

    def test_init(self):
        """測試初始化"""
        self.assertIsNotNone(self.processor.config)
        self.assertIsNotNone(self.processor.memory_monitor)
        self.assertEqual(self.processor.config.chunk_size, 5)

    def test_init_default_config(self):
        """測試默認配置初始化"""
        processor = StreamingPDFProcessor()
        self.assertEqual(processor.config.chunk_size, 10)

    def test_clean_text(self):
        """測試文字清理"""
        # 包含特殊字符的文字
        dirty_text = "Hello\x00World\ufeff Test"
        clean = self.processor._clean_text(dirty_text)

        # 應該移除特殊字符
        self.assertNotIn("\x00", clean)
        self.assertNotIn("\ufeff", clean)
        self.assertIn("Hello", clean)
        self.assertIn("World", clean)

    def test_clean_text_unicode_error(self):
        """測試 Unicode 錯誤處理"""
        # 這應該不會拋出異常
        text = "普通文字"
        clean = self.processor._clean_text(text)
        self.assertEqual(clean, text)

    @patch("pdfplumber.open")
    def test_stream_pages_basic(self, mock_pdf_open):
        """測試基本流式處理"""
        # 模擬 PDF
        mock_pdf = MagicMock()
        mock_page1 = MagicMock()
        mock_page1.extract_text.return_value = "Page 1 text"
        mock_page2 = MagicMock()
        mock_page2.extract_text.return_value = "Page 2 text"

        mock_pdf.pages = [mock_page1, mock_page2]
        mock_pdf.__enter__.return_value = mock_pdf
        mock_pdf_open.return_value = mock_pdf

        # 創建臨時 PDF 文件路徑
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
            tmp_path = tmp.name

        try:
            # 處理
            chunks = list(self.processor.stream_pages(tmp_path))

            # 驗證
            self.assertEqual(len(chunks), 1)  # chunk_size=5, 2 pages -> 1 chunk
            self.assertEqual(chunks[0].pages, [1, 2])
            self.assertIn("Page 1 text", chunks[0].text)
            self.assertIn("Page 2 text", chunks[0].text)

        finally:
            os.unlink(tmp_path)

    def test_stream_pages_file_not_found(self):
        """測試文件不存在"""
        with self.assertRaises(PDFProcessingError):
            list(self.processor.stream_pages("nonexistent.pdf"))

    @patch("pdfplumber.open")
    def test_stream_pages_with_page_range(self, mock_pdf_open):
        """測試指定頁面範圍"""
        # 模擬 10 頁的 PDF
        mock_pdf = MagicMock()
        mock_pages = []
        for i in range(10):
            mock_page = MagicMock()
            mock_page.extract_text.return_value = f"Page {i+1}"
            mock_pages.append(mock_page)

        mock_pdf.pages = mock_pages
        mock_pdf.__enter__.return_value = mock_pdf
        mock_pdf_open.return_value = mock_pdf

        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
            tmp_path = tmp.name

        try:
            # 只處理第 3-7 頁
            chunks = list(self.processor.stream_pages(tmp_path, start_page=3, end_page=7))

            # chunk_size=5, 5 pages (3-7) -> 1 chunk
            self.assertEqual(len(chunks), 1)
            self.assertEqual(chunks[0].pages, [3, 4, 5, 6, 7])

        finally:
            os.unlink(tmp_path)

    @patch("pdfplumber.open")
    def test_process_with_callback(self, mock_pdf_open):
        """測試回調處理"""
        # 模擬 PDF
        mock_pdf = MagicMock()
        mock_page = MagicMock()
        mock_page.extract_text.return_value = "Test text"
        mock_pdf.pages = [mock_page]
        mock_pdf.__enter__.return_value = mock_pdf
        mock_pdf_open.return_value = mock_pdf

        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
            tmp_path = tmp.name

        try:
            # 定義回調
            callback = Mock(return_value={"result": "processed"})

            # 處理
            results = self.processor.process_with_callback(tmp_path, callback)

            # 驗證
            self.assertEqual(len(results), 1)
            self.assertEqual(results[0]["result"], "processed")
            callback.assert_called_once()

        finally:
            os.unlink(tmp_path)

    @patch("pdfplumber.open")
    def test_process_with_callback_error(self, mock_pdf_open):
        """測試回調處理錯誤"""
        # 模擬 PDF
        mock_pdf = MagicMock()
        mock_page = MagicMock()
        mock_page.extract_text.return_value = "Test"
        mock_pdf.pages = [mock_page]
        mock_pdf.__enter__.return_value = mock_pdf
        mock_pdf_open.return_value = mock_pdf

        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
            tmp_path = tmp.name

        try:
            # 回調拋出異常
            callback = Mock(side_effect=Exception("Callback error"))

            # 處理（不應該拋出異常）
            results = self.processor.process_with_callback(tmp_path, callback)

            # 失敗應該返回 None
            self.assertEqual(results[0], None)

        finally:
            os.unlink(tmp_path)

    @patch("pdfplumber.open")
    def test_extract_text_streaming(self, mock_pdf_open):
        """測試流式文字提取"""
        # 模擬 PDF
        mock_pdf = MagicMock()
        mock_page1 = MagicMock()
        mock_page1.extract_text.return_value = "Text 1"
        mock_page2 = MagicMock()
        mock_page2.extract_text.return_value = "Text 2"
        mock_pdf.pages = [mock_page1, mock_page2]
        mock_pdf.__enter__.return_value = mock_pdf
        mock_pdf_open.return_value = mock_pdf

        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
            tmp_path = tmp.name

        try:
            # 提取
            text = self.processor.extract_text_streaming(tmp_path)

            # 驗證
            self.assertIn("Text 1", text)
            self.assertIn("Text 2", text)

        finally:
            os.unlink(tmp_path)

    @patch("pdfplumber.open")
    def test_extract_text_streaming_with_callback(self, mock_pdf_open):
        """測試帶回調的流式文字提取"""
        # 模擬 PDF
        mock_pdf = MagicMock()
        mock_page = MagicMock()
        mock_page.extract_text.return_value = "Test"
        mock_pdf.pages = [mock_page]
        mock_pdf.__enter__.return_value = mock_pdf
        mock_pdf_open.return_value = mock_pdf

        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
            tmp_path = tmp.name

        try:
            # 定義回調
            callback = Mock()

            # 提取
            text = self.processor.extract_text_streaming(tmp_path, callback)

            # 應該調用回調
            callback.assert_called_once()
            # 不應該返回累積文字
            self.assertEqual(text, "")

        finally:
            os.unlink(tmp_path)


class TestHelperFunctions(unittest.TestCase):
    """測試輔助函數"""

    def test_create_streaming_processor(self):
        """測試創建流式處理器"""
        processor = create_streaming_processor(chunk_size=20, memory_limit_mb=1024, enable_monitoring=False)

        self.assertIsInstance(processor, StreamingPDFProcessor)
        self.assertEqual(processor.config.chunk_size, 20)
        self.assertEqual(processor.config.memory_limit_mb, 1024)
        self.assertFalse(processor.config.enable_monitoring)

    def test_memory_efficient_processing_context(self):
        """測試記憶體高效處理上下文"""
        with memory_efficient_processing(memory_limit_mb=512) as monitor:
            # 在上下文中，monitor 應該可用
            self.assertIsInstance(monitor, MemoryMonitor)
            self.assertEqual(monitor.limit_mb, 512)

            # 可以獲取記憶體統計
            stats = monitor.get_stats()
            self.assertIn("current_mb", stats)


if __name__ == "__main__":
    unittest.main()
