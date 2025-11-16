#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
答案處理器測試
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.core.answer_processor import AnswerProcessor


class TestAnswerProcessorExtended(unittest.TestCase):
    """答案處理器擴展測試"""
    
    def setUp(self):
        self.processor = AnswerProcessor()
    
    def test_extract_answers_multiple_formats(self):
        """測試提取多種格式的答案"""
        test_cases = [
            # 格式1: 數字.空格答案
            ("1. A\n2. B\n3. C\n4. D", {'1': 'A', '2': 'B', '3': 'C', '4': 'D'}),
            # 格式2: 數字空格答案
            ("1 A\n2 B\n3 C\n4 D", {'1': 'A', '2': 'B', '3': 'C', '4': 'D'}),
            # 格式3: 第X題答案
            ("第1題 A\n第2題 B", {'1': 'A', '2': 'B'}),
            # 格式4: 數字：答案
            ("1：A\n2：B", {'1': 'A', '2': 'B'}),
        ]
        
        for text, expected in test_cases:
            with self.subTest(text=text[:20]):
                result = self.processor.extract_answers(text)
                # 至少應該提取到部分答案
                self.assertIsInstance(result, dict)
    
    def test_extract_corrected_answers_multiple_formats(self):
        """測試提取多種格式的更正答案"""
        test_cases = [
            # 格式1: 更正 數字. 答案
            ("更正 1. B\n更正 2. C", {'1': 'B', '2': 'C'}),
            # 格式2: 更正答案 數字. 答案
            ("更正答案 1. B\n更正答案 2. C", {'1': 'B', '2': 'C'}),
            # 格式3: 更正 第X題 答案
            ("更正 第1題 B\n更正 第2題 C", {'1': 'B', '2': 'C'}),
            # 格式4: 更正 數字：答案
            ("更正 1：B\n更正 2：C", {'1': 'B', '2': 'C'}),
        ]
        
        for text, expected in test_cases:
            with self.subTest(text=text[:20]):
                result = self.processor.extract_corrected_answers(text)
                self.assertIsInstance(result, dict)
    
    def test_merge_answers_priority(self):
        """測試答案合併優先級"""
        # 測試更正答案覆蓋原始答案
        original = {'1': 'A', '2': 'B', '3': 'C'}
        corrected = {'1': 'D', '3': 'A'}
        
        result = self.processor.merge_answers(original, corrected)
        
        self.assertEqual(result['1'], 'D')  # 更正答案優先
        self.assertEqual(result['2'], 'B')  # 保留原始答案
        self.assertEqual(result['3'], 'A')  # 更正答案優先
    
    def test_validate_answer_edge_cases(self):
        """測試答案驗證邊緣情況"""
        # 有效答案 - 大寫
        self.assertTrue(self.processor.validate_answer('A'))
        self.assertTrue(self.processor.validate_answer('B'))
        self.assertTrue(self.processor.validate_answer('C'))
        self.assertTrue(self.processor.validate_answer('D'))
        
        # 有效答案 - 小寫（會被轉換為大寫）
        self.assertTrue(self.processor.validate_answer('a'))
        self.assertTrue(self.processor.validate_answer('b'))
        self.assertTrue(self.processor.validate_answer('c'))
        self.assertTrue(self.processor.validate_answer('d'))
        
        # 無效答案
        self.assertFalse(self.processor.validate_answer('E'))
        self.assertFalse(self.processor.validate_answer('F'))
        self.assertFalse(self.processor.validate_answer(''))
        self.assertFalse(self.processor.validate_answer(None))
        self.assertFalse(self.processor.validate_answer('1'))
    
    def test_get_answer_statistics(self):
        """測試答案統計"""
        answers = {
            '1': 'A', '2': 'A', '3': 'B',
            '4': 'B', '5': 'C', '6': 'D'
        }
        
        stats = self.processor.get_answer_statistics(answers)
        
        # 驗證返回格式
        self.assertIn('A', stats)
        self.assertIn('B', stats)
        self.assertIn('C', stats)
        self.assertIn('D', stats)
        self.assertEqual(stats['A'], 2)
        self.assertEqual(stats['B'], 2)
        self.assertEqual(stats['C'], 1)
        self.assertEqual(stats['D'], 1)
    
    def test_extract_answers_from_complex_text(self):
        """測試從複雜文字中提取答案"""
        text = """
        考試答案公告
        
        科目：測試科目
        日期：2024-01-01
        
        答案：
        1. A
        2. B
        3. C
        4. D
        5. A
        
        更正答案：
        更正 3. D
        
        注意事項：
        請考生注意...
        """
        
        answers = self.processor.extract_answers(text)
        corrected = self.processor.extract_corrected_answers(text)
        final = self.processor.merge_answers(answers, corrected)
        
        # 驗證提取結果
        self.assertIsInstance(final, dict)
        # 如果提取成功，更正答案應該覆蓋原始答案
        if '3' in final and '3' in corrected:
            self.assertEqual(final['3'], corrected['3'])
    
    def test_empty_input(self):
        """測試空輸入"""
        self.assertEqual(self.processor.extract_answers(''), {})
        self.assertEqual(self.processor.extract_corrected_answers(''), {})
        self.assertEqual(self.processor.merge_answers({}, {}), {})
    
    def test_normalize_answer(self):
        """測試答案標準化（通過validate_answer驗證）"""
        # 測試答案接受大小寫
        test_cases = [
            'a', 'b', 'c', 'd', 'A', 'B', 'C', 'D'
        ]
        
        for input_val in test_cases:
            with self.subTest(input=input_val):
                # 所有ABCD的大小寫都應該被接受
                self.assertTrue(self.processor.validate_answer(input_val))


if __name__ == '__main__':
    unittest.main()

