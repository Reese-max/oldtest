#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pdfplumber
import re

pdf_path = '114年考古題/民國114年/民國114年_警察特考/資訊管理/中華民國憲法與警察專業英文/試題.pdf'

with pdfplumber.open(pdf_path) as pdf:
    text = ''.join([page.extract_text() or '' for page in pdf.pages])

# 找到測驗題部分
test_section_match = re.search(r'乙、測驗題部分.*?(?=請依下文回答|$)', text, re.DOTALL)
if test_section_match:
    test_section = test_section_match.group()
    
    print("=== 測驗題部分前500字元 ===")
    print(test_section[:500])
    
    print("\n=== 尋找第1題 ===")
    if '1 ' in test_section:
        pos = test_section.find('1 ')
        print(f"第1題位置: {pos}")
        print(f"第1題附近: {test_section[max(0, pos-50):pos+200]}")
    
    print("\n=== 尋找第6題 ===")
    if '6 ' in test_section:
        pos = test_section.find('6 ')
        print(f"第6題位置: {pos}")
        print(f"第6題附近: {test_section[max(0, pos-50):pos+200]}")
    
    # 測試正則表達式
    print("\n=== 正則表達式測試 ===")
    pattern = r'^(\d+)\s+(.+?)(?=^\d+\s+|$)'
    matches = re.finditer(pattern, test_section, re.MULTILINE | re.DOTALL)
    
    found_questions = []
    for match in matches:
        question_num = int(match.group(1))
        question_text = match.group(2).strip()
        found_questions.append((question_num, question_text[:50]))
    
    print(f"找到的題目: {len(found_questions)}")
    for num, text in found_questions[:10]:
        print(f"  第{num}題: {text}...")
