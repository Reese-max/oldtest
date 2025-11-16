#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pdfplumber
import re

pdf_path = '114年考古題/民國114年/民國114年_警察特考/資訊管理/中華民國憲法與警察專業英文/試題.pdf'

with pdfplumber.open(pdf_path) as pdf:
    text = ''.join([page.extract_text() or '' for page in pdf.pages])

print("=== 檢查第58-60題 ===")
for num in range(58, 61):
    if f'{num} ' in text:
        pos = text.find(f'{num} ')
        print(f"\n第{num}題:")
        print(f"位置: {pos}")
        print(f"內容: {text[max(0, pos-20):pos+200]}")
        print("-" * 50)
    else:
        print(f"第{num}題: 未找到")

print("\n=== 檢查第56-60題組 ===")
group_start = text.find("請依下文回答第56題至第60題")
if group_start != -1:
    group_text = text[group_start:group_start + 2000]
    print(f"題組內容前500字元:")
    print(group_text[:500])
