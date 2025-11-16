#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pdfplumber
import re

pdf_path = '114年考古題/民國114年/民國114年_警察特考/資訊管理/中華民國憲法與警察專業英文/試題.pdf'

with pdfplumber.open(pdf_path) as pdf:
    text = ''.join([page.extract_text() or '' for page in pdf.pages])

# 找到題組56-60
group_start = text.find("請依下文回答第56題至第60題")
if group_start != -1:
    group_text = text[group_start:group_start + 2000]
    
    print("=== 題組56-60內容 ===")
    print(group_text[:1000])
    
    print("\n=== 檢查每題是否存在 ===")
    for num in range(56, 61):
        if f'{num} ' in group_text:
            pos = group_text.find(f'{num} ')
            print(f"第{num}題: 存在 (位置: {pos})")
            print(f"  內容: {group_text[pos:pos+100]}")
        else:
            print(f"第{num}題: 不存在")
    
    print("\n=== 檢查選項符號 ===")
    option_symbols = ['\ue18c', '\ue18d', '\ue18e', '\ue18f']
    for num in range(56, 61):
        has_symbols = any(symbol in group_text[group_text.find(f'{num} '):group_text.find(f'{num} ')+200] if f'{num} ' in group_text else '' for symbol in option_symbols)
        print(f"第{num}題有選項符號: {has_symbols}")
