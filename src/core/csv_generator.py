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
from ..utils.constants import (
    CSV_COLUMN_QUESTION_NUM, CSV_COLUMN_QUESTION_TEXT, CSV_COLUMN_QUESTION_TYPE,
    CSV_COLUMN_OPTION_A, CSV_COLUMN_OPTION_B, CSV_COLUMN_OPTION_C, CSV_COLUMN_OPTION_D,
    CSV_COLUMN_CORRECT_ANSWER, CSV_COLUMN_CORRECTED_ANSWER, CSV_COLUMN_FINAL_ANSWER,
    CSV_COLUMN_DIFFICULTY, CSV_COLUMN_CATEGORY, CSV_COLUMN_QUESTION_GROUP,
    CSV_COLUMN_GROUP_ID, CSV_COLUMN_NOTES,
    DEFAULT_QUESTION_TYPE, DEFAULT_OUTPUT_DIR
)


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

            # 驗證必要欄位
            if questions:
                required_fields = [CSV_COLUMN_QUESTION_NUM, CSV_COLUMN_QUESTION_TEXT, CSV_COLUMN_QUESTION_TYPE]
                first_question = questions[0]
                missing_fields = [field for field in required_fields if field not in first_question]
                if missing_fields:
                    raise CSVGenerationError(f"題目缺少必要欄位: {missing_fields}")

            # 準備CSV資料
            if not questions:
                self.logger.warning("題目列表為空，生成空CSV檔案")
                csv_data = []
            else:
                csv_data = [
                    self._build_question_row(question, answers, include_corrected=False)
                    for question in questions
                ]

            # 建立DataFrame並儲存
            self._save_csv_data(csv_data, output_path)

            self.logger.success(f"✅ 題目CSV生成完成: {output_path}")
            return output_path

        except (IOError, OSError) as e:
            error_msg = f"CSV檔案寫入失敗: {e}"
            self.logger.failure(error_msg)
            raise CSVGenerationError(error_msg) from e
        except pd.errors.EmptyDataError:
            self.logger.warning("生成空CSV檔案")
            # 創建空DataFrame with columns
            self._save_empty_csv(output_path)
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
            csv_data = [
                self._build_question_row(question, answers, corrected_answers, include_corrected=True)
                for question in questions
            ]
            
            # 建立DataFrame並儲存
            self._save_csv_data(csv_data, output_path)
            
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
    
    def _build_question_row(self, question: Dict[str, Any], 
                           answers: Dict[str, str],
                           corrected_answers: Optional[Dict[str, str]] = None,
                           include_corrected: bool = False) -> Dict[str, Any]:
        """
        構建題目CSV行數據
        
        Args:
            question: 題目字典
            answers: 答案字典
            corrected_answers: 更正答案字典（可選）
            include_corrected: 是否包含更正答案欄位
            
        Returns:
            CSV行數據字典
        """
        question_num = question.get(CSV_COLUMN_QUESTION_NUM, '')
        
        row = {
            CSV_COLUMN_QUESTION_NUM: question_num,
            CSV_COLUMN_QUESTION_TEXT: question.get(CSV_COLUMN_QUESTION_TEXT, ''),
            CSV_COLUMN_QUESTION_TYPE: question.get(CSV_COLUMN_QUESTION_TYPE, DEFAULT_QUESTION_TYPE),
            CSV_COLUMN_OPTION_A: question.get(CSV_COLUMN_OPTION_A, ''),
            CSV_COLUMN_OPTION_B: question.get(CSV_COLUMN_OPTION_B, ''),
            CSV_COLUMN_OPTION_C: question.get(CSV_COLUMN_OPTION_C, ''),
            CSV_COLUMN_OPTION_D: question.get(CSV_COLUMN_OPTION_D, ''),
            CSV_COLUMN_CORRECT_ANSWER: answers.get(question_num, ''),
            CSV_COLUMN_DIFFICULTY: self._calculate_difficulty(question),
            CSV_COLUMN_CATEGORY: self._categorize_question(question),
            CSV_COLUMN_QUESTION_GROUP: question.get(CSV_COLUMN_QUESTION_GROUP, False),
            CSV_COLUMN_NOTES: ''
        }
        
        if include_corrected:
            corrected_answers = corrected_answers or {}
            final_answer = corrected_answers.get(question_num, answers.get(question_num, ''))
            row[CSV_COLUMN_CORRECTED_ANSWER] = corrected_answers.get(question_num, '')
            row[CSV_COLUMN_FINAL_ANSWER] = final_answer
            row[CSV_COLUMN_GROUP_ID] = question.get(CSV_COLUMN_GROUP_ID, '')
        
        return row
    
    def _save_csv_data(self, csv_data: List[Dict[str, Any]], output_path: str) -> None:
        """
        保存CSV數據到文件

        Args:
            csv_data: CSV數據列表
            output_path: 輸出文件路徑
        """
        try:
            # 處理空數據情況
            if not csv_data:
                self._save_empty_csv(output_path)
                return

            df = pd.DataFrame(csv_data)
            output_dir = os.path.dirname(output_path) or DEFAULT_OUTPUT_DIR

            # 確保輸出目錄存在
            if output_dir:
                os.makedirs(output_dir, exist_ok=True)

            # 保存CSV
            df.to_csv(output_path, index=False, encoding=self.config.output_encoding,
                     sep=self.config.csv_delimiter)

        except (IOError, OSError) as e:
            raise CSVGenerationError(f"CSV文件寫入失敗: {e}") from e
        except Exception as e:
            raise CSVGenerationError(f"CSV保存錯誤: {e}") from e

    def _save_empty_csv(self, output_path: str) -> None:
        """
        保存空CSV文件（僅包含欄位標題）

        Args:
            output_path: 輸出文件路徑
        """
        # 定義標準欄位
        columns = [
            CSV_COLUMN_QUESTION_NUM,
            CSV_COLUMN_QUESTION_TEXT,
            CSV_COLUMN_QUESTION_TYPE,
            CSV_COLUMN_OPTION_A,
            CSV_COLUMN_OPTION_B,
            CSV_COLUMN_OPTION_C,
            CSV_COLUMN_OPTION_D,
            CSV_COLUMN_CORRECT_ANSWER,
            CSV_COLUMN_DIFFICULTY,
            CSV_COLUMN_CATEGORY,
            CSV_COLUMN_QUESTION_GROUP,
            CSV_COLUMN_NOTES
        ]

        # 創建空DataFrame
        df = pd.DataFrame(columns=columns)
        output_dir = os.path.dirname(output_path) or DEFAULT_OUTPUT_DIR

        if output_dir:
            os.makedirs(output_dir, exist_ok=True)

        df.to_csv(output_path, index=False, encoding=self.config.output_encoding,
                 sep=self.config.csv_delimiter)
    
    def _calculate_difficulty(self, question: Dict[str, Any]) -> str:
        """
        計算題目難度
        
        Args:
            question: 題目字典
            
        Returns:
            難度等級字符串
        """
        from ..utils.constants import (
            DIFFICULTY_HARD_LENGTH, DIFFICULTY_MEDIUM_LENGTH,
            DEFAULT_QUESTION_DIFFICULTY
        )
        
        title = question.get(CSV_COLUMN_QUESTION_TEXT, '')
        title_len = len(title)
        
        if title_len > DIFFICULTY_HARD_LENGTH:
            return '困難'
        elif title_len > DIFFICULTY_MEDIUM_LENGTH:
            return '中等'
        else:
            return DEFAULT_QUESTION_DIFFICULTY
    
    def _categorize_question(self, question: Dict[str, Any]) -> str:
        """
        題目分類
        
        Args:
            question: 題目字典
            
        Returns:
            分類名稱
        """
        from ..utils.constants import CATEGORY_KEYWORDS, DEFAULT_QUESTION_CATEGORY
        
        title = question.get(CSV_COLUMN_QUESTION_TEXT, '')
        
        # 根據關鍵字進行分類
        for category, keywords in CATEGORY_KEYWORDS.items():
            if any(keyword in title for keyword in keywords):
                return category
        
        return DEFAULT_QUESTION_CATEGORY