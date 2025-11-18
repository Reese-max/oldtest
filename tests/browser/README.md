# 瀏覽器自動化測試

自動化測試考古題處理系統的所有前端功能，模擬真實用戶操作。

## 快速開始

```bash
# 1. 安裝依賴
pip install -r requirements-browser-test.txt
playwright install chromium

# 2. 運行測試
python run_browser_test.py
```

## 測試內容

- ✅ 首頁功能
- ✅ 爬蟲下載頁面
- ✅ OCR 處理頁面
- ✅ PDF 上傳頁面
- ✅ 性能監控頁面
- ✅ 頁面導航
- ✅ 響應式設計
- ✅ API 健康檢查

## 命令選項

```bash
# 無頭模式
python run_browser_test.py --headless

# 快速模式
python run_browser_test.py --fast

# 使用 Firefox
python run_browser_test.py --browser firefox

# 僅啟動服務器
python run_browser_test.py --server-only
```

## 查看結果

- **截圖**: `tests/browser/screenshots/`
- **測試報告**: `tests/browser/test_results.json`

## 詳細文檔

請查看 [瀏覽器測試指南](../../docs/BROWSER_TESTING_GUIDE.md)
