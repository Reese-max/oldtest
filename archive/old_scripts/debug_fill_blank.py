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
    
    print("=== 檢查第51-54題格式 ===")
    for num in range(51, 55):
        if f'{num} ' in group_text:
            pos = group_text.find(f'{num} ')
            question_text = group_text[pos:pos+200].strip()
            
            print(f"\n第{num}題:")
            print(f"原始文本: {question_text}")
            
            # 檢查是否有選項符號
            has_options = any(c in question_text for c in ['', '', '', ''])
            print(f"有選項符號: {has_options}")
            
            if not has_options:
                print(f"✓ 識別為填空題")
            else:
                print(f"✗ 識別為選擇題")
        else:
            print(f"第{num}題: 未找到")
