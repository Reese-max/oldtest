#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
增強PDF處理器測試
"""

import unittest
import sys
import os
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.core.enhanced_pdf_processor import EnhancedPDFProcessor


class TestEnhancedPDFProcessor(unittest.TestCase):
    """增強PDF處理器測試"""
    
    def setUp(self):
        self.processor = EnhancedPDFProcessor()
    
    @patch('pdfplumber.open')
    def test_extract_with_pdfplumber_success(self, mock_open):
        """測試使用pdfplumber提取成功"""
        mock_pdf = MagicMock()
        mock_page = MagicMock()
        mock_page.extract_text.return_value = "測試內容"
        mock_pdf.pages = [mock_page]
        mock_open.return_value.__enter__.return_value = mock_pdf
        
        result = self.processor._extract_with_pdfplumber('test.pdf')
        
        self.assertEqual(result, "測試內容")
    
    @patch('fitz.open')
    def test_extract_with_pymupdf_success(self, mock_open):
        """測試使用pymupdf (fitz)提取成功"""
        mock_doc = MagicMock()
        mock_page = MagicMock()
        mock_page.get_text.return_value = "測試內容"
        mock_doc.__len__.return_value = 1
        mock_doc.__getitem__.return_value = mock_page
        mock_open.return_value = mock_doc
        
        result = self.processor._extract_with_pymupdf('test.pdf')
        
        self.assertEqual(result, "測試內容")
    
    @patch('os.path.exists')
    def test_extract_with_best_method_file_not_exist(self, mock_exists):
        """測試處理不存在的檔案"""
        mock_exists.return_value = False
        
        with self.assertRaises(Exception):
            self.processor.extract_with_best_method('nonexistent.pdf')
    
    def test_calculate_text_quality(self):
        """測試計算文字質量"""
        text = "這是測試內容，包含中文和標點符號。"
        
        score = self.processor.get_text_quality_score(text)
        
        # 質量分數應該在0-1之間
        self.assertGreaterEqual(score, 0.0)
        self.assertLessEqual(score, 1.0)
    
    @patch('pdfplumber.open')
    @patch('fitz.open')
    def test_extract_with_best_method_fallback(self, mock_fitz, mock_pdfplumber):
        """測試方法回退機制"""
        # pdfplumber失敗
        mock_pdfplumber.side_effect = Exception("pdfplumber失敗")
        
        # pymupdf成功
        mock_doc = MagicMock()
        mock_page = MagicMock()
        mock_page.get_text.return_value = "測試內容，包含足夠的中文字符和標點符號，確保質量分數較高。"
        mock_doc.__len__.return_value = 1
        mock_doc.__getitem__.return_value = mock_page
        mock_fitz.return_value = mock_doc
        
        result = self.processor.extract_with_best_method('test.pdf')
        
        # 應該使用pymupdf的結果
        self.assertIn('text', result)
        self.assertIn('method', result)
        self.assertIn('score', result)
        self.assertGreater(result['score'], 0)


if __name__ == '__main__':
    unittest.main()

