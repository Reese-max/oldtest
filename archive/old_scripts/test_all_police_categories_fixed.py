#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
sys.path.append('src')

from src.processors.archaeology_processor import ArchaeologyProcessor

def test_single_pdf(pdf_path, processor):
    """測試單個PDF的題目提取"""
    try:
        result = processor.process_pdf(pdf_path)
        return {
            'success': result.get('success', False),
            'question_count': result.get('questions_count', 0),
            'statistics': result.get('statistics', {}),
            'error': None
        }
    except Exception as e:
        return {
            'success': False,
            'question_count': 0,
            'statistics': {},
            'error': str(e)
        }

def test_all_police_categories():
    """測試所有警察特考類別"""
    print("=== 民國114年警察特考全面測試 ===")
    
    # 初始化處理器
    processor = ArchaeologyProcessor(use_enhanced=True)
    
    base_dir = "114年考古題/民國114年/民國114年_警察特考"
    
    if not os.path.exists(base_dir):
        print(f"錯誤：找不到目錄 {base_dir}")
        return
    
    results = {}
    total_subjects = 0
    successful_subjects = 0
    total_questions = 0
    
    # 遍歷所有類別
    for category in sorted(os.listdir(base_dir)):
        category_path = os.path.join(base_dir, category)
        if not os.path.isdir(category_path):
            continue
        
        print(f"\n=== 測試類別: {category} ===")
        results[category] = {}
        
        # 遍歷該類別下的所有科目
        for subject in sorted(os.listdir(category_path)):
            subject_path = os.path.join(category_path, subject)
            if not os.path.isdir(subject_path):
                continue
            
            # 查找試題PDF
            question_pdf = os.path.join(subject_path, "試題.pdf")
            if not os.path.exists(question_pdf):
                print(f"  ⚠️ {subject}: 未找到試題.pdf")
                continue
            
            print(f"  📄 {subject}")
            result = test_single_pdf(question_pdf, processor)
            results[category][subject] = result
            
            total_subjects += 1
            if result['success']:
                successful_subjects += 1
                total_questions += result['question_count']
                print(f"    → ✅ 成功: {result['question_count']} 題")
            else:
                print(f"    → ❌ 失敗: {result['error']}")
    
    # 生成測試報告
    generate_test_report(results, total_subjects, successful_subjects, total_questions)
    
    print(f"\n=== 測試完成 ===")
    print(f"總科目數: {total_subjects}")
    print(f"成功科目數: {successful_subjects}")
    print(f"成功率: {successful_subjects/total_subjects*100:.1f}%")
    print(f"總題數: {total_questions}")

def generate_test_report(results, total_subjects, successful_subjects, total_questions):
    """生成測試報告"""
    report_path = 'test_output/民國114年警察特考_完整測試報告.md'
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("# 民國114年警察特考完整測試報告\n\n")
        f.write(f"**測試時間**: {os.popen('date').read().strip()}\n")
        f.write(f"**總科目數**: {total_subjects}\n")
        f.write(f"**成功科目數**: {successful_subjects}\n")
        f.write(f"**成功率**: {successful_subjects/total_subjects*100:.1f}%\n")
        f.write(f"**總題數**: {total_questions}\n\n")
        
        f.write("## 各類別詳細結果\n\n")
        for category, subjects in results.items():
            f.write(f"### {category}\n\n")
            f.write("| 科目 | 狀態 | 題數 | 錯誤信息 |\n")
            f.write("|------|------|------|----------|\n")
            
            for subject, result in subjects.items():
                status = "✅ 成功" if result['success'] else "❌ 失敗"
                question_count = result['question_count']
                error = result['error'] or ""
                f.write(f"| {subject} | {status} | {question_count} | {error} |\n")
            
            f.write("\n")
        
        # 統計各類別成功率
        f.write("## 各類別成功率統計\n\n")
        f.write("| 類別 | 總科目 | 成功科目 | 成功率 | 總題數 |\n")
        f.write("|------|--------|----------|--------|--------|\n")
        
        for category, subjects in results.items():
            total = len(subjects)
            successful = sum(1 for result in subjects.values() if result['success'])
            success_rate = successful/total*100 if total > 0 else 0
            category_questions = sum(result['question_count'] for result in subjects.values() if result['success'])
            f.write(f"| {category} | {total} | {successful} | {success_rate:.1f}% | {category_questions} |\n")
        
        # 識別問題科目
        f.write("\n## 問題科目分析\n\n")
        problem_subjects = []
        for category, subjects in results.items():
            for subject, result in subjects.items():
                if not result['success']:
                    problem_subjects.append({
                        'category': category,
                        'subject': subject,
                        'error': result['error']
                    })
        
        if problem_subjects:
            f.write("### 失敗科目列表\n\n")
            for item in problem_subjects:
                f.write(f"- **{item['category']} - {item['subject']}**: {item['error']}\n")
        else:
            f.write("### 所有科目均成功處理！\n")
    
    print(f"測試報告已保存至: {report_path}")

if __name__ == "__main__":
    test_all_police_categories()
