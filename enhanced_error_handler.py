#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
強化版錯誤處理和日誌系統
"""

import os
import sys
import traceback
import logging
import json
from datetime import datetime
from typing import Any, Dict, List, Optional, Callable, Union
from dataclasses import dataclass, asdict
from enum import Enum
from functools import wraps
import threading

class LogLevel(Enum):
    """日誌等級枚舉"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

class ErrorType(Enum):
    """錯誤類型枚舉"""
    VALIDATION_ERROR = "validation_error"
    PARSING_ERROR = "parsing_error"
    FILE_ERROR = "file_error"
    MEMORY_ERROR = "memory_error"
    NETWORK_ERROR = "network_error"
    CONFIGURATION_ERROR = "configuration_error"
    UNKNOWN_ERROR = "unknown_error"

@dataclass
class ErrorContext:
    """錯誤上下文資料結構"""
    error_type: ErrorType
    error_message: str
    function_name: str
    line_number: int
    timestamp: datetime
    thread_id: int
    process_id: int
    additional_data: Dict[str, Any]
    stack_trace: str

@dataclass
class LogEntry:
    """日誌條目資料結構"""
    level: LogLevel
    message: str
    timestamp: datetime
    function_name: str
    line_number: int
    thread_id: int
    process_id: int
    additional_data: Dict[str, Any]

class EnhancedLogger:
    """強化版日誌記錄器"""
    
    def __init__(self, name: str, log_file: Optional[str] = None, 
                 log_level: LogLevel = LogLevel.INFO):
        self.name = name
        self.log_file = log_file
        self.log_level = log_level
        self.thread_local = threading.local()
        
        # 設定日誌格式
        self.formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
        )
        
        # 建立日誌記錄器
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, log_level.value))
        
        # 清除現有的處理器
        self.logger.handlers.clear()
        
        # 控制台處理器
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(self.formatter)
        self.logger.addHandler(console_handler)
        
        # 檔案處理器
        if log_file:
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setFormatter(self.formatter)
            self.logger.addHandler(file_handler)
        
        # 防止重複日誌
        self.logger.propagate = False
    
    def _get_caller_info(self) -> tuple:
        """取得呼叫者資訊"""
        frame = sys._getframe(2)
        return frame.f_code.co_name, frame.f_lineno
    
    def debug(self, message: str, **kwargs):
        """記錄DEBUG等級日誌"""
        if self.log_level.value <= LogLevel.DEBUG.value:
            func_name, line_num = self._get_caller_info()
            self._log(LogLevel.DEBUG, message, func_name, line_num, kwargs)
    
    def info(self, message: str, **kwargs):
        """記錄INFO等級日誌"""
        if self.log_level.value <= LogLevel.INFO.value:
            func_name, line_num = self._get_caller_info()
            self._log(LogLevel.INFO, message, func_name, line_num, kwargs)
    
    def warning(self, message: str, **kwargs):
        """記錄WARNING等級日誌"""
        if self.log_level.value <= LogLevel.WARNING.value:
            func_name, line_num = self._get_caller_info()
            self._log(LogLevel.WARNING, message, func_name, line_num, kwargs)
    
    def error(self, message: str, **kwargs):
        """記錄ERROR等級日誌"""
        if self.log_level.value <= LogLevel.ERROR.value:
            func_name, line_num = self._get_caller_info()
            self._log(LogLevel.ERROR, message, func_name, line_num, kwargs)
    
    def critical(self, message: str, **kwargs):
        """記錄CRITICAL等級日誌"""
        if self.log_level.value <= LogLevel.CRITICAL.value:
            func_name, line_num = self._get_caller_info()
            self._log(LogLevel.CRITICAL, message, func_name, line_num, kwargs)
    
    def _log(self, level: LogLevel, message: str, func_name: str, 
             line_num: int, additional_data: Dict[str, Any]):
        """內部日誌記錄方法"""
        log_entry = LogEntry(
            level=level,
            message=message,
            timestamp=datetime.now(),
            function_name=func_name,
            line_number=line_num,
            thread_id=threading.get_ident(),
            process_id=os.getpid(),
            additional_data=additional_data
        )
        
        # 記錄到標準日誌系統
        log_method = getattr(self.logger, level.value.lower())
        log_method(f"{message} | {json.dumps(additional_data, ensure_ascii=False)}")
    
    def set_level(self, level: LogLevel):
        """設定日誌等級"""
        self.log_level = level
        self.logger.setLevel(getattr(logging, level.value))

class ErrorHandler:
    """強化版錯誤處理器"""
    
    def __init__(self, logger: EnhancedLogger):
        self.logger = logger
        self.error_history: List[ErrorContext] = []
        self.max_error_history = 1000
    
    def handle_error(self, error: Exception, error_type: ErrorType = ErrorType.UNKNOWN_ERROR,
                    additional_data: Optional[Dict[str, Any]] = None) -> ErrorContext:
        """處理錯誤"""
        # 取得錯誤上下文
        frame = sys._getframe(1)
        func_name = frame.f_code.co_name
        line_number = frame.f_lineno
        
        # 建立錯誤上下文
        error_context = ErrorContext(
            error_type=error_type,
            error_message=str(error),
            function_name=func_name,
            line_number=line_number,
            timestamp=datetime.now(),
            thread_id=threading.get_ident(),
            process_id=os.getpid(),
            additional_data=additional_data or {},
            stack_trace=traceback.format_exc()
        )
        
        # 記錄錯誤
        self.logger.error(
            f"錯誤發生: {error_type.value}",
            error_message=str(error),
            function_name=func_name,
            line_number=line_number,
            **additional_data or {}
        )
        
        # 儲存錯誤歷史
        self.error_history.append(error_context)
        if len(self.error_history) > self.max_error_history:
            self.error_history.pop(0)
        
        return error_context
    
    def get_error_statistics(self) -> Dict[str, Any]:
        """取得錯誤統計"""
        if not self.error_history:
            return {}
        
        error_types = {}
        for error in self.error_history:
            error_type = error.error_type.value
            error_types[error_type] = error_types.get(error_type, 0) + 1
        
        return {
            'total_errors': len(self.error_history),
            'error_types': error_types,
            'recent_errors': len([e for e in self.error_history 
                                if (datetime.now() - e.timestamp).seconds < 3600])
        }
    
    def clear_error_history(self):
        """清理錯誤歷史"""
        self.error_history.clear()

def error_handler(error_type: ErrorType = ErrorType.UNKNOWN_ERROR, 
                 reraise: bool = False, 
                 default_return: Any = None):
    """錯誤處理裝飾器"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                # 建立錯誤處理器實例
                logger = EnhancedLogger(func.__module__)
                handler = ErrorHandler(logger)
                
                # 處理錯誤
                error_context = handler.handle_error(e, error_type)
                
                if reraise:
                    raise
                else:
                    return default_return
        return wrapper
    return decorator

class RetryHandler:
    """重試處理器"""
    
    def __init__(self, max_retries: int = 3, delay: float = 1.0, 
                 backoff_factor: float = 2.0):
        self.max_retries = max_retries
        self.delay = delay
        self.backoff_factor = backoff_factor
    
    def retry(self, func: Callable, *args, **kwargs) -> Any:
        """重試執行函數"""
        last_exception = None
        
        for attempt in range(self.max_retries + 1):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                last_exception = e
                
                if attempt < self.max_retries:
                    wait_time = self.delay * (self.backoff_factor ** attempt)
                    print(f"⚠️ 嘗試 {attempt + 1} 失敗，{wait_time:.2f} 秒後重試: {e}")
                    import time
                    time.sleep(wait_time)
                else:
                    print(f"❌ 重試 {self.max_retries} 次後仍然失敗: {e}")
        
        raise last_exception

class CircuitBreaker:
    """斷路器模式"""
    
    def __init__(self, failure_threshold: int = 5, timeout: float = 60.0):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
    
    def call(self, func: Callable, *args, **kwargs) -> Any:
        """透過斷路器呼叫函數"""
        if self.state == "OPEN":
            if self._should_attempt_reset():
                self.state = "HALF_OPEN"
            else:
                raise Exception("斷路器開啟，拒絕呼叫")
        
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise e
    
    def _should_attempt_reset(self) -> bool:
        """判斷是否應該嘗試重置"""
        return (datetime.now() - self.last_failure_time).total_seconds() >= self.timeout
    
    def _on_success(self):
        """成功時的回調"""
        self.failure_count = 0
        self.state = "CLOSED"
    
    def _on_failure(self):
        """失敗時的回調"""
        self.failure_count += 1
        self.last_failure_time = datetime.now()
        
        if self.failure_count >= self.failure_threshold:
            self.state = "OPEN"

class ValidationError(Exception):
    """驗證錯誤"""
    pass

class ParsingError(Exception):
    """解析錯誤"""
    pass

class FileError(Exception):
    """檔案錯誤"""
    pass

class MemoryError(Exception):
    """記憶體錯誤"""
    pass

class ConfigurationError(Exception):
    """配置錯誤"""
    pass

def create_logger(name: str, log_file: Optional[str] = None, 
                 log_level: LogLevel = LogLevel.INFO) -> EnhancedLogger:
    """創建日誌記錄器"""
    return EnhancedLogger(name, log_file, log_level)

def test_error_handler():
    """測試錯誤處理系統"""
    print("🧪 錯誤處理系統測試")
    print("=" * 50)
    
    # 創建日誌記錄器
    logger = create_logger("test_logger", "test_output/error_test.log")
    
    # 測試基本日誌記錄
    logger.info("測試資訊日誌")
    logger.warning("測試警告日誌")
    logger.error("測試錯誤日誌")
    
    # 測試錯誤處理
    error_handler = ErrorHandler(logger)
    
    try:
        # 故意引發錯誤
        raise ValueError("測試錯誤")
    except Exception as e:
        error_context = error_handler.handle_error(e, ErrorType.VALIDATION_ERROR)
        print(f"📊 錯誤上下文: {error_context.error_type.value}")
    
    # 測試錯誤統計
    stats = error_handler.get_error_statistics()
    print(f"📈 錯誤統計: {stats}")
    
    # 測試重試處理器
    retry_handler = RetryHandler(max_retries=2, delay=0.1)
    
    def failing_function():
        raise Exception("重試測試錯誤")
    
    try:
        retry_handler.retry(failing_function)
    except Exception as e:
        print(f"🔄 重試測試完成: {e}")
    
    # 測試斷路器
    circuit_breaker = CircuitBreaker(failure_threshold=2, timeout=1.0)
    
    def circuit_function():
        raise Exception("斷路器測試錯誤")
    
    for i in range(5):
        try:
            circuit_breaker.call(circuit_function)
        except Exception as e:
            print(f"🔌 斷路器狀態: {circuit_breaker.state}, 錯誤: {e}")
    
    # 測試錯誤處理裝飾器
    @error_handler(ErrorType.PARSING_ERROR, default_return="預設值")
    def decorated_function():
        raise Exception("裝飾器測試錯誤")
    
    result = decorated_function()
    print(f"🎯 裝飾器測試結果: {result}")

if __name__ == "__main__":
    test_error_handler()