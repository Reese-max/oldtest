#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
考古題下載工具覆蓋率測試
檢查是否會遺漏某些學系的考科
"""

import requests
from bs4 import BeautifulSoup
import re
import json
from datetime import datetime

# 基本設定
BASE_URL = "https://wwwq.moex.gov.tw/exam/"
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7',
    'Connection': 'keep-alive'
}

def get_all_exams_by_year(year):
    """獲取指定年份的所有考試"""
    try:
        url = f"{BASE_URL}wFrmExamQandASearch.aspx?y={year + 1911}"
        response = requests.get(url, timeout=30, verify=False, headers=HEADERS)
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
                exams.append({
                    'code': exam_code,
                    'name': exam_name,
                    'year': year
                })
        
        return exams
    except Exception as e:
        print(f"❌ 獲取 {year} 年考試列表失敗: {e}")
        return []

def analyze_exam_coverage(exams):
    """分析考試覆蓋率"""
    coverage_analysis = {
        'total_exams': len(exams),
        'covered_exams': [],
        'missed_exams': [],
        'exam_categories': {}
    }
    
    # 現有工具支援的關鍵字
    supported_keywords = [
        "警察人員考試",
        "一般警察人員考試", 
        "司法人員考試",
        "國家安全情報人員考試",
        "移民行政人員考試"
    ]
    
    # 其他可能的考試類型
    other_exam_types = [
        "公務人員高等考試",
        "公務人員普通考試", 
        "公務人員初等考試",
        "公務人員特種考試",
        "專門職業及技術人員考試",
        "律師考試",
        "會計師考試",
        "建築師考試",
        "技師考試",
        "醫師考試",
        "護理師考試",
        "社會工作師考試",
        "心理師考試"
    ]
    
    for exam in exams:
        exam_name = exam['name']
        is_covered = False
        
        # 檢查是否被現有工具覆蓋
        for keyword in supported_keywords:
            if keyword in exam_name:
                coverage_analysis['covered_exams'].append(exam)
                is_covered = True
                break
        
        if not is_covered:
            coverage_analysis['missed_exams'].append(exam)
            
            # 分類未覆蓋的考試
            for exam_type in other_exam_types:
                if exam_type in exam_name:
                    if exam_type not in coverage_analysis['exam_categories']:
                        coverage_analysis['exam_categories'][exam_type] = []
                    coverage_analysis['exam_categories'][exam_type].append(exam)
                    break
    
    return coverage_analysis

def test_specific_year(year=113):
    """測試特定年份的覆蓋率"""
    print(f"\n{'='*70}")
    print(f"🔍 測試民國 {year} 年考古題下載覆蓋率")
    print(f"{'='*70}")
    
    # 獲取所有考試
    exams = get_all_exams_by_year(year)
    if not exams:
        print(f"❌ 無法獲取民國 {year} 年的考試列表")
        return
    
    print(f"📊 總共找到 {len(exams)} 個考試")
    
    # 分析覆蓋率
    analysis = analyze_exam_coverage(exams)
    
    print(f"\n📈 覆蓋率分析:")
    print(f"   ✅ 已覆蓋: {len(analysis['covered_exams'])} 個考試")
    print(f"   ❌ 未覆蓋: {len(analysis['missed_exams'])} 個考試")
    print(f"   📊 覆蓋率: {len(analysis['covered_exams'])/len(exams)*100:.1f}%")
    
    # 顯示已覆蓋的考試
    print(f"\n✅ 已覆蓋的考試:")
    for exam in analysis['covered_exams']:
        print(f"   - {exam['name']}")
    
    # 顯示未覆蓋的考試
    print(f"\n❌ 未覆蓋的考試:")
    for exam in analysis['missed_exams']:
        print(f"   - {exam['name']}")
    
    # 按類別顯示未覆蓋的考試
    if analysis['exam_categories']:
        print(f"\n📋 未覆蓋考試分類:")
        for category, exams_list in analysis['exam_categories'].items():
            print(f"   {category}: {len(exams_list)} 個")
            for exam in exams_list[:3]:  # 只顯示前3個
                print(f"     - {exam['name']}")
            if len(exams_list) > 3:
                print(f"     ... 還有 {len(exams_list)-3} 個")
    
    return analysis

def main():
    print("考古題下載工具覆蓋率測試")
    print("="*70)
    
    # 測試最近幾年
    test_years = [111, 112, 113, 114]
    
    all_analysis = {}
    for year in test_years:
        analysis = test_specific_year(year)
        if analysis:
            all_analysis[year] = analysis
    
    # 總結報告
    print(f"\n{'='*70}")
    print("📊 總結報告")
    print(f"{'='*70}")
    
    total_exams = sum(a['total_exams'] for a in all_analysis.values())
    total_covered = sum(len(a['covered_exams']) for a in all_analysis.values())
    total_missed = sum(len(a['missed_exams']) for a in all_analysis.values())
    
    print(f"總考試數: {total_exams}")
    print(f"已覆蓋: {total_covered} ({total_covered/total_exams*100:.1f}%)")
    print(f"未覆蓋: {total_missed} ({total_missed/total_exams*100:.1f}%)")
    
    # 建議
    print(f"\n💡 改進建議:")
    print("1. 擴展類科識別邏輯，支援更多考試類型")
    print("2. 添加動態類科識別，不依賴硬編碼的關鍵字")
    print("3. 提供用戶自定義篩選條件")
    print("4. 增加考試類型統計和報告功能")

if __name__ == "__main__":
    main()