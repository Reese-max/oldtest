#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
並發處理器
支持多線程/多進程批量處理 PDF 文件，大幅提升處理速度
"""

import os
import time
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed
from typing import List, Dict, Any, Callable, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
from threading import Lock
from .logger import logger


@dataclass
class ProcessingTask:
    """處理任務"""
    task_id: int
    pdf_path: str
    answer_pdf_path: Optional[str] = None
    corrected_answer_pdf_path: Optional[str] = None
    output_dir: str = "output"


@dataclass
class TaskResult:
    """任務結果"""
    task_id: int
    pdf_path: str
    success: bool
    result: Dict[str, Any]
    error: Optional[str] = None
    duration: float = 0.0
    start_time: Optional[str] = None
    end_time: Optional[str] = None


class ProgressTracker:
    """進度追蹤器（線程安全）"""

    def __init__(self, total_tasks: int):
        self.total_tasks = total_tasks
        self.completed = 0
        self.successful = 0
        self.failed = 0
        self.lock = Lock()
        self.start_time = time.time()

    def update(self, success: bool):
        """更新進度"""
        with self.lock:
            self.completed += 1
            if success:
                self.successful += 1
            else:
                self.failed += 1

            # 計算進度
            progress = (self.completed / self.total_tasks) * 100
            elapsed = time.time() - self.start_time
            avg_time = elapsed / self.completed if self.completed > 0 else 0
            remaining = avg_time * (self.total_tasks - self.completed)

            # 輸出進度
            logger.info(
                f"進度: {self.completed}/{self.total_tasks} ({progress:.1f}%) | "
                f"成功: {self.successful} | 失敗: {self.failed} | "
                f"預計剩餘: {remaining:.1f}秒"
            )

    def get_summary(self) -> Dict[str, Any]:
        """獲取摘要"""
        total_time = time.time() - self.start_time
        return {
            'total_tasks': self.total_tasks,
            'completed': self.completed,
            'successful': self.successful,
            'failed': self.failed,
            'success_rate': (self.successful / self.total_tasks * 100) if self.total_tasks > 0 else 0,
            'total_time': total_time,
            'avg_time_per_task': total_time / self.completed if self.completed > 0 else 0
        }


class ConcurrentProcessor:
    """並發處理器 - 支持多線程/多進程批量處理"""

    def __init__(self, max_workers: int = None, use_processes: bool = False):
        """
        初始化並發處理器

        Args:
            max_workers: 最大工作線程/進程數（默認: CPU 核心數）
            use_processes: 是否使用多進程（默認: False，使用多線程）

        Note:
            - 多線程適合 I/O 密集型任務（PDF 讀取）
            - 多進程適合 CPU 密集型任務（OCR 處理）
            - 建議 I/O 操作使用線程，計算密集使用進程
        """
        self.max_workers = max_workers or os.cpu_count() or 4
        self.use_processes = use_processes
        self.logger = logger

        self.logger.info(
            f"初始化並發處理器: "
            f"{'多進程' if use_processes else '多線程'} 模式, "
            f"{self.max_workers} 個 worker"
        )

    def process_batch(
        self,
        tasks: List[ProcessingTask],
        processor_func: Callable[[ProcessingTask], Dict[str, Any]],
        fail_fast: bool = False
    ) -> List[TaskResult]:
        """
        批量處理任務

        Args:
            tasks: 任務列表
            processor_func: 處理函數
            fail_fast: 是否在遇到錯誤時立即停止（默認: False）

        Returns:
            任務結果列表

        Example:
            ```python
            def process_task(task):
                processor = ArchaeologyProcessor()
                return processor.process_pdf(
                    task.pdf_path,
                    task.answer_pdf_path,
                    task.corrected_answer_pdf_path,
                    task.output_dir
                )

            results = concurrent_processor.process_batch(tasks, process_task)
            ```
        """
        if not tasks:
            self.logger.warning("任務列表為空")
            return []

        self.logger.info(f"開始批量處理: {len(tasks)} 個任務")

        # 初始化進度追蹤
        progress = ProgressTracker(len(tasks))
        results = []

        # 選擇執行器
        ExecutorClass = ProcessPoolExecutor if self.use_processes else ThreadPoolExecutor

        try:
            with ExecutorClass(max_workers=self.max_workers) as executor:
                # 提交所有任務
                future_to_task = {
                    executor.submit(self._process_single_task, task, processor_func): task
                    for task in tasks
                }

                # 收集結果
                for future in as_completed(future_to_task):
                    task = future_to_task[future]

                    try:
                        result = future.result()
                        results.append(result)
                        progress.update(result.success)

                        # 失敗快速退出
                        if fail_fast and not result.success:
                            self.logger.error(f"任務失敗，停止處理: {result.pdf_path}")
                            executor.shutdown(wait=False, cancel_futures=True)
                            break

                    except Exception as e:
                        error_msg = f"任務執行異常: {task.pdf_path} - {e}"
                        self.logger.error(error_msg)

                        # 記錄失敗結果
                        result = TaskResult(
                            task_id=task.task_id,
                            pdf_path=task.pdf_path,
                            success=False,
                            result={},
                            error=str(e)
                        )
                        results.append(result)
                        progress.update(False)

                        if fail_fast:
                            executor.shutdown(wait=False, cancel_futures=True)
                            break

        except KeyboardInterrupt:
            self.logger.warning("收到中斷信號，停止處理...")
            return results

        # 輸出摘要
        summary = progress.get_summary()
        self._log_summary(summary)

        return results

    def _process_single_task(
        self,
        task: ProcessingTask,
        processor_func: Callable[[ProcessingTask], Dict[str, Any]]
    ) -> TaskResult:
        """
        處理單個任務（內部方法）

        Args:
            task: 處理任務
            processor_func: 處理函數

        Returns:
            任務結果
        """
        start_time = datetime.now()
        start_timestamp = start_time.isoformat()

        try:
            # 執行處理
            result = processor_func(task)

            # 計算耗時
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()

            return TaskResult(
                task_id=task.task_id,
                pdf_path=task.pdf_path,
                success=result.get('success', False),
                result=result,
                error=result.get('message') if not result.get('success') else None,
                duration=duration,
                start_time=start_timestamp,
                end_time=end_time.isoformat()
            )

        except Exception as e:
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()

            self.logger.error(f"處理任務失敗: {task.pdf_path} - {e}")

            return TaskResult(
                task_id=task.task_id,
                pdf_path=task.pdf_path,
                success=False,
                result={},
                error=str(e),
                duration=duration,
                start_time=start_timestamp,
                end_time=end_time.isoformat()
            )

    def _log_summary(self, summary: Dict[str, Any]):
        """輸出處理摘要"""
        self.logger.info("=" * 60)
        self.logger.info("📊 批量處理摘要")
        self.logger.info("=" * 60)
        self.logger.info(f"總任務數: {summary['total_tasks']}")
        self.logger.info(f"完成數: {summary['completed']}")
        self.logger.info(f"成功數: {summary['successful']}")
        self.logger.info(f"失敗數: {summary['failed']}")
        self.logger.info(f"成功率: {summary['success_rate']:.1f}%")
        self.logger.info(f"總耗時: {summary['total_time']:.2f} 秒")
        self.logger.info(f"平均耗時: {summary['avg_time_per_task']:.2f} 秒/任務")

        if summary['successful'] > 0:
            speedup = summary['total_time'] / (summary['avg_time_per_task'] * summary['total_tasks'])
            self.logger.info(f"加速比: {1/speedup:.2f}x (並發 vs 串行)")

        self.logger.info("=" * 60)

    def process_directory(
        self,
        input_dir: str,
        output_dir: str,
        processor_func: Callable[[ProcessingTask], Dict[str, Any]],
        pattern: str = "*.pdf",
        recursive: bool = True
    ) -> Tuple[List[TaskResult], Dict[str, Any]]:
        """
        處理目錄中的所有 PDF 文件

        Args:
            input_dir: 輸入目錄
            output_dir: 輸出目錄
            processor_func: 處理函數
            pattern: 文件匹配模式（默認: "*.pdf"）
            recursive: 是否遞歸搜索子目錄（默認: True）

        Returns:
            (任務結果列表, 處理摘要)
        """
        import glob

        self.logger.info(f"掃描目錄: {input_dir}")

        # 查找 PDF 文件
        if recursive:
            pdf_files = glob.glob(os.path.join(input_dir, "**", pattern), recursive=True)
        else:
            pdf_files = glob.glob(os.path.join(input_dir, pattern))

        if not pdf_files:
            self.logger.warning(f"目錄中未找到 PDF 文件: {input_dir}")
            return [], {}

        self.logger.info(f"找到 {len(pdf_files)} 個 PDF 文件")

        # 創建任務
        tasks = []
        for idx, pdf_path in enumerate(pdf_files):
            # 查找對應的答案文件
            base_name = os.path.splitext(pdf_path)[0]
            answer_pdf = f"{base_name}_答案.pdf"
            corrected_answer_pdf = f"{base_name}_更正答案.pdf"

            task = ProcessingTask(
                task_id=idx,
                pdf_path=pdf_path,
                answer_pdf_path=answer_pdf if os.path.exists(answer_pdf) else None,
                corrected_answer_pdf_path=corrected_answer_pdf if os.path.exists(corrected_answer_pdf) else None,
                output_dir=output_dir
            )
            tasks.append(task)

        # 批量處理
        results = self.process_batch(tasks, processor_func)

        # 生成詳細摘要
        summary = self._generate_detailed_summary(results)

        return results, summary

    def _generate_detailed_summary(self, results: List[TaskResult]) -> Dict[str, Any]:
        """生成詳細摘要"""
        successful_results = [r for r in results if r.success]
        failed_results = [r for r in results if not r.success]

        total_questions = sum(
            r.result.get('questions_count', 0)
            for r in successful_results
        )

        total_time = sum(r.duration for r in results)

        summary = {
            'total_files': len(results),
            'successful': len(successful_results),
            'failed': len(failed_results),
            'total_questions': total_questions,
            'total_time': total_time,
            'avg_time_per_file': total_time / len(results) if results else 0,
            'failed_files': [r.pdf_path for r in failed_results],
            'success_rate': (len(successful_results) / len(results) * 100) if results else 0
        }

        return summary


def create_processor(max_workers: int = None, use_processes: bool = False) -> ConcurrentProcessor:
    """
    創建並發處理器的便捷函數

    Args:
        max_workers: 最大工作線程/進程數
        use_processes: 是否使用多進程

    Returns:
        並發處理器實例
    """
    return ConcurrentProcessor(max_workers=max_workers, use_processes=use_processes)
