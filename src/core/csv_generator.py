#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CSV生成器
負責生成各種格式的CSV檔案
"""

import os
import pandas as pd
from typing import List, Dict, Any, Optional
from ..utils.logger import logger
from ..utils.exceptions import CSVGenerationError
from ..utils.config import config_manager


class CSVGenerator:
    """CSV生成器"""
    
    def __init__(self):
        self.logger = logger
        self.config = config_manager.get_processing_config()
        self.google_form_config = config_manager.get_google_form_config()
    
    def generate_questions_csv(self, questions: List[Dict[str, Any]], 
                             answers: Dict[str, str],
                             output_path: str) -> str:
        """
        生成題目CSV檔案
        
        Args:
            questions: 題目列表
            answers: 答案字典
            output_path: 輸出檔案路徑
            
        Returns:
            生成的CSV檔案路徑
        """
        try:
            self.logger.info(f"開始生成題目CSV: {output_path}")
            
            # 準備CSV資料
            csv_data = []
            for question in questions:
                question_num = question.get('題號', '')
                row = {
                    '題號': question_num,
                    '題目': question.get('題目', ''),
                    '題型': question.get('題型', '選擇題'),
                    '選項A': question.get('選項A', ''),
                    '選項B': question.get('選項B', ''),
                    '選項C': question.get('選項C', ''),
                    '選項D': question.get('選項D', ''),
                    '正確答案': answers.get(question_num, ''),
                    '難度': self._calculate_difficulty(question),
                    '分類': self._categorize_question(question),
                    '題組': question.get('題組', False),
                    '備註': ''
                }
                csv_data.append(row)
            
            # 建立DataFrame並儲存
            df = pd.DataFrame(csv_data)
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            df.to_csv(output_path, index=False, encoding=self.config.output_encoding, 
                     sep=self.config.csv_delimiter)
            
            self.logger.success(f"題目CSV生成完成: {output_path}")
            return output_path
            
        except Exception as e:
            error_msg = f"題目CSV生成失敗: {e}"
            self.logger.failure(error_msg)
            raise CSVGenerationError(error_msg) from e
    
    def generate_google_form_csv(self, questions: List[Dict[str, Any]], 
                                answers: Dict[str, str],
                                corrected_answers: Dict[str, str],
                                output_path: str) -> str:
        """
        生成Google表單CSV檔案
        
        Args:
            questions: 題目列表
            answers: 答案字典
            corrected_answers: 更正答案字典
            output_path: 輸出檔案路徑
            
        Returns:
            生成的CSV檔案路徑
        """
        try:
            self.logger.info(f"開始生成Google表單CSV: {output_path}")
            
            # 準備CSV資料
            csv_data = []
            for question in questions:
                question_num = question.get('題號', '')
                
                # 計算最終答案（優先使用更正答案）
                final_answer = corrected_answers.get(question_num, answers.get(question_num, ''))
                
                row = {
                    '題號': question_num,
                    '題目': question.get('題目', ''),
                    '題型': question.get('題型', '選擇題'),
                    '選項A': question.get('選項A', ''),
                    '選項B': question.get('選項B', ''),
                    '選項C': question.get('選項C', ''),
                    '選項D': question.get('選項D', ''),
                    '正確答案': answers.get(question_num, ''),
                    '更正答案': corrected_answers.get(question_num, ''),
                    '最終答案': final_answer,
                    '難度': self._calculate_difficulty(question),
                    '分類': self._categorize_question(question),
                    '題組': question.get('題組', False),
                    '題組編號': question.get('題組編號', ''),
                    '備註': ''
                }
                csv_data.append(row)
            
            # 建立DataFrame並儲存
            df = pd.DataFrame(csv_data)
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            df.to_csv(output_path, index=False, encoding=self.config.output_encoding, 
                     sep=self.config.csv_delimiter)
            
            self.logger.success(f"Google表單CSV生成完成: {output_path}")
            return output_path
            
        except Exception as e:
            error_msg = f"Google表單CSV生成失敗: {e}"
            self.logger.failure(error_msg)
            raise CSVGenerationError(error_msg) from e
    
    def generate_question_groups_csv(self, questions: List[Dict[str, Any]], 
                                   answers: Dict[str, str],
                                   output_dir: str) -> List[str]:
        """
        生成題組分類CSV檔案
        
        Args:
            questions: 題目列表
            answers: 答案字典
            output_dir: 輸出目錄
            
        Returns:
            生成的CSV檔案路徑列表
        """
        try:
            self.logger.info(f"開始生成題組分類CSV: {output_dir}")
            
            # 分離一般題目和題組題目
            regular_questions = [q for q in questions if not q.get('題組', False)]
            group_questions = [q for q in questions if q.get('題組', False)]
            
            generated_files = []
            
            # 生成一般題目CSV
            if regular_questions:
                regular_path = os.path.join(output_dir, "一般題目.csv")
                self.generate_questions_csv(regular_questions, answers, regular_path)
                generated_files.append(regular_path)
            
            # 生成題組題目CSV
            if group_questions:
                group_path = os.path.join(output_dir, "題組題目.csv")
                self.generate_questions_csv(group_questions, answers, group_path)
                generated_files.append(group_path)
            
            # 生成完整題目CSV
            all_path = os.path.join(output_dir, "完整題目.csv")
            self.generate_questions_csv(questions, answers, all_path)
            generated_files.append(all_path)
            
            self.logger.success(f"題組分類CSV生成完成，共 {len(generated_files)} 個檔案")
            return generated_files
            
        except Exception as e:
            error_msg = f"題組分類CSV生成失敗: {e}"
            self.logger.failure(error_msg)
            raise CSVGenerationError(error_msg) from e
    
    def _calculate_difficulty(self, question: Dict[str, Any]) -> str:
        """計算題目難度"""
        title = question.get('題目', '')
        
        # 簡單的難度判斷邏輯
        if len(title) > 100:
            return '困難'
        elif len(title) > 50:
            return '中等'
        else:
            return '簡單'
    
    def _categorize_question(self, question: Dict[str, Any]) -> str:
        """題目分類"""
        title = question.get('題目', '')
        
        # 根據題目內容進行分類
        if '讀音' in title or '發音' in title:
            return '語音'
        elif '錯別字' in title or '字形' in title:
            return '字形'
        elif '成語' in title or '慣用語' in title:
            return '成語'
        elif '文法' in title or '語法' in title:
            return '文法'
        elif '閱讀' in title or '理解' in title:
            return '閱讀理解'
        elif '英文' in title or 'English' in title:
            return '英文'
        elif '憲法' in title or '法律' in title:
            return '法律'
        else:
            return '其他'