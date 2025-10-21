#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
增強版考古題處理器 - 整合所有優化功能
提供完整的題組選取優化和功能強化
"""

import os
import sys
import logging
import time
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import json

# 添加模組路徑
sys.path.insert(0, os.path.dirname(__file__))

from enhanced_question_group_processor import EnhancedQuestionGroupProcessor
from enhanced_option_extractor import EnhancedOptionExtractor
from enhanced_question_parser import EnhancedQuestionParser
from enhanced_validation_system import EnhancedValidationSystem
from enhanced_config_system import EnhancedConfigSystem
from performance_optimizer import PerformanceOptimizer, monitor_performance, optimize_memory_usage

class EnhancedArchaeologyProcessor:
    """增強版考古題處理器 - 整合所有優化功能"""
    
    def __init__(self, config_file: Optional[str] = None):
        self.logger = self._setup_logger()
        self.config = EnhancedConfigSystem(config_file)
        self.performance_optimizer = PerformanceOptimizer(
            max_workers=self.config.get_config('system.max_workers')
        )
        
        # 初始化處理器
        self.question_group_processor = EnhancedQuestionGroupProcessor()
        self.option_extractor = EnhancedOptionExtractor()
        self.question_parser = EnhancedQuestionParser()
        self.validator = EnhancedValidationSystem()
        
        self.logger.info("增強版考古題處理器初始化完成")
    
    def _setup_logger(self) -> logging.Logger:
        """設置日誌記錄器"""
        logger = logging.getLogger('EnhancedArchaeologyProcessor')
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            # 控制台處理器
            console_handler = logging.StreamHandler()
            console_formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            console_handler.setFormatter(console_formatter)
            logger.addHandler(console_handler)
            
            # 檔案處理器
            log_file = self.config.get_config('logging.log_file', 'logs/enhanced_processing.log')
            os.makedirs(os.path.dirname(log_file), exist_ok=True)
            
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            file_handler.setFormatter(file_formatter)
            logger.addHandler(file_handler)
        
        return logger
    
    @monitor_performance
    @optimize_memory_usage
    def process_pdf(self, pdf_path: str, output_dir: str = "output", 
                   answer_pdf_path: Optional[str] = None) -> Dict[str, Any]:
        """
        處理PDF檔案 - 主要方法
        
        Args:
            pdf_path: PDF檔案路徑
            output_dir: 輸出目錄
            answer_pdf_path: 答案PDF檔案路徑
            
        Returns:
            處理結果字典
        """
        self.logger.info(f"開始處理PDF: {pdf_path}")
        
        try:
            # 檢查檔案是否存在
            if not os.path.exists(pdf_path):
                raise FileNotFoundError(f"PDF檔案不存在: {pdf_path}")
            
            # 創建輸出目錄
            os.makedirs(output_dir, exist_ok=True)
            
            # 提取PDF文字
            text = self._extract_pdf_text(pdf_path)
            if not text:
                raise ValueError("無法從PDF中提取文字內容")
            
            self.logger.info(f"PDF文字提取完成: {len(text)} 字元")
            
            # 解析題目
            questions = self._parse_questions(text)
            if not questions:
                raise ValueError("未找到任何題目")
            
            self.logger.info(f"題目解析完成: {len(questions)} 題")
            
            # 驗證題目
            validation_result = self._validate_questions(questions)
            self.logger.info(f"題目驗證完成: {validation_result['valid_questions']} 有效, {validation_result['invalid_questions']} 無效")
            
            # 提取答案（如果有答案PDF）
            if answer_pdf_path and os.path.exists(answer_pdf_path):
                answers = self._extract_answers(answer_pdf_path)
                self._merge_answers(questions, answers)
                self.logger.info(f"答案提取完成: {len(answers)} 個答案")
            
            # 生成輸出檔案
            output_files = self._generate_output_files(questions, pdf_path, output_dir)
            
            # 生成報告
            reports = self._generate_reports(questions, validation_result, pdf_path, output_dir)
            output_files.extend(reports)
            
            # 生成Google表單（如果啟用）
            if self.config.get_config('google_form.enable_generation', True):
                google_files = self._generate_google_form(questions, pdf_path, output_dir)
                output_files.extend(google_files)
            
            # 返回結果
            result = {
                'success': True,
                'pdf_file': pdf_path,
                'output_directory': output_dir,
                'total_questions': len(questions),
                'valid_questions': validation_result['valid_questions'],
                'invalid_questions': validation_result['invalid_questions'],
                'quality_score': validation_result['quality_score'],
                'output_files': output_files,
                'processing_time': time.time(),
                'statistics': self._generate_statistics(questions, validation_result)
            }
            
            self.logger.info(f"PDF處理完成: {len(output_files)} 個輸出檔案")
            return result
            
        except Exception as e:
            error_msg = f"PDF處理失敗: {e}"
            self.logger.error(error_msg)
            return {
                'success': False,
                'error': error_msg,
                'pdf_file': pdf_path,
                'output_directory': output_dir
            }
    
    def _extract_pdf_text(self, pdf_path: str) -> str:
        """提取PDF文字"""
        try:
            import pdfplumber
            
            with pdfplumber.open(pdf_path) as pdf:
                text = ""
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
                
                return text
                
        except Exception as e:
            self.logger.error(f"PDF文字提取失敗: {e}")
            raise
    
    def _parse_questions(self, text: str) -> List[Dict[str, Any]]:
        """解析題目"""
        try:
            # 使用增強版題目解析器
            questions = self.question_parser.parse_questions(
                text,
                min_question_length=self.config.get_config('processing.min_question_length', 10),
                max_question_length=self.config.get_config('processing.max_question_length', 1000)
            )
            
            return questions
            
        except Exception as e:
            self.logger.error(f"題目解析失敗: {e}")
            raise
    
    def _validate_questions(self, questions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """驗證題目"""
        try:
            if not self.config.get_config('validation.enable_validation', True):
                return {
                    'valid_questions': len(questions),
                    'invalid_questions': 0,
                    'quality_score': 1.0,
                    'warnings': [],
                    'errors': []
                }
            
            validation_result = self.validator.validate_questions(questions)
            return validation_result
            
        except Exception as e:
            self.logger.error(f"題目驗證失敗: {e}")
            return {
                'valid_questions': len(questions),
                'invalid_questions': 0,
                'quality_score': 0.0,
                'warnings': [],
                'errors': [str(e)]
            }
    
    def _extract_answers(self, answer_pdf_path: str) -> Dict[str, str]:
        """提取答案"""
        try:
            import pdfplumber
            
            with pdfplumber.open(answer_pdf_path) as pdf:
                text = ""
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
            
            # 使用簡單的答案提取邏輯
            answers = {}
            import re
            
            # 匹配答案模式
            patterns = [
                r'(\d+)\.\s*([ABCD])',
                r'(\d+)\s*([ABCD])',
                r'第(\d+)題\s*([ABCD])',
                r'(\d+)\s*：\s*([ABCD])'
            ]
            
            for pattern in patterns:
                matches = re.findall(pattern, text)
                for match in matches:
                    question_num = match[0]
                    answer = match[1]
                    answers[question_num] = answer
            
            return answers
            
        except Exception as e:
            self.logger.error(f"答案提取失敗: {e}")
            return {}
    
    def _merge_answers(self, questions: List[Dict[str, Any]], answers: Dict[str, str]) -> None:
        """合併答案到題目"""
        for question in questions:
            question_num = question.get('題號', '')
            if question_num in answers:
                question['正確答案'] = answers[question_num]
                question['最終答案'] = answers[question_num]
    
    def _generate_output_files(self, questions: List[Dict[str, Any]], 
                              pdf_path: str, output_dir: str) -> List[str]:
        """生成輸出檔案"""
        output_files = []
        base_name = os.path.splitext(os.path.basename(pdf_path))[0]
        
        try:
            import pandas as pd
            
            # 分類題目
            regular_questions = [q for q in questions if not q.get('題組', False)]
            group_questions = [q for q in questions if q.get('題組', False)]
            
            # 生成CSV檔案
            if regular_questions:
                csv_path = os.path.join(output_dir, f"{base_name}_一般題目.csv")
                pd.DataFrame(regular_questions).to_csv(
                    csv_path, index=False, 
                    encoding=self.config.get_config('output.encoding', 'utf-8-sig')
                )
                output_files.append(csv_path)
                self.logger.info(f"一般題目CSV已生成: {csv_path}")
            
            if group_questions:
                csv_path = os.path.join(output_dir, f"{base_name}_題組題目.csv")
                pd.DataFrame(group_questions).to_csv(
                    csv_path, index=False,
                    encoding=self.config.get_config('output.encoding', 'utf-8-sig')
                )
                output_files.append(csv_path)
                self.logger.info(f"題組題目CSV已生成: {csv_path}")
            
            # 生成完整題目CSV
            if questions:
                csv_path = os.path.join(output_dir, f"{base_name}_完整題目.csv")
                pd.DataFrame(questions).to_csv(
                    csv_path, index=False,
                    encoding=self.config.get_config('output.encoding', 'utf-8-sig')
                )
                output_files.append(csv_path)
                self.logger.info(f"完整題目CSV已生成: {csv_path}")
            
            # 生成JSON檔案
            if self.config.get_config('output.enable_multiple_formats', True):
                json_path = os.path.join(output_dir, f"{base_name}_題目資料.json")
                with open(json_path, 'w', encoding='utf-8') as f:
                    json.dump(questions, f, ensure_ascii=False, indent=2)
                output_files.append(json_path)
                self.logger.info(f"題目資料JSON已生成: {json_path}")
            
        except Exception as e:
            self.logger.error(f"輸出檔案生成失敗: {e}")
        
        return output_files
    
    def _generate_reports(self, questions: List[Dict[str, Any]], 
                         validation_result: Dict[str, Any], 
                         pdf_path: str, output_dir: str) -> List[str]:
        """生成報告"""
        report_files = []
        base_name = os.path.splitext(os.path.basename(pdf_path))[0]
        
        try:
            # 生成驗證報告
            if self.config.get_config('output.enable_validation_report', True):
                report_path = os.path.join(output_dir, f"{base_name}_驗證報告.md")
                report_content = self.validator.generate_validation_report(validation_result)
                with open(report_path, 'w', encoding='utf-8') as f:
                    f.write(report_content)
                report_files.append(report_path)
                self.logger.info(f"驗證報告已生成: {report_path}")
            
            # 生成性能報告
            if self.config.get_config('output.enable_performance_report', True):
                performance_report = self.performance_optimizer.get_performance_report()
                report_path = os.path.join(output_dir, f"{base_name}_性能報告.json")
                with open(report_path, 'w', encoding='utf-8') as f:
                    json.dump(performance_report, f, ensure_ascii=False, indent=2)
                report_files.append(report_path)
                self.logger.info(f"性能報告已生成: {report_path}")
            
        except Exception as e:
            self.logger.error(f"報告生成失敗: {e}")
        
        return report_files
    
    def _generate_google_form(self, questions: List[Dict[str, Any]], 
                             pdf_path: str, output_dir: str) -> List[str]:
        """生成Google表單"""
        google_files = []
        base_name = os.path.splitext(os.path.basename(pdf_path))[0]
        
        try:
            # 這裡可以整合Google表單生成功能
            # 暫時生成一個基本的Google表單CSV
            google_csv_path = os.path.join(output_dir, f"{base_name}_Google表單.csv")
            
            # 轉換為Google表單格式
            google_questions = []
            for question in questions:
                google_question = {
                    '題號': question.get('題號', ''),
                    '題目': question.get('題目', ''),
                    '選項A': question.get('選項A', ''),
                    '選項B': question.get('選項B', ''),
                    '選項C': question.get('選項C', ''),
                    '選項D': question.get('選項D', ''),
                    '正確答案': question.get('正確答案', ''),
                    '題型': '選擇題'
                }
                google_questions.append(google_question)
            
            import pandas as pd
            pd.DataFrame(google_questions).to_csv(
                google_csv_path, index=False,
                encoding=self.config.get_config('output.encoding', 'utf-8-sig')
            )
            google_files.append(google_csv_path)
            self.logger.info(f"Google表單CSV已生成: {google_csv_path}")
            
        except Exception as e:
            self.logger.error(f"Google表單生成失敗: {e}")
        
        return google_files
    
    def _generate_statistics(self, questions: List[Dict[str, Any]], 
                           validation_result: Dict[str, Any]) -> Dict[str, Any]:
        """生成統計資訊"""
        return {
            'total_questions': len(questions),
            'valid_questions': validation_result.get('valid_questions', 0),
            'invalid_questions': validation_result.get('invalid_questions', 0),
            'quality_score': validation_result.get('quality_score', 0.0),
            'question_groups': len([q for q in questions if q.get('題組', False)]),
            'regular_questions': len([q for q in questions if not q.get('題組', False)]),
            'questions_with_answers': len([q for q in questions if q.get('正確答案', '')]),
            'processing_time': datetime.now().isoformat()
        }
    
    def process_directory(self, input_dir: str, output_dir: str = "output") -> Dict[str, Any]:
        """處理目錄中的所有PDF檔案"""
        self.logger.info(f"開始處理目錄: {input_dir}")
        
        try:
            if not os.path.exists(input_dir):
                raise FileNotFoundError(f"輸入目錄不存在: {input_dir}")
            
            # 尋找PDF檔案
            pdf_files = []
            for root, dirs, files in os.walk(input_dir):
                for file in files:
                    if file.lower().endswith('.pdf'):
                        pdf_files.append(os.path.join(root, file))
            
            if not pdf_files:
                raise ValueError("目錄中沒有找到PDF檔案")
            
            self.logger.info(f"找到 {len(pdf_files)} 個PDF檔案")
            
            # 處理每個PDF檔案
            results = []
            successful_files = 0
            failed_files = 0
            
            for pdf_file in pdf_files:
                try:
                    result = self.process_pdf(pdf_file, output_dir)
                    results.append(result)
                    
                    if result['success']:
                        successful_files += 1
                    else:
                        failed_files += 1
                        
                except Exception as e:
                    self.logger.error(f"處理檔案失敗 {pdf_file}: {e}")
                    results.append({
                        'success': False,
                        'error': str(e),
                        'pdf_file': pdf_file
                    })
                    failed_files += 1
            
            # 返回總體結果
            return {
                'success': True,
                'input_directory': input_dir,
                'output_directory': output_dir,
                'total_files': len(pdf_files),
                'successful_files': successful_files,
                'failed_files': failed_files,
                'results': results
            }
            
        except Exception as e:
            error_msg = f"目錄處理失敗: {e}"
            self.logger.error(error_msg)
            return {
                'success': False,
                'error': error_msg,
                'input_directory': input_dir,
                'output_directory': output_dir
            }
    
    def get_system_info(self) -> Dict[str, Any]:
        """獲取系統資訊"""
        return {
            'processor_name': 'Enhanced Archaeology Processor',
            'version': '2.0.0',
            'config_summary': self.config.get_config_summary(),
            'performance_info': self.performance_optimizer.get_system_info(),
            'timestamp': datetime.now().isoformat()
        }

def main():
    """主函數"""
    import argparse
    
    parser = argparse.ArgumentParser(description='增強版考古題處理器')
    parser.add_argument('input', help='輸入PDF檔案或目錄')
    parser.add_argument('-o', '--output', default='output', help='輸出目錄')
    parser.add_argument('-a', '--answer', help='答案PDF檔案路徑')
    parser.add_argument('-c', '--config', help='配置檔案路徑')
    
    args = parser.parse_args()
    
    # 創建處理器
    processor = EnhancedArchaeologyProcessor(args.config)
    
    # 處理輸入
    if os.path.isfile(args.input):
        result = processor.process_pdf(args.input, args.output, args.answer)
    else:
        result = processor.process_directory(args.input, args.output)
    
    # 輸出結果
    if result['success']:
        print("✅ 處理完成！")
        print(f"輸出目錄: {result['output_directory']}")
        if 'output_files' in result:
            print(f"輸出檔案: {len(result['output_files'])} 個")
        if 'total_questions' in result:
            print(f"總題數: {result['total_questions']}")
        if 'quality_score' in result:
            print(f"品質分數: {result['quality_score']:.2f}")
    else:
        print(f"❌ 處理失敗: {result.get('error', '未知錯誤')}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())