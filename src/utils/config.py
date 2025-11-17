#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置管理系統
統一管理所有配置參數
"""

import os
import json
import threading
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
class OCRConfig:
    """OCR配置"""
    # OCR啟用設定
    enable_ocr: bool = False  # 是否啟用 OCR
    ocr_fallback: bool = True  # OCR 失敗時是否降級到傳統方法

    # OCR引擎設定
    use_gpu: bool = False  # 是否使用 GPU 加速
    lang: str = "ch"  # 語言設定 ('ch'=中英文, 'chinese_cht'=繁體中文, 'en'=英文)

    # OCR處理設定
    use_structure: bool = False  # 是否使用結構化分析（PP-Structure）
    confidence_threshold: float = 0.5  # 信心度閾值（0-1）
    min_quality_score: float = 0.6  # 最低品質分數（0-1）

    # 圖片轉換設定
    pdf_to_image_dpi: int = 300  # PDF 轉圖片的 DPI
    pdf_to_image_zoom: float = 2.0  # PDF 轉圖片的放大倍數


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
    """配置管理器（線程安全單例模式）"""

    _instance = None
    _lock = threading.Lock()
    _file_lock = threading.Lock()  # 文件I/O操作鎖

    def __init__(self, config_file: str = "config.json"):
        """
        初始化配置管理器

        Args:
            config_file: 配置文件路徑（默認: "config.json"）

        Attributes:
            config_file: 配置文件路徑
            processing_config: 處理配置實例（ProcessingConfig）
            google_form_config: Google表單配置實例（GoogleFormConfig）
            ocr_config: OCR配置實例（OCRConfig）

        Note:
            - 如果配置文件存在，會自動載入配置
            - 如果配置文件不存在，會使用默認值並創建新配置文件
            - 此類使用單例模式，請通過 get_instance() 獲取實例
        """
        self.config_file = config_file
        self.processing_config = ProcessingConfig()
        self.google_form_config = GoogleFormConfig()
        self.ocr_config = OCRConfig()
        self._load_config()

    @classmethod
    def get_instance(cls, config_file: str = "config.json") -> 'ConfigManager':
        """
        獲取ConfigManager單例實例（線程安全）

        使用雙重檢查鎖定（Double-Checked Locking）模式

        Args:
            config_file: 配置文件路徑

        Returns:
            ConfigManager實例
        """
        # 第一次檢查（不加鎖，性能優化）
        if cls._instance is None:
            # 加鎖
            with cls._lock:
                # 第二次檢查（加鎖後再確認，避免多次創建）
                if cls._instance is None:
                    cls._instance = cls(config_file)
        return cls._instance
    
    def _load_config(self):
        """載入配置檔案（線程安全）"""
        with self._file_lock:
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

                    # 更新OCR配置
                    if 'ocr' in config_data:
                        ocr_data = config_data['ocr']
                        for key, value in ocr_data.items():
                            if hasattr(self.ocr_config, key):
                                setattr(self.ocr_config, key, value)

                    logger.info(f"配置已載入: {self.config_file}")
                except Exception as e:
                    logger.warning(f"載入配置失敗: {e}")
            else:
                self._save_config()
    
    def _save_config(self):
        """儲存配置檔案（線程安全）"""
        with self._file_lock:
            try:
                config_data = {
                    'processing': asdict(self.processing_config),
                    'google_form': asdict(self.google_form_config),
                    'ocr': asdict(self.ocr_config)
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

    def get_ocr_config(self) -> OCRConfig:
        """取得OCR配置"""
        return self.ocr_config

    def update_processing_config(self, **kwargs) -> None:
        """更新處理配置"""
        for key, value in kwargs.items():
            if hasattr(self.processing_config, key):
                setattr(self.processing_config, key, value)
        self._save_config()

    def update_google_form_config(self, **kwargs) -> None:
        """更新Google表單配置"""
        for key, value in kwargs.items():
            if hasattr(self.google_form_config, key):
                setattr(self.google_form_config, key, value)
        self._save_config()

    def update_ocr_config(self, **kwargs) -> None:
        """更新OCR配置"""
        for key, value in kwargs.items():
            if hasattr(self.ocr_config, key):
                setattr(self.ocr_config, key, value)
        self._save_config()


# 全域配置實例（線程安全單例）
config_manager = ConfigManager.get_instance()