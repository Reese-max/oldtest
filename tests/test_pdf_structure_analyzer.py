#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF結構分析器測試
"""

import os
import sys
import unittest
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from src.core.pdf_structure_analyzer import PDFStructureAnalyzer, QuestionType


class TestPDFStructureAnalyzer(unittest.TestCase):
    """PDF結構分析器測試"""

    def setUp(self):
        self.analyzer = PDFStructureAnalyzer()

    @patch("src.core.pdf_structure_analyzer.PDFProcessor.get_page_count")
    @patch("src.core.pdf_structure_analyzer.PDFProcessor.extract_text")
    @patch("os.path.exists")
    def test_analyze_pdf_structure(self, mock_exists, mock_extract, mock_page_count):
        """測試分析PDF結構"""
        mock_exists.return_value = True
        mock_extract.return_value = """
        第1題：下列何者正確？
        (A) 選項A
        (B) 選項B
        (C) 選項C
        (D) 選項D
        
        第2題：下列何者錯誤？
        (A) 選項A
        (B) 選項B
        """
        mock_page_count.return_value = 1

        features = self.analyzer.analyze_pdf_structure("test.pdf")

        # 檢查返回的結構特徵
        self.assertIsNotNone(features)
        self.assertGreater(features.text_length, 0)
        self.assertIsInstance(features.question_type, QuestionType)
        self.assertIsInstance(features.has_essay_section, bool)
        self.assertIsInstance(features.has_choice_section, bool)

    @patch("os.path.exists")
    def test_analyze_pdf_structure_nonexistent(self, mock_exists):
        """測試分析不存在的PDF"""
        mock_exists.return_value = False

        with self.assertRaises(Exception):
            self.analyzer.analyze_pdf_structure("nonexistent.pdf")

    def test_detect_question_type(self):
        """測試檢測題目類型"""
        # 測試選擇題
        choice_text = "測驗題部分 第1題 (A) (B) (C) (D)"
        q_type = self.analyzer._detect_question_type(choice_text, "test.pdf")
        self.assertIn(q_type, [QuestionType.CHOICE, QuestionType.UNKNOWN])

        # 測試申論題
        essay_text = "請論述以下問題..."
        q_type = self.analyzer._detect_question_type(essay_text, "essay.pdf")
        self.assertIsInstance(q_type, QuestionType)

        # 測試綜合格式
        comprehensive_text = "甲、申論題部分 乙、測驗題部分"
        q_type = self.analyzer._detect_question_type(comprehensive_text, "test.pdf")
        self.assertEqual(q_type, QuestionType.COMPREHENSIVE)

        # 測試混合格式
        mixed_text = "作文部分 測驗部分"
        q_type = self.analyzer._detect_question_type(mixed_text, "國文.pdf")
        self.assertEqual(q_type, QuestionType.MIXED)

    def test_analyze_question_patterns(self):
        """測試分析題目模式"""
        text = """
        第1題：問題
        第2題：問題
        """

        patterns = self.analyzer._analyze_question_patterns(text)

        self.assertIsInstance(patterns, list)

    def test_analyze_option_patterns(self):
        """測試分析選項模式"""
        text = """
        (A) 選項A
        (B) 選項B
        (C) 選項C
        (D) 選項D
        """

        patterns = self.analyzer._analyze_option_patterns(text)

        self.assertIsInstance(patterns, list)

    def test_find_section_headers(self):
        """測試提取章節標題"""
        text = """
        甲、申論題部分
        乙、測驗題部分
        """

        headers = self.analyzer._find_section_headers(text)

        self.assertIsInstance(headers, list)

    def test_has_essay_section(self):
        """測試檢測申論題部分"""
        essay_text = "甲、申論題部分"
        self.assertTrue(self.analyzer._has_essay_section(essay_text))

        no_essay_text = "測驗題部分"
        self.assertFalse(self.analyzer._has_essay_section(no_essay_text))

    def test_has_choice_section(self):
        """測試檢測選擇題部分"""
        choice_text = "乙、測驗題部分"
        self.assertTrue(self.analyzer._has_choice_section(choice_text))

        no_choice_text = "申論題部分"
        self.assertFalse(self.analyzer._has_choice_section(no_choice_text))

    def test_count_questions(self):
        """測試統計題目數量"""
        text = """
        第1題：問題1
        第2題：問題2
        """

        count = self.analyzer._count_questions(text)

        self.assertIsInstance(count, int)
        self.assertGreaterEqual(count, 0)

    def test_count_essay_questions(self):
        """測試統計申論題數量"""
        text = """
        第1題：問題（25分）
        第2題：問題（25分）
        """

        count = self.analyzer._count_essay_questions(text)

        self.assertIsInstance(count, int)
        self.assertGreaterEqual(count, 0)

    def test_count_choice_questions(self):
        """測試統計選擇題數量"""
        text = """
        第1題：問題 A. 選項
        第2題：問題 A. 選項
        """

        count = self.analyzer._count_choice_questions(text)

        self.assertIsInstance(count, int)
        self.assertGreaterEqual(count, 0)


if __name__ == "__main__":
    unittest.main()
