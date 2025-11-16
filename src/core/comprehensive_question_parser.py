#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
綜合題目解析器 - 處理混合格式PDF中的所有題目類型
"""

import re
import os
from typing import List, Dict, Any, Tuple
from ..utils.logger import logger

class ComprehensiveQuestionParser:
    """綜合題目解析器"""
    
    def __init__(self):
        self.logger = logger
    
    def parse_all_questions(self, text: str, pdf_path: str) -> List[Dict[str, Any]]:
        """解析PDF中的所有題目"""
        questions = []
        
        # 1. 解析申論題
        essay_questions = self._parse_essay_questions(text)
        questions.extend(essay_questions)
        
        # 2. 解析標準選擇題（第1-50題）
        standard_questions = self._parse_standard_questions(text)
        questions.extend(standard_questions)
        
        # 3. 解析題組選擇題（第51-60題）
        group_questions = self._parse_group_questions(text)
        questions.extend(group_questions)
        
        self.logger.info(f"✅ 綜合解析完成：申論題 {len(essay_questions)} 題，標準題 {len(standard_questions)} 題，題組題 {len(group_questions)} 題")
        
        return questions
    
    def _parse_essay_questions(self, text: str) -> List[Dict[str, Any]]:
        """解析申論題"""
        questions = []
        
        # 尋找申論題標題
        essay_patterns = [
            r'英文作文：\s*(.*?)(?=第\d+題|$)',
            r'申論題：\s*(.*?)(?=第\d+題|$)',
            r'作文題：\s*(.*?)(?=第\d+題|$)'
        ]
        
        for pattern in essay_patterns:
            matches = re.finditer(pattern, text, re.DOTALL)
            for match in matches:
                question_text = match.group(1).strip()
                if len(question_text) > 50:  # 確保是完整的題目
                    questions.append({
                        'question_number': '申論題',
                        'question_text': question_text,
                        'question_type': 'essay',
                        'options': [],
                        'correct_answer': '',
                        'score': 25
                    })
                    self.logger.info(f"✓ 提取申論題: {question_text[:50]}...")
        
        return questions
    
    def _parse_standard_questions(self, text: str) -> List[Dict[str, Any]]:
        """解析標準選擇題（第1-50題）"""
        questions = []
        
        # 先找到測驗題部分
        test_section_match = re.search(r'乙、測驗題部分.*?(?=請依下文回答|$)', text, re.DOTALL)
        if not test_section_match:
            return questions
        
        test_section = test_section_match.group()
        lines = test_section.split('\n')
        
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            # 匹配題號開頭的行
            match = re.match(r'^(\d+)\s+(.+)$', line)
            if match:
                question_num = int(match.group(1))
                if question_num > 50:  # 只處理1-50題
                    i += 1
                    continue
                
                question_text = match.group(2).strip()
                
                # 收集題目內容（可能跨行）
                j = i + 1
                while j < len(lines):
                    next_line = lines[j].strip()
                    # 如果遇到下一題或選項開始，停止
                    if re.match(r'^\d+\s+', next_line) or any(next_line.startswith(c) for c in ['', '', '', '']):
                        break
                    # 添加題目內容
                    if next_line:
                        question_text += ' ' + next_line
                    j += 1
                    # 如果題目以問號或句號結尾，停止
                    if question_text.endswith('？') or question_text.endswith('。'):
                        break
                
                # 收集選項（可能跨多行）
                options = []
                while j < len(lines) and len(options) < 4:
                    option_line = lines[j].strip()
                    
                    # 如果遇到下一題，停止
                    if re.match(r'^\d+\s+', option_line):
                        break
                    
                    # 處理選項行
                    if option_line:
                        # 方法1：處理有符號前綴的選項
                        # 簡化處理：直接移除符號前綴
                        cleaned_line = option_line
                        for prefix in ['', '', '', '']:
                            if cleaned_line.startswith(prefix):
                                cleaned_line = cleaned_line[len(prefix):].strip()
                                break
                        
                        if cleaned_line and len(cleaned_line) > 1:
                            options.append(cleaned_line)
                        else:
                            # 方法2：處理空格分隔的選項（如第6、7題）
                            # 檢查是否包含多個選項在同一行
                            if ' ' in option_line and not any(option_line.startswith(c) for c in ['', '', '', '']):
                                # 可能是空格分隔的選項
                                parts = option_line.split()
                                for part in parts:
                                    if part and len(part) > 1 and not part.isdigit():
                                        options.append(part)
                            else:
                                # 單個選項
                                if len(option_line) > 1:
                                    options.append(option_line)
                    
                    j += 1
                
                # 如果找到4個選項，添加題目
                if len(options) >= 4:
                    questions.append({
                        'question_number': str(question_num),
                        'question_text': question_text,
                        'question_type': 'choice',
                        'options': options[:4],  # 只取前4個
                        'correct_answer': '',
                        'score': 1.25
                    })
                    self.logger.info(f"✓ 提取標準題 {question_num}: {question_text[:30]}...")
                
                i = j
                continue
            
            i += 1
        
        return questions
    
    def _parse_group_questions(self, text: str) -> List[Dict[str, Any]]:
        """解析題組選擇題（第51-60題）"""
        questions = []
        
        # 尋找題組
        group_pattern = r'請依下文回答第(\d+)題至第(\d+)題\s*(.*?)(?=請依下文回答|$)'
        group_matches = re.finditer(group_pattern, text, re.DOTALL)
        
        for group_match in group_matches:
            start_num = int(group_match.group(1))
            end_num = int(group_match.group(2))
            group_text = group_match.group(3)
            
            # 解析題組中的每個題目
            for question_num in range(start_num, end_num + 1):
                question_data = self._extract_question_from_group(group_text, question_num)
                if question_data:
                    questions.append(question_data)
                    self.logger.info(f"✓ 提取題組題 {question_num}: {question_data['question_text'][:30]}...")
        
        return questions
    
    def _extract_question_from_group(self, group_text: str, question_num: int) -> Dict[str, Any]:
        """從題組文本中提取特定題目"""
        # 尋找題目內容
        question_pattern = rf'第{question_num}題\s*(.*?)(?=第{question_num+1}題|$)'
        question_match = re.search(question_pattern, group_text, re.DOTALL)
        
        if not question_match:
            return None
        
        question_text = question_match.group(1).strip()
        
        # 提取選項
        options = self._extract_options_for_question(group_text, question_num)
        
        if len(options) >= 4:
            return {
                'question_number': str(question_num),
                'question_text': question_text,
                'question_type': 'choice',
                'options': options,
                'correct_answer': '',
                'score': 1.25
            }
        
        return None
    
    def _extract_options_for_question(self, group_text: str, question_num: int) -> List[str]:
        """提取特定題號的選項"""
        lines = group_text.split('\n')
        
        for line in lines:
            line_stripped = line.strip()
            
            # 模式：題號 + 四個選項（包含特殊字符）
            pattern = rf'^{question_num}\s+([^\s]+)\s+([^\s]+)\s+([^\s]+)\s+([^\s]+)\s*$'
            match = re.match(pattern, line_stripped)
            
            if match:
                options = [match.group(i) for i in range(1, 5)]
                return options
        
        # 如果沒找到，嘗試寬鬆匹配
        for line in lines:
            if line.strip().startswith(str(question_num) + ' '):
                parts = line.strip().split()
                if len(parts) >= 5:  # 題號 + 4個選項
                    options = [p for p in parts[1:5] if p]
                    if len(options) == 4:
                        return options
        
        return []
