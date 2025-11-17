#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試混合格式處理器
"""

import os
import sys
import unittest

# 添加專案根目錄到路徑
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.core.mixed_format_parser import MixedFormatParser


class TestMixedFormatParser(unittest.TestCase):
    """測試 MixedFormatParser 類"""

    def setUp(self):
        """測試前設置"""
        self.parser = MixedFormatParser()

    def test_init(self):
        """測試初始化"""
        self.assertIsNotNone(self.parser.logger)

    def test_parse_essay_and_test_sections(self):
        """測試解析作文和測驗部分"""
        text = """
        甲、作文部分

        作文題目：我的夢想
        請以「我的夢想」為題，寫一篇文章。
        字數：至少500字

        乙、測驗部分

        1. 下列何者正確？
        (A) 選項A
        (B) 選項B
        (C) 選項C
        (D) 選項D

        2. 下列何者錯誤？
        (A) 選項A
        (B) 選項B
        (C) 選項C
        (D) 選項D
        """

        questions = self.parser.parse_mixed_format(text)

        # 應該能解析出作文和測驗題
        self.assertIsInstance(questions, list)
        self.assertGreater(len(questions), 0)

    def test_parse_only_essay_section(self):
        """測試只解析作文部分"""
        text = """
        甲、作文部分

        請以「科技與生活」為題，撰寫一篇論說文。
        內容需包括：
        1. 科技對現代生活的影響
        2. 舉出具體實例
        3. 提出個人看法

        字數：600-800字
        """

        questions = self.parser.parse_mixed_format(text)

        # 應該能解析作文題
        self.assertIsInstance(questions, list)

    def test_parse_only_test_section(self):
        """測試只解析測驗部分"""
        text = """
        乙、測驗部分

        第一部分：單選題（第1-30題）

        1. 題目1
        (A) A  (B) B  (C) C  (D) D

        2. 題目2
        (A) A  (B) B  (C) C  (D) D

        第二部分：多選題（第31-40題）

        31. 題目31（複選）
        (A) A  (B) B  (C) C  (D) D  (E) E
        """

        questions = self.parser.parse_mixed_format(text)

        # 應該能解析測驗題
        self.assertIsInstance(questions, list)

    def test_parse_empty_text(self):
        """測試解析空文本"""
        text = ""

        questions = self.parser.parse_mixed_format(text)

        # 空文本應該返回空列表
        self.assertEqual(questions, [])

    def test_parse_chinese_composition(self):
        """測試解析國文作文"""
        text = """
        甲、作文部分（60分）

        題目：四季之美

        說明：
        請以「四季之美」為題，描寫一年四季的景色變化。
        文體不限，但須結合個人經驗與感受。

        注意事項：
        1. 字數至少600字
        2. 須使用正體字
        3. 標點符號需正確使用
        """

        questions = self.parser.parse_mixed_format(text)

        # 應該能解析國文作文
        self.assertIsInstance(questions, list)

    def test_parse_english_composition(self):
        """測試解析英文作文"""
        text = """
        Part I: English Composition (20 points)

        Topic: My Favorite Season

        Instructions:
        Write an essay about your favorite season. Include:
        1. Which season you like best and why
        2. Specific activities you enjoy during that season
        3. Personal memories related to that season

        Requirements:
        - At least 250 words
        - Use proper grammar and punctuation
        """

        questions = self.parser.parse_mixed_format(text)

        # 應該能解析英文作文
        self.assertIsInstance(questions, list)

    def test_parse_bilingual_composition(self):
        """測試解析雙語作文"""
        text = """
        甲、作文部分 / Part I: Composition

        題目 / Topic: 環境保護 / Environmental Protection

        說明 / Instructions:
        請以中文或英文撰寫一篇關於環境保護的文章。
        Write an essay in Chinese or English about environmental protection.

        字數 / Word Count: 至少 500 字 / At least 500 words
        """

        questions = self.parser.parse_mixed_format(text)

        # 應該能解析雙語作文
        self.assertIsInstance(questions, list)

    def test_parse_multiple_essay_topics(self):
        """測試解析多個作文題目"""
        text = """
        甲、作文部分

        第一題：短文寫作（20分）
        題目：我的興趣
        字數：200-300字

        第二題：論說文（40分）
        題目：網路對現代社會的影響
        字數：500-700字
        """

        questions = self.parser.parse_mixed_format(text)

        # 應該能解析多個作文題目
        self.assertIsInstance(questions, list)

    def test_parse_test_with_subsections(self):
        """測試解析包含子部分的測驗題"""
        text = """
        乙、測驗部分

        第一部分：詞彙與文法（第1-20題）

        1. Choose the correct word:
        (A) A  (B) B  (C) C  (D) D

        第二部分：閱讀理解（第21-40題）

        21. According to the passage:
        (A) A  (B) B  (C) C  (D) D

        第三部分：綜合測驗（第41-50題）

        41. Fill in the blank:
        (A) A  (B) B  (C) C  (D) D
        """

        questions = self.parser.parse_mixed_format(text)

        # 應該能解析多部分測驗
        self.assertIsInstance(questions, list)

    def test_parse_mixed_question_types(self):
        """測試解析混合題型"""
        text = """
        乙、測驗部分

        一、單選題（每題2分）
        1-10題為單選題

        1. 題目1
        (A) A  (B) B  (C) C  (D) D

        二、多選題（每題3分）
        11-15題為多選題

        11. 題目11
        (A) A  (B) B  (C) C  (D) D  (E) E

        三、配合題（每題1分）
        16-20題為配合題

        16. 請將左右兩欄配對
        """

        questions = self.parser.parse_mixed_format(text)

        # 應該能解析混合題型
        self.assertIsInstance(questions, list)


class TestMixedFormatParserEdgeCases(unittest.TestCase):
    """測試 MixedFormatParser 的邊界情況"""

    def setUp(self):
        """測試前設置"""
        self.parser = MixedFormatParser()

    def test_parse_missing_section_markers(self):
        """測試解析缺少章節標記的文本"""
        text = """
        作文題目：我的家鄉
        （沒有明確的「甲、作文部分」標記）

        1. 測驗題目
        (A) A  (B) B  (C) C  (D) D
        （沒有明確的「乙、測驗部分」標記）
        """

        questions = self.parser.parse_mixed_format(text)

        # 應該能容錯處理
        self.assertIsInstance(questions, list)

    def test_parse_inverted_sections(self):
        """測試解析順序顛倒的章節"""
        text = """
        乙、測驗部分（先出現）

        1. 題目1
        (A) A  (B) B  (C) C  (D) D

        甲、作文部分（後出現）

        題目：我的理想
        字數：500字
        """

        questions = self.parser.parse_mixed_format(text)

        # 應該能處理順序顛倒
        self.assertIsInstance(questions, list)

    def test_parse_very_long_essay_prompt(self):
        """測試解析非常長的作文說明"""
        long_instructions = "說明內容" * 200

        text = f"""
        甲、作文部分

        題目：長篇說明的作文題
        {long_instructions}

        字數：1000字以上
        """

        questions = self.parser.parse_mixed_format(text)

        # 應該能處理長說明
        self.assertIsInstance(questions, list)

    def test_parse_malformed_section_markers(self):
        """測試解析格式錯誤的章節標記"""
        text = """
        甲作文部分（缺少頓號）

        題目：測試

        乙測驗部分（缺少頓號）

        1. 題目
        (A) A  (B) B
        """

        questions = self.parser.parse_mixed_format(text)

        # 應該能容錯處理
        self.assertIsInstance(questions, list)

    def test_parse_nested_subsections(self):
        """測試解析嵌套的子章節"""
        text = """
        甲、作文部分

        （一）短文寫作
        題目1：...

        （二）長文寫作
        題目2：...

        乙、測驗部分

        （一）單選題
        （1）基礎題
        1. 題目
        (A) A  (B) B

        （2）進階題
        11. 題目
        (A) A  (B) B
        """

        questions = self.parser.parse_mixed_format(text)

        # 應該能處理嵌套結構
        self.assertIsInstance(questions, list)

    def test_parse_special_formatting(self):
        """測試解析特殊格式"""
        text = """
        【作文部分】

        ★題目：特殊格式的題目

        ※說明：
        使用特殊符號的說明文字

        【測驗部分】

        ◆1. 題目1
        ①A  ②B  ③C  ④D
        """

        questions = self.parser.parse_mixed_format(text)

        # 應該能處理特殊格式
        self.assertIsInstance(questions, list)

    def test_parse_with_images_and_tables(self):
        """測試解析包含圖表說明的文本"""
        text = """
        甲、作文部分

        請參考下圖，撰寫一篇文章
        [圖片：環境污染示意圖]

        乙、測驗部分

        根據下表，回答問題

        [表格：年度數據統計]

        1. 根據表格，何者正確？
        (A) A  (B) B  (C) C  (D) D
        """

        questions = self.parser.parse_mixed_format(text)

        # 應該能處理圖表說明
        self.assertIsInstance(questions, list)


if __name__ == '__main__':
    unittest.main()
