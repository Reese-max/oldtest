#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試性能監控器
"""

import os
import sys
import unittest
import time
import tempfile
import json

# 添加專案根目錄到路徑
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.utils.performance_monitor import (
    PerformanceMonitor,
    PerformanceTimer,
    PerformanceMetrics,
    monitor_performance,
    global_monitor
)


class TestPerformanceTimer(unittest.TestCase):
    """測試 PerformanceTimer 類"""

    def test_context_manager(self):
        """測試上下文管理器"""
        with PerformanceTimer("test") as timer:
            time.sleep(0.1)

        # 驗證計時
        self.assertIsNotNone(timer.duration)
        self.assertGreater(timer.duration, 0.1)
        self.assertLess(timer.duration, 0.2)

    def test_manual_timing(self):
        """測試手動計時"""
        timer = PerformanceTimer("manual_test")

        timer.start()
        time.sleep(0.05)
        timer.stop()

        # 驗證計時
        duration = timer.get_duration()
        self.assertGreater(duration, 0.05)
        self.assertLess(duration, 0.1)

    def test_get_summary(self):
        """測試獲取摘要"""
        timer = PerformanceTimer("summary_test")

        timer.start()
        time.sleep(0.01)
        timer.stop()

        summary = timer.get_summary()

        # 驗證摘要包含關鍵信息
        self.assertIn("summary_test", summary)
        self.assertIn("秒", summary)
        self.assertIn("記憶體", summary)

    def test_memory_tracking(self):
        """測試記憶體追蹤"""
        timer = PerformanceTimer("memory_test")

        timer.start()
        # 創建一些數據
        data = [i for i in range(100000)]
        timer.stop()

        memory_delta = timer.get_memory_delta()

        # 記憶體應該有變化（可能增加或減少）
        self.assertIsInstance(memory_delta, float)


class TestPerformanceMetrics(unittest.TestCase):
    """測試 PerformanceMetrics 類"""

    def test_create_metrics(self):
        """測試創建性能指標"""
        metrics = PerformanceMetrics(
            function_name="test_func",
            start_time=time.time(),
            end_time=time.time() + 1,
            duration=1.0,
            memory_before_mb=100.0,
            memory_after_mb=110.0,
            memory_delta_mb=10.0,
            cpu_percent=50.0,
            timestamp="2025-11-17T12:00:00",
            success=True
        )

        self.assertEqual(metrics.function_name, "test_func")
        self.assertEqual(metrics.duration, 1.0)
        self.assertEqual(metrics.memory_delta_mb, 10.0)
        self.assertTrue(metrics.success)

    def test_to_dict(self):
        """測試轉換為字典"""
        metrics = PerformanceMetrics(
            function_name="test_func",
            start_time=1.0,
            end_time=2.0,
            duration=1.0,
            memory_before_mb=100.0,
            memory_after_mb=105.0,
            memory_delta_mb=5.0,
            cpu_percent=30.0,
            timestamp="2025-11-17"
        )

        metrics_dict = metrics.to_dict()

        self.assertIn('function_name', metrics_dict)
        self.assertIn('duration', metrics_dict)
        self.assertIn('memory_delta_mb', metrics_dict)
        self.assertIn('cpu_percent', metrics_dict)
        self.assertEqual(metrics_dict['function_name'], "test_func")


class TestPerformanceMonitor(unittest.TestCase):
    """測試 PerformanceMonitor 類"""

    def setUp(self):
        """測試前設置"""
        self.monitor = PerformanceMonitor()

    def test_decorator_basic(self):
        """測試基本裝飾器功能"""
        @self.monitor.monitor()
        def sample_function():
            time.sleep(0.01)
            return "result"

        result = sample_function()

        # 驗證函數正常執行
        self.assertEqual(result, "result")

        # 驗證性能指標被記錄
        self.assertEqual(len(self.monitor.metrics), 1)
        metrics = self.monitor.metrics[0]
        self.assertEqual(metrics.function_name, "sample_function")
        self.assertGreater(metrics.duration, 0.01)

    def test_decorator_with_exception(self):
        """測試處理異常的裝飾器"""
        @self.monitor.monitor()
        def failing_function():
            raise ValueError("Test error")

        # 應該拋出異常
        with self.assertRaises(ValueError):
            failing_function()

        # 但仍然記錄性能指標
        self.assertEqual(len(self.monitor.metrics), 1)
        metrics = self.monitor.metrics[0]
        self.assertFalse(metrics.success)
        self.assertIn("Test error", metrics.error_message)

    def test_function_stats(self):
        """測試函數統計"""
        @self.monitor.monitor()
        def repeated_function():
            time.sleep(0.01)

        # 調用多次
        for _ in range(5):
            repeated_function()

        # 獲取統計
        stats = self.monitor.get_function_stats("repeated_function")

        self.assertEqual(stats['call_count'], 5)
        self.assertGreater(stats['total_time'], 0.05)
        self.assertGreater(stats['avg_time'], 0.01)
        self.assertGreater(stats['min_time'], 0)
        self.assertGreater(stats['max_time'], 0)

    def test_get_all_stats(self):
        """測試獲取所有統計"""
        @self.monitor.monitor()
        def func1():
            time.sleep(0.01)

        @self.monitor.monitor()
        def func2():
            time.sleep(0.01)

        func1()
        func2()

        all_stats = self.monitor.get_all_stats()

        # 應該有兩個函數的統計
        self.assertEqual(len(all_stats), 2)
        self.assertIn('func1', all_stats)
        self.assertIn('func2', all_stats)

    def test_metrics_summary(self):
        """測試性能指標總結"""
        @self.monitor.monitor()
        def test_function():
            time.sleep(0.01)

        # 調用幾次
        test_function()
        test_function()

        summary = self.monitor.get_metrics_summary()

        self.assertEqual(summary['total_metrics'], 2)
        self.assertGreater(summary['total_duration'], 0.02)
        self.assertEqual(summary['success_rate'], 100.0)

    def test_generate_report(self):
        """測試生成報告"""
        @self.monitor.monitor()
        def test_function():
            time.sleep(0.01)

        test_function()

        report = self.monitor.generate_report()

        # 驗證報告包含關鍵信息
        self.assertIn("性能監控報告", report)
        self.assertIn("總體統計", report)
        self.assertIn("函數統計", report)
        self.assertIn("test_function", report)

    def test_export_metrics(self):
        """測試導出性能指標"""
        @self.monitor.monitor()
        def test_function():
            return "result"

        test_function()

        # 導出到臨時文件
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            temp_file = f.name

        try:
            self.monitor.export_metrics(temp_file)

            # 讀取並驗證
            with open(temp_file, 'r') as f:
                data = json.load(f)

            self.assertEqual(len(data), 1)
            self.assertEqual(data[0]['function_name'], "test_function")

        finally:
            os.unlink(temp_file)

    def test_clear_metrics(self):
        """測試清除性能指標"""
        @self.monitor.monitor()
        def test_function():
            pass

        test_function()

        # 確認有數據
        self.assertEqual(len(self.monitor.metrics), 1)

        # 清除
        self.monitor.clear_metrics()

        # 確認已清除
        self.assertEqual(len(self.monitor.metrics), 0)
        self.assertEqual(len(self.monitor.function_stats), 0)

    def test_record_metric_manually(self):
        """測試手動記錄指標"""
        metrics = PerformanceMetrics(
            function_name="manual_func",
            start_time=1.0,
            end_time=2.0,
            duration=1.0,
            memory_before_mb=100.0,
            memory_after_mb=105.0,
            memory_delta_mb=5.0,
            cpu_percent=30.0,
            timestamp="2025-11-17"
        )

        self.monitor.record_metric(metrics)

        # 驗證已記錄
        self.assertEqual(len(self.monitor.metrics), 1)
        self.assertEqual(self.monitor.metrics[0].function_name, "manual_func")


class TestGlobalMonitor(unittest.TestCase):
    """測試全局監控器"""

    def setUp(self):
        """測試前清除全局監控器"""
        global_monitor.clear_metrics()

    def test_global_decorator(self):
        """測試全局裝飾器"""
        @monitor_performance
        def global_test_function():
            time.sleep(0.01)
            return "global result"

        result = global_test_function()

        # 驗證函數執行
        self.assertEqual(result, "global result")

        # 驗證全局監控器記錄了指標
        self.assertGreater(len(global_monitor.metrics), 0)

    def test_global_report(self):
        """測試全局報告"""
        from src.utils.performance_monitor import get_global_report

        @monitor_performance
        def test_func():
            time.sleep(0.01)

        test_func()

        report = get_global_report()

        # 驗證報告內容
        self.assertIn("性能監控報告", report)
        self.assertIn("test_func", report)


class TestPerformanceMonitorIntegration(unittest.TestCase):
    """集成測試"""

    def test_multiple_functions_workflow(self):
        """測試多個函數的完整工作流程"""
        monitor = PerformanceMonitor()

        @monitor.monitor()
        def process_step1():
            time.sleep(0.01)
            return [1, 2, 3]

        @monitor.monitor()
        def process_step2(data):
            time.sleep(0.02)
            return [x * 2 for x in data]

        @monitor.monitor()
        def process_step3(data):
            time.sleep(0.01)
            return sum(data)

        # 執行工作流程
        data = process_step1()
        data = process_step2(data)
        result = process_step3(data)

        # 驗證結果
        self.assertEqual(result, 12)

        # 驗證監控
        self.assertEqual(len(monitor.metrics), 3)
        all_stats = monitor.get_all_stats()
        self.assertEqual(len(all_stats), 3)

        # 生成報告
        report = monitor.generate_report()
        self.assertIn("process_step1", report)
        self.assertIn("process_step2", report)
        self.assertIn("process_step3", report)


if __name__ == '__main__':
    unittest.main()
