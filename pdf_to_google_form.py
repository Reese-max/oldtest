#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF轉Google表單CSV工具
專門為Google Apps Script製作Google表單而設計
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
import google.generativeai as genai
from google.generativeai.client import configure
from google.generativeai.generative_models import GenerativeModel
from google.generativeai.files import upload_file, get_file
import time

class GoogleFormCSVGenerator:
    """Google表單CSV生成器"""
    
    def __init__(self):
        self.questions = []
        self.answers = {}
        self.corrected_answers = {}
    
    def add_question(self, question_data: Dict[str, Any]):
        """添加題目資料"""
        self.questions.append(question_data)
    
    def add_answer(self, question_num: str, answer: str):
        """添加正確答案"""
        self.answers[question_num] = answer
    
    def add_corrected_answer(self, question_num: str, corrected_answer: str):
        """添加更正答案"""
        self.corrected_answers[question_num] = corrected_answer
    
    def generate_google_form_csv(self, output_path: str) -> str:
        """生成適合Google表單的CSV檔案"""
        
        # Google表單需要的欄位格式
        csv_data = []
        
        for i, q in enumerate(self.questions, 1):
            question_num = str(i)
            
            # 基本題目資訊
            row = {
                '題號': question_num,
                '題目': q.get('題目', ''),
                '題型': q.get('題型', '選擇題'),
                '選項A': q.get('選項A', ''),
                '選項B': q.get('選項B', ''),
                '選項C': q.get('選項C', ''),
                '選項D': q.get('選項D', ''),
                '正確答案': self.answers.get(question_num, ''),
                '更正答案': self.corrected_answers.get(question_num, ''),
                '最終答案': self.corrected_answers.get(question_num, self.answers.get(question_num, '')),
                '難度': self._calculate_difficulty(q),
                '分類': self._categorize_question(q),
                '備註': ''
            }
            
            csv_data.append(row)
        
        # 建立DataFrame並儲存
        df = pd.DataFrame(csv_data)
        df.to_csv(output_path, index=False, encoding='utf-8-sig')
        
        return output_path
    
    def _calculate_difficulty(self, question: Dict[str, Any]) -> str:
        """計算題目難度"""
        title = question.get('題目', '')
        
        # 簡單的難度判斷邏輯
        if len(title) > 100:
            return '困難'
        elif len(title) > 50:
            return '中等'
        else:
            return '簡單'
    
    def _categorize_question(self, question: Dict[str, Any]) -> str:
        """題目分類"""
        title = question.get('題目', '')
        
        # 根據題目內容進行分類
        if '讀音' in title or '發音' in title:
            return '語音'
        elif '錯別字' in title or '字形' in title:
            return '字形'
        elif '成語' in title or '慣用語' in title:
            return '成語'
        elif '文法' in title or '語法' in title:
            return '文法'
        elif '修辭' in title:
            return '修辭'
        else:
            return '綜合'

class AnswerProcessor:
    """答案處理器"""
    
    @staticmethod
    def extract_answers_from_pdf(pdf_path: str) -> Dict[str, str]:
        """從PDF中提取答案"""
        answers = {}
        
        try:
            with pdfplumber.open(pdf_path) as pdf:
                text = ""
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
            
            # 使用正則表達式提取答案
            # 匹配格式：1. A 或 1.A 或 1) A
            answer_patterns = [
                r'(\d+)[\.\)]\s*([A-D])',
                r'(\d+)\s*([A-D])',
                r'第\s*(\d+)\s*題\s*([A-D])'
            ]
            
            for pattern in answer_patterns:
                matches = re.findall(pattern, text)
                for match in matches:
                    question_num, answer = match
                    answers[question_num] = answer
            
        except Exception as e:
            print(f"❌ 答案提取失敗: {e}")
        
        return answers
    
    @staticmethod
    def extract_corrected_answers_from_pdf(pdf_path: str) -> Dict[str, str]:
        """從更正答案PDF中提取答案"""
        corrected_answers = {}
        
        try:
            with pdfplumber.open(pdf_path) as pdf:
                text = ""
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
            
            # 更正答案的特殊格式處理
            corrected_patterns = [
                r'更正.*?(\d+)[\.\)]\s*([A-D])',
                r'(\d+)[\.\)]\s*([A-D])\s*更正',
                r'(\d+)\s*([A-D])\s*\(更正\)'
            ]
            
            for pattern in corrected_patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                for match in matches:
                    question_num, answer = match
                    corrected_answers[question_num] = answer
            
        except Exception as e:
            print(f"❌ 更正答案提取失敗: {e}")
        
        return corrected_answers

class EnhancedPDFProcessor:
    """增強版PDF處理器"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key
        if api_key:
            configure(api_key=api_key)
    
    def process_pdf_to_google_form_csv(self, 
                                     pdf_path: str, 
                                     answer_pdf_path: str = None,
                                     corrected_answer_pdf_path: str = None,
                                     output_path: str = None) -> str:
        """處理PDF並生成Google表單CSV"""
        
        print(f"\n{'='*70}")
        print(f"📄 處理檔案: {os.path.basename(pdf_path)}")
        print(f"{'='*70}")
        
        # 1. 提取題目
        questions = self._extract_questions_from_pdf(pdf_path)
        if not questions:
            print("❌ 無法提取題目")
            return None
        
        # 2. 建立CSV生成器
        csv_generator = GoogleFormCSVGenerator()
        
        # 3. 添加題目
        for q in questions:
            csv_generator.add_question(q)
        
        # 4. 處理答案
        if answer_pdf_path and os.path.exists(answer_pdf_path):
            print("🔍 提取正確答案...")
            answers = AnswerProcessor.extract_answers_from_pdf(answer_pdf_path)
            for q_num, answer in answers.items():
                csv_generator.add_answer(q_num, answer)
            print(f"✅ 找到 {len(answers)} 個答案")
        
        # 5. 處理更正答案
        if corrected_answer_pdf_path and os.path.exists(corrected_answer_pdf_path):
            print("🔍 提取更正答案...")
            corrected_answers = AnswerProcessor.extract_corrected_answers_from_pdf(corrected_answer_pdf_path)
            for q_num, answer in corrected_answers.items():
                csv_generator.add_corrected_answer(q_num, answer)
            print(f"✅ 找到 {len(corrected_answers)} 個更正答案")
        
        # 6. 生成CSV
        if not output_path:
            base_name = os.path.splitext(os.path.basename(pdf_path))[0]
            output_path = f"{base_name}_Google表單.csv"
        
        csv_path = csv_generator.generate_google_form_csv(output_path)
        print(f"✅ CSV已生成: {csv_path}")
        
        return csv_path
    
    def _extract_questions_from_pdf(self, pdf_path: str) -> List[Dict[str, Any]]:
        """從PDF提取題目（使用現有的解析邏輯）"""
        try:
            # 使用現有的文字提取方法
            with pdfplumber.open(pdf_path) as pdf:
                text = ""
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
            
            # 簡單的題目解析（可以後續整合Gemini API）
            questions = self._parse_questions_from_text(text)
            return questions
            
        except Exception as e:
            print(f"❌ 題目提取失敗: {e}")
            return []
    
    def _parse_questions_from_text(self, text: str) -> List[Dict[str, Any]]:
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
        
        matches = []
        for pattern in patterns:
            matches = re.findall(pattern, text, re.DOTALL)
            if matches:
                print(f"✅ 使用模式找到 {len(matches)} 題")
                break
        
        if not matches:
            # 如果正則表達式失敗，嘗試逐行解析
            print("⚠️ 正則表達式解析失敗，嘗試逐行解析...")
            questions = self._parse_questions_line_by_line(text)
            return questions
        
        for match in matches:
            question_num, title, option_a, option_b, option_c, option_d = match
            
            # 清理文字
            title = self._clean_text(title)
            option_a = self._clean_text(option_a)
            option_b = self._clean_text(option_b)
            option_c = self._clean_text(option_c)
            option_d = self._clean_text(option_d)
            
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
    
    def _parse_questions_line_by_line(self, text: str) -> List[Dict[str, Any]]:
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
    
    def _clean_text(self, text: str) -> str:
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
    """主程式"""
    print("PDF轉Google表單CSV工具")
    print("="*50)
    
    # 測試檔案路徑
    test_pdf = "test_pdfs/真實測試考古題.pdf"
    
    if not os.path.exists(test_pdf):
        print(f"❌ 測試PDF不存在: {test_pdf}")
        return
    
    # 建立處理器
    processor = EnhancedPDFProcessor()
    
    # 處理PDF
    csv_path = processor.process_pdf_to_google_form_csv(
        pdf_path=test_pdf,
        output_path="test_output/測試考古題_Google表單.csv"
    )
    
    if csv_path:
        print(f"\n🎉 處理完成！")
        print(f"📄 CSV檔案: {csv_path}")
        
        # 顯示CSV內容預覽
        try:
            df = pd.read_csv(csv_path, encoding='utf-8-sig')
            print(f"\n📊 CSV內容預覽:")
            print(f"   總題數: {len(df)}")
            print(f"   欄位: {list(df.columns)}")
            print(f"\n前3題預覽:")
            print(df.head(3).to_string(index=False))
        except Exception as e:
            print(f"❌ 無法讀取CSV: {e}")

if __name__ == "__main__":
    main()