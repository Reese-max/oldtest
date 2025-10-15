#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
考古題處理器
主要的處理邏輯整合
"""

import os
from typing import List, Dict, Any, Optional, Tuple
from ..core.pdf_processor import PDFProcessor
from ..core.question_parser import QuestionParser
from ..core.answer_processor import AnswerProcessor
from ..core.csv_generator import CSVGenerator
from ..utils.logger import logger
from ..utils.exceptions import ArchaeologyQuestionsError


class ArchaeologyProcessor:
    """考古題處理器"""
    
    def __init__(self):
        self.logger = logger
        self.pdf_processor = PDFProcessor()
        self.question_parser = QuestionParser()
        self.answer_processor = AnswerProcessor()
        self.csv_generator = CSVGenerator()
    
    def process_pdf(self, pdf_path: str, 
                   answer_pdf_path: Optional[str] = None,
                   corrected_answer_pdf_path: Optional[str] = None,
                   output_dir: str = "output") -> Dict[str, Any]:
        """
        處理PDF檔案，生成CSV
        
        Args:
            pdf_path: PDF檔案路徑
            answer_pdf_path: 答案PDF檔案路徑（可選）
            corrected_answer_pdf_path: 更正答案PDF檔案路徑（可選）
            output_dir: 輸出目錄
            
        Returns:
            處理結果字典
        """
        try:
            self.logger.info(f"開始處理PDF檔案: {pdf_path}")
            
            # 1. 提取PDF文字
            text = self.pdf_processor.extract_text(pdf_path)
            
            # 2. 解析題目
            questions = self.question_parser.parse_questions(text)
            
            if not questions:
                self.logger.warning("未找到任何題目")
                return {'success': False, 'message': '未找到任何題目'}
            
            # 3. 處理答案
            answers = {}
            corrected_answers = {}
            
            if answer_pdf_path and os.path.exists(answer_pdf_path):
                answer_text = self.pdf_processor.extract_text(answer_pdf_path)
                answers = self.answer_processor.extract_answers(answer_text)
            
            if corrected_answer_pdf_path and os.path.exists(corrected_answer_pdf_path):
                corrected_text = self.pdf_processor.extract_text(corrected_answer_pdf_path)
                corrected_answers = self.answer_processor.extract_corrected_answers(corrected_text)
            
            # 4. 生成CSV檔案
            os.makedirs(output_dir, exist_ok=True)
            base_name = os.path.splitext(os.path.basename(pdf_path))[0]
            
            # 生成各種格式的CSV
            csv_files = []
            
            # 一般CSV
            general_csv = os.path.join(output_dir, f"{base_name}.csv")
            self.csv_generator.generate_questions_csv(questions, answers, general_csv)
            csv_files.append(general_csv)
            
            # Google表單CSV
            google_csv = os.path.join(output_dir, f"{base_name}_Google表單.csv")
            self.csv_generator.generate_google_form_csv(questions, answers, corrected_answers, google_csv)
            csv_files.append(google_csv)
            
            # 題組分類CSV
            group_csvs = self.csv_generator.generate_question_groups_csv(questions, answers, output_dir)
            csv_files.extend(group_csvs)
            
            # 統計資訊
            stats = self._generate_statistics(questions, answers, corrected_answers)
            
            result = {
                'success': True,
                'pdf_path': pdf_path,
                'output_dir': output_dir,
                'csv_files': csv_files,
                'questions_count': len(questions),
                'answers_count': len(answers),
                'corrected_answers_count': len(corrected_answers),
                'statistics': stats
            }
            
            self.logger.success(f"PDF處理完成: {len(questions)} 題，{len(csv_files)} 個CSV檔案")
            return result
            
        except Exception as e:
            error_msg = f"PDF處理失敗: {e}"
            self.logger.failure(error_msg)
            return {'success': False, 'message': error_msg}
    
    def process_directory(self, input_dir: str, 
                         output_dir: str = "output") -> Dict[str, Any]:
        """
        處理目錄中的所有PDF檔案
        
        Args:
            input_dir: 輸入目錄
            output_dir: 輸出目錄
            
        Returns:
            處理結果字典
        """
        try:
            self.logger.info(f"開始處理目錄: {input_dir}")
            
            if not os.path.exists(input_dir):
                raise ArchaeologyQuestionsError(f"輸入目錄不存在: {input_dir}")
            
            # 尋找PDF檔案
            pdf_files = []
            for root, dirs, files in os.walk(input_dir):
                for file in files:
                    if file.lower().endswith('.pdf'):
                        pdf_files.append(os.path.join(root, file))
            
            if not pdf_files:
                self.logger.warning("目錄中未找到PDF檔案")
                return {'success': False, 'message': '目錄中未找到PDF檔案'}
            
            # 處理每個PDF檔案
            results = []
            total_questions = 0
            
            for pdf_path in pdf_files:
                self.logger.info(f"處理檔案: {os.path.basename(pdf_path)}")
                
                # 尋找對應的答案檔案
                base_name = os.path.splitext(pdf_path)[0]
                answer_pdf = f"{base_name}_答案.pdf"
                corrected_answer_pdf = f"{base_name}_更正答案.pdf"
                
                result = self.process_pdf(
                    pdf_path,
                    answer_pdf if os.path.exists(answer_pdf) else None,
                    corrected_answer_pdf if os.path.exists(corrected_answer_pdf) else None,
                    output_dir
                )
                
                results.append(result)
                if result['success']:
                    total_questions += result['questions_count']
            
            # 統計結果
            successful_count = sum(1 for r in results if r['success'])
            
            summary = {
                'success': True,
                'input_dir': input_dir,
                'output_dir': output_dir,
                'total_files': len(pdf_files),
                'successful_files': successful_count,
                'total_questions': total_questions,
                'results': results
            }
            
            self.logger.success(f"目錄處理完成: {successful_count}/{len(pdf_files)} 個檔案成功，共 {total_questions} 題")
            return summary
            
        except Exception as e:
            error_msg = f"目錄處理失敗: {e}"
            self.logger.failure(error_msg)
            return {'success': False, 'message': error_msg}
    
    def _generate_statistics(self, questions: List[Dict[str, Any]], 
                           answers: Dict[str, str],
                           corrected_answers: Dict[str, str]) -> Dict[str, Any]:
        """生成統計資訊"""
        try:
            # 題目統計
            regular_questions = [q for q in questions if not q.get('題組', False)]
            group_questions = [q for q in questions if q.get('題組', False)]
            
            # 題組統計
            question_groups = {}
            for q in group_questions:
                group_id = q.get('題組編號', 'unknown')
                if group_id not in question_groups:
                    question_groups[group_id] = 0
                question_groups[group_id] += 1
            
            # 答案統計
            answer_stats = self.answer_processor.get_answer_statistics(answers)
            
            stats = {
                'total_questions': len(questions),
                'regular_questions': len(regular_questions),
                'group_questions': len(group_questions),
                'question_groups': len(question_groups),
                'question_group_details': question_groups,
                'answers_count': len(answers),
                'corrected_answers_count': len(corrected_answers),
                'answer_statistics': answer_stats
            }
            
            return stats
            
        except Exception as e:
            self.logger.warning(f"統計資訊生成失敗: {e}")
            return {}