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
    
    print("=== 最終檢查第51-54題 ===")
    for num in range(51, 55):
        if f'{num} ' in group_text:
            pos = group_text.find(f'{num} ')
            question_text = group_text[pos:pos+200].strip()
            
            print(f"\n第{num}題:")
            print(f"文本: {repr(question_text)}")
            
            # 清理題目文本
            cleaned = re.sub(r'\s+', ' ', question_text)
            cleaned = re.sub(r'^\d+\s+', '', cleaned)
            cleaned = cleaned.strip()
            
            print(f"清理後: {repr(cleaned)}")
            
            # 檢查前100字元
            question_part = cleaned[:100]
            print(f"前100字元: {repr(question_part)}")
            
            # 檢查是否有選項符號
            option_symbols = ['', '', '', '']  # Unicode: 57740, 57741, 57742, 57743
            has_symbols = any(c in question_part for c in option_symbols)
            print(f"有選項符號: {has_symbols}")
            
            if not has_symbols:
                print(f"✓ 應該識別為填空題")
            else:
                print(f"✗ 識別為選擇題")
                # 找出符號位置
                for i, char in enumerate(question_part):
                    if char in option_symbols:
                        print(f"  符號 '{char}' (Unicode: {ord(char)}) 在位置 {i}")
        else:
            print(f"第{num}題: 未找到")
