#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
簡化的Google表單轉換器執行腳本
"""

import os
import sys
from google_forms_converter import GoogleFormsConverter

def main():
    print("🚀 Google表單考古題轉換器")
    print("="*50)
    
    # 檢查輸入目錄
    input_dir = "考選部考古題完整庫/民國114年"
    if not os.path.exists(input_dir):
        print(f"❌ 找不到輸入目錄: {input_dir}")
        print("請確認PDF檔案已下載到正確位置")
        return
    
    # 建立轉換器
    converter = GoogleFormsConverter()
    
    # 尋找PDF檔案
    import glob
    pdf_files = glob.glob(os.path.join(input_dir, "**", "*.pdf"), recursive=True)
    
    if not pdf_files:
        print("❌ 沒有找到PDF檔案")
        return
    
    print(f"📁 找到 {len(pdf_files)} 個PDF檔案")
    
    # 讓使用者選擇處理方式
    print("\n選擇處理方式:")
    print("1. 處理所有PDF檔案")
    print("2. 選擇特定PDF檔案")
    print("3. 處理單一PDF檔案")
    
    choice = input("\n請輸入選項 (1-3): ").strip()
    
    if choice == "1":
        # 處理所有檔案
        process_all_files(converter, pdf_files)
    elif choice == "2":
        # 選擇特定檔案
        select_files(converter, pdf_files)
    elif choice == "3":
        # 處理單一檔案
        process_single_file(converter, pdf_files)
    else:
        print("❌ 無效選項")
        return

def process_all_files(converter, pdf_files):
    """處理所有PDF檔案"""
    print(f"\n🔄 開始處理 {len(pdf_files)} 個檔案...")
    
    results = []
    for i, pdf_path in enumerate(pdf_files, 1):
        print(f"\n[{i}/{len(pdf_files)}] 處理: {os.path.basename(pdf_path)}")
        
        # 尋找答案檔案
        answer_path = find_answer_file(pdf_path)
        if answer_path:
            print(f"✅ 找到答案檔案: {os.path.basename(answer_path)}")
        
        # 處理PDF
        result = converter.process_pdf_to_google_forms(pdf_path, answer_path)
        if result:
            results.append(result)
    
    print_summary(results)

def select_files(converter, pdf_files):
    """讓使用者選擇要處理的檔案"""
    print("\n可用的PDF檔案:")
    for i, pdf_path in enumerate(pdf_files, 1):
        print(f"{i}. {os.path.basename(pdf_path)}")
    
    print("\n請輸入要處理的檔案編號 (用逗號分隔，例如: 1,3,5):")
    selection = input("檔案編號: ").strip()
    
    try:
        indices = [int(x.strip()) - 1 for x in selection.split(',')]
        selected_files = [pdf_files[i] for i in indices if 0 <= i < len(pdf_files)]
        
        if not selected_files:
            print("❌ 沒有選擇有效的檔案")
            return
        
        print(f"\n🔄 開始處理 {len(selected_files)} 個選定的檔案...")
        
        results = []
        for i, pdf_path in enumerate(selected_files, 1):
            print(f"\n[{i}/{len(selected_files)}] 處理: {os.path.basename(pdf_path)}")
            
            answer_path = find_answer_file(pdf_path)
            if answer_path:
                print(f"✅ 找到答案檔案: {os.path.basename(answer_path)}")
            
            result = converter.process_pdf_to_google_forms(pdf_path, answer_path)
            if result:
                results.append(result)
        
        print_summary(results)
        
    except ValueError:
        print("❌ 輸入格式錯誤")

def process_single_file(converter, pdf_files):
    """處理單一PDF檔案"""
    print("\n可用的PDF檔案:")
    for i, pdf_path in enumerate(pdf_files, 1):
        print(f"{i}. {os.path.basename(pdf_path)}")
    
    try:
        choice = int(input("\n請選擇檔案編號: ").strip()) - 1
        if 0 <= choice < len(pdf_files):
            pdf_path = pdf_files[choice]
            print(f"\n🔄 處理檔案: {os.path.basename(pdf_path)}")
            
            answer_path = find_answer_file(pdf_path)
            if answer_path:
                print(f"✅ 找到答案檔案: {os.path.basename(answer_path)}")
            
            result = converter.process_pdf_to_google_forms(pdf_path, answer_path)
            if result:
                print_single_result(result)
        else:
            print("❌ 無效的檔案編號")
    except ValueError:
        print("❌ 請輸入有效的數字")

def find_answer_file(pdf_path):
    """尋找對應的答案檔案"""
    base_name = os.path.splitext(os.path.basename(pdf_path))[0]
    base_dir = os.path.dirname(pdf_path)
    
    # 可能的答案檔案名稱
    answer_keywords = ['答案', '解答', 'answer', 'Answer']
    
    for keyword in answer_keywords:
        for ext in ['.pdf', '.PDF']:
            potential_answer = os.path.join(base_dir, f"{base_name}_{keyword}{ext}")
            if os.path.exists(potential_answer):
                return potential_answer
    
    return None

def print_summary(results):
    """列印處理結果摘要"""
    print(f"\n{'='*50}")
    print("📊 處理完成摘要")
    print(f"{'='*50}")
    print(f"成功處理: {len(results)} 個檔案")
    
    if results:
        total_questions = sum(r['question_count'] for r in results)
        total_answers = sum(r['answer_count'] for r in results)
        print(f"總題數: {total_questions}")
        print(f"有答案的題目: {total_answers}")
        print(f"輸出目錄: google_forms_output")
        
        print(f"\n📁 生成的檔案:")
        for i, result in enumerate(results, 1):
            print(f"{i}. {os.path.basename(result['google_csv'])}")
            print(f"   - 題目數: {result['question_count']}")
            print(f"   - 答案數: {result['answer_count']}")

def print_single_result(result):
    """列印單一檔案處理結果"""
    print(f"\n{'='*50}")
    print("📊 處理結果")
    print(f"{'='*50}")
    print(f"題目數: {result['question_count']}")
    print(f"答案數: {result['answer_count']}")
    print(f"輸出目錄: google_forms_output")
    print(f"\n📁 生成的檔案:")
    print(f"- {os.path.basename(result['google_csv'])}")
    print(f"- {os.path.basename(result['script'])}")
    print(f"- {os.path.basename(result['readme'])}")

if __name__ == "__main__":
    main()