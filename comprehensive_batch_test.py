#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
綜合批量測試
測試試題解析、申論題偵測、答案提取和匹配率
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
    """查找所有試題PDF及對應的答案PDF"""
    pdf_files = []
    for pdf_path in Path(base_path).rglob("試題.pdf"):
        parent_dir = pdf_path.parent
        answer_path = parent_dir / "答案.pdf"
        corrected_answer_path = parent_dir / "更正答案.pdf"

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
            'corrected_answer_path': str(corrected_answer_path) if corrected_answer_path.exists() else None,
            'full_name': f"{exam_type}/{position}/{subject}"
        })

    return pdf_files


def test_single_pdf_comprehensive(pdf_info, processor):
    """綜合測試單一PDF（試題+答案）"""
    result = {
        'name': pdf_info['full_name'],
        'subject': pdf_info['subject'],
        'exam_type': pdf_info['exam_type'],
        'position': pdf_info['position'],
        'success': False,
        'questions_count': 0,
        'has_answer': False,
        'has_corrected_answer': False,
        'answers_count': 0,
        'corrected_answers_count': 0,
        'match_rate': 0.0,
        'errors': [],
        'warnings': [],
        'essay_detection': None,
        'processing_time': 0.0,
    }

    import time
    start_time = time.time()

    try:
        # 1. 提取試題文本
        text = processor.pdf_processor.extract_text(pdf_info['pdf_path'])

        # 2. 解析試題（包含申論題偵測）
        questions = processor._parse_standard(text)

        if len(questions) >= 2:
            result['success'] = True
            result['questions_count'] = len(questions)

            # 3. 提取答案（如果有答案PDF）
            answers = {}
            corrected_answers = {}

            if pdf_info['answer_path']:
                result['has_answer'] = True
                try:
                    # 提取答案PDF的文本
                    answer_text = processor.pdf_processor.extract_text(pdf_info['answer_path'])
                    # 從文本中提取答案
                    answers = processor.answer_processor.extract_answers(answer_text)
                    result['answers_count'] = len(answers)
                except Exception as e:
                    result['warnings'].append(f"答案提取失敗: {str(e)}")

            if pdf_info['corrected_answer_path']:
                result['has_corrected_answer'] = True
                try:
                    # 提取更正答案PDF的文本
                    corrected_answer_text = processor.pdf_processor.extract_text(pdf_info['corrected_answer_path'])
                    # 從文本中提取更正答案
                    corrected_answers = processor.answer_processor.extract_corrected_answers(corrected_answer_text)
                    result['corrected_answers_count'] = len(corrected_answers)
                except Exception as e:
                    result['warnings'].append(f"更正答案提取失敗: {str(e)}")

            # 4. 計算答案匹配率
            if answers:
                matched = 0
                for q in questions:
                    q_num = str(q.get('題號', ''))
                    if q_num and q_num in answers:
                        matched += 1
                result['match_rate'] = (matched / len(questions)) * 100 if questions else 0
        else:
            # 解析失敗時，進行申論題偵測
            essay_result = processor.essay_detector.detect_essay_exam(text)
            result['essay_detection'] = essay_result

            if essay_result['is_essay']:
                result['errors'].append(
                    f"申論題試卷（信心度: {essay_result['confidence']:.1%}）"
                )
                # 申論題也檢查是否有答案PDF
                if pdf_info['answer_path']:
                    result['has_answer'] = True
                    result['warnings'].append("申論題試卷，但存在答案PDF")
            else:
                result['errors'].append("未解析到足夠題目")

    except Exception as e:
        result['errors'].append(str(e))

    result['processing_time'] = time.time() - start_time
    return result


def main():
    """主函數"""
    base_path = "考選部考古題完整庫/民國114年"

    print("=" * 80)
    print("🧪 綜合批量測試（試題+答案+申論題偵測）")
    print("=" * 80)
    print(f"\n📁 掃描目錄: {base_path}")

    pdf_files = find_all_test_pdfs(base_path)
    print(f"✅ 找到 {len(pdf_files)} 個試題PDF\n")

    # 統計答案PDF
    with_answer = sum(1 for p in pdf_files if p['answer_path'])
    with_corrected = sum(1 for p in pdf_files if p['corrected_answer_path'])

    print("📊 答案PDF分布:")
    print(f"  有答案.pdf: {with_answer} 個")
    print(f"  有更正答案.pdf: {with_corrected} 個")
    print()

    # 分類統計
    exam_types = defaultdict(int)
    for pdf in pdf_files:
        exam_types[pdf['exam_type']] += 1

    print("📊 考試類型分布:")
    for exam_type, count in sorted(exam_types.items()):
        print(f"  {exam_type}: {count} 個")

    print("\n" + "=" * 80)
    print("🚀 開始綜合測試")
    print("=" * 80 + "\n")

    # 初始化處理器
    processor = ArchaeologyProcessor(use_enhanced=True)

    results = []
    for i, pdf_info in enumerate(pdf_files, 1):
        print(f"[{i}/{len(pdf_files)}] 測試: {pdf_info['full_name']}")
        print(f"  試題: {pdf_info['pdf_path']}")
        if pdf_info['answer_path']:
            print(f"  答案: ✓")
        if pdf_info['corrected_answer_path']:
            print(f"  更正答案: ✓")

        result = test_single_pdf_comprehensive(pdf_info, processor)
        results.append(result)

        if result['success']:
            print(f"  ✅ 成功: {result['questions_count']} 題", end="")
            if result['has_answer']:
                print(f" | 答案: {result['answers_count']} 個 ({result['match_rate']:.0f}%)", end="")
            if result['has_corrected_answer']:
                print(f" | 更正: {result['corrected_answers_count']} 個", end="")
            print()
        else:
            if result['essay_detection'] and result['essay_detection']['is_essay']:
                print(f"  📝 申論題試卷（信心度: {result['essay_detection']['confidence']:.1%}）", end="")
                if result['has_answer']:
                    print(f" | ⚠️ 有答案PDF", end="")
                print()
            else:
                print(f"  ❌ 失敗: {', '.join(result['errors'])}")

        if result['warnings']:
            for warning in result['warnings']:
                print(f"    ⚠️  {warning}")
        print()

    # ===========================
    # 統計結果
    # ===========================
    print("=" * 80)
    print("📊 綜合統計結果")
    print("=" * 80 + "\n")

    total = len(results)
    success_count = sum(1 for r in results if r['success'])
    failed_count = total - success_count

    essay_count = sum(
        1 for r in results
        if not r['success'] and r['essay_detection'] and r['essay_detection']['is_essay']
    )

    unknown_count = failed_count - essay_count

    # 答案統計
    success_with_answer = sum(1 for r in results if r['success'] and r['has_answer'])
    success_with_corrected = sum(1 for r in results if r['success'] and r['has_corrected_answer'])

    # 答案匹配率統計
    results_with_answers = [r for r in results if r['success'] and r['has_answer'] and r['answers_count'] > 0]
    avg_match_rate = sum(r['match_rate'] for r in results_with_answers) / len(results_with_answers) if results_with_answers else 0

    print("🎯 試題解析統計:")
    print(f"  總測試數: {total}")
    print(f"  ✅ 選擇題成功: {success_count} ({success_count/total*100:.1f}%)")
    print(f"  📝 申論題識別: {essay_count} ({essay_count/total*100:.1f}%)")
    print(f"  ❌ 未識別失敗: {unknown_count} ({unknown_count/total*100:.1f}%)")
    print()

    print("📋 答案可用性統計:")
    print(f"  成功解析且有答案: {success_with_answer}/{success_count} ({success_with_answer/success_count*100 if success_count > 0 else 0:.1f}%)")
    print(f"  成功解析且有更正答案: {success_with_corrected}/{success_count} ({success_with_corrected/success_count*100 if success_count > 0 else 0:.1f}%)")
    print(f"  平均答案匹配率: {avg_match_rate:.1f}%")
    print()

    # 按考試類型統計
    print("📊 按考試類型統計:")
    print("-" * 80)

    by_exam_type = defaultdict(lambda: {
        'total': 0, 'success': 0, 'essay': 0, 'unknown': 0,
        'with_answer': 0, 'with_corrected': 0, 'total_match_rate': 0, 'match_count': 0
    })

    for result in results:
        exam_type = result['exam_type']
        stats = by_exam_type[exam_type]
        stats['total'] += 1

        if result['success']:
            stats['success'] += 1
            if result['has_answer']:
                stats['with_answer'] += 1
                if result['match_rate'] > 0:
                    stats['total_match_rate'] += result['match_rate']
                    stats['match_count'] += 1
            if result['has_corrected_answer']:
                stats['with_corrected'] += 1
        elif result['essay_detection'] and result['essay_detection']['is_essay']:
            stats['essay'] += 1
        else:
            stats['unknown'] += 1

    for exam_type, stats in sorted(by_exam_type.items()):
        total = stats['total']
        success = stats['success']
        essay = stats['essay']
        unknown = stats['unknown']
        with_answer = stats['with_answer']
        avg_match = stats['total_match_rate'] / stats['match_count'] if stats['match_count'] > 0 else 0

        print(f"\n{exam_type}:")
        print(f"  選擇題成功: {success}/{total} ({success/total*100:.1f}%)")
        print(f"  申論題識別: {essay}/{total} ({essay/total*100:.1f}%)")
        if unknown > 0:
            print(f"  未識別失敗: {unknown}/{total} ({unknown/total*100:.1f}%)")
        if with_answer > 0:
            print(f"  有答案: {with_answer}/{success} ({with_answer/success*100 if success > 0 else 0:.1f}%)")
            print(f"  平均匹配率: {avg_match:.1f}%")

    # 保存結果
    output = {
        'test_time': datetime.now().isoformat(),
        'total': total,
        'success': success_count,
        'essay_detected': essay_count,
        'unknown_failed': unknown_count,
        'success_with_answer': success_with_answer,
        'success_with_corrected': success_with_corrected,
        'avg_match_rate': avg_match_rate,
        'results': results
    }

    with open('comprehensive_batch_test_results.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print("\n" + "=" * 80)
    print("💾 結果已保存")
    print("=" * 80)
    print(f"詳細結果: comprehensive_batch_test_results.json")

    # 最終評估
    print("\n" + "=" * 80)
    print("✅ 最終評估")
    print("=" * 80 + "\n")

    identified_rate = (success_count + essay_count) / total if total > 0 else 0

    print(f"🎯 試卷類型識別率: {identified_rate*100:.1f}%")
    print(f"   - 選擇題處理: {success_count}/{total} ({success_count/total*100:.1f}%)")
    print(f"   - 申論題識別: {essay_count}/{total} ({essay_count/total*100:.1f}%)")
    print(f"   - 未識別: {unknown_count}/{total} ({unknown_count/total*100:.1f}%)")
    print()

    if success_with_answer > 0:
        print(f"📋 答案處理能力:")
        print(f"   - 答案覆蓋率: {success_with_answer}/{success_count} ({success_with_answer/success_count*100 if success_count > 0 else 0:.1f}%)")
        print(f"   - 平均匹配率: {avg_match_rate:.1f}%")
        print()

    if identified_rate >= 0.95:
        print("🎉 優秀！系統能識別超過95%的試卷類型")
    elif identified_rate >= 0.85:
        print("✅ 良好！系統能識別超過85%的試卷類型")
    else:
        print("⚠️  需改進：仍有較多試卷無法識別")

    if avg_match_rate >= 95:
        print("🎉 答案匹配率優秀（>95%）")
    elif avg_match_rate >= 85:
        print("✅ 答案匹配率良好（>85%）")


if __name__ == '__main__':
    main()
