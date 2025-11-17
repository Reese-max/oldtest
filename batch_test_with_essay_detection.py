#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量測試（含申論題偵測）
測試考選部考古題完整庫中的所有PDF，並在失敗時偵測是否為申論題
"""

import sys
import os
import json
from pathlib import Path
from datetime import datetime
from collections import defaultdict

sys.path.insert(0, '/home/user/oldtest')

from src.processors.archaeology_processor import ArchaeologyProcessor


def find_all_test_pdfs(base_path):
    """查找所有試題PDF"""
    pdf_files = []
    for pdf_path in Path(base_path).rglob("試題.pdf"):
        parent_dir = pdf_path.parent
        answer_path = parent_dir / "答案.pdf"

        parts = str(pdf_path.parent).split('/')
        exam_type = parts[-3] if len(parts) >= 3 else "未知"
        position = parts[-2] if len(parts) >= 2 else "未知"
        subject = parts[-1] if len(parts) >= 1 else "未知"

        pdf_files.append({
            'exam_type': exam_type,
            'position': position,
            'subject': subject,
            'pdf_path': str(pdf_path),
            'answer_path': str(answer_path) if answer_path.exists() else None,
            'full_name': f"{exam_type}/{position}/{subject}"
        })

    return pdf_files


def test_single_pdf(pdf_info, processor):
    """測試單一PDF"""
    result = {
        'name': pdf_info['full_name'],
        'subject': pdf_info['subject'],
        'exam_type': pdf_info['exam_type'],
        'position': pdf_info['position'],
        'success': False,
        'questions_count': 0,
        'answers_count': 0,
        'match_rate': 0.0,
        'errors': [],
        'warnings': [],
        'essay_detection': None,  # 申論題偵測結果
    }

    try:
        # 提取文本
        text = processor.pdf_processor.extract_text(pdf_info['pdf_path'])

        # 使用完整的解析流程（包含申論題偵測）
        questions = processor._parse_standard(text)

        if len(questions) >= 2:
            result['success'] = True
            result['questions_count'] = len(questions)
        else:
            # 解析失敗時，進行申論題偵測
            essay_result = processor.essay_detector.detect_essay_exam(text)
            result['essay_detection'] = essay_result

            if essay_result['is_essay']:
                result['errors'].append(
                    f"申論題試卷（信心度: {essay_result['confidence']:.1%}）"
                )
            else:
                result['errors'].append("未解析到足夠題目")

    except Exception as e:
        result['errors'].append(str(e))

    return result


def main():
    """主函數"""
    base_path = "考選部考古題完整庫/民國114年"

    print("=" * 80)
    print("🧪 批量測試（含申論題偵測）")
    print("=" * 80)
    print(f"\n📁 掃描目錄: {base_path}")

    pdf_files = find_all_test_pdfs(base_path)
    print(f"✅ 找到 {len(pdf_files)} 個試題PDF\n")

    # 分類統計
    exam_types = defaultdict(int)
    for pdf in pdf_files:
        exam_types[pdf['exam_type']] += 1

    print("📊 考試類型分布:")
    for exam_type, count in sorted(exam_types.items()):
        print(f"  {exam_type}: {count} 個")

    print("\n" + "=" * 80)
    print("🚀 開始批量測試")
    print("=" * 80 + "\n")

    # 初始化處理器
    processor = ArchaeologyProcessor(use_enhanced=True)

    results = []
    for i, pdf_info in enumerate(pdf_files, 1):
        print(f"[{i}/{len(pdf_files)}] 測試: {pdf_info['full_name']}")
        print(f"  PDF: {pdf_info['pdf_path']}")

        result = test_single_pdf(pdf_info, processor)
        results.append(result)

        if result['success']:
            print(f"  ✅ 成功: {result['questions_count']} 題")
        else:
            if result['essay_detection'] and result['essay_detection']['is_essay']:
                print(f"  📝 申論題試卷（信心度: {result['essay_detection']['confidence']:.1%}）")
            else:
                print(f"  ❌ 失敗: {', '.join(result['errors'])}")
        print()

    # 統計結果
    print("=" * 80)
    print("📊 統計結果")
    print("=" * 80 + "\n")

    total = len(results)
    success_count = sum(1 for r in results if r['success'])
    failed_count = total - success_count

    essay_count = sum(
        1 for r in results
        if not r['success'] and r['essay_detection'] and r['essay_detection']['is_essay']
    )

    unknown_count = failed_count - essay_count

    print(f"總測試數: {total}")
    print(f"  ✅ 選擇題成功: {success_count} ({success_count/total*100:.1f}%)")
    print(f"  📝 申論題識別: {essay_count} ({essay_count/total*100:.1f}%)")
    print(f"  ❌ 未識別失敗: {unknown_count} ({unknown_count/total*100:.1f}%)")
    print()

    # 按考試類型統計
    print("按考試類型統計:")
    print("-" * 80)

    by_exam_type = defaultdict(lambda: {'total': 0, 'success': 0, 'essay': 0, 'unknown': 0})
    for result in results:
        exam_type = result['exam_type']
        by_exam_type[exam_type]['total'] += 1

        if result['success']:
            by_exam_type[exam_type]['success'] += 1
        elif result['essay_detection'] and result['essay_detection']['is_essay']:
            by_exam_type[exam_type]['essay'] += 1
        else:
            by_exam_type[exam_type]['unknown'] += 1

    for exam_type, stats in sorted(by_exam_type.items()):
        total = stats['total']
        success = stats['success']
        essay = stats['essay']
        unknown = stats['unknown']

        print(f"{exam_type}:")
        print(f"  選擇題成功: {success}/{total} ({success/total*100:.1f}%)")
        print(f"  申論題識別: {essay}/{total} ({essay/total*100:.1f}%)")
        if unknown > 0:
            print(f"  未識別失敗: {unknown}/{total} ({unknown/total*100:.1f}%)")

    # 保存結果
    output = {
        'test_time': datetime.now().isoformat(),
        'total': total,
        'success': success_count,
        'essay_detected': essay_count,
        'unknown_failed': unknown_count,
        'success_rate': success_count / total if total > 0 else 0,
        'essay_detection_rate': essay_count / total if total > 0 else 0,
        'results': results
    }

    with open('batch_test_with_essay_detection.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print("\n結果已保存至: batch_test_with_essay_detection.json")

    # 最終評估
    print("\n" + "=" * 80)
    print("✅ 最終評估")
    print("=" * 80 + "\n")

    identified_rate = (success_count + essay_count) / total if total > 0 else 0

    print(f"總識別率: {identified_rate*100:.1%} （選擇題 + 申論題）")
    print(f"  - 選擇題處理: {success_count}/{total} ({success_count/total*100:.1f}%)")
    print(f"  - 申論題識別: {essay_count}/{total} ({essay_count/total*100:.1f}%)")
    print(f"  - 未識別: {unknown_count}/{total} ({unknown_count/total*100:.1f}%)")

    if identified_rate >= 0.95:
        print("\n🎉 優秀！系統能識別超過95%的試卷類型")
    elif identified_rate >= 0.85:
        print("\n✅ 良好！系統能識別超過85%的試卷類型")
    else:
        print("\n⚠️  需改進：仍有較多試卷無法識別")


if __name__ == '__main__':
    main()
