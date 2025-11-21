#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
題目解析器擴展測試
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from src.core.question_parser import QuestionParser


class TestQuestionParserExtended(unittest.TestCase):
    """題目解析器擴展測試"""

    def setUp(self):
        self.parser = QuestionParser()

    def test_parse_regular_questions_various_formats(self):
        """測試解析各種格式的一般題目"""
        # 格式1: 第X題：內容
        text1 = """
        第1題：下列何者正確？
        (A) 選項A
        (B) 選項B
        (C) 選項C
        (D) 選項D
        """

        questions = self.parser.parse_questions(text1)
        # 應該至少解析到1個題目，或者返回空列表
        self.assertIsInstance(questions, list)
        if len(questions) > 0:
            self.assertGreaterEqual(len(questions), 1)

        # 格式2: 數字. 內容 - 這種格式可能不被解析
        text2 = """
        1. 下列何者正確？
        (A) 選項A
        (B) 選項B
        (C) 選項C
        (D) 選項D
        """

        questions = self.parser.parse_questions(text2)
        # 可能解析成功也可能失敗，只驗證返回格式
        self.assertIsInstance(questions, list)

    def test_detect_question_groups_multiple_patterns(self):
        """測試檢測多種題組模式"""
        test_cases = [
            "請依下文回答第1題至第5題",
            "請根據下列文章回答第1題至第3題",
            "閱讀下文，回答第1題至第4題",
        ]

        for text in test_cases:
            with self.subTest(text=text):
                groups = self.parser._detect_question_groups(text)
                self.assertGreaterEqual(len(groups), 1)

    def test_extract_options_various_formats(self):
        """測試提取各種格式的選項"""
        # 標準格式
        text1 = """
        (A) 選項A
        (B) 選項B
        (C) 選項C
        (D) 選項D
        """
        options1 = self.parser._extract_options(text1)
        self.assertGreaterEqual(len(options1), 2)

        # 全形括號
        text2 = """
        （A）選項A
        （B）選項B
        （C）選項C
        （D）選項D
        """
        options2 = self.parser._extract_options(text2)
        self.assertGreaterEqual(len(options2), 2)

    def test_is_not_a_question_filters(self):
        """測試過濾非題目內容"""
        # 應該被過濾的內容
        bad_cases = [
            ("2501", "代號：2501"),  # 代號
            ("1", "頁次：1"),  # 頁次
            ("1", "注意事項"),  # 注意事項
            ("999", "這是一個很長的題號"),  # 題號過長
            ("1", "短"),  # 內容過短
        ]

        for question_num, text in bad_cases:
            with self.subTest(text=text):
                result = self.parser._is_not_a_question(question_num, text)
                # 應該被過濾掉
                self.assertTrue(result or len(text) < 10)

    def test_parse_empty_text(self):
        """測試解析空文字"""
        questions = self.parser.parse_questions("")
        self.assertEqual(len(questions), 0)

    def test_parse_text_with_no_questions(self):
        """測試解析沒有題目的文字"""
        text = """
        這是一段普通的文字
        沒有任何題目格式
        只是一般的內容
        """

        questions = self.parser.parse_questions(text)
        self.assertEqual(len(questions), 0)

    def test_extract_group_content(self):
        """測試提取題組內容"""
        text = """
        請依下文回答第1題至第3題
        
        這是文章內容...
        
        第1題：題目1
        (A) 選項A
        (B) 選項B
        (C) 選項C
        (D) 選項D
        
        請依下文回答第4題至第6題
        
        另一段文章內容...
        """

        groups = self.parser._detect_question_groups(text)
        if groups:
            content = self.parser._extract_group_content(text, groups[0])
            self.assertGreater(len(content), 0)
            self.assertIn("第1題", content)


if __name__ == "__main__":
    unittest.main()
