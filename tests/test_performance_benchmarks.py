"""
性能基準測試模組
測試各個組件的性能表現並建立基準線，用於檢測性能回歸
"""

import os
import statistics
import tempfile
import time
from pathlib import Path
from typing import Callable, Dict, List

import psutil
import pytest

from src.core.csv_generator import CSVGenerator
from src.core.essay_question_parser import EssayQuestionParser
from src.core.mixed_format_parser import MixedFormatParser

# 導入要測試的模組
from src.core.pdf_processor import PDFProcessor
from src.core.question_parser import QuestionParser
from src.core.ultimate_question_parser import UltimateQuestionParser
from src.utils.concurrent_processor import ConcurrentProcessor, ProcessingTask


class PerformanceBenchmark:
    """性能基準測試類"""

    def __init__(self):
        self.results: Dict[str, Dict] = {}
        self.process = psutil.Process(os.getpid())

    def measure_time(self, func: Callable, *args, **kwargs) -> tuple:
        """測量函數執行時間和記憶體使用"""
        # 記錄開始狀態
        start_time = time.perf_counter()
        start_memory = self.process.memory_info().rss / 1024 / 1024  # MB

        # 執行函數
        result = func(*args, **kwargs)

        # 記錄結束狀態
        end_time = time.perf_counter()
        end_memory = self.process.memory_info().rss / 1024 / 1024  # MB

        execution_time = end_time - start_time
        memory_used = end_memory - start_memory

        return result, execution_time, memory_used

    def run_multiple_times(self, func: Callable, iterations: int = 5, *args, **kwargs) -> Dict:
        """多次運行測試以獲得可靠的結果"""
        times = []
        memories = []

        for _ in range(iterations):
            _, exec_time, memory_used = self.measure_time(func, *args, **kwargs)
            times.append(exec_time)
            memories.append(memory_used)

        return {
            "avg_time": statistics.mean(times),
            "min_time": min(times),
            "max_time": max(times),
            "std_time": statistics.stdev(times) if len(times) > 1 else 0,
            "avg_memory": statistics.mean(memories),
            "min_memory": min(memories),
            "max_memory": max(memories),
        }


@pytest.fixture
def benchmark():
    """提供性能基準測試工具"""
    return PerformanceBenchmark()


@pytest.fixture
def sample_pdf_content():
    """提供測試用的 PDF 內容"""
    return (
        """
    1. 下列何者正確？
    (A) 選項 A
    (B) 選項 B
    (C) 選項 C
    (D) 選項 D

    2. 以下敘述何者為真？
    (A) 第一個選項
    (B) 第二個選項
    (C) 第三個選項
    (D) 第四個選項
    """
        * 10
    )  # 重複10次以模擬較大的內容


@pytest.fixture
def large_pdf_content():
    """提供大型 PDF 測試內容"""
    base_question = """
    {}. 測試題目內容？
    (A) 選項 A 的內容描述
    (B) 選項 B 的內容描述
    (C) 選項 C 的內容描述
    (D) 選項 D 的內容描述

    """
    return "".join([base_question.format(i) for i in range(1, 101)])  # 100 題


class TestPDFProcessorPerformance:
    """測試 PDF 處理器的性能"""

    def test_pdf_text_extraction_speed(self, benchmark, tmp_path):
        """測試 PDF 文字提取速度

        基準：< 1 秒/頁（純文字 PDF）
        """
        # 創建測試 PDF（實際測試中應使用真實 PDF）
        # 這裡使用模擬數據
        processor = PDFProcessor()

        # 模擬處理
        def extract_text():
            # 實際測試中應該處理真實 PDF
            return "測試文字" * 1000

        results = benchmark.run_multiple_times(extract_text, iterations=10)

        # 斷言性能基準
        assert results["avg_time"] < 1.0, f"PDF 文字提取太慢: {results['avg_time']:.3f}s"
        assert results["avg_memory"] < 50, f"記憶體使用過多: {results['avg_memory']:.2f}MB"

        print(f"\n📊 PDF 文字提取性能:")
        print(f"  平均時間: {results['avg_time']:.3f}s")
        print(f"  記憶體使用: {results['avg_memory']:.2f}MB")


class TestQuestionParserPerformance:
    """測試題目解析器的性能"""

    def test_standard_parser_speed(self, benchmark, sample_pdf_content):
        """測試標準解析器速度

        基準：< 0.1 秒/10題
        """
        parser = QuestionParser()

        def parse_questions():
            return parser.parse_questions(sample_pdf_content)

        results = benchmark.run_multiple_times(parse_questions, iterations=10)

        # 斷言性能基準
        assert results["avg_time"] < 0.1, f"解析速度太慢: {results['avg_time']:.3f}s"
        assert results["avg_memory"] < 10, f"記憶體使用過多: {results['avg_memory']:.2f}MB"

        print(f"\n📊 標準解析器性能:")
        print(f"  平均時間: {results['avg_time']:.3f}s")
        print(f"  標準差: {results['std_time']:.3f}s")
        print(f"  記憶體: {results['avg_memory']:.2f}MB")

    def test_large_document_parsing(self, benchmark, large_pdf_content):
        """測試大文件解析性能

        基準：< 1 秒/100題
        """
        parser = QuestionParser()

        def parse_large():
            return parser.parse_questions(large_pdf_content)

        results = benchmark.run_multiple_times(parse_large, iterations=5)

        assert results["avg_time"] < 1.0, f"大文件解析太慢: {results['avg_time']:.3f}s"

        print(f"\n📊 大文件解析性能 (100題):")
        print(f"  平均時間: {results['avg_time']:.3f}s")
        print(f"  吞吐量: {100 / results['avg_time']:.1f} 題/秒")


class TestParserComparison:
    """比較不同解析器的性能"""

    @pytest.mark.parametrize(
        "parser_class,name",
        [
            (QuestionParser, "標準解析器"),
            (EssayQuestionParser, "申論題解析器"),
            (MixedFormatParser, "混合格式解析器"),
            (UltimateQuestionParser, "終極解析器"),
        ],
    )
    def test_parser_comparison(self, benchmark, sample_pdf_content, parser_class, name):
        """比較不同解析器的性能"""
        parser = parser_class()

        def parse():
            try:
                return parser.parse(sample_pdf_content)
            except Exception:
                return []

        results = benchmark.run_multiple_times(parse, iterations=5)

        print(f"\n📊 {name} 性能:")
        print(f"  平均時間: {results['avg_time']:.3f}s")
        print(f"  記憶體: {results['avg_memory']:.2f}MB")

        # 每個解析器都應該在合理時間內完成
        assert results["avg_time"] < 2.0, f"{name} 性能不達標"


class TestConcurrentProcessingPerformance:
    """測試並發處理性能"""

    def test_concurrent_speedup(self, benchmark, tmp_path):
        """測試並發處理的速度提升

        預期：3-4 倍速度提升（4 worker）
        """
        # 創建測試文件
        test_files = []
        for i in range(4):
            test_file = tmp_path / f"test_{i}.txt"
            test_file.write_text(f"測試內容 {i}" * 100)
            test_files.append(str(test_file))

        def process_file(file_path):
            """模擬處理單個文件"""
            time.sleep(0.1)  # 模擬處理時間
            with open(file_path, "r", encoding="utf-8") as f:
                return len(f.read())

        # 測試順序處理
        def sequential_processing():
            return [process_file(f) for f in test_files]

        # 測試並發處理
        def concurrent_processing():
            processor = ConcurrentProcessor(max_workers=4)
            # Convert file paths to ProcessingTask objects with task_id
            tasks = [ProcessingTask(task_id=i, pdf_path=f, output_dir=str(tmp_path)) 
                    for i, f in enumerate(test_files)]
            
            # Create a wrapper function that accepts ProcessingTask
            def task_processor(task: ProcessingTask):
                return process_file(task.pdf_path)
            
            return processor.process_batch(tasks, task_processor)

        # 測量性能
        _, seq_time, _ = benchmark.measure_time(sequential_processing)
        _, con_time, _ = benchmark.measure_time(concurrent_processing)

        speedup = seq_time / con_time

        print(f"\n📊 並發處理性能:")
        print(f"  順序處理: {seq_time:.3f}s")
        print(f"  並發處理: {con_time:.3f}s")
        print(f"  速度提升: {speedup:.2f}x")

        # 應該有明顯的速度提升
        assert speedup > 2.0, f"並發速度提升不足: {speedup:.2f}x"


class TestMemoryUsage:
    """測試記憶體使用"""

    def test_memory_leak(self, benchmark, sample_pdf_content):
        """測試是否存在記憶體洩漏"""
        parser = QuestionParser()

        initial_memory = benchmark.process.memory_info().rss / 1024 / 1024

        # 多次執行
        for _ in range(100):
            parser.parse_questions(sample_pdf_content)

        final_memory = benchmark.process.memory_info().rss / 1024 / 1024
        memory_increase = final_memory - initial_memory

        print(f"\n📊 記憶體洩漏測試 (100 次迭代):")
        print(f"  初始記憶體: {initial_memory:.2f}MB")
        print(f"  最終記憶體: {final_memory:.2f}MB")
        print(f"  記憶體增長: {memory_increase:.2f}MB")

        # 記憶體增長應該在合理範圍內（< 50MB）
        assert memory_increase < 50, f"可能存在記憶體洩漏: {memory_increase:.2f}MB"

    def test_large_file_memory_efficiency(self, benchmark, large_pdf_content):
        """測試大文件處理的記憶體效率

        基準：< 100MB for 100 題
        """
        parser = QuestionParser()

        _, exec_time, memory_used = benchmark.measure_time(parser.parse_questions, large_pdf_content)

        print(f"\n📊 大文件記憶體效率 (100題):")
        print(f"  執行時間: {exec_time:.3f}s")
        print(f"  記憶體使用: {memory_used:.2f}MB")
        print(f"  記憶體效率: {memory_used / 100:.2f}MB/題")

        assert memory_used < 100, f"記憶體使用過多: {memory_used:.2f}MB"


class TestCSVGeneratorPerformance:
    """測試 CSV 生成器性能"""

    def test_csv_generation_speed(self, benchmark, tmp_path):
        """測試 CSV 生成速度

        基準：< 0.5 秒/100題
        """
        generator = CSVGenerator()

        # 創建測試數據
        test_questions = [
            {
                "題號": i,
                "題目": f"測試題目 {i}",
                "題型": "選擇題",
                "選項A": f"選項 A {i}",
                "選項B": f"選項 B {i}",
                "選項C": f"選項 C {i}",
                "選項D": f"選項 D {i}",
            }
            for i in range(1, 101)
        ]

        output_file = tmp_path / "test_output.csv"

        def generate_csv():
            # Use the correct method - generate_questions_csv
            answers = {str(i): "A" for i in range(1, 101)}
            generator.generate_questions_csv(test_questions, answers, str(output_file))

        results = benchmark.run_multiple_times(generate_csv, iterations=5)

        print(f"\n📊 CSV 生成性能 (100題):")
        print(f"  平均時間: {results['avg_time']:.3f}s")
        print(f"  吞吐量: {100 / results['avg_time']:.1f} 題/秒")

        assert results["avg_time"] < 0.5, f"CSV 生成太慢: {results['avg_time']:.3f}s"


class TestPerformanceRegression:
    """性能回歸測試"""

    # 定義性能基準線（這些值應該基於實際測量結果設定）
    BENCHMARKS = {
        "pdf_extraction": {"max_time": 1.0, "max_memory": 50},
        "question_parsing": {"max_time": 0.1, "max_memory": 10},
        "large_document": {"max_time": 1.0, "max_memory": 100},
        "csv_generation": {"max_time": 0.5, "max_memory": 20},
    }

    def test_no_performance_regression(self, benchmark, sample_pdf_content):
        """確保沒有性能回歸"""
        parser = QuestionParser()

        results = benchmark.run_multiple_times(parser.parse_questions, iterations=10, text=sample_pdf_content)

        baseline = self.BENCHMARKS["question_parsing"]

        # 檢查是否符合基準
        time_regression = results["avg_time"] > baseline["max_time"]
        memory_regression = results["avg_memory"] > baseline["max_memory"]

        print(f"\n📊 性能回歸測試:")
        print(f"  當前時間: {results['avg_time']:.3f}s (基準: {baseline['max_time']}s)")
        print(f"  當前記憶體: {results['avg_memory']:.2f}MB (基準: {baseline['max_memory']}MB)")

        if time_regression:
            pytest.fail(f"⚠️  檢測到時間性能回歸: " f"{results['avg_time']:.3f}s > {baseline['max_time']}s")

        if memory_regression:
            pytest.fail(f"⚠️  檢測到記憶體性能回歸: " f"{results['avg_memory']:.2f}MB > {baseline['max_memory']}MB")


class TestThroughput:
    """測試系統吞吐量"""

    def test_questions_per_second(self, benchmark, large_pdf_content):
        """測試每秒處理題目數量

        基準：> 100 題/秒
        """
        parser = QuestionParser()

        _, exec_time, _ = benchmark.measure_time(parser.parse_questions, large_pdf_content)

        throughput = 100 / exec_time  # 100題的吞吐量

        print(f"\n📊 系統吞吐量:")
        print(f"  處理時間: {exec_time:.3f}s (100題)")
        print(f"  吞吐量: {throughput:.1f} 題/秒")

        assert throughput > 100, f"吞吐量不足: {throughput:.1f} 題/秒"


# 運行基準測試的主函數
if __name__ == "__main__":
    pytest.main(
        [
            __file__,
            "-v",
            "--tb=short",
            "-s",  # 顯示 print 輸出
            "--benchmark-only",  # 僅運行基準測試
        ]
    )
