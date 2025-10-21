#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
增強版配置系統 - 提高系統靈活性
提供豐富的配置選項和動態配置管理
"""

import os
import json
import yaml
import logging
from typing import Dict, Any, Optional, List, Union
from datetime import datetime
import threading

class EnhancedConfigSystem:
    """增強版配置系統"""
    
    def __init__(self, config_file: Optional[str] = None):
        self.logger = logging.getLogger('EnhancedConfigSystem')
        self.config_file = config_file or 'enhanced_config.json'
        self.config = self._load_default_config()
        self.lock = threading.Lock()
        
        if os.path.exists(self.config_file):
            self.load_config(self.config_file)
    
    def _load_default_config(self) -> Dict[str, Any]:
        """載入預設配置"""
        return {
            'system': {
                'name': 'Enhanced Question Processing System',
                'version': '2.0.0',
                'debug': False,
                'log_level': 'INFO',
                'max_workers': None,  # 自動檢測
                'memory_threshold': 0.8,
                'temp_dir': 'temp'
            },
            'processing': {
                'max_text_length': 1000000,
                'min_question_length': 10,
                'max_question_length': 1000,
                'min_option_length': 2,
                'max_option_length': 200,
                'enable_parallel_processing': True,
                'batch_size': 100,
                'enable_memory_optimization': True,
                'enable_performance_monitoring': True
            },
            'question_group': {
                'enable_detection': True,
                'max_questions_per_group': 20,
                'min_group_content_length': 50,
                'detection_confidence_threshold': 0.5,
                'merge_overlapping_groups': True,
                'patterns': [
                    '請依下文回答第(\\d+)題至第(\\d+)題',
                    '請根據下列文章回答第(\\d+)題至第(\\d+)題',
                    '閱讀下文，回答第(\\d+)題至第(\\d+)題',
                    '根據下列文章，回答第(\\d+)題至第(\\d+)題',
                    '請根據下文回答第(\\d+)題至第(\\d+)題'
                ]
            },
            'option_extraction': {
                'enable_enhanced_extraction': True,
                'min_options_count': 2,
                'max_options_count': 4,
                'enable_semantic_analysis': True,
                'enable_fuzzy_matching': True,
                'confidence_threshold': 0.6,
                'patterns': [
                    'parentheses_standard',
                    'full_width',
                    'half_width',
                    'numbered',
                    'dot_numbered',
                    'dash',
                    'space_separated'
                ]
            },
            'question_parsing': {
                'enable_enhanced_parsing': True,
                'enable_question_indicators': True,
                'enable_content_filtering': True,
                'min_confidence_score': 0.5,
                'enable_pattern_optimization': True,
                'patterns': [
                    'numbered_standard',
                    'dot_numbered',
                    'space_numbered',
                    'real_exam',
                    'parentheses',
                    'colon'
                ]
            },
            'validation': {
                'enable_validation': True,
                'strict_mode': False,
                'enable_quality_scoring': True,
                'min_quality_score': 0.7,
                'enable_detailed_reporting': True,
                'rules': {
                    'question_number': {
                        'required': True,
                        'pattern': '^\\d+$',
                        'min_length': 1,
                        'max_length': 3
                    },
                    'question_text': {
                        'required': True,
                        'min_length': 10,
                        'max_length': 1000,
                        'forbidden_keywords': [
                            '代號', '頁次', '考試', '科目', '時間', '座號'
                        ],
                        'required_indicators': [
                            '？', '?', '什麼', '何者', '哪個'
                        ]
                    },
                    'options': {
                        'min_count': 2,
                        'max_count': 4,
                        'min_length': 2,
                        'max_length': 200,
                        'required_letters': ['A', 'B', 'C', 'D']
                    }
                }
            },
            'output': {
                'encoding': 'utf-8-sig',
                'csv_delimiter': ',',
                'enable_multiple_formats': True,
                'formats': ['csv', 'json', 'xlsx'],
                'enable_statistics': True,
                'enable_validation_report': True,
                'enable_performance_report': True
            },
            'google_form': {
                'enable_generation': True,
                'form_title': '考古題練習表單',
                'form_description': '此表單包含 {total_questions} 題考古題，用於練習和自測',
                'collect_email': True,
                'require_login': False,
                'enable_auto_scoring': True,
                'show_answers_after_submit': True,
                'default_question_type': '選擇題',
                'enable_question_groups': True,
                'enable_script_generation': True
            },
            'performance': {
                'enable_monitoring': True,
                'enable_profiling': False,
                'enable_memory_tracking': True,
                'enable_cpu_tracking': True,
                'log_interval': 60,  # 秒
                'max_log_entries': 1000
            },
            'logging': {
                'level': 'INFO',
                'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                'enable_file_logging': True,
                'log_file': 'logs/enhanced_processing.log',
                'max_file_size': 10485760,  # 10MB
                'backup_count': 5,
                'enable_console_logging': True
            }
        }
    
    def load_config(self, config_file: str) -> bool:
        """載入配置檔案"""
        try:
            with self.lock:
                if not os.path.exists(config_file):
                    self.logger.warning(f"配置檔案不存在: {config_file}")
                    return False
                
                with open(config_file, 'r', encoding='utf-8') as f:
                    if config_file.endswith('.yaml') or config_file.endswith('.yml'):
                        loaded_config = yaml.safe_load(f)
                    else:
                        loaded_config = json.load(f)
                
                # 合併配置
                self.config = self._merge_configs(self.config, loaded_config)
                self.config_file = config_file
                
                self.logger.info(f"配置檔案載入成功: {config_file}")
                return True
                
        except Exception as e:
            self.logger.error(f"載入配置檔案失敗: {e}")
            return False
    
    def save_config(self, config_file: Optional[str] = None) -> bool:
        """儲存配置檔案"""
        try:
            with self.lock:
                target_file = config_file or self.config_file
                
                with open(target_file, 'w', encoding='utf-8') as f:
                    if target_file.endswith('.yaml') or target_file.endswith('.yml'):
                        yaml.dump(self.config, f, default_flow_style=False, allow_unicode=True, indent=2)
                    else:
                        json.dump(self.config, f, ensure_ascii=False, indent=2)
                
                self.logger.info(f"配置檔案儲存成功: {target_file}")
                return True
                
        except Exception as e:
            self.logger.error(f"儲存配置檔案失敗: {e}")
            return False
    
    def get_config(self, key: str, default: Any = None) -> Any:
        """獲取配置值"""
        try:
            with self.lock:
                keys = key.split('.')
                value = self.config
                
                for k in keys:
                    if isinstance(value, dict) and k in value:
                        value = value[k]
                    else:
                        return default
                
                return value
                
        except Exception as e:
            self.logger.error(f"獲取配置失敗: {key} - {e}")
            return default
    
    def set_config(self, key: str, value: Any) -> bool:
        """設置配置值"""
        try:
            with self.lock:
                keys = key.split('.')
                config = self.config
                
                # 導航到目標位置
                for k in keys[:-1]:
                    if k not in config:
                        config[k] = {}
                    config = config[k]
                
                # 設置值
                config[keys[-1]] = value
                
                self.logger.debug(f"配置已更新: {key} = {value}")
                return True
                
        except Exception as e:
            self.logger.error(f"設置配置失敗: {key} - {e}")
            return False
    
    def update_config(self, updates: Dict[str, Any]) -> bool:
        """批量更新配置"""
        try:
            with self.lock:
                self.config = self._merge_configs(self.config, updates)
                self.logger.info(f"配置已批量更新: {len(updates)} 項")
                return True
                
        except Exception as e:
            self.logger.error(f"批量更新配置失敗: {e}")
            return False
    
    def _merge_configs(self, base: Dict[str, Any], updates: Dict[str, Any]) -> Dict[str, Any]:
        """合併配置"""
        result = base.copy()
        
        for key, value in updates.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_configs(result[key], value)
            else:
                result[key] = value
        
        return result
    
    def get_processing_config(self) -> Dict[str, Any]:
        """獲取處理配置"""
        return self.get_config('processing', {})
    
    def get_question_group_config(self) -> Dict[str, Any]:
        """獲取題組配置"""
        return self.get_config('question_group', {})
    
    def get_option_extraction_config(self) -> Dict[str, Any]:
        """獲取選項提取配置"""
        return self.get_config('option_extraction', {})
    
    def get_question_parsing_config(self) -> Dict[str, Any]:
        """獲取題目解析配置"""
        return self.get_config('question_parsing', {})
    
    def get_validation_config(self) -> Dict[str, Any]:
        """獲取驗證配置"""
        return self.get_config('validation', {})
    
    def get_output_config(self) -> Dict[str, Any]:
        """獲取輸出配置"""
        return self.get_config('output', {})
    
    def get_google_form_config(self) -> Dict[str, Any]:
        """獲取Google表單配置"""
        return self.get_config('google_form', {})
    
    def get_performance_config(self) -> Dict[str, Any]:
        """獲取性能配置"""
        return self.get_config('performance', {})
    
    def get_logging_config(self) -> Dict[str, Any]:
        """獲取日誌配置"""
        return self.get_config('logging', {})
    
    def validate_config(self) -> Dict[str, Any]:
        """驗證配置"""
        validation_result = {
            'is_valid': True,
            'errors': [],
            'warnings': []
        }
        
        # 驗證必要配置
        required_configs = [
            'system.name',
            'system.version',
            'processing.max_text_length',
            'processing.min_question_length',
            'processing.max_question_length'
        ]
        
        for config_key in required_configs:
            if self.get_config(config_key) is None:
                validation_result['is_valid'] = False
                validation_result['errors'].append(f"缺少必要配置: {config_key}")
        
        # 驗證數值範圍
        numeric_configs = [
            ('processing.max_text_length', 1000, 10000000),
            ('processing.min_question_length', 1, 100),
            ('processing.max_question_length', 10, 5000),
            ('question_group.max_questions_per_group', 1, 50),
            ('validation.min_quality_score', 0.0, 1.0)
        ]
        
        for config_key, min_val, max_val in numeric_configs:
            value = self.get_config(config_key)
            if value is not None:
                if not isinstance(value, (int, float)) or not (min_val <= value <= max_val):
                    validation_result['warnings'].append(f"配置值超出建議範圍: {config_key} = {value}")
        
        return validation_result
    
    def reset_to_default(self) -> bool:
        """重置為預設配置"""
        try:
            with self.lock:
                self.config = self._load_default_config()
                self.logger.info("配置已重置為預設值")
                return True
                
        except Exception as e:
            self.logger.error(f"重置配置失敗: {e}")
            return False
    
    def export_config(self, export_file: str, format: str = 'json') -> bool:
        """匯出配置"""
        try:
            with self.lock:
                if format.lower() == 'yaml':
                    with open(export_file, 'w', encoding='utf-8') as f:
                        yaml.dump(self.config, f, default_flow_style=False, allow_unicode=True, indent=2)
                else:
                    with open(export_file, 'w', encoding='utf-8') as f:
                        json.dump(self.config, f, ensure_ascii=False, indent=2)
                
                self.logger.info(f"配置已匯出: {export_file}")
                return True
                
        except Exception as e:
            self.logger.error(f"匯出配置失敗: {e}")
            return False
    
    def get_config_summary(self) -> Dict[str, Any]:
        """獲取配置摘要"""
        return {
            'system_name': self.get_config('system.name'),
            'version': self.get_config('system.version'),
            'debug_mode': self.get_config('system.debug'),
            'log_level': self.get_config('system.log_level'),
            'max_workers': self.get_config('system.max_workers'),
            'memory_threshold': self.get_config('system.memory_threshold'),
            'processing_enabled': {
                'question_group_detection': self.get_config('question_group.enable_detection'),
                'enhanced_option_extraction': self.get_config('option_extraction.enable_enhanced_extraction'),
                'enhanced_question_parsing': self.get_config('question_parsing.enable_enhanced_parsing'),
                'validation': self.get_config('validation.enable_validation'),
                'parallel_processing': self.get_config('processing.enable_parallel_processing'),
                'memory_optimization': self.get_config('processing.enable_memory_optimization')
            },
            'output_formats': self.get_config('output.formats', []),
            'google_form_enabled': self.get_config('google_form.enable_generation'),
            'performance_monitoring': self.get_config('performance.enable_monitoring')
        }

# 全域配置實例
config_system = EnhancedConfigSystem()

# 便捷函數
def get_config(key: str, default: Any = None) -> Any:
    """獲取配置值"""
    return config_system.get_config(key, default)

def set_config(key: str, value: Any) -> bool:
    """設置配置值"""
    return config_system.set_config(key, value)

def load_config(config_file: str) -> bool:
    """載入配置檔案"""
    return config_system.load_config(config_file)

def save_config(config_file: Optional[str] = None) -> bool:
    """儲存配置檔案"""
    return config_system.save_config(config_file)

def main():
    """測試函數"""
    config = EnhancedConfigSystem()
    
    # 測試基本操作
    print("測試配置系統...")
    
    # 獲取配置
    system_name = config.get_config('system.name')
    print(f"系統名稱: {system_name}")
    
    # 設置配置
    config.set_config('system.debug', True)
    debug_mode = config.get_config('system.debug')
    print(f"除錯模式: {debug_mode}")
    
    # 驗證配置
    validation = config.validate_config()
    print(f"配置驗證: {validation}")
    
    # 獲取配置摘要
    summary = config.get_config_summary()
    print(f"配置摘要: {json.dumps(summary, indent=2, ensure_ascii=False)}")
    
    # 儲存配置
    config.save_config('test_config.json')
    print("配置已儲存到 test_config.json")

if __name__ == "__main__":
    main()