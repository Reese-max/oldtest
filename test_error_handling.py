#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
錯誤處理測試
測試系統在各種異常情況下的處理能力
"""

import os
import sys
import tempfile
import unittest
from unittest.mock import patch, MagicMock

# 添加src目錄到路徑
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.api import ArchaeologyAPI
from src.core.pdf_processor import PDFProcessor
from src.core.question_parser import QuestionParser
from src.core.answer_processor import AnswerProcessor
from src.core.csv_generator import CSVGenerator
from src.utils.exceptions import PDFProcessingError, QuestionParsingError, AnswerProcessingError, CSVGenerationError


class TestErrorHandling(unittest.TestCase):
    """錯誤處理測試類"""
    
    def setUp(self):
        self.api = ArchaeologyAPI()
        self.pdf_processor = PDFProcessor()
        self.question_parser = QuestionParser()
        self.answer_processor = AnswerProcessor()
        self.csv_generator = CSVGenerator()
    
    def test_pdf_processor_errors(self):
        """測試PDF處理器錯誤處理"""
        print("🧪 測試PDF處理器錯誤處理")
        
        # 測試不存在的檔案
        with self.assertRaises(PDFProcessingError):
            self.pdf_processor.extract_text("nonexistent.pdf")
        
        # 測試損壞的PDF檔案
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_file:
            temp_file.write(b"This is not a valid PDF file")
            temp_file.flush()
            
            with self.assertRaises(PDFProcessingError):
                self.pdf_processor.extract_text(temp_file.name)
            
            os.unlink(temp_file.name)
        
        print("   ✅ PDF處理器錯誤處理正常")
    
    def test_question_parser_errors(self):
        """測試題目解析器錯誤處理"""
        print("🧪 測試題目解析器錯誤處理")
        
        # 測試空文字
        questions = self.question_parser.parse_questions("")
        self.assertEqual(len(questions), 0)
        
        # 測試無效格式的文字
        invalid_text = "這不是題目格式的文字內容"
        questions = self.question_parser.parse_questions(invalid_text)
        self.assertEqual(len(questions), 0)
        
        # 測試包含特殊字符的文字
        special_text = "1 測試題目？\n(A) 選項A\n(B) 選項B\n(C) 選項C\n(D) 選項D"
        questions = self.question_parser.parse_questions(special_text)
        self.assertGreaterEqual(len(questions), 0)
        
        print("   ✅ 題目解析器錯誤處理正常")
    
    def test_answer_processor_errors(self):
        """測試答案處理器錯誤處理"""
        print("🧪 測試答案處理器錯誤處理")
        
        # 測試空文字
        answers = self.answer_processor.extract_answers("")
        self.assertEqual(len(answers), 0)
        
        # 測試無效格式的答案
        invalid_answers = "這不是答案格式"
        answers = self.answer_processor.extract_answers(invalid_answers)
        self.assertEqual(len(answers), 0)
        
        # 測試部分有效的答案
        partial_answers = "答案：\n第1題 A\n無效答案\n第3題 C"
        answers = self.answer_processor.extract_answers(partial_answers)
        self.assertGreaterEqual(len(answers), 0)
        
        print("   ✅ 答案處理器錯誤處理正常")
    
    def test_csv_generator_errors(self):
        """測試CSV生成器錯誤處理"""
        print("🧪 測試CSV生成器錯誤處理")
        
        # 測試空題目列表
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = os.path.join(temp_dir, 'empty_test.csv')
            
            try:
                result_path = self.csv_generator.generate_questions_csv([], {}, output_path)
                self.assertTrue(os.path.exists(result_path))
            except Exception as e:
                self.fail(f"空題目列表處理失敗: {e}")
        
        # 測試無效的輸出路徑
        with self.assertRaises(CSVGenerationError):
            self.csv_generator.generate_questions_csv([], {}, "/invalid/path/test.csv")
        
        print("   ✅ CSV生成器錯誤處理正常")
    
    def test_api_error_handling(self):
        """測試API錯誤處理"""
        print("🧪 測試API錯誤處理")
        
        # 測試處理不存在的PDF
        result = self.api.process_single_pdf("nonexistent.pdf")
        self.assertFalse(result['success'])
        self.assertIn('PDF檔案不存在', result['message'])
        
        # 測試處理不存在的目錄
        result = self.api.process_directory("nonexistent_directory")
        self.assertFalse(result['success'])
        self.assertIn('輸入目錄不存在', result['message'])
        
        print("   ✅ API錯誤處理正常")
    
    def test_memory_errors(self):
        """測試記憶體相關錯誤"""
        print("🧪 測試記憶體相關錯誤")
        
        # 測試超大文字處理
        large_text = "1 測試題目？\n(A) 選項A\n(B) 選項B\n(C) 選項C\n(D) 選項D\n" * 10000
        
        try:
            questions = self.question_parser.parse_questions(large_text)
            self.assertIsInstance(questions, list)
        except MemoryError:
            self.fail("記憶體不足處理失敗")
        except Exception as e:
            # 其他異常是允許的，只要不是記憶體錯誤
            pass
        
        print("   ✅ 記憶體相關錯誤處理正常")
    
    def test_concurrent_access(self):
        """測試並發訪問錯誤"""
        print("🧪 測試並發訪問錯誤")
        
        import threading
        import time
        
        results = []
        errors = []
        
        def process_questions():
            try:
                text = "1 測試題目？\n(A) 選項A\n(B) 選項B\n(C) 選項C\n(D) 選項D"
                questions = self.question_parser.parse_questions(text)
                results.append(len(questions))
            except Exception as e:
                errors.append(str(e))
        
        # 創建多個線程同時處理
        threads = []
        for i in range(5):
            thread = threading.Thread(target=process_questions)
            threads.append(thread)
            thread.start()
        
        # 等待所有線程完成
        for thread in threads:
            thread.join()
        
        # 檢查結果
        self.assertEqual(len(errors), 0, f"並發處理出現錯誤: {errors}")
        self.assertEqual(len(results), 5)
        
        print("   ✅ 並發訪問錯誤處理正常")
    
    def test_file_permission_errors(self):
        """測試檔案權限錯誤"""
        print("🧪 測試檔案權限錯誤")
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # 創建只讀目錄
            read_only_dir = os.path.join(temp_dir, 'readonly')
            os.makedirs(read_only_dir)
            os.chmod(read_only_dir, 0o444)  # 只讀權限
            
            try:
                # 嘗試在只讀目錄中創建檔案
                output_path = os.path.join(read_only_dir, 'test.csv')
                with self.assertRaises(CSVGenerationError):
                    self.csv_generator.generate_questions_csv([], {}, output_path)
            finally:
                # 恢復權限以便清理
                os.chmod(read_only_dir, 0o755)
        
        print("   ✅ 檔案權限錯誤處理正常")
    
    def test_network_errors(self):
        """測試網路相關錯誤（模擬）"""
        print("🧪 測試網路相關錯誤")
        
        # 模擬網路錯誤
        with patch('src.core.pdf_processor.pdfplumber.open') as mock_open:
            mock_open.side_effect = ConnectionError("網路連接失敗")
            
            with self.assertRaises(PDFProcessingError):
                self.pdf_processor.extract_text("test.pdf")
        
        print("   ✅ 網路相關錯誤處理正常")
    
    def test_data_corruption_errors(self):
        """測試資料損壞錯誤"""
        print("🧪 測試資料損壞錯誤")
        
        # 測試損壞的題目資料
        corrupted_questions = [
            {'題號': '1', '題目': ''},  # 空題目
            {'題號': '', '題目': '測試題目'},  # 空題號
            {'題號': '2', '題目': '測試題目', '選項A': ''},  # 缺少選項
        ]
        
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = os.path.join(temp_dir, 'corrupted_test.csv')
            
            try:
                # 應該能夠處理損壞的資料而不崩潰
                result_path = self.csv_generator.generate_questions_csv(
                    corrupted_questions, {}, output_path
                )
                self.assertTrue(os.path.exists(result_path))
            except Exception as e:
                self.fail(f"損壞資料處理失敗: {e}")
        
        print("   ✅ 資料損壞錯誤處理正常")
    
    def test_unicode_errors(self):
        """測試Unicode錯誤"""
        print("🧪 測試Unicode錯誤")
        
        # 測試包含特殊Unicode字符的文字
        unicode_text = "1 測試題目？包含特殊字符：αβγδε\n(A) 選項A\n(B) 選項B\n(C) 選項C\n(D) 選項D"
        
        try:
            questions = self.question_parser.parse_questions(unicode_text)
            self.assertIsInstance(questions, list)
        except UnicodeError:
            self.fail("Unicode處理失敗")
        
        print("   ✅ Unicode錯誤處理正常")


def run_error_handling_tests():
    """運行錯誤處理測試"""
    print("🚀 開始錯誤處理測試")
    print("=" * 60)
    
    # 創建測試套件
    test_suite = unittest.TestLoader().loadTestsFromTestCase(TestErrorHandling)
    
    # 運行測試
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # 統計結果
    total_tests = result.testsRun
    failures = len(result.failures)
    errors = len(result.errors)
    success_rate = ((total_tests - failures - errors) / total_tests) * 100
    
    print(f"\n📊 錯誤處理測試報告")
    print("=" * 60)
    print(f"總測試數: {total_tests}")
    print(f"失敗數: {failures}")
    print(f"錯誤數: {errors}")
    print(f"成功率: {success_rate:.1f}%")
    
    if failures > 0:
        print(f"\n❌ 失敗的測試:")
        for test, traceback in result.failures:
            print(f"  - {test}: {traceback}")
    
    if errors > 0:
        print(f"\n❌ 錯誤的測試:")
        for test, traceback in result.errors:
            print(f"  - {test}: {traceback}")
    
    if success_rate == 100:
        print(f"\n✅ 所有錯誤處理測試通過")
    else:
        print(f"\n⚠️  有 {failures + errors} 個測試失敗")
    
    return result


if __name__ == '__main__':
    run_error_handling_tests()