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


class QuestionParser:
    """題目解析器"""
    
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
        
        # 題組檢測模式
        group_patterns = [
            r'請依下文回答第(\d+)題至第(\d+)題',
            r'請根據下列文章回答第(\d+)題至第(\d+)題',
            r'閱讀下文，回答第(\d+)題至第(\d+)題',
        ]
        
        for pattern in group_patterns:
            matches = re.finditer(pattern, text)
            for match in matches:
                start_num = int(match.group(1))
                end_num = int(match.group(2))
                question_groups.append({
                    'start': start_num,
                    'end': end_num,
                    'pattern': pattern,
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
        
        # 尋找下一個題組或文檔結束
        next_group_pattern = r'請依下文回答第\d+題至第\d+題|請根據下列文章回答第\d+題至第\d+題|閱讀下文，回答第\d+題至第\d+題'
        next_match = re.search(next_group_pattern, text[start_pos + 100:])
        
        if next_match:
            end_pos = start_pos + 100 + next_match.start()
        else:
            end_pos = len(text)
        
        return text[start_pos:end_pos]
    
    def _parse_group_questions(self, group_content: str, start_num: int, end_num: int) -> List[Dict[str, Any]]:
        """解析題組中的個別題目"""
        questions = []
        
        for question_num in range(start_num, end_num + 1):
            question_data = {
                '題號': str(question_num),
                '題目': '',
                '選項A': '',
                '選項B': '',
                '選項C': '',
                '選項D': '',
                '題型': '選擇題',
                '題組': True,
                '題組編號': f"{start_num}-{end_num}"
            }
            
            # 提取題目內容
            question_pattern = rf'第{question_num}題[：:]?\s*(.*?)(?=第{question_num + 1}題|$)'
            match = re.search(question_pattern, group_content, re.DOTALL)
            
            if match:
                question_text = match.group(1).strip()
                question_data['題目'] = question_text
                
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
        
        # 題目檢測模式 - 支援多種格式
        question_patterns = [
            r'第(\d+)題[：:]?\s*(.*?)(?=第\d+題|$)',
            r'(\d+)\.\s*(.*?)(?=\d+\.|$)',
            r'^(\d+)\s+(.*?)(?=^\d+\s+|$)',  # 真實考古題格式：數字+空格
            r'(\d+)\s+(.*?)(?=\d+\s+|$)',   # 更寬鬆的匹配
        ]
        
        for pattern in question_patterns:
            matches = re.finditer(pattern, text, re.DOTALL)
            for match in matches:
                question_num = match.group(1)
                question_text = match.group(2).strip()
                
                # 過濾掉非題目的內容
                if self._is_not_a_question(question_num, question_text):
                    continue
                
                if len(question_text) < self.config.min_question_length:
                    continue
                
                question_data = {
                    '題號': question_num,
                    '題目': question_text,
                    '選項A': '',
                    '選項B': '',
                    '選項C': '',
                    '選項D': '',
                    '題型': '選擇題',
                    '題組': False
                }
                
                # 提取選項
                options = self._extract_options(question_text)
                for i, option in enumerate(['A', 'B', 'C', 'D']):
                    if i < len(options):
                        question_data[f'選項{option}'] = options[i]
                
                questions.append(question_data)
        
        return questions
    
    def _is_not_a_question(self, question_num: str, question_text: str) -> bool:
        """判斷是否不是題目"""
        # 過濾掉代號（如2501）
        if len(question_num) > 3:
            return True
            
        # 過濾掉包含特定關鍵詞的內容
        filter_keywords = [
            '代號', '頁次', '考試', '科目', '時間', '座號', '注意', '禁止', '使用',
            '本試題', '單一選擇題', '選出', '正確', '適當', '答案', '共', '每題',
            '須用', '鉛筆', '試卡', '依題號', '清楚', '劃記', '作答者', '不予', '計分'
        ]
        
        for keyword in filter_keywords:
            if keyword in question_text:
                return True
        
        # 過濾掉太短的內容
        if len(question_text) < 10:
            return True
            
        return False
    
    def _extract_options(self, question_text: str) -> List[str]:
        """提取選項"""
        options = []
        
        # 先嘗試標準格式：(A) 選項內容
        standard_patterns = [
            r'[（(]A[）)]\s*(.*?)(?=[（(]B[）)]|$)',
            r'[（(]B[）)]\s*(.*?)(?=[（(]C[）)]|$)',
            r'[（(]C[）)]\s*(.*?)(?=[（(]D[）)]|$)',
            r'[（(]D[）)]\s*(.*?)(?=[（(]E[）)]|$)',
        ]
        
        standard_matches = []
        for pattern in standard_patterns:
            match = re.search(pattern, question_text, re.DOTALL)
            if match:
                option_text = match.group(1).strip()
                if option_text:
                    standard_matches.append(option_text)
        
        if len(standard_matches) >= 2:
            return standard_matches
        
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
            option_starters = ['經', '各', '行', '私', '於', '依', '關', '當', '偶', '下', '應', '若', '原', '該', '法', '警', '義', '偶', '褫', '受', '無', '須', '向', '得', '限']
            
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
                option_starters = ['經', '各', '行', '私', '於', '依', '關', '當', '偶', '下', '應', '若', '原', '該', '法', '警', '義', '偶', '褫', '受', '無']
                
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
            
            # 檢查選項
            option_count = sum(1 for opt in ['A', 'B', 'C', 'D'] if question.get(f'選項{opt}', '').strip())
            if option_count < 2:
                self.logger.warning(f"題目 {question.get('題號', '?')} 選項不足，跳過")
                continue
            
            validated_questions.append(question)
        
        return validated_questions