#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pdfplumber
import re
from typing import List

pdf_path = '114年考古題/民國114年/民國114年_警察特考/資訊管理/中華民國憲法與警察專業英文/試題.pdf'

with pdfplumber.open(pdf_path) as pdf:
    text = ''.join([page.extract_text() or '' for page in pdf.pages])

def _extract_options_for_question(test_section: str, question_num: int):
    """為特定題號提取選項"""
    lines = test_section.split('\n')
    
    # 找到題目所在的行
    question_line_idx = -1
    for i, line in enumerate(lines):
        if line.strip().startswith(f'{question_num} '):
            question_line_idx = i
            break
    
    if question_line_idx == -1:
        return []
    
    options = []
    
    # 從題目行開始，向後查找選項
    for i in range(question_line_idx + 1, min(question_line_idx + 10, len(lines))):
        line = lines[i].strip()
        
        # 如果遇到下一題，停止
        if re.match(r'^\d+\s+', line):
            break
        
        if not line:
            continue
        
        # 處理選項行
        line_options = _parse_option_line(line)
        options.extend(line_options)
        
        # 如果已經找到4個選項，停止
        if len(options) >= 4:
            break
    
    # 如果選項不足，嘗試在同一行查找
    if len(options) < 4:
        question_line = lines[question_line_idx].strip()
        # 檢查題目行是否包含選項
        if any(c in question_line for c in ['', '', '', '']):
            line_options = _parse_option_line(question_line)
            options.extend(line_options)
    
    return options[:4]

def _parse_option_line(line: str) -> List[str]:
    """解析選項行"""
    options = []
    
    # 檢查是否有選項符號
    option_symbols = [c for c in ['', '', '', ''] if c]  # 過濾空字符串
    for symbol in option_symbols:
        if symbol in line:
            # 找到符號後的所有內容
            parts = line.split(symbol)
            if len(parts) > 1:
                # 提取符號後的內容
                content = parts[1].strip()
                # 移除下一個符號前的內容
                for next_symbol in option_symbols:
                    if next_symbol in content:
                        content = content.split(next_symbol)[0].strip()
                if content:
                    options.append(content)
    
    # 如果沒有找到符號，嘗試空格分隔
    if not options and line:
        parts = line.split()
        for part in parts:
            if part and len(part) > 1:
                options.append(part)
    
    return options

# 測試第58-60題
for num in range(58, 61):
    print(f"\n=== 第{num}題 ===")
    if f'{num} ' in text:
        pos = text.find(f'{num} ')
        question_text = text[pos:pos+200].strip()
        print(f"題目文本: {question_text}")
        
        # 提取選項
        options = _extract_options_for_question(text, num)
        print(f"提取的選項: {options}")
        print(f"選項數量: {len(options)}")
    else:
        print(f"第{num}題: 未找到")
