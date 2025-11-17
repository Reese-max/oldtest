#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
整合工作流測試腳本
完整測試從爬蟲到PDF解析到Google表單生成的整個流程
"""

import os
import sys
import json
import time
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Tuple

# 添加src目錄到路徑
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.api import ArchaeologyAPI
from src.utils.logger import logger


class IntegratedWorkflowTest:
    """整合工作流測試"""

    def __init__(self):
        self.test_results = []
        self.api = ArchaeologyAPI()
        self.test_output_dir = "test_workflow_output"
        self.start_time = None
        self.end_time = None

    def log_test(self, test_name: str, passed: bool, message: str = "", details: Dict = None):
        """記錄測試結果"""
        result = {
            'test_name': test_name,
            'passed': passed,
            'message': message,
            'details': details or {},
            'timestamp': datetime.now().isoformat()
        }
        self.test_results.append(result)

        status = "✅ 通過" if passed else "❌ 失敗"
        print(f"\n{status} - {test_name}")
        if message:
            print(f"   {message}")
        if details:
            for key, value in details.items():
                print(f"   • {key}: {value}")

    def test_environment(self) -> bool:
        """測試環境檢查"""
        print("\n" + "="*70)
        print("📋 階段 1: 環境檢查")
        print("="*70)

        all_passed = True

        # 測試 1: Python版本
        python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        passed = sys.version_info >= (3, 7)
        self.log_test(
            "Python版本檢查",
            passed,
            f"Python {python_version}",
            {"要求": "Python >= 3.7"}
        )
        all_passed &= passed

        # 測試 2: 必要模組
        required_modules = {
            'pdfplumber': 'pdfplumber',
            'pandas': 'pandas',
            'requests': 'requests',
            'beautifulsoup4': 'bs4'  # 包名是beautifulsoup4，但導入時用bs4
        }

        for display_name, import_name in required_modules.items():
            try:
                __import__(import_name)
                self.log_test(f"模組檢查: {display_name}", True, "已安裝")
            except ImportError:
                self.log_test(f"模組檢查: {display_name}", False, "未安裝")
                all_passed = False

        # 測試 3: 專案結構
        required_dirs = ['src', 'src/core', 'src/processors', 'src/utils']
        for dir_path in required_dirs:
            exists = os.path.isdir(dir_path)
            self.log_test(
                f"目錄檢查: {dir_path}",
                exists,
                "存在" if exists else "不存在"
            )
            all_passed &= exists

        # 測試 4: 核心文件
        core_files = [
            'main.py',
            '考古題下載.py',
            'src/api.py',
            'src/core/google_script_generator.py',
            'src/core/question_parser.py'
        ]

        for file_path in core_files:
            exists = os.path.isfile(file_path)
            self.log_test(
                f"文件檢查: {file_path}",
                exists,
                "存在" if exists else "不存在"
            )
            all_passed &= exists

        return all_passed

    def test_crawler_integrity(self) -> bool:
        """測試爬蟲完整性"""
        print("\n" + "="*70)
        print("🕷️ 階段 2: 爬蟲完整性測試")
        print("="*70)

        all_passed = True

        # 測試 1: 爬蟲檔案存在且可讀取
        crawler_path = "考古題下載.py"
        try:
            with open(crawler_path, 'r', encoding='utf-8') as f:
                content = f.read()

            self.log_test(
                "爬蟲檔案讀取",
                True,
                f"成功讀取 {len(content)} 字元",
                {"檔案大小": f"{len(content) / 1024:.2f} KB"}
            )
        except Exception as e:
            self.log_test("爬蟲檔案讀取", False, str(e))
            return False

        # 測試 2: 重試邏輯驗證
        retry_blocks = content.count('continue  # 繼續下一次重試')
        expected_retry_blocks = 3
        passed = retry_blocks == expected_retry_blocks

        self.log_test(
            "重試邏輯驗證",
            passed,
            f"找到 {retry_blocks} 個重試區塊",
            {"預期": expected_retry_blocks, "實際": retry_blocks}
        )
        all_passed &= passed

        # 測試 3: 異常處理驗證
        has_bare_except = 'except:' in content and 'except (ImportError, OSError, AttributeError):' not in content
        passed = not has_bare_except

        self.log_test(
            "異常處理品質",
            passed,
            "使用明確異常類型" if passed else "發現裸露except語句"
        )
        all_passed &= passed

        # 測試 4: 檢查已下載的PDF數量
        pdf_dir = "考選部考古題完整庫"
        if os.path.isdir(pdf_dir):
            pdf_count = sum(1 for root, dirs, files in os.walk(pdf_dir)
                          for f in files if f.endswith('.pdf'))

            self.log_test(
                "已下載PDF統計",
                pdf_count > 0,
                f"找到 {pdf_count} 個PDF檔案",
                {"目錄": pdf_dir}
            )
        else:
            self.log_test(
                "已下載PDF統計",
                False,
                "PDF目錄不存在"
            )
            all_passed = False

        return all_passed

    def test_pdf_parsing(self) -> Tuple[bool, Dict[str, Any]]:
        """測試PDF解析流程"""
        print("\n" + "="*70)
        print("📄 階段 3: PDF解析流程測試")
        print("="*70)

        all_passed = True
        parsing_results = {}

        # 尋找測試PDF（選擇有完整答案的）
        test_pdf_base = "考選部考古題完整庫/民國114年/民國114年_警察特考/外事警察/警察情境實務(包括警察法規、實務操作標準作業程序、人權保障與正當法律程序)"

        test_pdf = f"{test_pdf_base}/試題.pdf"
        answer_pdf = f"{test_pdf_base}/答案.pdf"
        corrected_pdf = f"{test_pdf_base}/更正答案.pdf"

        # 檢查檔案是否存在
        files_exist = all([
            os.path.isfile(test_pdf),
            os.path.isfile(answer_pdf),
            os.path.isfile(corrected_pdf)
        ])

        if not files_exist:
            # 如果上面的不存在，嘗試找其他測試文件
            print("⚠️ 默認測試文件不存在，搜尋其他測試文件...")

            # 尋找任何有試題.pdf的目錄
            for root, dirs, files in os.walk("考選部考古題完整庫"):
                if "試題.pdf" in files:
                    test_pdf = os.path.join(root, "試題.pdf")
                    answer_pdf = os.path.join(root, "答案.pdf")
                    corrected_pdf = os.path.join(root, "更正答案.pdf")

                    if os.path.isfile(answer_pdf):
                        print(f"✓ 找到測試文件: {test_pdf}")
                        files_exist = True
                        break

        if not files_exist:
            self.log_test(
                "測試PDF文件檢查",
                False,
                "找不到合適的測試PDF文件"
            )
            return False, {}

        self.log_test(
            "測試PDF文件檢查",
            True,
            "找到測試PDF文件",
            {
                "試題": os.path.basename(test_pdf),
                "路徑": os.path.dirname(test_pdf)
            }
        )

        # 創建測試輸出目錄
        os.makedirs(self.test_output_dir, exist_ok=True)

        # 測試 1: 單一PDF處理（包含答案）
        print("\n🔍 測試單一PDF處理...")
        try:
            result = self.api.process_single_pdf(
                pdf_path=test_pdf,
                answer_pdf_path=answer_pdf if os.path.isfile(answer_pdf) else None,
                corrected_answer_pdf_path=corrected_pdf if os.path.isfile(corrected_pdf) else None,
                output_dir=self.test_output_dir,
                generate_script=True
            )

            parsing_results['single_pdf'] = result

            passed = result.get('success', False)
            self.log_test(
                "單一PDF處理",
                passed,
                result.get('message', ''),
                {
                    "題目數量": result.get('questions_count', 0),
                    "格式類型": result.get('format_type', 'N/A')
                }
            )
            all_passed &= passed

            # 測試 2: CSV檔案生成驗證
            csv_files = result.get('csv_files', [])
            csv_exists = len(csv_files) > 0 and all(os.path.isfile(f) for f in csv_files)

            self.log_test(
                "CSV檔案生成",
                csv_exists,
                f"生成 {len(csv_files)} 個CSV檔案",
                {"檔案列表": [os.path.basename(f) for f in csv_files]}
            )
            all_passed &= csv_exists

            # 測試 3: Google Script生成驗證
            script_file = result.get('script_file', '')
            script_exists = script_file and os.path.isfile(script_file)

            if script_exists:
                with open(script_file, 'r', encoding='utf-8') as f:
                    script_content = f.read()

                # 檢查關鍵功能
                has_quiz_mode = 'setIsQuiz(true)' in script_content
                has_answer_marking = 'setPoints(' in script_content
                has_correct_answer = 'setCorrectAnswer' in script_content or 'markAsCorrect' in script_content

                self.log_test(
                    "Google Script生成",
                    script_exists,
                    f"生成 {len(script_content)} 字元的Script",
                    {
                        "檔案": os.path.basename(script_file),
                        "Quiz模式": "✅" if has_quiz_mode else "❌",
                        "評分功能": "✅" if has_answer_marking else "❌",
                        "答案標記": "✅" if has_correct_answer else "❌"
                    }
                )

                parsing_results['script_analysis'] = {
                    'has_quiz_mode': has_quiz_mode,
                    'has_answer_marking': has_answer_marking,
                    'has_correct_answer': has_correct_answer
                }
            else:
                self.log_test(
                    "Google Script生成",
                    False,
                    "Script檔案未生成"
                )
                all_passed = False

            # 測試 4: 資料品質驗證
            if csv_exists and csv_files:
                import pandas as pd

                # 讀取Google表單CSV
                google_csv = [f for f in csv_files if 'Google' in f or '表單' in f]
                if google_csv:
                    df = pd.read_csv(google_csv[0], encoding='utf-8-sig')

                    # 檢查必要欄位
                    required_columns = ['題號', '題目', '題型']
                    has_required = all(col in df.columns for col in required_columns)

                    # 檢查資料完整性
                    empty_questions = df['題目'].isna().sum()
                    total_questions = len(df)

                    data_quality = empty_questions == 0 and total_questions > 0

                    self.log_test(
                        "資料品質驗證",
                        data_quality and has_required,
                        f"{total_questions} 題資料",
                        {
                            "必要欄位": "✅" if has_required else "❌",
                            "空題目數": empty_questions,
                            "資料完整": "✅" if data_quality else "❌"
                        }
                    )

                    parsing_results['data_quality'] = {
                        'total_questions': total_questions,
                        'empty_questions': empty_questions,
                        'has_required_columns': has_required
                    }

        except Exception as e:
            self.log_test(
                "PDF解析流程",
                False,
                f"發生異常: {str(e)}"
            )
            all_passed = False
            import traceback
            traceback.print_exc()

        return all_passed, parsing_results

    def test_core_functions(self) -> bool:
        """測試核心功能"""
        print("\n" + "="*70)
        print("⚙️ 階段 4: 核心功能測試")
        print("="*70)

        all_passed = True

        # 測試 1: 解析器初始化
        try:
            from src.core.question_parser import QuestionParser
            from src.core.ultimate_question_parser import UltimateQuestionParser
            from src.core.mixed_format_parser import MixedFormatParser
            from src.core.google_script_generator import GoogleScriptGenerator

            parsers = [
                QuestionParser(),
                UltimateQuestionParser(),
                MixedFormatParser(),
                GoogleScriptGenerator()
            ]

            self.log_test(
                "解析器初始化",
                True,
                f"成功初始化 {len(parsers)} 個解析器",
                {"解析器": [p.__class__.__name__ for p in parsers]}
            )
        except Exception as e:
            self.log_test(
                "解析器初始化",
                False,
                f"初始化失敗: {str(e)}"
            )
            all_passed = False

        # 測試 2: Unicode符號驗證
        try:
            from src.utils.regex_patterns import EMBEDDED_SYMBOLS

            expected_symbols = ['\ue18c', '\ue18d', '\ue18e', '\ue18f']
            symbols_correct = EMBEDDED_SYMBOLS == expected_symbols

            self.log_test(
                "Unicode符號驗證",
                symbols_correct,
                f"符號數量: {len(EMBEDDED_SYMBOLS)}",
                {"符號正確": "✅" if symbols_correct else "❌"}
            )
            all_passed &= symbols_correct
        except Exception as e:
            self.log_test(
                "Unicode符號驗證",
                False,
                f"驗證失敗: {str(e)}"
            )
            all_passed = False

        # 測試 3: 配置檔案
        config_file = "config.json"
        if os.path.isfile(config_file):
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)

                has_google_form = 'google_form' in config
                has_ocr = 'ocr' in config

                self.log_test(
                    "配置檔案驗證",
                    True,
                    "配置檔案有效",
                    {
                        "Google表單配置": "✅" if has_google_form else "❌",
                        "OCR配置": "✅" if has_ocr else "❌"
                    }
                )
            except Exception as e:
                self.log_test(
                    "配置檔案驗證",
                    False,
                    f"配置檔案無效: {str(e)}"
                )
                all_passed = False
        else:
            self.log_test(
                "配置檔案驗證",
                False,
                "配置檔案不存在"
            )
            # 不設為失敗，因為系統可能使用默認配置

        return all_passed

    def generate_report(self, parsing_results: Dict[str, Any]) -> str:
        """生成測試報告"""
        print("\n" + "="*70)
        print("📊 生成測試報告")
        print("="*70)

        # 統計
        total_tests = len(self.test_results)
        passed_tests = sum(1 for r in self.test_results if r['passed'])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0

        # 生成報告
        report_lines = [
            "# 整合工作流測試報告",
            "",
            f"生成時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"測試時長: {(self.end_time - self.start_time).total_seconds():.2f} 秒",
            "",
            "---",
            "",
            "## 📊 測試摘要",
            "",
            f"| 指標 | 數值 |",
            f"|------|------|",
            f"| 總測試數 | {total_tests} |",
            f"| ✅ 通過 | {passed_tests} |",
            f"| ❌ 失敗 | {failed_tests} |",
            f"| **成功率** | **{success_rate:.1f}%** |",
            "",
            "---",
            "",
            "## 📋 詳細測試結果",
            ""
        ]

        # 按階段分組
        stages = {
            "環境檢查": [],
            "爬蟲完整性測試": [],
            "PDF解析流程測試": [],
            "核心功能測試": []
        }

        for result in self.test_results:
            test_name = result['test_name']

            # 分配到對應階段
            if any(keyword in test_name for keyword in ['Python', '模組', '目錄', '文件檢查']):
                stage = "環境檢查"
            elif any(keyword in test_name for keyword in ['爬蟲', '重試', '異常處理', 'PDF統計']):
                stage = "爬蟲完整性測試"
            elif any(keyword in test_name for keyword in ['PDF', 'CSV', 'Script', '資料品質']):
                stage = "PDF解析流程測試"
            else:
                stage = "核心功能測試"

            stages[stage].append(result)

        # 輸出各階段結果
        for stage_name, results in stages.items():
            if not results:
                continue

            report_lines.extend([
                f"### {stage_name}",
                "",
                "| 測試項目 | 狀態 | 說明 |",
                "|---------|------|------|"
            ])

            for result in results:
                status = "✅" if result['passed'] else "❌"
                message = result['message'] or "-"
                report_lines.append(f"| {result['test_name']} | {status} | {message} |")

            report_lines.append("")

        # 添加解析結果詳情
        if parsing_results:
            report_lines.extend([
                "---",
                "",
                "## 🔍 PDF解析詳細結果",
                ""
            ])

            if 'single_pdf' in parsing_results:
                result = parsing_results['single_pdf']
                report_lines.extend([
                    "### 解析統計",
                    "",
                    f"- 成功: {'✅' if result.get('success') else '❌'}",
                    f"- 題目數量: {result.get('questions_count', 0)}",
                    f"- 格式類型: {result.get('format_type', 'N/A')}",
                    f"- CSV檔案數: {len(result.get('csv_files', []))}",
                    ""
                ])

            if 'script_analysis' in parsing_results:
                analysis = parsing_results['script_analysis']
                report_lines.extend([
                    "### Google Script功能分析",
                    "",
                    f"- Quiz模式: {'✅ 啟用' if analysis.get('has_quiz_mode') else '❌ 未啟用'}",
                    f"- 評分功能: {'✅ 包含' if analysis.get('has_answer_marking') else '❌ 缺少'}",
                    f"- 答案標記: {'✅ 包含' if analysis.get('has_correct_answer') else '❌ 缺少'}",
                    ""
                ])

            if 'data_quality' in parsing_results:
                quality = parsing_results['data_quality']
                report_lines.extend([
                    "### 資料品質分析",
                    "",
                    f"- 總題數: {quality.get('total_questions', 0)}",
                    f"- 空題目: {quality.get('empty_questions', 0)}",
                    f"- 必要欄位: {'✅ 完整' if quality.get('has_required_columns') else '❌ 缺少'}",
                    ""
                ])

        # 添加建議
        report_lines.extend([
            "---",
            "",
            "## 💡 測試結論與建議",
            ""
        ])

        if success_rate >= 90:
            report_lines.extend([
                "### ✅ 整體狀態: 優秀",
                "",
                "系統運作正常，所有核心功能通過測試。",
                "",
                "**建議**:",
                "- ✅ 可直接用於生產環境",
                "- 📊 建議定期監控系統效能",
                "- 🔄 持續進行回歸測試",
                ""
            ])
        elif success_rate >= 70:
            report_lines.extend([
                "### ⚠️ 整體狀態: 良好",
                "",
                "系統基本功能正常，但存在一些問題需要關注。",
                "",
                "**建議**:",
                "- 🔍 檢查失敗的測試項目",
                "- 🔧 修正發現的問題",
                "- ✅ 重新運行測試驗證修正",
                ""
            ])
        else:
            report_lines.extend([
                "### ❌ 整體狀態: 需要改進",
                "",
                "系統存在較多問題，需要立即處理。",
                "",
                "**建議**:",
                "- 🚨 優先修正關鍵失敗項目",
                "- 📋 檢查環境配置",
                "- 🔧 逐項修正並驗證",
                ""
            ])

        # 失敗項目列表
        failed_results = [r for r in self.test_results if not r['passed']]
        if failed_results:
            report_lines.extend([
                "### ❌ 失敗項目詳情",
                ""
            ])

            for i, result in enumerate(failed_results, 1):
                report_lines.extend([
                    f"**{i}. {result['test_name']}**",
                    f"- 錯誤: {result['message']}",
                    f"- 時間: {result['timestamp']}",
                    ""
                ])

        # 附錄
        report_lines.extend([
            "---",
            "",
            "## 📎 附錄",
            "",
            "### 測試環境",
            "",
            f"- Python版本: {sys.version}",
            f"- 作業系統: {os.name}",
            f"- 工作目錄: {os.getcwd()}",
            "",
            "### 生成的檔案",
            ""
        ])

        # 列出測試輸出目錄的檔案
        if os.path.isdir(self.test_output_dir):
            output_files = []
            for root, dirs, files in os.walk(self.test_output_dir):
                for f in files:
                    rel_path = os.path.relpath(os.path.join(root, f), self.test_output_dir)
                    output_files.append(rel_path)

            if output_files:
                for f in output_files:
                    report_lines.append(f"- `{f}`")
            else:
                report_lines.append("- (無)")
        else:
            report_lines.append("- (測試輸出目錄不存在)")

        report_lines.extend([
            "",
            "---",
            "",
            f"報告生成完成時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            ""
        ])

        report_content = "\n".join(report_lines)

        # 儲存報告
        report_file = "INTEGRATED_WORKFLOW_TEST_REPORT.md"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report_content)

        print(f"\n✅ 測試報告已生成: {report_file}")

        return report_file

    def run_all_tests(self):
        """運行所有測試"""
        self.start_time = datetime.now()

        print("╔" + "="*68 + "╗")
        print("║" + " "*68 + "║")
        print("║" + "整合工作流測試".center(68) + "║")
        print("║" + f"開始時間: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}".center(68) + "║")
        print("║" + " "*68 + "║")
        print("╚" + "="*68 + "╝")

        # 運行各階段測試
        env_passed = self.test_environment()
        crawler_passed = self.test_crawler_integrity()
        parsing_passed, parsing_results = self.test_pdf_parsing()
        core_passed = self.test_core_functions()

        self.end_time = datetime.now()

        # 生成報告
        report_file = self.generate_report(parsing_results)

        # 輸出總結
        print("\n" + "="*70)
        print("🎯 測試總結")
        print("="*70)

        total_tests = len(self.test_results)
        passed_tests = sum(1 for r in self.test_results if r['passed'])
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0

        print(f"\n總測試數: {total_tests}")
        print(f"✅ 通過: {passed_tests}")
        print(f"❌ 失敗: {total_tests - passed_tests}")
        print(f"📊 成功率: {success_rate:.1f}%")
        print(f"⏱️ 測試時長: {(self.end_time - self.start_time).total_seconds():.2f} 秒")
        print(f"\n📄 詳細報告: {report_file}")

        # 返回總體結果
        return success_rate >= 90


def main():
    """主函數"""
    test = IntegratedWorkflowTest()
    success = test.run_all_tests()

    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
