#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
調試真實PDF解析問題
"""

import sys
sys.path.insert(0, '/home/user/oldtest')

from src.core.enhanced_pdf_processor import EnhancedPDFProcessor
from src.core.question_parser import QuestionParser

# PDF路徑
pdf_path = "考選部考古題完整庫/民國114年/民國114年_司法特考/監獄官/法學知識與英文（包括中華民國憲法、法學緒論、英文）/試題.pdf"

# 提取文本
processor = EnhancedPDFProcessor()
result = processor.extract_with_best_method(pdf_path)

text = result['text']
print(f"文本長度: {len(text)} 字符")

# 提取前10題看看格式
import re

# 找到第1題到第10題
pattern = r'(\d+)\s+(.+?)(?=\d+\s+|$)'
matches = re.findall(pattern, text[:3000], re.DOTALL)

print(f"\n找到 {len(matches)} 個匹配")
print(f"\n前5個題目:")
for i, (num, content) in enumerate(matches[:5], 1):
    content_clean = ' '.join(content.split())
    print(f"\n題{num}:")
    print(f"  內容長度: {len(content_clean)}")
    print(f"  前100字符: {content_clean[:100]}...")

# 使用Question Parser解析
print(f"\n{'='*60}")
print("使用QuestionParser解析")
print(f"{'='*60}")

parser = QuestionParser()
questions = parser.parse_questions(text)

print(f"\n解析結果: {len(questions)} 題")

if questions:
    print(f"\n前3題詳情:")
    for i, q in enumerate(questions[:3], 1):
        print(f"\n題 {i}:")
        print(f"  題號: {q.get('題號')}")
        print(f"  題目長度: {len(str(q.get('題目', '')))}")
        print(f"  題目: {str(q.get('題目', ''))[:100]}...")
        print(f"  選項A: {q.get('選項A', 'N/A')[:50]}...")
        print(f"  選項B: {q.get('選項B', 'N/A')[:50]}...")
else:
    print("\n⚠️  未解析到任何題目")

# 手動測試單題解析
print(f"\n{'='*60}")
print("手動測試第1題解析")
print(f"{'='*60}")

# 提取第1題的完整文本
first_question_text = text[text.find("1 關於修憲程序"):text.find("2 依憲法規定")]
print(f"\n第1題文本:")
print(first_question_text)
print(f"\n長度: {len(first_question_text)} 字符")
