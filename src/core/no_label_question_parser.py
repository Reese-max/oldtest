#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
無標記選項題目解析器
處理選項沒有ABCD標記的選擇題（考選部標準格式）
"""

import re
from typing import List, Dict, Any
from ..utils.logger import logger
from ..utils.constants import (
    CSV_COLUMN_QUESTION_NUM, CSV_COLUMN_QUESTION_TEXT, CSV_COLUMN_QUESTION_TYPE,
    CSV_COLUMN_OPTION_A, CSV_COLUMN_OPTION_B, CSV_COLUMN_OPTION_C, CSV_COLUMN_OPTION_D,
    CSV_COLUMN_CORRECT_ANSWER, CSV_COLUMN_DIFFICULTY, CSV_COLUMN_CATEGORY,
    CSV_COLUMN_QUESTION_GROUP, CSV_COLUMN_NOTES,
    DEFAULT_QUESTION_TYPE
)


class NoLabelQuestionParser:
    """無標記選項題目解析器"""
    
    def __init__(self):
        self.logger = logger
    
    def parse_no_label_questions(self, text: str) -> List[Dict[str, Any]]:
        """
        解析無ABCD標記的選擇題
        
        Args:
            text: PDF提取的文字
            
        Returns:
            題目列表
        """
        self.logger.info("開始解析無標記選項題目")
        
        questions = []
        
        # 步驟1: 找到所有題號位置
        # 匹配模式: 行首的數字（題號）
        question_markers = []
        for match in re.finditer(r'^(\d+)\s+(.)', text, re.MULTILINE):
            num = int(match.group(1))
            # 只接受合理的題號 (1-50)
            if 1 <= num <= 50:
                question_markers.append({
                    'num': num,
                    'start': match.start(),
                    'content_start': match.start() + len(match.group(1)) + 1  # 跳過題號和空格
                })
        
        # 排序
        question_markers.sort(key=lambda x: x['start'])
        
        self.logger.info(f"找到 {len(question_markers)} 個題號標記")

        # 去重：如果同一題號出現多次，只保留最後一個（最完整的）
        unique_markers = {}
        for marker in question_markers:
            num = marker['num']
            # 如果這個題號已經存在，用後面的覆蓋前面的
            unique_markers[num] = marker

        # 轉回列表並按題號排序
        question_markers = [unique_markers[num] for num in sorted(unique_markers.keys())]
        self.logger.info(f"去重後剩餘 {len(question_markers)} 個題號")

        # 步驟2: 提取每個題目的完整內容
        for i, marker in enumerate(question_markers):
            question_num = marker['num']
            start_pos = marker['content_start']
            
            # 確定結束位置（下一題開始或文檔結束）
            if i + 1 < len(question_markers):
                end_pos = question_markers[i + 1]['start']
            else:
                end_pos = len(text)
            
            question_content = text[start_pos:end_pos].strip()
            
            # 分析題目和選項
            question_text, options = self._split_question_and_options(question_content)
            
            # 檢查選項 - 如果有英文單詞選項，允許較短的內容
            has_english_options = options and all(len(opt) <= 20 and opt.isalpha() for opt in options if opt)
            
            # 如果是英文單詞選項（完形填空），題目就是選項本身
            if has_english_options and len(question_text) < 50:
                question_text = f"請從以下選項中選出最適當的答案（英文完形填空題{question_num}）"
            
            # 跳過太短的內容（除非是英文單詞選項）
            if not has_english_options and len(question_content) < 10:
                self.logger.warning(f"題目 {question_num} 內容太短，跳過")
                continue

            # 檢查選項數量，但不跳過（保留所有題目）
            if len(options) < 2:
                self.logger.warning(f"題目 {question_num} 選項不足（只有{len(options)}個），但仍保留")

            # 確保有4個選項（補空白）
            while len(options) < 4:
                options.append('')

            # 安全獲取選項，防止索引越界
            def safe_get(lst, idx, default=''):
                """安全獲取列表元素"""
                return lst[idx] if 0 <= idx < len(lst) else default

            question = {
                CSV_COLUMN_QUESTION_NUM: question_num,  # 保持為整數
                CSV_COLUMN_QUESTION_TEXT: question_text,
                CSV_COLUMN_QUESTION_TYPE: DEFAULT_QUESTION_TYPE,
                CSV_COLUMN_OPTION_A: safe_get(options, 0),
                CSV_COLUMN_OPTION_B: safe_get(options, 1),
                CSV_COLUMN_OPTION_C: safe_get(options, 2),
                CSV_COLUMN_OPTION_D: safe_get(options, 3),
                CSV_COLUMN_CORRECT_ANSWER: '',
                CSV_COLUMN_DIFFICULTY: '中等',
                CSV_COLUMN_CATEGORY: '法律/英文',
                CSV_COLUMN_QUESTION_GROUP: has_english_options,  # 英文單詞選項標記為題組
                CSV_COLUMN_NOTES: '英文完形填空' if has_english_options else ''
            }
            
            questions.append(question)
            self.logger.info(f"✓ 提取題目 {question_num}")
        
        self.logger.success(f"無標記選項題目解析完成，共 {len(questions)} 題")
        return questions
    
    def _split_question_and_options(self, content: str) -> tuple:
        """
        分割題目和選項
        
        策略：
        1. 檢查是否為純英文單詞（完形填空選項）
        2. 題目通常以「？」結尾
        3. 選項在題目之後
        4. 選項通常較短（10-100字符）
        5. 選項之間用換行或空格分隔
        
        Returns:
            (題目文字, 選項列表)
        """
        # 優先檢查：是否為純英文單詞選項（完形填空）
        words = re.findall(r'\b[a-zA-Z]+\b', content)
        valid_words = [w for w in words if 3 <= len(w) <= 20]
        # 如果內容主要是英文單詞，且長度適中
        if len(valid_words) >= 4 and len(content) < 100:
            # 這可能是純選項（沒有題目）
            return "", valid_words[:4]
        
        # 尋找問號（題目結束）
        question_mark_pos = content.find('？')
        if question_mark_pos == -1:
            question_mark_pos = content.find('?')
        
        if question_mark_pos != -1:
            # 有問號，分割題目和選項區
            question_text = content[:question_mark_pos + 1].strip()
            options_text = content[question_mark_pos + 1:].strip()
        else:
            # 沒有問號，用第一個換行分割
            lines = content.split('\n', 1)
            if len(lines) >= 2:
                question_text = lines[0].strip()
                options_text = lines[1].strip()
            else:
                question_text = content
                options_text = ""
        
        # 解析選項
        options = self._parse_options(options_text)
        
        return question_text, options
    
    def _parse_options(self, options_text: str) -> List[str]:
        """
        解析選項文字
        
        策略：
        1. 檢查是否為英文單詞（完形填空）- 優先
        2. 按換行分割
        3. 按長度智能分割
        """
        if not options_text:
            return []
        
        # 策略1: 檢查是否為英文單詞（完形填空）
        # 提取所有英文單詞
        words = re.findall(r'\b[a-zA-Z]+\b', options_text)
        # 如果有4-8個英文單詞，且單詞長度合理（3-20字符）
        valid_words = [w for w in words if 3 <= len(w) <= 20]
        if 4 <= len(valid_words) <= 8:
            # 可能是英文單詞選項，取前4個
            return valid_words[:4]
        
        # 策略2: 按換行分割
        lines = [line.strip() for line in options_text.split('\n') if line.strip()]
        
        # 如果有2-6行，可能就是選項
        if 2 <= len(lines) <= 6:
            # 過濾掉過長的行（可能是題幹延續）
            potential_options = [line for line in lines if 5 <= len(line) <= 200]
            if len(potential_options) >= 2:
                return potential_options[:4]  # 最多4個選項
        
        # 策略3: 按空格分割（中文短句）
        # 尋找適當的分割點（長度相近的部分）
        if len(lines) == 1:
            # 單行，嘗試智能分割
            text = lines[0]
            # 如果有多個空格，可能是分隔符
            if '  ' in text:  # 兩個或以上空格
                parts = [p.strip() for p in re.split(r'\s{2,}', text) if p.strip()]
                if 2 <= len(parts) <= 4:
                    return parts
            
            # 嘗試按句子長度均分（假設4個選項）
            if len(text) >= 20:
                avg_len = len(text) // 4
                options = []
                current_pos = 0
                for i in range(4):
                    # 尋找接近avg_len位置的空格
                    target_pos = current_pos + avg_len
                    if target_pos >= len(text):
                        options.append(text[current_pos:].strip())
                        break
                    
                    # 向後尋找空格
                    space_pos = text.find(' ', target_pos)
                    if space_pos != -1 and space_pos < len(text):
                        options.append(text[current_pos:space_pos].strip())
                        current_pos = space_pos + 1
                    else:
                        options.append(text[current_pos:].strip())
                        break
                
                if len(options) >= 2:
                    return options[:4]
        
        # 如果都失敗，返回所有行作為選項
        return lines[:4] if lines else []
    
    def validate_questions(self, questions: List[Dict[str, Any]]) -> tuple:
        """
        驗證題目完整性
        
        Returns:
            (是否完整, 訊息)
        """
        if not questions:
            return False, "未提取到任何題目"
        
        question_nums = sorted([q['題號'] for q in questions])
        
        # 檢查題號連續性
        if question_nums:
            expected = list(range(1, max(question_nums) + 1))
            missing = set(expected) - set(question_nums)
            
            if missing:
                return False, f"題號有缺漏: {sorted(missing)}"
        
        # 檢查選項完整性
        incomplete = []
        for q in questions:
            if not q.get('選項A') or not q.get('選項B'):
                incomplete.append(q['題號'])
        
        if incomplete:
            return False, f"部分題目選項不完整: {incomplete}"
        
        return True, f"完整提取 {len(questions)} 題"

