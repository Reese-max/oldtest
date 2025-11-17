#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
輸入驗證測試
測試所有核心模組的輸入驗證功能
"""

import os
import sys
import unittest
import tempfile

# 添加項目根目錄到 Python 路徑
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.csv_generator import CSVGenerator
from src.core.google_script_generator import GoogleScriptGenerator
from src.core.pdf_processor import PDFProcessor
from src.utils.exceptions import CSVGenerationError, GoogleFormError, PDFProcessingError


class TestCSVGeneratorValidation(unittest.TestCase):
    """測試 CSV 生成器輸入驗證"""

    def setUp(self):
        self.csv_gen = CSVGenerator()
        self.temp_dir = tempfile.mkdtemp()

    def test_invalid_questions_type(self):
        """測試無效的 questions 類型"""
        with self.assertRaises(CSVGenerationError) as cm:
            self.csv_gen.generate_questions_csv(
                questions="not a list",  # 錯誤：應該是列表
                answers={},
                output_path=os.path.join(self.temp_dir, "test.csv")
            )
        self.assertIn("questions 必須是列表", str(cm.exception))

    def test_invalid_answers_type(self):
        """測試無效的 answers 類型"""
        with self.assertRaises(CSVGenerationError) as cm:
            self.csv_gen.generate_questions_csv(
                questions=[],
                answers="not a dict",  # 錯誤：應該是字典
                output_path=os.path.join(self.temp_dir, "test.csv")
            )
        self.assertIn("answers 必須是字典", str(cm.exception))

    def test_invalid_output_path_type(self):
        """測試無效的 output_path 類型"""
        with self.assertRaises(CSVGenerationError) as cm:
            self.csv_gen.generate_questions_csv(
                questions=[],
                answers={},
                output_path=123  # 錯誤：應該是字串
            )
        self.assertIn("output_path 必須是字串", str(cm.exception))

    def test_empty_output_path(self):
        """測試空的 output_path"""
        with self.assertRaises(CSVGenerationError) as cm:
            self.csv_gen.generate_questions_csv(
                questions=[],
                answers={},
                output_path=""  # 錯誤：不能為空
            )
        self.assertIn("output_path 不能為空字串", str(cm.exception))

    def test_output_path_is_directory(self):
        """測試 output_path 是目錄"""
        with self.assertRaises(CSVGenerationError) as cm:
            self.csv_gen.generate_questions_csv(
                questions=[],
                answers={},
                output_path=self.temp_dir  # 錯誤：不能是目錄
            )
        self.assertIn("output_path 不能是目錄", str(cm.exception))

    def test_auto_create_output_directory(self):
        """測試自動創建輸出目錄"""
        new_dir = os.path.join(self.temp_dir, "new_subdir", "nested")
        output_path = os.path.join(new_dir, "test.csv")

        # 目錄不存在
        self.assertFalse(os.path.exists(new_dir))

        # 生成 CSV 應該自動創建目錄
        self.csv_gen.generate_questions_csv(
            questions=[],
            answers={},
            output_path=output_path
        )

        # 目錄應該被創建
        self.assertTrue(os.path.exists(new_dir))
        self.assertTrue(os.path.isfile(output_path))


class TestGoogleScriptGeneratorValidation(unittest.TestCase):
    """測試 Google Script 生成器輸入驗證"""

    def setUp(self):
        self.script_gen = GoogleScriptGenerator()
        self.temp_dir = tempfile.mkdtemp()

    def test_invalid_csv_path_type(self):
        """測試無效的 csv_path 類型"""
        with self.assertRaises(GoogleFormError) as cm:
            self.script_gen.generate_script(
                csv_path=123,  # 錯誤：應該是字串
                output_path=os.path.join(self.temp_dir, "test.gs")
            )
        self.assertIn("csv_path 必須是字串", str(cm.exception))

    def test_empty_csv_path(self):
        """測試空的 csv_path"""
        with self.assertRaises(GoogleFormError) as cm:
            self.script_gen.generate_script(
                csv_path="",  # 錯誤：不能為空
                output_path=os.path.join(self.temp_dir, "test.gs")
            )
        self.assertIn("csv_path 不能為空字串", str(cm.exception))

    def test_csv_path_not_csv_file(self):
        """測試 csv_path 不是 CSV 檔案"""
        with self.assertRaises(GoogleFormError) as cm:
            self.script_gen.generate_script(
                csv_path="test.txt",  # 錯誤：應該是 .csv
                output_path=os.path.join(self.temp_dir, "test.gs")
            )
        self.assertIn("csv_path 必須是 CSV 檔案", str(cm.exception))

    def test_invalid_output_path_type(self):
        """測試無效的 output_path 類型"""
        with self.assertRaises(GoogleFormError) as cm:
            self.script_gen.generate_script(
                csv_path="test.csv",
                output_path=None  # 錯誤：應該是字串
            )
        self.assertIn("output_path 必須是字串", str(cm.exception))


class TestPDFProcessorValidation(unittest.TestCase):
    """測試 PDF 處理器輸入驗證"""

    def setUp(self):
        self.pdf_processor = PDFProcessor()

    def test_invalid_pdf_path_type(self):
        """測試無效的 pdf_path 類型"""
        with self.assertRaises(PDFProcessingError) as cm:
            self.pdf_processor.extract_text(pdf_path=123)
        self.assertIn("pdf_path 必須是字串", str(cm.exception))

    def test_empty_pdf_path(self):
        """測試空的 pdf_path"""
        with self.assertRaises(PDFProcessingError) as cm:
            self.pdf_processor.extract_text(pdf_path="")
        self.assertIn("pdf_path 不能為空字串", str(cm.exception))

    def test_pdf_path_not_pdf_file(self):
        """測試 pdf_path 不是 PDF 檔案"""
        with self.assertRaises(PDFProcessingError) as cm:
            self.pdf_processor.extract_text(pdf_path="test.txt")
        self.assertIn("pdf_path 必須是 PDF 檔案", str(cm.exception))

    def test_invalid_max_pages_type(self):
        """測試無效的 max_pages 類型"""
        with self.assertRaises(PDFProcessingError) as cm:
            self.pdf_processor.extract_text(pdf_path="test.pdf", max_pages="100")
        self.assertIn("max_pages 必須是整數", str(cm.exception))

    def test_invalid_max_pages_value(self):
        """測試無效的 max_pages 值"""
        with self.assertRaises(PDFProcessingError) as cm:
            self.pdf_processor.extract_text(pdf_path="test.pdf", max_pages=0)
        self.assertIn("max_pages 必須大於 0", str(cm.exception))

    def test_invalid_page_numbers_type(self):
        """測試無效的 page_numbers 類型"""
        with self.assertRaises(PDFProcessingError) as cm:
            self.pdf_processor.extract_text_from_pages(
                pdf_path="test.pdf",
                page_numbers="1,2,3"  # 錯誤：應該是列表
            )
        self.assertIn("page_numbers 必須是列表", str(cm.exception))

    def test_empty_page_numbers(self):
        """測試空的 page_numbers"""
        with self.assertRaises(PDFProcessingError) as cm:
            self.pdf_processor.extract_text_from_pages(
                pdf_path="test.pdf",
                page_numbers=[]  # 錯誤：不能為空
            )
        self.assertIn("page_numbers 不能為空列表", str(cm.exception))

    def test_invalid_page_number_in_list(self):
        """測試列表中無效的頁碼"""
        with self.assertRaises(PDFProcessingError) as cm:
            self.pdf_processor.extract_text_from_pages(
                pdf_path="test.pdf",
                page_numbers=[1, "2", 3]  # 錯誤：應該全是整數
            )
        self.assertIn("page_numbers[1] 必須是整數", str(cm.exception))

    def test_negative_page_number(self):
        """測試負數頁碼"""
        with self.assertRaises(PDFProcessingError) as cm:
            self.pdf_processor.extract_text_from_pages(
                pdf_path="test.pdf",
                page_numbers=[1, -2, 3]  # 錯誤：不能是負數
            )
        self.assertIn("page_numbers[1] 必須大於 0", str(cm.exception))


if __name__ == '__main__':
    # 運行測試
    unittest.main(verbosity=2)
