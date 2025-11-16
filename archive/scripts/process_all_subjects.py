#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
處理所有科目 - 將第114年司法三等考試監獄官的所有科目轉換為CSV
"""

import os
import pdfplumber
import pandas as pd
import re
import json
from typing import List, Dict, Any, Optional, Tuple
import glob

class AllSubjectsProcessor:
    """所有科目處理器"""
    
    @staticmethod
    def process_all_subjects(base_dir: str, output_dir: str = "") -> Dict[str, Any]:
        """處理所有科目"""
        
        print(f"\n{'='*70}")
        print(f"📚 處理第114年司法三等考試監獄官所有科目")
        print(f"{'='*70}")
        
        # 監獄官科目目錄
        subjects_dir = os.path.join(base_dir, "民國114年", "民國114年_司法特考", "監獄官")
        
        if not os.path.exists(subjects_dir):
            print(f"❌ 科目目錄不存在: {subjects_dir}")
            return {}
        
        # 獲取所有科目
        subjects = os.listdir(subjects_dir)
        print(f"📋 找到 {len(subjects)} 個科目")
        
        results = {}
        total_questions = 0
        
        for subject in subjects:
            subject_path = os.path.join(subjects_dir, subject)
            if os.path.isdir(subject_path):
                print(f"\n📖 處理科目: {subject}")
                
                # 處理科目
                subject_result = AllSubjectsProcessor.process_subject(subject_path, subject, output_dir)
                if subject_result:
                    results[subject] = subject_result
                    total_questions += subject_result.get('total_questions', 0)
        
        print(f"\n{'='*70}")
        print(f"📊 處理完成統計")
        print(f"{'='*70}")
        print(f"✅ 處理科目: {len(results)} 個")
        print(f"📝 總題數: {total_questions} 題")
        
        return results
    
    @staticmethod
    def process_subject(subject_path: str, subject_name: str, output_dir: str) -> Dict[str, Any]:
        """處理單一科目"""
        
        # 尋找試題和答案檔案
        question_files = glob.glob(os.path.join(subject_path, "*試題*.pdf"))
        answer_files = glob.glob(os.path.join(subject_path, "*答案*.pdf"))
        
        if not question_files:
            print(f"   ⚠️ 未找到試題檔案")
            return {}
        
        question_file = question_files[0]
        answer_file = answer_files[0] if answer_files else None
        
        print(f"   📄 試題檔案: {os.path.basename(question_file)}")
        if answer_file:
            print(f"   📄 答案檔案: {os.path.basename(answer_file)}")
        
        # 處理PDF
        questions = AllSubjectsProcessor.extract_questions_from_pdf(question_file, answer_file)
        
        if not questions:
            print(f"   ❌ 未提取到題目")
            return {}
        
        print(f"   ✅ 提取到 {len(questions)} 題")
        
        # 儲存CSV
        os.makedirs(output_dir, exist_ok=True)
        
        # 清理科目名稱
        clean_subject_name = re.sub(r'[\\/*?:"<>|]', "_", subject_name)
        
        # 分類題目
        regular_questions = [q for q in questions if not q.get('題組', False)]
        group_questions = [q for q in questions if q.get('題組', False)]
        
        saved_files = []
        
        if regular_questions:
            path = os.path.join(output_dir, f"{clean_subject_name}_一般題目.csv")
            pd.DataFrame(regular_questions).to_csv(path, index=False, encoding='utf-8-sig')
            print(f"   ✅ {path} ({len(regular_questions)}題)")
            saved_files.append(path)
        
        if group_questions:
            path = os.path.join(output_dir, f"{clean_subject_name}_題組題目.csv")
            pd.DataFrame(group_questions).to_csv(path, index=False, encoding='utf-8-sig')
            print(f"   ✅ {path} ({len(group_questions)}題)")
            saved_files.append(path)
        
        # 合併所有題目
        if questions:
            path = os.path.join(output_dir, f"{clean_subject_name}_完整題目.csv")
            pd.DataFrame(questions).to_csv(path, index=False, encoding='utf-8-sig')
            print(f"   ✅ {path} ({len(questions)}題)")
            saved_files.append(path)
        
        return {
            'total_questions': len(questions),
            'regular_questions': len(regular_questions),
            'group_questions': len(group_questions),
            'saved_files': saved_files
        }
    
    @staticmethod
    def extract_questions_from_pdf(pdf_path: str, answer_pdf_path: str = None) -> List[Dict[str, Any]]:
        """從PDF中提取題目"""
        
        try:
            # 提取PDF文字
            with pdfplumber.open(pdf_path) as pdf:
                text = ""
                for page in pdf.pages:
                    text += page.extract_text() or ""
            
            # 檢測題組
            groups = AllSubjectsProcessor.detect_question_groups(text)
            
            questions = []
            
            if groups:
                # 處理題組
                for group in groups:
                    group_questions = AllSubjectsProcessor.extract_questions_from_group(group)
                    questions.extend(group_questions)
            
            # 處理非題組的單獨題目
            # 這裡可以添加處理單獨題目的邏輯
            
            return questions
            
        except Exception as e:
            print(f"   ❌ 提取失敗: {e}")
            return []
    
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
        """從題組中提取題目"""
        questions = []
        start_q = group['start_question']
        end_q = group['end_question']
        group_content = group['content']
        
        # 在題組內容中尋找題目
        for q_num in range(start_q, end_q + 1):
            # 尋找題目模式
            question_patterns = [
                rf'{q_num}\s*[ＡＢＣＤ][^ＡＢＣＤ]*[ＡＢＣＤ][^ＡＢＣＤ]*[ＡＢＣＤ][^ＡＢＣＤ]*[ＡＢＣＤ]',  # 完整選項模式
                rf'{q_num}\s*[ABCD][^ABCD]*[ABCD][^ABCD]*[ABCD][^ABCD]*[ABCD]',  # 英文選項模式
            ]
            
            question_found = False
            for pattern in question_patterns:
                match = re.search(pattern, group_content)
                if match:
                    question_text = match.group()
                    
                    # 提取選項
                    options = AllSubjectsProcessor.extract_options_from_question(question_text)
                    
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

def main():
    """主函數"""
    import argparse
    
    parser = argparse.ArgumentParser(description='處理所有科目 - 支援題組處理')
    parser.add_argument('input', help='輸入目錄')
    parser.add_argument('-o', '--output', default='', help='輸出目錄')
    
    args = parser.parse_args()
    
    if os.path.isdir(args.input):
        results = AllSubjectsProcessor.process_all_subjects(args.input, args.output)
        
        if results:
            print(f"\n✅ 處理完成: {len(results)} 個科目")
        else:
            print("\n❌ 處理失敗")
    else:
        print("❌ 輸入目錄不存在")

if __name__ == "__main__":
    main()