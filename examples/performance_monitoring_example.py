#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
性能監控示例
演示如何使用性能監控系統來監控和優化代碼性能
"""

import sys
import os
import time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.utils.performance_monitor import (
    PerformanceMonitor,
    PerformanceTimer,
    monitor_performance,
    get_global_report,
    export_global_metrics
)


def example_basic_timer():
    """示例 1: 使用基本計時器"""
    print("=" * 60)
    print("示例 1: 使用基本計時器")
    print("=" * 60)

    print("""
    # 使用上下文管理器進行計時
    with PerformanceTimer("處理PDF") as timer:
        # 執行一些操作
        process_pdf()

    print(timer.get_summary())
    # 輸出: 處理PDF: 2.3456秒, 記憶體變化: +15.23MB
    """)

    # 實際示例
    with PerformanceTimer("示例處理") as timer:
        time.sleep(0.1)
        data = [i for i in range(10000)]

    print(timer.get_summary())
    print()


def example_monitor_decorator():
    """示例 2: 使用監控裝飾器"""
    print("=" * 60)
    print("示例 2: 使用監控裝飾器")
    print("=" * 60)

    print("""
    # 創建性能監控器
    monitor = PerformanceMonitor()

    # 使用裝飾器自動監控
    @monitor.monitor()
    def process_file(file_path):
        # 處理邏輯
        pass

    # 調用函數（自動記錄性能）
    process_file("test.pdf")

    # 查看統計
    stats = monitor.get_function_stats("process_file")
    print(f"調用次數: {stats['call_count']}")
    print(f"平均耗時: {stats['avg_time']:.4f}秒")
    """)

    # 實際示例
    monitor = PerformanceMonitor()

    @monitor.monitor()
    def process_data(size):
        data = [i ** 2 for i in range(size)]
        return len(data)

    # 多次調用
    for size in [1000, 5000, 10000]:
        result = process_data(size)
        print(f"處理 {size} 個元素，結果: {result}")

    # 查看統計
    stats = monitor.get_function_stats("process_data")
    print(f"\n統計信息:")
    print(f"  調用次數: {stats['call_count']}")
    print(f"  總耗時: {stats['total_time']:.4f}秒")
    print(f"  平均耗時: {stats['avg_time']:.4f}秒")
    print()


def example_global_monitor():
    """示例 3: 使用全局監控器"""
    print("=" * 60)
    print("示例 3: 使用全局監控器")
    print("=" * 60)

    print("""
    # 使用全局裝飾器（無需創建監控器實例）
    @monitor_performance
    def extract_text(pdf_path):
        # 提取文字邏輯
        pass

    @monitor_performance
    def parse_questions(text):
        # 解析題目邏輯
        pass

    # 自動使用全局監控器
    text = extract_text("exam.pdf")
    questions = parse_questions(text)

    # 獲取全局報告
    report = get_global_report()
    print(report)
    """)

    # 實際示例
    @monitor_performance
    def step1():
        time.sleep(0.05)
        return "Step 1 完成"

    @monitor_performance
    def step2():
        time.sleep(0.03)
        return "Step 2 完成"

    @monitor_performance
    def step3():
        time.sleep(0.02)
        return "Step 3 完成"

    # 執行工作流程
    result1 = step1()
    result2 = step2()
    result3 = step3()

    print(f"{result1}")
    print(f"{result2}")
    print(f"{result3}")
    print()


def example_performance_report():
    """示例 4: 生成性能報告"""
    print("=" * 60)
    print("示例 4: 生成詳細性能報告")
    print("=" * 60)

    monitor = PerformanceMonitor()

    @monitor.monitor()
    def process_batch(batch_size):
        total = 0
        for i in range(batch_size):
            total += i ** 2
        return total

    # 處理不同大小的批次
    for size in [100, 500, 1000, 5000]:
        result = process_batch(size)

    # 生成報告
    report = monitor.generate_report()
    print(report)
    print()


def example_export_metrics():
    """示例 5: 導出性能指標"""
    print("=" * 60)
    print("示例 5: 導出性能指標到文件")
    print("=" * 60)

    print("""
    monitor = PerformanceMonitor()

    @monitor.monitor()
    def process_pdf(pdf_path):
        # 處理邏輯
        pass

    # 處理多個文件
    for pdf in pdf_files:
        process_pdf(pdf)

    # 導出指標到 JSON
    monitor.export_metrics("performance_metrics.json")

    # 導出報告到文件
    report = monitor.generate_report("performance_report.txt")
    """)

    monitor = PerformanceMonitor()

    @monitor.monitor()
    def simulated_process(item_id):
        time.sleep(0.01)
        return f"處理完成: {item_id}"

    # 處理多個項目
    for i in range(5):
        simulated_process(i)

    # 導出到臨時文件
    import tempfile
    temp_dir = tempfile.gettempdir()

    metrics_file = os.path.join(temp_dir, "metrics_example.json")
    report_file = os.path.join(temp_dir, "report_example.txt")

    monitor.export_metrics(metrics_file)
    monitor.generate_report(report_file)

    print(f"指標已導出到: {metrics_file}")
    print(f"報告已導出到: {report_file}")
    print()


def example_real_world_usage():
    """示例 6: 實際應用場景"""
    print("=" * 60)
    print("示例 6: 實際應用 - 監控考古題處理流程")
    print("=" * 60)

    print("""
    monitor = PerformanceMonitor()

    @monitor.monitor()
    def extract_pdf_text(pdf_path):
        # 從 PDF 提取文字
        return pdf_text

    @monitor.monitor()
    def parse_questions(text):
        # 解析題目
        return questions

    @monitor.monitor()
    def validate_questions(questions):
        # 驗證題目
        return validated_questions

    @monitor.monitor()
    def export_to_csv(questions, output_path):
        # 導出到 CSV
        pass

    # 處理完整流程
    text = extract_pdf_text("exam.pdf")
    questions = parse_questions(text)
    validated = validate_questions(questions)
    export_to_csv(validated, "output.csv")

    # 生成性能報告
    report = monitor.generate_report()
    # 可以看到每個步驟的耗時和資源使用情況
    """)

    # 模擬實際流程
    monitor = PerformanceMonitor()

    @monitor.monitor()
    def simulate_pdf_extraction():
        time.sleep(0.1)
        return "模擬PDF文字內容..."

    @monitor.monitor()
    def simulate_parsing(text):
        time.sleep(0.2)
        return [{"q": "題目1"}, {"q": "題目2"}]

    @monitor.monitor()
    def simulate_validation(questions):
        time.sleep(0.05)
        return questions

    @monitor.monitor()
    def simulate_export(questions):
        time.sleep(0.03)
        return len(questions)

    # 執行流程
    text = simulate_pdf_extraction()
    questions = simulate_parsing(text)
    validated = simulate_validation(questions)
    count = simulate_export(validated)

    print(f"處理完成，共 {count} 個題目")
    print()

    # 生成簡化報告
    all_stats = monitor.get_all_stats()
    print("各步驟性能統計:")
    for func_name, stats in all_stats.items():
        print(f"  {func_name}: {stats['avg_time']:.4f}秒")
    print()


def example_compare_performance():
    """示例 7: 性能對比"""
    print("=" * 60)
    print("示例 7: 性能對比 - 不同算法比較")
    print("=" * 60)

    monitor = PerformanceMonitor()

    @monitor.monitor()
    def method_a(n):
        """方法A: 使用列表推導"""
        return [i ** 2 for i in range(n)]

    @monitor.monitor()
    def method_b(n):
        """方法B: 使用 map"""
        return list(map(lambda x: x ** 2, range(n)))

    # 測試兩種方法
    size = 10000

    result_a = method_a(size)
    result_b = method_b(size)

    # 比較性能
    stats_a = monitor.get_function_stats("method_a")
    stats_b = monitor.get_function_stats("method_b")

    print(f"方法A (列表推導): {stats_a['avg_time']:.6f}秒")
    print(f"方法B (map): {stats_b['avg_time']:.6f}秒")

    faster = "A" if stats_a['avg_time'] < stats_b['avg_time'] else "B"
    speedup = max(stats_a['avg_time'], stats_b['avg_time']) / min(stats_a['avg_time'], stats_b['avg_time'])
    print(f"\n方法{faster}更快，快 {speedup:.2f}倍")
    print()


def example_monitoring_best_practices():
    """示例 8: 監控最佳實踐"""
    print("=" * 60)
    print("示例 8: 性能監控最佳實踐")
    print("=" * 60)

    print("""
    ## 最佳實踐 1: 監控關鍵函數
    只監控關鍵的、耗時的函數，避免過度監控

    @monitor_performance
    def critical_function():  # 監控
        expensive_operation()

    def helper_function():  # 不監控
        simple_operation()

    ## 最佳實踐 2: 定期生成報告
    # 在批量處理結束後生成報告
    monitor = PerformanceMonitor()

    for pdf in pdf_files:
        process_pdf(pdf)

    # 批次處理完成後生成報告
    report = monitor.generate_report()
    monitor.clear_metrics()  # 清除舊指標

    ## 最佳實踐 3: 使用計時器進行細粒度監控
    def complex_function():
        # 監控整個函數
        with PerformanceTimer("步驟1") as t1:
            step1()

        with PerformanceTimer("步驟2") as t2:
            step2()

        print(f"步驟1: {t1.get_duration():.2f}秒")
        print(f"步驟2: {t2.get_duration():.2f}秒")

    ## 最佳實踐 4: 導出指標進行分析
    # 導出後可用其他工具分析
    monitor.export_metrics("metrics.json")
    # 然後用 pandas, matplotlib 等進行數據分析

    ## 最佳實踐 5: 監控資源使用
    # 同時監控時間、記憶體和 CPU
    @monitor.monitor(track_memory=True, track_cpu=True)
    def resource_intensive_function():
        # 處理大量數據
        pass
    """)
    print()


def example_troubleshooting():
    """示例 9: 性能問題排查"""
    print("=" * 60)
    print("示例 9: 使用性能監控排查性能瓶頸")
    print("=" * 60)

    print("""
    # 場景: 發現批量處理很慢，需要找出瓶頸

    monitor = PerformanceMonitor()

    @monitor.monitor()
    def read_pdf(path):
        # 讀取 PDF
        pass

    @monitor.monitor()
    def extract_text(pdf):
        # 提取文字
        pass

    @monitor.monitor()
    def parse_questions(text):
        # 解析題目
        pass

    @monitor.monitor()
    def save_to_db(questions):
        # 保存到資料庫
        pass

    # 處理多個文件
    for pdf_path in pdf_files:
        pdf = read_pdf(pdf_path)
        text = extract_text(pdf)
        questions = parse_questions(text)
        save_to_db(questions)

    # 生成報告找出瓶頸
    report = monitor.generate_report()
    # 可能發現: save_to_db 佔用了80%的時間
    # 然後可以針對性地優化資料庫操作
    """)

    # 模擬排查
    monitor = PerformanceMonitor()

    @monitor.monitor()
    def fast_operation():
        time.sleep(0.01)

    @monitor.monitor()
    def slow_operation():
        time.sleep(0.1)  # 這是瓶頸！

    @monitor.monitor()
    def normal_operation():
        time.sleep(0.02)

    # 執行多次
    for _ in range(3):
        fast_operation()
        slow_operation()
        normal_operation()

    # 查看統計
    all_stats = monitor.get_all_stats()
    print("各操作總耗時:")
    for func, stats in sorted(all_stats.items(), key=lambda x: x[1]['total_time'], reverse=True):
        percentage = (stats['total_time'] / sum(s['total_time'] for s in all_stats.values())) * 100
        print(f"  {func}: {stats['total_time']:.4f}秒 ({percentage:.1f}%)")

    print("\n結論: slow_operation 是性能瓶頸，應該優先優化！")
    print()


if __name__ == '__main__':
    print("\n" + "=" * 60)
    print(" 性能監控系統 - 完整示例")
    print("=" * 60 + "\n")

    # 運行所有示例
    example_basic_timer()
    example_monitor_decorator()
    example_global_monitor()
    example_performance_report()
    example_export_metrics()
    example_real_world_usage()
    example_compare_performance()
    example_monitoring_best_practices()
    example_troubleshooting()

    print("=" * 60)
    print(" 所有示例完成")
    print("=" * 60 + "\n")

    print("\n🚀 性能監控系統特點:")
    print("=" * 60)
    print("1. ⏱️  精確的時間測量")
    print("2. 💾 記憶體使用追蹤")
    print("3. 🖥️  CPU 使用監控")
    print("4. 📊 詳細的統計報告")
    print("5. 📝 自動日誌記錄")
    print("6. 📤 JSON 格式導出")
    print("7. 🎯 裝飾器簡化使用")
    print("8. 🔍 性能瓶頸識別")
    print("=" * 60 + "\n")
