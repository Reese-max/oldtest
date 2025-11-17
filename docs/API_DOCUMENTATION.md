# API 文檔

**版本**: 1.0
**日期**: 2025-11-17

---

## 📚 目錄

1. [核心模塊 API](#核心模塊-api)
2. [工具模塊 API](#工具模塊-api)
3. [處理器模塊 API](#處理器模塊-api)
4. [快速開始](#快速開始)
5. [常見用例](#常見用例)

---

## 核心模塊 API

### PDFProcessor

PDF 處理器，負責從 PDF 文件提取文字。

#### 類定義

```python
from src.core.pdf_processor import PDFProcessor

processor = PDFProcessor()
```

#### 方法

##### `extract_text(pdf_path: str, max_pages: int = 200) -> str`

從 PDF 文件中提取文字內容。

**參數:**
- `pdf_path` (str): PDF 文件路徑
- `max_pages` (int, optional): 最大處理頁數，默認 200

**返回:**
- `str`: 提取的文字內容

**異常:**
- `PDFProcessingError`: PDF 處理失敗時拋出

**示例:**
```python
processor = PDFProcessor()
text = processor.extract_text("exam.pdf", max_pages=100)
print(f"提取了 {len(text)} 個字符")
```

##### `extract_text_from_pages(pdf_path: str, page_numbers: List[int]) -> str`

從指定頁面提取文字。

**參數:**
- `pdf_path` (str): PDF 文件路徑
- `page_numbers` (List[int]): 要提取的頁碼列表

**返回:**
- `str`: 提取的文字內容

**示例:**
```python
text = processor.extract_text_from_pages("exam.pdf", [1, 2, 3])
```

##### `get_page_count(pdf_path: str) -> int`

獲取 PDF 的總頁數。

**參數:**
- `pdf_path` (str): PDF 文件路徑

**返回:**
- `int`: PDF 總頁數

**示例:**
```python
count = processor.get_page_count("exam.pdf")
print(f"PDF 共有 {count} 頁")
```

---

### QuestionParser

題目解析器，從文字中解析題目和選項。

#### 類定義

```python
from src.core.question_parser import QuestionParser

parser = QuestionParser()
```

#### 方法

##### `parse_questions(text: str) -> List[Dict[str, Any]]`

解析文字中的題目。

**參數:**
- `text` (str): 包含題目的文字內容

**返回:**
- `List[Dict[str, Any]]`: 題目列表，每個題目包含題號、題目文字、選項等

**示例:**
```python
parser = QuestionParser()
questions = parser.parse_questions(text)

for q in questions:
    print(f"題號: {q['題號']}")
    print(f"題目: {q['題目']}")
    print(f"選項: {q['選項']}")
```

---

### ArchaeologyProcessor

考古題處理器，完整的題目處理流程。

#### 類定義

```python
from src.processors.archaeology_processor import ArchaeologyProcessor

processor = ArchaeologyProcessor()
```

#### 方法

##### `process_pdf(pdf_path: str, answer_pdf_path: Optional[str] = None) -> Dict[str, Any]`

處理考古題 PDF。

**參數:**
- `pdf_path` (str): 題目 PDF 路徑
- `answer_pdf_path` (str, optional): 答案 PDF 路徑

**返回:**
- `Dict[str, Any]`: 處理結果，包含題目列表、統計信息等

**示例:**
```python
processor = ArchaeologyProcessor()
result = processor.process_pdf(
    "exam_questions.pdf",
    answer_pdf_path="exam_answers.pdf"
)

print(f"共解析 {result['question_count']} 題")
```

---

## 工具模塊 API

### ConcurrentProcessor

並發處理器，支持多線程/多進程批量處理。

#### 類定義

```python
from src.utils.concurrent_processor import ConcurrentProcessor, ProcessingTask

processor = ConcurrentProcessor(
    max_workers=4,
    use_processes=False
)
```

**參數:**
- `max_workers` (int, optional): 最大工作線程/進程數，默認為 CPU 核心數
- `use_processes` (bool, optional): 是否使用多進程，默認 False（使用多線程）

#### 方法

##### `process_batch(tasks: List[ProcessingTask], processor_func: Callable, fail_fast: bool = False) -> List[ProcessingResult]`

批量處理任務。

**參數:**
- `tasks` (List[ProcessingTask]): 任務列表
- `processor_func` (Callable): 處理函數
- `fail_fast` (bool, optional): 是否在首次失敗時停止，默認 False

**返回:**
- `List[ProcessingResult]`: 處理結果列表

**示例:**
```python
from src.utils.concurrent_processor import ConcurrentProcessor, ProcessingTask

def process_pdf(task):
    # 處理邏輯
    return {"success": True, "data": task.pdf_path}

tasks = [
    ProcessingTask(task_id=1, pdf_path="exam1.pdf"),
    ProcessingTask(task_id=2, pdf_path="exam2.pdf"),
]

processor = ConcurrentProcessor(max_workers=4)
results = processor.process_batch(tasks, process_pdf)

for result in results:
    if result.success:
        print(f"成功: {result.task_id}")
```

---

### StreamingPDFProcessor

流式 PDF 處理器，記憶體高效的頁面處理。

#### 類定義

```python
from src.utils.streaming_processor import StreamingPDFProcessor, StreamConfig

config = StreamConfig(
    chunk_size=10,
    memory_limit_mb=512
)

processor = StreamingPDFProcessor(config)
```

**配置參數 (StreamConfig):**
- `chunk_size` (int): 每次處理的頁數，默認 10
- `memory_limit_mb` (int): 記憶體限制（MB），默認 512
- `enable_monitoring` (bool): 是否啟用記憶體監控，默認 True
- `auto_gc` (bool): 是否自動垃圾回收，默認 True

#### 方法

##### `stream_pages(pdf_path: str, start_page: int = 1, end_page: Optional[int] = None) -> Iterator[PageChunk]`

流式處理 PDF 頁面（生成器）。

**參數:**
- `pdf_path` (str): PDF 文件路徑
- `start_page` (int, optional): 起始頁碼，默認 1
- `end_page` (int, optional): 結束頁碼，默認處理到最後

**返回:**
- `Iterator[PageChunk]`: 頁面區塊迭代器

**示例:**
```python
processor = StreamingPDFProcessor()

for chunk in processor.stream_pages("large_exam.pdf"):
    # 處理每個區塊（10頁）
    print(f"處理頁面 {chunk.pages}")
    questions = extract_questions(chunk.text)
    save_to_db(questions)
    # 區塊處理完自動釋放記憶體
```

##### `process_with_callback(pdf_path: str, callback: Callable, start_page: int = 1, end_page: Optional[int] = None) -> List[Any]`

使用回調函數處理 PDF。

**參數:**
- `pdf_path` (str): PDF 文件路徑
- `callback` (Callable): 處理回調函數
- `start_page` (int, optional): 起始頁碼
- `end_page` (int, optional): 結束頁碼

**返回:**
- `List[Any]`: 處理結果列表

**示例:**
```python
def process_chunk(chunk):
    return extract_questions(chunk.text)

results = processor.process_with_callback("exam.pdf", process_chunk)
```

---

### PerformanceMonitor

性能監控器，提供完整的性能監控和分析。

#### 類定義

```python
from src.utils.performance_monitor import PerformanceMonitor

monitor = PerformanceMonitor()
```

#### 裝飾器用法

##### `@monitor.monitor(log_result: bool = True, track_memory: bool = True, track_cpu: bool = True)`

性能監控裝飾器。

**參數:**
- `log_result` (bool): 是否記錄結果，默認 True
- `track_memory` (bool): 是否追蹤記憶體，默認 True
- `track_cpu` (bool): 是否追蹤 CPU，默認 True

**示例:**
```python
monitor = PerformanceMonitor()

@monitor.monitor()
def process_file(file_path):
    # 處理邏輯
    pass

process_file("test.pdf")

# 查看統計
stats = monitor.get_function_stats("process_file")
print(f"平均耗時: {stats['avg_time']:.4f}秒")
```

#### 方法

##### `get_function_stats(function_name: str) -> Dict[str, Any]`

獲取函數統計信息。

**返回字段:**
- `function_name`: 函數名稱
- `call_count`: 調用次數
- `total_time`: 總耗時
- `avg_time`: 平均耗時
- `min_time`: 最短耗時
- `max_time`: 最長耗時

##### `generate_report(output_file: Optional[str] = None) -> str`

生成性能報告。

**參數:**
- `output_file` (str, optional): 輸出文件路徑

**返回:**
- `str`: 報告內容

**示例:**
```python
report = monitor.generate_report("performance_report.txt")
print(report)
```

##### `export_metrics(output_file: str)`

導出性能指標到 JSON 文件。

**參數:**
- `output_file` (str): 輸出文件路徑

**示例:**
```python
monitor.export_metrics("performance_metrics.json")
```

---

### PerformanceTimer

性能計時器，上下文管理器形式的計時工具。

#### 用法

```python
from src.utils.performance_monitor import PerformanceTimer

with PerformanceTimer("處理PDF") as timer:
    # 執行操作
    process_pdf()

print(timer.get_summary())
# 輸出: 處理PDF: 2.3456秒, 記憶體變化: +15.23MB
```

#### 方法

##### `get_duration() -> float`

獲取持續時間（秒）。

##### `get_memory_delta() -> float`

獲取記憶體變化（MB）。

##### `get_summary() -> str`

獲取摘要信息。

---

### RetryHandler

錯誤恢復處理器，自動重試和斷點續傳。

#### 裝飾器用法

```python
from src.utils.retry_handler import retry_with_backoff

@retry_with_backoff(
    max_retries=3,
    initial_delay=1.0,
    exponential=True,
    exceptions=(IOError, ConnectionError)
)
def process_file(file_path):
    # 可能失敗的操作
    pass
```

**參數:**
- `max_retries` (int): 最大重試次數，默認 3
- `initial_delay` (float): 初始延遲（秒），默認 1.0
- `exponential` (bool): 是否使用指數退避，默認 True
- `exceptions` (Tuple): 要捕獲的異常類型

#### CheckpointManager

斷點管理器。

```python
from src.utils.retry_handler import CheckpointManager

checkpoint = CheckpointManager("process_checkpoint.json")

# 保存檢查點
checkpoint.save_checkpoint({
    'completed_tasks': [1, 2, 3],
    'current_task': 4
})

# 載入檢查點
data = checkpoint.load_checkpoint()
if data:
    print(f"從任務 {data['current_task']} 繼續")
```

---

### YAMLConfigManager

YAML 配置管理器。

#### 用法

```python
from src.utils.yaml_config import load_config

# 載入配置
config = load_config('config.yaml')

# 訪問配置
dpi = config.ocr.pdf_to_image_dpi
max_workers = config.concurrent.max_workers
```

#### 環境變數覆蓋

使用環境變數覆蓋配置：

```bash
# 格式: APP_SECTION_KEY=value
export APP_OCR_PDF_TO_IMAGE_DPI=400
export APP_CONCURRENT_MAX_WORKERS=8
```

---

## 處理器模塊 API

### 處理器層次結構

```
ArchaeologyProcessor (主處理器)
├── PDFProcessor (PDF 處理)
├── QuestionParser (題目解析)
├── AnswerProcessor (答案處理)
└── ScanTracker (掃描追蹤)
```

### 完整處理流程

```python
from src.processors.archaeology_processor import ArchaeologyProcessor

# 創建處理器
processor = ArchaeologyProcessor()

# 處理單個 PDF
result = processor.process_pdf(
    pdf_path="exam_questions.pdf",
    answer_pdf_path="exam_answers.pdf",
    corrected_answer_pdf_path="corrected_answers.pdf",
    output_dir="output"
)

# 查看結果
print(f"題目數量: {result['question_count']}")
print(f"掃描覆蓋率: {result['scan_coverage']}%")
print(f"輸出文件: {result['output_file']}")
```

---

## 快速開始

### 安裝依賴

```bash
pip install -r requirements.txt
```

### 基本使用

#### 1. 處理單個 PDF

```python
from src.processors.archaeology_processor import ArchaeologyProcessor

processor = ArchaeologyProcessor()
result = processor.process_pdf("exam.pdf")
```

#### 2. 批量處理

```python
from src.utils.concurrent_processor import ConcurrentProcessor, ProcessingTask

def process_pdf(task):
    processor = ArchaeologyProcessor()
    return processor.process_pdf(task.pdf_path)

tasks = [
    ProcessingTask(task_id=1, pdf_path="exam1.pdf"),
    ProcessingTask(task_id=2, pdf_path="exam2.pdf"),
]

concurrent = ConcurrentProcessor(max_workers=4)
results = concurrent.process_batch(tasks, process_pdf)
```

#### 3. 流式處理大文件

```python
from src.utils.streaming_processor import StreamingPDFProcessor

processor = StreamingPDFProcessor()

for chunk in processor.stream_pages("large_exam.pdf"):
    # 處理每個區塊
    process_chunk(chunk.text)
```

#### 4. 性能監控

```python
from src.utils.performance_monitor import monitor_performance

@monitor_performance
def process_file(file_path):
    # 處理邏輯
    pass

# 自動記錄性能
process_file("exam.pdf")
```

---

## 常見用例

### 用例 1: 完整的考古題處理流程

```python
from src.processors.archaeology_processor import ArchaeologyProcessor
from src.utils.performance_monitor import monitor_performance
from src.utils.retry_handler import retry_with_backoff

@monitor_performance
@retry_with_backoff(max_retries=3)
def process_exam(pdf_path, answer_path):
    processor = ArchaeologyProcessor()
    return processor.process_pdf(
        pdf_path=pdf_path,
        answer_pdf_path=answer_path,
        output_dir="output"
    )

# 處理
result = process_exam("exam.pdf", "answers.pdf")
```

### 用例 2: 批量處理 + 錯誤恢復

```python
from src.utils.concurrent_processor import ConcurrentProcessor
from src.utils.retry_handler import CheckpointManager, ErrorRecovery

# 設置斷點管理
checkpoint = CheckpointManager("batch_checkpoint.json")

# 載入進度
data = checkpoint.load_checkpoint()
completed = data.get('completed', []) if data else []

# 過濾已完成的任務
tasks = [t for t in all_tasks if t.task_id not in completed]

# 並發處理
processor = ConcurrentProcessor(max_workers=4)
results = processor.process_batch(tasks, process_func)

# 更新檢查點
completed.extend([r.task_id for r in results if r.success])
checkpoint.save_checkpoint({'completed': completed})
```

### 用例 3: 記憶體高效處理 + 性能監控

```python
from src.utils.streaming_processor import StreamingPDFProcessor
from src.utils.performance_monitor import PerformanceTimer

processor = StreamingPDFProcessor()

with PerformanceTimer("完整處理") as timer:
    for chunk in processor.stream_pages("huge_exam.pdf"):
        # 處理區塊
        questions = extract_questions(chunk.text)
        save_to_db(questions)

print(timer.get_summary())
```

### 用例 4: 自定義配置

```python
from src.utils.yaml_config import load_config
from src.processors.archaeology_processor import ArchaeologyProcessor

# 載入自定義配置
config = load_config('custom_config.yaml')

# 使用配置
processor = ArchaeologyProcessor()
processor.config = config

# 處理
result = processor.process_pdf("exam.pdf")
```

---

## 異常處理

### 常見異常

| 異常類型 | 說明 | 處理方式 |
|---------|------|---------|
| `PDFProcessingError` | PDF 處理失敗 | 檢查文件路徑和格式 |
| `QuestionParsingError` | 題目解析失敗 | 檢查文字格式 |
| `ConfigurationError` | 配置錯誤 | 檢查配置文件 |

### 示例

```python
from src.utils.exceptions import PDFProcessingError

try:
    text = processor.extract_text("exam.pdf")
except PDFProcessingError as e:
    print(f"處理失敗: {e}")
    # 錯誤處理邏輯
```

---

## 最佳實踐

### 1. 使用並發處理提高效率

```python
# ✅ 好
concurrent = ConcurrentProcessor(max_workers=4)
results = concurrent.process_batch(tasks, process_func)

# ❌ 避免
for task in tasks:
    result = process_func(task)  # 串行處理
```

### 2. 處理大文件使用流式處理

```python
# ✅ 好 - 記憶體穩定
for chunk in processor.stream_pages("large.pdf"):
    process(chunk)

# ❌ 避免 - 記憶體爆炸
text = processor.extract_text("large.pdf")  # 一次性載入
```

### 3. 啟用性能監控

```python
# ✅ 好 - 可觀測
@monitor_performance
def critical_function():
    pass

# ❌ 避免 - 無法追蹤性能
def critical_function():
    pass
```

### 4. 使用自動重試

```python
# ✅ 好 - 自動恢復
@retry_with_backoff(max_retries=3)
def process_file(path):
    pass

# ❌ 避免 - 手動重試
def process_file(path):
    for i in range(3):
        try:
            # 處理
            break
        except:
            continue
```

---

## 版本歷史

| 版本 | 日期 | 更新內容 |
|-----|------|---------|
| 1.0 | 2025-11-17 | 初始版本，完整 API 文檔 |

---

## 相關資源

- [改進總結報告](../IMPROVEMENTS_SUMMARY.md)
- [測試覆蓋報告](TEST_COVERAGE_REPORT.md)
- [快速開始指南](QUICK_START.md)
- [貢獻指南](CONTRIBUTING.md)

---

**文檔完成**
如有問題或建議，請提交 Issue。
