#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
申論題解析器
專門處理申論題（簡答題/問答題）的提取
確保不遺漏任何題目
"""

import re
from typing import List, Dict, Any, Tuple
from ..utils.logger import logger
from ..utils.constants import (
    CSV_COLUMN_QUESTION_NUM, CSV_COLUMN_QUESTION_TEXT, CSV_COLUMN_QUESTION_TYPE,
    CSV_COLUMN_OPTION_A, CSV_COLUMN_OPTION_B, CSV_COLUMN_OPTION_C, CSV_COLUMN_OPTION_D,
    CSV_COLUMN_CORRECT_ANSWER, CSV_COLUMN_DIFFICULTY, CSV_COLUMN_CATEGORY,
    CSV_COLUMN_QUESTION_GROUP, CSV_COLUMN_NOTES
)


class EssayQuestionParser:
    """申論題解析器"""
    
    def __init__(self):
        self.logger = logger
    
    def parse_essay_questions(self, text: str) -> List[Dict[str, Any]]:
        """
        解析申論題
        
        Args:
            text: PDF提取的文字
            
        Returns:
            申論題列表
        """
        self.logger.info("開始解析申論題")
        
        # 清理文字
        text = self._clean_text(text)
        
        # 檢測題目類型
        question_type = self._detect_question_type(text)
        
        if question_type == "essay":
            questions = self._parse_chinese_numerals(text)
            if not questions:
                questions = self._parse_arabic_numerals(text)
        else:
            questions = []
        
        self.logger.success(f"申論題解析完成，共 {len(questions)} 題")
        return questions
    
    def _clean_text(self, text: str) -> str:
        """清理文字"""
        if not text:
            return ""
        
        # 移除多餘空白
        text = re.sub(r'\s+', ' ', text)
        # 保留換行
        text = text.replace(' \n ', '\n')
        
        return text.strip()
    
    def _detect_question_type(self, text: str) -> str:
        """
        檢測題目類型
        
        Returns:
            "essay" - 申論題
            "choice" - 選擇題
            "unknown" - 未知
        """
        # 申論題特徵
        essay_patterns = [
            r'[一二三四五六七八九十]+、',  # 一、二、三、
            r'試(問|說明|分析|論述)',
            r'請(說明|分析|論述|簡述)',
            r'\d+\s*分\s*\)',  # (25 分)
            r'不必抄題',
            r'應使用本國文字作答',
        ]
        
        essay_count = sum(1 for pattern in essay_patterns 
                         if re.search(pattern, text))
        
        # 選擇題特徵
        choice_patterns = [
            r'[ABCD][\.、。]',
            r'選項',
            r'下列何者',
        ]
        
        choice_count = sum(1 for pattern in choice_patterns 
                          if re.search(pattern, text))
        
        if essay_count >= 2:
            return "essay"
        elif choice_count >= 2:
            return "choice"
        else:
            return "unknown"
    
    def _parse_chinese_numerals(self, text: str) -> List[Dict[str, Any]]:
        """
        解析中文數字編號的申論題
        例如: 一、二、三、四、
        """
        questions = []
        
        # 中文數字映射
        chinese_map = {
            '一': 1, '二': 2, '三': 3, '四': 4, '五': 5,
            '六': 6, '七': 7, '八': 8, '九': 9, '十': 10
        }
        
        # 匹配模式：一、 二、 三、等
        pattern = r'([一二三四五六七八九十]+)、(.*?)(?=(?:[一二三四五六七八九十]+、)|$)'
        matches = list(re.finditer(pattern, text, re.DOTALL))
        
        if not matches:
            return questions
        
        for match in matches:
            chinese_num = match.group(1)
            content = match.group(2).strip()
            
            # 轉換題號
            if chinese_num in chinese_map:
                question_num = chinese_map[chinese_num]
            else:
                continue
            
            # 提取分數
            score_match = re.search(r'[（(](\d+)\s*分[）)]', content)
            score = score_match.group(1) if score_match else ""
            
            # 清理內容（移除分數標記）
            if score_match:
                content = content[:score_match.start()] + content[score_match.end():]
            
            # 移除多餘空白
            content = ' '.join(content.split())
            
            # 跳過過短的內容
            if len(content) < 10:
                self.logger.warning(f"題目 {question_num} 內容過短，跳過")
                continue
            
            question = {
                CSV_COLUMN_QUESTION_NUM: question_num,
                CSV_COLUMN_QUESTION_TEXT: content,
                CSV_COLUMN_QUESTION_TYPE: '申論題',
                CSV_COLUMN_OPTION_A: '',
                CSV_COLUMN_OPTION_B: '',
                CSV_COLUMN_OPTION_C: '',
                CSV_COLUMN_OPTION_D: '',
                CSV_COLUMN_CORRECT_ANSWER: '',
                CSV_COLUMN_DIFFICULTY: '困難',  # 申論題通常較難
                CSV_COLUMN_CATEGORY: '申論',
                CSV_COLUMN_QUESTION_GROUP: False,
                CSV_COLUMN_NOTES: f'配分: {score}分' if score else ''
            }
            
            questions.append(question)
            self.logger.info(f"✓ 提取申論題 {question_num}")
        
        return questions
    
    def _parse_arabic_numerals(self, text: str) -> List[Dict[str, Any]]:
        """
        解析阿拉伯數字編號的申論題
        例如: 1. 2. 3. 4.
        """
        questions = []
        
        # 匹配模式：1. 2. 3.等
        pattern = r'(\d+)[\.、。]\s*(.*?)(?=(?:\d+[\.、。])|$)'
        matches = list(re.finditer(pattern, text, re.DOTALL))
        
        if not matches:
            return questions
        
        for match in matches:
            question_num = int(match.group(1))
            content = match.group(2).strip()
            
            # 跳過不合理的題號
            if question_num < 1 or question_num > 100:
                continue
            
            # 提取分數
            score_match = re.search(r'[（(](\d+)\s*分[）)]', content)
            score = score_match.group(1) if score_match else ""
            
            # 清理內容
            if score_match:
                content = content[:score_match.start()] + content[score_match.end():]
            
            content = ' '.join(content.split())
            
            # 跳過過短的內容
            if len(content) < 10:
                self.logger.warning(f"題目 {question_num} 內容過短，跳過")
                continue
            
            question = {
                '題號': question_num,
                '題目': content,
                '題型': '申論題',
                '選項A': '',
                '選項B': '',
                '選項C': '',
                '選項D': '',
                '正確答案': '',
                '難度': '困難',
                '分類': '申論',
                '題組': False,
                '備註': f'配分: {score}分' if score else ''
            }
            
            questions.append(question)
            self.logger.info(f"✓ 提取申論題 {question_num}")
        
        return questions
    
    def validate_coverage(self, questions: List[Dict[str, Any]], 
                         expected_count: int = None) -> Tuple[bool, str]:
        """
        驗證題目覆蓋率
        
        Args:
            questions: 提取的題目列表
            expected_count: 預期的題目數量
            
        Returns:
            (是否完整, 訊息)
        """
        if not questions:
            return False, "未提取到任何題目"
        
        question_nums = sorted([q['題號'] for q in questions])
        
        # 檢查是否連續
        expected_nums = list(range(1, len(questions) + 1))
        if question_nums != expected_nums:
            missing = set(expected_nums) - set(question_nums)
            return False, f"題號不連續，可能遺漏: {sorted(missing)}"
        
        # 檢查數量
        if expected_count and len(questions) != expected_count:
            return False, f"題目數量不符，預期{expected_count}題，實際{len(questions)}題"
        
        return True, f"完整提取{len(questions)}題"

