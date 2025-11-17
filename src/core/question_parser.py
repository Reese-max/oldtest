#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
題目解析器
負責從文字中解析題目和選項
"""

import re
import json
from typing import List, Dict, Any, Optional, Tuple
from ..utils.logger import logger
from ..utils.exceptions import QuestionParsingError
from ..utils.config import config_manager
from ..utils.regex_patterns import (
    QUESTION_GROUP_PATTERNS,
    QUESTION_PATTERNS,
    QUESTION_NUMBER_PATTERNS,
    STANDARD_OPTION_PATTERNS,
    NEXT_GROUP_PATTERN,
    NON_QUESTION_KEYWORDS,
    match_patterns,
)
from ..utils.constants import (
    CSV_COLUMN_QUESTION_NUM, CSV_COLUMN_QUESTION_TEXT, CSV_COLUMN_QUESTION_TYPE,
    CSV_COLUMN_OPTION_A, CSV_COLUMN_OPTION_B, CSV_COLUMN_OPTION_C, CSV_COLUMN_OPTION_D,
    CSV_COLUMN_CORRECT_ANSWER, CSV_COLUMN_DIFFICULTY, CSV_COLUMN_CATEGORY,
    CSV_COLUMN_QUESTION_GROUP, CSV_COLUMN_GROUP_ID, CSV_COLUMN_NOTES,
    DEFAULT_QUESTION_TYPE
)


class QuestionParser:
    """題目解析器"""
    

    # 選項起始詞常數（提取為類常數避免重複）
    OPTION_STARTERS = [
        '經', '各', '行', '私', '於', '依', '關', '當', '偶', '下',
        '應', '若', '原', '該', '法', '警', '義', '褫', '受', '無',
        '須', '向', '得', '限'
    ]

    def __init__(self):
        self.logger = logger
        self.config = config_manager.get_processing_config()
    
    def parse_questions(self, text: str) -> List[Dict[str, Any]]:
        """
        解析文字中的題目
        
        Args:
            text: 包含題目的文字內容
            
        Returns:
            題目列表
        """
        try:
            self.logger.info("開始解析題目")
            
            # 檢測題組
            question_groups = self._detect_question_groups(text)
            
            if question_groups:
                self.logger.info(f"檢測到 {len(question_groups)} 個題組")
                questions = self._parse_question_groups(text, question_groups)
            else:
                self.logger.info("未檢測到題組，解析一般題目")
                questions = self._parse_regular_questions(text)
            
            # 驗證題目
            validated_questions = self._validate_questions(questions)
            
            self.logger.success(f"題目解析完成，共 {len(validated_questions)} 題")
            return validated_questions
            
        except Exception as e:
            error_msg = f"題目解析失敗: {e}"
            self.logger.failure(error_msg)
            raise QuestionParsingError(error_msg) from e
    
    def _detect_question_groups(self, text: str) -> List[Dict[str, Any]]:
        """檢測題組"""
        question_groups = []
        
        # 使用預編譯的正則表達式模式
        for pattern in QUESTION_GROUP_PATTERNS:
            matches = pattern.finditer(text)
            for match in matches:
                start_num = int(match.group(1))
                end_num = int(match.group(2))
                question_groups.append({
                    'start': start_num,
                    'end': end_num,
                    'pattern': pattern.pattern,
                    'match_start': match.start(),
                    'match_end': match.end()
                })
        
        return question_groups
    
    def _parse_question_groups(self, text: str, question_groups: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """解析題組題目"""
        questions = []
        
        for group in question_groups:
            start_num = group['start']
            end_num = group['end']
            
            self.logger.info(f"解析題組: 第{start_num}題至第{end_num}題")
            
            # 提取題組內容
            group_content = self._extract_group_content(text, group)
            
            # 解析題組中的個別題目
            group_questions = self._parse_group_questions(group_content, start_num, end_num)
            questions.extend(group_questions)
        
        return questions
    
    def _extract_group_content(self, text: str, group: Dict[str, Any]) -> str:
        """提取題組內容"""
        # 從題組標記開始到下一題組或文檔結束
        start_pos = group['match_start']
        
        # 使用預編譯的正則表達式尋找下一個題組或文檔結束
        next_match = NEXT_GROUP_PATTERN.search(text[start_pos + 100:])
        
        if next_match:
            end_pos = start_pos + 100 + next_match.start()
        else:
            end_pos = len(text)
        
        return text[start_pos:end_pos]
    
    def _parse_group_questions(self, group_content: str, start_num: int, end_num: int) -> List[Dict[str, Any]]:
        """解析題組中的個別題目"""
        questions = []
        
        # 先按行分割內容
        lines = group_content.split('\n')
        
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
            
            # 尋找題號行（必須是獨立的題號行，例如"第1題："）
            question_start_idx = -1
            question_end_idx = len(lines)
            
            for i, line in enumerate(lines):
                line_stripped = line.strip()
                # 找到當前題號的開始（必須以"第X題"開頭，包含冒號）
                # 使用動態正則表達式匹配特定題號
                question_pattern = re.compile(rf'^\s*第{question_num}題[：:]', re.UNICODE)
                if question_pattern.match(line_stripped):
                    question_start_idx = i
                    # 找下一題的開始位置
                    next_question_pattern = re.compile(r'^\s*第\d+題[：:]', re.UNICODE)
                    for j in range(i + 1, len(lines)):
                        if next_question_pattern.match(lines[j].strip()):
                            question_end_idx = j
                            break
                    break
            
            # 如果找到題目
            if question_start_idx >= 0:
                # 提取從題號行到下一題之間的所有內容
                question_lines = lines[question_start_idx:question_end_idx]
                question_text = '\n'.join(question_lines)
                
                # 保留完整內容
                question_data['題目'] = question_text.strip()
                
                # 提取選項
                options = self._extract_options(question_text)
                for i, option in enumerate(['A', 'B', 'C', 'D']):
                    if i < len(options):
                        question_data[f'選項{option}'] = options[i]
            
            questions.append(question_data)
        
        return questions
    
    def _parse_regular_questions(self, text: str) -> List[Dict[str, Any]]:
        """解析一般題目"""
        questions = []
        
        # 使用預編譯的正則表達式模式
        for pattern in QUESTION_PATTERNS:
            matches = pattern.finditer(text)
            for match in matches:
                question_num = match.group(1)
                question_text = match.group(2).strip()
                
                # 過濾掉非題目的內容
                if self._is_not_a_question(question_num, question_text):
                    continue
                
                if len(question_text) < self.config.min_question_length:
                    continue
                
                # Create option column mapping
                option_columns = [CSV_COLUMN_OPTION_A, CSV_COLUMN_OPTION_B,
                                CSV_COLUMN_OPTION_C, CSV_COLUMN_OPTION_D]

                question_data = {
                    CSV_COLUMN_QUESTION_NUM: question_num,
                    CSV_COLUMN_QUESTION_TEXT: question_text,
                    CSV_COLUMN_OPTION_A: '',
                    CSV_COLUMN_OPTION_B: '',
                    CSV_COLUMN_OPTION_C: '',
                    CSV_COLUMN_OPTION_D: '',
                    CSV_COLUMN_QUESTION_TYPE: DEFAULT_QUESTION_TYPE,
                    CSV_COLUMN_QUESTION_GROUP: False
                }

                # 提取選項
                options = self._extract_options(question_text)
                for i in range(min(len(options), 4)):
                    question_data[option_columns[i]] = options[i]
                
                questions.append(question_data)
        
        return questions
    
    def _is_not_a_question(self, question_num: str, question_text: str) -> bool:
        """判斷是否不是題目"""
        # 過濾掉代號（如2501）
        if len(question_num) > 3:
            return True

        # 過濾不合理的題號範圍（1-100是合理範圍，過濾法條編號如666、689等）
        try:
            num = int(question_num)
            if num < 1 or num > 100:
                return True
        except ValueError:
            return True

        # 使用統一的關鍵詞列表過濾
        for keyword in NON_QUESTION_KEYWORDS:
            if keyword in question_text:
                return True

        # 過濾掉太短的內容
        if len(question_text) < 10:
            return True

        return False
    
    def _extract_options(self, question_text: str) -> List[str]:
        """提取選項"""
        options = []
        
        # 先嘗試標準格式：(A) 選項內容，使用預編譯的正則表達式
        standard_matches = []
        for pattern in STANDARD_OPTION_PATTERNS:
            match = pattern.search(question_text)
            if match:
                option_text = match.group(1).strip()
                if option_text:
                    standard_matches.append(option_text)
        
        if len(standard_matches) >= 2:
            return standard_matches
        
        # 嘗試空格分隔的英文選項格式（例如：compressed abridged extended abbreviated）
        lines = question_text.split('\n')
        for line in lines:
            line = line.strip()
            # 檢查是否為四個單詞的選項行
            words = line.split()
            if len(words) == 4 and all(len(w) > 2 and w.isalpha() for w in words):
                return words
            # 也可能是三個或更多單詞
            if 3 <= len(words) <= 5 and all(len(w) > 2 for w in words):
                # 檢查是否看起來像選項（都是小寫或首字母大寫）
                if all(w.islower() or w[0].isupper() for w in words):
                    return words[:4]
        
        # 真實考古題格式：每行包含兩個選項，用空格分隔
        # 例如：經公務人員考試錄取，接受訓練之人員 各級學校之軍訓教官
        lines = question_text.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # 跳過題目行（包含問號的行）
            if '？' in line or '?' in line:
                continue
                
            # 使用正則表達式分割選項
            # 尋找選項分割點：選項開始詞後面的空格
            option_starters = self.OPTION_STARTERS
            
            # 構建正則表達式模式
            pattern_parts = []
            for starter in option_starters:
                pattern_parts.append(f'{starter}[^\\s]*')
            
            # 使用正則表達式分割
            pattern = '|'.join(pattern_parts)
            matches = re.findall(pattern, line)
            
            for match in matches:
                if len(match.strip()) > 5:  # 選項應該有一定長度
                    options.append(match.strip())
        
        # 如果還是沒找到足夠選項，嘗試更簡單的方法
        if len(options) < 2:
            # 直接按空格分割整個文字
            words = question_text.split()
            current_option = ""

            for word in words:
                option_starters = self.OPTION_STARTERS
                
                if word in option_starters and current_option:
                    if len(current_option.strip()) > 5:
                        options.append(current_option.strip())
                    current_option = word
                else:
                    if current_option:
                        current_option += " " + word
                    else:
                        current_option = word
            
            if current_option and len(current_option.strip()) > 5:
                options.append(current_option.strip())
        
        return options[:4]  # 最多返回4個選項
    
    def _validate_questions(self, questions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """驗證題目"""
        validated_questions = []
        
        for question in questions:
            # 檢查題目長度
            if len(question.get('題目', '')) < self.config.min_question_length:
                self.logger.warning(f"題目 {question.get('題號', '?')} 長度不足，跳過")
                continue
            
            if len(question.get('題目', '')) > self.config.max_question_length:
                self.logger.warning(f"題目 {question.get('題號', '?')} 長度過長，截斷")
                question['題目'] = question['題目'][:self.config.max_question_length]
            
            # 檢查選項數量，但不跳過（保留所有題目）
            option_count = sum(1 for opt in ['A', 'B', 'C', 'D'] if question.get(f'選項{opt}', '').strip())
            if option_count < 2:
                self.logger.warning(f"題目 {question.get('題號', '?')} 選項不足（只有{option_count}個），但仍保留")
            
            validated_questions.append(question)
        
        return validated_questions