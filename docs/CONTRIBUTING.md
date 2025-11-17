# 貢獻指南

感謝您對本項目的關注！本指南將幫助您了解如何為項目做出貢獻。

---

## 📋 目錄

1. [開發環境設置](#開發環境設置)
2. [代碼規範](#代碼規範)
3. [提交規範](#提交規範)
4. [測試要求](#測試要求)
5. [文檔要求](#文檔要求)
6. [Pull Request 流程](#pull-request-流程)

---

## 開發環境設置

### 1. Fork 和 Clone

```bash
# Fork 項目到您的帳戶
# 然後 clone 到本地
git clone https://github.com/YOUR_USERNAME/oldtest.git
cd oldtest
```

### 2. 創建虛擬環境

```bash
# 創建虛擬環境
python -m venv venv

# 激活虛擬環境
# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 3. 安裝依賴

```bash
# 安裝項目依賴
pip install -r requirements.txt

# 安裝開發依賴
pip install pytest pytest-cov black flake8 mypy
```

### 4. 驗證環境

```bash
# 運行測試確認環境正常
python -m unittest discover tests
```

---

## 代碼規範

### Python 代碼風格

我們遵循 **PEP 8** 代碼風格指南。

#### 使用 Black 格式化代碼

```bash
# 格式化所有代碼
black src/ tests/

# 檢查代碼格式
black --check src/ tests/
```

#### 使用 Flake8 檢查代碼

```bash
flake8 src/ tests/ --max-line-length=100
```

### 命名規範

#### 文件命名
- 模塊文件: `snake_case.py`
- 測試文件: `test_module_name.py`

#### 代碼命名
```python
# 類名：PascalCase
class QuestionParser:
    pass

# 函數名：snake_case
def parse_questions(text):
    pass

# 常量：UPPER_CASE
MAX_PAGES = 200

# 私有方法：_leading_underscore
def _validate_input(data):
    pass
```

### 類型提示

所有公共函數和方法必須包含類型提示：

```python
from typing import List, Dict, Optional

def parse_questions(
    text: str,
    max_questions: Optional[int] = None
) -> List[Dict[str, Any]]:
    """
    解析題目。

    Args:
        text: 輸入文字
        max_questions: 最大題目數

    Returns:
        題目列表
    """
    pass
```

### 文檔字符串

使用 Google 風格的文檔字符串：

```python
def process_pdf(pdf_path: str, output_dir: str = "output") -> Dict[str, Any]:
    """
    處理 PDF 文件。

    Args:
        pdf_path: PDF 文件路徑
        output_dir: 輸出目錄，默認為 "output"

    Returns:
        處理結果字典，包含以下鍵：
        - question_count: 題目數量
        - output_file: 輸出文件路徑
        - success: 是否成功

    Raises:
        PDFProcessingError: PDF 處理失敗時拋出

    Example:
        ```python
        processor = PDFProcessor()
        result = processor.process_pdf("exam.pdf")
        print(result['question_count'])
        ```
    """
    pass
```

---

## 提交規範

### Commit Message 格式

使用以下格式撰寫 commit message：

```
<type>(<scope>): <subject>

<body>

<footer>
```

#### Type 類型

- `feat`: 新功能
- `fix`: 修復 bug
- `docs`: 文檔更新
- `style`: 代碼格式調整（不影響功能）
- `refactor`: 重構代碼
- `test`: 添加或修改測試
- `perf`: 性能優化
- `chore`: 構建工具或輔助工具的變動

#### 示例

```bash
# 新功能
git commit -m "feat(parser): add support for multi-column questions"

# 修復 bug
git commit -m "fix(pdf): resolve memory leak in large file processing"

# 文檔更新
git commit -m "docs(api): update API documentation for streaming processor"

# 測試
git commit -m "test(parser): add tests for edge cases in question parsing"
```

### 完整示例

```
feat(concurrent): add progress callback support

添加進度回調功能，允許用戶在批量處理時獲取實時進度。

Changes:
- Add progress_callback parameter to process_batch
- Implement progress tracking in worker threads
- Add example usage in documentation

Closes #123
```

---

## 測試要求

### 測試覆蓋率

- 新功能必須包含測試
- 測試覆蓋率應保持在 **90% 以上**
- Bug 修復必須包含回歸測試

### 運行測試

```bash
# 運行所有測試
python -m unittest discover tests -v

# 運行特定測試
python -m unittest tests.test_concurrent_processor -v

# 運行測試並查看覆蓋率
pytest --cov=src tests/
```

### 測試命名

```python
class TestQuestionParser:
    """測試 QuestionParser 類"""

    def test_parse_simple_question(self):
        """測試解析簡單題目"""
        pass

    def test_parse_empty_text_returns_empty_list(self):
        """測試解析空文本返回空列表"""
        pass

    def test_parse_invalid_format_raises_error(self):
        """測試解析無效格式拋出錯誤"""
        pass
```

### 測試結構

```python
def test_function_name(self):
    """測試描述"""
    # Arrange（準備）
    parser = QuestionParser()
    text = "測試文字"

    # Act（執行）
    result = parser.parse_questions(text)

    # Assert（斷言）
    self.assertEqual(len(result), 1)
    self.assertIn('題號', result[0])
```

---

## 文檔要求

### 代碼文檔

- 所有公共類、函數、方法必須有文檔字符串
- 文檔字符串應包含：描述、參數、返回值、異常、示例
- 使用中文撰寫文檔

### API 文檔

添加新功能時，需要更新以下文檔：

1. **API_DOCUMENTATION.md** - API 參考
2. **QUICK_START.md** - 快速開始指南（如適用）
3. **README.md** - 主要文檔（如適用）

### 示例代碼

新功能應包含示例代碼：

```python
# examples/new_feature_example.py
"""
新功能示例
演示如何使用新功能
"""

def example_basic_usage():
    """示例 1: 基本使用"""
    # 代碼示例
    pass

if __name__ == '__main__':
    example_basic_usage()
```

---

## Pull Request 流程

### 1. 創建分支

```bash
# 從 main 分支創建新分支
git checkout main
git pull origin main
git checkout -b feature/your-feature-name
```

### 2. 開發功能

```bash
# 開發代碼
# 添加測試
# 更新文檔
```

### 3. 提交代碼

```bash
# 添加更改
git add .

# 提交（遵循提交規範）
git commit -m "feat(module): description"

# 推送到遠程
git push origin feature/your-feature-name
```

### 4. 創建 Pull Request

在 GitHub 上創建 Pull Request，包含：

#### PR 標題
遵循 commit message 格式

#### PR 描述
```markdown
## 描述
簡要描述此 PR 的目的

## 更改內容
- 添加了 XXX 功能
- 修復了 XXX 問題
- 更新了 XXX 文檔

## 測試
- [ ] 所有測試通過
- [ ] 添加了新測試
- [ ] 測試覆蓋率 > 90%

## 文檔
- [ ] 更新了 API 文檔
- [ ] 更新了示例代碼
- [ ] 更新了 README（如需要）

## 截圖（如適用）
添加相關截圖

## 相關 Issue
Closes #123
```

### 5. Code Review

- 等待維護者 review
- 根據反饋進行修改
- 確保 CI 通過

### 6. 合併

PR 被批准後，維護者將合併到 main 分支。

---

## 代碼審查標準

### 功能性
- ✅ 功能是否正常工作
- ✅ 是否處理了邊界情況
- ✅ 錯誤處理是否完善

### 代碼質量
- ✅ 代碼是否清晰易讀
- ✅ 是否遵循項目代碼規範
- ✅ 是否有適當的註釋
- ✅ 是否有重複代碼

### 測試
- ✅ 是否包含單元測試
- ✅ 測試是否充分
- ✅ 測試是否通過

### 文檔
- ✅ 是否有文檔字符串
- ✅ API 文檔是否更新
- ✅ 是否有使用示例

### 性能
- ✅ 是否有性能問題
- ✅ 記憶體使用是否合理
- ✅ 是否有性能測試（如適用）

---

## 開發技巧

### 使用虛擬環境

始終在虛擬環境中開發，避免依賴衝突。

### 頻繁運行測試

```bash
# 開發時持續運行測試
watch -n 1 'python -m unittest discover tests'
```

### 使用 Git Hooks

設置 pre-commit hook 自動檢查代碼：

```bash
# .git/hooks/pre-commit
#!/bin/sh
black --check src/ tests/
flake8 src/ tests/
python -m unittest discover tests
```

### 性能分析

使用性能監控工具：

```python
from src.utils.performance_monitor import monitor_performance

@monitor_performance
def your_function():
    # 開發新功能時監控性能
    pass
```

---

## 問題反饋

### 提交 Bug

創建 Issue 時包含：

1. **Bug 描述** - 清楚描述問題
2. **重現步驟** - 如何重現
3. **預期行為** - 應該發生什麼
4. **實際行為** - 實際發生了什麼
5. **環境信息** - Python 版本、OS 等
6. **日誌** - 相關錯誤日誌
7. **截圖** - 如果適用

### 功能建議

創建 Issue 時包含：

1. **功能描述** - 想要什麼功能
2. **使用場景** - 為什麼需要這個功能
3. **建議實現** - 您的想法（可選）
4. **替代方案** - 其他可能的解決方案（可選）

---

## 社區準則

### 行為準則

- 尊重所有貢獻者
- 建設性的反饋
- 歡迎新手
- 保持友好和專業

### 溝通

- Issue 討論功能和 bug
- Pull Request 討論代碼實現
- 保持討論相關和專注

---

## 獎勵

優秀的貢獻者將被列入：

- 項目貢獻者列表
- Release notes
- 文檔致謝

---

## 聯繫方式

- **Issue**: GitHub Issues
- **Email**: your-email@example.com
- **討論**: GitHub Discussions

---

**感謝您的貢獻！** 🎉

每一個貢獻都讓項目變得更好！
