# 快速開始指南

歡迎使用考古題處理系統！本指南將幫助您快速上手。

---

## 📋 目錄

1. [系統要求](#系統要求)
2. [安裝](#安裝)
3. [基本使用](#基本使用)
4. [進階功能](#進階功能)
5. [常見問題](#常見問題)

---

## 系統要求

- **Python**: 3.8 或更高版本
- **作業系統**: Windows / Linux / macOS
- **記憶體**: 建議 4GB 以上
- **磁盤空間**: 100MB（不含 PDF 文件）

---

## 安裝

### 1. 克隆項目

```bash
git clone https://github.com/your-repo/oldtest.git
cd oldtest
```

### 2. 安裝依賴

```bash
pip install -r requirements.txt
```

### 3. 驗證安裝

```bash
python -m unittest discover tests
```

---

## 基本使用

### 場景 1: 處理單個 PDF

最基本的使用方式：

```python
from src.processors.archaeology_processor import ArchaeologyProcessor

# 創建處理器
processor = ArchaeologyProcessor()

# 處理 PDF
result = processor.process_pdf("exam_questions.pdf")

# 查看結果
print(f"✅ 成功處理 {result['question_count']} 題")
print(f"📄 輸出文件: {result['output_file']}")
```

**輸出示例:**
```
✅ 成功處理 60 題
📄 輸出文件: output/exam_questions.csv
```

---

### 場景 2: 處理題目 + 答案

如果有答案 PDF：

```python
processor = ArchaeologyProcessor()

result = processor.process_pdf(
    pdf_path="exam_questions.pdf",
    answer_pdf_path="exam_answers.pdf"
)

print(f"✅ 處理完成，共 {result['question_count']} 題")
```

---

### 場景 3: 批量處理多個 PDF

處理多個文件：

```python
from src.utils.concurrent_processor import ConcurrentProcessor, ProcessingTask
from src.processors.archaeology_processor import ArchaeologyProcessor

# 定義處理函數
def process_exam(task):
    processor = ArchaeologyProcessor()
    return processor.process_pdf(task.pdf_path)

# 準備任務
tasks = [
    ProcessingTask(task_id=1, pdf_path="exam1.pdf"),
    ProcessingTask(task_id=2, pdf_path="exam2.pdf"),
    ProcessingTask(task_id=3, pdf_path="exam3.pdf"),
]

# 並發處理（4個工作線程）
concurrent = ConcurrentProcessor(max_workers=4)
results = concurrent.process_batch(tasks, process_exam)

# 統計結果
successful = [r for r in results if r.success]
print(f"✅ 成功: {len(successful)}/{len(results)}")
```

**優勢:**
- 🚀 速度提升 3-4 倍
- ⚡ 自動並發處理
- 📊 實時進度顯示

---

### 場景 4: 處理超大 PDF（記憶體優化）

處理 1000+ 頁的大文件：

```python
from src.utils.streaming_processor import StreamingPDFProcessor

# 創建流式處理器
processor = StreamingPDFProcessor()

# 逐區塊處理（每次 10 頁）
for chunk in processor.stream_pages("huge_exam.pdf"):
    print(f"處理頁面 {chunk.pages}")

    # 提取題目
    questions = extract_questions(chunk.text)

    # 保存到資料庫
    save_to_database(questions)

print("✅ 大文件處理完成！")
```

**優勢:**
- 💾 記憶體使用降低 10 倍以上
- 📈 可處理 10000+ 頁 PDF
- 🔄 自動記憶體管理

---

## 進階功能

### 功能 1: 性能監控

監控處理性能：

```python
from src.utils.performance_monitor import monitor_performance, get_global_report

@monitor_performance
def process_file(pdf_path):
    processor = ArchaeologyProcessor()
    return processor.process_pdf(pdf_path)

# 處理文件
result = process_file("exam.pdf")

# 查看性能報告
report = get_global_report()
print(report)
```

**報告示例:**
```
================================================================================
性能監控報告
================================================================================

## 總體統計
總記錄數: 1
總耗時: 2.3456秒
平均CPU: 45.2%

## 函數統計

### process_file
  調用次數: 1
  總耗時: 2.3456秒
  平均耗時: 2.3456秒
```

---

### 功能 2: 自動錯誤恢復

處理可能失敗的任務：

```python
from src.utils.retry_handler import retry_with_backoff

@retry_with_backoff(max_retries=3, initial_delay=1.0)
def process_unreliable_pdf(pdf_path):
    # 可能會失敗的處理
    return processor.process_pdf(pdf_path)

# 自動重試最多 3 次
result = process_unreliable_pdf("exam.pdf")
```

**特點:**
- 🔄 自動重試
- ⏰ 指數退避
- 📝 錯誤記錄

---

### 功能 3: 斷點續傳

處理大批量任務時保存進度：

```python
from src.utils.retry_handler import CheckpointManager

checkpoint = CheckpointManager("batch_progress.json")

# 載入之前的進度
data = checkpoint.load_checkpoint()
completed = data.get('completed', []) if data else []

# 只處理未完成的任務
pending_tasks = [t for t in all_tasks if t.id not in completed]

# 處理任務
for task in pending_tasks:
    result = process_task(task)
    if result.success:
        completed.append(task.id)
        # 保存進度
        checkpoint.save_checkpoint({'completed': completed})

print(f"✅ 完成 {len(completed)} 個任務")
```

---

### 功能 4: 自定義配置

使用配置文件自定義行為：

#### config.yaml
```yaml
processing:
  max_pages: 200
  output_encoding: utf-8-sig

ocr:
  pdf_to_image_dpi: 300
  use_gpu: false

concurrent:
  max_workers: 4
  use_processes: false
```

#### 使用配置
```python
from src.utils.yaml_config import load_config

# 載入配置
config = load_config('config.yaml')

# 使用配置
max_pages = config.processing.max_pages
dpi = config.ocr.pdf_to_image_dpi
```

---

## 常見問題

### Q1: PDF 處理失敗怎麼辦？

**A:** 檢查以下幾點：
1. 確認 PDF 文件存在且可讀
2. 檢查 PDF 是否加密
3. 確認文件格式正確（非掃描版）
4. 查看日誌了解具體錯誤

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# 再次處理，查看詳細日誌
result = processor.process_pdf("exam.pdf")
```

---

### Q2: 記憶體不足怎麼辦？

**A:** 使用流式處理：

```python
# 改用流式處理器
from src.utils.streaming_processor import StreamingPDFProcessor

processor = StreamingPDFProcessor()
for chunk in processor.stream_pages("large.pdf"):
    process(chunk)  # 逐區塊處理，記憶體穩定
```

---

### Q3: 處理速度太慢怎麼辦？

**A:** 啟用並發處理：

```python
# 使用並發處理器
from src.utils.concurrent_processor import ConcurrentProcessor

concurrent = ConcurrentProcessor(max_workers=8)  # 增加工作線程
results = concurrent.process_batch(tasks, process_func)
```

---

### Q4: 如何查看處理進度？

**A:** 使用進度追蹤：

```python
from src.utils.concurrent_processor import ConcurrentProcessor

processor = ConcurrentProcessor(max_workers=4)

# 自動顯示進度
results = processor.process_batch(
    tasks,
    process_func,
    progress_callback=lambda i, total: print(f"進度: {i}/{total}")
)
```

---

### Q5: 如何提取特定頁面？

**A:** 使用頁面範圍參數：

```python
from src.core.pdf_processor import PDFProcessor

processor = PDFProcessor()

# 只提取第 10-20 頁
text = processor.extract_text_from_pages("exam.pdf", list(range(10, 21)))
```

---

### Q6: 支持哪些 PDF 格式？

**A:** 支持：
- ✅ 標準 PDF（文字型）
- ✅ 掃描 PDF（需要 OCR，使用 PaddleOCR）
- ✅ 混合格式 PDF
- ❌ 加密 PDF（需先解密）

---

### Q7: 如何導出其他格式？

**A:** 默認導出 CSV，可自定義：

```python
import pandas as pd

# 讀取 CSV
df = pd.read_csv("output.csv")

# 轉換格式
df.to_excel("output.xlsx", index=False)  # Excel
df.to_json("output.json", orient='records')  # JSON
```

---

## 📚 下一步

- 閱讀 [API 文檔](API_DOCUMENTATION.md) 了解詳細功能
- 查看 [示例代碼](../examples/) 學習更多用法
- 閱讀 [改進總結](../IMPROVEMENTS_SUMMARY.md) 了解系統特性

---

## 🆘 獲取幫助

遇到問題？

1. 查看 [常見問題](#常見問題)
2. 閱讀 [API 文檔](API_DOCUMENTATION.md)
3. 查看 [示例代碼](../examples/)
4. 提交 Issue

---

## 🎯 快速參考

### 命令速查

```bash
# 運行測試
python -m unittest discover tests

# 運行特定測試
python -m unittest tests.test_concurrent_processor

# 查看性能報告
python examples/performance_monitoring_example.py

# 運行並發示例
python examples/concurrent_processing_example.py
```

### 常用代碼片段

```python
# 基本處理
from src.processors.archaeology_processor import ArchaeologyProcessor
processor = ArchaeologyProcessor()
result = processor.process_pdf("exam.pdf")

# 並發處理
from src.utils.concurrent_processor import ConcurrentProcessor
concurrent = ConcurrentProcessor(max_workers=4)
results = concurrent.process_batch(tasks, process_func)

# 流式處理
from src.utils.streaming_processor import StreamingPDFProcessor
processor = StreamingPDFProcessor()
for chunk in processor.stream_pages("large.pdf"):
    process(chunk)

# 性能監控
from src.utils.performance_monitor import monitor_performance
@monitor_performance
def my_function():
    pass
```

---

**祝使用愉快！** 🎉
