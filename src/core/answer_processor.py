#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
答案處理器
負責從文字中提取和處理答案
"""

import re
from typing import Dict, List, Optional
from ..utils.logger import logger
from ..utils.exceptions import AnswerProcessingError
from ..utils.config import config_manager


class AnswerProcessor:
    """答案處理器"""
    
    def __init__(self):
        self.logger = logger
        self.config = config_manager.get_processing_config()
    
    def extract_answers(self, text: str) -> Dict[str, str]:
        """
        從文字中提取答案
        
        Args:
            text: 包含答案的文字內容
            
        Returns:
            題號到答案的映射字典
        """
        try:
            self.logger.info("開始提取答案")
            answers = {}
            
            for pattern in self.config.answer_patterns:
                matches = re.findall(pattern, text)
                for match in matches:
                    question_num = match[0]
                    answer = match[1]
                    answers[question_num] = answer
                    self.logger.debug(f"找到答案: 第{question_num}題 = {answer}")
            
            self.logger.success(f"答案提取完成，共找到 {len(answers)} 個答案")
            return answers
            
        except Exception as e:
            error_msg = f"答案提取失敗: {e}"
            self.logger.failure(error_msg)
            raise AnswerProcessingError(error_msg) from e
    
    def extract_corrected_answers(self, text: str) -> Dict[str, str]:
        """
        從文字中提取更正答案
        
        Args:
            text: 包含更正答案的文字內容
            
        Returns:
            題號到更正答案的映射字典
        """
        try:
            self.logger.info("開始提取更正答案")
            corrected_answers = {}
            
            for pattern in self.config.corrected_answer_patterns:
                matches = re.findall(pattern, text)
                for match in matches:
                    question_num = match[0]
                    answer = match[1]
                    corrected_answers[question_num] = answer
                    self.logger.debug(f"找到更正答案: 第{question_num}題 = {answer}")
            
            self.logger.success(f"更正答案提取完成，共找到 {len(corrected_answers)} 個更正答案")
            return corrected_answers
            
        except Exception as e:
            error_msg = f"更正答案提取失敗: {e}"
            self.logger.failure(error_msg)
            raise AnswerProcessingError(error_msg) from e
    
    def merge_answers(self, answers: Dict[str, str], 
                     corrected_answers: Dict[str, str]) -> Dict[str, str]:
        """
        合併答案和更正答案
        
        Args:
            answers: 原始答案
            corrected_answers: 更正答案
            
        Returns:
            最終答案字典（優先使用更正答案）
        """
        try:
            self.logger.info("開始合併答案")
            final_answers = {}
            
            # 先添加原始答案
            for question_num, answer in answers.items():
                final_answers[question_num] = answer
            
            # 用更正答案覆蓋原始答案
            for question_num, corrected_answer in corrected_answers.items():
                if question_num in final_answers:
                    self.logger.debug(f"第{question_num}題答案已更正: {final_answers[question_num]} -> {corrected_answer}")
                final_answers[question_num] = corrected_answer
            
            self.logger.success(f"答案合併完成，共 {len(final_answers)} 個最終答案")
            return final_answers
            
        except Exception as e:
            error_msg = f"答案合併失敗: {e}"
            self.logger.failure(error_msg)
            raise AnswerProcessingError(error_msg) from e
    
    def validate_answer(self, answer: str) -> bool:
        """
        驗證答案格式
        
        Args:
            answer: 要驗證的答案
            
        Returns:
            是否為有效答案格式
        """
        if not answer:
            return False
        
        # 檢查是否為A、B、C、D之一
        return answer.upper() in ['A', 'B', 'C', 'D']
    
    def get_answer_statistics(self, answers: Dict[str, str]) -> Dict[str, int]:
        """
        取得答案統計
        
        Args:
            answers: 答案字典
            
        Returns:
            答案統計字典
        """
        try:
            stats = {'A': 0, 'B': 0, 'C': 0, 'D': 0, '無效': 0}
            
            for question_num, answer in answers.items():
                if self.validate_answer(answer):
                    stats[answer.upper()] += 1
                else:
                    stats['無效'] += 1
            
            self.logger.info(f"答案統計: {stats}")
            return stats
            
        except Exception as e:
            self.logger.warning(f"答案統計計算失敗: {e}")
            return {}