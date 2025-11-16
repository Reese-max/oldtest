#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pdfplumber
import re

pdf_path = '114年考古題/民國114年/民國114年_警察特考/資訊管理/中華民國憲法與警察專業英文/試題.pdf'

with pdfplumber.open(pdf_path) as pdf:
    text = ''.join([page.extract_text() or '' for page in pdf.pages])

# 找到題組
group_start = text.find("請依下文回答第51題至第55題")
if group_start != -1:
    group_text = text[group_start:group_start + 2000]
    
    print("=== 檢查符號位置 ===")
    for num in range(51, 55):
        if f'{num} ' in group_text:
            pos = group_text.find(f'{num} ')
            question_text = group_text[pos:pos+200].strip()
            
            print(f"\n第{num}題:")
            print(f"文本: {question_text}")
            
            # 逐字檢查
            for i, char in enumerate(question_text):
                if char in ['', '', '', '']:
                    print(f"  符號 '{char}' 在位置 {i}: '{question_text[max(0, i-10):i+10]}'")
            
            # 檢查是否符號在題目開頭部分
            first_sentence = question_text.split('.')[0]
            print(f"  第一句: {first_sentence}")
            has_symbols_in_first = any(c in first_sentence for c in ['', '', '', ''])
            print(f"  第一句有符號: {has_symbols_in_first}")
