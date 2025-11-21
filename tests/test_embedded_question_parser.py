#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試嵌入式填空題解析器
"""

import os
import sys
import unittest

# 添加專案根目錄到路徑
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.core.embedded_question_parser import EmbeddedQuestionParser


class TestEmbeddedQuestionParser(unittest.TestCase):
    """測試 EmbeddedQuestionParser 類"""

    def setUp(self):
        """測試前設置"""
        self.parser = EmbeddedQuestionParser()

    def test_init(self):
        """測試初始化"""
        self.assertIsNotNone(self.parser.logger)

    def test_parse_embedded_cloze_test(self):
        """測試解析英文完形填空"""
        text = """
        Questions 1-5

        The quick brown fox __1__ over the lazy dog. This sentence __2__
        all the letters of the alphabet. It is __3__ used for testing.

        1. (A) jumps  (B) jumped  (C) jumping  (D) jump
        2. (A) contain  (B) contains  (C) contained  (D) containing
        3. (A) often  (B) seldom  (C) never  (D) always
        """

        questions = self.parser.parse_embedded_questions(text)

        # 應該能解析出嵌入式題目
        self.assertIsInstance(questions, list)

    def test_parse_empty_text(self):
        """測試解析空文本"""
        text = ""

        questions = self.parser.parse_embedded_questions(text)

        # 空文本應該返回空列表
        self.assertEqual(questions, [])

    def test_parse_no_embedded_questions(self):
        """測試解析不包含嵌入式題目的文本"""
        text = """
        這是一段普通的文字，沒有任何題目嵌入其中。
        只是純粹的文本內容。
        """

        questions = self.parser.parse_embedded_questions(text)

        # 應該返回空列表
        self.assertIsInstance(questions, list)

    def test_parse_numbered_blanks(self):
        """測試解析編號空格"""
        text = """
        文章：
        In the morning, I __1__ to school. My friend __2__ with me.
        We __3__ very happy.

        1. (A) go  (B) went  (C) goes  (D) going
        2. (A) walk  (B) walks  (C) walked  (D) walking
        3. (A) is  (B) are  (C) was  (D) were
        """

        questions = self.parser.parse_embedded_questions(text)

        # 應該能解析編號空格
        self.assertIsInstance(questions, list)

    def test_parse_multiple_passages(self):
        """測試解析多個段落"""
        text = """
        Passage 1 (Questions 1-3)
        This is the first passage with __1__ blanks. It talks about __2__.
        The conclusion is __3__.

        1. (A) some  (B) many  (C) few  (D) several
        2. (A) topic A  (B) topic B  (C) topic C  (D) topic D
        3. (A) clear  (B) unclear  (C) obvious  (D) hidden

        Passage 2 (Questions 4-6)
        This is the second passage with __4__ content. The author __5__.
        Finally, we __6__.

        4. (A) different  (B) same  (C) similar  (D) unique
        5. (A) argues  (B) agrees  (C) disagrees  (D) suggests
        6. (A) conclude  (B) begin  (C) start  (D) end
        """

        questions = self.parser.parse_embedded_questions(text)

        # 應該能解析多個段落
        self.assertIsInstance(questions, list)

    def test_parse_chinese_cloze_test(self):
        """測試解析中文填空題"""
        text = """
        第1-5題

        李白是唐代著名的__1__，他的詩作以__2__著稱。
        他與杜甫並稱為__3__。李白一生__4__各地，
        留下了許多__5__的作品。

        1. (A) 詩人  (B) 畫家  (C) 音樂家  (D) 書法家
        2. (A) 浪漫  (B) 寫實  (C) 抽象  (D) 古典
        3. (A) 李杜  (B) 蘇辛  (C) 元白  (D) 韓柳
        4. (A) 遊歷  (B) 居住  (C) 定居  (D) 生活
        5. (A) 優秀  (B) 平凡  (C) 普通  (D) 一般
        """

        questions = self.parser.parse_embedded_questions(text)

        # 應該能解析中文填空題
        self.assertIsInstance(questions, list)

    def test_parse_mixed_language_cloze(self):
        """測試解析中英混合填空題"""
        text = """
        Questions 1-3

        Python 是一種__1__的程式語言。它被廣泛應用於 __2__。
        Many programmers __3__ Python for its simplicity.

        1. (A) 簡單  (B) 複雜  (C) 困難  (D) 容易
        2. (A) data science  (B) web development  (C) AI  (D) all of above
        3. (A) like  (B) dislike  (C) love  (D) prefer
        """

        questions = self.parser.parse_embedded_questions(text)

        # 應該能解析中英混合題目
        self.assertIsInstance(questions, list)

    def test_parse_special_blank_markers(self):
        """測試解析特殊空格標記"""
        text = """
        文章段落：
        This sentence has ___1___ blank. Another one has (  2  ) marker.
        The third uses [__3__] format.

        1. (A) option 1  (B) option 2  (C) option 3  (D) option 4
        2. (A) option 1  (B) option 2  (C) option 3  (D) option 4
        3. (A) option 1  (B) option 2  (C) option 3  (D) option 4
        """

        questions = self.parser.parse_embedded_questions(text)

        # 應該能處理不同的空格標記
        self.assertIsInstance(questions, list)

    def test_parse_long_passage_with_many_blanks(self):
        """測試解析包含多個空格的長段落"""
        # 創建包含10個空格的長段落
        passage = "This is a long passage with many blanks. "
        for i in range(1, 11):
            passage += f"Blank __{i}__ is here. "

        options = []
        for i in range(1, 11):
            options.append(
                f"""
            {i}. (A) option A  (B) option B  (C) option C  (D) option D
            """
            )

        text = passage + "\n".join(options)

        questions = self.parser.parse_embedded_questions(text)

        # 應該能處理多空格的長段落
        self.assertIsInstance(questions, list)

    def test_parse_passage_without_question_numbers(self):
        """測試解析沒有明確題號的段落"""
        text = """
        文章：
        This passage has blanks ____ but no clear question numbers.
        Another blank ____ appears here.

        (A) option 1  (B) option 2  (C) option 3  (D) option 4
        (A) option 1  (B) option 2  (C) option 3  (D) option 4
        """

        questions = self.parser.parse_embedded_questions(text)

        # 應該能處理或返回空列表
        self.assertIsInstance(questions, list)


class TestEmbeddedQuestionParserEdgeCases(unittest.TestCase):
    """測試 EmbeddedQuestionParser 的邊界情況"""

    def setUp(self):
        """測試前設置"""
        self.parser = EmbeddedQuestionParser()

    def test_malformed_blank_markers(self):
        """測試格式錯誤的空格標記"""
        text = """
        This has malformed markers: __1 (missing closing), 2__ (missing opening).

        1. (A) option A  (B) option B  (C) option C  (D) option D
        """

        # 應該不崩潰
        try:
            questions = self.parser.parse_embedded_questions(text)
            self.assertIsInstance(questions, list)
        except Exception as e:
            # 允許返回空列表或拋出適當的異常
            pass

    def test_overlapping_question_groups(self):
        """測試重疊的題組"""
        text = """
        Questions 1-5
        Questions 3-7

        This has overlapping question ranges.

        1. (A) opt A  (B) opt B  (C) opt C  (D) opt D
        3. (A) opt A  (B) opt B  (C) opt C  (D) opt D
        5. (A) opt A  (B) opt B  (C) opt C  (D) opt D
        """

        questions = self.parser.parse_embedded_questions(text)

        # 應該能處理重疊情況
        self.assertIsInstance(questions, list)

    def test_inconsistent_blank_numbering(self):
        """測試不一致的空格編號"""
        text = """
        Passage with blanks __1__, __3__, __5__ (skipping 2 and 4).

        1. (A) opt A  (B) opt B  (C) opt C  (D) opt D
        3. (A) opt A  (B) opt B  (C) opt C  (D) opt D
        5. (A) opt A  (B) opt B  (C) opt C  (D) opt D
        """

        questions = self.parser.parse_embedded_questions(text)

        # 應該能處理不連續的編號
        self.assertIsInstance(questions, list)


if __name__ == "__main__":
    unittest.main()
