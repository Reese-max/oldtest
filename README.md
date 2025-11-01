# 考古題處理系統

## 🎯 專案概述

這是一個完整的PDF考古題轉換系統，可以將PDF格式的考古題轉換為Google表單，方便線上練習。系統採用模組化設計，具有清晰的架構和統一的接口。

## ✨ 主要特色

- **PDF解析**: 自動從PDF中提取題目和選項
- **答案處理**: 支援正確答案和更正答案
- **Google表單生成**: 自動生成Google Apps Script代碼
- **自動評分**: 內建自動評分和結果記錄功能
- **分類標籤**: 自動為題目添加分類和難度標籤
- **模組化架構**: 清晰的代碼結構，易於維護和擴展
- **統一配置**: 集中管理所有配置參數
- **結構化日誌**: 完整的日誌記錄和錯誤追蹤
- **類型提示**: 完整的Python類型註解
- **單元測試**: 全面的測試覆蓋
- **命令行接口**: 易用的命令行工具
- **API接口**: 可程式化調用的API

## 📁 專案結構

```
/workspace/
├── src/                          # 主要源代碼
│   ├── __init__.py
│   ├── api.py                    # 主要API接口
│   ├── core/                     # 核心模組
│   │   ├── __init__.py
│   │   ├── pdf_processor.py      # PDF處理器
│   │   ├── question_parser.py    # 題目解析器
│   │   ├── answer_processor.py   # 答案處理器
│   │   ├── csv_generator.py      # CSV生成器
│   │   └── google_script_generator.py  # Google Script生成器
│   ├── processors/               # 處理器模組
│   │   ├── __init__.py
│   │   └── archaeology_processor.py    # 考古題處理器
│   └── utils/                    # 工具模組
│       ├── __init__.py
│       ├── logger.py             # 日誌系統
│       ├── config.py             # 配置管理
│       ├── exceptions.py         # 自定義異常
│       └── quality_validator.py  # 資料品質驗證
├── tests/                        # 測試模組
│   ├── __init__.py
│   ├── test_core.py              # 核心功能測試
│   └── test_integration.py       # 整合測試
├── main.py                       # 主程序入口
├── config.json                   # 配置文件
├── requirements.txt              # 依賴清單
└── README.md                     # 本文檔
```

## 🚀 快速開始

### 1. 安裝依賴

```bash
pip install -r requirements.txt
```

### 2. 基本使用

#### 處理單一PDF檔案

```bash
python main.py input.pdf -o output_dir
```

#### 處理目錄中的所有PDF

```bash
python main.py input_directory -o output_dir
```

#### 包含答案檔案

```bash
python main.py input.pdf -a answer.pdf -c corrected.pdf -o output_dir
```

#### 不生成Google Apps Script

```bash
python main.py input.pdf -o output_dir --no-script
```

### 3. 程式化使用

```python
from src.api import ArchaeologyAPI

# 創建API實例
api = ArchaeologyAPI()

# 處理單一PDF
result = api.process_single_pdf(
    pdf_path="input.pdf",
    answer_pdf_path="answer.pdf",
    output_dir="output"
)

if result['success']:
    print(f"處理成功！生成了 {len(result['csv_files'])} 個CSV檔案")
else:
    print(f"處理失敗：{result['message']}")
```

## ⚙️ 配置說明

系統使用 `config.json` 檔案進行配置：

```json
{
  "processing": {
    "max_text_length": 1000000,
    "min_question_length": 10,
    "max_question_length": 1000,
    "ai_model": "gemini-1.5-flash",
    "ai_temperature": 0.1,
    "ai_max_tokens": 4000,
    "output_encoding": "utf-8-sig",
    "csv_delimiter": ","
  },
  "google_form": {
    "form_title": "考古題練習表單",
    "form_description": "此表單包含 {total_questions} 題考古題，用於練習和自測",
    "collect_email": true,
    "require_login": false,
    "enable_auto_scoring": true,
    "show_answers_after_submit": true,
    "default_question_type": "選擇題",
    "enable_question_groups": true
  }
}
```

配置驗證會在啟動時自動執行，確保所有參數符合要求。

## 📊 CSV格式

生成的CSV檔案包含以下欄位：

| 欄位 | 說明 |
|------|------|
| 題號 | 題目編號 |
| 題目 | 題目內容 |
| 題型 | 選擇題/問答題 |
| 選項A-D | 四個選項 |
| 正確答案 | 原始正確答案 |
| 更正答案 | 更正後的答案 |
| 最終答案 | 最終使用的答案 |
| 難度 | 簡單/中等/困難 |
| 分類 | 題目分類 |
| 備註 | 額外說明 |

## 🧪 測試

### 運行所有測試

```bash
python -m pytest tests/
```

### 運行特定測試

```bash
python -m pytest tests/test_core.py
python -m pytest tests/test_integration.py
```

### 測試覆蓋率

```bash
python -m pytest --cov=src tests/
```

## 📊 功能模組

### 1. PDF處理器 (`PDFProcessor`)

- 從PDF檔案提取文字內容
- 支援指定頁面提取
- 錯誤處理和日誌記錄

### 2. 題目解析器 (`QuestionParser`)

- 解析一般題目和題組
- 自動檢測題組模式
- 提取選項內容
- 題目驗證

### 3. 答案處理器 (`AnswerProcessor`)

- 提取原始答案和更正答案
- 合併答案（優先使用更正答案）
- 答案格式驗證
- 答案統計

### 4. CSV生成器 (`CSVGenerator`)

- 生成一般CSV檔案
- 生成Google表單專用CSV
- 題組分類CSV
- 題目難度和分類

### 5. Google Script生成器 (`GoogleScriptGenerator`)

- 生成Google Apps Script代碼
- 自動評分功能
- 表單設定和樣式

## 🔧 開發指南

### 添加新功能

1. 在相應的模組中添加新類別或方法
2. 添加對應的單元測試
3. 更新API接口（如需要）
4. 更新文檔

### 代碼規範

- 使用Python類型註解
- 遵循PEP 8代碼風格
- 添加適當的docstring
- 使用統一的日誌系統
- 使用自定義異常類別處理錯誤

### 錯誤處理

系統使用統一的異常處理機制：

- `PDFProcessingError`: PDF處理相關錯誤
- `QuestionParsingError`: 題目解析錯誤
- `AnswerProcessingError`: 答案處理錯誤
- `CSVGenerationError`: CSV生成錯誤
- `GoogleFormError`: Google表單處理錯誤
- `ConfigurationError`: 配置錯誤
- `ValidationError`: 驗證錯誤

所有異常都會記錄詳細的日誌資訊。

## 📈 性能優化

### 已實現的優化

- 模組化設計減少內存使用
- 統一的日誌系統避免重複輸出
- 配置管理避免硬編碼
- 類型提示提升開發效率
- 配置驗證確保參數正確性

### 未來優化方向

- 並行處理多個PDF檔案
- 快取機制減少重複處理
- 異步處理提升響應速度

## 🐛 故障排除

### 常見問題

1. **PDF無法解析**
   - 檢查PDF是否為掃描版
   - 確認PDF檔案完整性

2. **題目解析失敗**
   - 檢查PDF文字提取是否正確
   - 調整解析模式

3. **答案提取錯誤**
   - 確認答案格式符合預期
   - 檢查正則表達式模式

4. **配置錯誤**
   - 檢查 `config.json` 格式是否正確
   - 確認所有必填參數都已設定

### 日誌查看

系統會自動生成日誌檔案：

```
logs/
└── archaeology_questions_YYYYMMDD.log
```

## 📝 更新日誌

### v2.0.0 (2024-01-15)

- 完全重構代碼架構
- 實現模組化設計
- 添加統一的日誌和配置系統
- 建立完整的測試框架
- 提供API接口和命令行工具
- 消除代碼重複和命名混亂
- 增強類型提示和錯誤處理
- 增加配置驗證機制

## 📄 授權

此專案僅供學習和個人使用。

---

**開發者**: AI Assistant  
**版本**: 2.0.0  
**更新日期**: 2024年1月15日
