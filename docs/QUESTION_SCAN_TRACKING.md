# 題目掃描追蹤系統使用指南

## 📋 系統概述

題目掃描追蹤系統（Question Scan Tracking System）確保每一題都被正確掃描和記錄，絕不遺漏任何題目。

### 核心功能

1. **✅ 題目掃描記錄** - 記錄每一題的掃描狀態
2. **🔍 完整性驗證** - 自動檢測遺漏題號
3. **📊 詳細報告** - 生成完整的掃描分析報告
4. **⚠️ 重複檢測** - 識別重複掃描的題目
5. **🔧 解析器追蹤** - 記錄每題使用的解析器
6. **📝 掃描日誌** - 詳細的掃描過程記錄

---

## 🚀 快速開始

### 基本使用

```python
from src.processors.archaeology_processor import ArchaeologyProcessor

# 創建處理器
processor = ArchaeologyProcessor(use_enhanced=True)

# 處理 PDF（自動啟用掃描追蹤）
result = processor.process_pdf(
    pdf_path="exam.pdf",
    output_dir="output"
)

# 檢查掃描結果
if result['scan_complete']:
    print(f"✅ 所有題目掃描完成！共 {result['questions_count']} 題")
else:
    print(f"⚠️ 有題目遺漏:")
    print(f"   遺漏題號: {result['missing_questions']}")
```

### 查看掃描報告

掃描完成後，會自動生成詳細報告：

```
output/exam_scan_report.json
```

---

## 📊 掃描報告詳解

### 報告結構

```json
{
  "scan_summary": {
    "total_scanned": 50,        // 成功掃描的題數
    "expected_count": 50,        // 預期題數
    "question_range": "1 ~ 50",  // 題號範圍
    "is_complete": true,         // 是否完整
    "missing_count": 0,          // 遺漏題數
    "duplicate_count": 0,        // 重複題數
    "scan_duration": 2.35        // 掃描耗時（秒）
  },
  "missing_questions": [],       // 遺漏的題號列表
  "duplicate_questions": [],     // 重複的題號列表
  "parser_statistics": {         // 解析器統計
    "UltimateParser": 40,
    "StandardParser": 10
  },
  "parsers_used": [              // 使用的解析器列表
    "UltimateParser",
    "StandardParser"
  ],
  "question_details": {          // 每題詳細資訊
    "1": {
      "question_num": 1,
      "scanned": true,
      "parser_used": "UltimateParser",
      "scan_time": "2025-11-17T05:30:00",
      "content_preview": "下列何者為正確答案？",
      "scan_attempts": [
        {
          "parser": "UltimateParser",
          "time": "2025-11-17T05:30:00",
          "success": true
        }
      ],
      "warnings": []
    }
  }
}
```

### 日誌輸出示例

```
2025-11-17 05:30:00 - INFO - 📊 開始題目掃描追蹤（預期題數: 50）
2025-11-17 05:30:01 - INFO - 检测到格式类型: comprehensive
2025-11-17 05:30:02 - INFO - ============================================================
2025-11-17 05:30:02 - INFO - 📊 題目掃描完整性報告
2025-11-17 05:30:02 - INFO - ============================================================
2025-11-17 05:30:02 - INFO - ✅ 成功掃描: 50 題
2025-11-17 05:30:02 - INFO - 📝 題號範圍: 1 ~ 50
2025-11-17 05:30:02 - INFO - ✅ 題號連續，無遺漏
2025-11-17 05:30:02 - INFO - 🔧 使用的解析器:
2025-11-17 05:30:02 - INFO -    - UltimateParser: 40 題
2025-11-17 05:30:02 - INFO -    - StandardParser: 10 題
2025-11-17 05:30:02 - INFO - ⏱️  掃描耗時: 2.35 秒
2025-11-17 05:30:02 - INFO - ============================================================
```

---

## 🔍 完整性檢查

### 自動檢測

系統會自動檢測以下問題：

#### 1. **遺漏題號**

```python
# 示例：掃描到 1, 2, 4, 5（缺少 3）
# 日誌輸出：
❌ 遺漏題號: [3]
   共遺漏 1 題
```

#### 2. **重複掃描**

```python
# 示例：題號 5 被掃描兩次
# 日誌輸出：
⚠️  重複掃描: 第5題 (已由 UltimateParser 掃描)
```

#### 3. **題號不連續**

```python
# 示例：掃描到 1, 3, 5, 8
# 系統會檢測並報告遺漏的題號 [2, 4, 6, 7]
```

### 手動驗證

```python
from src.utils.question_scan_tracker import QuestionScanTracker

# 創建追蹤器
tracker = QuestionScanTracker(expected_count=50)

# 驗證題目列表
questions = [{'題號': i, '題目': f'問題{i}'} for i in range(1, 51)]
is_complete, message = tracker.validate_questions(questions)

if is_complete:
    print(f"✅ {message}")
else:
    print(f"❌ {message}")
```

---

## 📝 API 參考

### QuestionScanTracker 類

#### 初始化

```python
tracker = QuestionScanTracker(expected_count=50)
```

**參數:**
- `expected_count` (int, 可選): 預期題目數量

#### 主要方法

##### start_scan()
開始掃描追蹤

```python
tracker.start_scan(expected_count=60)
```

##### register_question()
註冊已掃描的題目

```python
tracker.register_question(
    question_num=1,          # 題號
    parser_name="Parser1",   # 解析器名稱
    content="題目內容"        # 題目內容預覽
)
```

##### record_attempt()
記錄掃描嘗試（包括失敗的）

```python
tracker.record_attempt(
    question_num=1,
    parser_name="Parser1",
    success=False,
    error="格式不匹配"
)
```

##### add_warning()
添加題目警告

```python
tracker.add_warning(
    question_num=1,
    message="題目內容過短"
)
```

##### end_scan()
結束掃描並生成報告

```python
report = tracker.end_scan()
```

**返回:** 完整的掃描報告字典

##### validate_questions()
驗證題目列表完整性

```python
is_complete, message = tracker.validate_questions(questions)
```

**參數:**
- `questions` (List[Dict]): 題目列表

**返回:** (是否完整, 驗證訊息)

##### save_report()
保存掃描報告到文件

```python
tracker.save_report("scan_report.json")
```

##### 輔助方法

```python
# 獲取遺漏的題號列表
missing = tracker.get_missing_questions()

# 檢查是否完整（無遺漏）
is_complete = tracker.is_complete()

# 獲取成功掃描的題目數量
count = tracker.get_scanned_count()

# 生成報告
report = tracker.generate_report()
```

---

## 🎯 使用場景

### 場景 1: 確保考卷完整掃描

```python
# 處理考卷 PDF
result = processor.process_pdf("exam_2024.pdf")

# 檢查完整性
if not result['scan_complete']:
    # 發出警告並記錄遺漏題號
    print(f"警告：考卷掃描不完整！")
    print(f"遺漏題號：{result['missing_questions']}")

    # 可以嘗試使用其他解析器重新掃描
```

### 場景 2: 批量處理多個文件

```python
import os

pdf_files = ["exam1.pdf", "exam2.pdf", "exam3.pdf"]
incomplete_files = []

for pdf_file in pdf_files:
    result = processor.process_pdf(pdf_file)

    if not result['scan_complete']:
        incomplete_files.append({
            'file': pdf_file,
            'missing': result['missing_questions']
        })

# 報告不完整的文件
if incomplete_files:
    print("以下文件掃描不完整：")
    for item in incomplete_files:
        print(f"  {item['file']}: 遺漏 {item['missing']}")
```

### 場景 3: 自定義掃描追蹤

```python
from src.utils.question_scan_tracker import QuestionScanTracker

# 創建自定義追蹤器
tracker = QuestionScanTracker(expected_count=60)
tracker.start_scan()

# 手動註冊題目
for question in my_questions:
    tracker.register_question(
        question_num=question['num'],
        parser_name="CustomParser",
        content=question['text']
    )

# 生成報告
report = tracker.end_scan()

# 檢查結果
if tracker.is_complete():
    print("✅ 所有題目已掃描")
else:
    print(f"❌ 遺漏題號: {tracker.get_missing_questions()}")
```

---

## ⚙️ 配置選項

### 在 ArchaeologyProcessor 中的配置

掃描追蹤系統會自動在 `process_pdf()` 方法中啟用。報告會保存到輸出目錄：

```
output/
├── exam.csv
├── exam_google.csv
├── exam_scan_report.json  ← 掃描報告
└── ...
```

### 自定義報告位置

如果需要自定義報告保存位置，可以在處理後手動保存：

```python
result = processor.process_pdf("exam.pdf")

# 獲取掃描追蹤器
tracker = processor.scan_tracker

# 保存到自定義位置
tracker.save_report("custom/path/report.json")
```

---

## 🔧 故障排除

### 問題 1: 掃描報告顯示遺漏題號

**可能原因:**
1. PDF 格式不標準，部分題目無法識別
2. 題號編碼問題（如使用特殊符號）
3. 題目內容過短被過濾

**解決方法:**
1. 檢查原始 PDF 文件
2. 嘗試使用不同的解析器
3. 查看掃描報告中的 `question_details` 了解詳情

### 問題 2: 重複掃描警告

**可能原因:**
- 同一題被多個解析器識別

**說明:**
- 這通常不是問題，系統會保留第一次掃描的結果
- 在報告中會記錄重複題號

### 問題 3: 掃描耗時過長

**可能原因:**
- PDF 文件過大
- 使用了多個解析器

**優化建議:**
1. 使用 `use_enhanced=True` 啟用增強模式
2. 對於標準格式考卷，可以只使用標準解析器

---

## 📊 性能指標

### 掃描速度

- 標準題目（50 題）: ~0.5-2 秒
- 綜合題目（60 題）: ~2-5 秒
- 申論題: ~1-3 秒

### 記憶體使用

- 基本掃描追蹤: ~1-2 MB
- 詳細報告: +0.5 MB per 50 questions

---

## 📚 最佳實踐

### 1. 總是檢查完整性

```python
result = processor.process_pdf("exam.pdf")

if result['scan_complete']:
    print("✅ 掃描完成，可以繼續處理")
else:
    print("⚠️ 掃描不完整，需要人工檢查")
    # 記錄到日誌或發送通知
```

### 2. 保存掃描報告

```python
# 掃描報告對於追蹤和調試非常有用
# 建議總是保存報告供後續分析
processor.scan_tracker.save_report(f"reports/{date}_scan.json")
```

### 3. 批量處理時的監控

```python
results = []
for pdf in pdf_files:
    result = processor.process_pdf(pdf)
    results.append({
        'file': pdf,
        'complete': result['scan_complete'],
        'count': result['questions_count'],
        'missing': result['missing_questions']
    })

# 生成批量處理報告
with open('batch_report.json', 'w') as f:
    json.dump(results, f, indent=2)
```

---

## 🎓 進階用法

### 自定義驗證規則

```python
class CustomValidator:
    def __init__(self, tracker):
        self.tracker = tracker

    def validate_with_custom_rules(self, questions):
        # 基本驗證
        is_complete, msg = self.tracker.validate_questions(questions)

        if not is_complete:
            return False, msg

        # 自定義規則：檢查題目內容長度
        for q in questions:
            if len(q.get('題目', '')) < 10:
                return False, f"題號 {q['題號']} 內容過短"

        return True, "驗證通過"
```

### 整合到 CI/CD 流程

```python
import sys

# 在 CI/CD 中使用
result = processor.process_pdf("exam.pdf")

if not result['scan_complete']:
    print(f"ERROR: Incomplete scan - missing questions: {result['missing_questions']}")
    sys.exit(1)  # 失敗退出

print(f"SUCCESS: All {result['questions_count']} questions scanned")
sys.exit(0)  # 成功退出
```

---

## 📖 相關文檔

- [題目解析器指南](QUESTION_PARSERS.md)
- [PDF 處理指南](PDF_PROCESSING.md)
- [API 參考文檔](API_REFERENCE.md)

---

## 🤝 支援

如有問題或建議，請聯繫開發團隊或提交 Issue。

---

**版本:** 1.0.0
**最後更新:** 2025-11-17
**作者:** Claude AI
