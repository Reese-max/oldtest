#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
簡化版考古題下載工具
專門下載指定的16個學系
"""

import os
import requests
from bs4 import BeautifulSoup
import time
import re
from urllib.parse import urljoin
import html
import json
from datetime import datetime
from typing import List, Dict, Any
import warnings
import urllib3

# 隱藏 urllib3 的 SSL 警告
warnings.filterwarnings('ignore', category=urllib3.exceptions.InsecureRequestWarning)

# 基本設定
BASE_URL = "https://wwwq.moex.gov.tw/exam/"
SAVE_DIR = "考選部考古題完整庫"
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7',
    'Connection': 'keep-alive'
}

def sanitize_filename(name):
    """清理檔名中的非法字元"""
    name = html.unescape(name)
    name = re.sub(r'[\\/*?:"<>|]', "", name)
    if len(name) > 150:
        name = name[:150]
    return name.strip()

def get_exam_list_by_year(session, year):
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
        for option in exam_select.find_all("option"):
            if option.has_attr('value') and option['value']:
                exam_code = option['value']
                exam_name = option.get_text(strip=True)
                
                # 只下載警察和司法相關考試
                if any(keyword in exam_name for keyword in ["警察人員考試", "司法人員考試"]):
                    exams.append({
                        'code': exam_code,
                        'name': exam_name,
                        'year': year
                    })
                    print(f"   ✅ 找到考試: {exam_name}")
        
        return exams
    except Exception as e:
        print(f"   ❌ 獲取 {year} 年考試列表失敗: {e}")
        return []

def parse_exam_page(html_content, exam_name=""):
    """解析考試頁面，識別目標學系"""
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # 收集所有類科代碼的科目和下載連結
    raw_structure = {}
    
    links = soup.find_all('a', href=re.compile(r'wHandExamQandA_File\.ashx'))
    
    for link in links:
        href = link.get('href', '')
        if not href:
            continue

        # 解析URL參數
        code_match = re.search(r'[&?]c=(\d+)', href)
        type_match = re.search(r'[&?]t=([QSMR])', href)

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
        if not tr:
            continue

        label = tr.find('label', {'class': 'exam-title'})
        if not label:
            label = tr.find('label')
        if not label:
            continue

        subject_name = label.get_text(strip=True)
        if not subject_name or subject_name in ['試題', '答案', '更正答案', '參考答案']:
            continue

        # 儲存資料
        if category_code not in raw_structure:
            raw_structure[category_code] = {}
        if subject_name not in raw_structure[category_code]:
            raw_structure[category_code][subject_name] = {
                'subject': sanitize_filename(subject_name),
                'original_name': subject_name,
                'downloads': []
            }

        raw_structure[category_code][subject_name]['downloads'].append({
            'type': file_type,
            'url': html.unescape(str(href))
        })

    # 根據科目特徵識別類科
    def identify_category(subjects_list):
        if not subjects_list:
            return None

        subjects_text = '|||'.join(subjects_list)

        # 檢查是否為內軌（必須有英文科目）
        is_internal = (
            '中華民國憲法與警察專業英文' in subjects_text or
            '中華民國憲法與消防警察專業英文' in subjects_text or
            '中華民國憲法與水上警察專業英文' in subjects_text
        )

        if not is_internal:
            # 檢查司法特考
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

            exclude_subjects = [
                '犯罪學概要',
                '刑法概要',
                '監獄行刑法概要',
                '監獄學概要'
            ]

            has_exclude_subjects = any(subject in subjects_text for subject in exclude_subjects)
            if has_exclude_subjects:
                return None

            judicial_matches = sum(1 for subject in judicial_subjects if subject in subjects_text)
            if judicial_matches >= 4:
                if exam_name and ('(男)' in exam_name or '男' in exam_name):
                    return '司法三等考試_監獄官(男)'
                elif exam_name and ('(女)' in exam_name or '女' in exam_name):
                    return '司法三等考試_監獄官(女)'
                else:
                    return '司法三等考試_監獄官'
            return None

        # 內軌14個類科識別
        if '警察學與警察勤務' in subjects_text:
            return '警察人員考試三等考試_行政警察人員類別'
        if '外事警察學' in subjects_text:
            return '警察人員考試三等考試_外事警察人員(選試英語)類別'
        if '犯罪偵查學' in subjects_text and '刑案現場處理' in subjects_text:
            return '警察人員考試三等考試_刑事警察人員類別'
        if '情報學' in subjects_text and '國家安全情報法制' in subjects_text:
            return '警察人員考試三等考試_公共安全人員類別'
        if '諮商輔導與婦幼保護' in subjects_text and '犯罪分析' in subjects_text:
            return '警察人員考試三等考試_犯罪防治人員類別預防組'
        if '火災學與消防化學' in subjects_text and '消防安全設備' in subjects_text:
            return '警察人員考試三等考試_消防警察人員類別'
        if '交通警察學' in subjects_text and '交通統計與分析' in subjects_text:
            return '警察人員考試三等考試_交通警察人員類別交通組'
        if '通訊系統' in subjects_text and '電路學' in subjects_text:
            return '警察人員考試三等考試_交通警察人員電訊組'
        if '電腦犯罪偵查' in subjects_text and '數位鑑識執法' in subjects_text:
            return '警察人員考試三等考試_警察資訊管理人員類別'
        if '物理鑑識' in subjects_text and '刑事化學' in subjects_text and '刑事生物' in subjects_text:
            return '警察人員考試三等考試_刑事鑑識人員類別'
        if '移民情勢與政策分析' in subjects_text and '國境執法' in subjects_text:
            return '警察人員考試三等考試_國境警察人員類別'
        if '水上警察學' in subjects_text and '海上犯罪偵查法學' in subjects_text:
            return '警察人員考試三等考試_水上警察人員類別'
        if '警察法制作業' in subjects_text and '行政法與警察行政違規調查裁處作業' in subjects_text:
            return '警察人員考試三等考試_警察法制人員類別'
        if '警察人事行政與法制' in subjects_text and '警察組織與事務管理' in subjects_text:
            return '警察人員考試三等考試_行政管理人員類別'

        return None

    # 整理成最終結構
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

    return exam_structure

def download_file(session, url, file_path, max_retries=3):
    """下載檔案"""
    for attempt in range(max_retries):
        try:
            response = session.get(url, headers=HEADERS, stream=True, timeout=60, verify=False)
            response.raise_for_status()

            content_type = response.headers.get('Content-Type', '')
            if 'pdf' not in content_type.lower() and 'application/octet-stream' not in content_type.lower():
                return False, "非PDF檔案"

            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)

            file_size = os.path.getsize(file_path)
            if file_size > 1024:
                return True, file_size
            else:
                os.remove(file_path)
                return False, "檔案過小"

        except Exception as e:
            if attempt == max_retries - 1:
                return False, str(e)[:50]
            time.sleep(2)

    return False, "重試失敗"

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
        
        exam_structure = parse_exam_page(response.text, exam_name)
        
        if not exam_structure:
            print("   ⚠️ 此考試沒有可下載的試題")
            stats['empty_exams'] += 1
            return
        
        # 建立考試資料夾
        short_exam_name = f"民國{year}年_警察司法特考"
        exam_folder = os.path.join(base_folder, f"民國{year}年", short_exam_name)
        os.makedirs(exam_folder, exist_ok=True)
        
        total_subjects = sum(len(subjects) for subjects in exam_structure.values())
        total_files = sum(
            len(subject['downloads']) 
            for subjects in exam_structure.values() 
            for subject in subjects
        )
        
        print(f"   📊 類科: {len(exam_structure)} 個 | 科目: {total_subjects} 個 | 檔案: {total_files} 個")
        
        # 學系名稱對應到資料夾名稱的映射
        department_folder_mapping = {
            "警察人員考試三等考試_行政警察人員類別": "行政警察",
            "警察人員考試三等考試_外事警察人員(選試英語)類別": "外事警察",
            "警察人員考試三等考試_刑事警察人員類別": "刑事警察", 
            "警察人員考試三等考試_公共安全人員類別": "公共安全",
            "警察人員考試三等考試_犯罪防治人員類別預防組": "犯罪防治",
            "警察人員考試三等考試_消防警察人員類別": "消防警察",
            "警察人員考試三等考試_交通警察人員類別交通組": "交通警察_交通",
            "警察人員考試三等考試_警察資訊管理人員類別": "資訊管理",
            "警察人員考試三等考試_刑事鑑識人員類別": "刑事鑑識",
            "警察人員考試三等考試_國境警察人員類別": "國境警察",
            "警察人員考試三等考試_水上警察人員類別": "水上警察",
            "警察人員考試三等考試_警察法制人員類別": "警察法制",
            "警察人員考試三等考試_交通警察人員電訊組": "交通警察_電訊",
            "警察人員考試三等考試_行政管理人員類別": "行政管理",
            "司法三等考試_監獄官(男)": "監獄官",
            "司法三等考試_監獄官(女)": "監獄官"
        }
        
        file_count = 0
        for category_name, subjects in exam_structure.items():
            # 取得對應的資料夾名稱
            folder_name = department_folder_mapping.get(category_name, category_name.split('_')[-1])
            category_folder = os.path.join(exam_folder, folder_name)
            os.makedirs(category_folder, exist_ok=True)
            
            for subject_info in subjects:
                subject_name = subject_info['subject']
                
                # 為每個科目建立專用資料夾
                subject_folder = os.path.join(category_folder, subject_name)
                os.makedirs(subject_folder, exist_ok=True)
                
                for download_info in subject_info['downloads']:
                    file_type = download_info['type']
                    url = download_info['url']
                    
                    file_name = f"{file_type}.pdf"
                    file_path = os.path.join(subject_folder, file_name)
                    
                    pdf_url = urljoin(BASE_URL, url)
                    success, result = download_file(session, pdf_url, file_path)
                    
                    file_count += 1
                    if file_count % 10 == 0:
                        print(f"   ⬇️  進度: {file_count}/{total_files}", end='\r')
                    
                    if success:
                        stats['success'] += 1
                        stats['total_size'] += result
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
                        time.sleep(2)
        
        print(f"   ✅ 完成: {file_count}/{total_files} 個檔案")
        stats['completed_exams'] += 1
        
    except Exception as e:
        print(f"   ❌ 處理失敗: {e}")
        stats['failed_exams'] += 1

def main():
    print("簡化版考古題下載工具")
    print("="*70)
    print("🎯 目標: 下載指定的16個學系")
    print("📅 年份: 民國114年")
    print("="*70)
    
    # 建立儲存目錄
    os.makedirs(SAVE_DIR, exist_ok=True)
    
    stats = {
        'success': 0,
        'failed': 0,
        'total_size': 0,
        'completed_exams': 0,
        'failed_exams': 0,
        'empty_exams': 0,
        'failed_list': []
    }
    
    session = requests.Session()
    session.headers.update(HEADERS)
    
    start_time = datetime.now()
    
    try:
        year = 114
        print(f"\n🔍 正在掃描民國 {year} 年的考試...")
        
        exams = get_exam_list_by_year(session, year)
        
        if not exams:
            print(f"   ⚠️ 民國 {year} 年沒有找到符合條件的考試")
            return
        
        print(f"   ✅ 找到 {len(exams)} 個考試")
        
        for exam in exams:
            download_exam(session, exam, SAVE_DIR, stats)
            time.sleep(1)
        
        elapsed_time = datetime.now() - start_time
        
        # 產生報告
        print("\n" + "="*70)
        print("📊 下載完成統計")
        print("="*70)
        print(f"⏱️  總耗時: {elapsed_time}")
        print(f"✅ 成功下載: {stats['success']} 個檔案")
        print(f"❌ 失敗: {stats['failed']} 個檔案")
        print(f"📦 總大小: {stats['total_size'] / (1024*1024):.2f} MB")
        
        if stats['failed_list']:
            print(f"\n⚠️  失敗清單 ({len(stats['failed_list'])} 個):")
            for item in stats['failed_list'][:5]:  # 只顯示前5個
                print(f"   - {item['category']}: {item['subject']} ({item['reason']})")
        
        print(f"\n🎉 下載完成！檔案位於: {SAVE_DIR}")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  使用者中斷下載")
    except Exception as e:
        print(f"\n❌ 發生錯誤: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    main()