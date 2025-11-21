#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
YAML 配置管理器
支持 YAML/JSON 雙格式，環境變量覆蓋，配置驗證
"""

import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Optional

import yaml

from .logger import logger


@dataclass
class ProcessingConfig:
    """處理配置"""

    max_pages: int = 200
    memory_cleanup_interval: int = 50
    output_encoding: str = "utf-8-sig"
    csv_delimiter: str = ","


@dataclass
class GoogleFormConfig:
    """Google 表單配置"""

    enable_auto_score: bool = True
    shuffle_options: bool = False
    required: bool = True
    form_title: str = "考古題測驗"


@dataclass
class OCRConfig:
    """OCR 配置"""

    pdf_to_image_dpi: int = 300
    pdf_to_image_zoom: float = 2.0
    confidence_threshold: float = 0.5
    use_gpu: bool = False
    lang: str = "ch"


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
    """掃描追蹤配置"""

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
class AppConfig:
    """應用程式配置（頂層）"""

    processing: ProcessingConfig = field(default_factory=ProcessingConfig)
    google_form: GoogleFormConfig = field(default_factory=GoogleFormConfig)
    ocr: OCRConfig = field(default_factory=OCRConfig)
    concurrent: ConcurrentConfig = field(default_factory=ConcurrentConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    scan_tracking: ScanTrackingConfig = field(default_factory=ScanTrackingConfig)
    performance: PerformanceConfig = field(default_factory=PerformanceConfig)
    error_recovery: ErrorRecoveryConfig = field(default_factory=ErrorRecoveryConfig)
    output: OutputConfig = field(default_factory=OutputConfig)


class YAMLConfigManager:
    """YAML 配置管理器 - 支持 YAML/JSON 雙格式"""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, "_initialized"):
            self.logger = logger
            self.config: Optional[AppConfig] = None
            self.config_file: Optional[str] = None
            self._initialized = True

    def load_config(self, config_file: str = "config.yaml") -> AppConfig:
        """
        載入配置文件

        Args:
            config_file: 配置文件路徑（支持 .yaml, .yml, .json）

        Returns:
            AppConfig: 配置對象

        Raises:
            FileNotFoundError: 配置文件不存在
            ValueError: 配置文件格式錯誤
        """
        self.config_file = config_file

        # 檢查文件是否存在
        if not os.path.exists(config_file):
            self.logger.warning(f"配置文件不存在: {config_file}，使用默認配置")
            self.config = AppConfig()
            return self.config

        # 根據文件擴展名選擇解析方式
        file_ext = Path(config_file).suffix.lower()

        try:
            with open(config_file, "r", encoding="utf-8") as f:
                if file_ext in [".yaml", ".yml"]:
                    config_data = yaml.safe_load(f) or {}
                elif file_ext == ".json":
                    config_data = json.load(f)
                else:
                    raise ValueError(f"不支持的配置文件格式: {file_ext}")

            # 解析配置
            self.config = self._parse_config(config_data)

            # 環境變量覆蓋
            self._apply_env_overrides()

            self.logger.info(f"✅ 配置已載入: {config_file}")
            return self.config

        except yaml.YAMLError as e:
            raise ValueError(f"YAML 解析錯誤: {e}")
        except json.JSONDecodeError as e:
            raise ValueError(f"JSON 解析錯誤: {e}")
        except Exception as e:
            raise ValueError(f"配置載入失敗: {e}")

    def _parse_config(self, data: Dict[str, Any]) -> AppConfig:
        """解析配置數據為 AppConfig 對象"""
        return AppConfig(
            processing=self._parse_section(data.get("processing", {}), ProcessingConfig),
            google_form=self._parse_section(data.get("google_form", {}), GoogleFormConfig),
            ocr=self._parse_section(data.get("ocr", {}), OCRConfig),
            concurrent=self._parse_section(data.get("concurrent", {}), ConcurrentConfig),
            logging=self._parse_section(data.get("logging", {}), LoggingConfig),
            scan_tracking=self._parse_section(data.get("scan_tracking", {}), ScanTrackingConfig),
            performance=self._parse_section(data.get("performance", {}), PerformanceConfig),
            error_recovery=self._parse_section(data.get("error_recovery", {}), ErrorRecoveryConfig),
            output=self._parse_section(data.get("output", {}), OutputConfig),
        )

    def _parse_section(self, data: Dict[str, Any], config_class):
        """解析配置段落"""
        if not data:
            return config_class()

        # 過濾出有效的字段
        valid_fields = {k: v for k, v in data.items() if hasattr(config_class, k)}
        return config_class(**valid_fields)

    def _apply_env_overrides(self):
        """應用環境變量覆蓋"""
        # 支持環境變量覆蓋，格式: APP_SECTION_KEY
        # 例如: APP_OCR_USE_GPU=true

        env_prefix = "APP_"

        for env_key, env_value in os.environ.items():
            if not env_key.startswith(env_prefix):
                continue

            # 解析環境變量名稱
            parts = env_key[len(env_prefix) :].lower().split("_")

            if len(parts) < 2:
                continue

            section_name = parts[0]
            field_name = "_".join(parts[1:])

            # 獲取對應的配置section
            if not hasattr(self.config, section_name):
                continue

            section = getattr(self.config, section_name)

            if not hasattr(section, field_name):
                continue

            # 類型轉換
            field_type = type(getattr(section, field_name))
            try:
                if field_type == bool:
                    value = env_value.lower() in ("true", "1", "yes")
                elif field_type == int:
                    value = int(env_value)
                elif field_type == float:
                    value = float(env_value)
                else:
                    value = env_value

                setattr(section, field_name, value)
                self.logger.debug(f"環境變量覆蓋: {section_name}.{field_name} = {value}")

            except (ValueError, TypeError) as e:
                self.logger.warning(f"環境變量類型轉換失敗: {env_key} = {env_value}, {e}")

    def save_config(self, output_file: str = None):
        """
        保存配置到文件

        Args:
            output_file: 輸出文件路徑（默認覆蓋原文件）
        """
        if not self.config:
            self.logger.warning("無配置可保存")
            return

        output_file = output_file or self.config_file or "config.yaml"
        file_ext = Path(output_file).suffix.lower()

        # 轉換為字典
        config_dict = self._config_to_dict()

        try:
            with open(output_file, "w", encoding="utf-8") as f:
                if file_ext in [".yaml", ".yml"]:
                    yaml.dump(config_dict, f, allow_unicode=True, default_flow_style=False)
                elif file_ext == ".json":
                    json.dump(config_dict, f, ensure_ascii=False, indent=2)
                else:
                    raise ValueError(f"不支持的輸出格式: {file_ext}")

            self.logger.info(f"✅ 配置已保存: {output_file}")

        except Exception as e:
            self.logger.error(f"配置保存失敗: {e}")
            raise

    def _config_to_dict(self) -> Dict[str, Any]:
        """將配置對象轉換為字典"""
        from dataclasses import asdict

        return asdict(self.config)

    def get_config(self) -> AppConfig:
        """獲取配置對象"""
        if not self.config:
            self.load_config()
        return self.config

    def reload_config(self):
        """重新載入配置"""
        if self.config_file:
            self.load_config(self.config_file)
        else:
            self.load_config()

    def validate_config(self) -> bool:
        """驗證配置有效性"""
        if not self.config:
            return False

        try:
            # 驗證處理配置
            assert self.config.processing.max_pages > 0, "max_pages 必須大於 0"
            assert self.config.processing.memory_cleanup_interval > 0, "memory_cleanup_interval 必須大於 0"

            # 驗證 OCR 配置
            assert self.config.ocr.pdf_to_image_dpi > 0, "pdf_to_image_dpi 必須大於 0"
            assert 0 < self.config.ocr.confidence_threshold <= 1, "confidence_threshold 必須在 0-1 之間"

            # 驗證並發配置
            assert self.config.concurrent.max_workers > 0, "max_workers 必須大於 0"
            assert self.config.concurrent.batch_size > 0, "batch_size 必須大於 0"

            # 驗證錯誤恢復配置
            assert self.config.error_recovery.max_retries >= 0, "max_retries 必須 >= 0"
            assert self.config.error_recovery.retry_delay >= 0, "retry_delay 必須 >= 0"

            self.logger.info("✅ 配置驗證通過")
            return True

        except AssertionError as e:
            self.logger.error(f"❌ 配置驗證失敗: {e}")
            return False


# 全局配置管理器實例
yaml_config_manager = YAMLConfigManager()


def load_config(config_file: str = "config.yaml") -> AppConfig:
    """
    載入配置的便捷函數

    Args:
        config_file: 配置文件路徑

    Returns:
        AppConfig: 配置對象
    """
    return yaml_config_manager.load_config(config_file)


def get_config() -> AppConfig:
    """
    獲取配置的便捷函數

    Returns:
        AppConfig: 配置對象
    """
    return yaml_config_manager.get_config()
