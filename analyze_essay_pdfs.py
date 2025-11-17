#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分析申論題PDF的特徵
"""

import os
import sys
import json

sys.path.insert(0, '/home/user/oldtest')

from src.core.enhanced_pdf_processor import EnhancedPDFProcessor

def analyze_failed_pdfs():
    """分析失敗的PDF，找出申論題特徵"""

    # 從測試結果中讀取失敗案例
    with open('batch_test_results.json', 'r', encoding='utf-8') as f:
        results = json.load(f)

    failed_cases = [r for r in results['results'] if not r['success']]

    print(f"================================================================================")
    print(f"分析 {len(failed_cases)} 個失敗案例")
    print(f"================================================================================\n")

    processor = EnhancedPDFProcessor()
    essay_features = []

    for i, case in enumerate(failed_cases[:5], 1):  # 只分析前5個
        name = case['name']
        subject = case['subject']
        pdf_path = f"考選部考古題完整庫/民國114年/{name}/試題.pdf"

        if not os.path.exists(pdf_path):
            continue

        print(f"[{i}/5] 分析: {subject}")
        print(f"  PDF: {pdf_path}")

        # 提取文本
        text = processor.extract_text(pdf_path)

        # 分析文本特徵
        features = analyze_text_features(text, subject)
        essay_features.append(features)

        # 顯示前500字元
        print(f"\n  前500字元:")
        print(f"  {'-'*70}")
        print(f"  {text[:500]}")
        print(f"  {'-'*70}\n")

        # 顯示特徵
        print(f"  特徵分析:")
        for key, value in features.items():
            print(f"    {key}: {value}")
        print()

    # 統計共同特徵
    print(f"================================================================================")
    print(f"申論題共同特徵")
    print(f"================================================================================\n")

    summarize_features(essay_features)

def analyze_text_features(text: str, subject: str) -> dict:
    """分析文本特徵"""
    import re

    features = {
        '科目': subject,
        '字數': len(text),
        '包含「一、」': '一、' in text or '一.' in text,
        '包含「二、」': '二、' in text or '二.' in text,
        '包含「三、」': '三、' in text or '三.' in text,
        '包含「申論題」': '申論題' in text or '申論' in text,
        '包含「試述」': '試述' in text,
        '包含「請說明」': '請說明' in text or '說明' in text,
        '包含「請論述」': '請論述' in text or '論述' in text,
        '包含「請分析」': '請分析' in text or '分析' in text,
        '包含「請比較」': '請比較' in text or '比較' in text,
        '包含「（25分）」': '25分' in text or '20分' in text or '30分' in text,
        '題號格式（數字句點）': bool(re.search(r'^[一二三四五]\s*[、.]', text, re.MULTILINE)),
        '選擇題標記（1 2 3）': bool(re.search(r'^\d+\s+\S', text, re.MULTILINE)),
        '選項標記（A B C D）': bool(re.search(r'[ABCD][.、)]\s', text)),
    }

    return features

def summarize_features(features_list: list):
    """統計共同特徵"""

    if not features_list:
        print("沒有特徵數據")
        return

    # 統計每個特徵出現的次數
    feature_counts = {}
    total = len(features_list)

    for features in features_list:
        for key, value in features.items():
            if key == '科目' or key == '字數':
                continue
            if key not in feature_counts:
                feature_counts[key] = 0
            if value:
                feature_counts[key] += 1

    # 按出現頻率排序
    sorted_features = sorted(feature_counts.items(), key=lambda x: x[1], reverse=True)

    print("特徵出現頻率:")
    print(f"{'特徵':<30} {'次數':<10} {'百分比'}")
    print(f"{'-'*60}")
    for feature, count in sorted_features:
        percentage = (count / total) * 100
        marker = "🔥" if percentage >= 80 else "✓" if percentage >= 50 else " "
        print(f"{marker} {feature:<28} {count}/{total:<8} {percentage:.1f}%")

    print(f"\n建議偵測規則:")
    print(f"  如果同時滿足以下條件，判定為申論題:")
    for feature, count in sorted_features:
        if count / total >= 0.8:  # 80%以上出現
            print(f"    ✓ {feature}")

if __name__ == '__main__':
    analyze_failed_pdfs()
