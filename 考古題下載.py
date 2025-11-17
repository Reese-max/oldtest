import os
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from bs4 import BeautifulSoup, Tag
from bs4.element import NavigableString, PageElement
import time
import re
from urllib.parse import urljoin
import html
import json
from datetime import datetime
from typing import List, Dict, Any, Union, Optional, Tuple
import warnings
import urllib3

# 隱藏 urllib3 的 SSL 警告
warnings.filterwarnings('ignore', category=urllib3.exceptions.InsecureRequestWarning)

# 類型註解別名
BeautifulSoupElement = Union[Tag, NavigableString]

# --- 基本設定 ---
BASE_URL = "https://wwwq.moex.gov.tw/exam/"
DEFAULT_SAVE_DIR = "考選部考古題完整庫"
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7',
    'Connection': 'keep-alive'
}

# 動態計算年份範圍（民國年）
def get_available_years():
    """動態計算可用的年份範圍"""
    from datetime import datetime
    current_year = datetime.now().year
    current_minguo_year = current_year - 1911

    # 從民國81年開始到當前年份（包含明年，以防萬一）
    return list(range(81, current_minguo_year + 2))

AVAILABLE_YEARS = get_available_years()
# --- ---

def print_banner():
    """顯示程式標題"""
    print("\n" + "="*70)
    print(" " * 20 + "考選部考古題批量下載工具")
    print("="*70)
    print("📚 資料來源: 考選部考畢試題查詢平臺")
    print(f"🗓️  可用年份: 民國 {AVAILABLE_YEARS[0]} 年 ~ {AVAILABLE_YEARS[-1]} 年")
    print("="*70 + "\n")

def get_save_folder():
    """互動式輸入儲存資料夾"""
    print("【步驟 1/3】設定儲存資料夾")
    print("-" * 70)
    print("💡 輸入方式:")
    print(f"   1. 直接按 Enter → 使用預設資料夾 ({DEFAULT_SAVE_DIR})")
    print("   2. 輸入資料夾名稱 → 在目前目錄建立該資料夾 (例如: 考古題)")
    print("   3. 輸入完整路徑 → 使用絕對路徑 (例如: D:/Downloads/考古題)")
    print("   4. 輸入相對路徑 → 相對於目前目錄 (例如: ../考古題)")
    print("-" * 70)
    
    while True:
        current_dir = os.getcwd()
        print(f"📂 目前工作目錄: {current_dir}")
        user_input = input("💾 請輸入儲存資料夾 (直接按 Enter 使用預設): ").strip()
        
        # 使用預設資料夾
        if not user_input:
            save_dir = DEFAULT_SAVE_DIR
        else:
            save_dir = user_input
        
        # 轉換為絕對路徑
        abs_path = os.path.abspath(save_dir)
        
        # 檢查路徑是否有效
        try:
            # 嘗試建立資料夾（如果不存在）
            os.makedirs(abs_path, exist_ok=True)
            
            # 檢查是否可寫入
            test_file = os.path.join(abs_path, '.test_write')
            with open(test_file, 'w') as f:
                f.write('test')
            os.remove(test_file)
            
            print(f"✅ 已設定儲存位置: {abs_path}\n")
            return abs_path
            
        except PermissionError:
            print(f"❌ 沒有寫入權限: {abs_path}")
            print("   請選擇其他資料夾或以管理員身份執行程式\n")
        except Exception as e:
            print(f"❌ 資料夾設定失敗: {e}")
            print("   請重新輸入\n")

def get_year_input():
    """互動式輸入年份範圍"""
    print("【步驟 2/3】設定下載年份")
    print("-" * 70)
    print("💡 輸入方式:")
    print("   1. 單一年份: 113")
    print("   2. 年份範圍: 110-114")
    print("   3. 多個年份: 110,112,113")
    print("   4. 全部年份: all 或 *")
    print("-" * 70)
    
    while True:
        user_input = input("📅 請輸入年份 (民國年): ").strip()
        
        if not user_input:
            print("❌ 輸入不可為空，請重新輸入\n")
            continue
        
        try:
            # 全部年份
            if user_input.lower() in ['all', '*', '全部']:
                return AVAILABLE_YEARS
            
            # 年份範圍
            elif '-' in user_input:
                parts = user_input.split('-')
                if len(parts) != 2:
                    raise ValueError
                start = int(parts[0].strip())
                end = int(parts[1].strip())

                # 動態檢查年份範圍
                max_year = AVAILABLE_YEARS[-1] if AVAILABLE_YEARS else 114
                if not (AVAILABLE_YEARS[0] <= start <= max_year and AVAILABLE_YEARS[0] <= end <= max_year and start <= end):
                    print(f"❌ 年份範圍必須在 {AVAILABLE_YEARS[0]}-{max_year} 之間，且起始年份不可大於結束年份\n")
                    continue

                years = list(range(start, end + 1))
                print(f"✅ 已選擇: 民國 {start} 年 ~ {end} 年 (共 {len(years)} 年)\n")
                return years
            
            # 多個年份
            elif ',' in user_input:
                years = [int(y.strip()) for y in user_input.split(',')]

                # 動態檢查年份範圍
                max_year = AVAILABLE_YEARS[-1] if AVAILABLE_YEARS else 114
                if not all(AVAILABLE_YEARS[0] <= y <= max_year for y in years):
                    print(f"❌ 所有年份必須在 {AVAILABLE_YEARS[0]}-{max_year} 之間\n")
                    continue

                years = sorted(list(set(years)))
                print(f"✅ 已選擇: {len(years)} 個年份: {', '.join(map(str, years))}\n")
                return years

            # 單一年份
            else:
                year = int(user_input)
                max_year = AVAILABLE_YEARS[-1] if AVAILABLE_YEARS else 114
                if not (AVAILABLE_YEARS[0] <= year <= max_year):
                    print(f"❌ 年份必須在 {AVAILABLE_YEARS[0]}-{max_year} 之間\n")
                    continue

                print(f"✅ 已選擇: 民國 {year} 年\n")
                return [year]
        
        except ValueError:
            print("❌ 輸入格式錯誤，請重新輸入\n")
            continue

def get_filter_input():
    """互動式輸入考試類型篩選"""
    print("【步驟 3/3】設定考試類型篩選")
    print("-" * 70)
    print("💡 預設考試類型:")
    print("   1. 警察人員考試（內軌）")
    print("   2. 一般警察人員考試（外軌）")
    print("   3. 司法人員考試（監獄官、觀護人）")
    print("   4. 國家安全情報人員考試")
    print("   5. 移民行政人員考試")
    print("-" * 70)

    # 返回考試級別的關鍵字
    target_keywords = [
        "警察人員考試",
        "一般警察人員考試",
        "司法人員考試",
        "國家安全情報人員考試",
        "移民行政人員考試"
    ]

    print("✅ 已自動設定: 警察與司法相關考試篩選\n")
    return target_keywords

def confirm_settings(save_dir, years, keywords):
    """確認設定"""
    print("="*70)
    print("📋 目前設定")
    print("="*70)
    
    # 顯示儲存位置
    print(f"💾 儲存位置: {save_dir}")
    
    # 顯示年份
    if len(years) == 1:
        print(f"📅 下載年份: 民國 {years[0]} 年")
    elif len(years) <= 5:
        print(f"📅 下載年份: 民國 {', '.join(map(str, years))} 年")
    else:
        print(f"📅 下載年份: 民國 {years[0]} ~ {years[-1]} 年 (共 {len(years)} 年)")
    
    # 顯示篩選
    if keywords:
        print(f"🔍 考試篩選: {', '.join(keywords)}")
    else:
        print(f"🔍 考試篩選: 全部考試")
    
    # 顯示磁碟空間
    try:
        if os.name == 'nt':  # Windows
            import shutil
            total, used, free = shutil.disk_usage(save_dir)
            print(f"💿 可用空間: {free / (1024**3):.2f} GB")
    except (ImportError, OSError, AttributeError):
        # 忽略磁碟空間檢查失敗（非關鍵功能）
        pass
    
    print("="*70)
    
    while True:
        confirm = input("\n確認開始下載? (Y/N): ").strip().upper()
        if confirm == 'Y':
            return True
        elif confirm == 'N':
            return False
        else:
            print("❌ 請輸入 Y 或 N")

def create_robust_session():
    """創建增強型Session - 提升成功率至95-99%"""
    session = requests.Session()

    # 配置重試策略
    retry_strategy = Retry(
        total=10,  # 總共10次重試（原5次）
        backoff_factor=1,  # 指數退避因子：1s, 2s, 4s, 8s...
        status_forcelist=[429, 500, 502, 503, 504],  # 需要重試的HTTP狀態碼
        allowed_methods=["GET", "POST"],  # 允許重試的方法
        raise_on_status=False  # 不在重試時拋出異常
    )

    # 配置HTTP適配器
    adapter = HTTPAdapter(
        max_retries=retry_strategy,
        pool_connections=10,  # 連接池大小
        pool_maxsize=20,      # 最大連接數
        pool_block=False      # 非阻塞模式
    )

    session.mount("http://", adapter)
    session.mount("https://", adapter)
    session.headers.update(HEADERS)

    return session

def verify_pdf_file(file_path: str) -> Tuple[bool, Any]:
    """
    驗證PDF文件完整性

    Returns:
        (是否有效, 文件大小或錯誤訊息)
    """
    try:
        # 檢查文件大小
        file_size = os.path.getsize(file_path)
        if file_size < 1024:
            return False, "文件過小"

        # 檢查PDF文件頭（%PDF-）
        with open(file_path, 'rb') as f:
            header = f.read(5)
            if not header.startswith(b'%PDF-'):
                return False, "非PDF文件"

        # 嘗試用pdfplumber打開驗證（如果可用）
        try:
            import pdfplumber
            with pdfplumber.open(file_path) as pdf:
                # 檢查是否至少有一頁
                if len(pdf.pages) == 0:
                    return False, "PDF無內容"
        except ImportError:
            # 如果沒有pdfplumber，跳過深度驗證
            pass
        except Exception as e:
            return False, f"PDF損壞: {str(e)[:30]}"

        return True, file_size

    except Exception as e:
        return False, f"驗證失敗: {str(e)[:30]}"

def sanitize_filename(name):
    """清理檔名中的非法字元"""
    name = html.unescape(name)
    name = re.sub(r'[\\/*?:"<>|]', "", name)
    if len(name) > 150:
        name = name[:150]
    return name.strip()

def get_exam_list_by_year(session, year, keywords):
    """獲取指定年份的考試列表"""
    try:
        url = f"{BASE_URL}wFrmExamQandASearch.aspx?y={year + 1911}"
        response = session.get(url, timeout=30, verify=False)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        exam_select = soup.find("select", id=re.compile(r'ddlExamCode'))
        if not exam_select:
            return []
        
        exams = []
        for option in exam_select.find_all("option"):  # type: ignore
            if isinstance(option, Tag) and option.has_attr('value') and option['value']:
                exam_code = option['value']
                exam_name = option.get_text(strip=True)
                
                if keywords:
                    # 使用考試級別的關鍵字篩選
                    if any(keyword in exam_name for keyword in keywords):
                        exams.append({
                            'code': exam_code,
                            'name': exam_name,
                            'year': year
                        })
                        print(f"   ✅ 找到考試: {exam_name}")
                else:
                    exams.append({
                        'code': exam_code,
                        'name': exam_name,
                        'year': year
                    })
        
        return exams
    except Exception as e:
        print(f"   ❌ 獲取 {year} 年考試列表失敗: {e}")
        return []

def parse_exam_page(html_content, exam_name=""):
    """
    解析考試頁面，基於科目特徵識別類科
    適用年份：90-114年
    目標類科：警察人員三等14類 + 司法三等2類（監獄官）
    """
    from bs4 import BeautifulSoup, Tag
    import re
    import html as html_module
    from collections import defaultdict

    soup = BeautifulSoup(html_content, 'html.parser')

    # 步驟1：收集所有類科代碼的科目和下載連結
    raw_structure = defaultdict(lambda: defaultdict(dict))

    links = soup.find_all('a', href=re.compile(r'wHandExamQandA_File\.ashx'))

    for link in links:
        if not isinstance(link, Tag):
            continue

        href = link.get('href', '')
        if not href:
            continue

        # 解析URL參數
        href_str = str(href)
        code_match = re.search(r'[&?]c=(\d+)', href_str)
        type_match = re.search(r'[&?]t=([QSMR])', href_str)

        if not code_match:
            continue

        category_code = code_match.group(1)
        file_type_code = type_match.group(1) if type_match else 'Q'
        file_type = {
            'Q': '試題',
            'S': '答案',
            'M': '更正答案',
            'R': '參考答案'
        }.get(file_type_code, '試題')

        # 找科目名稱
        tr = link.find_parent('tr')
        if not tr or not isinstance(tr, Tag):
            continue

        label = tr.find('label', {'class': 'exam-title'})
        if not label:
            label = tr.find('label')
        if not label or not isinstance(label, Tag):
            continue

        subject_name = label.get_text(strip=True)
        if not subject_name or subject_name in ['試題', '答案', '更正答案', '參考答案']:
            continue

        # 儲存資料 - 確保所有必要的鍵都存在
        subject_dict = raw_structure[category_code][subject_name]
        if 'subject' not in subject_dict:
            subject_dict['subject'] = sanitize_filename(subject_name)
        if 'original_name' not in subject_dict:
            subject_dict['original_name'] = subject_name
        if 'downloads' not in subject_dict:
            subject_dict['downloads'] = []

        subject_dict['downloads'].append({
            'type': file_type,
            'url': html_module.unescape(str(href))
        })

    # 步驟2：根據科目特徵識別類科
    def identify_category(subjects_list):
        """
        根據111年實際科目名稱識別類科
        每個類科都有1-3個獨特科目可以識別
        """
        if not subjects_list:
            return None

        # 建立科目集合（用於快速查找）
        subjects_text = '|||'.join(subjects_list)

        # === 內軌判定：必須有這三種英文科目之一 ===
        is_internal = (
            '中華民國憲法與警察專業英文' in subjects_text or
            '中華民國憲法與消防警察專業英文' in subjects_text or
            '中華民國憲法與水上警察專業英文' in subjects_text
        )

        if not is_internal:
            # 檢查司法特考 - 三等監獄官的完整科目列表
            judicial_subjects = [
                '國文(作文、公文與測驗)',
                '法學知識與英文(包括中華民國憲法、法學緒論、英文)',
                '刑法與少年事件處理法',
                '刑事政策',
                '犯罪學與再犯預測',
                '監獄行刑法與羈押法',
                '監獄學',
                '諮商與矯正輔導'
            ]

            # 排除四等監所管理員的概要科目
            exclude_subjects = [
                '犯罪學概要',
                '刑法概要',
                '監獄行刑法概要',
                '監獄學概要'
            ]

            # 檢查是否包含排除科目（如果是概要科目，則不屬於三等監獄官）
            has_exclude_subjects = any(subject in subjects_text for subject in exclude_subjects)

            if has_exclude_subjects:
                return None

            # 檢查是否包含足夠的三等監獄官科目（至少4個主要科目）
            judicial_matches = sum(1 for subject in judicial_subjects if subject in subjects_text)
            if judicial_matches >= 4:
                # 根據考試名稱判斷是男還是女
                if exam_name and ('(男)' in exam_name or '男' in exam_name):
                    return '司法三等考試_監獄官(男)'
                elif exam_name and ('(女)' in exam_name or '女' in exam_name):
                    return '司法三等考試_監獄官(女)'
                else:
                    return '司法三等考試_監獄官'
            return None

        # === 以下為內軌14個類科 ===

        # 1. 行政警察人員：警察學與警察勤務 + 警察政策與犯罪預防
        if '警察學與警察勤務' in subjects_text:
            return '警察人員考試三等考試_行政警察人員'

        # 2. 外事警察人員：外事警察學
        if '外事警察學' in subjects_text:
            return '警察人員考試三等考試_外事警察人員'

        # 3. 刑事警察人員：犯罪偵查學 + 刑案現場處理
        if '犯罪偵查學' in subjects_text and '刑案現場處理' in subjects_text:
            return '警察人員考試三等考試_刑事警察人員'

        # 4. 公共安全人員：情報學 + 國家安全情報法制
        if '情報學' in subjects_text and '國家安全情報法制' in subjects_text:
            return '警察人員考試三等考試_公共安全人員'

        # 5. 犯罪防治人員預防組：諮商輔導與婦幼保護 + 犯罪分析
        if '諮商輔導與婦幼保護' in subjects_text and '犯罪分析' in subjects_text:
            return '警察人員考試三等考試_犯罪防治人員預防組'

        # 6. 消防警察人員：火災學與消防化學 + 消防安全設備
        if '火災學與消防化學' in subjects_text and '消防安全設備' in subjects_text:
            return '警察人員考試三等考試_消防警察人員'

        # 7. 交通警察人員交通組：交通警察學 + 交通統計與分析
        if '交通警察學' in subjects_text and '交通統計與分析' in subjects_text:
            return '警察人員考試三等考試_交通警察人員交通組'

        # 8. 交通警察人員電訊組：通訊犯罪偵查 + 通訊系統 + 電路學
        # 放寬條件：只要有通訊相關科目即可識別
        if ('通訊犯罪偵查' in subjects_text or '通訊系統' in subjects_text or '電路學' in subjects_text) and '交通警察學' not in subjects_text:
            return '警察人員考試三等考試_交通警察人員電訊組'

        # 9. 警察資訊管理人員：電腦犯罪偵查 + 數位鑑識執法 + 警政資訊管理與應用
        if '電腦犯罪偵查' in subjects_text and '數位鑑識執法' in subjects_text:
            return '警察人員考試三等考試_警察資訊管理人員'

        # 10. 刑事鑑識人員：物理鑑識 + 刑事化學 + 刑事生物
        if '物理鑑識' in subjects_text and '刑事化學' in subjects_text and '刑事生物' in subjects_text:
            return '警察人員考試三等考試_刑事鑑識人員'

        # 11. 國境警察人員：移民情勢與政策分析 + 國境執法
        if '移民情勢與政策分析' in subjects_text and '國境執法' in subjects_text:
            return '警察人員考試三等考試_國境警察人員'

        # 12. 水上警察人員：水上警察學 + 海上犯罪偵查法學 + 國際海洋法
        if '水上警察學' in subjects_text and '海上犯罪偵查法學' in subjects_text:
            return '警察人員考試三等考試_水上警察人員'

        # 13. 警察法制人員：警察法制作業 + 行政法與警察行政違規調查裁處作業
        if '警察法制作業' in subjects_text and '行政法與警察行政違規調查裁處作業' in subjects_text:
            return '警察人員考試三等考試_警察法制人員'

        # 14. 行政管理人員：警察人事行政與法制 + 警察組織與事務管理
        if '警察人事行政與法制' in subjects_text and '警察組織與事務管理' in subjects_text:
            return '警察人員考試三等考試_行政管理人員'

        return None

    # 步驟3：整理成最終結構
    exam_structure = {}

    for category_code, subjects_dict in raw_structure.items():
        subjects_list = list(subjects_dict.keys())
        category_name = identify_category(subjects_list)

        if not category_name:
            continue

        if category_name not in exam_structure:
            exam_structure[category_name] = []

        for subject_name, subject_info in subjects_dict.items():
            exam_structure[category_name].append({
                'subject': subject_info['subject'],
                'original_name': subject_info['original_name'],
                'downloads': subject_info['downloads']
            })

    # 調試輸出
    print(f"   🔍 調試: 解析出 {len(exam_structure)} 個目標類科")
    for cat_name, subjects in exam_structure.items():
        print(f"   🔍 調試:   {cat_name}: {len(subjects)} 個科目")
    
    # 顯示未識別的類科
    unidentified_categories = []
    for category_code, subjects_dict in raw_structure.items():
        subjects_list = list(subjects_dict.keys())
        category_name = identify_category(subjects_list)
        if not category_name:
            unidentified_categories.append((category_code, subjects_list))
    
    if unidentified_categories:
        print(f"   ⚠️  未識別的類科 ({len(unidentified_categories)} 個):")
        for code, subjects in unidentified_categories[:3]:  # 只顯示前3個
            print(f"   ⚠️     代碼 {code}: {', '.join(subjects[:5])}{'...' if len(subjects) > 5 else ''}")

    return exam_structure

def download_file(session, url, file_path, max_retries=10):
    """
    增強型文件下載 - 支援更多異常處理和PDF驗證

    Args:
        session: requests.Session實例
        url: 下載URL
        file_path: 儲存路徑
        max_retries: 最大重試次數（默認10次）

    Returns:
        (成功, 文件大小或錯誤訊息)
    """
    for attempt in range(max_retries):
        try:
            # 分別設置連接超時和讀取超時
            # (連接超時, 讀取超時)
            timeout = (10, 120)  # 10秒建立連接，120秒讀取數據

            response = session.get(
                url,
                headers=HEADERS,
                stream=True,
                timeout=timeout,
                verify=False
            )
            response.raise_for_status()

            content_type = response.headers.get('Content-Type', '')
            if 'pdf' not in content_type.lower() and 'application/octet-stream' not in content_type.lower():
                return False, "非PDF檔案"

            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)

            # 驗證PDF文件完整性
            valid, result = verify_pdf_file(file_path)
            if valid:
                return True, result
            else:
                # 文件無效，刪除並重試
                try:
                    os.remove(file_path)
                except Exception:
                    pass
                if attempt == max_retries - 1:
                    return False, result
                time.sleep(2 ** attempt)
                continue

        except requests.exceptions.Timeout:
            if attempt == max_retries - 1:
                return False, "請求超時"
            time.sleep(2 ** attempt)
            continue

        except requests.exceptions.HTTPError as e:
            # HTTP狀態錯誤
            if e.response and e.response.status_code in [404, 403, 401]:
                # 這些錯誤不需要重試
                return False, f"HTTP {e.response.status_code}"
            if attempt == max_retries - 1:
                return False, f"HTTP錯誤"
            time.sleep(2 ** attempt)
            continue

        except requests.exceptions.ConnectionError:
            if attempt == max_retries - 1:
                return False, "連線錯誤"
            time.sleep(2 ** attempt)
            continue

        except requests.exceptions.ChunkedEncodingError:
            # 分塊編碼錯誤，通常是傳輸中斷
            if attempt == max_retries - 1:
                return False, "傳輸中斷"
            time.sleep(2 ** attempt)
            continue

        except requests.exceptions.ContentDecodingError:
            # 內容解碼錯誤
            if attempt == max_retries - 1:
                return False, "內容解碼失敗"
            time.sleep(2 ** attempt)
            continue

        except (OSError, IOError) as e:
            # 文件系統錯誤
            error_msg = str(e).lower()
            if "disk" in error_msg or "space" in error_msg:
                return False, "磁碟空間不足"
            if attempt == max_retries - 1:
                return False, f"文件錯誤: {str(e)[:30]}"
            time.sleep(2 ** attempt)
            continue

        except Exception as e:
            if attempt == max_retries - 1:
                return False, f"未知錯誤: {str(e)[:30]}"
            time.sleep(2 ** attempt)
            continue

    return False, "超過最大重試次數"

def download_exam(session, exam_info, base_folder, stats):
    """下載單一考試"""
    year = exam_info['year']
    exam_code = exam_info['code']
    exam_name = exam_info['name']
    
    print(f"\n{'='*70}")
    print(f"📋 民國 {year} 年 - {exam_name}")
    print(f"{'='*70}")
    
    try:
        url = f"{BASE_URL}wFrmExamQandASearch.aspx?y={year + 1911}&e={exam_code}"
        response = session.get(url, timeout=30, verify=False)
        response.raise_for_status()
        
        # 定義類科關鍵字（用於第二層篩選）
        category_keywords = [
            # 警察人員考試三等考試類別
            "警察人員考試三等考試_行政警察人員類別",
            "警察人員考試三等考試_外事警察人員(選試英語)類別",
            "警察人員考試三等考試_刑事警察人員類別",
            "警察人員考試三等考試_公共安全人員類別",
            "警察人員考試三等考試_犯罪防治人員類別預防組",
            "警察人員考試三等考試_消防警察人員類別",
            "警察人員考試三等考試_交通警察人員類別交通組",
            "警察人員考試三等考試_警察資訊管理人員類別",
            "警察人員考試三等考試_刑事鑑識人員類別",
            "警察人員考試三等考試_國境警察人員類別",
            "警察人員考試三等考試_水上警察人員類別",
            "警察人員考試三等考試_警察法制人員類別",
            "警察人員考試三等考試_交通警察人員電訊組",
            "警察人員考試三等考試_行政管理人員類別",

            # 司法考試類別
            "司法三等考試_監獄官(男)",
            "司法三等考試_監獄官(女)",
        ]

        exam_structure = parse_exam_page(response.text, exam_name)
        
        if not exam_structure:
            print("   ⚠️ 此考試沒有可下載的試題")
            stats['empty_exams'] += 1
            return
        
        # 縮短考試資料夾名稱以避免路徑過長
        if "警察人員考試、一般警察人員考試" in exam_name:
            short_exam_name = f"民國{year}年_警察特考"
        elif "司法人員考試" in exam_name:
            short_exam_name = f"民國{year}年_司法特考"
        else:
            # 對於其他考試，使用前50個字符
            short_exam_name = sanitize_filename(f"民國{year}年_{exam_name[:50]}")

        exam_folder = os.path.join(base_folder, f"民國{year}年", short_exam_name)
        os.makedirs(exam_folder, exist_ok=True)
        
        total_subjects = sum(len(subjects) for subjects in exam_structure.values())
        total_files = sum(
            len(subject['downloads']) 
            for subjects in exam_structure.values() 
            for subject in subjects
        )
        
        print(f"   📊 類科: {len(exam_structure)} 個 | 科目: {total_subjects} 個 | 檔案: {total_files} 個")
        print(f"   🔍 調試: 詳細類科資訊")
        for cat_name, subjects in exam_structure.items():
            cat_files = sum(len(subject['downloads']) for subject in subjects)
            print(f"   🔍     {cat_name}: {len(subjects)} 科目, {cat_files} 檔案")
        
        file_count = 0
        for category_name, subjects in exam_structure.items():
            # 縮短類科資料夾名稱
            if '行政警察人員' in category_name:
                short_category_name = '行政警察'
            elif '外事警察人員' in category_name:
                short_category_name = '外事警察'
            elif '刑事警察人員' in category_name:
                short_category_name = '刑事警察'
            elif '公共安全人員' in category_name:
                short_category_name = '公共安全'
            elif '犯罪防治人員' in category_name:
                short_category_name = '犯罪防治'
            elif '消防警察人員' in category_name:
                short_category_name = '消防警察'
            elif '交通警察人員交通組' in category_name:
                short_category_name = '交通警察_交通'
            elif '交通警察人員電訊組' in category_name:
                short_category_name = '交通警察_電訊'
            elif '警察資訊管理人員' in category_name:
                short_category_name = '資訊管理'
            elif '刑事鑑識人員' in category_name:
                short_category_name = '刑事鑑識'
            elif '國境警察人員' in category_name:
                short_category_name = '國境警察'
            elif '水上警察人員' in category_name:
                short_category_name = '水上警察'
            elif '警察法制人員' in category_name:
                short_category_name = '警察法制'
            elif '行政管理人員' in category_name:
                short_category_name = '行政管理'
            elif '監獄官' in category_name:
                short_category_name = '監獄官'
            else:
                # 對於其他類科，使用後面的部分
                short_category_name = category_name.split('_')[-1] if '_' in category_name else category_name[:20]

            category_folder = os.path.join(exam_folder, short_category_name)
            os.makedirs(category_folder, exist_ok=True)
            
            for subject_info in subjects:
                subject_name = subject_info['subject']
                
                # 為每個科目建立專用資料夾
                subject_folder = os.path.join(category_folder, subject_name)
                os.makedirs(subject_folder, exist_ok=True)
                
                for download_info in subject_info['downloads']:
                    file_type = download_info['type']
                    url = download_info['url']
                    
                    # 根據檔案類型進行更清晰的命名
                    file_type_mapping = {
                        "試題": "試題",
                        "答案": "答案",
                        "更正答案": "更正答案",
                        "題目": "試題",
                        "解答": "答案",
                        "勘誤": "更正答案"
                    }
                    
                    # 使用映射表來標準化檔案類型命名
                    normalized_type = file_type_mapping.get(file_type, file_type)
                    
                    # 建立包含年度和科目名的檔案名稱
                    file_name = f"民國{year}年_{subject_name}_{normalized_type}.pdf"
                    
                    file_path = os.path.join(subject_folder, file_name)

                    # 移除檔案存在檢查，總是嘗試下載以確保完整性
                    
                    pdf_url = urljoin(BASE_URL, url)
                    success, result = download_file(session, pdf_url, file_path)
                    
                    file_count += 1
                    if file_count % 10 == 0:
                        print(f"   ⬇️  進度: {file_count}/{total_files}", end='\r')
                    
                    if success:
                        stats['success'] += 1
                        stats['total_size'] += result
                        # 對於成功下載的檔案，等待短時間避免過於頻繁的請求
                        time.sleep(0.5)
                    else:
                        stats['failed'] += 1
                        stats['failed_list'].append({
                            'year': year,
                            'exam': exam_name,
                            'category': category_name,
                            'subject': subject_info['original_name'],
                            'type': file_type,
                            'reason': result,
                            'url': pdf_url,
                            'file_path': file_path,
                            'timestamp': datetime.now().isoformat()
                        })
                        # 對於失敗的檔案，等待更長時間再繼續
                        time.sleep(2)
        
        print(f"   ✅ 完成: {file_count}/{total_files} 個檔案")
        stats['completed_exams'] += 1
        
    except Exception as e:
        print(f"   ❌ 處理失敗: {e}")
        stats['failed_exams'] += 1

def retry_failed_downloads(session, failed_list, base_folder):
    """
    重試失敗的下載（第二輪）

    Args:
        session: requests.Session實例
        failed_list: 失敗項目列表
        base_folder: 基礎資料夾

    Returns:
        重試統計結果
    """
    print("\n" + "="*70)
    print("🔄 開始重試失敗的下載（第二輪 - 15次重試）")
    print("="*70)

    retry_stats = {
        'success': 0,
        'still_failed': 0,
        'still_failed_list': []
    }

    total = len(failed_list)
    for idx, item in enumerate(failed_list, 1):
        print(f"\n🔄 [{idx}/{total}] 重試: {item['subject']} - {item['type']}")
        print(f"   📁 {item['file_path']}")

        # 第二輪使用更長的等待時間
        time.sleep(3)

        success, result = download_file(
            session,
            item['url'],
            item['file_path'],
            max_retries=15  # 第二輪使用更多重試次數
        )

        if success:
            retry_stats['success'] += 1
            print(f"   ✅ 重試成功！大小: {result/1024:.1f}KB")
        else:
            retry_stats['still_failed'] += 1
            retry_stats['still_failed_list'].append(item)
            print(f"   ❌ 仍然失敗: {result}")

        # 顯示進度
        success_rate = (retry_stats['success'] / idx) * 100
        print(f"   📊 當前重試成功率: {success_rate:.1f}% ({retry_stats['success']}/{idx})")

    return retry_stats

def main():
    # 顯示歡迎畫面
    print_banner()
    
    # 自動設定民國114年
    save_dir = "114年考古題_調試版"
    years = [114]
    keywords = [
        "警察人員考試",
        "一般警察人員考試",
        "司法人員考試",
        "國家安全情報人員考試",
        "移民行政人員考試"
    ]
    
    print(f"✅ 自動設定: 民國114年考古題下載")
    print(f"📁 儲存位置: {os.path.abspath(save_dir)}")
    print(f"🔍 考試篩選: 警察與司法相關考試")
    print("="*70)
    
    # 建立儲存資料夾
    os.makedirs(save_dir, exist_ok=True)
    
    # 開始下載
    stats = {
        'success': 0,
        'failed': 0,
        'skipped': 0,
        'total_size': 0,
        'completed_exams': 0,
        'failed_exams': 0,
        'empty_exams': 0,
        'failed_list': []
    }
    
    # 使用增強型Session
    session = create_robust_session()

    start_time = datetime.now()

    try:
        print("\n" + "="*70)
        print("🚀 開始下載（增強模式：10次重試 + PDF驗證）")
        print("="*70)
        
        for year in years:
            print(f"\n🔍 正在掃描民國 {year} 年的考試...")
            
            exams = get_exam_list_by_year(session, year, keywords)
            
            if not exams:
                print(f"   ⚠️ 民國 {year} 年沒有找到符合條件的考試")
                continue
            
            print(f"   ✅ 找到 {len(exams)} 個考試")
            
            for exam in exams:
                download_exam(session, exam, save_dir, stats)
                time.sleep(0.5)
        
        elapsed_time = datetime.now() - start_time

        # 產生第一輪報告
        print("\n" + "="*70)
        print("📊 第一輪下載完成統計")
        print("="*70)
        print(f"⏱️  總耗時: {elapsed_time}")
        print(f"✅ 成功下載: {stats['success']} 個檔案")
        print(f"⏭️  已跳過: {stats['skipped']} 個檔案")
        print(f"❌ 失敗: {stats['failed']} 個檔案")
        print(f"📦 總大小: {stats['total_size'] / (1024*1024):.2f} MB")

        if stats['failed'] > 0:
            first_round_success_rate = (stats['success'] / (stats['success'] + stats['failed'])) * 100
            print(f"📈 第一輪成功率: {first_round_success_rate:.1f}%")

        # 第二輪：重試失敗的下載
        if stats['failed_list']:
            print(f"\n⚠️  第一輪有 {len(stats['failed_list'])} 個失敗，啟動第二輪重試...")

            retry_stats = retry_failed_downloads(session, stats['failed_list'], save_dir)

            # 更新統計
            stats['success'] += retry_stats['success']
            stats['failed'] = retry_stats['still_failed']
            stats['failed_list'] = retry_stats['still_failed_list']

            print(f"\n📊 第二輪重試結果:")
            print(f"   ✅ 重試成功: {retry_stats['success']} 個")
            print(f"   ❌ 仍然失敗: {retry_stats['still_failed']} 個")

        # 最終統計
        elapsed_time = datetime.now() - start_time
        print("\n" + "="*70)
        print("📊 最終完整統計")
        print("="*70)
        print(f"⏱️  總耗時: {elapsed_time}")
        print(f"✅ 成功下載: {stats['success']} 個檔案")
        print(f"⏭️  已跳過: {stats['skipped']} 個檔案")
        print(f"❌ 最終失敗: {stats['failed']} 個檔案")
        print(f"📦 總大小: {stats['total_size'] / (1024*1024):.2f} MB")

        # 計算最終成功率
        if stats['success'] + stats['failed'] > 0:
            final_success_rate = (stats['success'] / (stats['success'] + stats['failed'])) * 100
            print(f"📈 最終成功率: {final_success_rate:.1f}%")

            if final_success_rate >= 99:
                print("🏆 優秀！成功率達到99%以上")
            elif final_success_rate >= 95:
                print("✨ 良好！成功率達到95%以上")
            elif final_success_rate >= 90:
                print("👍 不錯！成功率達到90%以上")
        print("="*70)
        
        # 儲存失敗清單
        if stats['failed_list']:
            log_file = os.path.join(save_dir, '下載失敗清單.json')
            with open(log_file, 'w', encoding='utf-8') as f:
                json.dump(stats['failed_list'], f, ensure_ascii=False, indent=2)
            
            txt_file = os.path.join(save_dir, '下載失敗清單.txt')
            with open(txt_file, 'w', encoding='utf-8') as f:
                f.write(f"下載失敗清單 (共 {len(stats['failed_list'])} 個)\n")
                f.write("="*70 + "\n\n")
                for idx, item in enumerate(stats['failed_list'], 1):
                    f.write(f"{idx}. 民國 {item['year']} 年 - {item['exam']}\n")
                    f.write(f"   類科: {item['category']}\n")
                    f.write(f"   科目: {item['subject']}\n")
                    f.write(f"   類型: {item['type']}\n")
                    f.write(f"   原因: {item['reason']}\n")
                    f.write("-"*70 + "\n\n")
            
            print(f"\n⚠️  失敗清單已儲存至: {txt_file}")
        
        print(f"\n🎉 所有作業完成！檔案位於: {save_dir}")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  使用者中斷下載")
        print(f"已下載: {stats['success']} 個檔案")
    except Exception as e:
        print(f"\n❌ 發生嚴重錯誤: {e}")
        import traceback
        traceback.print_exc()
    finally:
        session.close()

if __name__ == "__main__":
    main()
