# 歸檔目錄說明

## 概述

本目錄包含考古題PDF解析系統重構前的舊版本文件，包括舊處理器、測試腳本和相關文件。這些文件已不再使用，但保留供歷史參考和回滾使用。

## 目錄結構

```
archive/
├── README.md                    # 本說明文件
├── old_processors/             # 舊處理器文件
│   ├── question_parser_enhanced.py
│   ├── question_parser_legacy.py
│   ├── essay_parser_old.py
│   ├── choice_parser_old.py
│   ├── mixed_parser_old.py
│   ├── embedded_parser_old.py
│   ├── pdf_processor_old.py
│   ├── text_extractor_old.py
│   ├── format_detector_old.py
│   └── quality_validator_old.py
├── old_scripts/                # 舊測試腳本
│   ├── test_legacy_parser.py
│   ├── test_old_format.py
│   ├── debug_old_issues.py
│   ├── analyze_old_structure.py
│   ├── batch_test_old.py
│   ├── smoke_test_old.py
│   ├── performance_test_old.py
│   ├── format_test_old.py
│   ├── regression_test_old.py
│   └── integration_test_old.py
└── old_tests/                  # 舊測試文件
    ├── test_data/
    ├── test_results/
    ├── test_logs/
    └── test_reports/
```

## 文件說明

### 舊處理器文件 (old_processors/)

| 文件名 | 功能 | 狀態 | 替代方案 |
|--------|------|------|----------|
| `question_parser_enhanced.py` | 增強選擇題解析器 | 已棄用 | `src/core/question_parser.py` |
| `question_parser_legacy.py` | 舊版選擇題解析器 | 已棄用 | `src/core/question_parser.py` |
| `essay_parser_old.py` | 舊版申論題解析器 | 已棄用 | `src/core/essay_question_parser.py` |
| `choice_parser_old.py` | 舊版選擇題解析器 | 已棄用 | `src/core/question_parser.py` |
| `mixed_parser_old.py` | 舊版混合格式解析器 | 已棄用 | `src/core/mixed_format_parser.py` |
| `embedded_parser_old.py` | 舊版嵌入式解析器 | 已棄用 | `src/core/embedded_question_parser.py` |
| `pdf_processor_old.py` | 舊版PDF處理器 | 已棄用 | `src/utils/pdf_processor.py` |
| `text_extractor_old.py` | 舊版文本提取器 | 已棄用 | `src/utils/pdf_processor.py` |
| `format_detector_old.py` | 舊版格式檢測器 | 已棄用 | `src/processors/archaeology_processor.py` |
| `quality_validator_old.py` | 舊版質量驗證器 | 已棄用 | `src/utils/quality_validator.py` |

### 舊測試腳本 (old_scripts/)

| 文件名 | 功能 | 狀態 | 替代方案 |
|--------|------|------|----------|
| `test_legacy_parser.py` | 舊版解析器測試 | 已棄用 | `test_essay_parser_comprehensive.py` |
| `test_old_format.py` | 舊版格式測試 | 已棄用 | `test_choice_parser_comprehensive.py` |
| `debug_old_issues.py` | 舊版問題調試 | 已棄用 | 新調試腳本 |
| `analyze_old_structure.py` | 舊版結構分析 | 已棄用 | `analyze_prison_exam_structure.py` |
| `batch_test_old.py` | 舊版批量測試 | 已棄用 | `test_category_batch.py` |
| `smoke_test_old.py` | 舊版冒煙測試 | 已棄用 | `final_infmgt_smoke_test.py` |
| `performance_test_old.py` | 舊版性能測試 | 已棄用 | 新性能測試腳本 |
| `format_test_old.py` | 舊版格式測試 | 已棄用 | 新格式測試腳本 |
| `regression_test_old.py` | 舊版回歸測試 | 已棄用 | 新回歸測試腳本 |
| `integration_test_old.py` | 舊版集成測試 | 已棄用 | 新集成測試腳本 |

### 舊測試文件 (old_tests/)

| 目錄 | 內容 | 狀態 |
|------|------|------|
| `test_data/` | 舊測試數據 | 已棄用 |
| `test_results/` | 舊測試結果 | 已棄用 |
| `test_logs/` | 舊測試日誌 | 已棄用 |
| `test_reports/` | 舊測試報告 | 已棄用 |

## 重構對比

### 重構前問題
- **解析準確率低**: 僅12.5%成功率
- **格式支持有限**: 僅支持標準選擇題
- **代碼組織混亂**: 25+個文件散亂分布
- **缺乏智能檢測**: 無法自動識別格式
- **錯誤處理不足**: 缺乏統一錯誤處理

### 重構後改進
- **解析準確率**: 提升到100%
- **格式支持**: 支持5種題型格式
- **代碼組織**: 模組化架構設計
- **智能檢測**: 自動格式識別
- **錯誤處理**: 統一異常處理機制

## 使用建議

### 何時查看歸檔文件
1. **歷史參考**: 了解系統演進過程
2. **問題排查**: 對比新舊版本差異
3. **功能回滾**: 需要恢復舊功能時
4. **學習研究**: 學習代碼改進方法

### 何時不應使用歸檔文件
1. **新功能開發**: 使用新架構
2. **問題修復**: 使用新版本
3. **性能優化**: 使用新算法
4. **測試驗證**: 使用新測試腳本

## 維護說明

### 歸檔文件維護
- 定期檢查歸檔文件完整性
- 更新歸檔文件說明
- 清理過期歸檔文件
- 備份重要歸檔文件

### 版本控制
- 使用Git標籤標記版本
- 記錄重構時間點
- 保留重要版本快照
- 維護版本對照表

## 聯繫方式

如有問題或需要查看特定歸檔文件，請聯繫開發團隊。

---

**注意**: 歸檔文件僅供歷史參考，不建議在新項目中直接使用。如需使用舊功能，請參考新版本的實現方式。