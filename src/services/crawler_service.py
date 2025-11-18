#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
爬蟲下載服務
整合考古題下載功能到 Web UI
"""

import os
import sys
import threading
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path

# 添加項目根目錄到路徑
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# 導入爬蟲模塊
import importlib.util
spec = importlib.util.spec_from_file_location(
    "crawler",
    str(Path(__file__).parent.parent.parent / "考古題下載.py")
)
crawler_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(crawler_module)


class CrawlerService:
    """爬蟲下載服務"""

    def __init__(self):
        self.tasks = {}  # 任務存儲
        self.lock = threading.Lock()

    def create_task(self, years: List[int], keywords: List[str], save_dir: str) -> str:
        """
        創建爬蟲任務

        Args:
            years: 年份列表
            keywords: 考試類型關鍵字列表
            save_dir: 保存目錄

        Returns:
            任務ID
        """
        task_id = str(uuid.uuid4())

        with self.lock:
            self.tasks[task_id] = {
                'id': task_id,
                'years': years,
                'keywords': keywords,
                'save_dir': save_dir,
                'status': 'pending',
                'created_at': datetime.now().isoformat(),
                'progress': 0,
                'stats': {
                    'success': 0,
                    'failed': 0,
                    'skipped': 0,
                    'total_size': 0,
                    'completed_exams': 0,
                    'failed_exams': 0,
                    'empty_exams': 0
                },
                'logs': [],
                'current_year': None,
                'current_exam': None
            }

        return task_id

    def start_task(self, task_id: str) -> bool:
        """
        啟動爬蟲任務

        Args:
            task_id: 任務ID

        Returns:
            是否成功啟動
        """
        with self.lock:
            if task_id not in self.tasks:
                return False

            task = self.tasks[task_id]

            if task['status'] != 'pending':
                return False

            task['status'] = 'running'
            task['started_at'] = datetime.now().isoformat()

        # 在新線程中運行爬蟲
        thread = threading.Thread(target=self._run_crawler, args=(task_id,))
        thread.daemon = True
        thread.start()

        return True

    def _run_crawler(self, task_id: str):
        """
        運行爬蟲（內部方法）

        Args:
            task_id: 任務ID
        """
        task = self.tasks[task_id]

        try:
            self._log(task_id, "開始爬蟲下載任務")

            # 創建保存目錄
            os.makedirs(task['save_dir'], exist_ok=True)

            # 創建 Session
            session = crawler_module.create_robust_session()

            # 獲取配置
            use_concurrent = crawler_module.DOWNLOADER_CONFIG.get('enable_concurrent', True)

            self._log(task_id, f"並發下載: {use_concurrent}")
            self._log(task_id, f"年份: {task['years']}")
            self._log(task_id, f"關鍵字: {task['keywords']}")

            # 遍歷年份
            total_years = len(task['years'])
            for idx, year in enumerate(task['years'], 1):
                if task['status'] == 'cancelled':
                    self._log(task_id, "任務已取消")
                    break

                task['current_year'] = year
                self._log(task_id, f"正在處理民國 {year} 年 ({idx}/{total_years})")

                # 獲取考試列表
                exams = crawler_module.get_exam_list_by_year(
                    session, year, task['keywords']
                )

                if not exams:
                    self._log(task_id, f"民國 {year} 年沒有找到符合條件的考試")
                    continue

                self._log(task_id, f"找到 {len(exams)} 個考試")

                # 下載每個考試
                for exam in exams:
                    if task['status'] == 'cancelled':
                        break

                    task['current_exam'] = exam['name']
                    self._log(task_id, f"下載考試: {exam['name']}")

                    # 使用並發或標準下載
                    if use_concurrent:
                        crawler_module.download_exam_concurrent(
                            session, exam, task['save_dir'], task['stats']
                        )
                    else:
                        crawler_module.download_exam(
                            session, exam, task['save_dir'], task['stats']
                        )

                # 更新進度
                task['progress'] = int((idx / total_years) * 100)

            # 完成
            if task['status'] != 'cancelled':
                task['status'] = 'completed'
                task['progress'] = 100
                task['completed_at'] = datetime.now().isoformat()
                self._log(task_id, f"任務完成！成功: {task['stats']['success']}, 失敗: {task['stats']['failed']}")

            session.close()

        except Exception as e:
            task['status'] = 'failed'
            task['error'] = str(e)
            self._log(task_id, f"任務失敗: {e}")

    def stop_task(self, task_id: str) -> bool:
        """
        停止爬蟲任務

        Args:
            task_id: 任務ID

        Returns:
            是否成功停止
        """
        with self.lock:
            if task_id not in self.tasks:
                return False

            task = self.tasks[task_id]

            if task['status'] != 'running':
                return False

            task['status'] = 'cancelled'
            task['cancelled_at'] = datetime.now().isoformat()
            self._log(task_id, "任務已停止")

        return True

    def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        """
        獲取任務信息

        Args:
            task_id: 任務ID

        Returns:
            任務信息字典，如果不存在則返回 None
        """
        with self.lock:
            return self.tasks.get(task_id)

    def get_all_tasks(self) -> List[Dict[str, Any]]:
        """
        獲取所有任務

        Returns:
            任務列表
        """
        with self.lock:
            tasks = list(self.tasks.values())
            # 按創建時間倒序排列
            tasks.sort(key=lambda x: x['created_at'], reverse=True)
            return tasks

    def delete_task(self, task_id: str) -> bool:
        """
        刪除任務

        Args:
            task_id: 任務ID

        Returns:
            是否成功刪除
        """
        with self.lock:
            if task_id not in self.tasks:
                return False

            del self.tasks[task_id]
            return True

    def _log(self, task_id: str, message: str):
        """
        記錄日誌

        Args:
            task_id: 任務ID
            message: 日誌消息
        """
        with self.lock:
            if task_id in self.tasks:
                self.tasks[task_id]['logs'].append({
                    'timestamp': datetime.now().isoformat(),
                    'message': message
                })

    def get_available_years(self) -> List[int]:
        """
        獲取可用年份列表

        Returns:
            年份列表
        """
        return crawler_module.get_available_years()

    def get_default_keywords(self) -> List[str]:
        """
        獲取默認關鍵字

        Returns:
            關鍵字列表
        """
        return [
            "警察人員考試",
            "一般警察人員考試",
            "司法人員考試",
            "國家安全情報人員考試",
            "移民行政人員考試"
        ]


# 全局服務實例
crawler_service = CrawlerService()
