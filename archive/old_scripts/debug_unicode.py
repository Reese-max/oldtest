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
    
    print("=== 檢查Unicode字符 ===")
    # 檢查所有特殊字符
    special_chars = set()
    for char in group_text:
        if ord(char) > 127:  # 非ASCII字符
            special_chars.add(char)
    
    print(f"找到的特殊字符: {special_chars}")
    for char in special_chars:
        print(f"  '{char}' (Unicode: {ord(char)})")
    
    # 檢查第51題
    if '51 ' in group_text:
        pos = group_text.find('51 ')
        question_text = group_text[pos:pos+200].strip()
        print(f"\n第51題文本: {repr(question_text)}")
        
        # 檢查每個字符
        for i, char in enumerate(question_text):
            if ord(char) > 127:
                print(f"  位置 {i}: '{char}' (Unicode: {ord(char)})")
