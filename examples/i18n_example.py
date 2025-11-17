#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
國際化（i18n）使用範例
演示如何在項目中使用多語言支持
"""

import sys
import os

# 添加專案根目錄到路徑
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.i18n import get_text, set_language, get_current_language
from src.i18n import I18nManager


def example_basic_usage():
    """基本使用範例"""
    print("=" * 60)
    print("範例 1: 基本使用")
    print("=" * 60)

    # 獲取當前語言
    current = get_current_language()
    print(f"當前語言: {current}")

    # 獲取翻譯文本
    app_name = get_text('app.name')
    print(f"應用名稱: {app_name}")

    success_msg = get_text('messages.success')
    print(f"成功訊息: {success_msg}")

    print()


def example_language_switching():
    """語言切換範例"""
    print("=" * 60)
    print("範例 2: 語言切換")
    print("=" * 60)

    languages = ['zh-TW', 'zh-CN', 'en', 'ja']

    for lang in languages:
        set_language(lang)
        app_name = get_text('app.name')
        print(f"{lang}: {app_name}")

    print()


def example_formatted_text():
    """格式化文本範例"""
    print("=" * 60)
    print("範例 3: 格式化文本")
    print("=" * 60)

    # 繁體中文
    set_language('zh-TW')
    text = get_text('app.version', version='1.8.0')
    print(f"繁體中文: {text}")

    # 英文
    set_language('en')
    text = get_text('app.version', version='1.8.0')
    print(f"English: {text}")

    # 日文
    set_language('ja')
    text = get_text('app.version', version='1.8.0')
    print(f"日本語: {text}")

    print()


def example_pdf_processing_messages():
    """PDF處理訊息範例"""
    print("=" * 60)
    print("範例 4: PDF處理訊息（多語言）")
    print("=" * 60)

    languages = {
        'zh-TW': '繁體中文',
        'en': 'English',
        'ja': '日本語'
    }

    for lang_code, lang_name in languages.items():
        set_language(lang_code)
        print(f"\n{lang_name} ({lang_code}):")
        print(f"  - {get_text('pdf.extracting')}")
        print(f"  - {get_text('parser.parsing')}")
        print(f"  - {get_text('processor.generating_csv')}")

    print()


def example_progress_messages():
    """進度訊息範例"""
    print("=" * 60)
    print("範例 5: 進度訊息")
    print("=" * 60)

    set_language('zh-TW')
    print("繁體中文:")
    for i in range(1, 6):
        text = get_text('pdf.extracting_page', page=i, total=5)
        print(f"  {text}")

    print("\nEnglish:")
    set_language('en')
    for i in range(1, 6):
        text = get_text('pdf.extracting_page', page=i, total=5)
        print(f"  {text}")

    print()


def example_error_messages():
    """錯誤訊息範例"""
    print("=" * 60)
    print("範例 6: 錯誤訊息")
    print("=" * 60)

    error_scenarios = [
        ('errors.file_not_found', {'path': '/path/to/file.pdf'}),
        ('errors.invalid_format', {'format': 'unknown'}),
        ('errors.out_of_memory', {}),
    ]

    for lang in ['zh-TW', 'en']:
        set_language(lang)
        print(f"\n{lang}:")
        for key, params in error_scenarios:
            text = get_text(key, **params)
            print(f"  ❌ {text}")

    print()


def example_status_messages():
    """狀態訊息範例"""
    print("=" * 60)
    print("範例 7: 處理狀態訊息")
    print("=" * 60)

    statuses = [
        'messages.processing',
        'messages.completed',
        'messages.success',
        'messages.warning',
        'messages.error'
    ]

    for lang in ['zh-TW', 'zh-CN', 'en', 'ja']:
        set_language(lang)
        print(f"\n{lang}:")
        for status in statuses:
            text = get_text(status)
            print(f"  {text}")

    print()


def example_cli_messages():
    """命令行介面訊息範例"""
    print("=" * 60)
    print("範例 8: CLI 訊息")
    print("=" * 60)

    cli_keys = [
        'cli.usage',
        'cli.options',
        'cli.help',
        'cli.version',
        'cli.language'
    ]

    for lang in ['zh-TW', 'en']:
        set_language(lang)
        print(f"\n{lang}:")
        for key in cli_keys:
            text = get_text(key)
            print(f"  • {text}")

    print()


def example_custom_i18n_manager():
    """自定義 I18nManager 範例"""
    print("=" * 60)
    print("範例 9: 自定義 I18nManager")
    print("=" * 60)

    # 創建自定義實例（不使用全局實例）
    i18n = I18nManager(default_language='en')

    # 獲取支持的語言
    languages = i18n.get_supported_languages()
    print("支持的語言:")
    for code, name in languages.items():
        print(f"  {code}: {name}")

    # 檢查語言支持
    print("\n語言支持檢查:")
    print(f"  zh-TW 是否支持: {i18n.is_language_supported('zh-TW')}")
    print(f"  fr 是否支持: {i18n.is_language_supported('fr')}")

    print()


def example_batch_processing_messages():
    """批量處理訊息範例"""
    print("=" * 60)
    print("範例 10: 批量處理訊息")
    print("=" * 60)

    set_language('zh-TW')
    print("模擬批量處理:")
    print(get_text('processor.processing_batch', count=10))
    print(get_text('processor.batch_progress', current=3, total=10))
    print(get_text('processor.batch_progress', current=7, total=10))
    print(get_text('processor.batch_completed', success=8, failed=2))

    print("\n英文版本:")
    set_language('en')
    print(get_text('processor.processing_batch', count=10))
    print(get_text('processor.batch_progress', current=3, total=10))
    print(get_text('processor.batch_progress', current=7, total=10))
    print(get_text('processor.batch_completed', success=8, failed=2))

    print()


def main():
    """主函數"""
    print("\n")
    print("╔" + "═" * 58 + "╗")
    print("║" + " " * 15 + "國際化（i18n）使用範例" + " " * 15 + "║")
    print("╚" + "═" * 58 + "╝")
    print()

    # 執行所有範例
    example_basic_usage()
    example_language_switching()
    example_formatted_text()
    example_pdf_processing_messages()
    example_progress_messages()
    example_error_messages()
    example_status_messages()
    example_cli_messages()
    example_custom_i18n_manager()
    example_batch_processing_messages()

    print("=" * 60)
    print("所有範例執行完成！")
    print("=" * 60)


if __name__ == '__main__':
    main()
