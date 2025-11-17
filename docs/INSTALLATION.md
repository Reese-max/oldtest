# 安裝指南

本文檔提供詳細的安裝說明，幫助您根據需求選擇合適的安裝方式。

---

## 📋 系統需求

### 基本需求
- **Python**: 3.8 或更高版本
- **作業系統**: Windows, macOS, Linux
- **記憶體**: 至少 2GB RAM（推薦 4GB+）
- **硬碟空間**:
  - 最小化安裝：~100MB
  - 完整安裝（含OCR）：~500MB

### OCR 功能額外需求
如需使用 OCR 功能處理掃描版PDF：
- **記憶體**: 至少 4GB RAM（推薦 8GB+）
- **硬碟空間**: 額外 ~400MB（PaddleOCR 模型）

---

## 🚀 快速安裝

### 方式一：使用 pip（推薦）

#### 1. 最小化安裝（基本功能）
適合只需要處理文字型PDF的用戶：

```bash
# 克隆倉庫
git clone https://github.com/yourusername/exam-question-processor.git
cd exam-question-processor

# 安裝最小化依賴
pip install -r requirements-minimal.txt
```

**包含功能**：
- ✅ PDF文字提取
- ✅ 題目解析
- ✅ CSV和Google表單生成
- ✅ 批量處理
- ✅ 性能監控

**不包含**：
- ❌ OCR功能（無法處理掃描版PDF）
- ❌ 開發工具

**適合用戶**：
- 只處理文字型PDF
- 對安裝包大小有要求
- 快速試用系統

---

#### 2. 完整安裝（推薦）
包含所有功能（含OCR）：

```bash
# 克隆倉庫
git clone https://github.com/yourusername/exam-question-processor.git
cd exam-question-processor

# 安裝完整依賴
pip install -r requirements.txt
```

**包含功能**：
- ✅ 所有基本功能
- ✅ OCR功能（PaddleOCR）
- ✅ 測試框架
- ✅ 代碼質量工具

**適合用戶**：
- 需要處理掃描版PDF
- 需要完整功能
- 生產環境使用

---

#### 3. 開發者安裝
適合想要參與開發的貢獻者：

```bash
# 克隆倉庫
git clone https://github.com/yourusername/exam-question-processor.git
cd exam-question-processor

# 安裝開發依賴
pip install -r requirements-dev.txt
```

**額外包含**：
- ✅ 測試工具（pytest）
- ✅ 代碼格式化（black）
- ✅ 代碼檢查（flake8, mypy）
- ✅ 文檔生成工具（sphinx）

---

### 方式二：使用 setup.py

#### 基本安裝
```bash
pip install -e .
```

#### 安裝特定功能
```bash
# 只安裝 OCR 功能
pip install -e ".[ocr]"

# 只安裝開發工具
pip install -e ".[dev]"

# 完整安裝（所有功能）
pip install -e ".[full]"

# 超級完整（包含AI功能）
pip install -e ".[all]"
```

---

## 🎯 按需安裝指南

### 場景一：只處理文字型PDF

如果您的PDF都是文字型的（不是掃描版），使用最小化安裝即可：

```bash
pip install -r requirements-minimal.txt
```

**優點**：
- 📦 安裝包小（約100MB）
- ⚡ 安裝速度快
- 💾 記憶體需求低

---

### 場景二：需要處理掃描版PDF

如果需要OCR功能：

```bash
# 先安裝核心功能
pip install -r requirements-minimal.txt

# 再安裝OCR功能
pip install -r requirements-ocr.txt
```

**注意事項**：
- PaddleOCR 首次運行會下載模型（約10-20MB）
- 需要至少 4GB RAM
- 處理速度會比文字提取慢

**GPU 加速**（可選）：

如果有 NVIDIA GPU 和 CUDA 支持：

```bash
# 替換 CPU 版本的 paddlepaddle
pip uninstall paddlepaddle
pip install paddlepaddle-gpu>=2.5.0

# 然後安裝其他OCR依賴
pip install paddleocr pdf2image Pillow
```

---

### 場景三：開發和貢獻

如果您想參與項目開發：

```bash
# 克隆並進入項目
git clone https://github.com/yourusername/exam-question-processor.git
cd exam-question-processor

# 安裝開發依賴
pip install -r requirements-dev.txt

# 安裝 pre-commit hooks（可選）
pre-commit install
```

---

## 🔧 依賴包詳細說明

### 核心依賴（必需）

| 包名 | 版本 | 用途 | 大小 |
|-----|------|------|------|
| pdfplumber | >=0.9.0 | PDF文字提取 | ~5MB |
| pandas | >=1.5.0 | 資料處理 | ~30MB |
| numpy | >=1.24.0 | 數值計算 | ~20MB |
| regex | >=2023.10.0 | 正則表達式 | ~1MB |
| python-Levenshtein | >=0.21.0 | 字串比對 | ~1MB |
| PyYAML | >=6.0 | 配置管理 | ~1MB |
| psutil | >=5.9.0 | 系統監控 | ~1MB |

**總大小**：約 60MB

---

### OCR 依賴（可選）

| 包名 | 版本 | 用途 | 大小 |
|-----|------|------|------|
| paddlepaddle | >=2.5.0 | 深度學習框架 | ~200MB |
| paddleocr | >=2.7.0 | OCR引擎 | ~10MB |
| pdf2image | >=1.16.3 | PDF轉圖片 | ~1MB |
| Pillow | >=10.0.0 | 圖像處理 | ~3MB |

**總大小**：約 214MB

**首次運行**：會下載OCR模型（約10-20MB）

---

### 開發工具（開發者）

| 包名 | 版本 | 用途 |
|-----|------|------|
| pytest | >=7.0.0 | 測試框架 |
| pytest-cov | >=4.0.0 | 測試覆蓋率 |
| black | >=22.0.0 | 代碼格式化 |
| flake8 | >=5.0.0 | 代碼檢查 |
| mypy | >=1.0.0 | 類型檢查 |

---

## 📊 安裝方式比較

| 安裝方式 | 功能 | 安裝大小 | 安裝時間 | 適合用戶 |
|---------|------|---------|---------|----------|
| 最小化 | 基本功能 | ~100MB | 1-2分鐘 | 只處理文字PDF |
| OCR | 基本+OCR | ~300MB | 3-5分鐘 | 需要處理掃描版 |
| 完整 | 全部功能 | ~400MB | 5-8分鐘 | 生產環境 |
| 開發 | 全部+開發工具 | ~500MB | 8-10分鐘 | 開發者 |

---

## ✅ 驗證安裝

安裝完成後，驗證是否成功：

### 1. 檢查 Python 版本
```bash
python --version
# 應該顯示 Python 3.8 或更高
```

### 2. 驗證核心功能
```bash
python -c "import pdfplumber; import pandas; print('✅ 核心依賴安裝成功')"
```

### 3. 驗證 OCR 功能（如果安裝了）
```bash
python -c "import paddleocr; print('✅ OCR 依賴安裝成功')"
```

### 4. 運行測試（如果安裝了開發工具）
```bash
pytest tests/ -v
```

### 5. 快速測試
```python
# test_installation.py
from src.processors.archaeology_processor import ArchaeologyProcessor

processor = ArchaeologyProcessor()
print("✅ 系統安裝成功！")
```

```bash
python test_installation.py
```

---

## 🐛 常見問題

### Q1: pip install 失敗

**問題**：`ERROR: Could not find a version that satisfies the requirement...`

**解決方案**：
```bash
# 升級 pip
python -m pip install --upgrade pip

# 重新安裝
pip install -r requirements-minimal.txt
```

---

### Q2: PaddleOCR 安裝失敗

**問題**：`ERROR: Failed building wheel for paddlepaddle`

**解決方案**：

**方案一**：使用預編譯版本
```bash
pip install paddlepaddle -i https://mirror.baidu.com/pypi/simple
```

**方案二**：跳過OCR功能
```bash
# 只安裝最小化依賴，不安裝OCR
pip install -r requirements-minimal.txt
```

---

### Q3: 記憶體不足

**問題**：處理大型PDF時記憶體不足

**解決方案**：

使用流式處理：
```python
from src.utils.streaming_processor import StreamingPDFProcessor

# 使用較小的分塊大小
processor = StreamingPDFProcessor(chunk_size=5)
for chunk in processor.stream_pages("large.pdf"):
    process(chunk)
```

---

### Q4: Windows 上 pdf2image 失敗

**問題**：`Unable to get page count. Is poppler installed and in PATH?`

**解決方案**：

需要安裝 poppler：
1. 下載 poppler：https://github.com/oschwartz10612/poppler-windows/releases
2. 解壓到 `C:\poppler`
3. 添加到環境變量 PATH：`C:\poppler\Library\bin`

---

### Q5: macOS 上安裝失敗

**問題**：缺少編譯工具

**解決方案**：
```bash
# 安裝 Xcode 命令行工具
xcode-select --install

# 使用 Homebrew 安裝依賴
brew install python@3.11
```

---

## 🔄 升級指南

### 升級到最新版本

```bash
# 拉取最新代碼
git pull origin main

# 升級依賴
pip install -r requirements.txt --upgrade
```

### 升級單個包

```bash
# 升級 pdfplumber
pip install --upgrade pdfplumber

# 升級 paddleocr
pip install --upgrade paddleocr
```

---

## 🗑️ 卸載

```bash
# 卸載所有依賴
pip uninstall -r requirements.txt -y

# 刪除項目目錄
cd ..
rm -rf exam-question-processor
```

---

## 📞 獲取幫助

如果遇到安裝問題：

1. 查看 [常見問題](../README.md#常見問題)
2. 查看 [GitHub Issues](https://github.com/yourusername/exam-question-processor/issues)
3. 提交新的 Issue

---

## 📚 下一步

安裝完成後，請閱讀：
- [快速開始指南](./QUICK_START.md)
- [API 文檔](./API_DOCUMENTATION.md)
- [貢獻指南](./CONTRIBUTING.md)

---

**最後更新**: 2025-11-17
**版本**: 1.7.0
