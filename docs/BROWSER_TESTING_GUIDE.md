# 瀏覽器自動化測試指南

## 📋 目錄

- [簡介](#簡介)
- [功能特性](#功能特性)
- [快速開始](#快速開始)
- [安裝步驟](#安裝步驟)
- [使用方法](#使用方法)
- [測試說明](#測試說明)
- [高級配置](#高級配置)
- [故障排除](#故障排除)

---

## 簡介

本項目提供完整的瀏覽器自動化測試方案，使用 **Playwright** 框架模擬真實用戶操作，自動測試考古題處理系統的所有前端功能。

### 為什麼選擇 Playwright？

- ✅ **現代化**：支持最新的 Web 標準
- ✅ **多瀏覽器**：支持 Chromium、Firefox、WebKit
- ✅ **快速穩定**：自動等待機制，減少不穩定測試
- ✅ **強大功能**：截圖、錄影、網絡攔截等
- ✅ **開發者友好**：豐富的 API 和優秀的文檔

---

## 功能特性

### 🎯 測試覆蓋

本測試套件覆蓋以下功能：

1. **首頁測試** ✅
   - 頁面元素檢查
   - 導航連結驗證
   - 統計數據顯示

2. **爬蟲下載頁面** ✅
   - 表單元素檢查
   - 年份和考試類型選擇
   - 下載按鈕功能

3. **OCR 處理頁面** ✅
   - 文件上傳控件
   - OCR 參數選項
   - 處理功能驗證

4. **PDF 上傳頁面** ✅
   - 文件上傳功能
   - 處理選項設置
   - 結果顯示

5. **性能監控頁面** ✅
   - 實時數據顯示
   - 圖表渲染
   - 數據更新

6. **頁面導航** ✅
   - 跨頁面導航
   - URL 驗證
   - 狀態保持

7. **響應式設計** ✅
   - Desktop (1920x1080)
   - Tablet (768x1024)
   - Mobile (375x667)

8. **API 健康檢查** ✅
   - 端點可用性
   - 響應狀態驗證

### 🎨 測試特性

- **自動截圖**：每個測試步驟自動截圖，保存到 `tests/browser/screenshots/`
- **詳細日誌**：實時顯示測試進度和結果
- **JSON 報告**：生成 JSON 格式的測試報告
- **可視化模式**：可選擇顯示瀏覽器窗口，觀察測試過程
- **多瀏覽器**：支持 Chromium、Firefox、WebKit
- **靈活配置**：可自定義 URL、延遲、超時等參數

---

## 快速開始

### 一鍵運行（推薦）

```bash
# 安裝依賴
pip install -r requirements-browser-test.txt
playwright install chromium

# 運行測試（自動啟動服務器）
python run_browser_test.py
```

就這麼簡單！腳本會：
1. 自動啟動 Web 服務器
2. 運行所有瀏覽器測試
3. 生成測試報告和截圖
4. 自動清理和關閉服務器

---

## 安裝步驟

### 1. 安裝 Python 依賴

```bash
# 安裝瀏覽器測試依賴
pip install -r requirements-browser-test.txt
```

### 2. 安裝瀏覽器

```bash
# 安裝 Chromium（推薦）
playwright install chromium

# 或安裝所有瀏覽器
playwright install
```

### 3. 驗證安裝

```bash
# 驗證 Playwright 安裝
playwright --version
```

---

## 使用方法

### 方法 1: 使用快速啟動腳本（推薦）

```bash
# 默認模式（顯示瀏覽器，慢速操作）
python run_browser_test.py

# 無頭模式（不顯示瀏覽器，適合 CI/CD）
python run_browser_test.py --headless

# 快速模式（不延遲操作）
python run_browser_test.py --fast

# 使用 Firefox
python run_browser_test.py --browser firefox

# 自定義端口
python run_browser_test.py --port 8080

# 僅啟動服務器（用於手動測試）
python run_browser_test.py --server-only
```

### 方法 2: 手動運行

```bash
# 終端 1: 啟動 Web 服務器
python run_webui.py

# 終端 2: 運行測試
python tests/browser/test_browser_automation.py
```

### 方法 3: 直接運行測試腳本

```bash
# 基本用法
python tests/browser/test_browser_automation.py

# 自定義 URL
python tests/browser/test_browser_automation.py --url http://localhost:8080

# 使用 Firefox 無頭模式
python tests/browser/test_browser_automation.py --browser firefox --headless

# 快速模式
python tests/browser/test_browser_automation.py --fast
```

---

## 測試說明

### 測試流程

測試腳本會按以下順序執行：

```
1. 啟動瀏覽器
2. 測試首頁
3. 測試爬蟲下載頁面
4. 測試 OCR 處理頁面
5. 測試 PDF 上傳頁面
6. 測試性能監控頁面
7. 測試頁面導航
8. 測試響應式設計
9. 測試 API 健康檢查
10. 生成測試報告
11. 關閉瀏覽器
```

### 測試輸出

#### 1. 控制台輸出

```
======================================================================
                        瀏覽器自動化測試
======================================================================

🌐 測試 URL: http://127.0.0.1:5000
🖥️  瀏覽器: chromium
👁️  可見模式: 是
⏱️  操作延遲: 500ms
📸 截圖目錄: /path/to/tests/browser/screenshots

======================================================================
測試 1: 首頁功能
======================================================================

📍 訪問首頁...
   頁面標題: 首頁 - 考古題處理系統

🔍 檢查頁面元素...
   主標題: 歡迎使用考古題處理系統 v2.0
   功能卡片數量: 4

✅ 首頁測試: PASS
...
```

#### 2. 截圖文件

測試過程中會自動截圖，保存到：

```
tests/browser/screenshots/
├── 01_homepage.png
├── 02_crawler_page.png
├── 02_crawler_filled.png
├── 03_ocr_page.png
├── 04_upload_page.png
├── 05_monitor_page.png
├── 06_nav_1_爬蟲下載.png
├── 06_nav_2_OCR.png
├── 06_nav_3_上傳.png
├── 06_nav_4_監控.png
├── 07_responsive_Desktop.png
├── 07_responsive_Tablet.png
├── 07_responsive_Mobile.png
└── 08_health_check.png
```

#### 3. JSON 測試報告

```json
[
  {
    "test": "首頁測試",
    "status": "PASS",
    "message": "所有元素正常顯示",
    "timestamp": 1699999999.123
  },
  {
    "test": "爬蟲頁面測試",
    "status": "PASS",
    "message": "表單元素完整",
    "timestamp": 1699999999.456
  }
]
```

保存位置: `tests/browser/test_results.json`

---

## 高級配置

### 自定義測試配置

編輯 `tests/browser/test_browser_automation.py`，修改 `BrowserTestConfig` 類：

```python
config = BrowserTestConfig(
    base_url="http://127.0.0.1:5000",  # 測試 URL
    headless=False,                     # 是否無頭模式
    slow_mo=500,                        # 操作延遲（ms）
    timeout=30000,                      # 超時時間（ms）
    browser_type="chromium"             # 瀏覽器類型
)
```

### 添加自定義測試

在 `BrowserAutomationTester` 類中添加新的測試方法：

```python
async def test_custom_feature(self):
    """測試自定義功能"""
    try:
        # 訪問頁面
        await self.page.goto(f"{self.config.base_url}/custom")

        # 執行操作
        button = self.page.locator("button.custom")
        await button.click()

        # 驗證結果
        result = await self.page.locator(".result").text_content()
        assert "成功" in result

        # 截圖
        await self.screenshot("custom_feature")

        # 記錄結果
        self.log_result("自定義功能測試", "PASS")

    except Exception as e:
        self.log_result("自定義功能測試", "FAIL", str(e))
        raise
```

然後在 `run_all_tests()` 中調用：

```python
async def run_all_tests(self):
    await self.setup()

    # 現有測試
    await self.test_homepage()
    # ...

    # 添加新測試
    await self.test_custom_feature()

    self.print_summary()
    await self.teardown()
```

### 配置不同的瀏覽器

```python
# Chromium（Chrome/Edge）
config = BrowserTestConfig(browser_type="chromium")

# Firefox
config = BrowserTestConfig(browser_type="firefox")

# WebKit（Safari）
config = BrowserTestConfig(browser_type="webkit")
```

---

## 故障排除

### 問題 1: 瀏覽器未安裝

**錯誤訊息**:
```
playwright._impl._api_types.Error: Executable doesn't exist
```

**解決方法**:
```bash
playwright install chromium
```

### 問題 2: Web 服務器未啟動

**錯誤訊息**:
```
playwright._impl._api_types.Error: net::ERR_CONNECTION_REFUSED
```

**解決方法**:
```bash
# 先啟動 Web 服務器
python run_webui.py

# 然後在另一個終端運行測試
python tests/browser/test_browser_automation.py --test-only
```

### 問題 3: 端口被占用

**錯誤訊息**:
```
OSError: [Errno 48] Address already in use
```

**解決方法**:
```bash
# 使用不同的端口
python run_browser_test.py --port 8080
```

或查找並關閉占用端口的進程：

```bash
# Linux/Mac
lsof -i :5000
kill -9 <PID>

# Windows
netstat -ano | findstr :5000
taskkill /PID <PID> /F
```

### 問題 4: 測試超時

**錯誤訊息**:
```
TimeoutError: Timeout 30000ms exceeded
```

**解決方法**:

調整超時時間：

```python
config = BrowserTestConfig(timeout=60000)  # 60秒
```

或在測試中增加等待時間：

```python
await self.page.wait_for_timeout(5000)  # 等待 5 秒
```

### 問題 5: 截圖失敗

**解決方法**:

確保截圖目錄存在：

```bash
mkdir -p tests/browser/screenshots
```

### 問題 6: 權限問題

**錯誤訊息**:
```
PermissionError: [Errno 13] Permission denied
```

**解決方法**:

```bash
# 給腳本添加執行權限
chmod +x run_browser_test.py
chmod +x tests/browser/test_browser_automation.py
```

---

## CI/CD 集成

### GitHub Actions

創建 `.github/workflows/browser-test.yml`:

```yaml
name: Browser Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v3

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'

    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install -r requirements-browser-test.txt

    - name: Install Playwright browsers
      run: playwright install chromium

    - name: Run browser tests
      run: python run_browser_test.py --headless --fast

    - name: Upload screenshots
      if: always()
      uses: actions/upload-artifact@v3
      with:
        name: test-screenshots
        path: tests/browser/screenshots/

    - name: Upload test results
      if: always()
      uses: actions/upload-artifact@v3
      with:
        name: test-results
        path: tests/browser/test_results.json
```

### GitLab CI

創建 `.gitlab-ci.yml`:

```yaml
browser_tests:
  image: mcr.microsoft.com/playwright/python:v1.40.0
  script:
    - pip install -r requirements.txt
    - pip install -r requirements-browser-test.txt
    - python run_browser_test.py --headless --fast
  artifacts:
    when: always
    paths:
      - tests/browser/screenshots/
      - tests/browser/test_results.json
```

---

## 最佳實踐

### 1. 測試前準備

- ✅ 確保所有依賴已安裝
- ✅ 檢查端口是否可用
- ✅ 清理舊的測試數據

### 2. 編寫測試

- ✅ 使用有意義的測試名稱
- ✅ 每個測試應該獨立
- ✅ 添加適當的等待時間
- ✅ 使用明確的斷言
- ✅ 截圖保存重要步驟

### 3. 錯誤處理

- ✅ 使用 try-except 捕獲異常
- ✅ 失敗時截圖
- ✅ 記錄詳細的錯誤信息

### 4. 性能優化

- ✅ 使用無頭模式（CI/CD）
- ✅ 合理設置超時時間
- ✅ 避免不必要的等待
- ✅ 並行運行測試（高級）

---

## 相關資源

- [Playwright 官方文檔](https://playwright.dev/python/)
- [Playwright API 參考](https://playwright.dev/python/docs/api/class-playwright)
- [測試最佳實踐](https://playwright.dev/python/docs/best-practices)

---

## 貢獻

歡迎提交 Issue 和 Pull Request！

## 授權

MIT License
