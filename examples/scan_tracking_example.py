#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
題目掃描追蹤示例
演示如何使用掃描追蹤系統確保每題都被掃描
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.processors.archaeology_processor import ArchaeologyProcessor
from src.utils.question_scan_tracker import QuestionScanTracker
import json


def example_basic_usage():
    """示例 1: 基本使用"""
    print("=" * 60)
    print("示例 1: 基本使用 - 處理 PDF 並檢查完整性")
    print("=" * 60)

    # 創建處理器
    processor = ArchaeologyProcessor(use_enhanced=True)

    # 處理 PDF（假設文件存在）
    # result = processor.process_pdf(
    #     pdf_path="sample_exam.pdf",
    #     output_dir="output"
    # )

    # 模擬結果
    result = {
        'scan_complete': True,
        'questions_count': 50,
        'missing_questions': [],
        'scan_report': {
            'scan_summary': {
                'total_scanned': 50,
                'is_complete': True,
                'missing_count': 0
            }
        }
    }

    # 檢查掃描結果
    if result['scan_complete']:
        print(f"✅ 所有題目掃描完成！共 {result['questions_count']} 題")
    else:
        print(f"⚠️ 有題目遺漏:")
        print(f"   遺漏題號: {result['missing_questions']}")

    print()


def example_incomplete_scan():
    """示例 2: 處理不完整掃描"""
    print("=" * 60)
    print("示例 2: 處理不完整掃描")
    print("=" * 60)

    # 模擬不完整的掃描結果
    result = {
        'scan_complete': False,
        'questions_count': 48,
        'missing_questions': [15, 32],
        'scan_report': {
            'scan_summary': {
                'total_scanned': 48,
                'expected_count': 50,
                'is_complete': False,
                'missing_count': 2
            },
            'parser_statistics': {
                'UltimateParser': 45,
                'StandardParser': 3
            }
        }
    }

    print(f"掃描題數: {result['questions_count']}")
    print(f"完整性: {'✅ 完整' if result['scan_complete'] else '❌ 不完整'}")

    if not result['scan_complete']:
        print(f"\n⚠️ 警告：發現遺漏題號！")
        print(f"遺漏題號: {result['missing_questions']}")
        print(f"遺漏數量: {len(result['missing_questions'])} 題")

        # 建議的處理方式
        print(f"\n建議處理方式:")
        print(f"1. 檢查原始 PDF 文件")
        print(f"2. 查看掃描報告了解詳情")
        print(f"3. 嘗試使用其他解析器")

    print()


def example_manual_validation():
    """示例 3: 手動驗證題目列表"""
    print("=" * 60)
    print("示例 3: 手動驗證題目列表")
    print("=" * 60)

    tracker = QuestionScanTracker(expected_count=50)

    # 完整的題目列表
    complete_questions = [
        {'題號': i, '題目': f'問題{i}'}
        for i in range(1, 51)
    ]

    is_complete, message = tracker.validate_questions(complete_questions)
    print(f"完整題目列表: {message}")

    # 不完整的題目列表（缺少題號 25）
    incomplete_questions = [
        {'題號': i, '題目': f'問題{i}'}
        for i in range(1, 51) if i != 25
    ]

    is_complete, message = tracker.validate_questions(incomplete_questions)
    print(f"不完整題目列表: {message}")

    # 有重複的題目列表
    duplicate_questions = [
        {'題號': 1, '題目': '問題1'},
        {'題號': 2, '題目': '問題2'},
        {'題號': 2, '題目': '問題2（重複）'}
    ]

    is_complete, message = tracker.validate_questions(duplicate_questions)
    print(f"重複題目列表: {message}")

    print()


def example_custom_tracking():
    """示例 4: 自定義掃描追蹤"""
    print("=" * 60)
    print("示例 4: 自定義掃描追蹤")
    print("=" * 60)

    # 創建追蹤器
    tracker = QuestionScanTracker(expected_count=10)
    tracker.start_scan()

    # 模擬掃描過程
    questions_data = [
        (1, "Parser1", "下列何者為正確答案？"),
        (2, "Parser1", "請選擇最佳選項。"),
        (3, "Parser2", "試說明以下概念。"),
        # 故意跳過題號 4
        (5, "Parser1", "請問下列敘述何者正確？"),
    ]

    print("開始掃描題目...")
    for num, parser, content in questions_data:
        tracker.register_question(num, parser, content)
        print(f"  ✓ 掃描第{num}題 [{parser}]")

    # 結束掃描
    print("\n結束掃描...")
    report = tracker.end_scan()

    # 顯示結果
    print(f"\n掃描摘要:")
    print(f"  總掃描: {report['scan_summary']['total_scanned']} 題")
    print(f"  預期數: {report['scan_summary']['expected_count']} 題")
    print(f"  完整性: {'✅' if report['scan_summary']['is_complete'] else '❌'}")

    if report['missing_questions']:
        print(f"  遺漏題號: {report['missing_questions']}")

    print(f"\n解析器統計:")
    for parser, count in report['parser_statistics'].items():
        print(f"  - {parser}: {count} 題")

    print()


def example_batch_processing():
    """示例 5: 批量處理多個文件"""
    print("=" * 60)
    print("示例 5: 批量處理多個文件")
    print("=" * 60)

    # 模擬批量處理結果
    files = [
        {"name": "exam1.pdf", "complete": True, "count": 50, "missing": []},
        {"name": "exam2.pdf", "complete": False, "count": 48, "missing": [12, 35]},
        {"name": "exam3.pdf", "complete": True, "count": 60, "missing": []},
        {"name": "exam4.pdf", "complete": False, "count": 55, "missing": [5, 23, 44]},
    ]

    print("批量處理結果:\n")

    complete_count = 0
    incomplete_files = []

    for file_info in files:
        status = "✅" if file_info['complete'] else "❌"
        print(f"{status} {file_info['name']}")
        print(f"   題數: {file_info['count']}")

        if file_info['complete']:
            complete_count += 1
            print(f"   狀態: 完整")
        else:
            incomplete_files.append(file_info)
            print(f"   狀態: 不完整（遺漏: {file_info['missing']}）")
        print()

    print(f"總結:")
    print(f"  完整文件: {complete_count}/{len(files)}")
    print(f"  不完整文件: {len(incomplete_files)}/{len(files)}")

    if incomplete_files:
        print(f"\n需要人工檢查的文件:")
        for file_info in incomplete_files:
            print(f"  - {file_info['name']}: 遺漏題號 {file_info['missing']}")

    print()


def example_report_analysis():
    """示例 6: 分析掃描報告"""
    print("=" * 60)
    print("示例 6: 分析掃描報告")
    print("=" * 60)

    # 模擬詳細掃描報告
    report = {
        'scan_summary': {
            'total_scanned': 50,
            'expected_count': 50,
            'question_range': '1 ~ 50',
            'is_complete': True,
            'missing_count': 0,
            'duplicate_count': 0,
            'scan_duration': 2.35
        },
        'parser_statistics': {
            'UltimateParser': 40,
            'StandardParser': 8,
            'EssayParser': 2
        },
        'missing_questions': [],
        'duplicate_questions': []
    }

    print(f"掃描報告分析:\n")
    print(f"📊 基本統計:")
    print(f"   總題數: {report['scan_summary']['total_scanned']}")
    print(f"   題號範圍: {report['scan_summary']['question_range']}")
    print(f"   掃描耗時: {report['scan_summary']['scan_duration']:.2f} 秒")
    print(f"   平均速度: {report['scan_summary']['total_scanned'] / report['scan_summary']['scan_duration']:.1f} 題/秒")

    print(f"\n🔧 解析器使用:")
    for parser, count in report['parser_statistics'].items():
        percentage = (count / report['scan_summary']['total_scanned']) * 100
        print(f"   {parser}: {count} 題 ({percentage:.1f}%)")

    print(f"\n✅ 完整性檢查:")
    print(f"   遺漏題數: {report['scan_summary']['missing_count']}")
    print(f"   重複題數: {report['scan_summary']['duplicate_count']}")
    print(f"   完整性: {'通過' if report['scan_summary']['is_complete'] else '失敗'}")

    print()


if __name__ == '__main__':
    print("\n" + "=" * 60)
    print(" 題目掃描追蹤系統 - 使用示例")
    print("=" * 60 + "\n")

    # 運行所有示例
    example_basic_usage()
    example_incomplete_scan()
    example_manual_validation()
    example_custom_tracking()
    example_batch_processing()
    example_report_analysis()

    print("=" * 60)
    print(" 所有示例執行完成")
    print("=" * 60 + "\n")
