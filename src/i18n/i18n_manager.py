#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
國際化管理器
負責管理多語言翻譯和語言切換
"""

import os
import json
from typing import Dict, Optional, Any
from pathlib import Path


class I18nManager:
    """國際化管理器"""

    # 支持的語言
    SUPPORTED_LANGUAGES = {
        'zh-TW': '繁體中文',
        'zh-CN': '简体中文',
        'en': 'English',
        'ja': '日本語'
    }

    def __init__(self, default_language: str = 'zh-TW'):
        """
        初始化國際化管理器

        Args:
            default_language: 默認語言代碼
        """
        self.default_language = default_language
        self.current_language = default_language
        self.translations: Dict[str, Dict[str, str]] = {}

        # 獲取語言檔案目錄
        self.locales_dir = Path(__file__).parent / 'locales'

        # 載入所有語言
        self._load_all_languages()

    def _load_all_languages(self):
        """載入所有支持的語言"""
        for lang_code in self.SUPPORTED_LANGUAGES.keys():
            self._load_language(lang_code)

    def _load_language(self, lang_code: str):
        """
        載入指定語言的翻譯檔案

        Args:
            lang_code: 語言代碼
        """
        lang_file = self.locales_dir / f'{lang_code}.json'

        if lang_file.exists():
            try:
                with open(lang_file, 'r', encoding='utf-8') as f:
                    self.translations[lang_code] = json.load(f)
            except Exception as e:
                print(f"⚠️  載入語言檔案失敗 ({lang_code}): {e}")
                self.translations[lang_code] = {}
        else:
            print(f"⚠️  語言檔案不存在: {lang_file}")
            self.translations[lang_code] = {}

    def set_language(self, lang_code: str) -> bool:
        """
        設置當前語言

        Args:
            lang_code: 語言代碼

        Returns:
            是否設置成功
        """
        if lang_code not in self.SUPPORTED_LANGUAGES:
            print(f"⚠️  不支持的語言: {lang_code}")
            return False

        self.current_language = lang_code
        return True

    def get_text(self, key: str, **kwargs) -> str:
        """
        獲取翻譯文本

        Args:
            key: 翻譯鍵值（支持點號分隔的嵌套鍵，如 'messages.success'）
            **kwargs: 用於格式化的參數

        Returns:
            翻譯後的文本
        """
        # 獲取當前語言的翻譯
        translation = self._get_nested_value(
            self.translations.get(self.current_language, {}),
            key
        )

        # 如果當前語言沒有翻譯，嘗試使用默認語言
        if translation is None and self.current_language != self.default_language:
            translation = self._get_nested_value(
                self.translations.get(self.default_language, {}),
                key
            )

        # 如果還是沒有翻譯，返回鍵值本身
        if translation is None:
            return key

        # 格式化翻譯文本
        try:
            return translation.format(**kwargs)
        except KeyError:
            return translation

    def _get_nested_value(self, data: Dict, key: str) -> Optional[str]:
        """
        獲取嵌套字典的值

        Args:
            data: 字典數據
            key: 鍵值（支持點號分隔）

        Returns:
            對應的值，如果不存在則返回 None
        """
        keys = key.split('.')
        value = data

        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return None

        return value if isinstance(value, str) else None

    def get_current_language(self) -> str:
        """
        獲取當前語言代碼

        Returns:
            當前語言代碼
        """
        return self.current_language

    def get_supported_languages(self) -> Dict[str, str]:
        """
        獲取所有支持的語言

        Returns:
            語言代碼到語言名稱的映射
        """
        return self.SUPPORTED_LANGUAGES.copy()

    def is_language_supported(self, lang_code: str) -> bool:
        """
        檢查語言是否支持

        Args:
            lang_code: 語言代碼

        Returns:
            是否支持
        """
        return lang_code in self.SUPPORTED_LANGUAGES


# 全局 i18n 管理器實例
_global_i18n_manager: Optional[I18nManager] = None


def get_i18n_manager() -> I18nManager:
    """
    獲取全局 i18n 管理器實例

    Returns:
        I18nManager 實例
    """
    global _global_i18n_manager

    if _global_i18n_manager is None:
        _global_i18n_manager = I18nManager()

    return _global_i18n_manager


def get_text(key: str, **kwargs) -> str:
    """
    快捷函數：獲取翻譯文本

    Args:
        key: 翻譯鍵值
        **kwargs: 格式化參數

    Returns:
        翻譯後的文本
    """
    return get_i18n_manager().get_text(key, **kwargs)


def set_language(lang_code: str) -> bool:
    """
    快捷函數：設置當前語言

    Args:
        lang_code: 語言代碼

    Returns:
        是否設置成功
    """
    return get_i18n_manager().set_language(lang_code)


def get_current_language() -> str:
    """
    快捷函數：獲取當前語言

    Returns:
        當前語言代碼
    """
    return get_i18n_manager().get_current_language()


# 簡寫別名
_ = get_text
t = get_text
