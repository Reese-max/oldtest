#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試國際化系統
"""

import os
import sys
import unittest

# 添加專案根目錄到路徑
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.i18n import I18nManager, get_current_language, get_text, set_language


class TestI18nManager(unittest.TestCase):
    """測試 I18nManager 類"""

    def setUp(self):
        """測試前設置"""
        self.i18n = I18nManager(default_language="zh-TW")

    def test_init(self):
        """測試初始化"""
        self.assertEqual(self.i18n.default_language, "zh-TW")
        self.assertEqual(self.i18n.current_language, "zh-TW")
        self.assertIn("zh-TW", self.i18n.translations)
        self.assertIn("en", self.i18n.translations)

    def test_get_supported_languages(self):
        """測試獲取支持的語言"""
        languages = self.i18n.get_supported_languages()
        self.assertIn("zh-TW", languages)
        self.assertIn("zh-CN", languages)
        self.assertIn("en", languages)
        self.assertIn("ja", languages)
        self.assertEqual(languages["zh-TW"], "繁體中文")
        self.assertEqual(languages["en"], "English")

    def test_set_language(self):
        """測試設置語言"""
        # 設置為英文
        result = self.i18n.set_language("en")
        self.assertTrue(result)
        self.assertEqual(self.i18n.current_language, "en")

        # 設置為簡體中文
        result = self.i18n.set_language("zh-CN")
        self.assertTrue(result)
        self.assertEqual(self.i18n.current_language, "zh-CN")

        # 設置不支持的語言
        result = self.i18n.set_language("fr")
        self.assertFalse(result)
        self.assertEqual(self.i18n.current_language, "zh-CN")  # 保持不變

    def test_get_text_simple(self):
        """測試獲取簡單文本"""
        # 繁體中文
        self.i18n.set_language("zh-TW")
        text = self.i18n.get_text("app.name")
        self.assertEqual(text, "考古題處理系統")

        # 英文
        self.i18n.set_language("en")
        text = self.i18n.get_text("app.name")
        self.assertEqual(text, "Exam Question Processor")

        # 日文
        self.i18n.set_language("ja")
        text = self.i18n.get_text("app.name")
        self.assertEqual(text, "試験問題処理システム")

    def test_get_text_with_format(self):
        """測試獲取格式化文本"""
        self.i18n.set_language("zh-TW")

        # 格式化參數
        text = self.i18n.get_text("app.version", version="1.0.0")
        self.assertEqual(text, "版本 1.0.0")

        # 英文格式化
        self.i18n.set_language("en")
        text = self.i18n.get_text("app.version", version="2.0.0")
        self.assertEqual(text, "Version 2.0.0")

    def test_get_text_nested(self):
        """測試獲取嵌套鍵值"""
        self.i18n.set_language("zh-TW")

        # 深層嵌套
        text = self.i18n.get_text("messages.success")
        self.assertEqual(text, "✅ 成功")

        text = self.i18n.get_text("pdf.extracting")
        self.assertEqual(text, "正在提取PDF文字...")

    def test_get_text_not_found(self):
        """測試獲取不存在的鍵值"""
        self.i18n.set_language("zh-TW")

        # 不存在的鍵值，返回鍵值本身
        text = self.i18n.get_text("non.existent.key")
        self.assertEqual(text, "non.existent.key")

    def test_get_text_fallback_to_default(self):
        """測試回退到默認語言"""
        # 假設某個鍵值在當前語言中不存在
        self.i18n.set_language("en")

        # 應該能從默認語言（zh-TW）獲取
        text = self.i18n.get_text("app.name")
        self.assertIsNotNone(text)

    def test_is_language_supported(self):
        """測試檢查語言支持"""
        self.assertTrue(self.i18n.is_language_supported("zh-TW"))
        self.assertTrue(self.i18n.is_language_supported("en"))
        self.assertTrue(self.i18n.is_language_supported("ja"))
        self.assertFalse(self.i18n.is_language_supported("fr"))
        self.assertFalse(self.i18n.is_language_supported("de"))


class TestGlobalI18nFunctions(unittest.TestCase):
    """測試全局 i18n 函數"""

    def test_set_language_global(self):
        """測試全局設置語言"""
        set_language("en")
        self.assertEqual(get_current_language(), "en")

        set_language("zh-TW")
        self.assertEqual(get_current_language(), "zh-TW")

    def test_get_text_global(self):
        """測試全局獲取文本"""
        set_language("zh-TW")
        text = get_text("messages.success")
        self.assertEqual(text, "✅ 成功")

        set_language("en")
        text = get_text("messages.success")
        self.assertEqual(text, "✅ Success")

    def test_get_text_with_params(self):
        """測試全局獲取帶參數的文本"""
        set_language("zh-TW")
        text = get_text("pdf.extracting_page", page=5, total=10)
        self.assertIn("5", text)
        self.assertIn("10", text)


class TestI18nLanguages(unittest.TestCase):
    """測試各種語言的翻譯"""

    def setUp(self):
        """測試前設置"""
        self.i18n = I18nManager()

    def test_traditional_chinese(self):
        """測試繁體中文"""
        self.i18n.set_language("zh-TW")

        self.assertEqual(self.i18n.get_text("app.name"), "考古題處理系統")
        self.assertEqual(self.i18n.get_text("messages.success"), "✅ 成功")
        self.assertEqual(self.i18n.get_text("pdf.extracting"), "正在提取PDF文字...")

    def test_simplified_chinese(self):
        """測試簡體中文"""
        self.i18n.set_language("zh-CN")

        self.assertEqual(self.i18n.get_text("app.name"), "考古题处理系统")
        self.assertEqual(self.i18n.get_text("messages.success"), "✅ 成功")
        self.assertEqual(self.i18n.get_text("pdf.extracting"), "正在提取PDF文字...")

    def test_english(self):
        """測試英文"""
        self.i18n.set_language("en")

        self.assertEqual(self.i18n.get_text("app.name"), "Exam Question Processor")
        self.assertEqual(self.i18n.get_text("messages.success"), "✅ Success")
        self.assertEqual(self.i18n.get_text("pdf.extracting"), "Extracting PDF text...")

    def test_japanese(self):
        """測試日文"""
        self.i18n.set_language("ja")

        self.assertEqual(self.i18n.get_text("app.name"), "試験問題処理システム")
        self.assertEqual(self.i18n.get_text("messages.success"), "✅ 成功")
        self.assertEqual(self.i18n.get_text("pdf.extracting"), "PDFテキストを抽出中...")


class TestI18nComplexScenarios(unittest.TestCase):
    """測試複雜場景"""

    def setUp(self):
        """測試前設置"""
        self.i18n = I18nManager()

    def test_multiple_parameters(self):
        """測試多個參數"""
        self.i18n.set_language("zh-TW")

        text = self.i18n.get_text("processor.batch_completed", success=10, failed=2)
        self.assertIn("10", text)
        self.assertIn("2", text)

    def test_language_switching(self):
        """測試語言切換"""
        # 繁體中文
        self.i18n.set_language("zh-TW")
        text1 = self.i18n.get_text("messages.processing")

        # 切換到英文
        self.i18n.set_language("en")
        text2 = self.i18n.get_text("messages.processing")

        # 切換到日文
        self.i18n.set_language("ja")
        text3 = self.i18n.get_text("messages.processing")

        # 確保不同
        self.assertNotEqual(text1, text2)
        self.assertNotEqual(text2, text3)
        self.assertNotEqual(text1, text3)

    def test_error_messages(self):
        """測試錯誤訊息"""
        self.i18n.set_language("zh-TW")

        error_msg = self.i18n.get_text("errors.file_not_found", path="/test/file.pdf")
        self.assertIn("/test/file.pdf", error_msg)

        self.i18n.set_language("en")
        error_msg = self.i18n.get_text("errors.file_not_found", path="/test/file.pdf")
        self.assertIn("/test/file.pdf", error_msg)


if __name__ == "__main__":
    unittest.main()
