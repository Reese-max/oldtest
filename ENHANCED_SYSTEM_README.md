# 增強版考古題處理系統

## 概述

本系統是對原有考古題處理系統的全面優化和功能強化，主要針對題組選取和現有功能進行了大幅改進。系統提供了更精確的題組檢測、更強大的選項提取、更智能的題目解析，以及全面的驗證和性能優化功能。

## 主要改進

### 1. 題組檢測優化
- **增強版題組處理器** (`enhanced_question_group_processor.py`)
  - 支援8種不同的題組檢測模式
  - 智能合併重疊題組
  - 信心度評估機制
  - 更精確的內容邊界檢測

### 2. 選項提取強化
- **增強版選項提取器** (`enhanced_option_extractor.py`)
  - 支援7種不同的選項格式
  - 多種提取方法組合
  - 語義分析支援
  - 選項品質評估

### 3. 題目解析改進
- **增強版題目解析器** (`enhanced_question_parser.py`)
  - 6種題目檢測模式
  - 智能內容過濾
  - 題目指示詞檢測
  - 解析統計分析

### 4. 驗證機制
- **增強版驗證系統** (`enhanced_validation_system.py`)
  - 全面的題目驗證
  - 品質分數計算
  - 詳細驗證報告
  - 多層次驗證規則

### 5. 性能優化
- **性能優化器** (`performance_optimizer.py`)
  - 並行處理支援
  - 記憶體使用優化
  - 性能監控
  - 批次處理

### 6. 配置系統
- **增強版配置系統** (`enhanced_config_system.py`)
  - 豐富的配置選項
  - 動態配置管理
  - 配置驗證
  - 多格式支援

### 7. 測試套件
- **綜合測試套件** (`comprehensive_test_suite.py`)
  - 單元測試
  - 整合測試
  - 性能測試
  - 錯誤處理測試

## 安裝和使用

### 環境要求
```bash
pip install pdfplumber pandas pyyaml psutil
```

### 基本使用

#### 1. 處理單一PDF檔案
```python
from enhanced_archaeology_processor import EnhancedArchaeologyProcessor

# 創建處理器
processor = EnhancedArchaeologyProcessor()

# 處理PDF
result = processor.process_pdf('input.pdf', 'output', 'answer.pdf')

if result['success']:
    print(f"處理完成！生成了 {len(result['output_files'])} 個檔案")
    print(f"總題數: {result['total_questions']}")
    print(f"品質分數: {result['quality_score']:.2f}")
else:
    print(f"處理失敗: {result['error']}")
```

#### 2. 處理目錄中的所有PDF
```python
# 處理目錄
result = processor.process_directory('input_dir', 'output')

if result['success']:
    print(f"處理完成！成功處理 {result['successful_files']} 個檔案")
    print(f"失敗: {result['failed_files']} 個檔案")
```

#### 3. 命令行使用
```bash
# 處理單一檔案
python enhanced_archaeology_processor.py input.pdf -o output -a answer.pdf

# 處理目錄
python enhanced_archaeology_processor.py input_dir -o output

# 使用自定義配置
python enhanced_archaeology_processor.py input.pdf -o output -c config.json
```

### 配置選項

系統提供了豐富的配置選項，可以通過JSON或YAML檔案進行配置：

```json
{
  "system": {
    "debug": false,
    "log_level": "INFO",
    "max_workers": null,
    "memory_threshold": 0.8
  },
  "processing": {
    "max_text_length": 1000000,
    "min_question_length": 10,
    "max_question_length": 1000,
    "enable_parallel_processing": true,
    "batch_size": 100
  },
  "question_group": {
    "enable_detection": true,
    "max_questions_per_group": 20,
    "detection_confidence_threshold": 0.5
  },
  "validation": {
    "enable_validation": true,
    "strict_mode": false,
    "min_quality_score": 0.7
  }
}
```

## 輸出檔案

系統會生成多種格式的輸出檔案：

### 1. CSV檔案
- `{檔名}_一般題目.csv` - 一般題目
- `{檔名}_題組題目.csv` - 題組題目
- `{檔名}_完整題目.csv` - 所有題目
- `{檔名}_Google表單.csv` - Google表單格式

### 2. JSON檔案
- `{檔名}_題目資料.json` - 結構化題目資料

### 3. 報告檔案
- `{檔名}_驗證報告.md` - 詳細驗證報告
- `{檔名}_性能報告.json` - 性能統計報告

## 功能特色

### 1. 智能題組檢測
- 自動識別多種題組格式
- 智能合併重疊題組
- 信心度評估
- 內容邊界精確檢測

### 2. 多格式選項提取
- 括號格式: (A) 選項內容
- 全形格式: Ａ選項內容
- 半形格式: A選項內容
- 數字格式: 1. 選項內容
- 破折號格式: A - 選項內容

### 3. 智能題目解析
- 多種題目格式支援
- 內容過濾和清理
- 題目指示詞檢測
- 解析品質評估

### 4. 全面驗證機制
- 題目內容驗證
- 選項完整性檢查
- 品質分數計算
- 詳細錯誤報告

### 5. 性能優化
- 並行處理
- 記憶體優化
- 批次處理
- 性能監控

### 6. 靈活配置
- 豐富的配置選項
- 動態配置管理
- 配置驗證
- 多格式支援

## 測試

運行完整測試套件：

```bash
python comprehensive_test_suite.py
```

測試包括：
- 單元測試
- 整合測試
- 性能測試
- 錯誤處理測試

## 日誌記錄

系統提供詳細的日誌記錄：

- 控制台輸出
- 檔案記錄
- 可配置日誌級別
- 性能監控日誌

## 錯誤處理

系統具有完善的錯誤處理機制：

- 優雅的錯誤恢復
- 詳細的錯誤報告
- 日誌記錄
- 用戶友好的錯誤訊息

## 性能監控

系統提供實時性能監控：

- 處理時間統計
- 記憶體使用監控
- CPU使用率追蹤
- 性能報告生成

## 擴展性

系統設計具有良好的擴展性：

- 模組化架構
- 插件式設計
- 配置驅動
- 易於擴展

## 技術架構

```
enhanced_archaeology_processor.py (主處理器)
├── enhanced_question_group_processor.py (題組處理)
├── enhanced_option_extractor.py (選項提取)
├── enhanced_question_parser.py (題目解析)
├── enhanced_validation_system.py (驗證系統)
├── enhanced_config_system.py (配置系統)
├── performance_optimizer.py (性能優化)
└── comprehensive_test_suite.py (測試套件)
```

## 版本歷史

### v2.0.0 (當前版本)
- 全面重構和優化
- 增強版題組檢測
- 強化選項提取
- 改進題目解析
- 全面驗證機制
- 性能優化
- 配置系統
- 測試套件

### v1.0.0 (原版本)
- 基本PDF處理功能
- 簡單題組檢測
- 基本選項提取

## 貢獻指南

歡迎貢獻代碼和建議：

1. Fork 專案
2. 創建功能分支
3. 提交更改
4. 發起 Pull Request

## 授權

本專案採用 MIT 授權條款。

## 聯繫方式

如有問題或建議，請聯繫開發團隊。

---

**注意**: 本系統是對原有考古題處理系統的全面優化版本，提供了更強大、更靈活、更穩定的功能。建議在生產環境使用前進行充分測試。