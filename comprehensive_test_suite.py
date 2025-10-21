#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
綜合測試套件 - 確保功能穩定性
提供完整的測試覆蓋，包括單元測試、整合測試和性能測試
"""

import os
import sys
import unittest
import tempfile
import shutil
import json
import time
from typing import List, Dict, Any, Optional
from unittest.mock import Mock, patch, MagicMock
import logging

# 添加模組路徑
sys.path.insert(0, os.path.dirname(__file__))

from enhanced_question_group_processor import EnhancedQuestionGroupProcessor
from enhanced_option_extractor import EnhancedOptionExtractor
from enhanced_question_parser import EnhancedQuestionParser
from enhanced_validation_system import EnhancedValidationSystem
from performance_optimizer import PerformanceOptimizer

class TestEnhancedQuestionGroupProcessor(unittest.TestCase):
    """測試增強版題組處理器"""
    
    def setUp(self):
        self.processor = EnhancedQuestionGroupProcessor()
        self.sample_text = """
        請依下文回答第1題至第3題：
        公務人員考試法規定，公務人員考試分為高等考試、普通考試、初等考試三種。
        高等考試分為一級、二級、三級，普通考試分為一級、二級，初等考試不分級。
        
        1. 公務人員考試法規定，公務人員考試分為幾種？
        (A) 一種 (B) 二種 (C) 三種 (D) 四種
        
        2. 高等考試分為幾級？
        (A) 一級 (B) 二級 (C) 三級 (D) 四級
        
        3. 初等考試分為幾級？
        (A) 一級 (B) 二級 (C) 三級 (D) 不分級
        """
    
    def test_detect_question_groups(self):
        """測試題組檢測"""
        groups = self.processor.detect_question_groups(self.sample_text)
        
        self.assertEqual(len(groups), 1)
        self.assertEqual(groups[0]['start_question'], 1)
        self.assertEqual(groups[0]['end_question'], 3)
        self.assertEqual(groups[0]['question_count'], 3)
    
    def test_extract_questions_from_group(self):
        """測試從題組提取題目"""
        groups = self.processor.detect_question_groups(self.sample_text)
        questions = self.processor.extract_questions_from_group(groups[0])
        
        self.assertEqual(len(questions), 3)
        self.assertTrue(all(q['題組'] for q in questions))
        self.assertTrue(all(q['題組編號'] == '1-3' for q in questions))
    
    def test_validation_question_range(self):
        """測試題號範圍驗證"""
        self.assertTrue(self.processor._validate_question_range(1, 3))
        self.assertFalse(self.processor._validate_question_range(3, 1))
        self.assertFalse(self.processor._validate_question_range(1, 25))
        self.assertFalse(self.processor._validate_question_range(0, 3))

class TestEnhancedOptionExtractor(unittest.TestCase):
    """測試增強版選項提取器"""
    
    def setUp(self):
        self.extractor = EnhancedOptionExtractor()
        self.sample_text = """
        1. 下列何者為公務人員考試法所稱之公務人員？
        (A) 經公務人員考試錄取，接受訓練之人員
        (B) 各級學校之軍訓教官
        (C) 私立學校之專任教師
        (D) 於政府機關擔任臨時人員
        """
    
    def test_extract_options(self):
        """測試選項提取"""
        options = self.extractor.extract_options(self.sample_text)
        
        self.assertIn('A', options)
        self.assertIn('B', options)
        self.assertIn('C', options)
        self.assertIn('D', options)
        self.assertIn('經公務人員考試錄取，接受訓練之人員', options['A'])
    
    def test_validate_options(self):
        """測試選項驗證"""
        valid_options = {
            'A': '選項A內容',
            'B': '選項B內容',
            'C': '選項C內容',
            'D': '選項D內容'
        }
        
        validation = self.extractor.validate_options(valid_options)
        self.assertTrue(validation['is_valid'])
        
        invalid_options = {
            'A': '選項A內容',
            'B': '選項B內容'
        }
        
        validation = self.extractor.validate_options(invalid_options)
        self.assertFalse(validation['is_valid'])

class TestEnhancedQuestionParser(unittest.TestCase):
    """測試增強版題目解析器"""
    
    def setUp(self):
        self.parser = EnhancedQuestionParser()
        self.sample_text = """
        1. 下列何者為公務人員考試法所稱之公務人員？
        經公務人員考試錄取，接受訓練之人員
        各級學校之軍訓教官
        私立學校之專任教師
        於政府機關擔任臨時人員
        
        2. 依公務人員考試法規定，公務人員考試分為幾種？
        一種
        二種
        三種
        四種
        """
    
    def test_parse_questions(self):
        """測試題目解析"""
        questions = self.parser.parse_questions(self.sample_text)
        
        self.assertEqual(len(questions), 2)
        self.assertEqual(questions[0]['題號'], '1')
        self.assertEqual(questions[1]['題號'], '2')
        self.assertTrue(questions[0]['題目'].startswith('下列何者'))
    
    def test_is_not_a_question(self):
        """測試非題目判斷"""
        self.assertTrue(self.parser._is_not_a_question('2501', '代號2501'))
        self.assertTrue(self.parser._is_not_a_question('1', '短'))
        self.assertFalse(self.parser._is_not_a_question('1', '下列何者為正確？'))
    
    def test_get_parsing_statistics(self):
        """測試解析統計"""
        questions = self.parser.parse_questions(self.sample_text)
        stats = self.parser.get_parsing_statistics(questions)
        
        self.assertEqual(stats['total'], 2)
        self.assertEqual(stats['regular_questions'], 2)

class TestEnhancedValidationSystem(unittest.TestCase):
    """測試增強版驗證系統"""
    
    def setUp(self):
        self.validator = EnhancedValidationSystem()
        self.sample_questions = [
            {
                '題號': '1',
                '題目': '下列何者為公務人員考試法所稱之公務人員？',
                '選項A': '經公務人員考試錄取，接受訓練之人員',
                '選項B': '各級學校之軍訓教官',
                '選項C': '私立學校之專任教師',
                '選項D': '於政府機關擔任臨時人員',
                '題型': '選擇題',
                '題組': False
            }
        ]
    
    def test_validate_questions(self):
        """測試題目驗證"""
        result = self.validator.validate_questions(self.sample_questions)
        
        self.assertEqual(result['total_questions'], 1)
        self.assertEqual(result['valid_questions'], 1)
        self.assertEqual(result['invalid_questions'], 0)
        self.assertGreater(result['quality_score'], 0.5)
    
    def test_validate_question_number(self):
        """測試題號驗證"""
        result = self.validator._validate_question_number('1')
        self.assertTrue(result['is_valid'])
        
        result = self.validator._validate_question_number('')
        self.assertFalse(result['is_valid'])
        
        result = self.validator._validate_question_number('abc')
        self.assertFalse(result['is_valid'])
    
    def test_validate_question_text(self):
        """測試題目文字驗證"""
        result = self.validator._validate_question_text('下列何者為正確？')
        self.assertTrue(result['is_valid'])
        
        result = self.validator._validate_question_text('短')
        self.assertFalse(result['is_valid'])
        
        result = self.validator._validate_question_text('代號2501')
        self.assertFalse(result['is_valid'])

class TestPerformanceOptimizer(unittest.TestCase):
    """測試性能優化器"""
    
    def setUp(self):
        self.optimizer = PerformanceOptimizer()
    
    def test_monitor_performance(self):
        """測試性能監控"""
        @self.optimizer.monitor_performance
        def test_func():
            time.sleep(0.01)
            return "test"
        
        result = test_func()
        self.assertEqual(result, "test")
        self.assertGreater(self.optimizer.processing_stats['total_processed'], 0)
    
    def test_optimize_memory_usage(self):
        """測試記憶體使用優化"""
        @self.optimizer.optimize_memory_usage
        def test_func():
            return [i for i in range(1000)]
        
        result = test_func()
        self.assertEqual(len(result), 1000)
    
    def test_parallel_processing(self):
        """測試並行處理"""
        def process_item(item):
            return item * 2
        
        items = list(range(10))
        results = self.optimizer.parallel_processing(items, process_item)
        
        self.assertEqual(len(results), 10)
        self.assertEqual(results[0], 0)
        self.assertEqual(results[1], 2)
    
    def test_batch_processing(self):
        """測試批次處理"""
        def process_batch(batch):
            return [item * 2 for item in batch]
        
        items = list(range(100))
        results = self.optimizer.batch_processing(items, batch_size=10, process_func=process_batch)
        
        self.assertEqual(len(results), 100)
        self.assertEqual(results[0], 0)
        self.assertEqual(results[1], 2)

class TestIntegration(unittest.TestCase):
    """整合測試"""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.processor = EnhancedQuestionGroupProcessor()
        self.parser = EnhancedQuestionParser()
        self.validator = EnhancedValidationSystem()
    
    def tearDown(self):
        shutil.rmtree(self.temp_dir)
    
    def test_end_to_end_processing(self):
        """端到端處理測試"""
        # 創建測試PDF文字
        test_text = """
        請依下文回答第1題至第2題：
        公務人員考試法規定，公務人員考試分為高等考試、普通考試、初等考試三種。
        
        1. 公務人員考試法規定，公務人員考試分為幾種？
        (A) 一種 (B) 二種 (C) 三種 (D) 四種
        
        2. 高等考試分為幾級？
        (A) 一級 (B) 二級 (C) 三級 (D) 四級
        """
        
        # 創建臨時PDF檔案
        pdf_path = os.path.join(self.temp_dir, 'test.pdf')
        with open(pdf_path, 'w', encoding='utf-8') as f:
            f.write(test_text)
        
        # 模擬PDF處理
        with patch('pdfplumber.open') as mock_pdf:
            mock_page = Mock()
            mock_page.extract_text.return_value = test_text
            mock_pdf.return_value.__enter__.return_value.pages = [mock_page]
            
            # 執行處理
            saved_files, stats = self.processor.process_pdf_with_enhanced_groups(
                pdf_path, self.temp_dir
            )
            
            # 驗證結果
            self.assertGreater(len(saved_files), 0)
            self.assertIn('完整題目.csv', saved_files[0])
            self.assertGreater(stats['total_questions'], 0)
    
    def test_validation_integration(self):
        """驗證系統整合測試"""
        # 創建測試題目
        questions = [
            {
                '題號': '1',
                '題目': '下列何者為正確？',
                '選項A': '選項A',
                '選項B': '選項B',
                '選項C': '選項C',
                '選項D': '選項D',
                '題型': '選擇題',
                '題組': False
            }
        ]
        
        # 執行驗證
        result = self.validator.validate_questions(questions)
        
        # 驗證結果
        self.assertEqual(result['total_questions'], 1)
        self.assertEqual(result['valid_questions'], 1)
        self.assertGreater(result['quality_score'], 0.0)

class TestErrorHandling(unittest.TestCase):
    """錯誤處理測試"""
    
    def setUp(self):
        self.processor = EnhancedQuestionGroupProcessor()
        self.parser = EnhancedQuestionParser()
        self.validator = EnhancedValidationSystem()
    
    def test_invalid_input_handling(self):
        """測試無效輸入處理"""
        # 空文字
        questions = self.parser.parse_questions("")
        self.assertEqual(len(questions), 0)
        
        # 無效題目
        invalid_questions = [{'題號': '', '題目': '', '選項A': '', '選項B': '', '選項C': '', '選項D': ''}]
        result = self.validator.validate_questions(invalid_questions)
        self.assertEqual(result['invalid_questions'], 1)
    
    def test_exception_handling(self):
        """測試異常處理"""
        # 測試正則表達式錯誤
        with patch('re.finditer', side_effect=re.error("Invalid pattern")):
            groups = self.processor.detect_question_groups("test")
            self.assertEqual(len(groups), 0)
    
    def test_file_not_found_handling(self):
        """測試檔案不存在處理"""
        with self.assertRaises(Exception):
            self.processor.process_pdf_with_enhanced_groups("nonexistent.pdf", "output")

def run_performance_tests():
    """運行性能測試"""
    print("開始性能測試...")
    
    optimizer = PerformanceOptimizer()
    
    # 測試大量資料處理
    large_data = list(range(10000))
    
    start_time = time.time()
    results = optimizer.parallel_processing(large_data, lambda x: x * 2)
    end_time = time.time()
    
    print(f"並行處理 10000 個項目: {end_time - start_time:.2f}s")
    print(f"結果數量: {len(results)}")
    
    # 測試記憶體使用
    @optimizer.optimize_memory_usage
    def memory_intensive_task():
        return [i for i in range(100000)]
    
    start_memory = psutil.Process().memory_info().rss / 1024 / 1024
    result = memory_intensive_task()
    end_memory = psutil.Process().memory_info().rss / 1024 / 1024
    
    print(f"記憶體使用: {end_memory - start_memory:.2f}MB")
    print(f"結果長度: {len(result)}")
    
    # 獲取性能報告
    report = optimizer.get_performance_report()
    print(f"性能報告: {json.dumps(report, indent=2, ensure_ascii=False)}")

def main():
    """主測試函數"""
    # 設置日誌
    logging.basicConfig(level=logging.INFO)
    
    # 創建測試套件
    test_suite = unittest.TestSuite()
    
    # 添加測試類
    test_classes = [
        TestEnhancedQuestionGroupProcessor,
        TestEnhancedOptionExtractor,
        TestEnhancedQuestionParser,
        TestEnhancedValidationSystem,
        TestPerformanceOptimizer,
        TestIntegration,
        TestErrorHandling
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # 運行測試
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # 運行性能測試
    run_performance_tests()
    
    # 輸出結果
    print(f"\n測試結果:")
    print(f"運行測試: {result.testsRun}")
    print(f"失敗: {len(result.failures)}")
    print(f"錯誤: {len(result.errors)}")
    
    if result.failures:
        print("\n失敗的測試:")
        for test, traceback in result.failures:
            print(f"- {test}: {traceback}")
    
    if result.errors:
        print("\n錯誤的測試:")
        for test, traceback in result.errors:
            print(f"- {test}: {traceback}")
    
    return len(result.failures) + len(result.errors) == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)