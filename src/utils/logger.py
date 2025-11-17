#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
統一日誌系統
提供結構化的日誌記錄功能
"""

import logging
import sys
from typing import Optional
from datetime import datetime
import os


class Logger:
    """統一日誌管理器"""
    
    _instance: Optional['Logger'] = None
    _logger: Optional[logging.Logger] = None
    
    def __new__(cls) -> 'Logger':
        """
        實現單例模式的 __new__ 方法

        確保整個應用程式只有一個 Logger 實例，避免重複初始化和日誌混亂

        Returns:
            Logger: 單例 Logger 實例
        """
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """
        初始化 Logger 實例

        只在第一次創建實例時設置日誌器，後續調用不會重新初始化
        設置控制台和文件兩個日誌處理器，分別輸出到 stdout 和日誌文件
        """
        if self._logger is None:
            self._setup_logger()
    
    def _setup_logger(self):
        """設置日誌器"""
        self._logger = logging.getLogger('archaeology_questions')
        self._logger.setLevel(logging.INFO)
        
        # 清除現有的處理器
        self._logger.handlers.clear()
        
        # 創建控制台處理器
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        
        # 創建文件處理器
        os.makedirs('logs', exist_ok=True)
        file_handler = logging.FileHandler(
            f'logs/archaeology_questions_{datetime.now().strftime("%Y%m%d")}.log',
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        
        # 設置格式
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(formatter)
        file_handler.setFormatter(formatter)
        
        # 添加處理器
        self._logger.addHandler(console_handler)
        self._logger.addHandler(file_handler)
    
    def info(self, message: str, **kwargs) -> None:
        """記錄信息日誌"""
        self._logger.info(message, **kwargs)

    def debug(self, message: str, **kwargs) -> None:
        """記錄調試日誌"""
        self._logger.debug(message, **kwargs)

    def warning(self, message: str, **kwargs) -> None:
        """記錄警告日誌"""
        self._logger.warning(message, **kwargs)

    def error(self, message: str, **kwargs) -> None:
        """記錄錯誤日誌"""
        self._logger.error(message, **kwargs)

    def success(self, message: str, **kwargs) -> None:
        """記錄成功日誌（自定義級別）"""
        self._logger.info(f"✅ {message}", **kwargs)

    def failure(self, message: str, **kwargs) -> None:
        """記錄失敗日誌（自定義級別）"""
        self._logger.error(f"❌ {message}", **kwargs)


# 全域日誌實例
logger = Logger()