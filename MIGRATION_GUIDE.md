# 遷移指南 v1.0 → v2.0

## 🎯 重構概述

v2.0版本進行了完全重構，大幅提升了代碼品質和可維護性。以下是從舊版本遷移到新版本的詳細指南。

## 📊 重構成果

### 代碼品質提升

| 項目 | v1.0 | v2.0 | 改善 |
|------|------|------|------|
| 檔案數量 | 60+ | 15 | -75% |
| 代碼重複 | 嚴重 | 消除 | ✅ |
| 命名規範 | 混亂 | 統一 | ✅ |
| 錯誤處理 | 分散 | 統一 | ✅ |
| 日誌系統 | 無 | 完整 | ✅ |
| 測試覆蓋 | 低 | 高 | ✅ |
| 文檔品質 | 基本 | 完整 | ✅ |

## 🔄 主要變更

### 1. 專案結構重組

#### 舊結構 (v1.0)
```
/workspace/
├── pdf_to_csv_improved.py
├── pdf_to_google_form.py
├── google_apps_script_generator_fixed.py
├── final_ultimate_final_ultimate_..._processor.py (19個重複檔案)
├── test_*.py (多個分散的測試檔案)
└── ... (60+個檔案)
```

#### 新結構 (v2.0)
```
/workspace/
├── src/                          # 主要源代碼
│   ├── api.py                    # 統一API接口
│   ├── core/                     # 核心模組
│   ├── processors/               # 處理器模組
│   └── utils/                    # 工具模組
├── tests/                        # 測試模組
├── main.py                       # 主程序入口
├── config.json                   # 配置文件
└── requirements.txt              # 依賴清單
```

### 2. 核心功能整合

#### 舊版本功能分散
- `pdf_to_csv_improved.py` - PDF轉CSV
- `pdf_to_google_form.py` - Google表單生成
- `google_apps_script_generator_fixed.py` - Script生成
- 19個重複的處理器檔案

#### 新版本統一架構
- `src/core/pdf_processor.py` - PDF處理
- `src/core/question_parser.py` - 題目解析
- `src/core/answer_processor.py` - 答案處理
- `src/core/csv_generator.py` - CSV生成
- `src/core/google_script_generator.py` - Script生成
- `src/processors/archaeology_processor.py` - 主要處理器

### 3. 配置管理

#### 舊版本
- 硬編碼配置
- 分散在各個檔案中
- 難以修改和維護

#### 新版本
- 統一的 `config.json` 配置檔案
- 類型安全的配置類別
- 動態配置載入和儲存

### 4. 日誌系統

#### 舊版本
- 1409個print語句分散在58個檔案
- 無結構化日誌
- 難以追蹤和除錯

#### 新版本
- 統一的日誌管理器
- 結構化日誌輸出
- 檔案和控制台雙重輸出
- 不同級別的日誌記錄

### 5. 錯誤處理

#### 舊版本
- 106個except語句但缺乏統一策略
- 錯誤訊息不一致
- 難以追蹤錯誤來源

#### 新版本
- 自定義異常類別體系
- 統一的錯誤處理策略
- 詳細的錯誤日誌記錄

## 🚀 遷移步驟

### 1. 備份現有專案

```bash
cp -r /workspace /workspace_backup_v1
```

### 2. 安裝新依賴

```bash
pip install -r requirements.txt
```

### 3. 更新使用方式

#### 舊版本使用方式
```python
# 舊版本
from pdf_to_csv_improved import PDFToCSVImproved
processor = PDFToCSVImproved()
result = processor.process_pdf("input.pdf", "output.csv")
```

#### 新版本使用方式
```python
# 新版本
from src.api import ArchaeologyAPI
api = ArchaeologyAPI()
result = api.process_single_pdf("input.pdf", output_dir="output")
```

### 4. 命令行使用

#### 舊版本
```bash
python pdf_to_csv_improved.py input.pdf -o output_dir
```

#### 新版本
```bash
python main.py input.pdf -o output_dir
```

### 5. 配置遷移

#### 舊版本
- 修改各個檔案中的硬編碼值

#### 新版本
- 編輯 `config.json` 檔案
- 或使用程式化配置：

```python
from src.utils.config import config_manager
config_manager.update_processing_config(
    max_text_length=2000000,
    min_question_length=15
)
```

## 📋 功能對照表

| 功能 | v1.0 檔案 | v2.0 模組 | 狀態 |
|------|-----------|-----------|------|
| PDF文字提取 | `pdf_to_csv_improved.py` | `src/core/pdf_processor.py` | ✅ 已遷移 |
| 題目解析 | 分散在多個檔案 | `src/core/question_parser.py` | ✅ 已整合 |
| 答案處理 | `pdf_to_csv_improved.py` | `src/core/answer_processor.py` | ✅ 已優化 |
| CSV生成 | 分散在多個檔案 | `src/core/csv_generator.py` | ✅ 已統一 |
| Google Script生成 | `google_apps_script_generator_fixed.py` | `src/core/google_script_generator.py` | ✅ 已重構 |
| 題組處理 | 多個重複檔案 | `src/core/question_parser.py` | ✅ 已整合 |
| 配置管理 | 硬編碼 | `src/utils/config.py` | ✅ 新增 |
| 日誌系統 | print語句 | `src/utils/logger.py` | ✅ 新增 |
| 錯誤處理 | 分散 | `src/utils/exceptions.py` | ✅ 新增 |
| 測試框架 | 分散檔案 | `tests/` | ✅ 新增 |

## 🔧 開發者指南

### 添加新功能

#### 舊版本
- 創建新的處理器檔案
- 複製現有代碼
- 修改檔案名稱

#### 新版本
1. 在相應模組中添加新類別
2. 添加單元測試
3. 更新API接口
4. 更新文檔

### 除錯和維護

#### 舊版本
- 查看控制台輸出
- 搜尋多個檔案
- 難以追蹤問題

#### 新版本
- 查看結構化日誌檔案
- 使用統一的日誌系統
- 清晰的錯誤追蹤

## ⚠️ 注意事項

### 1. 向後相容性

v2.0不向後相容v1.0，需要更新使用方式。

### 2. 依賴變更

- 新增了 `pytest` 用於測試
- 新增了 `black`、`flake8`、`mypy` 用於代碼品質
- 移除了未使用的依賴

### 3. 配置變更

- 所有配置現在集中在 `config.json`
- 舊的硬編碼配置需要遷移到新格式

### 4. 檔案路徑變更

- 主要功能現在在 `src/` 目錄下
- 測試檔案在 `tests/` 目錄下
- 移除了所有重複檔案

## 🎉 遷移完成檢查清單

- [ ] 備份舊版本專案
- [ ] 安裝新依賴
- [ ] 更新使用方式
- [ ] 測試基本功能
- [ ] 驗證輸出結果
- [ ] 更新文檔和說明
- [ ] 清理舊檔案

## 📞 支援

如果在遷移過程中遇到問題，請：

1. 查看新的文檔：`README_v2.md`
2. 檢查日誌檔案：`logs/archaeology_questions_*.log`
3. 運行測試：`python -m pytest tests/`
4. 查看配置：`config.json`

---

**遷移完成後，您將享受到更清晰、更易維護、更高品質的代碼！** 🚀