#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
性能測試套件
測試各個核心模組的執行效率和性能指標
"""

import time
import os
import sys
import tempfile
from typing import Dict, List, Callable, Any
import logging

# 設定路徑
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.utils.logger import setup_logger
from src.utils.config import ConfigManager
from src.core.csv_generator import CSVGenerator
from src.core.google_script_generator import GoogleScriptGenerator

# 設定日誌
logger = setup_logger('performance_test', logging.INFO)


class PerformanceTest:
    """性能測試基礎類"""

    def __init__(self):
        self.results = []
        self.config = ConfigManager()

    def measure_time(self, func: Callable, *args, **kwargs) -> Dict[str, Any]:
        """測量函數執行時間"""
        start_time = time.time()
        start_memory = self._get_memory_usage()

        try:
            result = func(*args, **kwargs)
            success = True
            error = None
        except Exception as e:
            result = None
            success = False
            error = str(e)

        end_time = time.time()
        end_memory = self._get_memory_usage()

        execution_time = end_time - start_time
        memory_delta = end_memory - start_memory

        return {
            'success': success,
            'execution_time': execution_time,
            'memory_delta': memory_delta,
            'result': result,
            'error': error
        }

    def _get_memory_usage(self) -> float:
        """獲取當前記憶體使用量（MB）"""
        try:
            import psutil
            process = psutil.Process(os.getpid())
            return process.memory_info().rss / 1024 / 1024  # MB
        except ImportError:
            return 0.0

    def run_test(self, test_name: str, func: Callable, *args, **kwargs):
        """運行單個測試"""
        logger.info(f"\n▶ 測試: {test_name}")

        result = self.measure_time(func, *args, **kwargs)

        self.results.append({
            'name': test_name,
            **result
        })

        if result['success']:
            logger.info(f"✅ {test_name} - 執行時間: {result['execution_time']:.4f}秒")
            if result['memory_delta'] > 0:
                logger.info(f"   記憶體增加: {result['memory_delta']:.2f}MB")
        else:
            logger.error(f"❌ {test_name} - 失敗: {result['error']}")

    def print_summary(self):
        """打印測試摘要"""
        logger.info("\n" + "="*70)
        logger.info("📊 性能測試結果摘要")
        logger.info("="*70 + "\n")

        successful_tests = [r for r in self.results if r['success']]
        failed_tests = [r for r in self.results if not r['success']]

        for result in self.results:
            status = "✅ PASS" if result['success'] else "❌ FAIL"
            logger.info(f"{status} {result['name']}")
            if result['success']:
                logger.info(f"   執行時間: {result['execution_time']:.4f}秒")
                if result['memory_delta'] > 0:
                    logger.info(f"   記憶體: +{result['memory_delta']:.2f}MB")
            else:
                logger.info(f"   錯誤: {result['error']}")

        logger.info("\n" + "-"*70)
        logger.info(f"總測試數: {len(self.results)}")
        logger.info(f"✅ 通過: {len(successful_tests)}")
        logger.info(f"❌ 失敗: {len(failed_tests)}")

        if successful_tests:
            total_time = sum(r['execution_time'] for r in successful_tests)
            avg_time = total_time / len(successful_tests)
            logger.info(f"總執行時間: {total_time:.4f}秒")
            logger.info(f"平均執行時間: {avg_time:.4f}秒")

        logger.info("-"*70)

        return len(failed_tests) == 0


class CSVGeneratorPerformanceTest(PerformanceTest):
    """CSV 生成器性能測試"""

    def test_small_dataset(self):
        """測試小數據集（10題）"""
        questions = self._generate_questions(10)
        answers = self._generate_answers(10)

        def generate_csv():
            csv_gen = CSVGenerator(self.config)
            # 使用安全的臨時文件創建方法
            with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as tmp:
                temp_path = tmp.name
            result = csv_gen.generate_questions_csv(questions, answers, temp_path)
            if os.path.exists(temp_path):
                os.remove(temp_path)
            return result

        self.run_test("CSV生成 - 10題", generate_csv)

    def test_medium_dataset(self):
        """測試中等數據集（100題）"""
        questions = self._generate_questions(100)
        answers = self._generate_answers(100)

        def generate_csv():
            csv_gen = CSVGenerator(self.config)
            # 使用安全的臨時文件創建方法
            with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as tmp:
                temp_path = tmp.name
            result = csv_gen.generate_questions_csv(questions, answers, temp_path)
            if os.path.exists(temp_path):
                os.remove(temp_path)
            return result

        self.run_test("CSV生成 - 100題", generate_csv)

    def test_large_dataset(self):
        """測試大數據集（500題）"""
        questions = self._generate_questions(500)
        answers = self._generate_answers(500)

        def generate_csv():
            csv_gen = CSVGenerator(self.config)
            # 使用安全的臨時文件創建方法
            with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as tmp:
                temp_path = tmp.name
            result = csv_gen.generate_questions_csv(questions, answers, temp_path)
            if os.path.exists(temp_path):
                os.remove(temp_path)
            return result

        self.run_test("CSV生成 - 500題", generate_csv)

    def _generate_questions(self, count: int) -> List[Dict]:
        """生成測試題目"""
        questions = []
        for i in range(1, count + 1):
            questions.append({
                '題號': str(i),
                '題目': f'測試題目{i}' * 10,  # 較長的題目
                '題型': '選擇題',
                '選項A': f'選項A_{i}',
                '選項B': f'選項B_{i}',
                '選項C': f'選項C_{i}',
                '選項D': f'選項D_{i}',
                '題組': False
            })
        return questions

    def _generate_answers(self, count: int) -> Dict[str, str]:
        """生成測試答案"""
        options = ['A', 'B', 'C', 'D']
        return {str(i): options[i % 4] for i in range(1, count + 1)}


class GoogleScriptPerformanceTest(PerformanceTest):
    """Google Script 生成器性能測試"""

    def test_small_script(self):
        """測試小腳本生成（10題）"""
        questions = self._generate_questions(10)
        answers = self._generate_answers(10)

        def generate_script():
            script_gen = GoogleScriptGenerator(self.config)
            # 使用安全的臨時文件創建方法
            with tempfile.NamedTemporaryFile(mode='w', suffix='.gs', delete=False) as tmp:
                temp_path = tmp.name
            result = script_gen.generate_google_script(questions, answers, temp_path)
            if os.path.exists(temp_path):
                os.remove(temp_path)
            return result

        self.run_test("Google Script - 10題", generate_script)

    def test_medium_script(self):
        """測試中等腳本生成（100題）"""
        questions = self._generate_questions(100)
        answers = self._generate_answers(100)

        def generate_script():
            script_gen = GoogleScriptGenerator(self.config)
            # 使用安全的臨時文件創建方法
            with tempfile.NamedTemporaryFile(mode='w', suffix='.gs', delete=False) as tmp:
                temp_path = tmp.name
            result = script_gen.generate_google_script(questions, answers, temp_path)
            if os.path.exists(temp_path):
                os.remove(temp_path)
            return result

        self.run_test("Google Script - 100題", generate_script)

    def test_large_script(self):
        """測試大腳本生成（500題）"""
        questions = self._generate_questions(500)
        answers = self._generate_answers(500)

        def generate_script():
            script_gen = GoogleScriptGenerator(self.config)
            # 使用安全的臨時文件創建方法
            with tempfile.NamedTemporaryFile(mode='w', suffix='.gs', delete=False) as tmp:
                temp_path = tmp.name
            result = script_gen.generate_google_script(questions, answers, temp_path)
            if os.path.exists(temp_path):
                os.remove(temp_path)
            return result

        self.run_test("Google Script - 500題", generate_script)

    def _generate_questions(self, count: int) -> List[Dict]:
        """生成測試題目"""
        questions = []
        for i in range(1, count + 1):
            questions.append({
                '題號': str(i),
                '題目': f'測試題目{i}' * 10,
                '題型': '選擇題',
                '選項A': f'選項A_{i}',
                '選項B': f'選項B_{i}',
                '選項C': f'選項C_{i}',
                '選項D': f'選項D_{i}',
                '題組': False
            })
        return questions

    def _generate_answers(self, count: int) -> Dict[str, str]:
        """生成測試答案"""
        options = ['A', 'B', 'C', 'D']
        return {str(i): options[i % 4] for i in range(1, count + 1)}


class ConfigPerformanceTest(PerformanceTest):
    """配置管理器性能測試"""

    def test_config_load(self):
        """測試配置載入速度"""
        def load_config():
            return ConfigManager()

        self.run_test("配置載入", load_config)

    def test_multiple_loads(self):
        """測試多次配置載入"""
        def load_multiple():
            configs = []
            for _ in range(100):
                configs.append(ConfigManager())
            return configs

        self.run_test("配置載入 x100", load_multiple)


class StringProcessingPerformanceTest(PerformanceTest):
    """字符串處理性能測試"""

    def test_regex_performance(self):
        """測試正則表達式性能"""
        import re

        def test_regex():
            # 模擬題目解析中的正則表達式操作
            text = "1. 題目內容\n(A) 選項A\n(B) 選項B\n" * 1000

            # 題號匹配
            pattern1 = re.compile(r'^\d+\.')
            matches1 = pattern1.findall(text)

            # 選項匹配
            pattern2 = re.compile(r'\([A-D]\)')
            matches2 = pattern2.findall(text)

            return len(matches1) + len(matches2)

        self.run_test("正則表達式處理", test_regex)

    def test_string_operations(self):
        """測試字符串操作性能"""
        def test_strings():
            # 模擬大量字符串操作
            result = []
            for i in range(10000):
                text = f"題目{i}"
                text = text.strip()
                text = text.replace('\n', ' ')
                text = text.upper()
                result.append(text)
            return len(result)

        self.run_test("字符串操作 x10000", test_strings)


def main():
    """主測試函數"""
    logger.info("\n" + "="*70)
    logger.info("🔥 開始性能測試")
    logger.info("="*70)

    all_success = True

    # CSV 生成器性能測試
    logger.info("\n【CSV 生成器性能測試】")
    csv_test = CSVGeneratorPerformanceTest()
    csv_test.test_small_dataset()
    csv_test.test_medium_dataset()
    csv_test.test_large_dataset()
    all_success = csv_test.print_summary() and all_success

    # Google Script 生成器性能測試
    logger.info("\n【Google Script 生成器性能測試】")
    script_test = GoogleScriptPerformanceTest()
    script_test.test_small_script()
    script_test.test_medium_script()
    script_test.test_large_script()
    all_success = script_test.print_summary() and all_success

    # 配置管理器性能測試
    logger.info("\n【配置管理器性能測試】")
    config_test = ConfigPerformanceTest()
    config_test.test_config_load()
    config_test.test_multiple_loads()
    all_success = config_test.print_summary() and all_success

    # 字符串處理性能測試
    logger.info("\n【字符串處理性能測試】")
    string_test = StringProcessingPerformanceTest()
    string_test.test_regex_performance()
    string_test.test_string_operations()
    all_success = string_test.print_summary() and all_success

    # 總結
    logger.info("\n" + "="*70)
    logger.info("📊 性能測試總結")
    logger.info("="*70)

    all_tests = (
        csv_test.results +
        script_test.results +
        config_test.results +
        string_test.results
    )

    successful = [r for r in all_tests if r['success']]
    failed = [r for r in all_tests if not r['success']]

    logger.info(f"總測試數: {len(all_tests)}")
    logger.info(f"✅ 通過: {len(successful)}")
    logger.info(f"❌ 失敗: {len(failed)}")

    if successful:
        total_time = sum(r['execution_time'] for r in successful)
        logger.info(f"總執行時間: {total_time:.4f}秒")

    if all_success:
        logger.info("\n✅ 🎉 所有性能測試通過！")
        return 0
    else:
        logger.error("\n❌ ⚠️  部分性能測試失敗")
        return 1


if __name__ == '__main__':
    sys.exit(main())
