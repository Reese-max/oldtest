#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試PDF轉CSV的答案辨識功能
"""

import os
import sys
import json
import pandas as pd
from pdf_to_csv import PDFFeatureAnalyzer, ValidationResult

def test_answer_detection():
    """測試答案辨識功能"""
    
    print("🧪 測試PDF轉CSV答案辨識功能")
    print("="*50)
    
    # 測試答案處理器
    print("\n🔍 測試答案處理器...")
    
    # 模擬答案文字
    test_answer_text = """
    1. A
    2. B  
    3. C
    4. D
    5. A
    """
    
    # 模擬更正答案文字
    test_corrected_answer_text = """
    更正答案
    1. B
    3. A
    5. C
    """
    
    # 建立臨時檔案
    temp_answer_file = "temp_answer.txt"
    temp_corrected_file = "temp_corrected.txt"
    
    with open(temp_answer_file, 'w', encoding='utf-8') as f:
        f.write(test_answer_text)
    
    with open(temp_corrected_file, 'w', encoding='utf-8') as f:
        f.write(test_corrected_answer_text)
    
    print("   📝 模擬答案文字:")
    print(f"   {test_answer_text.strip()}")
    
    print("\n   📝 模擬更正答案文字:")
    print(f"   {test_corrected_answer_text.strip()}")
    
    # 測試正則表達式匹配
    import re
    
    # 答案模式
    answer_patterns = [
        r'(\d+)[\.\)]\s*([A-D])',
        r'(\d+)\s*([A-D])',
        r'第\s*(\d+)\s*題\s*([A-D])'
    ]
    
    print("\n   🔍 測試答案提取...")
    answers = {}
    for pattern in answer_patterns:
        matches = re.findall(pattern, test_answer_text)
        for match in matches:
            question_num, answer = match
            answers[question_num] = answer
            print(f"     題號 {question_num}: {answer}")
    
    # 更正答案模式
    corrected_patterns = [
        r'更正.*?(\d+)[\.\)]\s*([A-D])',
        r'(\d+)[\.\)]\s*([A-D])\s*更正',
        r'(\d+)\s*([A-D])\s*\(更正\)'
    ]
    
    print("\n   🔍 測試更正答案提取...")
    corrected_answers = {}
    for pattern in corrected_patterns:
        matches = re.findall(pattern, test_corrected_answer_text, re.IGNORECASE)
        for match in matches:
            question_num, answer = match
            corrected_answers[question_num] = answer
            print(f"     題號 {question_num}: {answer} (更正)")
    
    # 測試CSV輸出格式
    print("\n📊 測試CSV輸出格式...")
    
    # 建立測試題目資料（包含答案）
    test_questions = [
        {
            '題號': '1',
            '題目': '下列各組「」內的字，讀音完全相同的選項是：',
            '選項A': '「緋」聞纏身／「誹」謗他人／「斐」然成章',
            '選項B': '「緋」聞纏身／「誹」謗他人／「斐」然成章',
            '選項C': '「緋」聞纏身／「誹」謗他人／「斐」然成章',
            '選項D': '「緋」聞纏身／「誹」謗他人／「斐」然成章',
            '題型': '選擇題',
            '正確答案': 'A',
            '更正答案': 'B'
        },
        {
            '題號': '2',
            '題目': '下列文句，完全沒有錯別字的選項是：',
            '選項A': '他做事總是虎頭蛇尾，令人失望',
            '選項B': '他做事總是虎頭蛇尾，令人失望',
            '選項C': '他做事總是虎頭蛇尾，令人失望',
            '選項D': '他做事總是虎頭蛇尾，令人失望',
            '題型': '選擇題',
            '正確答案': 'B',
            '更正答案': ''
        },
        {
            '題號': '3',
            '題目': '下列成語使用正確的選項是：',
            '選項A': '他做事總是虎頭蛇尾，令人失望',
            '選項B': '他做事總是虎頭蛇尾，令人失望',
            '選項C': '他做事總是虎頭蛇尾，令人失望',
            '選項D': '他做事總是虎頭蛇尾，令人失望',
            '題型': '選擇題',
            '正確答案': 'C',
            '更正答案': 'A'
        }
    ]
    
    # 輸出CSV
    try:
        output_dir = "test_output"
        os.makedirs(output_dir, exist_ok=True)
        
        # 選擇題CSV
        choice_questions = [q for q in test_questions if q['題型'] == '選擇題']
        if choice_questions:
            choice_path = os.path.join(output_dir, "測試答案辨識_選擇題.csv")
            df = pd.DataFrame(choice_questions)
            df.to_csv(choice_path, index=False, encoding='utf-8-sig')
            print(f"   ✅ 選擇題CSV已建立: {choice_path}")
            print(f"   📊 包含 {len(choice_questions)} 題")
            
            # 顯示CSV內容
            print("\n   📋 CSV內容預覽:")
            print(df.to_string(index=False))
    
    except Exception as e:
        print(f"   ❌ CSV輸出失敗: {e}")
        return False
    
    # 測試驗證功能
    print("\n✅ 測試驗證功能...")
    
    # 建立測試特徵
    test_features = {
        'page_count': 1,
        'file_size_mb': 0.1,
        'expected_question_count': 3
    }
    
    # 測試驗證
    from pdf_to_csv import validate_questions
    validation_result = validate_questions(test_questions, test_features)
    validation_result.print_result()
    
    # 清理臨時檔案
    if os.path.exists(temp_answer_file):
        os.remove(temp_answer_file)
    if os.path.exists(temp_corrected_file):
        os.remove(temp_corrected_file)
    
    print("\n🎉 答案辨識功能測試完成！")
    return True

def test_answer_validation():
    """測試答案驗證功能"""
    
    print("\n🛡️ 測試答案驗證功能")
    print("="*50)
    
    # 測試有效答案
    print("📝 測試有效答案...")
    valid_questions = [
        {
            '題號': '1',
            '題目': '測試題目',
            '選項A': 'A選項',
            '選項B': 'B選項',
            '選項C': 'C選項',
            '選項D': 'D選項',
            '題型': '選擇題',
            '正確答案': 'A',
            '更正答案': 'B'
        }
    ]
    
    from pdf_to_csv import validate_questions
    result = validate_questions(valid_questions, {})
    result.print_result()
    
    # 測試無效答案
    print("\n📝 測試無效答案...")
    invalid_questions = [
        {
            '題號': '1',
            '題目': '測試題目',
            '選項A': 'A選項',
            '選項B': 'B選項',
            '選項C': 'C選項',
            '選項D': 'D選項',
            '題型': '選擇題',
            '正確答案': 'X',  # 無效答案
            '更正答案': 'Y'   # 無效答案
        }
    ]
    
    result = validate_questions(invalid_questions, {})
    result.print_result()
    
    print("✅ 答案驗證功能測試完成")

if __name__ == "__main__":
    success = test_answer_detection()
    test_answer_validation()
    
    if success:
        print("\n🎉 所有測試完成！")
        sys.exit(0)
    else:
        print("\n❌ 測試失敗")
        sys.exit(1)