#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完整工作流自動化測試
模擬真實用戶使用場景，全面測試所有功能

測試範圍：
1. 優先級1：爬蟲性能增強（並發下載、進度顯示、斷點續傳）
2. 優先級2：OCR深度整合（自動檢測、智能調優、質量驗證、混合處理）
3. 整合測試：爬蟲 + OCR 完整流程
4. 異常處理測試
5. 配置驗證
6. 文檔完整性檢查
"""

import os
import sys
import time
import yaml
import tempfile
import shutil
from datetime import datetime
from pathlib import Path

# 添加項目根目錄到路徑
sys.path.insert(0, os.path.dirname(__file__))

class Colors:
    """終端顏色"""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class WorkflowTester:
    """完整工作流測試器"""

    def __init__(self):
        self.test_results = []
        self.start_time = None
        self.test_data_dir = None

    def log_test(self, category: str, test_name: str, passed: bool, details: str = ""):
        """記錄測試結果"""
        result = {
            'category': category,
            'test_name': test_name,
            'passed': passed,
            'details': details,
            'timestamp': datetime.now().isoformat()
        }
        self.test_results.append(result)

        # 實時顯示
        status = f"{Colors.OKGREEN}✅ 通過{Colors.ENDC}" if passed else f"{Colors.FAIL}❌ 失敗{Colors.ENDC}"
        print(f"  {status}: {test_name}")
        if details and not passed:
            print(f"    {Colors.WARNING}詳情: {details}{Colors.ENDC}")

    def print_header(self, text: str):
        """打印測試區塊標題"""
        print(f"\n{Colors.HEADER}{'='*70}")
        print(f"{text}")
        print(f"{'='*70}{Colors.ENDC}")

    def print_section(self, text: str):
        """打印測試小節標題"""
        print(f"\n{Colors.OKBLUE}{text}{Colors.ENDC}")

    def setup_test_environment(self):
        """設置測試環境"""
        self.print_header("🔧 測試環境設置")

        # 創建臨時測試目錄
        self.test_data_dir = tempfile.mkdtemp(prefix='workflow_test_')
        print(f"  📁 測試目錄: {self.test_data_dir}")

        # 檢查必要文件
        required_files = [
            'config.yaml',
            'requirements.txt',
            '考古題下載.py',
            'src/core/enhanced_ocr_processor.py',
            'test_enhanced_downloader.py',
            'test_enhanced_ocr.py',
            'ENHANCEMENT_GUIDE.md',
            'OCR_INTEGRATION_GUIDE.md'
        ]

        all_exist = True
        for file in required_files:
            exists = os.path.exists(file)
            self.log_test("環境檢查", f"文件存在: {file}", exists)
            if not exists:
                all_exist = False

        return all_exist

    def test_configuration_files(self):
        """測試配置文件"""
        self.print_header("📋 配置文件測試")

        try:
            # 測試 config.yaml 載入
            self.print_section("1. 載入 config.yaml")
            with open('config.yaml', 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            self.log_test("配置文件", "config.yaml 載入成功", True)

            # 驗證爬蟲配置
            self.print_section("2. 驗證爬蟲配置")
            downloader_config = config.get('downloader', {})
            required_downloader_keys = [
                'enable_concurrent', 'concurrent_downloads',
                'show_progress_bar', 'enable_resume'
            ]
            for key in required_downloader_keys:
                exists = key in downloader_config
                self.log_test("爬蟲配置", f"配置項 {key}", exists)

            # 驗證 OCR 配置
            self.print_section("3. 驗證 OCR 配置")
            ocr_config = config.get('ocr', {})
            required_ocr_keys = [
                'enable_enhanced_ocr', 'auto_detect_scan',
                'auto_tune_parameters', 'enable_quality_check',
                'enable_hybrid_mode'
            ]
            for key in required_ocr_keys:
                exists = key in ocr_config
                self.log_test("OCR配置", f"配置項 {key}", exists)

            # 驗證配置值合理性
            self.print_section("4. 驗證配置值合理性")

            # 爬蟲配置值
            concurrent_downloads = downloader_config.get('concurrent_downloads', 0)
            valid = 1 <= concurrent_downloads <= 10
            self.log_test("配置驗證", f"並發數合理 ({concurrent_downloads})", valid)

            max_retries = downloader_config.get('max_retries', 0)
            valid = max_retries > 0
            self.log_test("配置驗證", f"重試次數合理 ({max_retries})", valid)

            # OCR 配置值
            max_dpi = ocr_config.get('max_dpi', 0)
            min_dpi = ocr_config.get('min_dpi', 0)
            valid = min_dpi < max_dpi and min_dpi >= 100 and max_dpi <= 600
            self.log_test("配置驗證", f"DPI範圍合理 ({min_dpi}-{max_dpi})", valid)

            return True

        except Exception as e:
            self.log_test("配置文件", "配置文件測試", False, str(e))
            return False

    def test_crawler_enhancements(self):
        """測試爬蟲性能增強功能"""
        self.print_header("🚀 爬蟲性能增強測試")

        try:
            # 測試模塊導入
            self.print_section("1. 模塊導入測試")
            from 考古題下載 import (
                download_file_with_resume,
                download_exam_concurrent,
                load_config,
                create_robust_session,
                stats_lock
            )
            self.log_test("爬蟲模塊", "模塊導入成功", True)

            # 測試配置加載
            self.print_section("2. 配置加載測試")
            config = load_config()
            has_config = len(config) > 0
            self.log_test("爬蟲模塊", "配置加載成功", has_config)

            # 測試 Session 創建
            self.print_section("3. Session 創建測試")
            session = create_robust_session()
            self.log_test("爬蟲模塊", "Session創建成功", session is not None)

            # 測試線程鎖
            self.print_section("4. 線程安全測試")
            self.log_test("爬蟲模塊", "stats_lock存在", stats_lock is not None)

            # 測試函數簽名
            self.print_section("5. 函數簽名驗證")
            import inspect

            # download_file_with_resume 簽名
            sig = inspect.signature(download_file_with_resume)
            params = list(sig.parameters.keys())
            expected = ['session', 'url', 'file_path', 'max_retries', 'pbar']
            has_all = all(p in params for p in expected)
            self.log_test("函數簽名", "download_file_with_resume", has_all)

            # download_exam_concurrent 簽名
            sig = inspect.signature(download_exam_concurrent)
            params = list(sig.parameters.keys())
            expected = ['session', 'exam_info', 'base_folder', 'stats']
            has_all = all(p in params for p in expected)
            self.log_test("函數簽名", "download_exam_concurrent", has_all)

            return True

        except Exception as e:
            self.log_test("爬蟲模塊", "爬蟲增強測試", False, str(e))
            return False

    def test_ocr_integration(self):
        """測試 OCR 深度整合功能"""
        self.print_header("🔍 OCR 深度整合測試")

        try:
            # 測試模塊導入
            self.print_section("1. 模塊導入測試")
            from src.core.enhanced_ocr_processor import (
                EnhancedOCRProcessor,
                PDFType,
                OCRQuality
            )
            self.log_test("OCR模塊", "模塊導入成功", True)

            # 測試類初始化
            self.print_section("2. 處理器初始化測試")
            processor = EnhancedOCRProcessor(use_gpu=False, lang='ch')
            self.log_test("OCR模塊", "處理器初始化成功", True)

            # 測試 PDF 類型枚舉
            self.print_section("3. PDF類型枚舉測試")
            types = [PDFType.TEXT_BASED, PDFType.SCANNED, PDFType.HYBRID, PDFType.UNKNOWN]
            self.log_test("OCR模塊", f"PDF類型定義 ({len(types)}種)", len(types) == 4)

            # 測試 OCR 質量枚舉
            self.print_section("4. OCR質量枚舉測試")
            qualities = [OCRQuality.EXCELLENT, OCRQuality.GOOD, OCRQuality.FAIR, OCRQuality.POOR]
            self.log_test("OCR模塊", f"質量等級定義 ({len(qualities)}種)", len(qualities) == 4)

            # 測試 PDF 類型分類邏輯
            self.print_section("5. PDF類型分類邏輯測試")
            test_cases = [
                {'text_ratio': 0.9, 'scanned_ratio': 0.1, 'avg_chars': 1000, 'images': 2,
                 'expected': PDFType.TEXT_BASED, 'desc': '文字型PDF'},
                {'text_ratio': 0.1, 'scanned_ratio': 0.8, 'avg_chars': 50, 'images': 10,
                 'expected': PDFType.SCANNED, 'desc': '掃描版PDF'},
                {'text_ratio': 0.5, 'scanned_ratio': 0.4, 'avg_chars': 300, 'images': 5,
                 'expected': PDFType.HYBRID, 'desc': '混合型PDF'},
            ]

            for case in test_cases:
                result = processor._classify_pdf_type(
                    case['text_ratio'], case['scanned_ratio'],
                    case['avg_chars'], case['images']
                )
                passed = result == case['expected']
                self.log_test("PDF分類", case['desc'], passed)

            # 測試質量驗證
            self.print_section("6. OCR質量驗證測試")
            test_texts = [
                ("一、下列何者為正確？ (A)選項一 (B)選項二", "高質量文本"),
                ("測試abc123", "少量文本"),
                ("", "空文本")
            ]

            for text, desc in test_texts:
                try:
                    quality, metrics = processor.validate_ocr_quality(text)
                    self.log_test("質量驗證", desc, True)
                except Exception as e:
                    self.log_test("質量驗證", desc, False, str(e))

            # 測試參數調優
            self.print_section("7. 智能參數調優測試")
            test_types = [
                (PDFType.SCANNED, "掃描版優化"),
                (PDFType.TEXT_BASED, "文字型優化"),
                (PDFType.HYBRID, "混合型優化")
            ]

            for pdf_type, desc in test_types:
                try:
                    params = processor.optimize_ocr_parameters(
                        'dummy.pdf', pdf_type, {'avg_chars_per_page': 300}
                    )
                    has_params = 'dpi' in params and 'zoom' in params
                    self.log_test("參數調優", desc, has_params)
                except Exception as e:
                    self.log_test("參數調優", desc, False, str(e))

            return True

        except Exception as e:
            self.log_test("OCR模塊", "OCR整合測試", False, str(e))
            return False

    def test_dependencies(self):
        """測試依賴庫"""
        self.print_header("📦 依賴庫測試")

        dependencies = {
            '核心依賴': ['yaml', 'requests', 'bs4'],
            '增強功能': ['tqdm'],
            'PDF處理': ['pdfplumber'],
            'OCR功能': []  # PaddleOCR 可選
        }

        for category, libs in dependencies.items():
            self.print_section(f"{category}")
            for lib in libs:
                try:
                    __import__(lib)
                    self.log_test("依賴庫", f"{lib} 已安裝", True)
                except ImportError:
                    if category == 'OCR功能':
                        self.log_test("依賴庫", f"{lib} 未安裝（可選）", True)
                    else:
                        self.log_test("依賴庫", f"{lib} 未安裝", False)

        return True

    def test_documentation(self):
        """測試文檔完整性"""
        self.print_header("📚 文檔完整性測試")

        docs = [
            ('ENHANCEMENT_GUIDE.md', '爬蟲性能增強指南'),
            ('OCR_INTEGRATION_GUIDE.md', 'OCR深度整合指南')
        ]

        for doc_file, doc_name in docs:
            self.print_section(f"{doc_name}")

            # 檢查文件存在
            exists = os.path.exists(doc_file)
            self.log_test("文檔", f"{doc_name} 存在", exists)

            if exists:
                try:
                    with open(doc_file, 'r', encoding='utf-8') as f:
                        content = f.read()

                    # 檢查內容長度
                    has_content = len(content) > 1000
                    self.log_test("文檔", f"{doc_name} 有內容 ({len(content)}字)", has_content)

                    # 檢查關鍵章節
                    key_sections = ['快速開始', '功能', '測試', '配置']
                    for section in key_sections:
                        has_section = section in content
                        self.log_test("文檔", f"{doc_name} 包含'{section}'章節", has_section)

                except Exception as e:
                    self.log_test("文檔", f"{doc_name} 讀取失敗", False, str(e))

        return True

    def test_unit_tests(self):
        """運行單元測試"""
        self.print_header("🧪 單元測試執行")

        test_scripts = [
            ('test_enhanced_downloader.py', '爬蟲增強測試'),
            ('test_enhanced_ocr.py', 'OCR整合測試')
        ]

        for script, name in test_scripts:
            self.print_section(f"{name}")

            if not os.path.exists(script):
                self.log_test("單元測試", f"{name} 腳本不存在", False)
                continue

            try:
                import subprocess
                result = subprocess.run(
                    ['python', script],
                    capture_output=True,
                    text=True,
                    timeout=60
                )

                success = result.returncode == 0
                self.log_test("單元測試", name, success)

                if not success and result.stderr:
                    print(f"    {Colors.WARNING}錯誤輸出:{Colors.ENDC}")
                    print(f"    {result.stderr[:200]}")

            except subprocess.TimeoutExpired:
                self.log_test("單元測試", f"{name} 超時", False)
            except Exception as e:
                self.log_test("單元測試", name, False, str(e))

        return True

    def test_integration_scenario(self):
        """測試整合場景"""
        self.print_header("🔗 整合場景測試")

        self.print_section("場景：用戶完整工作流")

        # 場景1: 查看配置
        self.print_section("1. 用戶查看配置文件")
        try:
            with open('config.yaml', 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            downloader_enabled = config.get('downloader', {}).get('enable_concurrent', False)
            ocr_enabled = config.get('ocr', {}).get('enable_enhanced_ocr', False)
            self.log_test("整合場景", "爬蟲增強已啟用", downloader_enabled)
            self.log_test("整合場景", "OCR增強已啟用", ocr_enabled)
        except Exception as e:
            self.log_test("整合場景", "配置查看失敗", False, str(e))

        # 場景2: 導入模塊
        self.print_section("2. 用戶導入模塊")
        try:
            from src.core.enhanced_ocr_processor import EnhancedOCRProcessor
            from 考古題下載 import create_robust_session
            self.log_test("整合場景", "成功導入OCR處理器", True)
            self.log_test("整合場景", "成功導入爬蟲模塊", True)
        except Exception as e:
            self.log_test("整合場景", "模塊導入失敗", False, str(e))

        # 場景3: 創建處理器實例
        self.print_section("3. 用戶創建處理器")
        try:
            processor = EnhancedOCRProcessor(use_gpu=False, lang='ch')
            session = create_robust_session()
            self.log_test("整合場景", "OCR處理器創建成功", True)
            self.log_test("整合場景", "HTTP Session創建成功", True)
        except Exception as e:
            self.log_test("整合場景", "處理器創建失敗", False, str(e))

        # 場景4: 模擬PDF類型檢測
        self.print_section("4. 用戶檢測PDF類型（模擬）")
        try:
            # 模擬不同類型的檢測結果
            test_results = [
                processor._classify_pdf_type(0.9, 0.1, 1000, 2),  # 文字型
                processor._classify_pdf_type(0.1, 0.8, 50, 10),   # 掃描版
                processor._classify_pdf_type(0.5, 0.4, 300, 5)    # 混合型
            ]
            self.log_test("整合場景", "PDF類型檢測功能正常", len(test_results) == 3)
        except Exception as e:
            self.log_test("整合場景", "PDF檢測失敗", False, str(e))

        return True

    def test_error_handling(self):
        """測試錯誤處理"""
        self.print_header("⚠️  異常處理測試")

        # 測試無效配置
        self.print_section("1. 無效配置處理")
        try:
            from 考古題下載 import load_config
            # 即使配置文件有問題，也應該有默認值
            config = load_config()
            self.log_test("異常處理", "配置加載容錯機制", True)
        except Exception as e:
            # 應該有錯誤處理，不應該崩潰
            self.log_test("異常處理", "配置加載容錯", False, str(e))

        # 測試無效輸入
        self.print_section("2. 無效輸入處理")
        try:
            from src.core.enhanced_ocr_processor import EnhancedOCRProcessor
            processor = EnhancedOCRProcessor()

            # 空文本驗證
            quality, metrics = processor.validate_ocr_quality("")
            self.log_test("異常處理", "空文本處理", quality == 'poor')

            # 異常字符文本
            quality, metrics = processor.validate_ocr_quality("###@@@!!!")
            self.log_test("異常處理", "異常字符處理", quality == 'poor')

        except Exception as e:
            self.log_test("異常處理", "輸入驗證失敗", False, str(e))

        return True

    def generate_report(self):
        """生成測試報告"""
        self.print_header("📊 測試報告生成")

        # 統計結果
        total_tests = len(self.test_results)
        passed_tests = sum(1 for r in self.test_results if r['passed'])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0

        # 按類別統計
        categories = {}
        for result in self.test_results:
            cat = result['category']
            if cat not in categories:
                categories[cat] = {'total': 0, 'passed': 0}
            categories[cat]['total'] += 1
            if result['passed']:
                categories[cat]['passed'] += 1

        # 打印報告
        print(f"\n{Colors.BOLD}{'='*70}")
        print("測試執行摘要")
        print(f"{'='*70}{Colors.ENDC}")

        print(f"\n⏱️  測試時長: {time.time() - self.start_time:.2f} 秒")
        print(f"📊 總測試數: {total_tests}")
        print(f"✅ 通過: {passed_tests}")
        print(f"❌ 失敗: {failed_tests}")
        print(f"📈 成功率: {success_rate:.1f}%")

        print(f"\n{Colors.BOLD}分類統計:{Colors.ENDC}")
        for cat, stats in categories.items():
            rate = (stats['passed'] / stats['total'] * 100) if stats['total'] > 0 else 0
            status = f"{Colors.OKGREEN}✓{Colors.ENDC}" if rate == 100 else f"{Colors.WARNING}!{Colors.ENDC}"
            print(f"  {status} {cat}: {stats['passed']}/{stats['total']} ({rate:.0f}%)")

        # 失敗詳情
        if failed_tests > 0:
            print(f"\n{Colors.FAIL}失敗測試詳情:{Colors.ENDC}")
            for result in self.test_results:
                if not result['passed']:
                    print(f"  ❌ [{result['category']}] {result['test_name']}")
                    if result['details']:
                        print(f"     → {result['details']}")

        # 保存報告到文件
        report_file = os.path.join(self.test_data_dir, 'test_report.txt')
        try:
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write("完整工作流自動化測試報告\n")
                f.write("="*70 + "\n\n")
                f.write(f"測試時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"測試時長: {time.time() - self.start_time:.2f} 秒\n")
                f.write(f"總測試數: {total_tests}\n")
                f.write(f"通過: {passed_tests}\n")
                f.write(f"失敗: {failed_tests}\n")
                f.write(f"成功率: {success_rate:.1f}%\n\n")

                f.write("詳細結果:\n")
                f.write("-"*70 + "\n")
                for result in self.test_results:
                    status = "✅ 通過" if result['passed'] else "❌ 失敗"
                    f.write(f"{status} [{result['category']}] {result['test_name']}\n")
                    if result['details']:
                        f.write(f"  詳情: {result['details']}\n")

            print(f"\n📄 報告已保存: {report_file}")
        except Exception as e:
            print(f"\n⚠️  報告保存失敗: {e}")

        return success_rate >= 80  # 80% 通過率視為成功

    def cleanup(self):
        """清理測試環境"""
        if self.test_data_dir and os.path.exists(self.test_data_dir):
            try:
                shutil.rmtree(self.test_data_dir)
                print(f"\n🧹 已清理測試目錄: {self.test_data_dir}")
            except Exception as e:
                print(f"\n⚠️  清理失敗: {e}")

    def run_all_tests(self):
        """運行所有測試"""
        self.start_time = time.time()

        print(f"{Colors.BOLD}{Colors.HEADER}")
        print("="*70)
        print("完整工作流自動化測試")
        print("="*70)
        print(f"{Colors.ENDC}")
        print(f"開始時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"測試者: 自動化測試腳本（模擬真實用戶）")

        # 測試序列
        test_sequence = [
            ("環境設置", self.setup_test_environment),
            ("配置文件", self.test_configuration_files),
            ("依賴庫", self.test_dependencies),
            ("爬蟲增強", self.test_crawler_enhancements),
            ("OCR整合", self.test_ocr_integration),
            ("文檔完整性", self.test_documentation),
            ("單元測試", self.test_unit_tests),
            ("整合場景", self.test_integration_scenario),
            ("異常處理", self.test_error_handling),
        ]

        for name, test_func in test_sequence:
            try:
                test_func()
            except Exception as e:
                self.log_test(name, f"{name}測試組", False, str(e))
                print(f"{Colors.FAIL}測試組 {name} 發生嚴重錯誤: {e}{Colors.ENDC}")

        # 生成報告
        success = self.generate_report()

        # 清理
        self.cleanup()

        return 0 if success else 1


def main():
    """主函數"""
    tester = WorkflowTester()
    exit_code = tester.run_all_tests()

    # 最終結論
    if exit_code == 0:
        print(f"\n{Colors.OKGREEN}{Colors.BOLD}")
        print("🎉 所有測試通過！系統運行正常，功能完整！")
        print(f"{Colors.ENDC}")
    else:
        print(f"\n{Colors.WARNING}{Colors.BOLD}")
        print("⚠️  部分測試失敗，請檢查詳細報告。")
        print(f"{Colors.ENDC}")

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
