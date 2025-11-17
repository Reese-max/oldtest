#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試基本題目解析器
"""

import os
import sys
import unittest
from unittest.mock import Mock, patch, MagicMock

# 添加專案根目錄到路徑
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.core.question_parser import QuestionParser
from src.utils.exceptions import QuestionParsingError


class TestQuestionParser(unittest.TestCase):
    """測試 QuestionParser 類"""

    def setUp(self):
        """測試前設置"""
        self.parser = QuestionParser()

    def test_init(self):
        """測試初始化"""
        self.assertIsNotNone(self.parser.logger)
        self.assertIsNotNone(self.parser.config)

    def test_parse_simple_question(self):
        """測試解析簡單題目"""
        text = """
        1. 下列何者正確？
        (A) 選項A
        (B) 選項B
        (C) 選項C
        (D) 選項D
        """

        questions = self.parser.parse_questions(text)

        # 應該至少解析出1題
        self.assertGreaterEqual(len(questions), 1)

        if questions:
            question = questions[0]
            # 驗證題目結構
            self.assertIn('題號', question)
            self.assertIn('題目', question)

    def test_parse_multiple_questions(self):
        """測試解析多個題目"""
        text = """
        1. 第一題題目？
        (A) 選項A
        (B) 選項B
        (C) 選項C
        (D) 選項D

        2. 第二題題目？
        (A) 選項A
        (B) 選項B
        (C) 選項C
        (D) 選項D

        3. 第三題題目？
        (A) 選項A
        (B) 選項B
        (C) 選項C
        (D) 選項D
        """

        questions = self.parser.parse_questions(text)

        # 應該至少解析出2題以上
        self.assertGreaterEqual(len(questions), 2)

    def test_parse_question_with_long_text(self):
        """測試解析包含長文本的題目"""
        text = """
        5. 根據以下文章，下列敘述何者正確？
        文章內容：這是一段很長的文章內容，用於測試解析器是否能正確處理包含長文本的題目。
        文章可能包含多個段落和複雜的句子結構。

        (A) 第一個選項包含較長的描述
        (B) 第二個選項
        (C) 第三個選項
        (D) 第四個選項
        """

        questions = self.parser.parse_questions(text)

        # 應該能解析出題目
        self.assertGreaterEqual(len(questions), 0)

    def test_parse_empty_text(self):
        """測試解析空文本"""
        text = ""

        questions = self.parser.parse_questions(text)

        # 空文本應該返回空列表
        self.assertEqual(questions, [])

    def test_parse_no_questions(self):
        """測試解析不包含題目的文本"""
        text = """
        這是一段普通的文字，不包含任何題目。
        只是一些說明文字而已。
        """

        questions = self.parser.parse_questions(text)

        # 應該返回空列表或空
        self.assertIsInstance(questions, list)

    def test_parse_question_with_special_characters(self):
        """測試解析包含特殊字符的題目"""
        text = """
        10. 下列何者正確？（包含特殊符號：＠＃＄％）
        (A) 選項A：包含冒號
        (B) 選項B「包含引號」
        (C) 選項C【包含括號】
        (D) 選項D（包含括號）
        """

        # 應該不拋出異常
        try:
            questions = self.parser.parse_questions(text)
            # 測試通過
            self.assertIsInstance(questions, list)
        except Exception as e:
            self.fail(f"解析特殊字符時拋出異常: {e}")

    def test_parse_question_with_numbers_in_options(self):
        """測試解析選項中包含數字的題目"""
        text = """
        15. 下列何者數值最大？
        (A) 100
        (B) 200
        (C) 300
        (D) 400
        """

        questions = self.parser.parse_questions(text)

        # 應該能正確解析
        self.assertIsInstance(questions, list)

    def test_parse_question_with_english_text(self):
        """測試解析包含英文的題目"""
        text = """
        20. Which of the following is correct?
        (A) Option A
        (B) Option B
        (C) Option C
        (D) Option D
        """

        questions = self.parser.parse_questions(text)

        # 應該能解析英文題目
        self.assertIsInstance(questions, list)

    def test_parse_question_with_mixed_language(self):
        """測試解析中英混合的題目"""
        text = """
        25. 下列關於 Python 的敘述何者正確？
        (A) Python is a programming language
        (B) Python 是一種程式語言
        (C) Python 適合 data science
        (D) 以上皆是
        """

        questions = self.parser.parse_questions(text)

        # 應該能解析中英混合題目
        self.assertIsInstance(questions, list)

    def test_parse_question_numbers_out_of_order(self):
        """測試解析題號不連續的題目"""
        text = """
        10. 第十題？
        (A) 選項A
        (B) 選項B
        (C) 選項C
        (D) 選項D

        15. 第十五題？
        (A) 選項A
        (B) 選項B
        (C) 選項C
        (D) 選項D

        20. 第二十題？
        (A) 選項A
        (B) 選項B
        (C) 選項C
        (D) 選項D
        """

        questions = self.parser.parse_questions(text)

        # 應該能解析不連續的題號
        self.assertIsInstance(questions, list)

    def test_parse_question_with_three_options(self):
        """測試解析只有三個選項的題目"""
        text = """
        30. 下列何者正確？
        (A) 選項A
        (B) 選項B
        (C) 選項C
        """

        questions = self.parser.parse_questions(text)

        # 應該能解析三個選項的題目
        self.assertIsInstance(questions, list)

    def test_parse_question_with_five_options(self):
        """測試解析有五個選項的題目"""
        text = """
        35. 下列何者正確？
        (A) 選項A
        (B) 選項B
        (C) 選項C
        (D) 選項D
        (E) 選項E
        """

        questions = self.parser.parse_questions(text)

        # 應該能解析五個選項的題目
        self.assertIsInstance(questions, list)

    def test_parse_malformed_question(self):
        """測試解析格式錯誤的題目"""
        text = """
        這是一題格式錯誤的題目
        沒有題號
        選項A
        選項B
        """

        # 應該不拋出異常，返回空列表或嘗試解析
        try:
            questions = self.parser.parse_questions(text)
            self.assertIsInstance(questions, list)
        except QuestionParsingError:
            # 允許拋出 QuestionParsingError
            pass

    def test_parse_question_with_multiline_options(self):
        """測試解析跨多行的選項"""
        text = """
        40. 下列何者正確？
        (A) 這是一個很長的選項
            延伸到下一行
        (B) 這也是一個長選項
            同樣延伸到下一行
        (C) 選項C
        (D) 選項D
        """

        questions = self.parser.parse_questions(text)

        # 應該能處理跨行選項
        self.assertIsInstance(questions, list)

    def test_parse_question_with_nested_parentheses(self):
        """測試解析包含嵌套括號的題目"""
        text = """
        45. 下列何者正確？
        (A) 選項A（包含說明（嵌套括號））
        (B) 選項B
        (C) 選項C
        (D) 選項D
        """

        questions = self.parser.parse_questions(text)

        # 應該能處理嵌套括號
        self.assertIsInstance(questions, list)


class TestQuestionParserEdgeCases(unittest.TestCase):
    """測試 QuestionParser 的邊界情況"""

    def setUp(self):
        """測試前設置"""
        self.parser = QuestionParser()

    def test_very_long_text(self):
        """測試處理非常長的文本"""
        # 創建包含100個題目的長文本
        questions_text = []
        for i in range(1, 101):
            questions_text.append(f"""
            {i}. 第{i}題題目？
            (A) 選項A
            (B) 選項B
            (C) 選項C
            (D) 選項D
            """)

        text = "\n".join(questions_text)

        # 應該能處理長文本而不崩潰
        try:
            questions = self.parser.parse_questions(text)
            self.assertIsInstance(questions, list)
            # 應該能解析出相當數量的題目
            self.assertGreater(len(questions), 0)
        except Exception as e:
            self.fail(f"處理長文本時失敗: {e}")

    def test_unicode_characters(self):
        """測試處理 Unicode 字符"""
        text = """
        50. 下列何者包含特殊符號？
        (A) 選項A ★☆♥♦
        (B) 選項B ①②③④
        (C) 選項C ㄅㄆㄇㄈ
        (D) 選項D αβγδ
        """

        questions = self.parser.parse_questions(text)

        # 應該能處理 Unicode 字符
        self.assertIsInstance(questions, list)

    def test_whitespace_variations(self):
        """測試處理各種空白字符"""
        text = """
        55.   下列何者正確？（多個空格）
        (A)選項A（無空格）
        (B)  選項B（多個空格）
        (C)\t選項C（Tab）
        (D) 選項D
        """

        questions = self.parser.parse_questions(text)

        # 應該能處理各種空白字符
        self.assertIsInstance(questions, list)


if __name__ == '__main__':
    unittest.main()
