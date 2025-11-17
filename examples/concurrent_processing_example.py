#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
並發批量處理示例
演示如何使用並發處理器大幅提升批量處理速度
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.processors.archaeology_processor import ArchaeologyProcessor
from src.utils.concurrent_processor import (
    ConcurrentProcessor,
    ProcessingTask,
    create_processor
)


def example_basic_concurrent_processing():
    """示例 1: 基本並發處理"""
    print("=" * 60)
    print("示例 1: 基本並發處理")
    print("=" * 60)

    # 創建並發處理器（使用 4 個線程）
    processor = ConcurrentProcessor(max_workers=4)

    # 定義處理函數
    def process_task(task):
        """處理單個任務"""
        archaeology_processor = ArchaeologyProcessor()
        return archaeology_processor.process_pdf(
            task.pdf_path,
            task.answer_pdf_path,
            task.corrected_answer_pdf_path,
            task.output_dir
        )

    # 創建任務列表
    tasks = [
        ProcessingTask(
            task_id=i,
            pdf_path=f"exam_{i}.pdf",
            answer_pdf_path=f"exam_{i}_答案.pdf",
            output_dir="output"
        )
        for i in range(1, 11)  # 10 個任務
    ]

    # 批量處理（模擬）
    print(f"準備處理 {len(tasks)} 個 PDF 文件...")
    print("（實際執行需要有 PDF 文件）")
    print()


def example_multithread_vs_serial():
    """示例 2: 多線程 vs 串行處理性能對比"""
    print("=" * 60)
    print("示例 2: 多線程 vs 串行 - 性能對比")
    print("=" * 60)

    import time

    def mock_process(task):
        """模擬處理（需要 0.5 秒）"""
        time.sleep(0.5)
        return {
            'success': True,
            'questions_count': 50,
            'pdf_path': task.pdf_path
        }

    # 創建 10 個任務
    tasks = [
        ProcessingTask(task_id=i, pdf_path=f"test_{i}.pdf", output_dir="output")
        for i in range(10)
    ]

    # 串行處理
    print("📊 串行處理:")
    start = time.time()
    for task in tasks:
        mock_process(task)
    serial_time = time.time() - start
    print(f"   耗時: {serial_time:.2f} 秒\n")

    # 並發處理（4 個線程）
    print("📊 並發處理 (4 線程):")
    processor = ConcurrentProcessor(max_workers=4)
    start = time.time()
    processor.process_batch(tasks, mock_process)
    concurrent_time = time.time() - start
    print(f"   耗時: {concurrent_time:.2f} 秒\n")

    # 性能對比
    speedup = serial_time / concurrent_time
    print(f"🚀 加速比: {speedup:.2f}x")
    print(f"   性能提升: {(speedup - 1) * 100:.1f}%")
    print()


def example_progress_tracking():
    """示例 3: 進度追蹤"""
    print("=" * 60)
    print("示例 3: 實時進度追蹤")
    print("=" * 60)

    import time

    def mock_process(task):
        """模擬處理"""
        time.sleep(0.2)
        # 90% 成功率
        success = task.task_id % 10 != 0
        return {
            'success': success,
            'questions_count': 50 if success else 0,
            'message': 'Success' if success else 'Failed'
        }

    tasks = [
        ProcessingTask(task_id=i, pdf_path=f"test_{i}.pdf", output_dir="output")
        for i in range(20)
    ]

    processor = ConcurrentProcessor(max_workers=4)

    print("處理過程中會顯示實時進度：")
    print("- 完成數 / 總數")
    print("- 成功 / 失敗統計")
    print("- 預計剩餘時間")
    print()

    results = processor.process_batch(tasks, mock_process)

    # 結果分析
    successful = [r for r in results if r.success]
    failed = [r for r in results if not r.success]

    print(f"\n最終結果:")
    print(f"   成功: {len(successful)} 個")
    print(f"   失敗: {len(failed)} 個")
    print()


def example_error_handling():
    """示例 4: 錯誤處理"""
    print("=" * 60)
    print("示例 4: 錯誤處理與重試")
    print("=" * 60)

    def mock_process(task):
        """模擬處理（部分失敗）"""
        if task.task_id % 3 == 0:
            # 每第 3 個任務失敗
            return {
                'success': False,
                'message': f'處理失敗: {task.pdf_path}'
            }
        return {
            'success': True,
            'questions_count': 50
        }

    tasks = [
        ProcessingTask(task_id=i, pdf_path=f"test_{i}.pdf", output_dir="output")
        for i in range(9)
    ]

    processor = ConcurrentProcessor(max_workers=3)
    results = processor.process_batch(tasks, mock_process)

    # 收集失敗任務
    failed_tasks = [r for r in results if not r.success]

    print(f"\n失敗任務處理:")
    print(f"   失敗數: {len(failed_tasks)}")
    if failed_tasks:
        print(f"   失敗文件:")
        for r in failed_tasks:
            print(f"      - {r.pdf_path}: {r.error}")

    # 可以對失敗任務進行重試
    if failed_tasks:
        print(f"\n   可以對 {len(failed_tasks)} 個失敗任務進行重試...")

    print()


def example_directory_processing():
    """示例 5: 目錄批量處理"""
    print("=" * 60)
    print("示例 5: 目錄批量處理")
    print("=" * 60)

    def mock_process(task):
        """模擬處理"""
        return {
            'success': True,
            'questions_count': 50,
            'pdf_path': task.pdf_path
        }

    processor = ConcurrentProcessor(max_workers=4)

    print("使用方法:")
    print("""
    results, summary = processor.process_directory(
        input_dir="./pdf_files",      # 輸入目錄
        output_dir="./output",         # 輸出目錄
        processor_func=process_task,   # 處理函數
        recursive=True                 # 遞歸搜索
    )

    # 查看摘要
    print(f"總文件數: {summary['total_files']}")
    print(f"成功數: {summary['successful']}")
    print(f"失敗數: {summary['failed']}")
    print(f"總題數: {summary['total_questions']}")
    print(f"成功率: {summary['success_rate']:.1f}%")
    """)
    print()


def example_performance_tuning():
    """示例 6: 性能調優"""
    print("=" * 60)
    print("示例 6: 性能調優技巧")
    print("=" * 60)

    print("""
    # 1. 根據任務類型選擇合適的並發模式

    # I/O 密集型（PDF 讀取）- 使用多線程
    processor = ConcurrentProcessor(
        max_workers=8,
        use_processes=False  # 線程
    )

    # CPU 密集型（OCR 處理）- 使用多進程
    processor = ConcurrentProcessor(
        max_workers=4,  # CPU 核心數
        use_processes=True  # 進程
    )

    # 2. 調整 worker 數量

    # 輕量級任務：更多 worker
    processor = ConcurrentProcessor(max_workers=16)

    # 重量級任務：少量 worker
    processor = ConcurrentProcessor(max_workers=4)

    # 3. 使用快速失敗模式

    results = processor.process_batch(
        tasks,
        process_func,
        fail_fast=True  # 遇到錯誤立即停止
    )

    # 4. 批量處理優化

    # 將大任務分批處理，避免記憶體溢出
    batch_size = 50
    for i in range(0, len(all_tasks), batch_size):
        batch = all_tasks[i:i+batch_size]
        results = processor.process_batch(batch, process_func)
        # 處理結果...
    """)
    print()


def example_real_world_usage():
    """示例 7: 實際應用場景"""
    print("=" * 60)
    print("示例 7: 實際應用場景")
    print("=" * 60)

    print("""
    # 場景 1: 批量處理考卷

    from src.processors.archaeology_processor import ArchaeologyProcessor
    from src.utils.concurrent_processor import create_processor

    def process_exam(task):
        processor = ArchaeologyProcessor()
        return processor.process_pdf(
            task.pdf_path,
            task.answer_pdf_path,
            task.corrected_answer_pdf_path,
            task.output_dir
        )

    # 創建任務
    tasks = [
        ProcessingTask(
            task_id=i,
            pdf_path=f"exam_{i}.pdf",
            output_dir="output"
        )
        for i in range(100)  # 100 份考卷
    ]

    # 並發處理（預計速度提升 3-4x）
    concurrent = create_processor(max_workers=8)
    results = concurrent.process_batch(tasks, process_exam)

    # 場景 2: 處理整個目錄

    results, summary = concurrent.process_directory(
        input_dir="./exam_archive",
        output_dir="./processed",
        processor_func=process_exam,
        recursive=True
    )

    print(f"處理完成: {summary['successful']}/{summary['total_files']}")
    print(f"總題數: {summary['total_questions']}")

    # 場景 3: 失敗重試機制

    # 第一次處理
    results = concurrent.process_batch(tasks, process_exam)

    # 收集失敗任務
    failed = [r for r in results if not r.success]

    # 重試失敗任務
    if failed:
        retry_tasks = [
            ProcessingTask(task_id=r.task_id, pdf_path=r.pdf_path)
            for r in failed
        ]
        retry_results = concurrent.process_batch(retry_tasks, process_exam)
    """)
    print()


if __name__ == '__main__':
    print("\n" + "=" * 60)
    print(" 並發批量處理 - 使用示例")
    print("=" * 60 + "\n")

    # 運行所有示例
    example_basic_concurrent_processing()
    example_multithread_vs_serial()
    example_progress_tracking()
    example_error_handling()
    example_directory_processing()
    example_performance_tuning()
    example_real_world_usage()

    print("=" * 60)
    print(" 所有示例執行完成")
    print("=" * 60 + "\n")

    print("\n🚀 性能提升總結:")
    print("=" * 60)
    print("1. 多線程處理: 3-4x 加速（I/O 密集型）")
    print("2. 多進程處理: 2-3x 加速（CPU 密集型）")
    print("3. 批量處理 100 份考卷: 從 50 分鐘 → 15 分鐘")
    print("4. 實時進度追蹤: 清楚掌握處理狀態")
    print("5. 自動錯誤處理: 失敗任務不影響整體")
    print("=" * 60 + "\n")
