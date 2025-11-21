#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
性能監控系統
提供完整的性能監控、統計和分析功能
"""

import functools
import json
import os
import time
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional

import psutil

from .logger import logger


@dataclass
class PerformanceMetrics:
    """性能指標"""

    function_name: str
    start_time: float
    end_time: float
    duration: float
    memory_before_mb: float
    memory_after_mb: float
    memory_delta_mb: float
    cpu_percent: float
    timestamp: str
    success: bool = True
    error_message: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典"""
        return {
            "function_name": self.function_name,
            "duration": round(self.duration, 4),
            "memory_delta_mb": round(self.memory_delta_mb, 2),
            "cpu_percent": round(self.cpu_percent, 2),
            "timestamp": self.timestamp,
            "success": self.success,
            "error_message": self.error_message,
            "metadata": self.metadata,
        }


class PerformanceTimer:
    """性能計時器"""

    def __init__(self, name: str = ""):
        """
        初始化性能計時器

        Args:
            name: 計時器名稱
        """
        self.name = name
        self.start_time = None
        self.end_time = None
        self.duration = None
        self.process = psutil.Process(os.getpid())
        self.memory_before = None
        self.memory_after = None

    def __enter__(self):
        """進入上下文管理器"""
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """退出上下文管理器"""
        self.stop()
        return False

    def start(self):
        """開始計時"""
        self.memory_before = self.process.memory_info().rss / 1024 / 1024
        self.start_time = time.time()

    def stop(self):
        """停止計時"""
        self.end_time = time.time()
        self.memory_after = self.process.memory_info().rss / 1024 / 1024
        self.duration = self.end_time - self.start_time

    def get_duration(self) -> float:
        """獲取持續時間（秒）"""
        return self.duration if self.duration is not None else 0.0

    def get_memory_delta(self) -> float:
        """獲取記憶體變化（MB）"""
        if self.memory_before is not None and self.memory_after is not None:
            return self.memory_after - self.memory_before
        return 0.0

    def get_summary(self) -> str:
        """獲取摘要信息"""
        if self.duration is None:
            return f"{self.name}: 尚未完成"

        duration_str = f"{self.duration:.4f}秒"
        memory_delta = self.get_memory_delta()
        memory_str = f"{memory_delta:+.2f}MB"

        return f"{self.name}: {duration_str}, 記憶體變化: {memory_str}"


class PerformanceMonitor:
    """性能監控器"""

    def __init__(self):
        """初始化性能監控器"""
        self.metrics: List[PerformanceMetrics] = []
        self.function_stats: Dict[str, List[float]] = defaultdict(list)
        self.logger = logger
        self.process = psutil.Process(os.getpid())

    def monitor(
        self,
        func: Optional[Callable] = None,
        *,
        log_result: bool = True,
        track_memory: bool = True,
        track_cpu: bool = True,
    ):
        """
        性能監控裝飾器

        Args:
            func: 被裝飾的函數
            log_result: 是否記錄結果
            track_memory: 是否追蹤記憶體
            track_cpu: 是否追蹤 CPU

        Example:
            ```python
            monitor = PerformanceMonitor()

            @monitor.monitor()
            def process_pdf(pdf_path):
                # 處理邏輯
                pass

            # 自動記錄性能指標
            ```
        """

        def decorator(f):
            @functools.wraps(f)
            def wrapper(*args, **kwargs):
                # 記錄開始狀態
                start_time = time.time()
                memory_before = 0
                if track_memory:
                    memory_before = self.process.memory_info().rss / 1024 / 1024

                cpu_percent_start = 0
                if track_cpu:
                    cpu_percent_start = self.process.cpu_percent()

                success = True
                error_message = ""

                try:
                    # 執行函數
                    result = f(*args, **kwargs)
                    return result
                except Exception as e:
                    success = False
                    error_message = str(e)
                    raise
                finally:
                    # 記錄結束狀態
                    end_time = time.time()
                    duration = end_time - start_time

                    memory_after = 0
                    memory_delta = 0
                    if track_memory:
                        memory_after = self.process.memory_info().rss / 1024 / 1024
                        memory_delta = memory_after - memory_before

                    cpu_percent = 0
                    if track_cpu:
                        cpu_percent = self.process.cpu_percent()

                    # 創建性能指標
                    metrics = PerformanceMetrics(
                        function_name=f.__name__,
                        start_time=start_time,
                        end_time=end_time,
                        duration=duration,
                        memory_before_mb=memory_before,
                        memory_after_mb=memory_after,
                        memory_delta_mb=memory_delta,
                        cpu_percent=cpu_percent,
                        timestamp=datetime.now().isoformat(),
                        success=success,
                        error_message=error_message,
                    )

                    # 記錄指標
                    self.metrics.append(metrics)
                    self.function_stats[f.__name__].append(duration)

                    # 記錄日誌
                    if log_result:
                        if success:
                            self.logger.debug(
                                f"⏱️  {f.__name__}: {duration:.4f}秒, "
                                f"記憶體: {memory_delta:+.2f}MB, "
                                f"CPU: {cpu_percent:.1f}%"
                            )
                        else:
                            self.logger.error(f"❌ {f.__name__}: 失敗 ({error_message}), " f"耗時: {duration:.4f}秒")

            return wrapper

        if func is None:
            return decorator
        else:
            return decorator(func)

    def record_metric(self, metrics: PerformanceMetrics):
        """
        手動記錄性能指標

        Args:
            metrics: 性能指標對象
        """
        self.metrics.append(metrics)
        self.function_stats[metrics.function_name].append(metrics.duration)

    def get_function_stats(self, function_name: str) -> Dict[str, Any]:
        """
        獲取函數統計信息

        Args:
            function_name: 函數名稱

        Returns:
            統計信息字典
        """
        durations = self.function_stats.get(function_name, [])

        if not durations:
            return {
                "function_name": function_name,
                "call_count": 0,
                "total_time": 0,
                "avg_time": 0,
                "min_time": 0,
                "max_time": 0,
            }

        return {
            "function_name": function_name,
            "call_count": len(durations),
            "total_time": sum(durations),
            "avg_time": sum(durations) / len(durations),
            "min_time": min(durations),
            "max_time": max(durations),
        }

    def get_all_stats(self) -> Dict[str, Dict[str, Any]]:
        """
        獲取所有函數的統計信息

        Returns:
            所有函數的統計信息
        """
        return {func_name: self.get_function_stats(func_name) for func_name in self.function_stats.keys()}

    def get_metrics_summary(self) -> Dict[str, Any]:
        """
        獲取性能指標總結

        Returns:
            總結信息
        """
        if not self.metrics:
            return {"total_metrics": 0, "total_duration": 0, "total_memory_delta": 0, "avg_cpu": 0, "success_rate": 0}

        total_duration = sum(m.duration for m in self.metrics)
        total_memory_delta = sum(m.memory_delta_mb for m in self.metrics)
        avg_cpu = sum(m.cpu_percent for m in self.metrics) / len(self.metrics)
        success_count = sum(1 for m in self.metrics if m.success)

        return {
            "total_metrics": len(self.metrics),
            "total_duration": total_duration,
            "total_memory_delta": total_memory_delta,
            "avg_cpu": avg_cpu,
            "success_rate": (success_count / len(self.metrics)) * 100,
        }

    def generate_report(self, output_file: Optional[str] = None) -> str:
        """
        生成性能報告

        Args:
            output_file: 輸出文件路徑（可選）

        Returns:
            報告內容
        """
        report_lines = []
        report_lines.append("=" * 80)
        report_lines.append("性能監控報告")
        report_lines.append("=" * 80)
        report_lines.append("")

        # 總體統計
        summary = self.get_metrics_summary()
        report_lines.append("## 總體統計")
        report_lines.append(f"總記錄數: {summary['total_metrics']}")
        report_lines.append(f"總耗時: {summary['total_duration']:.4f}秒")
        report_lines.append(f"總記憶體變化: {summary['total_memory_delta']:+.2f}MB")
        report_lines.append(f"平均CPU: {summary['avg_cpu']:.2f}%")
        report_lines.append(f"成功率: {summary['success_rate']:.2f}%")
        report_lines.append("")

        # 函數統計
        report_lines.append("## 函數統計")
        all_stats = self.get_all_stats()

        for func_name, stats in sorted(all_stats.items(), key=lambda x: x[1]["total_time"], reverse=True):
            report_lines.append(f"\n### {func_name}")
            report_lines.append(f"  調用次數: {stats['call_count']}")
            report_lines.append(f"  總耗時: {stats['total_time']:.4f}秒")
            report_lines.append(f"  平均耗時: {stats['avg_time']:.4f}秒")
            report_lines.append(f"  最短耗時: {stats['min_time']:.4f}秒")
            report_lines.append(f"  最長耗時: {stats['max_time']:.4f}秒")

        report_lines.append("")
        report_lines.append("=" * 80)

        report = "\n".join(report_lines)

        # 輸出到文件
        if output_file:
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(report)
            self.logger.info(f"性能報告已保存到: {output_file}")

        return report

    def export_metrics(self, output_file: str):
        """
        導出性能指標到 JSON 文件

        Args:
            output_file: 輸出文件路徑
        """
        metrics_data = [m.to_dict() for m in self.metrics]

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(metrics_data, f, ensure_ascii=False, indent=2)

        self.logger.info(f"性能指標已導出到: {output_file}")

    def clear_metrics(self):
        """清除所有性能指標"""
        self.metrics.clear()
        self.function_stats.clear()
        self.logger.debug("性能指標已清除")


# 全局性能監控器實例
global_monitor = PerformanceMonitor()


def monitor_performance(func: Optional[Callable] = None, *, log_result: bool = True):
    """
    便捷的性能監控裝飾器（使用全局監控器）

    Args:
        func: 被裝飾的函數
        log_result: 是否記錄結果

    Example:
        ```python
        @monitor_performance
        def process_file(file_path):
            # 處理邏輯
            pass
        ```
    """
    return global_monitor.monitor(func, log_result=log_result)


def get_global_report() -> str:
    """
    獲取全局性能報告

    Returns:
        性能報告
    """
    return global_monitor.generate_report()


def export_global_metrics(output_file: str):
    """
    導出全局性能指標

    Args:
        output_file: 輸出文件路徑
    """
    global_monitor.export_metrics(output_file)
