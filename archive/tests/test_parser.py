#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試解析器
"""

import re
from typing import List, Dict, Any

def parse_questions_from_text(text: str) -> List[Dict[str, Any]]:
    """從文字中解析題目"""
    questions = []
    
    # 先清理文字，移除多餘的空白和換行
    text = re.sub(r'\s+', ' ', text)
    
    # 多種題目格式的正則表達式
    patterns = [
        # 格式1: 1. 題目內容 (A) 選項A (B) 選項B (C) 選項C (D) 選項D
        r'(\d+)\.\s*([^(]+?)\s*\(A\)\s*([^(]+?)\s*\(B\)\s*([^(]+?)\s*\(C\)\s*([^(]+?)\s*\(D\)\s*([^(]+?)(?=\d+\.|$)',
        # 格式2: 1. 題目內容 A. 選項A B. 選項B C. 選項C D. 選項D
        r'(\d+)\.\s*([^A]+?)\s*A\.\s*([^B]+?)\s*B\.\s*([^C]+?)\s*C\.\s*([^D]+?)\s*D\.\s*([^(]+?)(?=\d+\.|$)',
        # 格式3: 1. 題目內容 A) 選項A B) 選項B C) 選項C D) 選項D
        r'(\d+)\.\s*([^A]+?)\s*A\)\s*([^B]+?)\s*B\)\s*([^C]+?)\s*C\)\s*([^D]+?)\s*D\)\s*([^(]+?)(?=\d+\.|$)'
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, text, re.DOTALL)
        if matches:
            print(f"✅ 使用模式找到 {len(matches)} 題")
            break
    
    if not matches:
        # 如果正則表達式失敗，嘗試逐行解析
        print("⚠️ 正則表達式解析失敗，嘗試逐行解析...")
        questions = parse_questions_line_by_line(text)
        return questions
    
    for match in matches:
        question_num, title, option_a, option_b, option_c, option_d = match
        
        # 清理文字
        title = clean_text(title)
        option_a = clean_text(option_a)
        option_b = clean_text(option_b)
        option_c = clean_text(option_c)
        option_d = clean_text(option_d)
        
        if len(title) > 5:  # 確保題目有足夠內容
            questions.append({
                '題號': question_num,
                '題目': title,
                '選項A': option_a,
                '選項B': option_b,
                '選項C': option_c,
                '選項D': option_d,
                '題型': '選擇題'
            })
    
    return questions

def parse_questions_line_by_line(text: str) -> List[Dict[str, Any]]:
    """逐行解析題目（備用方法）"""
    questions = []
    lines = text.split('\n')
    
    current_question = None
    current_options = {}
    option_keys = ['A', 'B', 'C', 'D']
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # 檢查是否為題目開始
        if re.match(r'^\d+\.', line):
            # 儲存前一題
            if current_question and len(current_options) == 4:
                questions.append({
                    '題號': current_question['num'],
                    '題目': current_question['text'],
                    '選項A': current_options.get('A', ''),
                    '選項B': current_options.get('B', ''),
                    '選項C': current_options.get('C', ''),
                    '選項D': current_options.get('D', ''),
                    '題型': '選擇題'
                })
            
            # 開始新題目
            match = re.match(r'^(\d+)\.\s*(.+)', line)
            if match:
                current_question = {
                    'num': match.group(1),
                    'text': match.group(2)
                }
                current_options = {}
        
        # 檢查是否為選項
        elif current_question and re.match(r'^[A-D][\.\)]\s*', line):
            match = re.match(r'^([A-D])[\.\)]\s*(.+)', line)
            if match:
                option_key = match.group(1)
                option_text = match.group(2)
                current_options[option_key] = option_text
    
    # 儲存最後一題
    if current_question and len(current_options) == 4:
        questions.append({
            '題號': current_question['num'],
            '題目': current_question['text'],
            '選項A': current_options.get('A', ''),
            '選項B': current_options.get('B', ''),
            '選項C': current_options.get('C', ''),
            '選項D': current_options.get('D', ''),
            '題型': '選擇題'
        })
    
    print(f"✅ 逐行解析找到 {len(questions)} 題")
    return questions

def clean_text(text: str) -> str:
    """清理文字"""
    if not text:
        return ""
    
    # 移除多餘空白
    text = re.sub(r'\s+', ' ', text)
    
    # 移除開頭和結尾的空白
    text = text.strip()
    
    # 移除特殊字符
    text = re.sub(r'[^\w\s\u4e00-\u9fff\u3000-\u303f\uff00-\uffef]', '', text)
    
    return text

def main():
    """測試主程式"""
    print("測試解析器")
    print("="*50)
    
    # 讀取測試檔案
    with open('test_questions.txt', 'r', encoding='utf-8') as f:
        text = f.read()
    
    print("原始文字:")
    print(text[:500])
    print("\n" + "="*50)
    
    # 解析題目
    questions = parse_questions_from_text(text)
    
    print(f"\n解析結果: 找到 {len(questions)} 題")
    
    for i, q in enumerate(questions, 1):
        print(f"\n第{i}題:")
        print(f"  題號: {q['題號']}")
        print(f"  題目: {q['題目']}")
        print(f"  選項A: {q['選項A']}")
        print(f"  選項B: {q['選項B']}")
        print(f"  選項C: {q['選項C']}")
        print(f"  選項D: {q['選項D']}")

if __name__ == "__main__":
    main()