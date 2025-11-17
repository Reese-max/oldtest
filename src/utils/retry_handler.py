#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
重試和錯誤恢復處理器
提供自動重試、指數退避、斷點續傳等功能
"""

import time
import functools
from typing import Callable, Any, Optional, Type, Tuple
from .logger import logger


def retry_with_backoff(
    max_retries: int = 3,
    initial_delay: float = 1.0,
    exponential: bool = True,
    exceptions: Tuple[Type[Exception], ...] = (Exception,),
    on_retry: Optional[Callable] = None
):
    """
    重試裝飾器（支持指數退避）

    Args:
        max_retries: 最大重試次數
        initial_delay: 初始延遲（秒）
        exponential: 是否使用指數退避
        exceptions: 要捕獲的異常類型
        on_retry: 重試時的回調函數

    Example:
        ```python
        @retry_with_backoff(max_retries=3, exponential=True)
        def process_pdf(pdf_path):
            # 處理邏輯
            pass
        ```
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            last_exception = None

            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)

                except exceptions as e:
                    last_exception = e

                    if attempt < max_retries:
                        # 計算延遲時間
                        if exponential:
                            delay = initial_delay * (2 ** attempt)
                        else:
                            delay = initial_delay

                        logger.warning(
                            f"⚠️  {func.__name__} 失敗 (嘗試 {attempt + 1}/{max_retries + 1}): {e}"
                        )
                        logger.info(f"   等待 {delay:.1f} 秒後重試...")

                        # 調用重試回調
                        if on_retry:
                            on_retry(attempt, e)

                        time.sleep(delay)
                    else:
                        logger.error(
                            f"❌ {func.__name__} 失敗 (已達最大重試次數): {e}"
                        )

            # 所有重試都失敗
            raise last_exception

        return wrapper
    return decorator


class CheckpointManager:
    """斷點續傳管理器"""

    def __init__(self, checkpoint_file: str = ".checkpoint.json"):
        """
        初始化斷點管理器

        Args:
            checkpoint_file: 斷點文件路徑
        """
        self.checkpoint_file = checkpoint_file
        self.logger = logger

    def save_checkpoint(self, data: dict):
        """
        保存斷點

        Args:
            data: 要保存的數據
        """
        import json

        try:
            with open(self.checkpoint_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            self.logger.debug(f"💾 斷點已保存: {self.checkpoint_file}")

        except Exception as e:
            self.logger.warning(f"斷點保存失敗: {e}")

    def load_checkpoint(self) -> Optional[dict]:
        """
        載入斷點

        Returns:
            斷點數據，如果不存在則返回 None
        """
        import json
        import os

        if not os.path.exists(self.checkpoint_file):
            return None

        try:
            with open(self.checkpoint_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            self.logger.info(f"📂 斷點已載入: {self.checkpoint_file}")
            return data

        except Exception as e:
            self.logger.warning(f"斷點載入失敗: {e}")
            return None

    def clear_checkpoint(self):
        """清除斷點文件"""
        import os

        if os.path.exists(self.checkpoint_file):
            try:
                os.remove(self.checkpoint_file)
                self.logger.debug(f"🗑️  斷點已清除: {self.checkpoint_file}")
            except Exception as e:
                self.logger.warning(f"斷點清除失敗: {e}")


class ErrorRecovery:
    """錯誤恢復處理器"""

    def __init__(self, max_retries: int = 3, retry_delay: int = 2):
        """
        初始化錯誤恢復處理器

        Args:
            max_retries: 最大重試次數
            retry_delay: 重試延遲（秒）
        """
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.logger = logger
        self.checkpoint = CheckpointManager()

    def process_with_recovery(
        self,
        tasks: list,
        process_func: Callable,
        save_interval: int = 10
    ) -> Tuple[list, list]:
        """
        帶錯誤恢復的批量處理

        Args:
            tasks: 任務列表
            process_func: 處理函數
            save_interval: 保存斷點的間隔

        Returns:
            (成功結果列表, 失敗任務列表)
        """
        # 載入斷點
        checkpoint_data = self.checkpoint.load_checkpoint()

        if checkpoint_data:
            completed = set(checkpoint_data.get('completed', []))
            self.logger.info(f"📂 從斷點恢復，已完成 {len(completed)} 個任務")
        else:
            completed = set()

        results = []
        failed = []

        for idx, task in enumerate(tasks):
            # 跳過已完成的任務
            task_id = getattr(task, 'task_id', idx)

            if task_id in completed:
                self.logger.debug(f"⏭️  跳過已完成任務: {task_id}")
                continue

            # 處理任務（帶重試）
            success, result = self._process_with_retry(task, process_func)

            if success:
                results.append(result)
                completed.add(task_id)
            else:
                failed.append((task, result))

            # 定期保存斷點
            if (idx + 1) % save_interval == 0:
                self.checkpoint.save_checkpoint({
                    'completed': list(completed),
                    'total': len(tasks),
                    'timestamp': time.time()
                })

        # 清除斷點
        if not failed:
            self.checkpoint.clear_checkpoint()
            self.logger.success("✅ 所有任務完成，斷點已清除")

        return results, failed

    def _process_with_retry(
        self,
        task: Any,
        process_func: Callable
    ) -> Tuple[bool, Any]:
        """
        處理單個任務（帶重試）

        Args:
            task: 任務
            process_func: 處理函數

        Returns:
            (是否成功, 結果)
        """
        last_error = None

        for attempt in range(self.max_retries + 1):
            try:
                result = process_func(task)
                return True, result

            except Exception as e:
                last_error = e

                if attempt < self.max_retries:
                    delay = self.retry_delay * (2 ** attempt)  # 指數退避

                    self.logger.warning(
                        f"⚠️  任務失敗 (嘗試 {attempt + 1}/{self.max_retries + 1}): {e}"
                    )
                    self.logger.info(f"   等待 {delay:.1f} 秒後重試...")

                    time.sleep(delay)

        # 所有重試都失敗
        self.logger.error(f"❌ 任務最終失敗: {last_error}")
        return False, last_error


def safe_execute(
    func: Callable,
    *args,
    default=None,
    log_error: bool = True,
    **kwargs
) -> Any:
    """
    安全執行函數（捕獲所有異常）

    Args:
        func: 要執行的函數
        *args: 位置參數
        default: 失敗時的默認返回值
        log_error: 是否記錄錯誤
        **kwargs: 關鍵字參數

    Returns:
        函數結果或默認值
    """
    try:
        return func(*args, **kwargs)
    except Exception as e:
        if log_error:
            logger.error(f"執行 {func.__name__} 失敗: {e}")
        return default


# 便捷函數
def create_error_recovery(max_retries: int = 3, retry_delay: int = 2) -> ErrorRecovery:
    """
    創建錯誤恢復處理器的便捷函數

    Args:
        max_retries: 最大重試次數
        retry_delay: 重試延遲（秒）

    Returns:
        ErrorRecovery: 錯誤恢復處理器
    """
    return ErrorRecovery(max_retries=max_retries, retry_delay=retry_delay)
