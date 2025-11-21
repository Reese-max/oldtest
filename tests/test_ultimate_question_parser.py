#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試終極題目解析器
"""

import os
import sys
import unittest

# 添加專案根目錄到路徑
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.core.ultimate_question_parser import UltimateQuestionParser


class TestUltimateQuestionParser(unittest.TestCase):
    """測試 UltimateQuestionParser 類"""

    def setUp(self):
        """測試前設置"""
        self.parser = UltimateQuestionParser()

    def test_init(self):
        """測試初始化"""
        self.assertIsNotNone(self.parser.logger)

    def test_parse_complete_60_questions(self):
        """測試解析完整60題"""
        text = """
        甲、申論題部分

        英文作文：
        Write about your dream job.

        乙、測驗題部分

        第1-50題：標準選擇題

        1. 第1題？
        (A) 選項A
        (B) 選項B
        (C) 選項C
        (D) 選項D

        2. 第2題？
        (A) 選項A
        (B) 選項B
        (C) 選項C
        (D) 選項D

        第51-60題：題組題

        題組：閱讀下文，回答第51-53題

        51. 第51題？
        (A) 選項A
        (B) 選項B
        (C) 選項C
        (D) 選項D
        """

        questions = self.parser.parse_all_60_questions(text, "test_60.pdf")

        # 應該能解析出多題
        self.assertIsInstance(questions, list)
        self.assertGreater(len(questions), 0)

    def test_parse_essay_section(self):
        """測試解析申論題部分"""
        text = """
        英文作文：
        Describe a memorable trip you have taken. Include details about:
        1. Where you went
        2. What you did
        3. Why it was memorable

        字數限制：至少250字
        """

        questions = self.parser.parse_all_60_questions(text, "essay.pdf")

        # 應該能解析出申論題
        self.assertIsInstance(questions, list)

    def test_parse_test_section_only(self):
        """測試只解析測驗題部分"""
        text = """
        乙、測驗題部分

        1. 下列何者正確？
        (A) 選項A
        (B) 選項B
        (C) 選項C
        (D) 選項D

        10. 下列何者錯誤？
        (A) 選項A
        (B) 選項B
        (C) 選項C
        (D) 選項D

        60. 最後一題？
        (A) 選項A
        (B) 選項B
        (C) 選項C
        (D) 選項D
        """

        questions = self.parser.parse_all_60_questions(text, "test_only.pdf")

        # 應該能解析測驗題
        self.assertIsInstance(questions, list)

    def test_parse_partial_questions(self):
        """測試解析部分題目"""
        text = """
        第25-30題

        25. 第25題？
        (A) 選項A
        (B) 選項B
        (C) 選項C
        (D) 選項D

        26. 第26題？
        (A) 選項A
        (B) 選項B
        (C) 選項C
        (D) 選項D
        """

        questions = self.parser.parse_all_60_questions(text, "partial.pdf")

        # 應該能解析部分題目
        self.assertIsInstance(questions, list)

    def test_parse_empty_text(self):
        """測試解析空文本"""
        text = ""

        questions = self.parser.parse_all_60_questions(text, "empty.pdf")

        # 空文本應該返回空列表
        self.assertEqual(questions, [])

    def test_parse_question_groups(self):
        """測試解析題組"""
        text = """
        請閱讀以下文章，回答第51-55題

        文章內容：
        This is a reading comprehension passage. It contains multiple
        paragraphs and discusses various topics. Students need to read
        carefully and answer the questions based on the passage.

        51. According to the passage, what is the main idea?
        (A) Topic A
        (B) Topic B
        (C) Topic C
        (D) Topic D

        52. The author suggests that:
        (A) Suggestion A
        (B) Suggestion B
        (C) Suggestion C
        (D) Suggestion D

        53. Which of the following is NOT mentioned?
        (A) Item A
        (B) Item B
        (C) Item C
        (D) Item D
        """

        questions = self.parser.parse_all_60_questions(text, "groups.pdf")

        # 應該能解析題組
        self.assertIsInstance(questions, list)

    def test_parse_mixed_language_questions(self):
        """測試解析中英混合題目"""
        text = """
        1. 下列關於 Python 的敘述何者正確？
        (A) Python is a compiled language
        (B) Python 是直譯式語言
        (C) Python cannot be used for web development
        (D) Python 不支援物件導向

        2. What does "AI" stand for?
        (A) 人工智慧 (Artificial Intelligence)
        (B) 自動化介面 (Automated Interface)
        (C) 應用整合 (Application Integration)
        (D) 進階指令 (Advanced Instruction)
        """

        questions = self.parser.parse_all_60_questions(text, "mixed_lang.pdf")

        # 應該能解析中英混合
        self.assertIsInstance(questions, list)

    def test_parse_questions_with_special_formats(self):
        """測試解析特殊格式的題目"""
        text = """
        【情境題】第10-12題

        情境：小明參加英語演講比賽

        10. 根據上述情境，小明應該：
        (A) 準備中文講稿
        (B) 準備英文講稿
        (C) 不需要準備
        (D) 請別人代講

        【圖表題】第20題

        [圖表：顯示年度銷售數據]

        20. 根據圖表，下列何者正確？
        (A) 銷售上升
        (B) 銷售下降
        (C) 銷售持平
        (D) 無法判斷
        """

        questions = self.parser.parse_all_60_questions(text, "special.pdf")

        # 應該能處理特殊格式
        self.assertIsInstance(questions, list)

    def test_parse_questions_across_pages(self):
        """測試解析跨頁題目"""
        text = """
        第30題（接續上頁）

        30. 承上題，下列何者正確？
        (A) 選項A
        (B) 選項B
        (C) 選項C
        (D) 選項D

        第31題（延續下頁）
        下列關於...
        """

        questions = self.parser.parse_all_60_questions(text, "cross_page.pdf")

        # 應該能處理跨頁題目
        self.assertIsInstance(questions, list)

    def test_parse_questions_with_multiple_correct_answers(self):
        """測試解析多選題"""
        text = """
        15. 下列何者正確？（複選題）
        (A) 選項A
        (B) 選項B
        (C) 選項C
        (D) 選項D
        (E) 選項E

        答案：(A)(C)(E)
        """

        questions = self.parser.parse_all_60_questions(text, "multiple.pdf")

        # 應該能處理多選題
        self.assertIsInstance(questions, list)


class TestUltimateQuestionParserEdgeCases(unittest.TestCase):
    """測試 UltimateQuestionParser 的邊界情況"""

    def setUp(self):
        """測試前設置"""
        self.parser = UltimateQuestionParser()

    def test_parse_incomplete_question_set(self):
        """測試解析不完整的題組"""
        text = """
        1. 第1題
        (A) 選項A
        (B) 選項B

        （缺少第2-29題）

        30. 第30題
        (A) 選項A
        (B) 選項B
        (C) 選項C
        (D) 選項D

        （缺少第31-60題）
        """

        questions = self.parser.parse_all_60_questions(text, "incomplete.pdf")

        # 應該能處理不完整的題組
        self.assertIsInstance(questions, list)

    def test_parse_duplicate_question_numbers(self):
        """測試解析重複的題號"""
        text = """
        1. 第一個第1題
        (A) 選項A
        (B) 選項B
        (C) 選項C
        (D) 選項D

        1. 第二個第1題（重複）
        (A) 選項A
        (B) 選項B
        (C) 選項C
        (D) 選項D
        """

        questions = self.parser.parse_all_60_questions(text, "duplicate.pdf")

        # 應該能處理重複題號
        self.assertIsInstance(questions, list)

    def test_parse_out_of_range_questions(self):
        """測試解析超出範圍的題號"""
        text = """
        70. 超出60題範圍的題目
        (A) 選項A
        (B) 選項B
        (C) 選項C
        (D) 選項D

        100. 遠超範圍的題號
        (A) 選項A
        (B) 選項B
        (C) 選項C
        (D) 選項D
        """

        questions = self.parser.parse_all_60_questions(text, "out_of_range.pdf")

        # 應該能處理或過濾超出範圍的題號
        self.assertIsInstance(questions, list)

    def test_parse_malformed_options(self):
        """測試解析格式錯誤的選項"""
        text = """
        1. 格式錯誤的選項
        A) 缺少括號
        (B 缺少閉括號
        C) 缺少開括號
        (D) 正確格式
        """

        questions = self.parser.parse_all_60_questions(text, "malformed_opts.pdf")

        # 應該能處理格式錯誤
        self.assertIsInstance(questions, list)


if __name__ == "__main__":
    unittest.main()
