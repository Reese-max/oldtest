#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pdfplumber
import re

pdf_path = '114年考古題/民國114年/民國114年_警察特考/資訊管理/中華民國憲法與警察專業英文/試題.pdf'

with pdfplumber.open(pdf_path) as pdf:
    text = ''.join([page.extract_text() or '' for page in pdf.pages])

def _parse_option_line(line: str) -> list:
    """解析選項行"""
    options = []
    
    # 檢查是否有選項符號
    option_symbols = [c for c in ['', '', '', ''] if c]  # 過濾空字符串
    
    # 使用正則表達式提取選項
    for symbol in option_symbols:
        if symbol in line:
            # 找到所有該符號的位置
            positions = [i for i, char in enumerate(line) if char == symbol]
            for pos in positions:
                # 提取符號後的內容，直到下一個符號或行尾
                start = pos + 1
                end = len(line)
                
                # 找到下一個符號的位置
                for next_symbol in option_symbols:
                    next_pos = line.find(next_symbol, start)
                    if next_pos != -1 and next_pos < end:
                        end = next_pos
                
                content = line[start:end].strip()
                if content:
                    options.append(content)
    
    return options

# 測試第58-60題
for num in range(58, 61):
    print(f"\n=== 第{num}題 ===")
    if f'{num} ' in text:
        pos = text.find(f'{num} ')
        question_text = text[pos:pos+200].strip()
        print(f"題目文本: {question_text}")
        
        # 提取選項
        options = _parse_option_line(question_text)
        print(f"提取的選項: {options}")
        print(f"選項數量: {len(options)}")
        
        # 檢查原始字符
        print(f"原始字符: {repr(question_text[:100])}")
    else:
        print(f"第{num}題: 未找到")
