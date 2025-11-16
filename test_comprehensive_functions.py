#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
全面功能測試套件
測試所有核心功能和最近的代碼修正
"""

import sys
import os
import tempfile
import traceback
from pathlib import Path

# 添加專案路徑
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


class ComprehensiveFunctionalTest:
    """全面功能測試類"""

    def __init__(self):
        # 延遲導入 logger 以避免初始依賴問題
        from src.utils.logger import logger
        self.logger = logger
        self.test_results = []
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0

    def run_test(self, test_name, test_func):
        """運行單個測試"""
        self.total_tests += 1
        try:
            test_func()
            self.test_results.append((test_name, "✅ PASS", None))
            self.passed_tests += 1
            self.logger.success(f"✅ {test_name} - 通過")
            return True
        except Exception as e:
            self.test_results.append((test_name, "❌ FAIL", str(e)))
            self.failed_tests += 1
            self.logger.failure(f"❌ {test_name} - 失敗: {e}")
            traceback.print_exc()
            return False

    # ========== 測試 1: 修正的除零錯誤 ==========
    def test_division_by_zero_fix(self):
        """測試除零錯誤修正（quality_validator.py）"""
        # 檢查代碼修正
        validator_path = Path(__file__).parent / 'src' / 'utils' / 'quality_validator.py'
        with open(validator_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 驗證包含除零檢查
        assert 'if stats[\'total_questions\'] > 0' in content, "缺少除零檢查"
        assert 'valid_rate' in content, "缺少 valid_rate 變數"

    # ========== 測試 2: OCR 資源管理 ==========
    def test_ocr_resource_management(self):
        """測試 OCR 資源管理（臨時目錄清理）"""
        ocr_path = Path(__file__).parent / 'src' / 'core' / 'ocr_processor.py'
        with open(ocr_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 驗證包含必要的修正
        assert 'import shutil' in content, "缺少 shutil 導入"
        assert 'self._temp_dirs' in content, "缺少 _temp_dirs 屬性"
        assert 'self._temp_dirs.append(temp_dir)' in content, "缺少臨時目錄追蹤"
        assert 'shutil.rmtree(temp_dir)' in content, "缺少臨時目錄清理"

    # ========== 測試 3: None 值檢查 ==========
    def test_none_value_handling(self):
        """測試 None 值檢查（archaeology_processor.py）"""
        processor_path = Path(__file__).parent / 'src' / 'processors' / 'archaeology_processor.py'
        with open(processor_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 驗證包含 None 檢查
        assert 'if answer_text:' in content, "缺少 answer_text 的 None 檢查"
        assert 'if corrected_text:' in content, "缺少 corrected_text 的 None 檢查"
        assert 'self.logger.warning(f"無法從答案PDF提取文字' in content, "缺少警告訊息"

    # ========== 測試 4: 導入正確性 ==========
    def test_import_correctness(self):
        """測試導入正確性（無重複、無未使用）"""
        # 測試 api.py 沒有重複導入
        api_path = Path(__file__).parent / 'src' / 'api.py'
        with open(api_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        # 計算 ConfigManager 導入次數
        config_imports = [line for line in lines if 'from .utils.config import ConfigManager' in line]
        assert len(config_imports) == 1, f"ConfigManager 導入次數錯誤: {len(config_imports)}"

        # 測試 comprehensive_question_parser.py 沒有未使用的 os 導入
        parser_path = Path(__file__).parent / 'src' / 'core' / 'comprehensive_question_parser.py'
        with open(parser_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 檢查不應該有獨立的 "import os"
        lines = content.split('\n')
        import_lines = [line.strip() for line in lines if line.strip().startswith('import ')]
        os_import = [line for line in import_lines if line == 'import os']

        assert len(os_import) == 0, f"發現未使用的 os 導入: {os_import}"

    # ========== 測試 5: 配置系統 ==========
    def test_config_system(self):
        """測試配置系統載入"""
        from src.utils.config import config_manager

        # 測試配置管理器已正確初始化
        assert config_manager is not None, "配置管理器未初始化"

        # 測試獲取配置
        google_config = config_manager.get_google_form_config()
        assert google_config is not None, "Google 表單配置未載入"
        assert hasattr(google_config, 'enable_auto_scoring'), "缺少 enable_auto_scoring 配置"

        # 測試 OCR 配置
        ocr_config = config_manager.get_ocr_config()
        assert ocr_config is not None, "OCR 配置未載入"
        assert hasattr(ocr_config, 'enable_ocr'), "缺少 enable_ocr 配置"
        assert hasattr(ocr_config, 'ocr_fallback'), "缺少 ocr_fallback 配置"
        assert hasattr(ocr_config, 'confidence_threshold'), "缺少 confidence_threshold 配置"

    # ========== 測試 6: CSV 生成器 ==========
    def test_csv_generator(self):
        """測試 CSV 生成器基本功能"""
        from src.core.csv_generator import CSVGenerator

        csv_gen = CSVGenerator()

        test_questions = [
            {
                '題號': '1',
                '題目': '測試題目',
                '題型': '選擇題',
                '選項A': '選項A',
                '選項B': '選項B',
                '選項C': '選項C',
                '選項D': '選項D',
                '題組': False
            }
        ]

        test_answers = {'1': 'A'}

        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            temp_path = f.name

        try:
            # 測試生成 CSV
            result = csv_gen.generate_questions_csv(test_questions, test_answers, temp_path)
            assert os.path.exists(result), "CSV 檔案未生成"

            # 驗證 CSV 內容
            import pandas as pd
            df = pd.read_csv(result, encoding='utf-8-sig')
            assert len(df) == 1, "CSV 題目數量錯誤"
            assert str(df.iloc[0]['題號']) == '1', "題號錯誤"
            assert str(df.iloc[0]['正確答案']) == 'A', "答案錯誤"
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

    # ========== 測試 7: 語法檢查 ==========
    def test_syntax_validation(self):
        """測試修正的文件語法正確"""
        import py_compile

        files_to_check = [
            'src/utils/quality_validator.py',
            'src/core/ocr_processor.py',
            'src/processors/archaeology_processor.py',
            'src/api.py',
            'src/core/comprehensive_question_parser.py'
        ]

        for file_path in files_to_check:
            full_path = Path(__file__).parent / file_path
            try:
                py_compile.compile(str(full_path), doraise=True)
            except py_compile.PyCompileError as e:
                raise AssertionError(f"語法錯誤 {file_path}: {e}")

    # ========== 測試 8: 錯誤處理 ==========
    def test_error_handling(self):
        """測試錯誤處理機制"""
        from src.utils.exceptions import (
            ArchaeologyQuestionsError,
            PDFProcessingError,
            CSVGenerationError,
            GoogleFormError
        )

        # 驗證所有異常類存在且可實例化
        exceptions = [
            ArchaeologyQuestionsError,
            PDFProcessingError,
            CSVGenerationError,
            GoogleFormError
        ]

        for exc_class in exceptions:
            try:
                raise exc_class("測試錯誤")
            except exc_class as e:
                assert str(e) == "測試錯誤", f"{exc_class.__name__} 訊息不正確"

    # ========== 測試 9: 日誌系統 ==========
    def test_logging_system(self):
        """測試日誌系統"""
        from src.utils.logger import logger

        # 測試各種日誌級別
        logger.info("測試 INFO 日誌")
        logger.success("測試 SUCCESS 日誌")
        logger.warning("測試 WARNING 日誌")

        # 驗證日誌器有必要的方法
        assert hasattr(logger, 'info'), "日誌器缺少 info 方法"
        assert hasattr(logger, 'success'), "日誌器缺少 success 方法"
        assert hasattr(logger, 'warning'), "日誌器缺少 warning 方法"
        assert hasattr(logger, 'failure'), "日誌器缺少 failure 方法"

    # ========== 測試 10: 文件完整性 ==========
    def test_file_integrity(self):
        """測試所有修正的文件存在"""
        files = [
            'src/utils/quality_validator.py',
            'src/core/ocr_processor.py',
            'src/processors/archaeology_processor.py',
            'src/api.py',
            'src/core/comprehensive_question_parser.py',
            'CODE_FIX_REPORT.md',
            'code_analysis_report.md',
        ]

        for file_path in files:
            full_path = Path(__file__).parent / file_path
            assert full_path.exists(), f"檔案不存在: {file_path}"

    def run_all_tests(self):
        """運行所有測試"""
        self.logger.info("\n" + "=" * 70)
        self.logger.info("🧪 開始全面功能測試")
        self.logger.info("=" * 70 + "\n")

        # 測試列表
        tests = [
            ("修正的除零錯誤", self.test_division_by_zero_fix),
            ("OCR 資源管理", self.test_ocr_resource_management),
            ("None 值處理", self.test_none_value_handling),
            ("導入正確性", self.test_import_correctness),
            ("配置系統", self.test_config_system),
            ("CSV 生成器", self.test_csv_generator),
            ("語法驗證", self.test_syntax_validation),
            ("錯誤處理", self.test_error_handling),
            ("日誌系統", self.test_logging_system),
            ("文件完整性", self.test_file_integrity),
        ]

        # 運行所有測試
        for test_name, test_func in tests:
            self.logger.info(f"\n▶ 測試: {test_name}")
            self.run_test(test_name, test_func)

        # 輸出結果
        self.print_summary()

    def print_summary(self):
        """輸出測試摘要"""
        self.logger.info("\n" + "=" * 70)
        self.logger.info("📊 測試結果摘要")
        self.logger.info("=" * 70 + "\n")

        for test_name, status, error in self.test_results:
            if error:
                self.logger.info(f"{status} {test_name}")
                self.logger.info(f"   錯誤: {error}")
            else:
                self.logger.info(f"{status} {test_name}")

        self.logger.info("\n" + "-" * 70)
        self.logger.info(f"總測試數: {self.total_tests}")
        self.logger.info(f"✅ 通過: {self.passed_tests}")
        self.logger.info(f"❌ 失敗: {self.failed_tests}")
        pass_rate = (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0
        self.logger.info(f"通過率: {pass_rate:.1f}%")
        self.logger.info("-" * 70 + "\n")

        if self.failed_tests == 0:
            self.logger.success("🎉 所有測試通過！")
        else:
            self.logger.failure(f"⚠️  有 {self.failed_tests} 個測試失敗")

        return self.failed_tests == 0


def main():
    """主函數"""
    tester = ComprehensiveFunctionalTest()
    success = tester.run_all_tests()
    return 0 if success else 1


if __name__ == '__main__':
    sys.exit(main())
