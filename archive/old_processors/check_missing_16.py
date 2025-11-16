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
    
    print("=== 檢查缺失的題目 ===")
    missing = [1, 7, 12, 13, 38, 48, 49, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60]
    
    for num in missing[:5]:  # 檢查前5個
        if f'{num} ' in test_section:
            pos = test_section.find(f'{num} ')
            print(f"\n第{num}題:")
            print(f"位置: {pos}")
            print(f"內容: {test_section[max(0, pos-20):pos+200]}")
            print("-" * 50)
        else:
            print(f"第{num}題: 未找到")
    
    # 檢查是否有題組
    print(f"\n=== 檢查題組 ===")
    group_patterns = [
        r'請依下文回答第\s*(\d+)\s*題至第\s*(\d+)\s*題',
        r'第\s*(\d+)\s*題至第\s*(\d+)\s*題',
        r'(\d+)-(\d+)\s*題'
    ]
    
    for i, pattern in enumerate(group_patterns):
        matches = re.findall(pattern, test_section)
        print(f"題組模式 {i+1}: {len(matches)} 個")
        for match in matches:
            print(f"  {match}")
