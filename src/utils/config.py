#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置管理系統
統一管理所有配置參數
支持 YAML 和 JSON 兩種格式（優先使用 YAML）
"""

import json
import os
import threading
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, Optional

from .logger import logger

try:
    import yaml

    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False
    logger.warning("PyYAML 未安裝，僅支持 JSON 格式配置")


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
                r"(\d+)\.\s*([ABCD])",  # 1. A
                r"(\d+)\s*([ABCD])",  # 1 A
                r"第(\d+)題\s*([ABCD])",  # 第1題 A
                r"(\d+)\s*：\s*([ABCD])",  # 1：A
            ]

        if self.corrected_answer_patterns is None:
            self.corrected_answer_patterns = [
                r"更正\s*(\d+)\.\s*([ABCD])",  # 更正 1. B
                r"更正答案\s*(\d+)\.\s*([ABCD])",  # 更正答案 1. B
                r"更正\s*第(\d+)題\s*([ABCD])",  # 更正 第1題 B
                r"更正\s*(\d+)\s*：\s*([ABCD])",  # 更正 1：B
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


@dataclass
class ConcurrentConfig:
    """並發處理配置"""

    max_workers: int = 4
    use_processes: bool = False
    batch_size: int = 50
    fail_fast: bool = False


@dataclass
class LoggingConfig:
    """日誌配置"""

    level: str = "INFO"
    file: str = "logs/app.log"
    max_size: int = 10485760  # 10MB
    backup_count: int = 5
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"


@dataclass
class ScanTrackingConfig:
    """題目掃描追蹤配置"""

    enabled: bool = True
    save_report: bool = True
    report_format: str = "json"


@dataclass
class PerformanceConfig:
    """性能監控配置"""

    enabled: bool = False
    metrics_interval: int = 60
    save_metrics: bool = False


@dataclass
class ErrorRecoveryConfig:
    """錯誤恢復配置"""

    max_retries: int = 3
    retry_delay: int = 2
    exponential_backoff: bool = True


@dataclass
class OutputConfig:
    """輸出配置"""

    default_dir: str = "output"
    create_subdirs: bool = True
    overwrite_existing: bool = False


@dataclass
class DownloaderConfig:
    """下載器配置"""

    # 並發下載設置
    concurrent_downloads: int = 5
    enable_concurrent: bool = True

    # 進度顯示設置
    show_progress_bar: bool = True
    progress_bar_style: str = "bar"
    show_download_speed: bool = True
    show_eta: bool = True

    # 斷點續傳設置
    enable_resume: bool = True
    resume_chunk_size: int = 8192
    resume_temp_suffix: str = ".part"
    verify_resume: bool = True

    # 連接設置
    connection_timeout: int = 10
    read_timeout: int = 120
    max_retries: int = 10
    retry_delay: float = 0.5

    # 速率限制
    rate_limit_enabled: bool = False
    max_speed_mbps: int = 10

    # 其他
    verify_ssl: bool = False
    user_agent: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"


class ConfigManager:
    """配置管理器（線程安全單例模式）"""

    _instance = None
    _lock = threading.Lock()
    _file_lock = threading.Lock()  # 文件I/O操作鎖

    def __init__(self, config_file: Optional[str] = None):
        """
        初始化配置管理器

        Args:
            config_file: 配置文件路徑（可選）
                        如果未指定，會自動尋找 config.yaml 或 config.json

        Attributes:
            config_file: 配置文件路徑
            processing_config: 處理配置實例（ProcessingConfig）
            google_form_config: Google表單配置實例（GoogleFormConfig）
            ocr_config: OCR配置實例（OCRConfig）
            concurrent_config: 並發處理配置實例（ConcurrentConfig）
            logging_config: 日誌配置實例（LoggingConfig）
            scan_tracking_config: 掃描追蹤配置實例（ScanTrackingConfig）
            performance_config: 性能監控配置實例（PerformanceConfig）
            error_recovery_config: 錯誤恢復配置實例（ErrorRecoveryConfig）
            output_config: 輸出配置實例（OutputConfig）
            downloader_config: 下載器配置實例（DownloaderConfig）

        Note:
            - 優先使用 YAML 格式 (config.yaml)，如果不存在則使用 JSON (config.json)
            - 如果配置文件存在，會自動載入配置
            - 如果配置文件不存在，會使用默認值並創建新配置文件
            - 此類使用單例模式，請通過 get_instance() 獲取實例
        """
        # 自動選擇配置文件
        if config_file is None:
            if os.path.exists("config.yaml") and YAML_AVAILABLE:
                config_file = "config.yaml"
            elif os.path.exists("config.json"):
                config_file = "config.json"
            else:
                # 默認使用 YAML（如果可用）
                config_file = "config.yaml" if YAML_AVAILABLE else "config.json"

        self.config_file = config_file
        self.processing_config = ProcessingConfig()
        self.google_form_config = GoogleFormConfig()
        self.ocr_config = OCRConfig()
        self.concurrent_config = ConcurrentConfig()
        self.logging_config = LoggingConfig()
        self.scan_tracking_config = ScanTrackingConfig()
        self.performance_config = PerformanceConfig()
        self.error_recovery_config = ErrorRecoveryConfig()
        self.output_config = OutputConfig()
        self.downloader_config = DownloaderConfig()
        self._load_config()

    @classmethod
    def get_instance(cls, config_file: Optional[str] = None) -> "ConfigManager":
        """
        獲取ConfigManager單例實例（線程安全）

        使用雙重檢查鎖定（Double-Checked Locking）模式

        Args:
            config_file: 配置文件路徑（可選）
                        如果未指定，會自動尋找 config.yaml 或 config.json

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
                    with open(self.config_file, "r", encoding="utf-8") as f:
                        # 根據文件擴展名選擇解析器
                        if self.config_file.endswith(".yaml") or self.config_file.endswith(".yml"):
                            if not YAML_AVAILABLE:
                                raise ImportError("PyYAML 未安裝，無法讀取 YAML 配置文件")
                            config_data = yaml.safe_load(f)
                        else:
                            config_data = json.load(f)

                    if config_data is None:
                        logger.warning(f"配置文件為空: {self.config_file}")
                        config_data = {}

                    # 更新各個配置
                    config_mapping = {
                        "processing": self.processing_config,
                        "google_form": self.google_form_config,
                        "ocr": self.ocr_config,
                        "concurrent": self.concurrent_config,
                        "logging": self.logging_config,
                        "scan_tracking": self.scan_tracking_config,
                        "performance": self.performance_config,
                        "error_recovery": self.error_recovery_config,
                        "output": self.output_config,
                        "downloader": self.downloader_config,
                    }

                    for section_name, config_obj in config_mapping.items():
                        if section_name in config_data:
                            section_data = config_data[section_name]
                            if isinstance(section_data, dict):
                                for key, value in section_data.items():
                                    if hasattr(config_obj, key):
                                        setattr(config_obj, key, value)
                                    else:
                                        logger.debug(f"未知配置項: {section_name}.{key}")

                    logger.info(f"配置已載入: {self.config_file}")
                except FileNotFoundError:
                    logger.warning(f"配置文件不存在: {self.config_file}")
                    self._save_config()
                except (json.JSONDecodeError, yaml.YAMLError) as e:
                    logger.error(f"配置文件格式錯誤: {e}")
                    raise
                except Exception as e:
                    logger.error(f"載入配置失敗: {e}")
                    raise
            else:
                logger.info(f"配置文件不存在，使用默認值並創建: {self.config_file}")
                self._save_config()

    def _save_config(self):
        """儲存配置檔案（線程安全）"""
        with self._file_lock:
            try:
                config_data = {
                    "processing": asdict(self.processing_config),
                    "google_form": asdict(self.google_form_config),
                    "ocr": asdict(self.ocr_config),
                    "concurrent": asdict(self.concurrent_config),
                    "logging": asdict(self.logging_config),
                    "scan_tracking": asdict(self.scan_tracking_config),
                    "performance": asdict(self.performance_config),
                    "error_recovery": asdict(self.error_recovery_config),
                    "output": asdict(self.output_config),
                    "downloader": asdict(self.downloader_config),
                }

                with open(self.config_file, "w", encoding="utf-8") as f:
                    # 根據文件擴展名選擇格式
                    if self.config_file.endswith(".yaml") or self.config_file.endswith(".yml"):
                        if not YAML_AVAILABLE:
                            raise ImportError("PyYAML 未安裝，無法保存 YAML 配置文件")
                        yaml.safe_dump(config_data, f, allow_unicode=True, default_flow_style=False, sort_keys=False)
                    else:
                        json.dump(config_data, f, ensure_ascii=False, indent=2)

                logger.info(f"配置已儲存: {self.config_file}")
            except Exception as e:
                logger.error(f"儲存配置失敗: {e}")
                raise

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

    # 新增配置的 getter 方法
    def get_concurrent_config(self) -> ConcurrentConfig:
        """取得並發處理配置"""
        return self.concurrent_config

    def get_logging_config(self) -> LoggingConfig:
        """取得日誌配置"""
        return self.logging_config

    def get_scan_tracking_config(self) -> ScanTrackingConfig:
        """取得掃描追蹤配置"""
        return self.scan_tracking_config

    def get_performance_config(self) -> PerformanceConfig:
        """取得性能監控配置"""
        return self.performance_config

    def get_error_recovery_config(self) -> ErrorRecoveryConfig:
        """取得錯誤恢復配置"""
        return self.error_recovery_config

    def get_output_config(self) -> OutputConfig:
        """取得輸出配置"""
        return self.output_config

    def get_downloader_config(self) -> DownloaderConfig:
        """取得下載器配置"""
        return self.downloader_config

    # 新增配置的 update 方法
    def update_concurrent_config(self, **kwargs) -> None:
        """更新並發處理配置"""
        for key, value in kwargs.items():
            if hasattr(self.concurrent_config, key):
                setattr(self.concurrent_config, key, value)
        self._save_config()

    def update_logging_config(self, **kwargs) -> None:
        """更新日誌配置"""
        for key, value in kwargs.items():
            if hasattr(self.logging_config, key):
                setattr(self.logging_config, key, value)
        self._save_config()

    def update_scan_tracking_config(self, **kwargs) -> None:
        """更新掃描追蹤配置"""
        for key, value in kwargs.items():
            if hasattr(self.scan_tracking_config, key):
                setattr(self.scan_tracking_config, key, value)
        self._save_config()

    def update_performance_config(self, **kwargs) -> None:
        """更新性能監控配置"""
        for key, value in kwargs.items():
            if hasattr(self.performance_config, key):
                setattr(self.performance_config, key, value)
        self._save_config()

    def update_error_recovery_config(self, **kwargs) -> None:
        """更新錯誤恢復配置"""
        for key, value in kwargs.items():
            if hasattr(self.error_recovery_config, key):
                setattr(self.error_recovery_config, key, value)
        self._save_config()

    def update_output_config(self, **kwargs) -> None:
        """更新輸出配置"""
        for key, value in kwargs.items():
            if hasattr(self.output_config, key):
                setattr(self.output_config, key, value)
        self._save_config()

    def update_downloader_config(self, **kwargs) -> None:
        """更新下載器配置"""
        for key, value in kwargs.items():
            if hasattr(self.downloader_config, key):
                setattr(self.downloader_config, key, value)
        self._save_config()

    def validate_config(self) -> bool:
        """
        驗證配置的完整性和有效性

        Returns:
            bool: 配置是否有效

        Raises:
            ValueError: 配置無效時拋出
        """
        # 驗證處理配置
        if self.processing_config.max_text_length <= 0:
            raise ValueError("max_text_length 必須大於 0")
        if self.processing_config.min_question_length <= 0:
            raise ValueError("min_question_length 必須大於 0")
        if self.processing_config.max_question_length <= self.processing_config.min_question_length:
            raise ValueError("max_question_length 必須大於 min_question_length")

        # 驗證 OCR 配置
        if not 0 <= self.ocr_config.confidence_threshold <= 1:
            raise ValueError("confidence_threshold 必須在 0 到 1 之間")
        if not 0 <= self.ocr_config.min_quality_score <= 1:
            raise ValueError("min_quality_score 必須在 0 到 1 之間")
        if self.ocr_config.pdf_to_image_dpi <= 0:
            raise ValueError("pdf_to_image_dpi 必須大於 0")

        # 驗證並發配置
        if self.concurrent_config.max_workers <= 0:
            raise ValueError("max_workers 必須大於 0")
        if self.concurrent_config.batch_size <= 0:
            raise ValueError("batch_size 必須大於 0")

        # 驗證日誌配置
        valid_log_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if self.logging_config.level not in valid_log_levels:
            raise ValueError(f"日誌級別必須是以下之一: {', '.join(valid_log_levels)}")

        # 驗證錯誤恢復配置
        if self.error_recovery_config.max_retries < 0:
            raise ValueError("max_retries 不能為負數")
        if self.error_recovery_config.retry_delay < 0:
            raise ValueError("retry_delay 不能為負數")

        logger.info("配置驗證通過")
        return True


# 全域配置實例（線程安全單例）
config_manager = ConfigManager.get_instance()
