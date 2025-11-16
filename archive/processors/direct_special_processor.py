#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
直接特殊格式處理器 - 直接處理特殊格式的題目
"""

import os
import pdfplumber
import pandas as pd
import re
import json
from typing import List, Dict, Any, Optional, Tuple
import glob

class DirectSpecialProcessor:
    """直接特殊格式處理器"""
    
    @staticmethod
    def process_pdf_direct_special(pdf_path: str, output_dir: str = "", 
                                 answer_pdf_path: str = "") -> Tuple[List[str], Dict[str, Any]]:
        """直接特殊格式PDF處理"""
        
        print(f"\n{'='*70}")
        print(f"📄 {os.path.basename(pdf_path)} (直接特殊格式處理)")
        print(f"{'='*70}")
        
        try:
            # 提取PDF文字
            with pdfplumber.open(pdf_path) as pdf:
                text = ""
                for page in pdf.pages:
                    text += page.extract_text() or ""
            
            print(f"📊 提取文字長度: {len(text)} 字元")
            
            # 直接處理特殊格式
            questions = DirectSpecialProcessor.extract_questions_direct_special(text)
            
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
    
    @staticmethod
    def extract_questions_direct_special(text: str) -> List[Dict[str, Any]]:
        """直接特殊格式提取題目"""
        questions = []
        
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
                
                print(f"🔍 找到題組 {start_q}-{end_q}")
                
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
                
                # 直接處理題組中的題目
                group_questions = DirectSpecialProcessor.extract_questions_from_group_direct_special(group_content, start_q, end_q)
                questions.extend(group_questions)
        
        return questions
    
    @staticmethod
    def extract_questions_from_group_direct_special(group_content: str, start_q: int, end_q: int) -> List[Dict[str, Any]]:
        """直接特殊格式從題組中提取題目"""
        questions = []
        
        print(f"   📚 處理題組 {start_q}-{end_q}，內容長度: {len(group_content)} 字元")
        
        # 在題組內容中尋找題目
        for q_num in range(start_q, end_q + 1):
            # 直接特殊格式的題目模式 - 直接匹配題號後面的選項
            question_patterns = [
                # 匹配題號後面的選項，使用更精確的模式
                rf'{q_num}\s*([ＡＢＣＤ][^ＡＢＣＤ]*?[ＡＢＣＤ][^ＡＢＣＤ]*?[ＡＢＣＤ][^ＡＢＣＤ]*?[ＡＢＣＤ][^ＡＢＣＤ]*)',
                rf'{q_num}\s*([ABCD][^ABCD]*?[ABCD][^ABCD]*?[ABCD][^ABCD]*?[ABCD][^ABCD]*)',
            ]
            
            question_found = False
            for pattern in question_patterns:
                match = re.search(pattern, group_content)
                if match:
                    question_text = match.group(1)
                    print(f"   📝 找到題目 {q_num}: {question_text[:100]}...")
                    
                    # 直接特殊格式選項提取
                    options = DirectSpecialProcessor.extract_options_direct_special(question_text)
                    
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
    def extract_options_direct_special(question_text: str) -> Dict[str, str]:
        """直接特殊格式選項提取"""
        options = {}
        
        # 直接特殊格式選項提取
        # 格式：Ａcompressed Ｂabridged Ｃextended Ｄabbreviated
        
        # 嘗試不同的選項模式
        option_patterns = [
            # 中文選項模式 - 匹配選項字母後面的內容
            r'([ＡＢＣＤ])([^ＡＢＣＤ]*)',
            # 英文選項模式
            r'([ABCD])([^ABCD]*)',
        ]
        
        for pattern in option_patterns:
            matches = re.findall(pattern, question_text)
            if len(matches) >= 4:  # 至少要有4個選項
                for match in matches:
                    option_letter = match[0]
                    option_content = match[1].strip()
                    if option_content:
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

def main():
    """主函數"""
    import argparse
    
    parser = argparse.ArgumentParser(description='直接特殊格式處理器 - 處理特殊格式題目')
    parser.add_argument('input', help='輸入PDF檔案')
    parser.add_argument('-o', '--output', default='', help='輸出目錄')
    parser.add_argument('--answer', default='', help='答案PDF檔案路徑')
    
    args = parser.parse_args()
    
    if os.path.isfile(args.input):
        saved_files, stats = DirectSpecialProcessor.process_pdf_direct_special(args.input, args.output, args.answer)
        
        if saved_files:
            print(f"\n✅ 已儲存: {saved_files}")
            print(f"📊 統計: {stats}")
        else:
            print("\n❌ 處理失敗")
    else:
        print("❌ 輸入檔案不存在")

if __name__ == "__main__":
    main()