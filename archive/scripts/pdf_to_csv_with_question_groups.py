#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
改進版PDF轉CSV功能 - 專門處理題組問題
解決英文等科目中5-6個選擇題為一組的情況
"""

import os
import pdfplumber
import pandas as pd
import re
import json
import hashlib
from typing import List, Dict, Any, Optional, Tuple
import glob
from datetime import datetime, timedelta

class QuestionGroupProcessor:
    """題組處理器 - 專門處理題組問題"""
    
    @staticmethod
    def detect_question_groups(text: str) -> List[Dict[str, Any]]:
        """檢測題組"""
        groups = []
        
        # 檢測題組模式：請依下文回答第X題至第Y題
        group_patterns = [
            r'請依下文回答第(\d+)題至第(\d+)題：',
            r'請依上文回答第(\d+)題至第(\d+)題：',
            r'請依下列文章回答第(\d+)題至第(\d+)題：',
            r'請依下列短文回答第(\d+)題至第(\d+)題：',
            r'請依下列內容回答第(\d+)題至第(\d+)題：',
        ]
        
        for pattern in group_patterns:
            matches = re.finditer(pattern, text)
            for match in matches:
                start_q = int(match.group(1))
                end_q = int(match.group(2))
                
                # 找到題組開始位置
                start_pos = match.end()
                
                # 尋找下一個題組或文章結束位置
                next_group_match = re.search(r'請依.*?回答第\d+題至第\d+題：', text[start_pos:])
                if next_group_match:
                    end_pos = start_pos + next_group_match.start()
                else:
                    # 如果沒有下一個題組，找到文章結束位置
                    end_pos = len(text)
                
                # 提取題組內容
                group_content = text[start_pos:end_pos].strip()
                
                groups.append({
                    'start_question': start_q,
                    'end_question': end_q,
                    'content': group_content,
                    'question_count': end_q - start_q + 1
                })
        
        return groups
    
    @staticmethod
    def extract_questions_from_group(group: Dict[str, Any], text: str) -> List[Dict[str, Any]]:
        """從題組中提取個別題目"""
        questions = []
        start_q = group['start_question']
        end_q = group['end_question']
        group_content = group['content']
        
        # 在題組內容中尋找題目
        for q_num in range(start_q, end_q + 1):
            # 尋找題目模式
            question_patterns = [
                rf'{q_num}\s*[ＡＢＣＤ]',  # 題號 + 選項
                rf'{q_num}\s*[ABCD]',      # 題號 + 選項
                rf'第{q_num}題',           # 第X題
            ]
            
            question_found = False
            for pattern in question_patterns:
                match = re.search(pattern, group_content)
                if match:
                    # 提取題目內容
                    question_start = match.start()
                    
                    # 尋找選項
                    options = []
                    option_pattern = r'[ＡＢＣＤ][ＡＢＣＤ][ＡＢＣＤ][ＡＢＣＤ]'
                    option_match = re.search(option_pattern, group_content[question_start:])
                    
                    if option_match:
                        option_text = option_match.group()
                        # 分割選項
                        for i in range(0, len(option_text), 1):
                            if i + 1 < len(option_text):
                                option_letter = option_text[i]
                                option_content = option_text[i+1:i+2] if i+1 < len(option_text) else ""
                                options.append({
                                    'letter': option_letter,
                                    'content': option_content
                                })
                    
                    # 如果沒有找到選項，嘗試其他模式
                    if not options:
                        # 尋找單個選項模式
                        single_option_pattern = r'[ＡＢＣＤ][^ＡＢＣＤ]*'
                        single_matches = re.findall(single_option_pattern, group_content[question_start:question_start+200])
                        for i, match in enumerate(single_matches[:4]):  # 最多4個選項
                            if len(match) > 1:
                                options.append({
                                    'letter': match[0],
                                    'content': match[1:].strip()
                                })
                    
                    # 建立題目
                    question = {
                        '題號': str(q_num),
                        '題目': f"題組題目（第{q_num}題）",
                        '選項A': options[0]['content'] if len(options) > 0 else '',
                        '選項B': options[1]['content'] if len(options) > 1 else '',
                        '選項C': options[2]['content'] if len(options) > 2 else '',
                        '選項D': options[3]['content'] if len(options) > 3 else '',
                        '題型': '選擇題',
                        '正確答案': '',
                        '更正答案': '',
                        '題組': True,
                        '題組內容': group_content[:200] + '...' if len(group_content) > 200 else group_content
                    }
                    
                    questions.append(question)
                    question_found = True
                    break
            
            # 如果沒有找到具體題目，創建一個基本題目
            if not question_found:
                question = {
                    '題號': str(q_num),
                    '題目': f"題組題目（第{q_num}題）",
                    '選項A': '',
                    '選項B': '',
                    '選項C': '',
                    '選項D': '',
                    '題型': '選擇題',
                    '正確答案': '',
                    '更正答案': '',
                    '題組': True,
                    '題組內容': group_content[:200] + '...' if len(group_content) > 200 else group_content
                }
                questions.append(question)
        
        return questions

class AnswerProcessor:
    """答案處理器 - 從PDF文字中提取答案和更正答案"""
    
    @staticmethod
    def extract_answers_from_pdf(pdf_path: str) -> Dict[str, str]:
        """從PDF檔案中提取答案"""
        try:
            with pdfplumber.open(pdf_path) as pdf:
                text = ""
                for page in pdf.pages:
                    text += page.extract_text() or ""
            
            return AnswerProcessor.extract_answers_from_text(text)
        except Exception as e:
            print(f"❌ 提取答案失敗: {e}")
            return {}
    
    @staticmethod
    def extract_answers_from_text(text: str) -> Dict[str, str]:
        """從文字中提取答案"""
        answers = {}
        
        # 匹配答案模式：1. A, 2. B, 3. C 等
        answer_patterns = [
            r'(\d+)\.\s*([ABCD])',  # 1. A
            r'(\d+)\s*([ABCD])',    # 1 A
            r'第(\d+)題\s*([ABCD])', # 第1題 A
            r'(\d+)\s*：\s*([ABCD])', # 1：A
        ]
        
        for pattern in answer_patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                question_num = match[0]
                answer = match[1]
                answers[question_num] = answer
        
        return answers

def parse_questions_with_groups(text: str, expected_count: int = 0) -> List[Dict[str, Any]]:
    """解析包含題組的題目"""
    questions = []
    
    # 檢測題組
    groups = QuestionGroupProcessor.detect_question_groups(text)
    print(f"🔍 檢測到 {len(groups)} 個題組")
    
    if groups:
        # 處理題組
        for group in groups:
            print(f"   📚 題組 {group['start_question']}-{group['end_question']}: {group['question_count']} 題")
            group_questions = QuestionGroupProcessor.extract_questions_from_group(group, text)
            questions.extend(group_questions)
    
    # 處理非題組的單獨題目
    # 這裡可以添加處理單獨題目的邏輯
    
    return questions

def process_pdf_with_groups(pdf_path: str, output_dir: str = "", 
                           answer_pdf_path: str = "") -> Tuple[List[str], Dict[str, Any]]:
    """處理包含題組的PDF"""
    
    print(f"\n{'='*70}")
    print(f"📄 {os.path.basename(pdf_path)} (含題組處理)")
    print(f"{'='*70}")
    
    try:
        # 提取PDF文字
        with pdfplumber.open(pdf_path) as pdf:
            text = ""
            for page in pdf.pages:
                text += page.extract_text() or ""
        
        print(f"📊 提取文字長度: {len(text)} 字元")
        
        # 解析題目（包含題組）
        questions = parse_questions_with_groups(text)
        
        if not questions:
            print("❌ 未找到任何題目")
            return [], {}
        
        print(f"✅ 解析出 {len(questions)} 題")
        
        # 提取答案
        answers = {}
        if answer_pdf_path and os.path.exists(answer_pdf_path):
            print(f"🔍 提取答案: {os.path.basename(answer_pdf_path)}")
            answers = AnswerProcessor.extract_answers_from_pdf(answer_pdf_path)
            print(f"   ✅ 找到 {len(answers)} 個答案")
        
        # 合併答案到題目
        for question in questions:
            question_num = question.get('題號', '')
            correct_answer = answers.get(question_num, '')
            question['正確答案'] = correct_answer
            question['最終答案'] = correct_answer
        
        # 儲存CSV
        os.makedirs(output_dir, exist_ok=True)
        base = os.path.splitext(os.path.basename(pdf_path))[0]
        
        # 分類題目
        regular_questions = [q for q in questions if not q.get('題組', False)]
        group_questions = [q for q in questions if q.get('題組', False)]
        
        saved_files = []
        
        if regular_questions:
            path = os.path.join(output_dir, f"{base}_一般題目.csv")
            pd.DataFrame(regular_questions).to_csv(path, index=False, encoding='utf-8-sig')
            print(f"✅ {path} ({len(regular_questions)}題)")
            saved_files.append(path)
        
        if group_questions:
            path = os.path.join(output_dir, f"{base}_題組題目.csv")
            pd.DataFrame(group_questions).to_csv(path, index=False, encoding='utf-8-sig')
            print(f"✅ {path} ({len(group_questions)}題)")
            saved_files.append(path)
        
        # 合併所有題目
        if questions:
            path = os.path.join(output_dir, f"{base}_完整題目.csv")
            pd.DataFrame(questions).to_csv(path, index=False, encoding='utf-8-sig')
            print(f"✅ {path} ({len(questions)}題)")
            saved_files.append(path)
        
        return saved_files, {'total_questions': len(questions), 'group_questions': len(group_questions)}
        
    except Exception as e:
        print(f"❌ 處理失敗: {e}")
        return [], {}

def main():
    """主函數"""
    import argparse
    
    parser = argparse.ArgumentParser(description='PDF轉CSV工具 - 支援題組處理')
    parser.add_argument('input', help='輸入PDF檔案')
    parser.add_argument('-o', '--output', default='', help='輸出目錄')
    parser.add_argument('--answer', default='', help='答案PDF檔案路徑')
    
    args = parser.parse_args()
    
    if os.path.isfile(args.input):
        saved_files, stats = process_pdf_with_groups(args.input, args.output, args.answer)
        
        if saved_files:
            print(f"\n✅ 已儲存: {saved_files}")
            print(f"📊 統計: {stats}")
        else:
            print("\n❌ 處理失敗")
    else:
        print("❌ 輸入檔案不存在")

if __name__ == "__main__":
    main()