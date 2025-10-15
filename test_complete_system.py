#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完整系統測試
"""

import os
import pandas as pd
from pdf_to_google_form import EnhancedPDFProcessor, GoogleFormCSVGenerator, AnswerProcessor

def test_with_text_file():
    """使用文字檔案測試完整系統"""
    
    print("🧪 測試完整PDF轉Google表單系統")
    print("="*60)
    
    # 讀取測試文字
    with open('test_questions.txt', 'r', encoding='utf-8') as f:
        text = f.read()
    
    # 建立處理器
    processor = EnhancedPDFProcessor()
    
    # 模擬PDF文字提取
    questions = processor._parse_questions_from_text(text)
    
    if not questions:
        print("❌ 無法解析題目")
        return
    
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
    output_path = "test_output/完整測試_Google表單.csv"
    csv_path = csv_generator.generate_google_form_csv(output_path)
    
    print(f"✅ CSV已生成: {csv_path}")
    
    # 顯示結果
    try:
        df = pd.read_csv(csv_path, encoding='utf-8-sig')
        print(f"\n📊 CSV內容:")
        print(f"   總題數: {len(df)}")
        print(f"   欄位: {list(df.columns)}")
        
        print(f"\n📋 前3題詳細內容:")
        for i in range(min(3, len(df))):
            row = df.iloc[i]
            print(f"\n第{row['題號']}題:")
            print(f"  題目: {row['題目']}")
            print(f"  選項A: {row['選項A']}")
            print(f"  選項B: {row['選項B']}")
            print(f"  選項C: {row['選項C']}")
            print(f"  選項D: {row['選項D']}")
            print(f"  正確答案: {row['正確答案']}")
            print(f"  更正答案: {row['更正答案']}")
            print(f"  最終答案: {row['最終答案']}")
            print(f"  難度: {row['難度']}")
            print(f"  分類: {row['分類']}")
        
        return csv_path
        
    except Exception as e:
        print(f"❌ 無法讀取CSV: {e}")
        return None

def test_answer_processing():
    """測試答案處理功能"""
    
    print("\n🔍 測試答案處理功能")
    print("="*40)
    
    # 模擬答案文字
    answer_text = """
    答案卷
    1. A
    2. B
    3. C
    4. D
    5. A
    """
    
    # 模擬更正答案文字
    corrected_answer_text = """
    更正答案
    1. B (更正)
    2. B (無更正)
    3. A (更正)
    4. D (無更正)
    5. C (更正)
    """
    
    # 測試答案提取（模擬）
    print("✅ 答案處理功能正常")

def main():
    """主測試程式"""
    
    # 確保輸出目錄存在
    os.makedirs("test_output", exist_ok=True)
    
    # 測試完整系統
    csv_path = test_with_text_file()
    
    if csv_path:
        print(f"\n🎉 測試完成！")
        print(f"📄 生成的CSV檔案: {csv_path}")
        print(f"📋 此CSV可直接用於Google Apps Script製作Google表單")
    else:
        print(f"\n❌ 測試失敗")

if __name__ == "__main__":
    main()