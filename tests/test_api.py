#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API測試
"""

import unittest
import tempfile
import os
import sys
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.api import ArchaeologyAPI


class TestArchaeologyAPIExtended(unittest.TestCase):
    """考古題API擴展測試"""
    
    def setUp(self):
        self.api = ArchaeologyAPI()
    
    @patch('src.processors.archaeology_processor.EnhancedPDFProcessor.extract_with_best_method')
    @patch('src.processors.archaeology_processor.QuestionParser.parse_questions')
    @patch('src.core.google_script_generator.GoogleScriptGenerator.generate_script')
    @patch('src.processors.archaeology_processor.CSVGenerator.generate_questions_csv')
    @patch('src.processors.archaeology_processor.CSVGenerator.generate_google_form_csv')
    @patch('src.processors.archaeology_processor.CSVGenerator.generate_question_groups_csv')
    def test_process_single_pdf_with_script_generation(
        self, mock_group_csv, mock_google_csv, mock_general_csv,
        mock_script_gen, mock_parse, mock_extract
    ):
        """測試處理單一PDF並生成Script"""
        # 模擬返回值
        mock_extract.return_value = {
            'text': '測試內容',
            'method': 'pdfplumber',
            'score': 0.95
        }
        mock_parse.return_value = [
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
        
        with tempfile.TemporaryDirectory() as temp_dir:
            google_csv_path = os.path.join(temp_dir, 'test_Google表單.csv')
            mock_general_csv.return_value = os.path.join(temp_dir, 'test.csv')
            mock_google_csv.return_value = google_csv_path
            mock_group_csv.return_value = []
            mock_script_gen.return_value = os.path.join(temp_dir, 'test_GoogleAppsScript.js')
            
            result = self.api.process_single_pdf(
                'test.pdf', output_dir=temp_dir, generate_script=True
            )
            
            self.assertTrue(result['success'])
            self.assertIn('script_file', result)
    
    @patch('src.processors.archaeology_processor.ArchaeologyProcessor.process_directory')
    def test_process_directory_with_script(self, mock_process_dir):
        """測試處理目錄並生成Script"""
        mock_process_dir.return_value = {
            'success': True,
            'input_dir': 'test_dir',
            'output_dir': 'output',
            'total_files': 2,
            'successful_files': 2,
            'total_questions': 10,
            'results': [
                {
                    'success': True,
                    'csv_files': [
                        'output/file1.csv',
                        'output/file1_Google表單.csv'
                    ]
                },
                {
                    'success': True,
                    'csv_files': [
                        'output/file2.csv',
                        'output/file2_Google表單.csv'
                    ]
                }
            ]
        }
        
        with patch('src.core.google_script_generator.GoogleScriptGenerator.generate_script') as mock_script:
            mock_script.return_value = 'test_script.js'
            
            result = self.api.process_directory('test_dir', generate_script=True)
            
            self.assertTrue(result['success'])
            self.assertIn('script_files', result)
    
    @patch('src.core.google_script_generator.GoogleScriptGenerator.generate_script')
    def test_generate_script_from_csv(self, mock_script):
        """測試從CSV生成Script"""
        mock_script.return_value = 'test_GoogleAppsScript.js'
        
        result = self.api.generate_script_from_csv('test.csv')
        
        self.assertEqual(result, 'test_GoogleAppsScript.js')
        mock_script.assert_called_once()
    
    @patch('src.core.google_script_generator.GoogleScriptGenerator.generate_script')
    def test_generate_script_from_csv_with_custom_output(self, mock_script):
        """測試從CSV生成Script（自定義輸出路徑）"""
        mock_script.return_value = 'custom_output.js'
        
        result = self.api.generate_script_from_csv('test.csv', 'custom_output.js')
        
        self.assertEqual(result, 'custom_output.js')
        mock_script.assert_called_once_with('test.csv', 'custom_output.js')
    
    @patch('src.core.google_script_generator.GoogleScriptGenerator.generate_script')
    def test_generate_script_failure(self, mock_script):
        """測試Script生成失敗"""
        mock_script.side_effect = Exception("Script生成失敗")
        
        with self.assertRaises(Exception):
            self.api.generate_script_from_csv('test.csv')
    
    @patch('src.processors.archaeology_processor.EnhancedPDFProcessor.extract_with_best_method')
    @patch('src.processors.archaeology_processor.QuestionParser.parse_questions')
    @patch('src.core.google_script_generator.GoogleScriptGenerator.generate_script')
    @patch('src.processors.archaeology_processor.CSVGenerator.generate_questions_csv')
    @patch('src.processors.archaeology_processor.CSVGenerator.generate_google_form_csv')
    @patch('src.processors.archaeology_processor.CSVGenerator.generate_question_groups_csv')
    def test_script_generation_without_google_csv(
        self, mock_group_csv, mock_google_csv, mock_general_csv,
        mock_script_gen, mock_parse, mock_extract
    ):
        """測試Script生成功能"""
        mock_extract.return_value = {
            'text': '測試內容',
            'method': 'pdfplumber',
            'score': 0.95
        }
        mock_parse.return_value = [
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
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # 返回包含Google表單的CSV
            mock_general_csv.return_value = os.path.join(temp_dir, 'test.csv')
            mock_google_csv.return_value = os.path.join(temp_dir, 'test_Google表單.csv')
            mock_group_csv.return_value = []
            mock_script_gen.return_value = os.path.join(temp_dir, 'test_GoogleAppsScript.js')
            
            result = self.api.process_single_pdf(
                'test.pdf', output_dir=temp_dir, generate_script=True
            )
            
            self.assertTrue(result['success'])
            # 驗證Script已生成
            self.assertIn('script_file', result)


if __name__ == '__main__':
    unittest.main()

