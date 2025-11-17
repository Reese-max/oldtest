# 國際化（i18n）使用指南

**版本**: 1.0
**最後更新**: 2025-11-17

---

## 📖 目錄

- [概述](#概述)
- [支持的語言](#支持的語言)
- [快速開始](#快速開始)
- [API參考](#api參考)
- [使用範例](#使用範例)
- [添加新語言](#添加新語言)
- [最佳實踐](#最佳實踐)
- [常見問題](#常見問題)

---

## 概述

本系統提供完整的國際化（i18n）支持，允許用戶在不同語言之間輕鬆切換，並為開發者提供簡單的API來添加多語言支持。

### 主要特性

- ✅ 支持 4 種語言（繁體中文、簡體中文、英文、日文）
- ✅ 簡單易用的 API
- ✅ 支持文本格式化（參數替換）
- ✅ 嵌套鍵值支持（如 `messages.success`）
- ✅ 自動回退到默認語言
- ✅ 完整的類型提示
- ✅ 全局和自定義實例兩種使用方式

---

## 支持的語言

| 語言代碼 | 語言名稱 | 狀態 |
|---------|---------|------|
| `zh-TW` | 繁體中文 | ✅ 完整支持 |
| `zh-CN` | 简体中文 | ✅ 完整支持 |
| `en` | English | ✅ 完整支持 |
| `ja` | 日本語 | ✅ 完整支持 |

**默認語言**: `zh-TW`（繁體中文）

---

## 快速開始

### 1. 基本使用

```python
from src.i18n import get_text, set_language

# 獲取翻譯文本
app_name = get_text('app.name')
print(app_name)  # 輸出: 考古題處理系統

# 切換語言
set_language('en')
app_name = get_text('app.name')
print(app_name)  # 輸出: Exam Question Processor
```

### 2. 格式化文本

```python
from src.i18n import get_text

# 帶參數的翻譯
text = get_text('app.version', version='1.8.0')
print(text)  # 輸出: 版本 1.8.0

text = get_text('pdf.extracting_page', page=5, total=10)
print(text)  # 輸出: 正在提取第 5/10 頁...
```

### 3. 檢查當前語言

```python
from src.i18n import get_current_language

current = get_current_language()
print(f"當前語言: {current}")  # 輸出: 當前語言: zh-TW
```

---

## API參考

### 全局函數

#### `get_text(key, **kwargs) -> str`

獲取翻譯文本。

**參數**:
- `key` (str): 翻譯鍵值，支持點號分隔（如 `'messages.success'`）
- `**kwargs`: 用於格式化的參數

**返回**:
- `str`: 翻譯後的文本

**範例**:
```python
text = get_text('messages.success')
text = get_text('app.version', version='1.0.0')
```

---

#### `set_language(lang_code) -> bool`

設置當前語言。

**參數**:
- `lang_code` (str): 語言代碼（如 `'en'`, `'zh-TW'`）

**返回**:
- `bool`: 是否設置成功

**範例**:
```python
success = set_language('en')
if success:
    print("語言切換成功")
```

---

#### `get_current_language() -> str`

獲取當前語言代碼。

**返回**:
- `str`: 當前語言代碼

**範例**:
```python
current = get_current_language()
print(f"當前語言: {current}")
```

---

### I18nManager 類

如果需要更多控制，可以直接使用 `I18nManager` 類。

#### 初始化

```python
from src.i18n import I18nManager

i18n = I18nManager(default_language='zh-TW')
```

#### 方法

##### `get_text(key, **kwargs) -> str`

獲取翻譯文本。

##### `set_language(lang_code) -> bool`

設置當前語言。

##### `get_current_language() -> str`

獲取當前語言代碼。

##### `get_supported_languages() -> Dict[str, str]`

獲取所有支持的語言。

**返回**:
```python
{
    'zh-TW': '繁體中文',
    'zh-CN': '简体中文',
    'en': 'English',
    'ja': '日本語'
}
```

##### `is_language_supported(lang_code) -> bool`

檢查語言是否支持。

---

## 使用範例

### 範例1: 在PDF處理中使用

```python
from src.i18n import get_text, set_language

class PDFProcessor:
    def process(self, pdf_path):
        # 開始處理
        print(get_text('pdf.extracting'))

        try:
            # 處理邏輯
            for i, page in enumerate(pages):
                msg = get_text('pdf.extracting_page', page=i+1, total=len(pages))
                print(msg)

            # 成功
            print(get_text('pdf.extract_success'))

        except Exception as e:
            # 失敗
            error_msg = get_text('pdf.extract_failed', error=str(e))
            print(error_msg)
```

### 範例2: CLI工具多語言支持

```python
import argparse
from src.i18n import get_text, set_language

def create_parser():
    parser = argparse.ArgumentParser(
        description=get_text('app.description')
    )

    parser.add_argument(
        '--lang',
        choices=['zh-TW', 'zh-CN', 'en', 'ja'],
        default='zh-TW',
        help=get_text('cli.language')
    )

    parser.add_argument(
        '--version',
        action='version',
        version=get_text('app.version', version='1.8.0'),
        help=get_text('cli.version')
    )

    return parser

def main():
    parser = create_parser()
    args = parser.parse_args()

    # 設置語言
    set_language(args.lang)

    # 顯示歡迎訊息
    print(get_text('app.name'))
    print(get_text('app.description'))
```

### 範例3: 批量處理進度提示

```python
from src.i18n import get_text

def process_batch(files):
    total = len(files)

    # 開始訊息
    print(get_text('processor.processing_batch', count=total))

    success = 0
    failed = 0

    for i, file in enumerate(files):
        # 進度訊息
        progress = get_text('processor.batch_progress', current=i+1, total=total)
        print(progress)

        try:
            process_file(file)
            success += 1
        except Exception:
            failed += 1

    # 完成訊息
    result = get_text('processor.batch_completed', success=success, failed=failed)
    print(result)
```

### 範例4: 錯誤處理

```python
from src.i18n import get_text

def safe_process(file_path):
    try:
        return process_file(file_path)
    except FileNotFoundError:
        error = get_text('errors.file_not_found', path=file_path)
        print(error)
    except PermissionError:
        error = get_text('errors.permission_denied', path=file_path)
        print(error)
    except MemoryError:
        error = get_text('errors.out_of_memory')
        print(error)
    except Exception as e:
        error = get_text('errors.unknown_error', error=str(e))
        print(error)
```

### 範例5: 語言選擇菜單

```python
from src.i18n import I18nManager, set_language, get_text

def show_language_menu():
    i18n = I18nManager()
    languages = i18n.get_supported_languages()

    print(get_text('i18n.available_languages'))
    for i, (code, name) in enumerate(languages.items(), 1):
        print(f"  {i}. {name} ({code})")

    choice = input("選擇語言 (1-4): ")
    lang_codes = list(languages.keys())

    if choice.isdigit() and 1 <= int(choice) <= len(lang_codes):
        selected = lang_codes[int(choice) - 1]
        if set_language(selected):
            msg = get_text('i18n.language_changed', language=languages[selected])
            print(msg)
```

---

## 添加新語言

如果需要添加新語言（如法文、德文等），請按以下步驟操作：

### 步驟1: 創建語言檔案

在 `src/i18n/locales/` 目錄下創建新的JSON檔案：

```bash
touch src/i18n/locales/fr.json
```

### 步驟2: 添加翻譯

參考現有的語言檔案（如 `zh-TW.json`），添加所有翻譯：

```json
{
  "app": {
    "name": "Système de traitement des questions d'examen",
    "version": "Version {version}",
    "description": "Analyseur intelligent de questions PDF"
  },
  "messages": {
    "success": "✅ Succès",
    "error": "❌ Erreur",
    ...
  },
  ...
}
```

### 步驟3: 註冊新語言

在 `src/i18n/i18n_manager.py` 中添加新語言：

```python
class I18nManager:
    SUPPORTED_LANGUAGES = {
        'zh-TW': '繁體中文',
        'zh-CN': '简体中文',
        'en': 'English',
        'ja': '日本語',
        'fr': 'Français',  # 新增
    }
```

### 步驟4: 測試

創建測試確保新語言正常工作：

```python
def test_french():
    i18n = I18nManager()
    i18n.set_language('fr')
    text = i18n.get_text('app.name')
    assert text == "Système de traitement des questions d'examen"
```

---

## 最佳實踐

### 1. 使用有意義的鍵值

**好的範例**:
```python
get_text('pdf.extract_success')
get_text('errors.file_not_found')
```

**不好的範例**:
```python
get_text('msg1')
get_text('err_code_123')
```

### 2. 保持翻譯檔案結構一致

確保所有語言檔案都有相同的鍵值結構：

```json
// zh-TW.json
{
  "app": { "name": "..." },
  "messages": { "success": "..." }
}

// en.json
{
  "app": { "name": "..." },
  "messages": { "success": "..." }
}
```

### 3. 使用參數而非字串拼接

**好的範例**:
```python
get_text('pdf.extracting_page', page=5, total=10)
```

**不好的範例**:
```python
f"正在提取第 {page}/{total} 頁..."
```

### 4. 提供上下文

在鍵值命名時提供足夠的上下文：

```python
'pdf.extract_success'  # 明確是PDF提取成功
'parser.parse_failed'  # 明確是解析失敗
```

### 5. 統一使用全局函數

在大多數情況下，使用全局函數即可：

```python
from src.i18n import get_text, set_language

# 簡單直接
text = get_text('app.name')
```

只在需要多個獨立實例時才使用 `I18nManager`:

```python
from src.i18n import I18nManager

# 創建獨立實例
i18n1 = I18nManager(default_language='en')
i18n2 = I18nManager(default_language='ja')
```

---

## 常見問題

### Q1: 如何設置默認語言？

在應用啟動時設置：

```python
from src.i18n import set_language

# 應用啟動時
def main():
    set_language('zh-TW')  # 設置默認語言
    # ... 其他初始化
```

或者創建自定義實例：

```python
from src.i18n import I18nManager

i18n = I18nManager(default_language='en')
```

### Q2: 如何根據系統語言自動設置？

```python
import locale
from src.i18n import set_language

# 獲取系統語言
system_lang = locale.getdefaultlocale()[0]  # 例如: 'zh_TW'

# 轉換為我們的語言代碼
lang_map = {
    'zh_TW': 'zh-TW',
    'zh_CN': 'zh-CN',
    'en_US': 'en',
    'ja_JP': 'ja',
}

lang_code = lang_map.get(system_lang, 'zh-TW')
set_language(lang_code)
```

### Q3: 翻譯文本不顯示怎麼辦？

檢查以下幾點：

1. 鍵值是否正確：
```python
# 錯誤：使用了不存在的鍵值
text = get_text('app.title')  # 應該是 'app.name'
```

2. 語言檔案是否存在對應翻譯：
```json
// 檢查 src/i18n/locales/zh-TW.json
{
  "app": {
    "name": "考古題處理系統"  // 確保存在
  }
}
```

3. 語言是否正確設置：
```python
from src.i18n import get_current_language

print(get_current_language())  # 檢查當前語言
```

### Q4: 如何處理缺失的翻譯？

系統會自動回退到默認語言，如果默認語言也沒有，則返回鍵值本身：

```python
# 如果 'some.missing.key' 在所有語言中都不存在
text = get_text('some.missing.key')
print(text)  # 輸出: 'some.missing.key'
```

### Q5: 可以動態添加翻譯嗎？

目前系統從JSON檔案載入翻譯，如需動態添加，可以：

1. 修改JSON檔案後重新載入
2. 或者擴展 `I18nManager` 類添加動態載入功能

### Q6: 性能如何？

翻譯在初始化時一次性載入到記憶體，查詢速度非常快（O(1)）。不會影響應用性能。

---

## 翻譯鍵值總覽

### 應用程序
- `app.name` - 應用名稱
- `app.version` - 版本資訊
- `app.description` - 應用描述

### 訊息
- `messages.success` - 成功
- `messages.error` - 錯誤
- `messages.warning` - 警告
- `messages.info` - 資訊
- `messages.processing` - 處理中
- `messages.completed` - 已完成
- `messages.failed` - 失敗

### PDF處理
- `pdf.extracting` - 正在提取
- `pdf.extracting_page` - 提取頁面
- `pdf.extract_success` - 提取成功
- `pdf.extract_failed` - 提取失敗
- `pdf.file_not_found` - 檔案不存在
- `pdf.ocr_enabled` - OCR已啟用
- `pdf.ocr_processing` - OCR處理中
- `pdf.ocr_success` - OCR成功
- `pdf.ocr_failed` - OCR失敗

### 解析器
- `parser.parsing` - 解析中
- `parser.parse_success` - 解析成功
- `parser.parse_failed` - 解析失敗
- `parser.detecting_format` - 檢測格式
- `parser.format_detected` - 格式已檢測

### 處理器
- `processor.processing_pdf` - 處理PDF
- `processor.processing_batch` - 批量處理
- `processor.batch_completed` - 批量完成
- `processor.generating_csv` - 生成CSV
- `processor.generating_form` - 生成表單

### 性能監控
- `performance.monitoring` - 監控啟用
- `performance.duration` - 執行時間
- `performance.memory_usage` - 記憶體使用
- `performance.cpu_usage` - CPU使用

### 錯誤
- `errors.unknown_error` - 未知錯誤
- `errors.file_not_found` - 檔案不存在
- `errors.permission_denied` - 權限不足
- `errors.out_of_memory` - 記憶體不足

完整列表請參考語言檔案：`src/i18n/locales/zh-TW.json`

---

**文檔版本**: 1.0
**最後更新**: 2025-11-17
**維護者**: 開發團隊
