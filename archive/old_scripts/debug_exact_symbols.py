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
    
    print("=== 檢查具體符號 ===")
    for num in range(51, 55):
        if f'{num} ' in group_text:
            pos = group_text.find(f'{num} ')
            question_text = group_text[pos:pos+200].strip()
            
            print(f"\n第{num}題:")
            print(f"文本: {repr(question_text)}")
            
            # 逐字檢查
            for i, char in enumerate(question_text):
                if char in ['', '', '', '']:
                    print(f"  符號 '{char}' (Unicode: {ord(char)}) 在位置 {i}")
                    print(f"  周圍文本: {repr(question_text[max(0, i-5):i+5])}")
            
            # 檢查第一句的每個字符
            first_sentence = question_text.split('.')[0]
            print(f"  第一句: {repr(first_sentence)}")
            for i, char in enumerate(first_sentence):
                if char in ['', '', '', '']:
                    print(f"    符號 '{char}' (Unicode: {ord(char)}) 在位置 {i}")
