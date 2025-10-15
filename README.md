# PDF轉Google表單系統

這是一個完整的PDF考古題轉換系統，可以將PDF格式的考古題轉換為Google表單，方便線上練習。

## 🚀 功能特色

- **PDF解析**: 自動從PDF中提取題目和選項
- **答案處理**: 支援正確答案和更正答案
- **Google表單生成**: 自動生成Google Apps Script代碼
- **自動評分**: 內建自動評分和結果記錄功能
- **分類標籤**: 自動為題目添加分類和難度標籤

## 📁 檔案結構

```
/workspace/
├── pdf_to_google_form.py          # 主要PDF處理器
├── google_apps_script_generator_fixed.py  # Google Apps Script生成器
├── test_complete_workflow.py      # 完整工作流程測試
├── test_questions.txt             # 測試題目檔案
├── test_output/                   # 輸出目錄
│   ├── 完整工作流程測試.csv
│   └── 完整工作流程測試_GoogleAppsScript.js
└── Google_Apps_Script_使用說明.md
```

## 🛠️ 使用方法

### 1. 準備PDF檔案

將考古題PDF檔案放在 `test_pdfs/` 目錄中，或修改程式中的檔案路徑。

### 2. 執行轉換

```bash
python3 pdf_to_google_form.py
```

### 3. 生成Google表單

```bash
python3 google_apps_script_generator_fixed.py
```

### 4. 部署到Google Apps Script

1. 前往 [Google Apps Script](https://script.google.com)
2. 建立新專案
3. 複製生成的JavaScript代碼
4. 執行 `main()` 函數建立表單

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

## 🔧 自訂設定

### 修改題目分類邏輯

在 `GoogleFormCSVGenerator` 類別中修改 `_categorize_question()` 方法。

### 調整難度判斷

修改 `_calculate_difficulty()` 方法來調整難度判斷標準。

### 自訂Google表單樣式

修改 `google_apps_script_generator_fixed.py` 中的模板。

## 🧪 測試

執行完整測試：

```bash
python3 test_complete_workflow.py
```

## 📝 注意事項

1. **PDF格式**: 目前支援標準的PDF格式，複雜版面可能需要調整
2. **文字編碼**: 確保PDF中的中文文字可以正確提取
3. **Google權限**: 需要適當的Google帳戶權限來建立表單
4. **API限制**: Google Apps Script有執行時間和API調用限制

## 🐛 故障排除

### 常見問題

1. **PDF無法解析**: 檢查PDF是否為掃描版，需要OCR處理
2. **文字亂碼**: 確認PDF編碼格式
3. **Google表單建立失敗**: 檢查Google帳戶權限和API設定

### 除錯方法

1. 檢查控制台輸出訊息
2. 驗證CSV檔案格式
3. 測試JavaScript代碼語法

## 📈 未來改進

- [ ] 支援更多PDF格式
- [ ] 添加OCR功能
- [ ] 支援圖片題目
- [ ] 添加題目統計分析
- [ ] 支援批量處理

## 📄 授權

此專案僅供學習和個人使用。

---

**開發者**: AI Assistant  
**版本**: 1.0.0  
**更新日期**: 2024年