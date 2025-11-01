#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置管理系統
統一管理所有配置參數
"""

import os
import json
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict, field
from .logger import logger
from .exceptions import ConfigurationError


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
    answer_patterns: List[str] = field(default_factory=list)
    corrected_answer_patterns: List[str] = field(default_factory=list)
    
    # 輸出設定
    output_encoding: str = "utf-8-sig"
    csv_delimiter: str = ","
    
    def __post_init__(self):
        if not self.answer_patterns:
            self.answer_patterns = [
                r'(\d+)\.\s*([ABCD])',  # 1. A
                r'(\d+)\s*([ABCD])',    # 1 A
                r'第(\d+)題\s*([ABCD])', # 第1題 A
                r'(\d+)\s*：\s*([ABCD])', # 1：A
            ]
        
        if not self.corrected_answer_patterns:
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
                    self._validate_and_update_processing_config(processing_data)
                
                # 更新Google表單配置
                if 'google_form' in config_data:
                    google_form_data = config_data['google_form']
                    self._validate_and_update_google_form_config(google_form_data)
                
                # 驗證配置完整性
                self._validate_config()
                
                logger.info(f"配置已載入: {self.config_file}")
            except json.JSONDecodeError as e:
                error_msg = f"配置檔案JSON格式錯誤: {e}"
                logger.error(error_msg)
                raise ConfigurationError(error_msg) from e
            except Exception as e:
                error_msg = f"載入配置失敗: {e}"
                logger.error(error_msg)
                raise ConfigurationError(error_msg) from e
        else:
            self._save_config()
            logger.info(f"配置檔案不存在，已建立預設配置: {self.config_file}")
    
    def _validate_and_update_processing_config(self, processing_data: Dict[str, Any]) -> None:
        """驗證並更新處理配置"""
        # 定義驗證規則
        validation_rules = {
            'max_text_length': (int, lambda x: x > 0, "必須為正整數"),
            'min_question_length': (int, lambda x: x > 0, "必須為正整數"),
            'max_question_length': (int, lambda x: x > 0, "必須為正整數"),
            'ai_temperature': (float, lambda x: 0 <= x <= 2, "必須在0-2之間"),
            'ai_max_tokens': (int, lambda x: x > 0, "必須為正整數"),
            'output_encoding': (str, lambda x: x in ['utf-8', 'utf-8-sig', 'big5'], "必須為有效的編碼格式"),
            'csv_delimiter': (str, lambda x: len(x) == 1, "必須為單一字元"),
        }
        
        for key, value in processing_data.items():
            if hasattr(self.processing_config, key):
                # 類型驗證
                if key in validation_rules:
                    expected_type, validator, error_msg = validation_rules[key]
                    if not isinstance(value, expected_type):
                        raise ConfigurationError(
                            f"配置項 '{key}' 類型錯誤: 期望 {expected_type.__name__}, 實際 {type(value).__name__}"
                        )
                    if not validator(value):
                        raise ConfigurationError(f"配置項 '{key}' 驗證失敗: {error_msg}")
                
                setattr(self.processing_config, key, value)
            else:
                logger.warning(f"未知的處理配置項: {key}")
    
    def _validate_and_update_google_form_config(self, google_form_data: Dict[str, Any]) -> None:
        """驗證並更新Google表單配置"""
        validation_rules = {
            'form_title': (str, lambda x: len(x) > 0, "不能為空"),
            'form_description': (str, lambda x: True, ""),  # 允許空字串
            'collect_email': (bool, lambda x: True, ""),
            'require_login': (bool, lambda x: True, ""),
            'enable_auto_scoring': (bool, lambda x: True, ""),
            'show_answers_after_submit': (bool, lambda x: True, ""),
            'default_question_type': (str, lambda x: x in ['選擇題', '問答題'], "必須為 '選擇題' 或 '問答題'"),
            'enable_question_groups': (bool, lambda x: True, ""),
        }
        
        for key, value in google_form_data.items():
            if hasattr(self.google_form_config, key):
                # 類型驗證
                if key in validation_rules:
                    expected_type, validator, error_msg = validation_rules[key]
                    if not isinstance(value, expected_type):
                        raise ConfigurationError(
                            f"配置項 '{key}' 類型錯誤: 期望 {expected_type.__name__}, 實際 {type(value).__name__}"
                        )
                    if not validator(value):
                        raise ConfigurationError(f"配置項 '{key}' 驗證失敗: {error_msg}")
                
                setattr(self.google_form_config, key, value)
            else:
                logger.warning(f"未知的Google表單配置項: {key}")
    
    def _validate_config(self) -> None:
        """驗證配置完整性"""
        # 檢查範圍合理性
        if self.processing_config.min_question_length >= self.processing_config.max_question_length:
            raise ConfigurationError(
                "min_question_length 必須小於 max_question_length"
            )
        
        if self.processing_config.max_text_length < self.processing_config.max_question_length:
            logger.warning("max_text_length 小於 max_question_length，可能導致問題")
    
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
    
    def update_processing_config(self, **kwargs: Any) -> None:
        """更新處理配置"""
        if not kwargs:
            return
        
        # 驗證並更新配置
        self._validate_and_update_processing_config(kwargs)
        self._validate_config()
        self._save_config()
        logger.info(f"處理配置已更新: {list(kwargs.keys())}")
    
    def update_google_form_config(self, **kwargs: Any) -> None:
        """更新Google表單配置"""
        if not kwargs:
            return
        
        # 驗證並更新配置
        self._validate_and_update_google_form_config(kwargs)
        self._save_config()
        logger.info(f"Google表單配置已更新: {list(kwargs.keys())}")


# 全域配置實例
config_manager = ConfigManager()