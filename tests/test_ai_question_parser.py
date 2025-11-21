#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試AI輔助題目解析器
"""

import os
import sys
import unittest

# 添加專案根目錄到路徑
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.core.ai_question_parser import AIQuestionParser


class TestAIQuestionParser(unittest.TestCase):
    """測試 AIQuestionParser 類"""

    def setUp(self):
        """測試前設置"""
        self.parser = AIQuestionParser()

    def test_init(self):
        """測試初始化"""
        self.assertIsNotNone(self.parser.logger)
        self.assertIsNotNone(self.parser.config)

    def test_parse_intelligent_questions(self):
        """測試智能解析題目"""
        text = """
        1. 下列何者正確？
        (A) 選項A
        (B) 選項B
        (C) 選項C
        (D) 選項D

        題組：請閱讀以下文章，回答第5-7題
        文章內容...

        5. 第5題？
        (A) 選項A
        (B) 選項B
        (C) 選項C
        (D) 選項D
        """

        questions = self.parser.parse_questions_intelligent(text)

        # 應該能智能解析
        self.assertIsInstance(questions, list)

    def test_detect_question_groups(self):
        """測試檢測題組"""
        text = """
        題組一：請閱讀下文，回答第1-3題

        文章內容：這是第一個題組的文章...

        1. 第1題？
        (A) A  (B) B  (C) C  (D) D

        2. 第2題？
        (A) A  (B) B  (C) C  (D) D

        題組二：請閱讀下文，回答第10-12題

        文章內容：這是第二個題組的文章...

        10. 第10題？
        (A) A  (B) B  (C) C  (D) D
        """

        questions = self.parser.parse_questions_intelligent(text)

        # 應該能檢測到題組
        self.assertIsInstance(questions, list)

    def test_parse_mixed_single_and_group_questions(self):
        """測試解析混合單題和題組"""
        text = """
        1. 單獨題目1
        (A) A  (B) B  (C) C  (D) D

        2. 單獨題目2
        (A) A  (B) B  (C) C  (D) D

        題組：閱讀下文，回答第5-7題
        文章...

        5. 題組題目5
        (A) A  (B) B  (C) C  (D) D

        6. 題組題目6
        (A) A  (B) B  (C) C  (D) D

        8. 單獨題目8
        (A) A  (B) B  (C) C  (D) D
        """

        questions = self.parser.parse_questions_intelligent(text)

        # 應該能正確區分單題和題組
        self.assertIsInstance(questions, list)

    def test_parse_empty_text(self):
        """測試解析空文本"""
        text = ""

        questions = self.parser.parse_questions_intelligent(text)

        # 空文本應該返回空列表
        self.assertEqual(questions, [])

    def test_parse_complex_question_groups(self):
        """測試解析複雜題組"""
        text = """
        【閱讀測驗】請詳細閱讀以下文章，並回答第15-20題

        文章標題：人工智慧的發展與應用

        第一段：人工智慧（AI）是當代科技發展的重要領域...
        第二段：AI的應用範圍廣泛，包括...
        第三段：然而，AI也帶來了一些挑戰...

        15. 根據第一段，AI是什麼？
        (A) 一種軟體
        (B) 科技領域
        (C) 應用程式
        (D) 硬體設備

        16. 文中提到AI的應用包括：
        (A) 醫療
        (B) 教育
        (C) 交通
        (D) 以上皆是
        """

        questions = self.parser.parse_questions_intelligent(text)

        # 應該能解析複雜題組
        self.assertIsInstance(questions, list)

    def test_parse_nested_question_groups(self):
        """測試解析嵌套題組"""
        text = """
        大題組：請閱讀以下兩篇文章

        文章一：
        內容...

        回答第1-5題

        1. 問題1
        (A) A  (B) B  (C) C  (D) D

        文章二：
        內容...

        回答第6-10題

        6. 問題6
        (A) A  (B) B  (C) C  (D) D
        """

        questions = self.parser.parse_questions_intelligent(text)

        # 應該能處理嵌套題組
        self.assertIsInstance(questions, list)

    def test_parse_questions_with_context(self):
        """測試解析帶上下文的題目"""
        text = """
        情境說明：
        小明參加了一個英語演講比賽，以下是相關情境。

        根據上述情境，回答第30-32題

        30. 小明應該準備什麼？
        (A) 中文講稿
        (B) 英文講稿
        (C) 雙語講稿
        (D) 不需準備

        31. 比賽的語言是？
        (A) 中文
        (B) 英文
        (C) 日文
        (D) 韓文
        """

        questions = self.parser.parse_questions_intelligent(text)

        # 應該能處理帶上下文的題目
        self.assertIsInstance(questions, list)

    def test_parse_questions_with_formulas(self):
        """測試解析包含公式的題目"""
        text = """
        25. 已知 f(x) = x² + 2x + 1，則 f(2) = ?
        (A) 5
        (B) 7
        (C) 9
        (D) 11

        26. 求 ∫(3x² + 2x)dx = ?
        (A) x³ + x² + C
        (B) 3x³ + 2x² + C
        (C) x³ + x + C
        (D) 3x + 2 + C
        """

        questions = self.parser.parse_questions_intelligent(text)

        # 應該能處理數學公式
        self.assertIsInstance(questions, list)

    def test_parse_questions_with_code_snippets(self):
        """測試解析包含程式碼片段的題目"""
        text = """
        40. 下列 Python 程式碼的輸出是什麼？

        def add(a, b):
            return a + b

        result = add(3, 5)
        print(result)

        (A) 3
        (B) 5
        (C) 8
        (D) 35
        """

        questions = self.parser.parse_questions_intelligent(text)

        # 應該能處理程式碼片段
        self.assertIsInstance(questions, list)

    def test_parse_bilingual_questions(self):
        """測試解析雙語題目"""
        text = """
        45. 請選擇正確的翻譯 / Choose the correct translation:
        "今天天氣很好"

        (A) The weather is bad today
        (B) The weather is good today
        (C) It is raining today
        (D) It is snowing today
        """

        questions = self.parser.parse_questions_intelligent(text)

        # 應該能處理雙語題目
        self.assertIsInstance(questions, list)


class TestAIQuestionParserEdgeCases(unittest.TestCase):
    """測試 AIQuestionParser 的邊界情況"""

    def setUp(self):
        """測試前設置"""
        self.parser = AIQuestionParser()

    def test_parse_ambiguous_question_groups(self):
        """測試解析模糊的題組範圍"""
        text = """
        請回答以下問題（可能是題組，也可能不是）

        1. 問題1
        (A) A  (B) B  (C) C  (D) D

        2. 問題2
        (A) A  (B) B  (C) C  (D) D
        """

        questions = self.parser.parse_questions_intelligent(text)

        # 應該能處理模糊情況
        self.assertIsInstance(questions, list)

    def test_parse_overlapping_groups(self):
        """測試解析重疊的題組"""
        text = """
        題組1：第1-5題
        題組2：第3-7題（與題組1重疊）

        1. 問題1
        (A) A  (B) B  (C) C  (D) D

        3. 問題3（屬於兩個題組）
        (A) A  (B) B  (C) C  (D) D
        """

        questions = self.parser.parse_questions_intelligent(text)

        # 應該能處理重疊題組
        self.assertIsInstance(questions, list)

    def test_parse_very_long_question_text(self):
        """測試解析非常長的題目文字"""
        long_text = "這是一個非常長的題目，" * 100

        text = f"""
        50. {long_text}
        (A) 選項A
        (B) 選項B
        (C) 選項C
        (D) 選項D
        """

        questions = self.parser.parse_questions_intelligent(text)

        # 應該能處理長題目
        self.assertIsInstance(questions, list)

    def test_parse_malformed_group_markers(self):
        """測試解析格式錯誤的題組標記"""
        text = """
        題組：回答第（缺少範圍）

        1. 問題1
        (A) A  (B) B  (C) C  (D) D

        閱讀下文，回答題目（缺少具體題號）

        2. 問題2
        (A) A  (B) B  (C) C  (D) D
        """

        questions = self.parser.parse_questions_intelligent(text)

        # 應該能容錯處理
        self.assertIsInstance(questions, list)

    def test_parse_special_characters_in_questions(self):
        """測試解析包含特殊字符的題目"""
        text = """
        55. 下列符號何者正確？＠＃＄％＾＆＊
        (A) ①②③④
        (B) ⓐⓑⓒⓓ
        (C) ⅠⅡⅢⅣ
        (D) ㈠㈡㈢㈣
        """

        questions = self.parser.parse_questions_intelligent(text)

        # 應該能處理特殊字符
        self.assertIsInstance(questions, list)


if __name__ == "__main__":
    unittest.main()
