#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
並發安全測試
測試 ConfigManager 的線程安全性
"""

import os
import sys
import unittest
import threading
import tempfile
import time

# 添加項目根目錄到 Python 路徑
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utils.config import ConfigManager


class TestConfigManagerConcurrency(unittest.TestCase):
    """測試 ConfigManager 並發安全性"""

    def setUp(self):
        """測試前設置"""
        # 重置單例實例
        ConfigManager._instance = None
        self.instances = []
        self.temp_config = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
        self.temp_config.write('{"processing": {}, "google_form": {}, "ocr": {}}')
        self.temp_config.close()

    def tearDown(self):
        """測試後清理"""
        if os.path.exists(self.temp_config.name):
            os.unlink(self.temp_config.name)
        ConfigManager._instance = None

    def test_singleton_same_instance(self):
        """測試單例模式：多次調用返回同一實例"""
        instance1 = ConfigManager.get_instance(self.temp_config.name)
        instance2 = ConfigManager.get_instance(self.temp_config.name)
        instance3 = ConfigManager.get_instance(self.temp_config.name)

        self.assertIs(instance1, instance2)
        self.assertIs(instance2, instance3)
        self.assertIs(instance1, instance3)

    def test_concurrent_initialization(self):
        """測試並發初始化：多線程同時獲取實例"""
        num_threads = 20
        instances = [None] * num_threads
        threads = []

        def get_instance(index):
            """線程任務：獲取ConfigManager實例"""
            instances[index] = ConfigManager.get_instance(self.temp_config.name)

        # 創建並啟動多個線程
        for i in range(num_threads):
            thread = threading.Thread(target=get_instance, args=(i,))
            threads.append(thread)
            thread.start()

        # 等待所有線程完成
        for thread in threads:
            thread.join()

        # 驗證所有線程獲得的是同一個實例
        first_instance = instances[0]
        for instance in instances:
            self.assertIs(instance, first_instance)

    def test_concurrent_config_updates(self):
        """測試並發配置更新：多線程同時更新配置"""
        instance = ConfigManager.get_instance(self.temp_config.name)
        num_threads = 10
        updates_per_thread = 5
        completed_updates = []
        lock = threading.Lock()

        def update_config(thread_id):
            """線程任務：更新配置"""
            for i in range(updates_per_thread):
                # 更新處理配置
                instance.update_processing_config(
                    max_text_length=1000000 + thread_id * 100 + i
                )

                # 記錄完成的更新
                with lock:
                    completed_updates.append((thread_id, i))

                # 短暫睡眠，增加競爭條件
                time.sleep(0.001)

        # 創建並啟動多個線程
        threads = []
        for i in range(num_threads):
            thread = threading.Thread(target=update_config, args=(i,))
            threads.append(thread)
            thread.start()

        # 等待所有線程完成
        for thread in threads:
            thread.join()

        # 驗證所有更新都已完成
        self.assertEqual(len(completed_updates), num_threads * updates_per_thread)

    def test_concurrent_read_write(self):
        """測試並發讀寫：多線程同時讀寫配置"""
        instance = ConfigManager.get_instance(self.temp_config.name)
        num_readers = 10
        num_writers = 5
        read_count = [0]
        write_count = [0]
        lock = threading.Lock()

        def reader_task(reader_id):
            """讀取任務"""
            for _ in range(10):
                config = instance.get_processing_config()
                self.assertIsNotNone(config)
                with lock:
                    read_count[0] += 1
                time.sleep(0.001)

        def writer_task(writer_id):
            """寫入任務"""
            for i in range(5):
                instance.update_processing_config(
                    max_text_length=1000000 + writer_id * 10 + i
                )
                with lock:
                    write_count[0] += 1
                time.sleep(0.002)

        # 創建讀者線程
        threads = []
        for i in range(num_readers):
            thread = threading.Thread(target=reader_task, args=(i,))
            threads.append(thread)

        # 創建寫者線程
        for i in range(num_writers):
            thread = threading.Thread(target=writer_task, args=(i,))
            threads.append(thread)

        # 啟動所有線程
        for thread in threads:
            thread.start()

        # 等待所有線程完成
        for thread in threads:
            thread.join()

        # 驗證讀寫次數
        self.assertEqual(read_count[0], num_readers * 10)
        self.assertEqual(write_count[0], num_writers * 5)

    def test_no_race_condition_on_file_ops(self):
        """測試文件操作無競爭條件"""
        instance = ConfigManager.get_instance(self.temp_config.name)
        num_threads = 15
        operations = []
        lock = threading.Lock()

        def file_operation(thread_id):
            """文件操作任務：交替讀寫"""
            for i in range(3):
                # 寫入
                instance.update_google_form_config(
                    form_title=f"Thread-{thread_id}-Iteration-{i}"
                )
                with lock:
                    operations.append(('write', thread_id, i))

                # 讀取
                config = instance.get_google_form_config()
                with lock:
                    operations.append(('read', thread_id, config.form_title))

                time.sleep(0.001)

        # 創建並啟動多個線程
        threads = []
        for i in range(num_threads):
            thread = threading.Thread(target=file_operation, args=(i,))
            threads.append(thread)
            thread.start()

        # 等待所有線程完成
        for thread in threads:
            thread.join()

        # 驗證操作順序一致性（沒有異常即表示文件操作安全）
        self.assertEqual(len(operations), num_threads * 6)  # 每線程3次讀+3次寫

    def test_instance_identity_across_modules(self):
        """測試跨模組實例一致性"""
        instance1 = ConfigManager.get_instance(self.temp_config.name)

        # 在另一個線程中獲取實例
        instance2 = None

        def get_in_thread():
            nonlocal instance2
            instance2 = ConfigManager.get_instance(self.temp_config.name)

        thread = threading.Thread(target=get_in_thread)
        thread.start()
        thread.join()

        # 驗證實例相同
        self.assertIs(instance1, instance2)


class TestThreadSafeLocking(unittest.TestCase):
    """測試鎖機制"""

    def setUp(self):
        """測試前設置"""
        ConfigManager._instance = None

    def tearDown(self):
        """測試後清理"""
        ConfigManager._instance = None

    def test_lock_exists(self):
        """測試鎖對象存在"""
        # 檢查鎖對象是否存在且可用
        self.assertIsNotNone(ConfigManager._lock)
        self.assertIsNotNone(ConfigManager._file_lock)

        # 驗證鎖對象具有必要的方法
        self.assertTrue(hasattr(ConfigManager._lock, 'acquire'))
        self.assertTrue(hasattr(ConfigManager._lock, 'release'))
        self.assertTrue(hasattr(ConfigManager._file_lock, 'acquire'))
        self.assertTrue(hasattr(ConfigManager._file_lock, 'release'))

    def test_double_checked_locking_pattern(self):
        """測試雙重檢查鎖定模式"""
        # 第一次調用應創建實例
        self.assertIsNone(ConfigManager._instance)
        instance1 = ConfigManager.get_instance()
        self.assertIsNotNone(ConfigManager._instance)

        # 第二次調用應返回相同實例
        instance2 = ConfigManager.get_instance()
        self.assertIs(instance1, instance2)


if __name__ == '__main__':
    # 運行測試
    unittest.main(verbosity=2)
