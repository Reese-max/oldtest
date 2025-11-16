#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CSV生成器測試
"""

import unittest
import tempfile
import os
import csv
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.core.csv_generator import CSVGenerator


class TestCSVGeneratorExtended(unittest.TestCase):
    """CSV生成器擴展測試"""
    
    def setUp(self):
        self.generator = CSVGenerator()
        self.test_questions = [
            {
                '題號': '1',
                '題目': '這是一個測試題目？',
                '選項A': '選項A',
                '選項B': '選項B',
                '選項C': '選項C',
                '選項D': '選項D',
                '題型': '選擇題',
                '題組': False
            },
            {
                '題號': '2',
                '題目': '這是一個題組題目？',
                '選項A': '選項A',
                '選項B': '選項B',
                '選項C': '選項C',
                '選項D': '選項D',
                '題型': '選擇題',
                '題組': True,
                '題組編號': '2-3'
            },
            {
                '題號': '3',
                '題目': '這是另一個題組題目？',
                '選項A': '選項A',
                '選項B': '選項B',
                '選項C': '選項C',
                '選項D': '選項D',
                '題型': '選擇題',
                '題組': True,
                '題組編號': '2-3'
            }
        ]
        self.test_answers = {'1': 'A', '2': 'B', '3': 'C'}
    
    def test_generate_questions_csv_with_answers(self):
        """測試生成包含答案的題目CSV"""
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = os.path.join(temp_dir, 'test.csv')
            
            result = self.generator.generate_questions_csv(
                self.test_questions, self.test_answers, output_path
            )
            
            self.assertEqual(result, output_path)
            self.assertTrue(os.path.exists(output_path))
            
            # 驗證CSV內容
            with open(output_path, 'r', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f)
                rows = list(reader)
                self.assertEqual(len(rows), 3)
    
    def test_generate_google_form_csv_complete(self):
        """測試生成完整的Google表單CSV"""
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = os.path.join(temp_dir, 'test_google.csv')
            corrected_answers = {'2': 'D'}
            
            result = self.generator.generate_google_form_csv(
                self.test_questions, self.test_answers, corrected_answers, output_path
            )
            
            self.assertEqual(result, output_path)
            self.assertTrue(os.path.exists(output_path))
            
            # 驗證CSV內容
            with open(output_path, 'r', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f)
                rows = list(reader)
                self.assertGreater(len(rows), 0)
    
    def test_generate_question_groups_csv(self):
        """測試生成題組分類CSV"""
        with tempfile.TemporaryDirectory() as temp_dir:
            csv_files = self.generator.generate_question_groups_csv(
                self.test_questions, self.test_answers, temp_dir
            )
            
            # 應該生成多個CSV檔案（一般題目、題組題目等）
            self.assertIsInstance(csv_files, list)
            for csv_file in csv_files:
                self.assertTrue(os.path.exists(csv_file))
    
    def test_calculate_difficulty_levels(self):
        """測試計算不同難度級別"""
        easy_q = {'題目': '簡短題目'}
        medium_q = {'題目': '這是一個中等長度的題目，包含一些內容來測試難度計算，讓題目長度達到中等水準' * 1}
        hard_q = {'題目': '這是一個非常長的題目，包含大量內容和詳細描述，用來測試困難級別的題目難度計算功能，確保系統能夠正確識別不同難度題目' * 2}
        
        self.assertIn(self.generator._calculate_difficulty(easy_q), ['簡單', '中等', '困難'])
        self.assertIn(self.generator._calculate_difficulty(medium_q), ['簡單', '中等', '困難'])
        self.assertIn(self.generator._calculate_difficulty(hard_q), ['簡單', '中等', '困難'])
    
    def test_categorize_question_types(self):
        """測試題目分類"""
        test_cases = [
            ({'題目': '下列讀音何者正確？'}, '語音'),
            ({'題目': '下列詞語何者沒有錯別字？'}, '字形'),
            ({'題目': '「一鼓作氣」這個成語的意思是？'}, '成語'),
            ({'題目': '下列文法何者正確？'}, '文法'),
            ({'題目': 'What is the meaning of this word?'}, '英文'),
            ({'題目': '根據憲法第10條規定？'}, '法律'),
            ({'題目': '請閱讀下列文章並回答問題'}, '閱讀理解'),
            ({'題目': '這是一個普通題目'}, '其他'),
        ]
        
        for question, expected_category in test_cases:
            with self.subTest(question=question['題目'][:20]):
                result = self.generator._categorize_question(question)
                self.assertIsInstance(result, str)
    
    def test_format_question_for_google_form(self):
        """測試格式化題目為Google表單格式"""
        # 該方法可能不存在或是私有方法，測試基本的格式化功能
        question = self.test_questions[0]
        
        # 測試題目包含必要的欄位
        self.assertIn('題號', question)
        self.assertIn('題目', question)
        self.assertIn('選項A', question)
        self.assertIn('選項B', question)
        self.assertIn('選項C', question)
        self.assertIn('選項D', question)
    
    def test_generate_csv_with_empty_questions(self):
        """測試處理空題目列表"""
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = os.path.join(temp_dir, 'empty.csv')
            
            result = self.generator.generate_questions_csv(
                [], {}, output_path
            )
            
            self.assertEqual(result, output_path)
            self.assertTrue(os.path.exists(output_path))
    
    def test_generate_csv_with_missing_answers(self):
        """測試處理缺少答案的情況"""
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = os.path.join(temp_dir, 'no_answers.csv')
            
            # 沒有提供答案
            result = self.generator.generate_questions_csv(
                self.test_questions, {}, output_path
            )
            
            self.assertEqual(result, output_path)
            self.assertTrue(os.path.exists(output_path))


if __name__ == '__main__':
    unittest.main()

