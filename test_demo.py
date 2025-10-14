#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試Google表單轉換器的示範腳本
"""

import os
import json
from google_forms_converter import GoogleFormsConverter

def create_demo_data():
    """建立示範資料"""
    demo_questions = [
        {
            '題號': '1',
            '題目': '下列何者為警察法第2條所規定之警察任務？',
            '選項A': '維護社會秩序',
            '選項B': '保護人民生命財產',
            '選項C': '促進人民福利',
            '選項D': '以上皆是',
            '題型': '選擇題'
        },
        {
            '題號': '2',
            '題目': '警察人員執行職務時，應遵守之基本原則為何？',
            '選項A': '依法行政',
            '選項B': '比例原則',
            '選項C': '正當程序',
            '選項D': '以上皆是',
            '題型': '選擇題'
        },
        {
            '題號': '3',
            '題目': '請說明警察人員在執行職務時應具備的基本素養。',
            '選項A': '',
            '選項B': '',
            '選項C': '',
            '選項D': '',
            '題型': '問答題'
        }
    ]
    
    demo_answers = {
        '1': 'D',
        '2': 'D',
        '3': '專業知識、法律素養、溝通技巧、危機處理能力等'
    }
    
    return demo_questions, demo_answers

def main():
    print("🧪 Google表單轉換器測試示範")
    print("="*50)
    
    # 建立轉換器
    converter = GoogleFormsConverter()
    
    # 建立示範資料
    questions, answers = create_demo_data()
    print(f"✅ 建立 {len(questions)} 題示範資料")
    
    # 轉換為Google表單格式
    google_forms_data = converter.convert_to_google_forms_format(questions, answers)
    print(f"✅ 轉換為Google表單格式")
    
    # 建立輸出目錄
    output_dir = "demo_output"
    os.makedirs(output_dir, exist_ok=True)
    
    # 儲存CSV檔案
    import pandas as pd
    df = pd.DataFrame(google_forms_data)
    csv_path = os.path.join(output_dir, "demo_google_forms.csv")
    df.to_csv(csv_path, index=False, encoding='utf-8-sig')
    print(f"✅ 儲存CSV: {csv_path}")
    
    # 生成Google Apps Script
    script_content = converter.create_google_apps_script(google_forms_data, "警察法規考古題練習")
    script_path = os.path.join(output_dir, "demo_google_apps_script.js")
    with open(script_path, 'w', encoding='utf-8') as f:
        f.write(script_content)
    print(f"✅ 儲存Script: {script_path}")
    
    # 顯示結果預覽
    print(f"\n📊 轉換結果預覽:")
    print(f"總題數: {len(google_forms_data)}")
    print(f"選擇題: {len([q for q in google_forms_data if q['題型'] == '選擇題'])}")
    print(f"問答題: {len([q for q in google_forms_data if q['題型'] == '問答題'])}")
    print(f"有答案: {len([q for q in google_forms_data if q['正確答案']])}")
    
    print(f"\n📝 題目預覽:")
    for i, q in enumerate(google_forms_data[:2], 1):
        print(f"{i}. {q['題目']}")
        if q['題型'] == '選擇題':
            print(f"   選項: A.{q['選項A']} B.{q['選項B']} C.{q['選項C']} D.{q['選項D']}")
            print(f"   答案: {q['正確答案']}")
        print()
    
    print(f"✅ 測試完成！檔案已儲存至 {output_dir} 目錄")
    print(f"\n📁 生成的檔案:")
    print(f"- {csv_path}")
    print(f"- {script_path}")

if __name__ == "__main__":
    main()