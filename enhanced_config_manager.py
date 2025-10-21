#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
強化版配置管理系統 - 提供靈活的配置選項
"""

import os
import json
import yaml
from typing import Any, Dict, List, Optional, Union, Callable
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import logging

class ConfigFormat(Enum):
    """配置檔案格式枚舉"""
    JSON = "json"
    YAML = "yaml"
    ENV = "env"
    INI = "ini"

class LogLevel(Enum):
    """日誌等級枚舉"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

@dataclass
class ProcessingConfig:
    """處理配置"""
    max_text_length: int = 1000000
    min_question_length: int = 10
    max_question_length: int = 2000
    min_option_length: int = 2
    max_option_length: int = 500
    min_options_count: int = 2
    max_options_count: int = 6
    min_confidence_score: float = 0.3
    max_duplicate_content_ratio: float = 0.8
    enable_parallel_processing: bool = True
    max_workers: Optional[int] = None
    chunk_size: int = 10000
    enable_caching: bool = True
    cache_size: int = 128

@dataclass
class ValidationConfig:
    """驗證配置"""
    validation_level: str = "standard"  # basic, standard, strict
    enable_auto_correction: bool = False
    strict_mode: bool = False
    validate_question_format: bool = True
    validate_option_quality: bool = True
    validate_duplicates: bool = True
    min_validation_score: float = 0.5

@dataclass
class LoggingConfig:
    """日誌配置"""
    level: LogLevel = LogLevel.INFO
    enable_file_logging: bool = True
    log_file_path: str = "logs/application.log"
    max_log_file_size: int = 10 * 1024 * 1024  # 10MB
    backup_count: int = 5
    enable_console_logging: bool = True
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

@dataclass
class OutputConfig:
    """輸出配置"""
    output_encoding: str = "utf-8-sig"
    csv_delimiter: str = ","
    include_metadata: bool = True
    include_confidence_scores: bool = True
    include_validation_results: bool = True
    generate_summary_report: bool = True
    output_format: str = "csv"  # csv, json, xlsx

@dataclass
class QuestionGroupConfig:
    """題組配置"""
    enable_group_detection: bool = True
    group_patterns: List[str] = field(default_factory=lambda: [
        r'請依下文回答第(\d+)題至第(\d+)題[：:]?',
        r'請依上文回答第(\d+)題至第(\d+)題[：:]?',
        r'請根據下列文章回答第(\d+)題至第(\d+)題[：:]?',
        r'閱讀下文，回答第(\d+)題至第(\d+)題[：:]?',
    ])
    min_group_size: int = 2
    max_group_size: int = 10
    enable_group_validation: bool = True

@dataclass
class OptionExtractionConfig:
    """選項提取配置"""
    enable_multiple_formats: bool = True
    option_patterns: List[str] = field(default_factory=lambda: [
        r'[（(]?[ＡＢＣＤ][）)]?\s*([^ＡＢＣＤ\n]+?)(?=[（(]?[ＢＣＤＥ][）)]?|$)',
        r'[（(]?[ABCD][）)]?\s*([^ABCD\n]+?)(?=[（(]?[BCDE][）)]?|$)',
        r'[ＡＢＣＤ][：:]\s*([^ＡＢＣＤ\n]+?)(?=[ＡＢＣＤ][：:]|$)',
        r'[ABCD][：:]\s*([^ABCD\n]+?)(?=[ABCD][：:]|$)',
    ])
    enable_intelligent_splitting: bool = True
    min_option_confidence: float = 0.5
    enable_option_validation: bool = True

@dataclass
class PerformanceConfig:
    """效能配置"""
    enable_memory_optimization: bool = True
    enable_parallel_processing: bool = True
    max_memory_usage_mb: int = 1024
    enable_garbage_collection: bool = True
    gc_frequency: int = 100  # 每100次操作執行一次GC
    enable_profiling: bool = False
    profile_output_path: str = "profiles/"

@dataclass
class SystemConfig:
    """系統配置"""
    processing: ProcessingConfig = field(default_factory=ProcessingConfig)
    validation: ValidationConfig = field(default_factory=ValidationConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    output: OutputConfig = field(default_factory=OutputConfig)
    question_group: QuestionGroupConfig = field(default_factory=QuestionGroupConfig)
    option_extraction: OptionExtractionConfig = field(default_factory=OptionExtractionConfig)
    performance: PerformanceConfig = field(default_factory=PerformanceConfig)

class EnhancedConfigManager:
    """強化版配置管理器"""
    
    def __init__(self, config_file: Optional[str] = None):
        self.config_file = config_file
        self.config = SystemConfig()
        self.config_watchers: List[Callable] = []
        
        # 載入配置
        if config_file and os.path.exists(config_file):
            self.load_config(config_file)
        else:
            # 使用預設配置
            self._apply_environment_overrides()
    
    def load_config(self, config_file: str) -> bool:
        """載入配置檔案"""
        try:
            config_path = Path(config_file)
            
            if not config_path.exists():
                print(f"⚠️ 配置檔案不存在: {config_file}")
                return False
            
            with open(config_path, 'r', encoding='utf-8') as f:
                if config_path.suffix.lower() == '.json':
                    config_data = json.load(f)
                elif config_path.suffix.lower() in ['.yml', '.yaml']:
                    config_data = yaml.safe_load(f)
                else:
                    print(f"❌ 不支援的配置檔案格式: {config_path.suffix}")
                    return False
            
            # 更新配置
            self._update_config_from_dict(config_data)
            self._apply_environment_overrides()
            
            print(f"✅ 配置已載入: {config_file}")
            return True
            
        except Exception as e:
            print(f"❌ 載入配置失敗: {e}")
            return False
    
    def save_config(self, config_file: str, format: ConfigFormat = ConfigFormat.JSON) -> bool:
        """儲存配置檔案"""
        try:
            config_path = Path(config_file)
            config_path.parent.mkdir(parents=True, exist_ok=True)
            
            config_dict = self._config_to_dict()
            
            with open(config_path, 'w', encoding='utf-8') as f:
                if format == ConfigFormat.JSON:
                    json.dump(config_dict, f, indent=2, ensure_ascii=False)
                elif format == ConfigFormat.YAML:
                    yaml.dump(config_dict, f, default_flow_style=False, allow_unicode=True)
                else:
                    print(f"❌ 不支援的儲存格式: {format}")
                    return False
            
            print(f"✅ 配置已儲存: {config_file}")
            return True
            
        except Exception as e:
            print(f"❌ 儲存配置失敗: {e}")
            return False
    
    def _update_config_from_dict(self, config_data: Dict[str, Any]):
        """從字典更新配置"""
        if 'processing' in config_data:
            self._update_dataclass(self.config.processing, config_data['processing'])
        
        if 'validation' in config_data:
            self._update_dataclass(self.config.validation, config_data['validation'])
        
        if 'logging' in config_data:
            self._update_dataclass(self.config.logging, config_data['logging'])
        
        if 'output' in config_data:
            self._update_dataclass(self.config.output, config_data['output'])
        
        if 'question_group' in config_data:
            self._update_dataclass(self.config.question_group, config_data['question_group'])
        
        if 'option_extraction' in config_data:
            self._update_dataclass(self.config.option_extraction, config_data['option_extraction'])
        
        if 'performance' in config_data:
            self._update_dataclass(self.config.performance, config_data['performance'])
    
    def _update_dataclass(self, dataclass_instance, data: Dict[str, Any]):
        """更新資料類別實例"""
        for key, value in data.items():
            if hasattr(dataclass_instance, key):
                setattr(dataclass_instance, key, value)
    
    def _config_to_dict(self) -> Dict[str, Any]:
        """將配置轉換為字典"""
        return {
            'processing': asdict(self.config.processing),
            'validation': asdict(self.config.validation),
            'logging': asdict(self.config.logging),
            'output': asdict(self.config.output),
            'question_group': asdict(self.config.question_group),
            'option_extraction': asdict(self.config.option_extraction),
            'performance': asdict(self.config.performance),
        }
    
    def _apply_environment_overrides(self):
        """應用環境變數覆蓋"""
        env_mappings = {
            'ARCHAEOLOGY_LOG_LEVEL': ('logging', 'level'),
            'ARCHAEOLOGY_MAX_TEXT_LENGTH': ('processing', 'max_text_length'),
            'ARCHAEOLOGY_MIN_QUESTION_LENGTH': ('processing', 'min_question_length'),
            'ARCHAEOLOGY_MAX_QUESTION_LENGTH': ('processing', 'max_question_length'),
            'ARCHAEOLOGY_ENABLE_PARALLEL': ('processing', 'enable_parallel_processing'),
            'ARCHAEOLOGY_MAX_WORKERS': ('processing', 'max_workers'),
            'ARCHAEOLOGY_VALIDATION_LEVEL': ('validation', 'validation_level'),
            'ARCHAEOLOGY_OUTPUT_ENCODING': ('output', 'output_encoding'),
            'ARCHAEOLOGY_ENABLE_GROUP_DETECTION': ('question_group', 'enable_group_detection'),
        }
        
        for env_var, (section, key) in env_mappings.items():
            value = os.getenv(env_var)
            if value is not None:
                # 取得對應的配置物件
                config_obj = getattr(self.config, section)
                
                # 轉換值類型
                current_value = getattr(config_obj, key)
                if isinstance(current_value, bool):
                    converted_value = value.lower() in ('true', '1', 'yes', 'on')
                elif isinstance(current_value, int):
                    converted_value = int(value)
                elif isinstance(current_value, float):
                    converted_value = float(value)
                else:
                    converted_value = value
                
                setattr(config_obj, key, converted_value)
    
    def get(self, key_path: str, default: Any = None) -> Any:
        """取得配置值"""
        keys = key_path.split('.')
        value = self.config
        
        try:
            for key in keys:
                value = getattr(value, key)
            return value
        except AttributeError:
            return default
    
    def set(self, key_path: str, value: Any) -> bool:
        """設定配置值"""
        keys = key_path.split('.')
        config_obj = self.config
        
        try:
            # 導航到最後一個物件
            for key in keys[:-1]:
                config_obj = getattr(config_obj, key)
            
            # 設定值
            setattr(config_obj, keys[-1], value)
            
            # 通知監聽器
            self._notify_watchers(key_path, value)
            
            return True
        except AttributeError:
            return False
    
    def add_config_watcher(self, callback: Callable[[str, Any], None]):
        """添加配置監聽器"""
        self.config_watchers.append(callback)
    
    def _notify_watchers(self, key_path: str, value: Any):
        """通知配置監聽器"""
        for callback in self.config_watchers:
            try:
                callback(key_path, value)
            except Exception as e:
                print(f"⚠️ 配置監聽器錯誤: {e}")
    
    def validate_config(self) -> List[str]:
        """驗證配置"""
        issues = []
        
        # 驗證處理配置
        if self.config.processing.max_text_length <= 0:
            issues.append("max_text_length 必須大於 0")
        
        if self.config.processing.min_question_length <= 0:
            issues.append("min_question_length 必須大於 0")
        
        if self.config.processing.max_question_length <= self.config.processing.min_question_length:
            issues.append("max_question_length 必須大於 min_question_length")
        
        # 驗證驗證配置
        if self.config.validation.validation_level not in ['basic', 'standard', 'strict']:
            issues.append("validation_level 必須是 basic, standard 或 strict")
        
        # 驗證日誌配置
        if self.config.logging.max_log_file_size <= 0:
            issues.append("max_log_file_size 必須大於 0")
        
        return issues
    
    def create_default_config_file(self, config_file: str, format: ConfigFormat = ConfigFormat.JSON) -> bool:
        """創建預設配置檔案"""
        return self.save_config(config_file, format)
    
    def reset_to_defaults(self):
        """重置為預設配置"""
        self.config = SystemConfig()
        self._apply_environment_overrides()

def create_config_manager(config_file: Optional[str] = None) -> EnhancedConfigManager:
    """創建配置管理器"""
    return EnhancedConfigManager(config_file)

def test_config_manager():
    """測試配置管理器"""
    print("🧪 配置管理器測試")
    print("=" * 50)
    
    # 創建配置管理器
    config_manager = create_config_manager()
    
    # 測試基本操作
    print(f"📊 最大文字長度: {config_manager.get('processing.max_text_length')}")
    print(f"📊 日誌等級: {config_manager.get('logging.level')}")
    
    # 測試設定值
    config_manager.set('processing.max_text_length', 2000000)
    print(f"📊 更新後的最大文字長度: {config_manager.get('processing.max_text_length')}")
    
    # 測試配置監聽器
    def config_watcher(key_path: str, value: Any):
        print(f"🔔 配置變更: {key_path} = {value}")
    
    config_manager.add_config_watcher(config_watcher)
    config_manager.set('processing.min_question_length', 15)
    
    # 測試配置驗證
    issues = config_manager.validate_config()
    if issues:
        print(f"⚠️ 配置問題: {issues}")
    else:
        print("✅ 配置驗證通過")
    
    # 測試儲存和載入
    test_config_file = "test_output/test_config.json"
    if config_manager.save_config(test_config_file):
        print(f"✅ 配置已儲存到: {test_config_file}")
        
        # 創建新的配置管理器並載入
        new_config_manager = create_config_manager(test_config_file)
        print(f"📊 載入的配置: {new_config_manager.get('processing.max_text_length')}")
    
    # 測試環境變數覆蓋
    os.environ['ARCHAEOLOGY_LOG_LEVEL'] = 'DEBUG'
    config_manager._apply_environment_overrides()
    print(f"📊 環境變數覆蓋後的日誌等級: {config_manager.get('logging.level')}")

if __name__ == "__main__":
    test_config_manager()