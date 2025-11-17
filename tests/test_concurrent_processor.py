#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
並發處理器測試
測試多線程/多進程批量處理功能
"""

import unittest
import time
import tempfile
import os
from src.utils.concurrent_processor import (
    ConcurrentProcessor,
    ProcessingTask,
    TaskResult,
    ProgressTracker,
    create_processor
)


class TestProgressTracker(unittest.TestCase):
    """進度追蹤器測試"""

    def test_init(self):
        """測試初始化"""
        tracker = ProgressTracker(total_tasks=10)

        self.assertEqual(tracker.total_tasks, 10)
        self.assertEqual(tracker.completed, 0)
        self.assertEqual(tracker.successful, 0)
        self.assertEqual(tracker.failed, 0)

    def test_update_success(self):
        """測試更新成功任務"""
        tracker = ProgressTracker(total_tasks=10)

        tracker.update(success=True)

        self.assertEqual(tracker.completed, 1)
        self.assertEqual(tracker.successful, 1)
        self.assertEqual(tracker.failed, 0)

    def test_update_failure(self):
        """測試更新失敗任務"""
        tracker = ProgressTracker(total_tasks=10)

        tracker.update(success=False)

        self.assertEqual(tracker.completed, 1)
        self.assertEqual(tracker.successful, 0)
        self.assertEqual(tracker.failed, 1)

    def test_get_summary(self):
        """測試獲取摘要"""
        tracker = ProgressTracker(total_tasks=10)

        # 模擬完成 7 個成功，3 個失敗
        for _ in range(7):
            tracker.update(success=True)
        for _ in range(3):
            tracker.update(success=False)

        summary = tracker.get_summary()

        self.assertEqual(summary['total_tasks'], 10)
        self.assertEqual(summary['completed'], 10)
        self.assertEqual(summary['successful'], 7)
        self.assertEqual(summary['failed'], 3)
        self.assertEqual(summary['success_rate'], 70.0)
        self.assertGreater(summary['total_time'], 0)


class TestConcurrentProcessor(unittest.TestCase):
    """並發處理器測試"""

    def setUp(self):
        """測試前準備"""
        self.processor = ConcurrentProcessor(max_workers=2)

    def test_init(self):
        """測試初始化"""
        processor = ConcurrentProcessor(max_workers=4, use_processes=False)

        self.assertEqual(processor.max_workers, 4)
        self.assertFalse(processor.use_processes)

    def test_init_default_workers(self):
        """測試默認 worker 數量"""
        processor = ConcurrentProcessor()

        self.assertGreater(processor.max_workers, 0)

    def test_process_empty_batch(self):
        """測試處理空任務列表"""
        results = self.processor.process_batch([], lambda task: {})

        self.assertEqual(len(results), 0)

    def test_process_single_task_success(self):
        """測試處理單個成功任務"""
        def mock_processor(task):
            return {
                'success': True,
                'questions_count': 50,
                'message': 'Success'
            }

        task = ProcessingTask(
            task_id=1,
            pdf_path="test.pdf",
            output_dir="output"
        )

        results = self.processor.process_batch([task], mock_processor)

        self.assertEqual(len(results), 1)
        self.assertTrue(results[0].success)
        self.assertEqual(results[0].result['questions_count'], 50)

    def test_process_single_task_failure(self):
        """測試處理單個失敗任務"""
        def mock_processor(task):
            return {
                'success': False,
                'message': 'Failed to process'
            }

        task = ProcessingTask(
            task_id=1,
            pdf_path="test.pdf",
            output_dir="output"
        )

        results = self.processor.process_batch([task], mock_processor)

        self.assertEqual(len(results), 1)
        self.assertFalse(results[0].success)
        self.assertIsNotNone(results[0].error)

    def test_process_multiple_tasks(self):
        """測試處理多個任務"""
        def mock_processor(task):
            # 模擬處理延遲
            time.sleep(0.1)
            return {
                'success': True,
                'questions_count': task.task_id * 10
            }

        tasks = [
            ProcessingTask(task_id=i, pdf_path=f"test_{i}.pdf", output_dir="output")
            for i in range(5)
        ]

        start_time = time.time()
        results = self.processor.process_batch(tasks, mock_processor)
        duration = time.time() - start_time

        # 驗證結果
        self.assertEqual(len(results), 5)
        self.assertTrue(all(r.success for r in results))

        # 驗證並發加速（應該比串行快）
        # 串行需要 5 * 0.1 = 0.5 秒，並發應該少於 0.3 秒
        self.assertLess(duration, 0.4)

    def test_process_mixed_results(self):
        """測試處理混合結果（成功和失敗）"""
        def mock_processor(task):
            # 奇數任務失敗，偶數任務成功
            if task.task_id % 2 == 0:
                return {'success': True, 'questions_count': 50}
            else:
                return {'success': False, 'message': 'Failed'}

        tasks = [
            ProcessingTask(task_id=i, pdf_path=f"test_{i}.pdf", output_dir="output")
            for i in range(10)
        ]

        results = self.processor.process_batch(tasks, mock_processor)

        successful = [r for r in results if r.success]
        failed = [r for r in results if not r.success]

        self.assertEqual(len(successful), 5)
        self.assertEqual(len(failed), 5)

    def test_process_with_exception(self):
        """測試處理拋出異常的任務"""
        def mock_processor(task):
            if task.task_id == 2:
                raise ValueError("Test exception")
            return {'success': True}

        tasks = [
            ProcessingTask(task_id=i, pdf_path=f"test_{i}.pdf", output_dir="output")
            for i in range(5)
        ]

        results = self.processor.process_batch(tasks, mock_processor)

        # 應該捕獲異常並記錄為失敗
        self.assertEqual(len(results), 5)
        failed = [r for r in results if not r.success]
        self.assertEqual(len(failed), 1)
        self.assertIn("Test exception", failed[0].error)

    def test_fail_fast_mode(self):
        """測試快速失敗模式"""
        def mock_processor(task):
            if task.task_id == 2:
                return {'success': False, 'message': 'Critical error'}
            time.sleep(0.1)
            return {'success': True}

        tasks = [
            ProcessingTask(task_id=i, pdf_path=f"test_{i}.pdf", output_dir="output")
            for i in range(10)
        ]

        results = self.processor.process_batch(tasks, mock_processor, fail_fast=True)

        # 快速失敗模式下，遇到錯誤應該停止
        # 結果數量應該少於總任務數
        self.assertLessEqual(len(results), 10)

    def test_task_duration_tracking(self):
        """測試任務耗時追蹤"""
        def mock_processor(task):
            time.sleep(0.1)
            return {'success': True}

        task = ProcessingTask(task_id=1, pdf_path="test.pdf", output_dir="output")

        results = self.processor.process_batch([task], mock_processor)

        self.assertEqual(len(results), 1)
        self.assertGreater(results[0].duration, 0.1)
        self.assertIsNotNone(results[0].start_time)
        self.assertIsNotNone(results[0].end_time)

    def test_create_processor_helper(self):
        """測試創建處理器的便捷函數"""
        processor = create_processor(max_workers=8, use_processes=True)

        self.assertEqual(processor.max_workers, 8)
        self.assertTrue(processor.use_processes)

    def test_multithread_mode(self):
        """測試多線程模式"""
        processor = ConcurrentProcessor(max_workers=2, use_processes=False)

        def mock_processor(task):
            time.sleep(0.05)
            return {'success': True}

        tasks = [
            ProcessingTask(task_id=i, pdf_path=f"test_{i}.pdf", output_dir="output")
            for i in range(4)
        ]

        start_time = time.time()
        results = processor.process_batch(tasks, mock_processor)
        duration = time.time() - start_time

        self.assertEqual(len(results), 4)
        # 多線程應該比串行快
        self.assertLess(duration, 0.2)  # 串行需要 0.2 秒

    def test_process_directory_empty(self):
        """測試處理空目錄"""
        with tempfile.TemporaryDirectory() as temp_dir:
            results, summary = self.processor.process_directory(
                input_dir=temp_dir,
                output_dir=temp_dir,
                processor_func=lambda task: {'success': True}
            )

            self.assertEqual(len(results), 0)
            self.assertEqual(summary, {})


class TestProcessingTask(unittest.TestCase):
    """處理任務測試"""

    def test_init_minimal(self):
        """測試最小參數初始化"""
        task = ProcessingTask(task_id=1, pdf_path="test.pdf")

        self.assertEqual(task.task_id, 1)
        self.assertEqual(task.pdf_path, "test.pdf")
        self.assertIsNone(task.answer_pdf_path)
        self.assertIsNone(task.corrected_answer_pdf_path)
        self.assertEqual(task.output_dir, "output")

    def test_init_full(self):
        """測試完整參數初始化"""
        task = ProcessingTask(
            task_id=1,
            pdf_path="test.pdf",
            answer_pdf_path="answer.pdf",
            corrected_answer_pdf_path="corrected.pdf",
            output_dir="custom_output"
        )

        self.assertEqual(task.task_id, 1)
        self.assertEqual(task.pdf_path, "test.pdf")
        self.assertEqual(task.answer_pdf_path, "answer.pdf")
        self.assertEqual(task.corrected_answer_pdf_path, "corrected.pdf")
        self.assertEqual(task.output_dir, "custom_output")


class TestTaskResult(unittest.TestCase):
    """任務結果測試"""

    def test_init(self):
        """測試初始化"""
        result = TaskResult(
            task_id=1,
            pdf_path="test.pdf",
            success=True,
            result={'questions_count': 50}
        )

        self.assertEqual(result.task_id, 1)
        self.assertEqual(result.pdf_path, "test.pdf")
        self.assertTrue(result.success)
        self.assertEqual(result.result['questions_count'], 50)
        self.assertIsNone(result.error)

    def test_with_error(self):
        """測試包含錯誤的結果"""
        result = TaskResult(
            task_id=1,
            pdf_path="test.pdf",
            success=False,
            result={},
            error="Processing failed",
            duration=1.5
        )

        self.assertFalse(result.success)
        self.assertEqual(result.error, "Processing failed")
        self.assertEqual(result.duration, 1.5)


if __name__ == '__main__':
    unittest.main()
