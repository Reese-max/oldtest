# 考古題 PDF 解析系統 - 生產環境 Docker 鏡像
# 基於 Python 3.11 slim 版本以減少鏡像大小

FROM python:3.11-slim as base

# 設定環境變數
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    DEBIAN_FRONTEND=noninteractive

# 設定工作目錄
WORKDIR /app

# 安裝系統依賴（用於 OCR 和 PDF 處理）
RUN apt-get update && apt-get install -y --no-install-recommends \
    # OCR 依賴
    libgl1-mesa-glx \
    libglib2.0-0 \
    libgomp1 \
    # PDF 處理
    poppler-utils \
    # 工具
    curl \
    && rm -rf /var/lib/apt/lists/*

# =====================================
# 階段 1: 最小化版本（僅核心功能）
# =====================================
FROM base as minimal

# 複製依賴文件
COPY requirements-minimal.txt .

# 安裝最小化依賴
RUN pip install --no-cache-dir -r requirements-minimal.txt

# 複製源代碼
COPY src/ ./src/
COPY main.py .
COPY config.json config.yaml ./

# 創建輸出目錄
RUN mkdir -p output logs

# 暴露端口（如果需要 API）
EXPOSE 5000

# 健康檢查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import sys; sys.exit(0)"

# 預設命令
CMD ["python", "main.py", "--help"]

# =====================================
# 階段 2: 完整版本（包含 OCR）
# =====================================
FROM base as full

# 複製依賴文件
COPY requirements-minimal.txt requirements-ocr.txt ./

# 安裝完整依賴
RUN pip install --no-cache-dir -r requirements-minimal.txt && \
    pip install --no-cache-dir -r requirements-ocr.txt

# 複製源代碼
COPY src/ ./src/
COPY main.py .
COPY config.json config.yaml ./

# 創建必要的目錄
RUN mkdir -p output logs temp

# 暴露端口
EXPOSE 5000

# 健康檢查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import src.core.pdf_processor; sys.exit(0)" || exit 1

# 預設命令
CMD ["python", "main.py", "--help"]

# =====================================
# 階段 3: Web 版本（包含 Web 界面）
# =====================================
FROM full as web

# 安裝 Web 依賴
COPY requirements-web.txt .
RUN pip install --no-cache-dir -r requirements-web.txt

# 複製 Web 相關文件
COPY src/web/ ./src/web/
COPY run_web.py .

# 創建上傳目錄
RUN mkdir -p uploads

# 暴露 Web 端口
EXPOSE 5000

# 健康檢查（檢查 Web 服務）
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:5000/ || exit 1

# 啟動 Web 服務
CMD ["python", "run_web.py"]

# =====================================
# 階段 4: 開發版本（包含開發工具）
# =====================================
FROM web as dev

# 安裝開發依賴
COPY requirements-dev.txt .
RUN pip install --no-cache-dir -r requirements-dev.txt

# 複製測試文件
COPY tests/ ./tests/
COPY pytest.ini ./

# 安裝額外的開發工具
RUN pip install --no-cache-dir ipython jupyter

# 開發模式下不使用健康檢查
HEALTHCHECK NONE

# 開發模式預設命令（保持容器運行）
CMD ["python", "run_web.py", "--debug"]

# =====================================
# 預設使用 Web 版本
# =====================================
FROM web
