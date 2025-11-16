#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
sys.path.append('src')

from src.processors.archaeology_processor import ArchaeologyProcessor

def test_single_category(category_name):
    """測試單個類別"""
    print(f"=== 測試類別: {category_name} ===")
    
    processor = ArchaeologyProcessor(use_enhanced=True)
    base_dir = f"114年考古題/民國114年/民國114年_警察特考/{category_name}"
    
    if not os.path.exists(base_dir):
        print(f"錯誤：找不到目錄 {base_dir}")
        return {}
    
    results = {}
    total_subjects = 0
    successful_subjects = 0
    total_questions = 0
    
    for subject in sorted(os.listdir(base_dir)):
        subject_path = os.path.join(base_dir, subject)
        if not os.path.isdir(subject_path):
            continue
        
        question_pdf = os.path.join(subject_path, "試題.pdf")
        if not os.path.exists(question_pdf):
            print(f"  ⚠️ {subject}: 未找到試題.pdf")
            continue
        
        print(f"  📄 {subject}")
        try:
            result = processor.process_pdf(question_pdf)
            success = result.get('success', False)
            question_count = result.get('questions_count', 0)
            
            results[subject] = {
                'success': success,
                'question_count': question_count,
                'error': None
            }
            
            total_subjects += 1
            if success:
                successful_subjects += 1
                total_questions += question_count
                print(f"    → ✅ 成功: {question_count} 題")
            else:
                print(f"    → ❌ 失敗")
        except Exception as e:
            results[subject] = {
                'success': False,
                'question_count': 0,
                'error': str(e)
            }
            total_subjects += 1
            print(f"    → ❌ 錯誤: {str(e)}")
    
    print(f"\n{category_name} 完成: {successful_subjects}/{total_subjects} 成功, {total_questions} 題")
    return results

def test_selected_categories():
    """測試選定的類別"""
    # 先測試幾個關鍵類別
    categories = [
        "資訊管理",  # 已知100%成功
        "交通警察_交通",
        "公共安全", 
        "刑事警察"
    ]
    
    all_results = {}
    total_subjects = 0
    total_successful = 0
    total_questions = 0
    
    for category in categories:
        results = test_single_category(category)
        all_results[category] = results
        
        category_subjects = len(results)
        category_successful = sum(1 for r in results.values() if r['success'])
        category_questions = sum(r['question_count'] for r in results.values() if r['success'])
        
        total_subjects += category_subjects
        total_successful += category_successful
        total_questions += category_questions
    
    print(f"\n=== 總計 ===")
    print(f"測試類別: {len(categories)}")
    print(f"總科目數: {total_subjects}")
    print(f"成功科目數: {total_successful}")
    print(f"成功率: {total_successful/total_subjects*100:.1f}%")
    print(f"總題數: {total_questions}")
    
    return all_results

if __name__ == "__main__":
    test_selected_categories()
