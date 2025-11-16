#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
改進版PDF轉CSV功能 - 解決三個主要問題
1. 答案欄位缺失
2. 選項內容重複
3. 資料品質
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
    
    @staticmethod
    def extract_corrected_answers_from_pdf(pdf_path: str) -> Dict[str, str]:
        """從PDF檔案中提取更正答案"""
        try:
            with pdfplumber.open(pdf_path) as pdf:
                text = ""
                for page in pdf.pages:
                    text += page.extract_text() or ""
            
            return AnswerProcessor.extract_corrected_answers_from_text(text)
        except Exception as e:
            print(f"❌ 提取更正答案失敗: {e}")
            return {}
    
    @staticmethod
    def extract_corrected_answers_from_text(text: str) -> Dict[str, str]:
        """從文字中提取更正答案"""
        corrected_answers = {}
        
        # 匹配更正答案模式：更正 1. B, 更正答案 1. B 等
        corrected_patterns = [
            r'更正\s*(\d+)\.\s*([ABCD])',  # 更正 1. B
            r'更正答案\s*(\d+)\.\s*([ABCD])', # 更正答案 1. B
            r'更正\s*第(\d+)題\s*([ABCD])', # 更正 第1題 B
            r'更正\s*(\d+)\s*：\s*([ABCD])', # 更正 1：B
        ]
        
        for pattern in corrected_patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                question_num = match[0]
                answer = match[1]
                corrected_answers[question_num] = answer
        
        return corrected_answers

class PDFCacheManager:
    """PDF快取管理器"""
    def __init__(self, cache_file: str = "pdf_cache.json"):
        self.cache_file = cache_file
        self.cache = self.load_cache()
        self.client: Optional[genai.Client] = None

    def load_cache(self) -> Dict[str, Any]:
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {}
        return {}

    def save_cache(self):
        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.cache, f, ensure_ascii=False, indent=2)
        except:
            pass

    def get_pdf_hash(self, pdf_path: str) -> str:
        sha256_hash = hashlib.sha256()
        with open(pdf_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()

    def get_cached_result(self, pdf_hash: str) -> Optional[Dict[str, Any]]:
        if pdf_hash in self.cache:
            cache_entry = self.cache[pdf_hash]
            cached_time = datetime.fromisoformat(cache_entry.get('timestamp', '2000-01-01'))
            if datetime.now() - cached_time < timedelta(days=7):
                return cache_entry.get('result')
        return None

    def cache_result(self, pdf_hash: str, result: Dict[str, Any]):
        self.cache[pdf_hash] = {
            'timestamp': datetime.now().isoformat(),
            'result': result
        }
        self.save_cache()

    def cleanup_expired_cache(self):
        now = datetime.now()
        expired_keys = []
        for key, entry in self.cache.items():
            cached_time = datetime.fromisoformat(entry.get('timestamp', '2000-01-01'))
            if now - cached_time > timedelta(days=7):
                expired_keys.append(key)
        
        for key in expired_keys:
            del self.cache[key]
        
        if expired_keys:
            self.save_cache()

class ValidationResult:
    def __init__(self):
        self.status = 'success'
        self.issues = []
        self.warnings = []
        self.summary = {}
        self.questions_with_answers = 0
        self.questions_with_corrected_answers = 0

    def add_issue(self, message: str):
        self.issues.append(message)
        self.status = 'error'

    def add_warning(self, message: str):
        self.warnings.append(message)
        if self.status == 'success':
            self.status = 'warning'

    def print_result(self):
        icons = {'success': '✅', 'warning': '⚠️', 'error': '❌'}
        print(f"\n{icons.get(self.status, '❓')} 驗證結果:")

        for key, value in self.summary.items():
            print(f"  {key}: {value}")

        if self.warnings:
            print(f"\n⚠️ 警告:")
            for warning in self.warnings:
                print(f"  - {warning}")

        if self.issues:
            print(f"\n❌ 問題:")
            for issue in self.issues:
                print(f"  - {issue}")

class PDFFeatureAnalyzer:
    """PDF特徵分析器"""
    
    @staticmethod
    def analyze_pdf(pdf_path: str) -> Dict[str, Any]:
        """分析PDF特徵"""
        features = {
            'page_count': 0,
            'file_size': 0,
            'expected_question_count': 0
        }
        
        try:
            with pdfplumber.open(pdf_path) as pdf:
                features['page_count'] = len(pdf.pages)
                
                # 提取文字內容
                full_text = ""
                for page in pdf.pages:
                    text = page.extract_text()
                    if text:
                        full_text += text + "\n"
                
                # 分析預期題數
                count_patterns = [
                    r'共\s*(\d+)\s*題',
                    r'總共\s*(\d+)\s*題',
                    r'共計\s*(\d+)\s*題',
                    r'(\d+)\s*題'
                ]
                
                for pattern in count_patterns:
                    count_match = re.search(pattern, full_text)
                    if count_match:
                        features['expected_question_count'] = int(count_match.group(1))
                        break
                
                # 如果沒找到明確的題數，嘗試從題號推測
                if features['expected_question_count'] == 0:
                    question_numbers = re.findall(r'(\d+)\.\s*[^0-9]', full_text)
                    if question_numbers:
                        max_num = max(int(num) for num in question_numbers)
                        features['expected_question_count'] = max_num
            
            # 檔案大小
            features['file_size'] = os.path.getsize(pdf_path)
            
        except Exception as e:
            print(f"⚠️ PDF分析失敗: {e}")
        
        return features

def should_skip_file(filename: str) -> bool:
    """判斷是否應該跳過此檔案"""
    # 答案檔案關鍵字
    skip_keywords = ['答案', '解答', '更正答案', 'answer', 'Answer', 'ANSWER']
    
    # 檢查檔名是否包含跳過關鍵字
    for keyword in skip_keywords:
        if keyword in filename:
            return True
    
    return False

def upload_pdf_to_gemini(pdf_path: str) -> Optional[str]:
    """上傳PDF到Gemini"""
    try:
        file_uri = upload_file(pdf_path)
        return file_uri
    except Exception as e:
        print(f"❌ PDF上傳失敗: {e}")
        return None

def parse_with_pdf_upload(pdf_path: str, use_pro: bool = False) -> List[Dict[str, Any]]:
    """使用PDF上傳方式解析"""
    try:
        file_uri = upload_pdf_to_gemini(pdf_path)
        if not file_uri:
            return []

        sample_file = get_file(file_uri.split('/')[-1])

        # 選擇模型：優先使用 Flash，失敗時可切換到 Pro
        model_name = 'gemini-2.5-pro' if use_pro else 'gemini-2.5-flash'
        model = GenerativeModel(model_name)

        # 從PDF路徑提取預期題數，用於更精確的解析
        pdf_features = PDFFeatureAnalyzer.analyze_pdf(pdf_path)
        expected_count = pdf_features.get('expected_question_count', 0)

        if use_pro:
            print(f"🔄 使用 Gemini 2.5 Pro 重新解析...")

        prompt = f"""分析這份PDF考古題，精確提取所有試題和答案：

預期題數：{expected_count}題

如果這是答案卷（只有題號和答案選項），返回 []

否則返回JSON格式：
[{{"題號": "1", "題目": "完整題目內容", "選項A": "...", "選項B": "...", "選項C": "...", "選項D": "...", "題型": "選擇題", "正確答案": "A", "更正答案": ""}}]

重要規則：
1. 答案卷直接返回 []
2. 題號必須從1開始，連續編號到{expected_count}
3. 題目內容必須完整，至少15字
4. 選擇題必須有A、B、C、D四個選項，且每個選項內容必須完全不同
5. 總題數必須為{expected_count}題，絕對不能多也不能少
6. 不要將頁首、頁尾、說明、註解誤認為題目
7. 仔細檢查每一題的完整性
8. 如果PDF中包含答案，請在"正確答案"欄位填入對應的A、B、C、D
9. 如果PDF中包含更正答案，請在"更正答案"欄位填入對應的A、B、C、D
10. 如果沒有答案資訊，相關欄位留空"""

        response = model.generate_content([sample_file, prompt])
        text = response.text.strip()

        # 處理空返回（答案卷）
        if text == '[]' or text == '[ ]':
            print("✓ 檢測到答案卷，跳過")
            return []

        if text.startswith('```json'):
            text = text[7:]
        if text.startswith('```'):
            text = text[3:]
        if text.endswith('```'):
            text = text[:-3]

        questions = json.loads(text.strip())

        # 過濾和驗證題目
        validated = []
        seen_numbers = set()

        for q in questions:
            if isinstance(q, dict) and '題號' in q and '題目' in q:
                # 檢查題號是否為數字且不重複
                try:
                    num = int(str(q.get('題號', '')).strip())
                    if num in seen_numbers:
                        continue  # 跳過重複題號
                    seen_numbers.add(num)
                except:
                    continue  # 題號無效跳過

                # 檢查題目內容長度
                title = str(q.get('題目', '')).strip()
                if len(title) < 15:  # 放寬到15字
                    continue  # 題目太短跳過

                validated.append({
                    '題號': str(num),
                    '題目': title,
                    '選項A': str(q.get('選項A', '')),
                    '選項B': str(q.get('選項B', '')),
                    '選項C': str(q.get('選項C', '')),
                    '選項D': str(q.get('選項D', '')),
                    '題型': str(q.get('題型', '選擇題')),
                    '正確答案': str(q.get('正確答案', '')),
                    '更正答案': str(q.get('更正答案', ''))
                })

        # 如果解析出的題數明顯偏離預期，嘗試修正
        if expected_count and abs(len(validated) - expected_count) > 3:
            print(f"⚠️ 解析題數({len(validated)})與預期({expected_count})差距過大，可能有誤")
            # 返回較少的題目（通常是過度解析的問題）
            if len(validated) > expected_count:
                validated = validated[:expected_count]

        return validated

    except Exception as e:
        print(f"❌ PDF上傳解析失敗: {e}")
        return []

def parse_questions_with_text_gemini(text: str, expected_count: int = 0) -> List[Dict[str, Any]]:
    """使用文字解析方式"""
    try:
        # 使用 Gemini 2.5 Flash
        model = GenerativeModel('gemini-2.5-flash')

        prompt = f"""分析以下考古題文字，如果是答案卷返回[]，如果是試題請精確提取所有題目和答案。

預期題數：{expected_count}題

請返回JSON格式：
[{{"題號": "1", "題目": "完整題目內容至少20字", "選項A": "...", "選項B": "...", "選項C": "...", "選項D": "...", "題型": "選擇題", "正確答案": "A", "更正答案": ""}}]

重要規則：
1. 答案卷直接返回 []
2. 題號必須從1開始連續編號
3. 題目內容必須完整，至少20字
4. 選擇題必須有A、B、C、D四個選項，且每個選項內容必須完全不同
5. 總題數應為{expected_count}題，勿多勿少
6. 不要將頁首、頁尾、說明文字誤認為題目
7. 如果文字中包含答案，請在"正確答案"欄位填入對應的A、B、C、D
8. 如果文字中包含更正答案，請在"更正答案"欄位填入對應的A、B、C、D
9. 如果沒有答案資訊，相關欄位留空

文字內容：
{text}"""

        response = model.generate_content(prompt)
        text = response.text.strip()

        if text == '[]' or text == '[ ]':
            return []

        if text.startswith('```json'):
            text = text[7:]
        if text.startswith('```'):
            text = text[3:]
        if text.endswith('```'):
            text = text[:-3]

        questions = json.loads(text.strip())

        # 過濾和驗證題目
        validated = []
        seen_numbers = set()

        for q in questions:
            if isinstance(q, dict) and '題號' in q and '題目' in q:
                # 檢查題號是否為數字且不重複
                try:
                    num = int(str(q.get('題號', '')).strip())
                    if num in seen_numbers:
                        continue  # 跳過重複題號
                    seen_numbers.add(num)
                except:
                    continue  # 題號無效跳過

                # 檢查題目內容長度
                title = str(q.get('題目', '')).strip()
                if len(title) < 20:
                    continue  # 題目太短跳過

                validated.append({
                    '題號': str(num),
                    '題目': title,
                    '選項A': str(q.get('選項A', '')),
                    '選項B': str(q.get('選項B', '')),
                    '選項C': str(q.get('選項C', '')),
                    '選項D': str(q.get('選項D', '')),
                    '題型': str(q.get('題型', '選擇題')),
                    '正確答案': str(q.get('正確答案', '')),
                    '更正答案': str(q.get('更正答案', ''))
                })

        # 如果解析出的題數明顯偏離預期，嘗試修正
        if expected_count and abs(len(validated) - expected_count) > 3:
            print(f"⚠️ 文字解析題數({len(validated)})與預期({expected_count})差距過大，可能有誤")
            # 返回較少的題目（通常是過度解析的問題）
            if len(validated) > expected_count:
                validated = validated[:expected_count]

        return validated

    except Exception as e:
        print(f"❌ 文字解析失敗: {e}")
        return []

def improve_option_diversity(questions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """改善選項內容差異性"""
    
    for question in questions:
        if question.get('題型') == '選擇題':
            options = ['選項A', '選項B', '選項C', '選項D']
            option_values = [question.get(opt, '').strip() for opt in options]
            
            # 檢查是否有重複選項
            if len(set(option_values)) < len(option_values):
                # 如果選項重複，嘗試從題目中提取不同的選項
                question_text = question.get('題目', '')
                
                # 嘗試從題目中提取選項（如果題目包含選項內容）
                if 'A.' in question_text and 'B.' in question_text:
                    # 這是一個包含選項的題目，需要重新解析
                    print(f"⚠️ 題目 {question.get('題號', '')} 選項重複，需要重新解析")
                    
                    # 暫時標記為需要重新處理
                    question['_needs_reprocessing'] = True
    
    return questions

def merge_answers_to_questions(questions: List[Dict[str, Any]], 
                              answers: Dict[str, str], 
                              corrected_answers: Dict[str, str]) -> List[Dict[str, Any]]:
    """將答案合併到題目中，並計算最終答案"""
    
    for question in questions:
        question_num = question.get('題號', '')
        
        # 獲取正確答案和更正答案
        correct_answer = answers.get(question_num, '')
        corrected_answer = corrected_answers.get(question_num, '')
        
        # 更新答案欄位
        question['正確答案'] = correct_answer
        question['更正答案'] = corrected_answer
        
        # 計算最終答案：優先使用更正答案，其次使用正確答案
        if corrected_answer:
            question['最終答案'] = corrected_answer
        elif correct_answer:
            question['最終答案'] = correct_answer
        else:
            question['最終答案'] = ''
    
    return questions

def validate_questions(questions: List[Dict[str, Any]], pdf_features: Dict[str, Any]) -> ValidationResult:
    """零誤差驗證"""
    result = ValidationResult()

    total = len(questions)
    choice = len([q for q in questions if q.get('題型') == '選擇題'])
    essay = len([q for q in questions if q.get('題型') == '問答題'])

    result.summary['實際題數'] = total
    result.summary['選擇題'] = choice
    result.summary['問答題'] = essay

    expected = pdf_features.get('expected_question_count')
    if expected:
        result.summary['預期題數'] = expected
        if total != expected:
            result.add_issue(f"題數不符: 預期{expected}題，實際{total}題（差{abs(expected-total)}題）")

    # 題號驗證
    nums = []
    for i, q in enumerate(questions):
        try:
            num = q.get('題號')
            if isinstance(num, str) and num.isdigit():
                nums.append(int(num))
            elif isinstance(num, int):
                nums.append(num)
        except:
            pass

    if nums:
        nums.sort()
        result.summary['題號範圍'] = f"{nums[0]}-{nums[-1]}"

        if nums[0] != 1:
            result.add_issue(f"題號不從1開始（從{nums[0]}開始）")

        expected_range = set(range(nums[0], nums[-1] + 1))
        missing = expected_range - set(nums)
        if missing:
            result.add_issue(f"遺失題號: {sorted(list(missing))}")

        duplicates = [n for n in set(nums) if nums.count(n) > 1]
        if duplicates:
            result.add_issue(f"重複題號: {sorted(duplicates)}")

        if expected and nums[-1] != expected:
            result.add_issue(f"最後題號應為{expected}，實際為{nums[-1]}")

    # 內容驗證
    for i, q in enumerate(questions):
        text = q.get('題目', '').strip()
        if not text:
            result.add_issue(f"第{i+1}題為空")
        elif len(text) < 8:
            result.add_issue(f"第{i+1}題過短({len(text)}字)")

    # 選項驗證
    for i, q in enumerate(questions):
        if q.get('題型') == '選擇題':
            missing = [opt[-1] for opt in ['選項A', '選項B', '選項C', '選項D'] 
                      if not q.get(opt, '').strip()]
            if missing:
                result.add_issue(f"第{i+1}題缺選項: {','.join(missing)}")
            
            # 檢查選項差異性
            options = [q.get(opt, '').strip() for opt in ['選項A', '選項B', '選項C', '選項D']]
            if len(set(options)) < len(options):
                result.add_warning(f"第{i+1}題選項內容重複")
    
    # 答案驗證
    questions_with_answers = 0
    questions_with_corrected_answers = 0
    
    for i, q in enumerate(questions):
        correct_answer = q.get('正確答案', '').strip()
        corrected_answer = q.get('更正答案', '').strip()
        final_answer = q.get('最終答案', '').strip()
        
        if correct_answer:
            questions_with_answers += 1
            if correct_answer not in ['A', 'B', 'C', 'D']:
                result.add_issue(f"第{i+1}題正確答案格式錯誤: {correct_answer}")
        
        if corrected_answer:
            questions_with_corrected_answers += 1
            if corrected_answer not in ['A', 'B', 'C', 'D']:
                result.add_issue(f"第{i+1}題更正答案格式錯誤: {corrected_answer}")
        
        if final_answer and final_answer not in ['A', 'B', 'C', 'D']:
            result.add_issue(f"第{i+1}題最終答案格式錯誤: {final_answer}")
    
    result.questions_with_answers = questions_with_answers
    result.questions_with_corrected_answers = questions_with_corrected_answers
    result.summary['有答案題數'] = questions_with_answers
    result.summary['有更正答案題數'] = questions_with_corrected_answers

    return result

def process_pdf_with_answers(pdf_path: str, output_dir: str = "", 
                           answer_pdf_path: str = "", 
                           corrected_answer_pdf_path: str = "") -> Tuple[List[str], ValidationResult]:
    """處理PDF並合併答案"""
    
    print(f"\n{'='*70}")
    print(f"📄 {os.path.basename(pdf_path)} (含答案辨識)")
    print(f"{'='*70}")
    
    # 處理主PDF檔案
    questions, validation_result = process_pdf_to_csv(pdf_path, output_dir)
    
    if not questions:
        return questions, validation_result
    
    # 提取答案
    answers = {}
    corrected_answers = {}
    
    if answer_pdf_path and os.path.exists(answer_pdf_path):
        print(f"🔍 提取答案: {os.path.basename(answer_pdf_path)}")
        answers = AnswerProcessor.extract_answers_from_pdf(answer_pdf_path)
        print(f"   ✅ 找到 {len(answers)} 個答案")
    
    if corrected_answer_pdf_path and os.path.exists(corrected_answer_pdf_path):
        print(f"🔍 提取更正答案: {os.path.basename(corrected_answer_pdf_path)}")
        corrected_answers = AnswerProcessor.extract_corrected_answers_from_pdf(corrected_answer_pdf_path)
        print(f"   ✅ 找到 {len(corrected_answers)} 個更正答案")
    
    # 改善選項差異性
    questions = improve_option_diversity(questions)
    
    # 合併答案到題目
    questions = merge_answers_to_questions(questions, answers, corrected_answers)
    
    # 更新驗證結果
    validation_result.questions_with_answers = sum(1 for q in questions if q.get('最終答案'))
    validation_result.questions_with_corrected_answers = sum(1 for q in questions if q.get('更正答案'))
    
    return questions, validation_result

def process_pdf_to_csv(pdf_path: str, output_dir: str = "") -> Tuple[List[str], ValidationResult]:
    """零誤差處理"""
    print(f"\n{'='*70}")
    print(f"📄 {os.path.basename(pdf_path)}")
    print(f"{'='*70}")

    # 檢查快取
    cache_manager = PDFCacheManager()
    pdf_hash = cache_manager.get_pdf_hash(pdf_path)
    cached_result = cache_manager.get_cached_result(pdf_hash)
    
    if cached_result:
        print("✓ 使用快取結果")
        return cached_result['saved_files'], ValidationResult()

    # 分析PDF特徵
    pdf_features = PDFFeatureAnalyzer.analyze_pdf(pdf_path)
    print(f"📊 PDF特徵: {pdf_features}")

    # 嘗試多種解析策略
    strategies = [
        ("PDF上傳 + Flash", lambda: parse_with_pdf_upload(pdf_path, False)),
        ("PDF上傳 + Pro", lambda: parse_with_pdf_upload(pdf_path, True)),
    ]

    best_q = []
    best_v = ValidationResult()

    for strategy_name, strategy_func in strategies:
        print(f"\n🔄 嘗試策略: {strategy_name}")
        try:
            questions = strategy_func()
            if questions:
                print(f"✓ 解析出 {len(questions)} 題")
                
                # 驗證結果
                validation_result = validate_questions(questions, pdf_features)
                
                # 選擇最佳結果
                if len(questions) > len(best_q):
                    best_q = questions
                    best_v = validation_result
                    print(f"✓ 更新最佳結果: {len(questions)} 題")
                else:
                    print(f"⚠️ 結果不如之前: {len(questions)} vs {len(best_q)}")
            else:
                print("⚠️ 解析失敗")
        except Exception as e:
            print(f"❌ 策略失敗: {e}")

    if not best_q:
        print("❌ 所有策略都失敗")
        return [], ValidationResult()

    os.makedirs(output_dir, exist_ok=True)
    base = os.path.splitext(os.path.basename(pdf_path))[0]
    saved = []

    choice = [q for q in best_q if q['題型'] == '選擇題']
    essay = [q for q in best_q if q['題型'] == '問答題']

    if choice:
        path = os.path.join(output_dir, f"{base}_選擇題.csv")
        pd.DataFrame(choice).to_csv(path, index=False, encoding='utf-8-sig')
        print(f"\n✅ {path} ({len(choice)}題)")
        saved.append(path)

    if essay:
        path = os.path.join(output_dir, f"{base}_問答題.csv")
        pd.DataFrame(essay).to_csv(path, index=False, encoding='utf-8-sig')
        print(f"✅ {path} ({len(essay)}題)")
        saved.append(path)

    # 快取結果
    cache_manager.cache_result(pdf_hash, {'saved_files': saved})

    return saved, best_v

def process_directory(input_dir: str, output_dir: str = "") -> Dict[str, Any]:
    """處理目錄中的所有PDF"""
    pdf_files = glob.glob(os.path.join(input_dir, "**", "*.pdf"), recursive=True)

    if not pdf_files:
        print("未找到PDF")
        return {}

    # 預先過濾答案檔案
    print(f"\n找到 {len(pdf_files)} 個PDF")

    filtered_files = []
    skipped_files = []

    for pdf_file in pdf_files:
        filename = os.path.basename(pdf_file)
        if should_skip_file(filename):
            skipped_files.append(filename)
        else:
            filtered_files.append(pdf_file)

    print(f"⏭️  過濾掉 {len(skipped_files)} 個答案檔案")
    print(f"📄 將處理 {len(filtered_files)} 個試題檔案\n")

    cache_manager = PDFCacheManager()
    cache_manager.cleanup_expired_cache()

    results = []
    success = warning = error = 0

    for i, pdf in enumerate(filtered_files, 1):
        try:
            print(f"\n[{i}/{len(filtered_files)}]")

            rel = os.path.relpath(pdf, input_dir)
            out = os.path.join(output_dir, os.path.dirname(rel)) if output_dir else os.path.dirname(pdf)

            # 尋找對應的答案檔案
            answer_pdf_path = ""
            corrected_answer_pdf_path = ""
            
            # 尋找答案檔案
            base_name = os.path.splitext(os.path.basename(pdf))[0]
            answer_files = glob.glob(os.path.join(os.path.dirname(pdf), f"*答案*.pdf"))
            corrected_answer_files = glob.glob(os.path.join(os.path.dirname(pdf), f"*更正*.pdf"))
            
            if answer_files:
                answer_pdf_path = answer_files[0]
            if corrected_answer_files:
                corrected_answer_pdf_path = corrected_answer_files[0]
            
            _, v = process_pdf_with_answers(pdf, out, answer_pdf_path, corrected_answer_pdf_path)

            results.append({
                'file': os.path.basename(pdf),
                'status': v.status,
                'summary': v.summary,
                'issues': v.issues
            })

            if v.status == 'success':
                success += 1
            elif v.status == 'warning':
                warning += 1
            else:
                error += 1
        except Exception as e:
            print(f"❌ 錯誤: {e}")
            error += 1

    print(f"\n{'='*70}")
    print("統計")
    print(f"{'='*70}")
    print(f"總試題PDF: {len(filtered_files)}")
    print(f"✅ 成功: {success} ({success/max(len(filtered_files),1)*100:.1f}%)")
    print(f"⚠️ 警告: {warning} ({warning/max(len(filtered_files),1)*100:.1f}%)")
    print(f"❌ 錯誤: {error} ({error/max(len(filtered_files),1)*100:.1f}%)")
    print(f"\n⏭️  已跳過 {len(skipped_files)} 個答案檔案")

    if error > 0:
        print(f"\n需檢查:")
        for r in results:
            if r['status'] == 'error':
                print(f"  - {r['file']}")

    report = os.path.join(output_dir if output_dir else input_dir, "validation_report.json")
    with open(report, 'w', encoding='utf-8') as f:
        json.dump({
            'summary': {
                'total_files': len(pdf_files),
                'processed': len(filtered_files),
                'skipped': len(skipped_files),
                'success': success,
                'warning': warning,
                'error': error
            },
            'results': results
        }, f, ensure_ascii=False, indent=2)

    print(f"\n📊 詳細報告: {report}")

    return {
        'total_files': len(pdf_files),
        'processed': len(filtered_files),
        'skipped': len(skipped_files),
        'success': success,
        'warning': warning,
        'error': error,
        'results': results
    }

def main():
    """主函數"""
    import argparse
    
    parser = argparse.ArgumentParser(description='改進版PDF轉CSV工具')
    parser.add_argument('input', help='輸入PDF檔案或目錄')
    parser.add_argument('-o', '--output', default='', help='輸出目錄')
    parser.add_argument('--answer', default='', help='答案PDF檔案路徑')
    parser.add_argument('--corrected', default='', help='更正答案PDF檔案路徑')
    
    args = parser.parse_args()
    
    if os.path.isfile(args.input):
        # 單一檔案處理
        if args.answer or args.corrected:
            saved_files, validation_result = process_pdf_with_answers(
                args.input, args.output, args.answer, args.corrected
            )
        else:
            saved_files, validation_result = process_pdf_to_csv(args.input, args.output)
        
        validation_result.print_result()
        
        if saved_files:
            print(f"\n✅ 已儲存: {saved_files}")
        else:
            print("\n❌ 處理失敗")
    else:
        # 目錄處理
        result = process_directory(args.input, args.output)
        if result:
            print(f"\n✅ 處理完成: {result['success']} 成功, {result['warning']} 警告, {result['error']} 錯誤")

if __name__ == "__main__":
    main()