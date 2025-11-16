#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
sys.path.append('src')

from src.processors.archaeology_processor import ArchaeologyProcessor

def test_single_category(category_name):
    """測試單個類別的所有科目"""
    print(f"=== 測試類別: {category_name} ===")
    
    # 初始化處理器
    processor = ArchaeologyProcessor(use_enhanced=True)
    
    base_dir = f"114年考古題/民國114年/民國114年_警察特考/{category_name}"
    
    if not os.path.exists(base_dir):
        print(f"錯誤：找不到目錄 {base_dir}")
        return
    
    results = {}
    total_subjects = 0
    successful_subjects = 0
    total_questions = 0
    
    # 遍歷該類別下的所有科目
    for subject in sorted(os.listdir(base_dir)):
        subject_path = os.path.join(base_dir, subject)
        if not os.path.isdir(subject_path):
            continue
        
        # 查找試題PDF
        question_pdf = os.path.join(subject_path, "試題.pdf")
        if not os.path.exists(question_pdf):
            print(f"  ⚠️ {subject}: 未找到試題.pdf")
            continue
        
        print(f"  📄 {subject}")
        try:
            questions = processor.process_pdf(question_pdf)
            results[subject] = {
                'success': True,
                'question_count': len(questions),
                'questions': questions,
                'error': None
            }
            successful_subjects += 1
            total_questions += len(questions)
            print(f"    → ✅ 成功: {len(questions)} 題")
        except Exception as e:
            results[subject] = {
                'success': False,
                'question_count': 0,
                'questions': [],
                'error': str(e)
            }
            print(f"    → ❌ 失敗: {str(e)}")
        
        total_subjects += 1
    
    # 生成該類別的報告
    generate_category_report(category_name, results, total_subjects, successful_subjects, total_questions)
    
    print(f"\n=== {category_name} 測試完成 ===")
    print(f"總科目數: {total_subjects}")
    print(f"成功科目數: {successful_subjects}")
    print(f"成功率: {successful_subjects/total_subjects*100:.1f}%")
    print(f"總題數: {total_questions}")
    
    return results

def generate_category_report(category_name, results, total_subjects, successful_subjects, total_questions):
    """生成單個類別的測試報告"""
    os.makedirs('test_output', exist_ok=True)
    report_path = f'test_output/{category_name}_測試報告.md'
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(f"# {category_name} 測試報告\n\n")
        f.write(f"**測試時間**: {os.popen('date').read().strip()}\n")
        f.write(f"**總科目數**: {total_subjects}\n")
        f.write(f"**成功科目數**: {successful_subjects}\n")
        f.write(f"**成功率**: {successful_subjects/total_subjects*100:.1f}%\n")
        f.write(f"**總題數**: {total_questions}\n\n")
        
        f.write("## 科目詳細結果\n\n")
        f.write("| 科目 | 狀態 | 題數 | 錯誤信息 |\n")
        f.write("|------|------|------|----------|\n")
        
        for subject, result in results.items():
            status = "✅ 成功" if result['success'] else "❌ 失敗"
            question_count = result['question_count']
            error = result['error'] or ""
            f.write(f"| {subject} | {status} | {question_count} | {error} |\n")
        
        # 問題科目分析
        problem_subjects = [subject for subject, result in results.items() if not result['success']]
        if problem_subjects:
            f.write("\n## 問題科目\n\n")
            for subject in problem_subjects:
                f.write(f"- **{subject}**: {results[subject]['error']}\n")
        else:
            f.write("\n## 所有科目均成功處理！\n")
    
    print(f"報告已保存至: {report_path}")

if __name__ == "__main__":
    # 測試第一個類別：資訊管理
    test_single_category("資訊管理")
