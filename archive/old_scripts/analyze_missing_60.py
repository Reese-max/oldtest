#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
sys.path.insert(0, 'src')

from src.core.comprehensive_question_parser import ComprehensiveQuestionParser
import pdfplumber

pdf_path = '114年考古題/民國114年/民國114年_警察特考/資訊管理/中華民國憲法與警察專業英文/試題.pdf'

with pdfplumber.open(pdf_path) as pdf:
    text = ''.join([page.extract_text() or '' for page in pdf.pages])

parser = ComprehensiveQuestionParser()
questions = parser.parse_all_questions(text, pdf_path)

# 統計已提取的題號
extracted_nums = set()
for q in questions:
    if q['question_number'].isdigit():
        extracted_nums.add(int(q['question_number']))

missing = [i for i in range(1, 61) if i not in extracted_nums]

print(f'已提取: {len(questions)} 題')
print(f'缺失題號: {missing[:10]}...')
print(f'缺失總數: {len(missing)} 題')

# 分析缺失題目的格式
print(f'\n=== 分析缺失題目格式 ===')
for num in missing[:5]:  # 分析前5個缺失題目
    if f'{num} ' in text:
        pos = text.find(f'{num} ')
        print(f'\n第{num}題附近:')
        print(text[max(0, pos-50):pos+200])
        print('-' * 50)
