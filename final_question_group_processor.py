#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
最終版題組處理器 - 精確處理司法考試的題組格式
"""

import os
import pdfplumber
import pandas as pd
import re
import json
from typing import List, Dict, Any, Optional, Tuple

class FinalQuestionGroupProcessor:
    """最終版題組處理器"""
    
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
    def extract_questions_from_group(group: Dict[str, Any]) -> List[Dict[str, Any]]:
        """從題組中提取個別題目"""
        questions = []
        start_q = group['start_question']
        end_q = group['end_question']
        group_content = group['content']
        
        print(f"   🔍 處理題組 {start_q}-{end_q}，內容長度: {len(group_content)} 字元")
        
        # 在題組內容中尋找所有題目和選項
        for q_num in range(start_q, end_q + 1):
            # 尋找題目模式 - 更精確的匹配
            question_patterns = [
                rf'{q_num}\s*[ＡＢＣＤ][^ＡＢＣＤ]*[ＡＢＣＤ][^ＡＢＣＤ]*[ＡＢＣＤ][^ＡＢＣＤ]*[ＡＢＣＤ]',  # 完整選項模式
                rf'{q_num}\s*[ABCD][^ABCD]*[ABCD][^ABCD]*[ABCD][^ABCD]*[ABCD]',  # 英文選項模式
            ]
            
            question_found = False
            for pattern in question_patterns:
                match = re.search(pattern, group_content)
                if match:
                    question_text = match.group()
                    print(f"   📝 找到題目 {q_num}: {question_text[:100]}...")
                    
                    # 提取選項
                    options = FinalQuestionGroupProcessor.extract_options_from_question(question_text)
                    
                    # 建立題目
                    question = {
                        '題號': str(q_num),
                        '題目': f"題組題目（第{q_num}題）",
                        '選項A': options.get('A', ''),
                        '選項B': options.get('B', ''),
                        '選項C': options.get('C', ''),
                        '選項D': options.get('D', ''),
                        '題型': '選擇題',
                        '正確答案': '',
                        '更正答案': '',
                        '題組': True,
                        '題組內容': group_content[:200] + '...' if len(group_content) > 200 else group_content,
                        '原始題目': question_text
                    }
                    
                    questions.append(question)
                    question_found = True
                    break
            
            # 如果沒有找到具體題目，創建一個基本題目
            if not question_found:
                print(f"   ⚠️ 未找到題目 {q_num} 的具體內容")
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
                    '題組內容': group_content[:200] + '...' if len(group_content) > 200 else group_content,
                    '原始題目': ''
                }
                questions.append(question)
        
        return questions
    
    @staticmethod
    def extract_options_from_question(question_text: str) -> Dict[str, str]:
        """從題目文字中提取選項"""
        options = {}
        
        # 嘗試不同的選項模式
        option_patterns = [
            # 中文選項模式
            r'[ＡＢＣＤ][^ＡＢＣＤ]*',
            # 英文選項模式
            r'[ABCD][^ABCD]*',
        ]
        
        for pattern in option_patterns:
            matches = re.findall(pattern, question_text)
            if len(matches) >= 4:  # 至少要有4個選項
                for i, match in enumerate(matches[:4]):
                    if len(match) > 1:
                        option_letter = match[0]
                        option_content = match[1:].strip()
                        options[option_letter] = option_content
                break
        
        # 如果沒有找到選項，嘗試更簡單的模式
        if not options:
            # 尋找數字後面的選項
            simple_pattern = r'(\d+)\s*([ＡＢＣＤ])\s*([^ＡＢＣＤ]*)'
            matches = re.findall(simple_pattern, question_text)
            for match in matches:
                option_letter = match[1]
                option_content = match[2].strip()
                if option_content:
                    options[option_letter] = option_content
        
        return options

def process_pdf_with_final_groups(pdf_path: str, output_dir: str = "", 
                                 answer_pdf_path: str = "") -> Tuple[List[str], Dict[str, Any]]:
    """使用最終版處理器處理PDF"""
    
    print(f"\n{'='*70}")
    print(f"📄 {os.path.basename(pdf_path)} (最終版題組處理)")
    print(f"{'='*70}")
    
    try:
        # 提取PDF文字
        with pdfplumber.open(pdf_path) as pdf:
            text = ""
            for page in pdf.pages:
                text += page.extract_text() or ""
        
        print(f"📊 提取文字長度: {len(text)} 字元")
        
        # 檢測題組
        groups = FinalQuestionGroupProcessor.detect_question_groups(text)
        print(f"🔍 檢測到 {len(groups)} 個題組")
        
        questions = []
        
        if groups:
            # 處理題組
            for group in groups:
                print(f"   📚 題組 {group['start_question']}-{group['end_question']}: {group['question_count']} 題")
                group_questions = FinalQuestionGroupProcessor.extract_questions_from_group(group)
                questions.extend(group_questions)
        
        if not questions:
            print("❌ 未找到任何題目")
            return [], {}
        
        print(f"✅ 解析出 {len(questions)} 題")
        
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
        import traceback
        traceback.print_exc()
        return [], {}

def main():
    """主函數"""
    import argparse
    
    parser = argparse.ArgumentParser(description='最終版PDF轉CSV工具 - 支援題組處理')
    parser.add_argument('input', help='輸入PDF檔案')
    parser.add_argument('-o', '--output', default='', help='輸出目錄')
    parser.add_argument('--answer', default='', help='答案PDF檔案路徑')
    
    args = parser.parse_args()
    
    if os.path.isfile(args.input):
        saved_files, stats = process_pdf_with_final_groups(args.input, args.output, args.answer)
        
        if saved_files:
            print(f"\n✅ 已儲存: {saved_files}")
            print(f"📊 統計: {stats}")
        else:
            print("\n❌ 處理失敗")
    else:
        print("❌ 輸入檔案不存在")

if __name__ == "__main__":
    main()