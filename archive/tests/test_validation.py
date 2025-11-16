#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試PDF轉CSV的驗證機制
"""

import os
import sys
from pdf_to_csv import validate_questions, ValidationResult, PDFFeatureAnalyzer

def test_validation_mechanisms():
    """測試各種驗證機制"""
    
    print("🔍 測試驗證機制")
    print("="*50)
    
    # 測試1: 正常題目
    print("\n✅ 測試1: 正常題目")
    normal_questions = [
        {
            '題號': '1',
            '題目': '這是一個正常的測試題目，內容足夠長度',
            '選項A': '選項A內容',
            '選項B': '選項B內容', 
            '選項C': '選項C內容',
            '選項D': '選項D內容',
            '題型': '選擇題'
        }
    ]
    
    features = {'expected_question_count': 1}
    result = validate_questions(normal_questions, features)
    result.print_result()
    
    # 測試2: 題號問題
    print("\n❌ 測試2: 題號問題")
    invalid_numbering = [
        {
            '題號': '2',  # 不從1開始
            '題目': '這是一個測試題目',
            '選項A': 'A', '選項B': 'B', '選項C': 'C', '選項D': 'D',
            '題型': '選擇題'
        },
        {
            '題號': '2',  # 重複題號
            '題目': '這是另一個測試題目',
            '選項A': 'A', '選項B': 'B', '選項C': 'C', '選項D': 'D',
            '題型': '選擇題'
        }
    ]
    
    result = validate_questions(invalid_numbering, {'expected_question_count': 2})
    result.print_result()
    
    # 測試3: 題目內容問題
    print("\n❌ 測試3: 題目內容問題")
    invalid_content = [
        {
            '題號': '1',
            '題目': '',  # 空題目
            '選項A': 'A', '選項B': 'B', '選項C': 'C', '選項D': 'D',
            '題型': '選擇題'
        },
        {
            '題號': '2',
            '題目': '短',  # 題目太短
            '選項A': 'A', '選項B': 'B', '選項C': 'C', '選項D': 'D',
            '題型': '選擇題'
        }
    ]
    
    result = validate_questions(invalid_content, {'expected_question_count': 2})
    result.print_result()
    
    # 測試4: 選項缺失
    print("\n❌ 測試4: 選項缺失")
    missing_options = [
        {
            '題號': '1',
            '題目': '這是一個測試題目',
            '選項A': 'A',
            '選項B': '',  # 缺失選項B
            '選項C': 'C',
            '選項D': 'D',
            '題型': '選擇題'
        }
    ]
    
    result = validate_questions(missing_options, {'expected_question_count': 1})
    result.print_result()
    
    # 測試5: 題數不符
    print("\n❌ 測試5: 題數不符")
    wrong_count = [
        {
            '題號': '1',
            '題目': '這是一個測試題目',
            '選項A': 'A', '選項B': 'B', '選項C': 'C', '選項D': 'D',
            '題型': '選擇題'
        }
    ]
    
    result = validate_questions(wrong_count, {'expected_question_count': 5})
    result.print_result()
    
    # 測試6: 混合題型
    print("\n✅ 測試6: 混合題型")
    mixed_types = [
        {
            '題號': '1',
            '題目': '這是一個選擇題',
            '選項A': 'A', '選項B': 'B', '選項C': 'C', '選項D': 'D',
            '題型': '選擇題'
        },
        {
            '題號': '2',
            '題目': '這是一個問答題，請詳細說明你的觀點',
            '選項A': '', '選項B': '', '選項C': '', '選項D': '',
            '題型': '問答題'
        }
    ]
    
    result = validate_questions(mixed_types, {'expected_question_count': 2})
    result.print_result()
    
    print("\n✅ 驗證機制測試完成")

def test_pdf_analysis():
    """測試PDF分析功能"""
    
    print("\n📄 測試PDF分析功能")
    print("="*50)
    
    # 測試存在的PDF
    test_pdf = "test_pdfs/測試考古題_民國114年_警察特考_行政警察_國文.pdf"
    if os.path.exists(test_pdf):
        print(f"📄 分析檔案: {test_pdf}")
        features = PDFFeatureAnalyzer.analyze_pdf(test_pdf)
        print(f"   頁數: {features['page_count']}")
        print(f"   檔案大小: {features['file_size_mb']:.2f} MB")
        print(f"   預期題數: {features.get('expected_question_count', '未檢測到')}")
    else:
        print("❌ 測試PDF不存在")
    
    # 測試不存在的PDF
    print("\n📄 測試不存在的PDF")
    non_existent = "不存在的檔案.pdf"
    features = PDFFeatureAnalyzer.analyze_pdf(non_existent)
    print(f"   頁數: {features['page_count']}")
    print(f"   檔案大小: {features['file_size_mb']:.2f} MB")
    print(f"   預期題數: {features.get('expected_question_count', '未檢測到')}")

def test_file_filtering():
    """測試檔案過濾功能"""
    
    print("\n🔍 測試檔案過濾功能")
    print("="*50)
    
    from pdf_to_csv import should_skip_file, is_answer_file
    
    # 測試檔名過濾
    test_files = [
        "民國114年_警察特考_國文.pdf",  # 正常檔案
        "民國114年_警察特考_國文_答案.pdf",  # 答案檔案
        "民國114年_警察特考_國文_解答.pdf",  # 解答檔案
        "民國114年_警察特考_國文_更正答案.pdf",  # 更正答案檔案
        "民國114年_警察特考_國文_Answer.pdf",  # 英文答案檔案
    ]
    
    print("📁 檔名過濾測試:")
    for filename in test_files:
        should_skip = should_skip_file(filename)
        print(f"   {filename}: {'跳過' if should_skip else '處理'}")
    
    # 測試內容過濾
    print("\n📄 內容過濾測試:")
    test_pdf = "test_pdfs/測試考古題_民國114年_警察特考_行政警察_國文.pdf"
    if os.path.exists(test_pdf):
        is_answer = is_answer_file(test_pdf)
        print(f"   {test_pdf}: {'答案檔案' if is_answer else '試題檔案'}")

if __name__ == "__main__":
    test_validation_mechanisms()
    test_pdf_analysis()
    test_file_filtering()
    
    print("\n🎉 所有驗證測試完成！")