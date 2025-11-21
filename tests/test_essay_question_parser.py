#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
申論題解析器測試
測試申論題提取和驗證功能
"""

import unittest

from src.core.essay_question_parser import EssayQuestionParser
from src.core.pdf_structure_analyzer import QuestionType


class TestEssayQuestionParser(unittest.TestCase):
    """申論題解析器測試"""

    def setUp(self):
        """測試前準備"""
        self.parser = EssayQuestionParser()

    def test_parse_chinese_numerals(self):
        """測試解析中文數字編號的申論題"""
        text = """
        一、請說明軟體工程的主要原則。（25 分）
        二、試論述敏捷開發的優點與缺點。（25 分）
        三、請分析設計模式在軟體開發中的重要性。（25 分）
        四、試說明測試驅動開發（TDD）的流程。（25 分）
        """

        questions = self.parser.parse_essay_questions(text)

        # 應該提取到4題
        self.assertEqual(len(questions), 4)

        # 檢查題號
        self.assertEqual(questions[0]["題號"], 1)
        self.assertEqual(questions[1]["題號"], 2)
        self.assertEqual(questions[2]["題號"], 3)
        self.assertEqual(questions[3]["題號"], 4)

        # 檢查題型
        for q in questions:
            self.assertEqual(q["題型"], "申論題")

        # 檢查題目內容包含關鍵字
        self.assertIn("軟體工程", questions[0]["題目"])
        self.assertIn("敏捷開發", questions[1]["題目"])
        self.assertIn("設計模式", questions[2]["題目"])
        self.assertIn("測試驅動開發", questions[3]["題目"])

        # 檢查備註包含分數
        self.assertIn("25", questions[0]["備註"])

    def test_parse_arabic_numerals(self):
        """測試解析阿拉伯數字編號的申論題"""
        text = """
        1. 請說明資料庫正規化的目的。（20 分）
        2. 試論述索引對查詢效能的影響。（20 分）
        3. 請分析ACID特性在交易處理中的重要性。（30 分）
        """

        questions = self.parser.parse_essay_questions(text)

        # 應該提取到3題
        self.assertEqual(len(questions), 3)

        # 檢查題號
        self.assertEqual(questions[0]["題號"], 1)
        self.assertEqual(questions[1]["題號"], 2)
        self.assertEqual(questions[2]["題號"], 3)

    def test_detect_essay_type(self):
        """測試檢測申論題類型"""
        essay_text = """
        一、試說明網路安全的重要性。
        二、請分析防火牆的運作原理。
        """

        # 使用內部方法檢測類型
        question_type = self.parser._detect_question_type(essay_text)

        # 應該識別為申論題
        self.assertEqual(question_type, QuestionType.ESSAY)

    def test_detect_choice_type(self):
        """測試檢測選擇題類型"""
        choice_text = """
        1. 下列何者為正確答案？
        A. 選項一
        B. 選項二
        C. 選項三
        D. 選項四
        """

        # 使用內部方法檢測類型
        question_type = self.parser._detect_question_type(choice_text)

        # 應該識別為選擇題
        self.assertEqual(question_type, QuestionType.CHOICE)

    def test_validate_coverage_complete(self):
        """測試驗證完整題目覆蓋"""
        questions = [{"題號": 1, "題目": "問題一"}, {"題號": 2, "題目": "問題二"}, {"題號": 3, "題目": "問題三"}]

        is_valid, message = self.parser.validate_coverage(questions)

        # 應該是完整的
        self.assertTrue(is_valid)
        self.assertIn("完整", message)

    def test_validate_coverage_incomplete(self):
        """測試驗證不完整題目覆蓋"""
        questions = [
            {"題號": 1, "題目": "問題一"},
            {"題號": 3, "題目": "問題三"},  # 缺少題號2
            {"題號": 4, "題目": "問題四"},
        ]

        is_valid, message = self.parser.validate_coverage(questions)

        # 應該是不完整的
        self.assertFalse(is_valid)
        self.assertIn("遺漏", message)
        self.assertIn("2", message)

    def test_validate_coverage_expected_count_mismatch(self):
        """測試驗證預期題目數量不符"""
        questions = [{"題號": 1, "題目": "問題一"}, {"題號": 2, "題目": "問題二"}]

        is_valid, message = self.parser.validate_coverage(questions, expected_count=3)

        # 應該是不符的
        self.assertFalse(is_valid)
        self.assertIn("不符", message)

    def test_parse_empty_text(self):
        """測試解析空文本"""
        questions = self.parser.parse_essay_questions("")

        # 應該返回空列表
        self.assertEqual(len(questions), 0)

    def test_parse_short_content_filtered(self):
        """測試過短內容被過濾"""
        text = """
        一、短題。
        二、這是一個正常長度的題目，應該被保留下來用於測試。
        """

        questions = self.parser.parse_essay_questions(text)

        # 只有第二題應該被保留（第一題太短）
        self.assertEqual(len(questions), 1)
        self.assertEqual(questions[0]["題號"], 2)

    def test_difficulty_classification(self):
        """測試難度分類"""
        text = """
        一、試說明。（10 分）
        """

        questions = self.parser.parse_essay_questions(text)

        # 申論題通常被標記為困難
        self.assertEqual(questions[0]["難度"], "困難")

    def test_category_classification(self):
        """測試分類"""
        text = """
        一、試說明軟體工程的重要性。（25 分）
        """

        questions = self.parser.parse_essay_questions(text)

        # 申論題的分類應該是申論
        self.assertEqual(questions[0]["分類"], "申論")

    def test_no_question_group(self):
        """測試申論題不應該被標記為題組"""
        text = """
        一、請說明資料結構的基本概念。（25 分）
        """

        questions = self.parser.parse_essay_questions(text)

        # 題組欄位應該為 False
        self.assertFalse(questions[0]["題組"])

    def test_options_empty_for_essay(self):
        """測試申論題選項欄位應為空"""
        text = """
        一、請說明演算法的時間複雜度。（25 分）
        """

        questions = self.parser.parse_essay_questions(text)

        # 所有選項欄位應該為空
        self.assertEqual(questions[0]["選項A"], "")
        self.assertEqual(questions[0]["選項B"], "")
        self.assertEqual(questions[0]["選項C"], "")
        self.assertEqual(questions[0]["選項D"], "")
        self.assertEqual(questions[0]["正確答案"], "")


if __name__ == "__main__":
    unittest.main()
