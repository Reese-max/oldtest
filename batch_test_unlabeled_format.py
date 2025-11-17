#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量測試無標籤格式支援
測試考選部考古題完整庫中的所有PDF
"""

import sys
import os
import json
from pathlib import Path
from datetime import datetime
from collections import defaultdict

sys.path.insert(0, '/home/user/oldtest')

from src.processors.archaeology_processor import ArchaeologyProcessor
from src.core.enhanced_pdf_processor import EnhancedPDFProcessor
from src.core.no_label_question_parser import NoLabelQuestionParser


def find_all_test_pdfs(base_path):
    """查找所有試題PDF"""
    pdf_files = []
    for pdf_path in Path(base_path).rglob("試題.pdf"):
        # 查找對應的答案PDF
        parent_dir = pdf_path.parent
        answer_path = parent_dir / "答案.pdf"

        # 提取科目信息
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


def test_single_pdf(pdf_info, output_base_dir='batch_test_output'):
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
        'processing_time': 0,
        'pdf_quality': 0.0,
        'parser_used': None
    }

    try:
        start_time = datetime.now()

        # 創建處理器
        processor = ArchaeologyProcessor()

        # 先測試PDF提取質量
        pdf_processor = EnhancedPDFProcessor()
        extraction_result = pdf_processor.extract_with_best_method(pdf_info['pdf_path'])
        result['pdf_quality'] = extraction_result.get('quality', 0.0)

        # 測試題目解析
        text = extraction_result['text']
        parser = NoLabelQuestionParser()
        questions = parser.parse_no_label_questions(text)

        result['questions_count'] = len(questions)
        result['parser_used'] = 'NoLabelQuestionParser'

        # 如果有答案PDF，提取答案
        if pdf_info['answer_path']:
            answer_text = pdf_processor.extract_text(pdf_info['answer_path'])
            from src.core.answer_processor import AnswerProcessor
            answer_proc = AnswerProcessor()
            answers = answer_proc.extract_answers(answer_text)
            result['answers_count'] = len(answers)

            # 計算答案對應率
            if questions and answers:
                matched = 0
                for q in questions:
                    q_num = str(q.get('題號', ''))
                    if q_num in answers:
                        matched += 1
                result['match_rate'] = (matched / len(questions)) * 100 if questions else 0

        # 判斷成功
        if result['questions_count'] > 0:
            result['success'] = True

            # 檢查題目質量
            if result['questions_count'] < 10:
                result['warnings'].append(f"題目數量較少: {result['questions_count']}題")

            # 檢查答案對應
            if pdf_info['answer_path'] and result['match_rate'] < 80:
                result['warnings'].append(f"答案對應率較低: {result['match_rate']:.1f}%")
        else:
            result['errors'].append("未解析到任何題目")

        end_time = datetime.now()
        result['processing_time'] = (end_time - start_time).total_seconds()

    except Exception as e:
        result['errors'].append(str(e))
        result['success'] = False

    return result


def main():
    print("="*80)
    print("🧪 考選部官方格式批量測試")
    print("="*80)
    print()

    # 查找所有PDF
    base_path = "考選部考古題完整庫/民國114年"
    print(f"📁 掃描目錄: {base_path}")
    pdf_files = find_all_test_pdfs(base_path)
    print(f"✅ 找到 {len(pdf_files)} 個試題PDF")
    print()

    # 按考試類型分組
    by_exam_type = defaultdict(list)
    for pdf in pdf_files:
        by_exam_type[pdf['exam_type']].append(pdf)

    print("📊 考試類型分布:")
    for exam_type, pdfs in sorted(by_exam_type.items()):
        print(f"  {exam_type}: {len(pdfs)} 個")
    print()

    # 批量測試
    print("="*80)
    print("🚀 開始批量測試")
    print("="*80)
    print()

    results = []
    total = len(pdf_files)

    for i, pdf_info in enumerate(pdf_files, 1):
        print(f"[{i}/{total}] 測試: {pdf_info['full_name']}")
        print(f"  PDF: {pdf_info['pdf_path']}")

        result = test_single_pdf(pdf_info)
        results.append(result)

        if result['success']:
            print(f"  ✅ 成功: {result['questions_count']} 題")
            if result['answers_count'] > 0:
                print(f"     答案: {result['answers_count']} 個 (對應率: {result['match_rate']:.1f}%)")
            if result['warnings']:
                for warn in result['warnings']:
                    print(f"     ⚠️  {warn}")
        else:
            print(f"  ❌ 失敗: {', '.join(result['errors'])}")

        print(f"  處理時間: {result['processing_time']:.2f}秒")
        print()

    # 生成統計報告
    print("="*80)
    print("📊 測試統計")
    print("="*80)
    print()

    success_count = sum(1 for r in results if r['success'])
    success_rate = (success_count / total * 100) if total > 0 else 0

    total_questions = sum(r['questions_count'] for r in results)
    avg_questions = total_questions / success_count if success_count > 0 else 0

    total_answers = sum(r['answers_count'] for r in results)
    avg_match_rate = sum(r['match_rate'] for r in results if r['match_rate'] > 0) / len([r for r in results if r['match_rate'] > 0]) if any(r['match_rate'] > 0 for r in results) else 0

    print(f"總測試數: {total}")
    print(f"成功數: {success_count}")
    print(f"失敗數: {total - success_count}")
    print(f"成功率: {success_rate:.1f}%")
    print()
    print(f"總題數: {total_questions}")
    print(f"平均題數: {avg_questions:.1f} 題/PDF")
    print(f"總答案數: {total_answers}")
    print(f"平均答案對應率: {avg_match_rate:.1f}%")
    print()

    # 按考試類型統計
    print("按考試類型統計:")
    for exam_type in sorted(by_exam_type.keys()):
        exam_results = [r for r in results if r['exam_type'] == exam_type]
        exam_success = sum(1 for r in exam_results if r['success'])
        exam_total = len(exam_results)
        exam_rate = (exam_success / exam_total * 100) if exam_total > 0 else 0
        exam_questions = sum(r['questions_count'] for r in exam_results)

        print(f"  {exam_type}:")
        print(f"    測試數: {exam_total}")
        print(f"    成功率: {exam_rate:.1f}% ({exam_success}/{exam_total})")
        print(f"    總題數: {exam_questions}")
    print()

    # 列出失敗的案例
    failed_results = [r for r in results if not r['success']]
    if failed_results:
        print("❌ 失敗案例:")
        for r in failed_results:
            print(f"  {r['name']}")
            for err in r['errors']:
                print(f"    錯誤: {err}")
        print()

    # 列出警告
    warned_results = [r for r in results if r['warnings']]
    if warned_results:
        print("⚠️  警告案例:")
        for r in warned_results:
            print(f"  {r['name']}")
            for warn in r['warnings']:
                print(f"    {warn}")
        print()

    # 保存詳細結果
    output_file = "batch_test_results.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            'test_time': datetime.now().isoformat(),
            'total': total,
            'success': success_count,
            'success_rate': success_rate,
            'total_questions': total_questions,
            'total_answers': total_answers,
            'avg_match_rate': avg_match_rate,
            'results': results
        }, f, ensure_ascii=False, indent=2)

    print(f"📄 詳細結果已保存: {output_file}")
    print()

    # 最終評估
    print("="*80)
    print("✅ 最終評估")
    print("="*80)
    print()

    if success_rate >= 90:
        print("🎉 優秀！系統表現優異")
        rating = "⭐⭐⭐⭐⭐"
    elif success_rate >= 75:
        print("✅ 良好！系統表現穩定")
        rating = "⭐⭐⭐⭐☆"
    elif success_rate >= 60:
        print("⚠️  一般，仍有改進空間")
        rating = "⭐⭐⭐☆☆"
    else:
        print("❌ 需要改進")
        rating = "⭐⭐☆☆☆"

    print(f"系統評級: {rating}")
    print(f"成功率: {success_rate:.1f}%")
    print(f"處理能力: {total_questions} 題")
    print()


if __name__ == "__main__":
    main()
