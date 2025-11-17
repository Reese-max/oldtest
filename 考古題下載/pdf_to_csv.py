import os
import pdfplumber
import pandas as pd
import re
import json
import hashlib
from typing import List, Dict, Any, Optional, Tuple
import glob
from datetime import datetime, timedelta
from google import genai
from google.generativeai.client import configure
from google.generativeai.generative_models import GenerativeModel
from google.generativeai.files import upload_file, get_file
import time

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
                print(f"✅ 使用快取結果")
                return cache_entry.get('result')
        return None

    def set_cached_result(self, pdf_hash: str, result: Dict[str, Any]):
        self.cache[pdf_hash] = {
            'result': result,
            'timestamp': datetime.now().isoformat()
        }
        self.save_cache()

    def cleanup_expired_cache(self):
        expired = [k for k, v in self.cache.items() 
                  if datetime.now() - datetime.fromisoformat(v.get('timestamp', '2000-01-01')) >= timedelta(days=7)]
        for k in expired:
            del self.cache[k]
        if expired:
            self.save_cache()

class PDFFeatureAnalyzer:
    @staticmethod
    def analyze_pdf(pdf_path: str) -> Dict[str, Any]:
        features = {
            'page_count': 0,
            'file_size_mb': 0.0,
            'expected_question_count': None
        }

        try:
            features['file_size_mb'] = os.path.getsize(pdf_path) / (1024 * 1024)

            with pdfplumber.open(pdf_path) as pdf:
                features['page_count'] = len(pdf.pages)
                full_text = ""
                for page in pdf.pages:
                    text = page.extract_text()
                    if text:
                        full_text += text + "\n"

                # 提取預期題數
                count_match = re.search(r'共\s*(\d+)\s*題', full_text)
                if count_match:
                    features['expected_question_count'] = int(count_match.group(1))
        except:
            pass

        return features

class ValidationResult:
    def __init__(self):
        self.status = 'success'
        self.issues = []
        self.warnings = []
        self.summary = {}

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
            print(f"   {key}: {value}")

        if self.issues:
            print(f"   嚴重問題:")
            for issue in self.issues:
                print(f"     ❌ {issue}")

        if self.warnings:
            print(f"   警告:")
            for warning in self.warnings[:3]:
                print(f"     ⚠️ {warning}")

cache_manager = PDFCacheManager()

def setup_gemini_api(api_key: str):
    configure(api_key=api_key)
    cache_manager.client = genai.Client(api_key=api_key)

# ============ 新增：檔案過濾功能 ============
def should_skip_file(filename: str) -> bool:
    """判斷是否應該跳過此檔案"""
    # 答案檔案關鍵字
    skip_keywords = ['答案', '解答', '更正答案', 'answer', 'Answer', 'ANSWER']

    # 檢查檔名是否包含跳過關鍵字
    for keyword in skip_keywords:
        if keyword in filename:
            return True
    return False

def is_answer_file(pdf_path: str) -> bool:
    """檢測PDF是否為答案檔案（通過內容分析）"""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            # 只檢查第一頁
            if len(pdf.pages) > 0:
                text = pdf.pages[0].extract_text()
                if text:
                    # 答案檔案的特徵：
                    # 1. 包含大量的 (A) (B) (C) (D) 格式
                    # 2. 行數很少（通常1頁25題）
                    # 3. 沒有長文字段落

                    lines = text.split('\n')
                    short_lines = [l for l in lines if len(l.strip()) < 20]

                    # 如果超過80%的行都很短，很可能是答案卷
                    if len(short_lines) / max(len(lines), 1) > 0.8:
                        # 檢查是否有大量括號選項
                        option_pattern = r'\([A-D]\)'
                        option_count = len(re.findall(option_pattern, text))

                        # 如果有10個以上的選項標記，很可能是答案卷
                        if option_count >= 10:
                            return True
    except:
        pass

    return False
# ============================================

def extract_text_from_pdf(pdf_path: str) -> str:
    try:
        with pdfplumber.open(pdf_path) as pdf:
            text = ""
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        return text
    except:
        return ""

def upload_pdf_to_gemini(pdf_path: str) -> Optional[str]:
    if cache_manager.client is None:
        print("❌ Gemini client 未初始化")
        return None

    try:
        print(f"📤 上傳PDF到Gemini...")

        sample_file = upload_file(pdf_path, mime_type='application/pdf')

        print(f"⏳ 等待處理...")
        max_wait = 60
        wait_time = 0

        while sample_file.state.name == "PROCESSING" and wait_time < max_wait:
            time.sleep(2)
            wait_time += 2
            sample_file = get_file(sample_file.name)

        if sample_file.state.name == "FAILED":
            return None

        print(f"✅ 上傳成功")
        return sample_file.uri
    except Exception as e:
        print(f"❌ 上傳失敗: {e}")
        return None

def parse_with_pdf_upload(pdf_path: str, use_pro: bool = False) -> List[Dict[str, Any]]:
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

        prompt = f"""分析這份PDF考古題，精確提取所有試題：

預期題數：{expected_count}題

如果這是答案卷（只有題號和答案選項），返回 []

否則返回JSON格式：
[{{"題號": "1", "題目": "完整題目內容", "選項A": "...", "選項B": "...", "選項C": "...", "選項D": "...", "題型": "選擇題"}}]

重要規則：
1. 答案卷直接返回 []
2. 題號必須從1開始，連續編號到{expected_count}
3. 題目內容必須完整，至少15字
4. 選擇題必須有A、B、C、D四個選項
5. 總題數必須為{expected_count}題，絕對不能多也不能少
6. 不要將頁首、頁尾、說明、註解誤認為題目
7. 仔細檢查每一題的完整性"""

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
                    '題型': str(q.get('題型', '選擇題'))
                })

        # 如果解析出的題數明顯偏離預期，嘗試修正
        if expected_count and abs(len(validated) - expected_count) > 2:  # 縮小差距閾值
            print(f"⚠️ 解析題數({len(validated)})與預期({expected_count})差距過大，可能有誤")
            # 對於Pro模型，如果差距不大，嘗試智能修正
            if use_pro and abs(len(validated) - expected_count) <= 5:
                if len(validated) > expected_count:
                    validated = validated[:expected_count]
                elif len(validated) < expected_count:
                    # 補充缺失的題號（如果有跳號）
                    existing_nums = sorted([int(q['題號']) for q in validated])
                    missing_nums = []
                    for i in range(1, expected_count + 1):
                        if i not in existing_nums:
                            missing_nums.append(i)
                    print(f"  發現缺失題號: {missing_nums}")

        print(f"✅ 解析成功，找到 {len(validated)} 題")
        return validated
    except Exception as e:
        print(f"❌ 解析失敗: {e}")
        return []

def parse_questions_with_text_gemini(text: str, expected_count: int = 0) -> List[Dict[str, Any]]:
    try:
        # 使用 Gemini 2.5 Flash
        model = GenerativeModel('gemini-2.5-flash')

        prompt = f"""分析以下考古題文字，如果是答案卷返回[]，如果是試題請精確提取所有題目。

預期題數：{expected_count}題

請返回JSON格式：
[{{"題號": "1", "題目": "完整題目內容至少20字", "選項A": "...", "選項B": "...", "選項C": "...", "選項D": "...", "題型": "選擇題"}}]

重要規則：
1. 答案卷直接返回 []
2. 題號必須從1開始連續編號
3. 題目內容必須完整，至少20字
4. 選擇題必須有A、B、C、D四個選項
5. 總題數應為{expected_count}題，勿多勿少
6. 不要將頁首、頁尾、說明文字誤認為題目

文字內容：
{text[:15000]}"""

        response = model.generate_content(prompt)
        text = response.text.strip()

        if text == '[]':
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
                    '題型': str(q.get('題型', '選擇題'))
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

    return result

def process_pdf_to_csv(pdf_path: str, output_dir: str = "") -> Tuple[List[str], ValidationResult]:
    """零誤差處理"""
    print(f"\n{'='*70}")
    print(f"📄 {os.path.basename(pdf_path)}")
    print(f"{'='*70}")

    # ============ 新增：檔案檢查 ============
    filename = os.path.basename(pdf_path)

    # 先通過檔名檢查
    if should_skip_file(filename):
        print(f"⏭️ 跳過答案檔案（檔名判斷）")
        return [], ValidationResult()

    # 再通過內容檢查
    if is_answer_file(pdf_path):
        print(f"⏭️ 跳過答案檔案（內容判斷）")
        return [], ValidationResult()
    # ========================================

    pdf_features = PDFFeatureAnalyzer.analyze_pdf(pdf_path)
    print(f"頁數: {pdf_features['page_count']}, 大小: {pdf_features['file_size_mb']:.2f}MB")
    if pdf_features.get('expected_question_count'):
        print(f"預期題數: {pdf_features['expected_question_count']}")

    # 四次重試：增加Pro模型重試
    strategies = [
        ('text', '文字模式 - Gemini 2.5 Flash'),
        ('pdf', 'PDF上傳 - Gemini 2.5 Flash'),
        ('pdf', 'PDF上傳重試 - Gemini 2.5 Flash'),
        ('pdf_pro', 'PDF上傳 - Gemini 2.5 Pro')
    ]

    best_q = []
    best_v = ValidationResult()

    for i, (stype, sdesc) in enumerate(strategies, 1):
        print(f"\n第{i}/{len(strategies)}次: {sdesc}")

        if stype == 'text':
            text = extract_text_from_pdf(pdf_path)
            expected_count = pdf_features.get('expected_question_count', 0)
            q = parse_questions_with_text_gemini(text, expected_count) if text else []
        elif stype == 'pdf_pro':
            q = parse_with_pdf_upload(pdf_path, use_pro=True)
        else:
            q = parse_with_pdf_upload(pdf_path)

        if not q:
            print("⚠️ 未找到題目")
            continue

        v = validate_questions(q, pdf_features)
        v.print_result()

        if not best_q or v.status == 'success' or len(q) > len(best_q):
            best_q = q
            best_v = v

        if v.status == 'success':
            print("\n✅ 零誤差驗證通過！")
            break

        if i < len(strategies):
            print("⏳ 準備重試...")
            time.sleep(2)

    print(f"\n{'='*70}")
    print("最終結果")
    print(f"{'='*70}")
    if best_v:
        best_v.print_result()

    if best_v and best_v.status == 'error':
        print(f"\n⚠️⚠️⚠️ 需要人工檢查 ⚠️⚠️⚠️")
        print(f"檔案: {pdf_path}")

    if not best_q:
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

    return saved, best_v

def process_directory(input_dir: str, output_dir: str = "") -> Dict[str, Any]:
    pdf_files = glob.glob(os.path.join(input_dir, "**", "*.pdf"), recursive=True)

    if not pdf_files:
        print("未找到PDF")
        return {}

    # ============ 新增：統計過濾資訊 ============
    print(f"\n找到 {len(pdf_files)} 個PDF")

    # 預先過濾答案檔案
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
    # ==========================================

    cache_manager.cleanup_expired_cache()

    results = []
    success = warning = error = 0

    for i, pdf in enumerate(filtered_files, 1):
        try:
            print(f"\n[{i}/{len(filtered_files)}]")

            rel = os.path.relpath(pdf, input_dir)
            out = os.path.join(output_dir, os.path.dirname(rel)) if output_dir else os.path.dirname(pdf)

            _, v = process_pdf_to_csv(pdf, out)

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
            'skipped_files': skipped_files,
            'details': results
        }, f, ensure_ascii=False, indent=2)

    print(f"\n報告: {report}")
    return {'total': len(filtered_files), 'success': success, 'warning': warning, 'error': error}

def main():
    print("PDF轉CSV工具 - 零誤差版 + 答案檔案過濾")
    print("="*70)

    api_key = "AIzaSyDkeFFssyn-Srci1zJPBF8FxXPbILrKj6k"  # 請替換為您的API key
    setup_gemini_api(api_key)

    input_dir = r"考選部考古題完整庫\民國114年"
    output_dir = r"考選部考古題完整庫\民國114年_csv"

    print(f"輸入: {input_dir}")
    print(f"輸出: {output_dir}\n")

    results = process_directory(input_dir, output_dir)

    print(f"\n完成！成功率: {results['success']/(results['total'] or 1)*100:.1f}%")

if __name__ == "__main__":
    main()
