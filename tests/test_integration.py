#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
整合測試
測試完整的處理流程
"""

import unittest
import os
import tempfile
import sys
from unittest.mock import patch, MagicMock

# 添加src目錄到路徑
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.api import ArchaeologyAPI
from src.utils.exceptions import ArchaeologyQuestionsError


class TestArchaeologyAPI(unittest.TestCase):
    """考古題API整合測試"""
    
    def setUp(self):
        self.api = ArchaeologyAPI()
    
    @patch('src.processors.archaeology_processor.PDFProcessor.extract_text')
    @patch('src.processors.archaeology_processor.QuestionParser.parse_questions')
    @patch('src.processors.archaeology_processor.AnswerProcessor.extract_answers')
    @patch('src.processors.archaeology_processor.CSVGenerator.generate_questions_csv')
    @patch('src.processors.archaeology_processor.CSVGenerator.generate_google_form_csv')
    def test_process_single_pdf_success(self, mock_google_csv, mock_general_csv, 
                                      mock_extract_answers, mock_parse_questions, 
                                      mock_extract_text):
        """測試成功處理單一PDF"""
        # 模擬返回值
        mock_extract_text.return_value = "測試PDF內容"
        mock_parse_questions.return_value = [
            {
                '題號': '1',
                '題目': '測試題目',
                '選項A': '選項A',
                '選項B': '選項B',
                '選項C': '選項C',
                '選項D': '選項D',
                '題型': '選擇題',
                '題組': False
            }
        ]
        mock_extract_answers.return_value = {'1': 'A'}
        mock_general_csv.return_value = '/tmp/test.csv'
        mock_google_csv.return_value = '/tmp/test_google.csv'
        
        with tempfile.TemporaryDirectory() as temp_dir:
            result = self.api.process_single_pdf(
                'test.pdf', output_dir=temp_dir, generate_script=False
            )
        
        self.assertTrue(result['success'])
        self.assertEqual(result['questions_count'], 1)
        self.assertIn('csv_files', result)
    
    @patch('src.processors.archaeology_processor.PDFProcessor.extract_text')
    def test_process_single_pdf_failure(self, mock_extract_text):
        """測試處理PDF失敗"""
        mock_extract_text.side_effect = Exception("PDF處理失敗")
        
        with tempfile.TemporaryDirectory() as temp_dir:
            result = self.api.process_single_pdf(
                'test.pdf', output_dir=temp_dir, generate_script=False
            )
        
        self.assertFalse(result['success'])
        self.assertIn('PDF處理失敗', result['message'])
    
    @patch('src.processors.archaeology_processor.ArchaeologyProcessor.process_directory')
    def test_process_directory_success(self, mock_process_directory):
        """測試成功處理目錄"""
        # 模擬目錄處理結果
        mock_process_directory.return_value = {
            'success': True,
            'input_dir': '/test',
            'output_dir': '/tmp/output',
            'total_files': 2,
            'successful_files': 2,
            'total_questions': 10,
            'results': [
                {'success': True, 'questions_count': 5, 'csv_files': ['/tmp/file1.csv']},
                {'success': True, 'questions_count': 5, 'csv_files': ['/tmp/file2.csv']}
            ]
        }
        
        with tempfile.TemporaryDirectory() as temp_dir:
            result = self.api.process_directory('/test', temp_dir, generate_script=False)
        
        self.assertTrue(result['success'])
        self.assertEqual(result['total_files'], 2)
        self.assertEqual(result['successful_files'], 2)
        self.assertEqual(result['total_questions'], 10)
    
    def test_process_directory_nonexistent(self):
        """測試處理不存在的目錄"""
        result = self.api.process_directory('nonexistent_dir')
        
        self.assertFalse(result['success'])
        self.assertIn('輸入目錄不存在', result['message'])


class TestEndToEnd(unittest.TestCase):
    """端到端測試"""
    
    def setUp(self):
        self.api = ArchaeologyAPI()
    
    def test_complete_workflow_mock(self):
        """測試完整工作流程（使用模擬）"""
        # 創建測試PDF內容 - 使用更符合真實格式的內容
        test_pdf_content = """1 下列何者正確？這是一個測試題目，用來驗證系統的題目解析功能是否正常運作。
(A) 選項A內容
(B) 選項B內容  
(C) 選項C內容
(D) 選項D內容

2 下列何者錯誤？這是另一個測試題目，用來驗證系統能夠正確處理多個題目的情況。
(A) 選項A內容
(B) 選項B內容
(C) 選項C內容
(D) 選項D內容"""

        test_answer_content = """答案：
第1題 A
第2題 B"""
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # 創建測試PDF檔案
            pdf_path = os.path.join(temp_dir, 'test.pdf')
            answer_path = os.path.join(temp_dir, 'test_答案.pdf')
            
            with open(pdf_path, 'w', encoding='utf-8') as f:
                f.write(test_pdf_content)
            
            with open(answer_path, 'w', encoding='utf-8') as f:
                f.write(test_answer_content)
            
            # 模擬PDF處理
            with patch('src.core.pdf_processor.pdfplumber.open') as mock_open:
                mock_pdf = MagicMock()
                mock_page = MagicMock()
                mock_page.extract_text.return_value = test_pdf_content
                mock_pdf.pages = [mock_page]
                mock_open.return_value.__enter__.return_value = mock_pdf
                
                # 模擬答案PDF處理
                with patch('src.core.pdf_processor.pdfplumber.open') as mock_answer_open:
                    mock_answer_pdf = MagicMock()
                    mock_answer_page = MagicMock()
                    mock_answer_page.extract_text.return_value = test_answer_content
                    mock_answer_pdf.pages = [mock_answer_page]
                    mock_answer_open.return_value.__enter__.return_value = mock_answer_pdf
                    
                    # 執行處理
                    result = self.api.process_single_pdf(
                        pdf_path, answer_path, output_dir=temp_dir, generate_script=False
                    )
            
            # 驗證結果
            self.assertTrue(result['success'])
            self.assertGreater(result['questions_count'], 0)
            self.assertIn('csv_files', result)


if __name__ == '__main__':
    unittest.main()