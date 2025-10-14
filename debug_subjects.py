#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
調試腳本：檢查科目組合
"""

import requests
from bs4 import BeautifulSoup
import re
from collections import defaultdict

BASE_URL = "https://wwwq.moex.gov.tw/exam/"
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

def debug_subjects():
    session = requests.Session()
    session.headers.update(HEADERS)
    
    # 獲取警察特考頁面
    url = f"{BASE_URL}wFrmExamQandASearch.aspx?y=2025&e=114"
    response = session.get(url, timeout=30, verify=False)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # 收集所有類科代碼的科目
    raw_structure = defaultdict(lambda: defaultdict(dict))
    
    links = soup.find_all('a', href=re.compile(r'wHandExamQandA_File\.ashx'))
    
    for link in links:
        href = link.get('href', '')
        if not href:
            continue

        # 解析URL參數
        code_match = re.search(r'[&?]c=(\d+)', href)
        if not code_match:
            continue

        category_code = code_match.group(1)

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

        raw_structure[category_code][subject_name] = True

    print("找到的類科和科目組合:")
    print("="*70)
    
    for category_code, subjects_dict in raw_structure.items():
        subjects_list = list(subjects_dict.keys())
        subjects_text = '|||'.join(subjects_list)
        
        print(f"\n類科代碼: {category_code}")
        print(f"科目數量: {len(subjects_list)}")
        print("科目列表:")
        for subject in subjects_list:
            print(f"  - {subject}")
        
        # 檢查是否為內軌
        is_internal = (
            '中華民國憲法與警察專業英文' in subjects_text or
            '中華民國憲法與消防警察專業英文' in subjects_text or
            '中華民國憲法與水上警察專業英文' in subjects_text
        )
        
        print(f"是否為內軌: {is_internal}")
        
        if is_internal:
            # 檢查具體的學系識別
            if '警察學與警察勤務' in subjects_text:
                print("  → 行政警察人員")
            elif '外事警察學' in subjects_text:
                print("  → 外事警察人員")
            elif '犯罪偵查學' in subjects_text and '刑案現場處理' in subjects_text:
                print("  → 刑事警察人員")
            elif '情報學' in subjects_text and '國家安全情報法制' in subjects_text:
                print("  → 公共安全人員")
            elif '諮商輔導與婦幼保護' in subjects_text and '犯罪分析' in subjects_text:
                print("  → 犯罪防治人員")
            elif '火災學與消防化學' in subjects_text and '消防安全設備' in subjects_text:
                print("  → 消防警察人員")
            elif '交通警察學' in subjects_text and '交通統計與分析' in subjects_text:
                print("  → 交通警察人員交通組")
            elif '通訊系統' in subjects_text and '電路學' in subjects_text:
                print("  → 交通警察人員電訊組")
            elif '電腦犯罪偵查' in subjects_text and '數位鑑識執法' in subjects_text:
                print("  → 警察資訊管理人員")
            elif '物理鑑識' in subjects_text and '刑事化學' in subjects_text and '刑事生物' in subjects_text:
                print("  → 刑事鑑識人員")
            elif '移民情勢與政策分析' in subjects_text and '國境執法' in subjects_text:
                print("  → 國境警察人員")
            elif '水上警察學' in subjects_text and '海上犯罪偵查法學' in subjects_text:
                print("  → 水上警察人員")
            elif '警察法制作業' in subjects_text and '行政法與警察行政違規調查裁處作業' in subjects_text:
                print("  → 警察法制人員")
            elif '警察人事行政與法制' in subjects_text and '警察組織與事務管理' in subjects_text:
                print("  → 行政管理人員")
            else:
                print("  → 未識別")
        else:
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
            if not has_exclude_subjects:
                judicial_matches = sum(1 for subject in judicial_subjects if subject in subjects_text)
                if judicial_matches >= 4:
                    print("  → 司法三等考試_監獄官")
                else:
                    print("  → 未識別")
            else:
                print("  → 非三等監獄官")

if __name__ == "__main__":
    debug_subjects()