#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
性能優化模組 - 優化處理效能
減少記憶體使用和處理時間，提升系統整體性能
"""

import os
import gc
import time
import psutil
import logging
from typing import List, Dict, Any, Optional, Tuple, Callable
from functools import wraps
import threading
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import multiprocessing as mp

class PerformanceOptimizer:
    """性能優化器"""
    
    def __init__(self, max_workers: Optional[int] = None):
        self.logger = logging.getLogger('PerformanceOptimizer')
        self.max_workers = max_workers or min(32, (os.cpu_count() or 1) + 4)
        self.memory_threshold = 0.8  # 記憶體使用率閾值
        self.processing_stats = {
            'total_processed': 0,
            'total_time': 0.0,
            'memory_peak': 0.0,
            'cpu_peak': 0.0
        }
    
    def monitor_performance(self, func: Callable) -> Callable:
        """性能監控裝飾器"""
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            start_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
            start_cpu = psutil.Process().cpu_percent()
            
            try:
                result = func(*args, **kwargs)
                
                end_time = time.time()
                end_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
                end_cpu = psutil.Process().cpu_percent()
                
                # 更新統計資訊
                processing_time = end_time - start_time
                memory_used = end_memory - start_memory
                
                self.processing_stats['total_processed'] += 1
                self.processing_stats['total_time'] += processing_time
                self.processing_stats['memory_peak'] = max(self.processing_stats['memory_peak'], end_memory)
                self.processing_stats['cpu_peak'] = max(self.processing_stats['cpu_peak'], end_cpu)
                
                self.logger.info(f"函數 {func.__name__} 執行完成: {processing_time:.2f}s, 記憶體: {memory_used:.2f}MB")
                
                return result
                
            except Exception as e:
                self.logger.error(f"函數 {func.__name__} 執行失敗: {e}")
                raise
        
        return wrapper
    
    def optimize_memory_usage(self, func: Callable) -> Callable:
        """記憶體使用優化裝飾器"""
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 檢查記憶體使用率
            memory_percent = psutil.virtual_memory().percent / 100
            if memory_percent > self.memory_threshold:
                self.logger.warning(f"記憶體使用率過高: {memory_percent:.1%}, 執行垃圾回收")
                gc.collect()
            
            try:
                result = func(*args, **kwargs)
                
                # 執行後清理記憶體
                gc.collect()
                
                return result
                
            except Exception as e:
                self.logger.error(f"記憶體優化失敗: {e}")
                raise
        
        return wrapper
    
    def parallel_processing(self, items: List[Any], process_func: Callable, 
                          use_multiprocessing: bool = False) -> List[Any]:
        """
        並行處理
        
        Args:
            items: 要處理的項目列表
            process_func: 處理函數
            use_multiprocessing: 是否使用多進程
            
        Returns:
            處理結果列表
        """
        if not items:
            return []
        
        self.logger.info(f"開始並行處理 {len(items)} 個項目")
        
        start_time = time.time()
        
        try:
            if use_multiprocessing and len(items) > 1:
                # 使用多進程
                with ProcessPoolExecutor(max_workers=self.max_workers) as executor:
                    results = list(executor.map(process_func, items))
            else:
                # 使用多線程
                with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                    results = list(executor.map(process_func, items))
            
            processing_time = time.time() - start_time
            self.logger.info(f"並行處理完成: {processing_time:.2f}s")
            
            return results
            
        except Exception as e:
            self.logger.error(f"並行處理失敗: {e}")
            # 回退到順序處理
            return [process_func(item) for item in items]
    
    def batch_processing(self, items: List[Any], batch_size: int = 100, 
                        process_func: Callable = None) -> List[Any]:
        """
        批次處理
        
        Args:
            items: 要處理的項目列表
            batch_size: 批次大小
            process_func: 處理函數
            
        Returns:
            處理結果列表
        """
        if not items:
            return []
        
        if not process_func:
            return items
        
        self.logger.info(f"開始批次處理 {len(items)} 個項目，批次大小: {batch_size}")
        
        results = []
        total_batches = (len(items) + batch_size - 1) // batch_size
        
        for i in range(0, len(items), batch_size):
            batch = items[i:i + batch_size]
            batch_num = i // batch_size + 1
            
            self.logger.debug(f"處理批次 {batch_num}/{total_batches}")
            
            try:
                batch_result = process_func(batch)
                if isinstance(batch_result, list):
                    results.extend(batch_result)
                else:
                    results.append(batch_result)
                
                # 批次間清理記憶體
                if batch_num % 10 == 0:
                    gc.collect()
                    
            except Exception as e:
                self.logger.error(f"批次 {batch_num} 處理失敗: {e}")
                continue
        
        self.logger.info(f"批次處理完成: {len(results)} 個結果")
        return results
    
    def optimize_text_processing(self, text: str) -> str:
        """優化文字處理"""
        if not text:
            return text
        
        # 移除多餘空白
        text = re.sub(r'\s+', ' ', text)
        
        # 移除多餘換行
        text = re.sub(r'\n\s*\n', '\n', text)
        
        # 移除頁碼和頁次
        text = re.sub(r'第\s*\d+\s*頁', '', text)
        text = re.sub(r'頁次：\s*\d+', '', text)
        
        return text.strip()
    
    def optimize_regex_patterns(self, patterns: List[str]) -> List[str]:
        """優化正則表達式模式"""
        optimized_patterns = []
        
        for pattern in patterns:
            try:
                # 編譯模式以檢查有效性
                re.compile(pattern)
                
                # 優化常見模式
                optimized_pattern = pattern
                
                # 移除不必要的捕獲組
                optimized_pattern = re.sub(r'\(\?\:\s*', '(', optimized_pattern)
                
                # 優化量詞
                optimized_pattern = re.sub(r'\+\?', '+', optimized_pattern)
                optimized_pattern = re.sub(r'\*\?', '*', optimized_pattern)
                
                optimized_patterns.append(optimized_pattern)
                
            except re.error as e:
                self.logger.warning(f"無效的正則表達式模式: {pattern} - {e}")
                continue
        
        return optimized_patterns
    
    def get_system_info(self) -> Dict[str, Any]:
        """獲取系統資訊"""
        memory = psutil.virtual_memory()
        cpu_count = os.cpu_count()
        
        return {
            'cpu_count': cpu_count,
            'max_workers': self.max_workers,
            'memory_total': memory.total / 1024 / 1024 / 1024,  # GB
            'memory_available': memory.available / 1024 / 1024 / 1024,  # GB
            'memory_percent': memory.percent,
            'processing_stats': self.processing_stats.copy()
        }
    
    def optimize_file_operations(self, file_path: str, operation: str = 'read') -> Any:
        """優化檔案操作"""
        if operation == 'read':
            return self._optimized_read_file(file_path)
        elif operation == 'write':
            return self._optimized_write_file(file_path)
        else:
            raise ValueError(f"不支援的操作: {operation}")
    
    def _optimized_read_file(self, file_path: str) -> str:
        """優化的檔案讀取"""
        try:
            # 檢查檔案大小
            file_size = os.path.getsize(file_path)
            if file_size > 100 * 1024 * 1024:  # 100MB
                self.logger.warning(f"檔案過大: {file_size / 1024 / 1024:.2f}MB")
            
            # 使用適當的緩衝區大小
            buffer_size = min(8192, file_size)
            
            with open(file_path, 'r', encoding='utf-8', buffering=buffer_size) as f:
                content = f.read()
            
            return content
            
        except Exception as e:
            self.logger.error(f"檔案讀取失敗: {e}")
            raise
    
    def _optimized_write_file(self, file_path: str, content: str) -> None:
        """優化的檔案寫入"""
        try:
            # 確保目錄存在
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            # 使用適當的緩衝區大小
            buffer_size = min(8192, len(content))
            
            with open(file_path, 'w', encoding='utf-8', buffering=buffer_size) as f:
                f.write(content)
            
        except Exception as e:
            self.logger.error(f"檔案寫入失敗: {e}")
            raise
    
    def cleanup_resources(self):
        """清理資源"""
        self.logger.info("開始清理資源")
        
        # 強制垃圾回收
        gc.collect()
        
        # 重置統計資訊
        self.processing_stats = {
            'total_processed': 0,
            'total_time': 0.0,
            'memory_peak': 0.0,
            'cpu_peak': 0.0
        }
        
        self.logger.info("資源清理完成")
    
    def get_performance_report(self) -> Dict[str, Any]:
        """獲取性能報告"""
        system_info = self.get_system_info()
        
        report = {
            'timestamp': time.time(),
            'system_info': system_info,
            'performance_metrics': {
                'average_processing_time': (
                    self.processing_stats['total_time'] / self.processing_stats['total_processed']
                    if self.processing_stats['total_processed'] > 0 else 0
                ),
                'total_processed': self.processing_stats['total_processed'],
                'total_time': self.processing_stats['total_time'],
                'memory_peak_mb': self.processing_stats['memory_peak'],
                'cpu_peak_percent': self.processing_stats['cpu_peak']
            }
        }
        
        return report

# 全域性能優化器實例
performance_optimizer = PerformanceOptimizer()

# 便捷函數
def monitor_performance(func):
    """性能監控裝飾器"""
    return performance_optimizer.monitor_performance(func)

def optimize_memory_usage(func):
    """記憶體使用優化裝飾器"""
    return performance_optimizer.optimize_memory_usage(func)

def parallel_process(items, process_func, use_multiprocessing=False):
    """並行處理函數"""
    return performance_optimizer.parallel_processing(items, process_func, use_multiprocessing)

def batch_process(items, batch_size=100, process_func=None):
    """批次處理函數"""
    return performance_optimizer.batch_processing(items, batch_size, process_func)

def main():
    """測試函數"""
    optimizer = PerformanceOptimizer()
    
    # 測試性能監控
    @monitor_performance
    @optimize_memory_usage
    def test_function(data):
        time.sleep(0.1)  # 模擬處理時間
        return [x * 2 for x in data]
    
    # 測試並行處理
    test_data = list(range(100))
    results = parallel_process(test_data, test_function)
    
    print(f"並行處理結果: {len(results)} 個項目")
    
    # 獲取性能報告
    report = optimizer.get_performance_report()
    print(f"性能報告: {report}")

if __name__ == "__main__":
    main()