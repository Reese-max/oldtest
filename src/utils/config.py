#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置管理系統
統一管理所有配置參數
"""

import os
import json
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict
from .logger import logger


@dataclass
class ProcessingConfig:
    """處理配置"""
    # PDF處理設定
    max_text_length: int = 1000000
    min_question_length: int = 10
    max_question_length: int = 1000
    
    # AI處理設定
    ai_model: str = "gemini-1.5-flash"
    ai_temperature: float = 0.1
    ai_max_tokens: int = 4000
    
    # 答案處理設定
    answer_patterns: list = None
    corrected_answer_patterns: list = None
    
    # 輸出設定
    output_encoding: str = "utf-8-sig"
    csv_delimiter: str = ","
    
    def __post_init__(self):
        if self.answer_patterns is None:
            self.answer_patterns = [
                r'(\d+)\.\s*([ABCD])',  # 1. A
                r'(\d+)\s*([ABCD])',    # 1 A
                r'第(\d+)題\s*([ABCD])', # 第1題 A
                r'(\d+)\s*：\s*([ABCD])', # 1：A
            ]
        
        if self.corrected_answer_patterns is None:
            self.corrected_answer_patterns = [
                r'更正\s*(\d+)\.\s*([ABCD])',  # 更正 1. B
                r'更正答案\s*(\d+)\.\s*([ABCD])', # 更正答案 1. B
                r'更正\s*第(\d+)題\s*([ABCD])', # 更正 第1題 B
                r'更正\s*(\d+)\s*：\s*([ABCD])', # 更正 1：B
            ]


@dataclass
class GoogleFormConfig:
    """Google表單配置"""
    # 表單設定
    form_title: str = "考古題練習表單"
    form_description: str = "此表單包含考古題，用於練習和自測"
    collect_email: bool = True
    require_login: bool = False
    
    # 評分設定
    enable_auto_scoring: bool = True
    show_answers_after_submit: bool = True
    
    # 題目設定
    default_question_type: str = "選擇題"
    enable_question_groups: bool = True


class ConfigManager:
    """配置管理器"""
    
    def __init__(self, config_file: str = "config.json"):
        self.config_file = config_file
        self.processing_config = ProcessingConfig()
        self.google_form_config = GoogleFormConfig()
        self._load_config()
    
    def _load_config(self):
        """載入配置檔案"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
                
                # 更新處理配置
                if 'processing' in config_data:
                    processing_data = config_data['processing']
                    for key, value in processing_data.items():
                        if hasattr(self.processing_config, key):
                            setattr(self.processing_config, key, value)
                
                # 更新Google表單配置
                if 'google_form' in config_data:
                    google_form_data = config_data['google_form']
                    for key, value in google_form_data.items():
                        if hasattr(self.google_form_config, key):
                            setattr(self.google_form_config, key, value)
                
                logger.info(f"配置已載入: {self.config_file}")
            except Exception as e:
                logger.warning(f"載入配置失敗: {e}")
        else:
            self._save_config()
    
    def _save_config(self):
        """儲存配置檔案"""
        try:
            config_data = {
                'processing': asdict(self.processing_config),
                'google_form': asdict(self.google_form_config)
            }
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"配置已儲存: {self.config_file}")
        except Exception as e:
            logger.error(f"儲存配置失敗: {e}")
    
    def get_processing_config(self) -> ProcessingConfig:
        """取得處理配置"""
        return self.processing_config
    
    def get_google_form_config(self) -> GoogleFormConfig:
        """取得Google表單配置"""
        return self.google_form_config
    
    def update_processing_config(self, **kwargs):
        """更新處理配置"""
        for key, value in kwargs.items():
            if hasattr(self.processing_config, key):
                setattr(self.processing_config, key, value)
        self._save_config()
    
    def update_google_form_config(self, **kwargs):
        """更新Google表單配置"""
        for key, value in kwargs.items():
            if hasattr(self.google_form_config, key):
                setattr(self.google_form_config, key, value)
        self._save_config()


# 全域配置實例
config_manager = ConfigManager()