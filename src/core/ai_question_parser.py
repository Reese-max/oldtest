#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI輔助題目解析器
使用正則表達式和AI結合的方式來解析複雜格式的題目
"""

import re
from typing import List, Dict, Any, Optional
from ..utils.logger import logger
from ..utils.config import config_manager
from ..utils.constants import (
    CSV_COLUMN_QUESTION_NUM, CSV_COLUMN_QUESTION_TEXT, CSV_COLUMN_QUESTION_TYPE,
    CSV_COLUMN_OPTION_A, CSV_COLUMN_OPTION_B, CSV_COLUMN_OPTION_C, CSV_COLUMN_OPTION_D,
    CSV_COLUMN_QUESTION_GROUP, CSV_COLUMN_GROUP_ID,
    DEFAULT_QUESTION_TYPE
)


class AIQuestionParser:
    """AI輔助的智能題目解析器"""
    
    def __init__(self):
        self.logger = logger
        self.config = config_manager.get_processing_config()
    
    def parse_questions_intelligent(self, text: str) -> List[Dict[str, Any]]:
        """
        智能解析題目，結合多種策略
        
        Args:
            text: PDF提取的文字
            
        Returns:
            題目列表
        """
        questions = []
        
        # 策略1: 檢測題組
        question_groups = self._detect_question_groups_enhanced(text)
        if question_groups:
            self.logger.info(f"檢測到 {len(question_groups)} 個題組")
            for group in question_groups:
                group_questions = self._parse_question_group_enhanced(
                    text, group['start'], group['end'], group.get('context', '')
                )
                questions.extend(group_questions)
        
        # 策略2: 解析一般題目（排除已經在題組中的題號）
        parsed_question_nums = {q['題號'] for q in questions}
        regular_questions = self._parse_regular_questions_enhanced(text, parsed_question_nums)
        questions.extend(regular_questions)
        
        # 策略3: 如果還是沒找到題目，使用AI輔助
        if len(questions) < 3:
            self.logger.warning("常規方法提取題目不足，嘗試AI輔助解析")
            ai_questions = self._parse_with_ai_assistance(text)
            questions.extend(ai_questions)
        
        # 去重和排序
        questions = self._deduplicate_and_sort(questions)
        
        self.logger.info(f"✅ 智能解析完成，共 {len(questions)} 題")
        return questions
    
    def _detect_question_groups_enhanced(self, text: str) -> List[Dict[str, Any]]:
        """增強的題組檢測"""
        groups = []
        
        # 中文題組格式
        patterns = [
            r'請依下文回答第(\d+)題至第(\d+)題[：:]?',
            r'第(\d+)題至第(\d+)題[，,]?請依',
            r'根據以下.*?回答第(\d+)題至第(\d+)題',
            r'第(\d+)[－\-~](\d+)題',
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, text)
            for match in matches:
                start_num = int(match.group(1))
                end_num = int(match.group(2))
                
                # 提取題組上下文（前後500字）
                context_start = max(0, match.start() - 100)
                context_end = min(len(text), match.end() + 1500)
                context = text[context_start:context_end]
                
                groups.append({
                    'start': start_num,
                    'end': end_num,
                    'context': context,
                    'pattern': pattern
                })
                
                self.logger.info(f"檢測到題組: 第{start_num}題至第{end_num}題")
        
        return groups
    
    def _parse_question_group_enhanced(
        self, 
        text: str, 
        start_num: int, 
        end_num: int,
        context: str = ""
    ) -> List[Dict[str, Any]]:
        """增強的題組解析"""
        questions = []
        
        # 使用上下文文字
        search_text = context if context else text
        
        # Create option column mapping
        option_columns = [CSV_COLUMN_OPTION_A, CSV_COLUMN_OPTION_B,
                        CSV_COLUMN_OPTION_C, CSV_COLUMN_OPTION_D]

        for question_num in range(start_num, end_num + 1):
            question_data = {
                CSV_COLUMN_QUESTION_NUM: str(question_num),
                CSV_COLUMN_QUESTION_TEXT: '',
                CSV_COLUMN_OPTION_A: '',
                CSV_COLUMN_OPTION_B: '',
                CSV_COLUMN_OPTION_C: '',
                CSV_COLUMN_OPTION_D: '',
                CSV_COLUMN_QUESTION_TYPE: DEFAULT_QUESTION_TYPE,
                CSV_COLUMN_QUESTION_GROUP: True,
                CSV_COLUMN_GROUP_ID: f"{start_num}-{end_num}"
            }

            # 多種題號格式匹配
            question_text = self._extract_question_text(search_text, question_num)

            if question_text:
                question_data[CSV_COLUMN_QUESTION_TEXT] = question_text[:500]  # 限制長度

                # 提取選項
                options = self._extract_options_enhanced(question_text)
                for i in range(min(len(options), 4)):
                    question_data[option_columns[i]] = options[i]
                
                # 驗證題目有效性
                if self._validate_question(question_data):
                    questions.append(question_data)
                else:
                    self.logger.warning(f"題目 {question_num} 驗證失敗，跳過")
        
        return questions
    
    def _extract_question_text(self, text: str, question_num: int) -> str:
        """提取指定題號的題目文字"""
        patterns = [
            # 純數字格式: "41 選項1 選項2..."
            rf'^{question_num}\s+(.+?)(?=^{question_num + 1}\s+|\Z)',
            # 第XX題格式
            rf'第{question_num}題[：:]?\s*(.+?)(?=第{question_num + 1}題|\Z)',
            # 數字加句點: "41. 題目內容"
            rf'^{question_num}\.\s+(.+?)(?=^{question_num + 1}\.|\Z)',
            # 括號格式: "(41) 題目內容"
            rf'\({question_num}\)\s+(.+?)(?=\({question_num + 1}\)|\Z)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.MULTILINE | re.DOTALL)
            if match:
                return match.group(1).strip()
        
        # 如果沒找到，嘗試找包含該題號的段落
        lines = text.split('\n')
        for i, line in enumerate(lines):
            if str(question_num) in line:
                # 取接下來的10行
                question_lines = lines[i:min(i+10, len(lines))]
                return '\n'.join(question_lines).strip()
        
        return ""
    
    def _extract_options_enhanced(self, question_text: str) -> List[str]:
        """增強的選項提取"""
        options = []
        
        # 策略1: 標準括號格式 (A) (B) (C) (D)
        bracket_patterns = [
            r'[（(]A[）)]\s*(.*?)(?=[（(]B[）)]|$)',
            r'[（(]B[）)]\s*(.*?)(?=[（(]C[）)]|$)',
            r'[（(]C[）)]\s*(.*?)(?=[（(]D[）)]|$)',
            r'[（(]D[）)]\s*(.*?)(?=[（(]E[）)]|$)',
        ]
        
        for pattern in bracket_patterns:
            match = re.search(pattern, question_text, re.DOTALL)
            if match:
                option_text = match.group(1).strip()
                if option_text:
                    options.append(option_text)
        
        if len(options) >= 2:
            return options[:4]
        
        # 策略2: 英文選項 - 四個單詞一行
        lines = question_text.split('\n')
        for line in lines:
            line = line.strip()
            words = line.split()
            
            # 檢查是否為4個英文單詞
            if len(words) == 4:
                # 確保都是字母且長度合理
                if all(w.isalpha() and 2 < len(w) < 20 for w in words):
                    return words
            
            # 也可能是3個單詞
            if len(words) == 3:
                if all(w.isalpha() and 3 < len(w) < 20 for w in words):
                    return words + ['']  # 補齊第4個
        
        # 策略3: 中文選項 - 空格分隔的長句子
        for line in lines:
            line = line.strip()
            if not line or '？' in line or '?' in line:
                continue
            
            # 如果這行有多個長片段（可能是選項）
            segments = re.split(r'\s{2,}', line)  # 兩個以上空格分隔
            if 2 <= len(segments) <= 4:
                # 檢查每個片段是否足夠長
                if all(len(seg) > 5 for seg in segments):
                    return segments[:4]
        
        # 策略4: 使用字串相似度分組
        # 這裡簡化實作，實際可以用Levenshtein距離
        
        return options[:4]
    
    def _parse_regular_questions_enhanced(
        self, 
        text: str, 
        exclude_nums: set
    ) -> List[Dict[str, Any]]:
        """增強的一般題目解析"""
        questions = []
        
        # 找出所有可能的題號
        question_patterns = [
            r'^(\d+)[\s\.]',  # 行首數字
            r'第(\d+)題',      # 第XX題
            r'\((\d+)\)',     # (XX)
        ]
        
        found_nums = set()
        for pattern in question_patterns:
            matches = re.finditer(pattern, text, re.MULTILINE)
            for match in matches:
                num = int(match.group(1))
                if 1 <= num <= 100 and num not in exclude_nums:
                    found_nums.add(num)
        
        # 對每個找到的題號嘗試提取
        for num in sorted(found_nums):
            question_text = self._extract_question_text(text, num)
            
            if question_text and len(question_text) > 10:
                # Create option column mapping
                option_columns = [CSV_COLUMN_OPTION_A, CSV_COLUMN_OPTION_B,
                                CSV_COLUMN_OPTION_C, CSV_COLUMN_OPTION_D]

                question_data = {
                    CSV_COLUMN_QUESTION_NUM: str(num),
                    CSV_COLUMN_QUESTION_TEXT: question_text[:500],
                    CSV_COLUMN_OPTION_A: '',
                    CSV_COLUMN_OPTION_B: '',
                    CSV_COLUMN_OPTION_C: '',
                    CSV_COLUMN_OPTION_D: '',
                    CSV_COLUMN_QUESTION_TYPE: DEFAULT_QUESTION_TYPE,
                    CSV_COLUMN_QUESTION_GROUP: False,
                }

                # 提取選項
                options = self._extract_options_enhanced(question_text)
                for i in range(min(len(options), 4)):
                    question_data[option_columns[i]] = options[i]
                
                # 驗證
                if self._validate_question(question_data):
                    questions.append(question_data)
        
        return questions
    
    def _parse_with_ai_assistance(self, text: str) -> List[Dict[str, Any]]:
        """使用AI輔助解析（當常規方法失敗時）"""
        # 這裡可以集成Google Gemini或其他AI
        # 暫時返回空列表，避免額外的API調用
        self.logger.info("AI輔助解析功能待實作")
        return []
    
    def _validate_question(self, question: Dict[str, Any]) -> bool:
        """驗證題目是否有效"""
        # 檢查題目長度
        if len(question.get('題目', '')) < 10:
            return False
        
        # 檢查選項數量
        option_count = sum(
            1 for opt in ['A', 'B', 'C', 'D'] 
            if question.get(f'選項{opt}', '').strip()
        )
        
        if option_count < 2:
            return False
        
        return True
    
    def _deduplicate_and_sort(self, questions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """去重並排序題目"""
        # 按題號去重
        seen_nums = set()
        unique_questions = []
        
        for q in questions:
            num = q['題號']
            if num not in seen_nums:
                seen_nums.add(num)
                unique_questions.append(q)
        
        # 按題號排序
        try:
            unique_questions.sort(key=lambda x: int(x['題號']))
        except ValueError:
            pass  # 如果題號無法轉換為整數，保持原順序
        
        return unique_questions

