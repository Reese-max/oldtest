#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試申論題偵測功能
專門測試之前失敗的13個案例
"""

import sys
import os
import json
from pathlib import Path

sys.path.insert(0, '/home/user/oldtest')

from src.processors.archaeology_processor import ArchaeologyProcessor


def test_failed_cases():
    """測試之前失敗的案例"""

    # 從測試結果中讀取失敗案例
    with open('batch_test_results.json', 'r', encoding='utf-8') as f:
        results = json.load(f)

    failed_cases = [r for r in results['results'] if not r['success']]

    print(f"================================================================================")
    print(f"申論題偵測測試 - {len(failed_cases)} 個失敗案例")
    print(f"================================================================================\n")

    processor = ArchaeologyProcessor(use_enhanced=True)
    detection_results = []

    for i, case in enumerate(failed_cases, 1):
        name = case['name']
        subject = case['subject']
        exam_type = case.get('exam_type', '')
        position = case.get('position', '')

        pdf_path = f"考選部考古題完整庫/民國114年/{name}/試題.pdf"

        if not os.path.exists(pdf_path):
            print(f"[{i}/{len(failed_cases)}] 跳過（文件不存在）: {subject}")
            continue

        print(f"[{i}/{len(failed_cases)}] 測試: {subject}")
        print(f"  考試: {exam_type}")
        print(f"  職位: {position}")
        print(f"  PDF: {pdf_path}")

        # 提取文本
        text = processor.pdf_processor.extract_text(pdf_path)

        # 偵測申論題
        essay_result = processor.essay_detector.detect_essay_exam(text)

        # 記錄結果
        result = {
            'name': name,
            'subject': subject,
            'exam_type': exam_type,
            'position': position,
            'is_essay': essay_result['is_essay'],
            'confidence': essay_result['confidence'],
            'reason': essay_result['reason'],
            'features': essay_result['features']
        }
        detection_results.append(result)

        # 顯示結果
        if essay_result['is_essay']:
            print(f"  ✓ 偵測為申論題試卷")
            print(f"    信心度: {essay_result['confidence']:.2%}")
        else:
            print(f"  ✗ 未偵測為申論題")
            print(f"    信心度: {essay_result['confidence']:.2%}")

        print(f"  理由: {essay_result['reason']}")
        print()

    # 統計結果
    print(f"================================================================================")
    print(f"統計結果")
    print(f"================================================================================\n")

    total = len(detection_results)
    essay_count = sum(1 for r in detection_results if r['is_essay'])
    non_essay_count = total - essay_count

    print(f"總測試數: {total}")
    print(f"識別為申論題: {essay_count} ({essay_count/total*100:.1f}%)")
    print(f"未識別為申論題: {non_essay_count} ({non_essay_count/total*100:.1f}%)")
    print()

    # 顯示詳細分類
    print("詳細分類:")
    print("-" * 80)
    print(f"{'科目':<40} {'考試類型':<20} {'偵測結果':<15} {'信心度'}")
    print("-" * 80)

    for result in detection_results:
        subject = result['subject'][:38]
        exam = result['exam_type'].replace('民國114年_', '')[:18]
        detected = "✓ 申論題" if result['is_essay'] else "✗ 非申論題"
        confidence = f"{result['confidence']:.1%}"

        print(f"{subject:<40} {exam:<20} {detected:<15} {confidence}")

    # 保存結果
    with open('essay_detection_results.json', 'w', encoding='utf-8') as f:
        json.dump(detection_results, f, ensure_ascii=False, indent=2)

    print()
    print("結果已保存至: essay_detection_results.json")

    # 高信心度案例
    print()
    print("=" * 80)
    print("高信心度申論題案例 (>70%)")
    print("=" * 80)

    high_confidence = [r for r in detection_results if r['is_essay'] and r['confidence'] > 0.7]
    for result in high_confidence:
        print(f"  ✓ {result['subject']} ({result['confidence']:.1%})")
        features = result['features']
        print(f"     - 申論關鍵詞: {features['essay_keywords']['count']} 個")
        print(f"     - 分數標記: {features['score_marks']['count']} 個")
        print(f"     - 中文數字題號: {features['chinese_numbers']['count']} 個")

    # 低信心度案例
    print()
    print("=" * 80)
    print("低信心度或未識別案例 (<50%)")
    print("=" * 80)

    low_confidence = [r for r in detection_results if r['confidence'] < 0.5]
    for result in low_confidence:
        print(f"  ⚠️  {result['subject']} ({result['confidence']:.1%})")
        print(f"     {result['reason']}")


if __name__ == '__main__':
    test_failed_cases()
