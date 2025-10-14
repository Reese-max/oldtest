# Google表單考古題轉換器

這個工具可以將PDF考古題轉換為適合Google表單的CSV格式，並自動生成Google Apps Script代碼來建立表單。

## 功能特色

- 📄 自動解析PDF考古題
- 🔍 智能識別答案檔案
- 📊 轉換為Google表單格式
- 🤖 自動生成Google Apps Script
- 📝 提供詳細使用說明

## 安裝依賴

```bash
pip install -r requirements.txt
```

## 使用方法

### 方法1: 使用簡化腳本 (推薦)

```bash
python run_google_forms_converter.py
```

### 方法2: 直接使用轉換器

```python
from google_forms_converter import GoogleFormsConverter

converter = GoogleFormsConverter()
result = converter.process_pdf_to_google_forms(
    pdf_path="path/to/question.pdf",
    answer_path="path/to/answer.pdf",  # 可選
    output_dir="google_forms_output"
)
```

## 檔案結構

```
workspace/
├── pdf_to_csv.py                    # 原始PDF解析器
├── google_forms_converter.py        # Google表單轉換器
├── run_google_forms_converter.py    # 簡化執行腳本
├── requirements.txt                 # 依賴套件清單
└── google_forms_output/            # 輸出目錄
    ├── 檔案名_google_forms.csv      # Google表單格式CSV
    ├── 檔案名_google_apps_script.js # Google Apps Script代碼
    └── 檔案名_README.md             # 使用說明
```

## 輸出檔案說明

### 1. Google表單格式CSV
包含以下欄位：
- 題號: 題目編號
- 題目: 題目內容
- 題型: 選擇題/問答題
- 正確答案: 正確答案選項
- 選項A/B/C/D: 選擇題選項
- 說明: 額外說明
- 分數: 題目分數
- 必答: 是否必答

### 2. Google Apps Script代碼
自動生成的JavaScript代碼，可以直接在Google Apps Script中使用來建立表單。

### 3. 使用說明
詳細的步驟說明，包含如何在Google表單中使用這些檔案。

## 在Google表單中使用

### 步驟1: 使用Google Apps Script (推薦)
1. 開啟 [Google Apps Script](https://script.google.com)
2. 建立新專案
3. 複製生成的 `.js` 檔案內容到編輯器
4. 點擊「執行」按鈕
5. 系統會自動建立Google表單並回傳URL

### 步驟2: 手動建立表單
1. 開啟 [Google表單](https://forms.google.com)
2. 建立新表單
3. 參考生成的CSV檔案手動輸入題目

## 注意事項

- 確保PDF檔案路徑正確
- 答案檔案命名應包含「答案」、「解答」等關鍵字
- 建議先在測試環境中建立表單進行測試
- 可以根據需要調整表單設定（如時間限制、分數等）

## 故障排除

### 常見問題

1. **找不到PDF檔案**
   - 確認檔案路徑正確
   - 檢查檔案權限

2. **解析失敗**
   - 確認PDF檔案沒有密碼保護
   - 檢查PDF檔案是否損壞

3. **答案解析不正確**
   - 確認答案檔案格式正確
   - 手動檢查答案檔案內容

### 支援的答案格式

- `1.(A) 2.(B) 3.(C)`
- `1A 2B 3C`
- `1. A 2. B 3. C`

## 技術細節

- 使用 `pdfplumber` 解析PDF檔案
- 使用 `pandas` 處理CSV資料
- 使用正則表達式解析答案
- 支援多種答案格式自動識別

## 更新日誌

- v1.0.0: 初始版本，支援基本PDF轉Google表單功能
- 支援答案檔案自動識別
- 支援多種答案格式解析
- 自動生成Google Apps Script代碼