#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
負載測試套件
測試系統在高負載、大數據量下的穩定性和性能
"""

import time
import os
import sys
import tempfile
import threading
import concurrent.futures
from typing import Dict, List, Any
import logging

# 設定路徑
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.utils.logger import setup_logger
from src.utils.config import ConfigManager
from src.core.csv_generator import CSVGenerator
from src.core.google_script_generator import GoogleScriptGenerator

# 設定日誌
logger = setup_logger('load_test', logging.INFO)


class LoadTest:
    """負載測試基礎類"""

    def __init__(self):
        self.results = []
        self.config = ConfigManager()
        self.errors = []

    def run_concurrent_test(self, test_name: str, func, num_threads: int):
        """運行並發測試"""
        logger.info(f"\n▶ 測試: {test_name} (並發數: {num_threads})")

        start_time = time.time()
        errors = []
        results = []

        with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = [executor.submit(func, i) for i in range(num_threads)]

            for future in concurrent.futures.as_completed(futures):
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    errors.append(str(e))

        end_time = time.time()
        execution_time = end_time - start_time

        success_rate = len(results) / num_threads * 100
        throughput = num_threads / execution_time if execution_time > 0 else 0

        test_result = {
            'name': test_name,
            'num_threads': num_threads,
            'successful': len(results),
            'failed': len(errors),
            'success_rate': success_rate,
            'execution_time': execution_time,
            'throughput': throughput,
            'errors': errors
        }

        self.results.append(test_result)

        if success_rate == 100:
            logger.info(f"✅ {test_name} - 成功率: {success_rate:.1f}%")
        else:
            logger.warning(f"⚠️  {test_name} - 成功率: {success_rate:.1f}%")

        logger.info(f"   執行時間: {execution_time:.4f}秒")
        logger.info(f"   吞吐量: {throughput:.2f} 操作/秒")

        if errors:
            logger.warning(f"   錯誤數: {len(errors)}")

    def run_stress_test(self, test_name: str, func, duration_seconds: int):
        """運行壓力測試（持續時間）"""
        logger.info(f"\n▶ 測試: {test_name} (持續時間: {duration_seconds}秒)")

        start_time = time.time()
        iterations = 0
        errors = []

        while time.time() - start_time < duration_seconds:
            try:
                func(iterations)
                iterations += 1
            except Exception as e:
                errors.append(str(e))

        execution_time = time.time() - start_time
        throughput = iterations / execution_time if execution_time > 0 else 0
        error_rate = len(errors) / iterations * 100 if iterations > 0 else 0

        test_result = {
            'name': test_name,
            'duration': duration_seconds,
            'iterations': iterations,
            'errors': len(errors),
            'error_rate': error_rate,
            'execution_time': execution_time,
            'throughput': throughput
        }

        self.results.append(test_result)

        if error_rate == 0:
            logger.info(f"✅ {test_name} - 迭代次數: {iterations}")
        else:
            logger.warning(f"⚠️  {test_name} - 錯誤率: {error_rate:.2f}%")

        logger.info(f"   吞吐量: {throughput:.2f} 操作/秒")

    def print_summary(self):
        """打印測試摘要"""
        logger.info("\n" + "="*70)
        logger.info("📊 負載測試結果摘要")
        logger.info("="*70 + "\n")

        for result in self.results:
            logger.info(f"測試: {result['name']}")

            if 'num_threads' in result:
                # 並發測試結果
                logger.info(f"  並發數: {result['num_threads']}")
                logger.info(f"  成功: {result['successful']}")
                logger.info(f"  失敗: {result['failed']}")
                logger.info(f"  成功率: {result['success_rate']:.1f}%")
                logger.info(f"  執行時間: {result['execution_time']:.4f}秒")
                logger.info(f"  吞吐量: {result['throughput']:.2f} 操作/秒")
            elif 'duration' in result:
                # 壓力測試結果
                logger.info(f"  持續時間: {result['duration']}秒")
                logger.info(f"  迭代次數: {result['iterations']}")
                logger.info(f"  錯誤數: {result['errors']}")
                logger.info(f"  錯誤率: {result['error_rate']:.2f}%")
                logger.info(f"  吞吐量: {result['throughput']:.2f} 操作/秒")

            logger.info("")

        logger.info("-"*70)

        return True


class CSVLoadTest(LoadTest):
    """CSV 生成器負載測試"""

    def test_concurrent_small(self):
        """並發生成小CSV（10個並發）"""
        def generate_csv(thread_id):
            questions = self._generate_questions(50)
            answers = self._generate_answers(50)
            csv_gen = CSVGenerator(self.config)
            temp_path = tempfile.mktemp(suffix=f'_thread_{thread_id}.csv')
            try:
                result = csv_gen.generate_questions_csv(questions, answers, temp_path)
                return result
            finally:
                if os.path.exists(temp_path):
                    os.remove(temp_path)

        self.run_concurrent_test("CSV並發生成 - 10並發x50題", generate_csv, 10)

    def test_concurrent_large(self):
        """並發生成大CSV（20個並發）"""
        def generate_csv(thread_id):
            questions = self._generate_questions(100)
            answers = self._generate_answers(100)
            csv_gen = CSVGenerator(self.config)
            temp_path = tempfile.mktemp(suffix=f'_thread_{thread_id}.csv')
            try:
                result = csv_gen.generate_questions_csv(questions, answers, temp_path)
                return result
            finally:
                if os.path.exists(temp_path):
                    os.remove(temp_path)

        self.run_concurrent_test("CSV並發生成 - 20並發x100題", generate_csv, 20)

    def test_stress_csv(self):
        """CSV生成壓力測試（10秒）"""
        def generate_csv(iteration):
            questions = self._generate_questions(20)
            answers = self._generate_answers(20)
            csv_gen = CSVGenerator(self.config)
            temp_path = tempfile.mktemp(suffix=f'_iter_{iteration}.csv')
            try:
                csv_gen.generate_questions_csv(questions, answers, temp_path)
            finally:
                if os.path.exists(temp_path):
                    os.remove(temp_path)

        self.run_stress_test("CSV生成壓力測試", generate_csv, 10)

    def _generate_questions(self, count: int) -> List[Dict]:
        """生成測試題目"""
        questions = []
        for i in range(1, count + 1):
            questions.append({
                '題號': str(i),
                '題目': f'測試題目{i}',
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


class GoogleScriptLoadTest(LoadTest):
    """Google Script 生成器負載測試"""

    def test_concurrent_script(self):
        """並發生成Google Script（10個並發）"""
        def generate_script(thread_id):
            questions = self._generate_questions(50)
            answers = self._generate_answers(50)
            script_gen = GoogleScriptGenerator(self.config)
            temp_path = tempfile.mktemp(suffix=f'_thread_{thread_id}.gs')
            try:
                result = script_gen.generate_google_script(questions, answers, temp_path)
                return result
            finally:
                if os.path.exists(temp_path):
                    os.remove(temp_path)

        self.run_concurrent_test("Script並發生成 - 10並發x50題", generate_script, 10)

    def test_stress_script(self):
        """Script生成壓力測試（10秒）"""
        def generate_script(iteration):
            questions = self._generate_questions(20)
            answers = self._generate_answers(20)
            script_gen = GoogleScriptGenerator(self.config)
            temp_path = tempfile.mktemp(suffix=f'_iter_{iteration}.gs')
            try:
                script_gen.generate_google_script(questions, answers, temp_path)
            finally:
                if os.path.exists(temp_path):
                    os.remove(temp_path)

        self.run_stress_test("Script生成壓力測試", generate_script, 10)

    def _generate_questions(self, count: int) -> List[Dict]:
        """生成測試題目"""
        questions = []
        for i in range(1, count + 1):
            questions.append({
                '題號': str(i),
                '題目': f'測試題目{i}',
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


class MemoryLoadTest(LoadTest):
    """記憶體負載測試"""

    def test_large_data_structure(self):
        """測試大型數據結構處理"""
        def process_large_data(iteration):
            # 創建大量題目數據
            questions = []
            for i in range(1000):
                questions.append({
                    '題號': str(i),
                    '題目': f'測試題目{i}' * 100,  # 長題目
                    '題型': '選擇題',
                    '選項A': f'選項A_{i}' * 10,
                    '選項B': f'選項B_{i}' * 10,
                    '選項C': f'選項C_{i}' * 10,
                    '選項D': f'選項D_{i}' * 10,
                    '題組': False
                })

            # 處理數據
            processed = []
            for q in questions:
                processed.append({
                    'id': q['題號'],
                    'text': q['題目'].strip(),
                    'type': q['題型']
                })

            return len(processed)

        self.run_stress_test("大數據結構處理", process_large_data, 5)

    def test_string_concatenation(self):
        """測試大量字符串拼接"""
        def concat_strings(iteration):
            result = ""
            for i in range(10000):
                result += f"行{i}\n"
            return len(result)

        # 注意：這個測試可能會很慢，因為字符串拼接效率低
        logger.info("\n▶ 測試: 字符串拼接（可能較慢）")
        start_time = time.time()

        try:
            # 只執行一次作為基準
            length = concat_strings(0)
            execution_time = time.time() - start_time

            logger.info(f"✅ 字符串拼接 - 長度: {length}")
            logger.info(f"   執行時間: {execution_time:.4f}秒")

            self.results.append({
                'name': '字符串拼接測試',
                'length': length,
                'execution_time': execution_time
            })
        except Exception as e:
            logger.error(f"❌ 字符串拼接測試失敗: {e}")


def main():
    """主測試函數"""
    logger.info("\n" + "="*70)
    logger.info("🔥 開始負載測試")
    logger.info("="*70)

    all_success = True

    # CSV 負載測試
    logger.info("\n【CSV 生成器負載測試】")
    csv_test = CSVLoadTest()
    csv_test.test_concurrent_small()
    csv_test.test_concurrent_large()
    csv_test.test_stress_csv()
    csv_test.print_summary()

    # Google Script 負載測試
    logger.info("\n【Google Script 生成器負載測試】")
    script_test = GoogleScriptLoadTest()
    script_test.test_concurrent_script()
    script_test.test_stress_script()
    script_test.print_summary()

    # 記憶體負載測試
    logger.info("\n【記憶體負載測試】")
    memory_test = MemoryLoadTest()
    memory_test.test_large_data_structure()
    memory_test.test_string_concatenation()
    memory_test.print_summary()

    # 總結
    logger.info("\n" + "="*70)
    logger.info("📊 負載測試總結")
    logger.info("="*70)

    all_results = csv_test.results + script_test.results + memory_test.results

    logger.info(f"總測試數: {len(all_results)}")

    # 計算平均吞吐量
    throughput_results = [r for r in all_results if 'throughput' in r]
    if throughput_results:
        avg_throughput = sum(r['throughput'] for r in throughput_results) / len(throughput_results)
        logger.info(f"平均吞吐量: {avg_throughput:.2f} 操作/秒")

    logger.info("\n✅ 🎉 負載測試完成！")
    return 0


if __name__ == '__main__':
    sys.exit(main())
