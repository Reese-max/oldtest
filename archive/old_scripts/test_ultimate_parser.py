#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
sys.path.insert(0, 'src')

from src.core.ultimate_question_parser import UltimateQuestionParser
import pdfplumber

pdf_path = '114年考古題/民國114年/民國114年_警察特考/資訊管理/中華民國憲法與警察專業英文/試題.pdf'

with pdfplumber.open(pdf_path) as pdf:
    text = ''.join([page.extract_text() or '' for page in pdf.pages])

parser = UltimateQuestionParser()
questions = parser.parse_all_60_questions(text, pdf_path)

# 統計已提取的題號
extracted_nums = set()
for q in questions:
    if q['question_number'].isdigit():
        extracted_nums.add(int(q['question_number']))

missing = [i for i in range(1, 61) if i not in extracted_nums]

print(f'終極解析結果: {len(questions)} 題')
print(f'缺失題號: {missing[:10]}...')
print(f'缺失總數: {len(missing)} 題')

# 顯示前5題
print(f'\n=== 前5題預覽 ===')
for i, q in enumerate(questions[:5]):
    print(f"\n第 {i+1} 題:")
    print(f"  題號: {q['question_number']}")
    print(f"  類型: {q['question_type']}")
    print(f"  題目: {q['question_text'][:50]}...")
    if q['options']:
        print(f"  選項數: {len(q['options'])}")
