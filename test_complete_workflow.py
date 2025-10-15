#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完整工作流程測試
從PDF到Google表單的完整流程
"""

import os
import pandas as pd
from pdf_to_google_form import EnhancedPDFProcessor, GoogleFormCSVGenerator, AnswerProcessor
from google_apps_script_generator_fixed import GoogleAppsScriptGenerator

def test_complete_workflow():
    """測試完整工作流程"""
    
    print("🚀 完整工作流程測試")
    print("="*60)
    
    # 步驟1: 處理PDF並生成CSV
    print("\n📄 步驟1: PDF轉CSV")
    print("-" * 30)
    
    # 使用文字檔案模擬PDF
    with open('test_questions.txt', 'r', encoding='utf-8') as f:
        text = f.read()
    
    processor = EnhancedPDFProcessor()
    questions = processor._parse_questions_from_text(text)
    
    if not questions:
        print("❌ PDF解析失敗")
        return False
    
    print(f"✅ 成功解析 {len(questions)} 題")
    
    # 建立CSV生成器
    csv_generator = GoogleFormCSVGenerator()
    
    # 添加題目
    for q in questions:
        csv_generator.add_question(q)
    
    # 模擬答案資料
    sample_answers = {
        '1': 'A',
        '2': 'B', 
        '3': 'C',
        '4': 'D',
        '5': 'A'
    }
    
    sample_corrected_answers = {
        '1': 'B',  # 更正答案
        '2': 'B',  # 無更正
        '3': 'A',  # 更正答案
        '4': 'D',  # 無更正
        '5': 'C'   # 更正答案
    }
    
    # 添加答案
    for q_num, answer in sample_answers.items():
        csv_generator.add_answer(q_num, answer)
    
    for q_num, answer in sample_corrected_answers.items():
        csv_generator.add_corrected_answer(q_num, answer)
    
    # 生成CSV
    csv_path = "test_output/完整工作流程測試.csv"
    csv_generator.generate_google_form_csv(csv_path)
    print(f"✅ CSV已生成: {csv_path}")
    
    # 步驟2: 生成Google Apps Script
    print("\n📝 步驟2: 生成Google Apps Script")
    print("-" * 30)
    
    script_generator = GoogleAppsScriptGenerator()
    script_path = script_generator.generate_script_from_csv(csv_path)
    
    if not script_path:
        print("❌ JavaScript生成失敗")
        return False
    
    print(f"✅ JavaScript已生成: {script_path}")
    
    # 步驟3: 驗證生成的檔案
    print("\n🔍 步驟3: 驗證生成的檔案")
    print("-" * 30)
    
    # 檢查CSV檔案
    try:
        df = pd.read_csv(csv_path, encoding='utf-8-sig')
        print(f"✅ CSV驗證通過: {len(df)} 題")
        print(f"   欄位: {list(df.columns)}")
        
        # 檢查答案完整性
        answered_questions = df[df['最終答案'].notna() & (df['最終答案'] != '')]
        print(f"   有答案的題目: {len(answered_questions)}/{len(df)}")
        
    except Exception as e:
        print(f"❌ CSV驗證失敗: {e}")
        return False
    
    # 檢查JavaScript檔案
    try:
        with open(script_path, 'r', encoding='utf-8') as f:
            js_content = f.read()
        
        # 檢查關鍵函數是否存在
        required_functions = [
            'createPracticeForm',
            'addQuestionsToForm',
            'calculateScore',
            'main'
        ]
        
        missing_functions = []
        for func in required_functions:
            if f'function {func}' not in js_content:
                missing_functions.append(func)
        
        if missing_functions:
            print(f"❌ JavaScript驗證失敗: 缺少函數 {missing_functions}")
            return False
        
        print(f"✅ JavaScript驗證通過: {len(js_content)} 字元")
        
    except Exception as e:
        print(f"❌ JavaScript驗證失敗: {e}")
        return False
    
    # 步驟4: 生成使用說明
    print("\n📋 步驟4: 生成使用說明")
    print("-" * 30)
    
    instructions_path = script_generator.generate_instructions()
    print(f"✅ 使用說明已生成: {instructions_path}")
    
    # 步驟5: 總結
    print("\n🎉 工作流程測試完成")
    print("="*60)
    
    print(f"📄 生成的檔案:")
    print(f"   - CSV資料: {csv_path}")
    print(f"   - JavaScript: {script_path}")
    print(f"   - 使用說明: {instructions_path}")
    
    print(f"\n📝 使用步驟:")
    print(f"1. 將JavaScript代碼複製到Google Apps Script")
    print(f"2. 執行main()函數建立Google表單")
    print(f"3. 分享表單連結開始練習")
    print(f"4. 查看試算表中的練習結果")
    
    return True

def test_error_handling():
    """測試錯誤處理"""
    
    print("\n🛡️ 錯誤處理測試")
    print("-" * 30)
    
    # 測試不存在的CSV檔案
    try:
        generator = GoogleAppsScriptGenerator()
        result = generator.generate_script_from_csv("不存在的檔案.csv")
        if result is None:
            print("✅ 不存在檔案處理正常")
        else:
            print("❌ 不存在檔案處理異常")
    except Exception as e:
        print(f"✅ 錯誤處理正常: {e}")
    
    # 測試空CSV檔案
    try:
        empty_df = pd.DataFrame()
        empty_df.to_csv("test_output/空檔案.csv", index=False, encoding='utf-8-sig')
        
        generator = GoogleAppsScriptGenerator()
        result = generator.generate_script_from_csv("test_output/空檔案.csv")
        if result is None:
            print("✅ 空檔案處理正常")
        else:
            print("❌ 空檔案處理異常")
    except Exception as e:
        print(f"✅ 空檔案錯誤處理正常: {e}")

def main():
    """主程式"""
    
    # 確保輸出目錄存在
    os.makedirs("test_output", exist_ok=True)
    
    # 執行完整工作流程測試
    success = test_complete_workflow()
    
    if success:
        # 執行錯誤處理測試
        test_error_handling()
        
        print(f"\n🎉 所有測試完成！")
        print(f"📋 系統已準備就緒，可以開始使用PDF轉Google表單功能")
    else:
        print(f"\n❌ 測試失敗，請檢查錯誤訊息")

if __name__ == "__main__":
    main()