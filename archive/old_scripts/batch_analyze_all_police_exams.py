#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
import sys
sys.path.append('src')

import pdfplumber
from src.processors.archaeology_processor import ArchaeologyProcessor

def analyze_pdf_structure(pdf_path):
    """分析單個PDF的結構"""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            text = ''.join([page.extract_text() or '' for page in pdf.pages])
        
        # 基本統計
        total_chars = len(text)
        total_lines = len(text.split('\n'))
        
        # 檢測題型特徵
        features = {
            'has_essay_section': '甲、申論題部分' in text or '申論題' in text,
            'has_test_section': '乙、測驗題部分' in text or '測驗題' in text,
            'has_essay_questions': any(f'第{i}題' in text for i in range(1, 11)),
            'has_choice_questions': any(f'{i}.' in text for i in range(1, 51)),
            'has_question_groups': '請依下文回答第' in text and '題至第' in text,
            'has_composition': '作文' in text,
            'has_english': 'English' in text or '英文' in text,
            'has_choice_symbols': any(symbol in text for symbol in ['', '', '', '']),
            'total_questions_mentioned': len([m for m in text.split() if m.isdigit() and 1 <= int(m) <= 100]),
        }
        
        # 估算題數
        estimated_questions = 0
        if features['has_essay_questions']:
            estimated_questions += 4  # 通常申論題4題
        if features['has_choice_questions']:
            estimated_questions += 20  # 通常選擇題20題
        if features['has_question_groups']:
            estimated_questions += 10  # 題組通常10題
        
        return {
            'total_chars': total_chars,
            'total_lines': total_lines,
            'features': features,
            'estimated_questions': estimated_questions,
            'text_preview': text[:500] if text else ''
        }
    except Exception as e:
        return {
            'error': str(e),
            'total_chars': 0,
            'total_lines': 0,
            'features': {},
            'estimated_questions': 0,
            'text_preview': ''
        }

def batch_analyze_all_police_exams():
    """批量分析所有警察特考科目"""
    base_dir = "114年考古題/民國114年/民國114年_警察特考"
    
    if not os.path.exists(base_dir):
        print(f"錯誤：找不到目錄 {base_dir}")
        return
    
    results = {}
    total_subjects = 0
    total_questions_estimated = 0
    
    # 遍歷所有類別
    for category in os.listdir(base_dir):
        category_path = os.path.join(base_dir, category)
        if not os.path.isdir(category_path):
            continue
        
        print(f"\n=== 分析類別: {category} ===")
        results[category] = {}
        
        # 遍歷該類別下的所有科目
        for subject in os.listdir(category_path):
            subject_path = os.path.join(category_path, subject)
            if not os.path.isdir(subject_path):
                continue
            
            # 查找試題PDF
            question_pdf = os.path.join(subject_path, "試題.pdf")
            if not os.path.exists(question_pdf):
                print(f"  ⚠️ {subject}: 未找到試題.pdf")
                continue
            
            print(f"  📄 {subject}")
            analysis = analyze_pdf_structure(question_pdf)
            results[category][subject] = analysis
            
            total_subjects += 1
            total_questions_estimated += analysis['estimated_questions']
            
            print(f"    → 預估題數: {analysis['estimated_questions']}")
            if 'error' in analysis:
                print(f"    → 錯誤: {analysis['error']}")
    
    # 保存結構分析結果
    os.makedirs('test_output', exist_ok=True)
    with open('test_output/全部警察特考_結構分析.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    # 生成統計報告
    generate_statistics_report(results, total_subjects, total_questions_estimated)
    
    print(f"\n=== 分析完成 ===")
    print(f"總科目數: {total_subjects}")
    print(f"總預估題數: {total_questions_estimated}")
    print(f"結果已保存至: test_output/全部警察特考_結構分析.json")

def generate_statistics_report(results, total_subjects, total_questions_estimated):
    """生成統計報告"""
    report_path = 'test_output/全部警察特考_統計報告.md'
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("# 民國114年警察特考全面結構分析報告\n\n")
        f.write(f"**分析時間**: {os.popen('date').read().strip()}\n")
        f.write(f"**總科目數**: {total_subjects}\n")
        f.write(f"**總預估題數**: {total_questions_estimated}\n\n")
        
        f.write("## 類別統計\n\n")
        for category, subjects in results.items():
            f.write(f"### {category}\n\n")
            f.write("| 科目 | 預估題數 | 特徵 |\n")
            f.write("|------|----------|------|\n")
            
            for subject, analysis in subjects.items():
                features = analysis.get('features', {})
                feature_list = []
                if features.get('has_essay_section'):
                    feature_list.append("申論")
                if features.get('has_test_section'):
                    feature_list.append("測驗")
                if features.get('has_composition'):
                    feature_list.append("作文")
                if features.get('has_question_groups'):
                    feature_list.append("題組")
                
                feature_str = ", ".join(feature_list) if feature_list else "未知"
                f.write(f"| {subject} | {analysis['estimated_questions']} | {feature_str} |\n")
            
            f.write("\n")
        
        f.write("## 格式特徵統計\n\n")
        format_stats = {
            '申論題': 0,
            '測驗題': 0,
            '混合格式': 0,
            '綜合格式': 0,
            '未知格式': 0
        }
        
        for category, subjects in results.items():
            for subject, analysis in subjects.items():
                features = analysis.get('features', {})
                if features.get('has_essay_section') and features.get('has_test_section'):
                    format_stats['綜合格式'] += 1
                elif features.get('has_essay_section'):
                    format_stats['申論題'] += 1
                elif features.get('has_test_section'):
                    format_stats['測驗題'] += 1
                elif features.get('has_composition'):
                    format_stats['混合格式'] += 1
                else:
                    format_stats['未知格式'] += 1
        
        for format_type, count in format_stats.items():
            f.write(f"- **{format_type}**: {count} 科目\n")
    
    print(f"統計報告已保存至: {report_path}")

if __name__ == "__main__":
    batch_analyze_all_police_exams()
