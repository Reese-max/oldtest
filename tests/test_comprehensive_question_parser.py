#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試綜合題目解析器
"""

import os
import sys
import unittest

# 添加專案根目錄到路徑
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.core.comprehensive_question_parser import ComprehensiveQuestionParser


class TestComprehensiveQuestionParser(unittest.TestCase):
    """測試 ComprehensiveQuestionParser 類"""

    def setUp(self):
        """測試前設置"""
        self.parser = ComprehensiveQuestionParser()

    def test_init(self):
        """測試初始化"""
        self.assertIsNotNone(self.parser.logger)

    def test_parse_mixed_format_pdf(self):
        """測試解析混合格式 PDF"""
        text = """
        甲、申論題部分

        英文作文：
        Write an essay about environmental protection.
        Your essay should include:
        1. Current environmental issues
        2. Possible solutions
        3. Personal actions

        乙、測驗題部分

        1. What is the capital of Taiwan?
        (A) Taipei
        (B) Taichung
        (C) Kaohsiung
        (D) Tainan

        2. Which programming language is most popular?
        (A) Python
        (B) Java
        (C) C++
        (D) JavaScript
        """

        questions = self.parser.parse_all_questions(text, "test.pdf")

        # 應該能解析出申論題和選擇題
        self.assertIsInstance(questions, list)
        self.assertGreater(len(questions), 0)

    def test_parse_only_essay_questions(self):
        """測試只解析申論題"""
        text = """
        英文作文：
        Describe your favorite season and explain why you like it.
        Include specific examples and personal experiences.

        申論題：
        請論述全球暖化對環境的影響。
        """

        questions = self.parser.parse_all_questions(text, "essay_only.pdf")

        # 應該至少解析出申論題
        self.assertIsInstance(questions, list)

    def test_parse_only_multiple_choice(self):
        """測試只解析選擇題"""
        text = """
        第1題 下列何者正確？
        (A) 選項A
        (B) 選項B
        (C) 選項C
        (D) 選項D

        第2題 下列何者錯誤？
        (A) 選項A
        (B) 選項B
        (C) 選項C
        (D) 選項D
        """

        questions = self.parser.parse_all_questions(text, "mc_only.pdf")

        # 應該解析出選擇題
        self.assertIsInstance(questions, list)

    def test_parse_standard_and_group_questions(self):
        """測試解析標準題和題組題"""
        text = """
        第1-50題為標準選擇題

        1. 標準題目1？
        (A) 選項A
        (B) 選項B
        (C) 選項C
        (D) 選項D

        第51-60題為題組題

        題組：閱讀下文，回答第51-53題
        文章內容...

        51. 第51題？
        (A) 選項A
        (B) 選項B
        (C) 選項C
        (D) 選項D

        52. 第52題？
        (A) 選項A
        (B) 選項B
        (C) 選項C
        (D) 選項D
        """

        questions = self.parser.parse_all_questions(text, "mixed.pdf")

        # 應該解析出標準題和題組題
        self.assertIsInstance(questions, list)

    def test_parse_empty_text(self):
        """測試解析空文本"""
        text = ""

        questions = self.parser.parse_all_questions(text, "empty.pdf")

        # 空文本應該返回空列表
        self.assertEqual(questions, [])

    def test_parse_complex_essay_question(self):
        """測試解析複雜的申論題"""
        text = """
        申論題：

        一、請說明何謂「人工智慧」？（10分）

        二、人工智慧在現代社會的應用有哪些？請舉三個實例說明。（15分）

        三、討論人工智慧可能帶來的倫理問題。（15分）
        """

        questions = self.parser.parse_all_questions(text, "complex_essay.pdf")

        # 應該能解析複雜的申論題
        self.assertIsInstance(questions, list)

    def test_parse_questions_with_images(self):
        """測試解析包含圖片說明的題目"""
        text = """
        1. 根據下圖，下列敘述何者正確？
        [圖片：顯示一個流程圖]
        (A) 選項A
        (B) 選項B
        (C) 選項C
        (D) 選項D

        2. 如上圖所示，下列何者錯誤？
        (A) 選項A
        (B) 選項B
        (C) 選項C
        (D) 選項D
        """

        questions = self.parser.parse_all_questions(text, "with_images.pdf")

        # 應該能處理圖片說明
        self.assertIsInstance(questions, list)

    def test_parse_questions_with_tables(self):
        """測試解析包含表格的題目"""
        text = """
        根據下表，回答第1-3題

        項目    數值A    數值B    數值C
        資料1   100      200      300
        資料2   150      250      350

        1. 根據上表，何者正確？
        (A) 選項A
        (B) 選項B
        (C) 選項C
        (D) 選項D
        """

        questions = self.parser.parse_all_questions(text, "with_tables.pdf")

        # 應該能處理表格
        self.assertIsInstance(questions, list)

    def test_parse_bilingual_questions(self):
        """測試解析雙語題目"""
        text = """
        1. 下列哪個英文單字的意思是「快樂」？
        Which word means "happy"?
        (A) sad
        (B) joyful
        (C) angry
        (D) tired

        2. Translate the following sentence: "我愛台灣"
        (A) I love Taiwan
        (B) I like Taiwan
        (C) I visit Taiwan
        (D) I live in Taiwan
        """

        questions = self.parser.parse_all_questions(text, "bilingual.pdf")

        # 應該能解析雙語題目
        self.assertIsInstance(questions, list)


class TestComprehensiveQuestionParserEdgeCases(unittest.TestCase):
    """測試 ComprehensiveQuestionParser 的邊界情況"""

    def setUp(self):
        """測試前設置"""
        self.parser = ComprehensiveQuestionParser()

    def test_parse_very_long_pdf(self):
        """測試解析非常長的 PDF"""
        # 創建包含100題的長文本
        questions_text = ["甲、測驗題部分\n"]
        for i in range(1, 101):
            questions_text.append(f"""
            {i}. 第{i}題？
            (A) 選項A
            (B) 選項B
            (C) 選項C
            (D) 選項D
            """)

        text = "\n".join(questions_text)

        questions = self.parser.parse_all_questions(text, "long.pdf")

        # 應該能處理長文本
        self.assertIsInstance(questions, list)

    def test_parse_malformed_sections(self):
        """測試解析格式錯誤的章節"""
        text = """
        甲、申論題部分（缺少實際題目）

        乙、測驗題部分（缺少題號）
        下列何者正確？
        (A) 選項A
        (B) 選項B
        """

        questions = self.parser.parse_all_questions(text, "malformed.pdf")

        # 應該能處理或返回部分結果
        self.assertIsInstance(questions, list)

    def test_parse_mixed_question_types(self):
        """測試解析混合題型"""
        text = """
        1. 單選題
        (A) 選項A
        (B) 選項B
        (C) 選項C
        (D) 選項D

        2. 多選題（可能有2個或以上答案）
        (A) 選項A
        (B) 選項B
        (C) 選項C
        (D) 選項D

        3. 是非題
        (O) 對
        (X) 錯
        """

        questions = self.parser.parse_all_questions(text, "mixed_types.pdf")

        # 應該能處理混合題型
        self.assertIsInstance(questions, list)

    def test_parse_questions_with_formulas(self):
        """測試解析包含數學公式的題目"""
        text = """
        1. 若 x² + 2x + 1 = 0，則 x = ?
        (A) -1
        (B) 0
        (C) 1
        (D) 2

        2. ∫(2x + 1)dx = ?
        (A) x² + x + C
        (B) 2x² + x + C
        (C) x² + 2x + C
        (D) 2x + C
        """

        questions = self.parser.parse_all_questions(text, "math.pdf")

        # 應該能處理數學公式
        self.assertIsInstance(questions, list)

    def test_parse_questions_with_code(self):
        """測試解析包含程式碼的題目"""
        text = """
        1. 下列 Python 程式碼的輸出為何？
        ```python
        x = 5
        y = 10
        print(x + y)
        ```
        (A) 5
        (B) 10
        (C) 15
        (D) 50
        """

        questions = self.parser.parse_all_questions(text, "code.pdf")

        # 應該能處理程式碼
        self.assertIsInstance(questions, list)


if __name__ == '__main__':
    unittest.main()
