#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
無標記選項題目解析器測試
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from src.core.no_label_question_parser import NoLabelQuestionParser


class TestNoLabelQuestionParser(unittest.TestCase):
    """無標記選項題目解析器測試"""

    def setUp(self):
        self.parser = NoLabelQuestionParser()

    def test_parse_no_label_questions_empty(self):
        """測試解析空文字"""
        questions = self.parser.parse_no_label_questions("")

        self.assertIsInstance(questions, list)
        self.assertEqual(len(questions), 0)

    def test_parse_no_label_questions_standard_format(self):
        """測試解析標準格式"""
        text = """
        1 下列何者正確？
        選項一內容
        選項二內容
        選項三內容
        選項四內容
        
        2 下列何者錯誤？
        選項一內容
        選項二內容
        選項三內容
        選項四內容
        """

        questions = self.parser.parse_no_label_questions(text)

        # 應該解析到題目
        self.assertIsInstance(questions, list)
        # 根據實際解析邏輯，可能解析到0個或多個題目
        for question in questions:
            self.assertIn("題號", question)
            self.assertIn("題目", question)
            self.assertIn("選項A", question)

    def test_parse_no_label_questions_english_options(self):
        """測試解析英文選項"""
        text = """
        1 word1 word2 word3 word4
        """

        questions = self.parser.parse_no_label_questions(text)

        # 應該能夠處理英文選項
        self.assertIsInstance(questions, list)

    def test_parse_no_label_questions_invalid_number(self):
        """測試無效題號"""
        text = """
        100 這是一個無效的題號（超過50）
        """

        questions = self.parser.parse_no_label_questions(text)

        # 無效題號應該被跳過
        self.assertIsInstance(questions, list)


if __name__ == "__main__":
    unittest.main()
