#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pdfplumber
import re

pdf_path = '114年考古題/民國114年/民國114年_警察特考/資訊管理/中華民國憲法與警察專業英文/試題.pdf'

with pdfplumber.open(pdf_path) as pdf:
    text = ''.join([page.extract_text() or '' for page in pdf.pages])

print("=== 檢查51-60題 ===")
for num in range(51, 61):
    if f'{num} ' in text:
        pos = text.find(f'{num} ')
        print(f"\n第{num}題:")
        print(f"位置: {pos}")
        print(f"內容: {text[max(0, pos-20):pos+200]}")
        print("-" * 50)
    else:
        print(f"第{num}題: 未找到")

print("\n=== 檢查題組標記 ===")
group_markers = [
    "請依下文回答第",
    "題至第",
    "題組",
    "第51題",
    "第52題"
]

for marker in group_markers:
    if marker in text:
        pos = text.find(marker)
        print(f"找到 '{marker}' 在位置 {pos}")
        print(f"附近內容: {text[max(0, pos-50):pos+200]}")
        print("-" * 30)
