# Web 管理界面使用指南

本文檔詳細介紹考古題處理系統的 Web 管理界面功能、使用方法和配置選項。

## 📑 目錄

1. [簡介](#簡介)
2. [安裝](#安裝)
3. [快速開始](#快速開始)
4. [功能介紹](#功能介紹)
5. [API 參考](#api-參考)
6. [配置選項](#配置選項)
7. [部署指南](#部署指南)
8. [故障排除](#故障排除)

---

## 簡介

Web 管理界面提供了一個友好的圖形化界面，讓您可以通過瀏覽器輕鬆：

- 📤 **上傳 PDF 文件**：支持拖放和批量上傳
- ⚙️ **處理考古題**：一鍵處理，自動生成結果
- 📊 **監控進度**：即時查看處理狀態
- 📥 **下載結果**：下載 CSV 和 Google Script
- 📈 **性能監控**：查看系統性能指標
- 🌍 **多語言支持**：支持繁體中文、簡體中文、英文、日文

### 技術架構

- **後端**：Flask 2.3+（輕量級 Python Web 框架）
- **前端**：原生 JavaScript + CSS（無需編譯）
- **儲存**：檔案系統（開發環境）/ 可擴展至資料庫（生產環境）

---

## 安裝

### 方法 1：使用 requirements-web.txt（推薦）

```bash
# 安裝基本依賴
pip install -r requirements-minimal.txt

# 安裝 Web 界面依賴
pip install -r requirements-web.txt
```

### 方法 2：使用 setup.py

```bash
# 安裝基本功能 + Web 界面
pip install -e ".[web]"

# 或安裝完整功能（包含 OCR + Web）
pip install -e ".[full,web]"
```

### 驗證安裝

```bash
python -c "from src.web.app import create_app; print('✅ Web 依賴安裝成功')"
```

---

## 快速開始

### 1. 啟動 Web 服務器

**開發模式**（本機訪問）：
```bash
python run_web.py
```

**允許外部訪問**：
```bash
python run_web.py --host 0.0.0.0
```

**自訂端口**：
```bash
python run_web.py --port 8080
```

**生產模式**（關閉除錯）：
```bash
python run_web.py --no-debug --host 0.0.0.0
```

### 2. 訪問界面

服務器啟動後，在瀏覽器中打開：

```
http://127.0.0.1:5000
```

您將看到主頁，包含三個主要功能：

1. **上傳處理** - 上傳和處理 PDF 文件
2. **性能監控** - 查看系統性能指標
3. **系統設定** - 配置選項（未來功能）

### 3. 上傳和處理 PDF

#### 步驟 1：上傳文件

1. 點擊導航欄的「上傳處理」
2. 點擊「選擇文件」按鈕，或直接拖放 PDF 文件
3. 選擇一個或多個 PDF 文件
4. 點擊「開始上傳」

#### 步驟 2：處理文件

1. 上傳完成後，文件會出現在「任務列表」中
2. 點擊「處理」按鈕開始處理
3. 等待處理完成（狀態會從「上傳完成」變為「處理中」再到「已完成」）

#### 步驟 3：下載結果

處理完成後，您可以：

- 點擊「下載 CSV」獲取題目數據
- 點擊「下載 Google Script」獲取 Google Apps Script 代碼

---

## 功能介紹

### 1. 首頁（Dashboard）

首頁顯示系統概覽：

- **統計卡片**：
  - 總處理題數
  - 成功率
  - 平均處理時間
  - 待處理任務數

- **功能卡片**：
  - PDF 上傳處理
  - 性能監控
  - 批量處理
  - API 文檔

### 2. 上傳處理頁面

#### 文件上傳區

- **支持格式**：PDF（.pdf）
- **上傳方式**：
  - 點擊選擇文件
  - 拖放文件到上傳區
- **批量上傳**：支持一次上傳多個文件

#### 任務列表

每個任務顯示：

- **文件名**：上傳的 PDF 文件名
- **狀態**：
  - `上傳完成` - 文件已上傳，等待處理
  - `處理中` - 正在處理
  - `已完成` - 處理成功
  - `失敗` - 處理失敗
- **題數**：處理完成後顯示題目數量
- **操作按鈕**：
  - `處理` - 開始處理任務
  - `下載 CSV` - 下載題目數據
  - `下載 Script` - 下載 Google Script
  - `刪除` - 刪除任務

#### 自動刷新

任務列表每 5 秒自動刷新，無需手動重新整理頁面。

### 3. 性能監控頁面

#### 指標摘要

顯示關鍵性能指標：

- **總調用次數**：所有函數的總調用次數
- **平均執行時間**：所有函數的平均執行時間
- **記憶體使用**：當前記憶體使用量
- **最慢函數**：執行時間最長的函數

#### 函數統計表

顯示每個函數的詳細統計：

- 函數名稱
- 調用次數
- 平均時間（ms）
- 最小時間（ms）
- 最大時間（ms）

#### 最近指標列表

顯示最近 20 條性能記錄：

- 時間戳
- 函數名稱
- 執行時間（ms）
- 記憶體使用（MB）

#### 導出報告

點擊「下載報告」按鈕，可以下載完整的性能監控報告（JSON 格式）。

---

## API 參考

Web 界面提供了 RESTful API，您可以通過程式方式與系統互動。

### 基本 URL

```
http://127.0.0.1:5000/api
```

### 1. 文件上傳

**端點**：`POST /api/upload`

**請求**：
- Content-Type: `multipart/form-data`
- 參數：`file` - PDF 文件

**響應**：
```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "filename": "exam.pdf",
  "status": "uploaded"
}
```

**範例**：
```bash
curl -X POST http://127.0.0.1:5000/api/upload \
  -F "file=@exam.pdf"
```

```python
import requests

with open('exam.pdf', 'rb') as f:
    response = requests.post(
        'http://127.0.0.1:5000/api/upload',
        files={'file': f}
    )
    data = response.json()
    task_id = data['task_id']
```

### 2. 處理任務

**端點**：`POST /api/process/<task_id>`

**請求**：
- 無需請求體

**響應**：
```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "completed",
  "question_count": 50,
  "csv_path": "/path/to/result.csv",
  "script_path": "/path/to/script.gs"
}
```

**範例**：
```bash
curl -X POST http://127.0.0.1:5000/api/process/550e8400-e29b-41d4-a716-446655440000
```

```python
response = requests.post(f'http://127.0.0.1:5000/api/process/{task_id}')
result = response.json()
print(f"處理了 {result['question_count']} 題")
```

### 3. 查詢任務狀態

**端點**：`GET /api/task/<task_id>`

**響應**：
```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "filename": "exam.pdf",
  "status": "completed",
  "question_count": 50,
  "created_at": "2025-01-15T10:30:00"
}
```

**範例**：
```bash
curl http://127.0.0.1:5000/api/task/550e8400-e29b-41d4-a716-446655440000
```

### 4. 列出所有任務

**端點**：`GET /api/tasks`

**響應**：
```json
[
  {
    "task_id": "550e8400-e29b-41d4-a716-446655440000",
    "filename": "exam1.pdf",
    "status": "completed",
    "question_count": 50,
    "created_at": "2025-01-15T10:30:00"
  },
  {
    "task_id": "660e8400-e29b-41d4-a716-446655440001",
    "filename": "exam2.pdf",
    "status": "processing",
    "created_at": "2025-01-15T10:35:00"
  }
]
```

**範例**：
```bash
curl http://127.0.0.1:5000/api/tasks
```

### 5. 下載結果

**端點**：`GET /api/download/<task_id>/<file_type>`

**參數**：
- `file_type`: `csv` 或 `script`

**響應**：文件下載

**範例**：
```bash
# 下載 CSV
curl -O http://127.0.0.1:5000/api/download/550e8400-e29b-41d4-a716-446655440000/csv

# 下載 Google Script
curl -O http://127.0.0.1:5000/api/download/550e8400-e29b-41d4-a716-446655440000/script
```

### 6. 刪除任務

**端點**：`DELETE /api/delete/<task_id>`

**響應**：
```json
{
  "message": "任務已刪除"
}
```

**範例**：
```bash
curl -X DELETE http://127.0.0.1:5000/api/delete/550e8400-e29b-41d4-a716-446655440000
```

### 7. 性能監控

**端點**：`GET /api/monitor/metrics`

**響應**：
```json
{
  "summary": {
    "total_calls": 1523,
    "avg_time": 245.6,
    "memory_usage": 128.5,
    "slowest_function": "process_pdf"
  },
  "function_stats": {
    "process_pdf": {
      "count": 50,
      "avg_time": 1250.5,
      "min_time": 980.2,
      "max_time": 2100.8
    }
  },
  "recent_metrics": [
    {
      "timestamp": "2025-01-15T10:30:00",
      "function": "process_pdf",
      "execution_time": 1250.5,
      "memory_used": 128.5
    }
  ]
}
```

### 8. 切換語言

**端點**：`POST /api/language/<lang_code>`

**參數**：
- `lang_code`: `zh-TW`, `zh-CN`, `en`, `ja`

**響應**：
```json
{
  "language": "zh-TW",
  "message": "語言已切換"
}
```

### 9. 健康檢查

**端點**：`GET /health`

**響應**：
```json
{
  "status": "healthy",
  "version": "1.7.0",
  "uptime": 3600
}
```

---

## 配置選項

### 環境變數

您可以通過環境變數配置 Web 應用：

```bash
# 上傳文件存儲目錄
export UPLOAD_FOLDER=/var/exam_uploads

# 最大文件大小（位元組）
export MAX_CONTENT_LENGTH=52428800  # 50MB

# 啟用除錯模式
export FLASK_DEBUG=1

# 密鑰（用於 session）
export SECRET_KEY=your-secret-key-here
```

### 配置文件

創建 `config.yaml` 文件：

```yaml
# Web 服務器配置
web:
  host: 0.0.0.0
  port: 5000
  debug: false

  # 上傳配置
  upload_folder: /var/exam_uploads
  max_file_size: 52428800  # 50MB
  allowed_extensions:
    - pdf

  # 性能配置
  max_workers: 4  # 並發處理數
  timeout: 300    # 處理超時（秒）

  # 安全配置
  secret_key: your-secret-key-here
  enable_cors: false
  rate_limit: 100  # 每分鐘請求數限制
```

### 程式化配置

在 Python 代碼中配置：

```python
from src.web.app import run_app

config = {
    'UPLOAD_FOLDER': '/var/exam_uploads',
    'MAX_CONTENT_LENGTH': 50 * 1024 * 1024,  # 50MB
    'SECRET_KEY': 'your-secret-key'
}

run_app(host='0.0.0.0', port=5000, debug=False, config=config)
```

---

## 部署指南

### 開發環境

開發環境使用 Flask 內建服務器即可：

```bash
python run_web.py
```

### 生產環境

#### 方法 1：使用 Gunicorn（Linux/Mac）

1. **安裝 Gunicorn**：
```bash
pip install gunicorn
```

2. **啟動服務**：
```bash
gunicorn -w 4 -b 0.0.0.0:5000 "src.web.app:create_app()"
```

參數說明：
- `-w 4`：4 個工作進程
- `-b 0.0.0.0:5000`：綁定地址和端口
- `--timeout 300`：請求超時時間（秒）
- `--access-logfile -`：訪問日誌輸出到標準輸出

3. **完整啟動命令**：
```bash
gunicorn -w 4 \
  -b 0.0.0.0:5000 \
  --timeout 300 \
  --access-logfile - \
  --error-logfile - \
  "src.web.app:create_app()"
```

#### 方法 2：使用 Waitress（跨平台）

1. **安裝 Waitress**：
```bash
pip install waitress
```

2. **啟動服務**：
```bash
waitress-serve --host=0.0.0.0 --port=5000 src.web.app:create_app
```

#### 方法 3：使用 Docker

1. **創建 Dockerfile**：
```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements-minimal.txt requirements-web.txt ./
RUN pip install --no-cache-dir -r requirements-minimal.txt -r requirements-web.txt

COPY . .

EXPOSE 5000

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "src.web.app:create_app()"]
```

2. **構建映像**：
```bash
docker build -t exam-processor-web .
```

3. **運行容器**：
```bash
docker run -d -p 5000:5000 \
  -v /var/exam_uploads:/app/uploads \
  exam-processor-web
```

### Nginx 反向代理

配置 Nginx 作為反向代理：

```nginx
server {
    listen 80;
    server_name your-domain.com;

    client_max_body_size 50M;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # 增加超時時間（處理大文件）
        proxy_read_timeout 300;
        proxy_connect_timeout 300;
        proxy_send_timeout 300;
    }

    location /static {
        alias /path/to/src/web/static;
        expires 30d;
    }
}
```

### Systemd 服務（Linux）

創建 `/etc/systemd/system/exam-processor-web.service`：

```ini
[Unit]
Description=Exam Question Processor Web Interface
After=network.target

[Service]
Type=notify
User=www-data
Group=www-data
WorkingDirectory=/path/to/exam-processor
Environment="PATH=/path/to/venv/bin"
ExecStart=/path/to/venv/bin/gunicorn -w 4 -b 127.0.0.1:5000 "src.web.app:create_app()"
Restart=always

[Install]
WantedBy=multi-user.target
```

啟動服務：

```bash
sudo systemctl enable exam-processor-web
sudo systemctl start exam-processor-web
sudo systemctl status exam-processor-web
```

---

## 故障排除

### 問題 1：Flask 未安裝

**症狀**：
```
ModuleNotFoundError: No module named 'flask'
```

**解決方案**：
```bash
pip install -r requirements-web.txt
```

### 問題 2：端口已被佔用

**症狀**：
```
OSError: [Errno 48] Address already in use
```

**解決方案**：

1. 查找佔用端口的進程：
```bash
# Linux/Mac
lsof -i :5000

# Windows
netstat -ano | findstr :5000
```

2. 終止該進程或使用其他端口：
```bash
python run_web.py --port 8080
```

### 問題 3：上傳文件失敗

**症狀**：
```
413 Request Entity Too Large
```

**解決方案**：

調整最大文件大小：

```python
# 在 run_web.py 中
config = {
    'MAX_CONTENT_LENGTH': 100 * 1024 * 1024  # 100MB
}
run_app(config=config)
```

### 問題 4：處理超時

**症狀**：
處理大文件時，請求超時。

**解決方案**：

1. **增加 Flask 超時**（開發環境）：
   Flask 內建服務器沒有超時限制，問題可能在前端。

2. **增加 Gunicorn 超時**（生產環境）：
```bash
gunicorn -w 4 -b 0.0.0.0:5000 --timeout 600 "src.web.app:create_app()"
```

3. **使用異步處理**（建議）：
   將處理任務改為後台任務，使用 Celery 或 RQ。

### 問題 5：CORS 錯誤

**症狀**：
```
Access to fetch at 'http://...' from origin 'http://...' has been blocked by CORS policy
```

**解決方案**：

1. **安裝 Flask-CORS**：
```bash
pip install Flask-CORS
```

2. **啟用 CORS**（在 `src/web/app.py` 中）：
```python
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
```

### 問題 6：靜態文件未加載

**症狀**：
CSS/JS 文件 404。

**解決方案**：

檢查文件路徑和目錄結構：

```
src/web/
├── static/
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── app.js
└── templates/
    └── ...
```

確保 Flask 應用正確配置：

```python
app = Flask(__name__,
            static_folder='static',
            template_folder='templates')
```

### 問題 7：記憶體不足

**症狀**：
處理大量文件時系統記憶體不足。

**解決方案**：

1. **限制並發任務數**
2. **使用串流處理**（已在 `StreamingPDFProcessor` 中實現）
3. **增加系統記憶體**
4. **使用工作隊列**（Celery）分散負載

---

## 最佳實踐

### 安全性

1. **不要在生產環境使用除錯模式**
```bash
python run_web.py --no-debug
```

2. **使用強密鑰**
```python
import secrets
secret_key = secrets.token_hex(32)
```

3. **限制上傳文件大小**
```python
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB
```

4. **驗證文件類型**
```python
ALLOWED_EXTENSIONS = {'pdf'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
```

5. **使用 HTTPS**（生產環境必須）
```nginx
server {
    listen 443 ssl;
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    ...
}
```

### 性能優化

1. **使用生產級 WSGI 服務器**（Gunicorn/Waitress）
2. **啟用靜態文件緩存**（Nginx）
3. **使用 CDN**（如果有大量靜態資源）
4. **實現任務隊列**（Celery）處理長時間運行的任務
5. **使用資料庫**替代記憶體存儲（生產環境）

### 監控和日誌

1. **記錄所有錯誤**
```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
```

2. **監控性能指標**
   - 使用內建的性能監控頁面
   - 整合 Prometheus/Grafana（進階）

3. **健康檢查**
```bash
# 定期檢查服務健康
curl http://127.0.0.1:5000/health
```

---

## 進階功能

### 1. 整合任務隊列（Celery）

將長時間運行的 PDF 處理任務放到後台：

```bash
# 安裝 Celery
pip install celery redis

# 啟動 Redis
redis-server

# 啟動 Celery worker
celery -A src.web.tasks worker --loglevel=info
```

### 2. WebSocket 即時更新

使用 Flask-SocketIO 實現即時進度更新：

```bash
pip install flask-socketio
```

### 3. 用戶認證

使用 Flask-Login 實現用戶登入：

```bash
pip install flask-login
```

### 4. 資料庫整合

使用 SQLAlchemy 存儲任務資訊：

```bash
pip install flask-sqlalchemy
```

---

## 總結

Web 管理界面提供了一個直觀、易用的方式來處理考古題 PDF 文件。通過本指南，您應該能夠：

✅ 安裝和啟動 Web 服務器
✅ 使用界面上傳和處理 PDF
✅ 通過 API 整合到其他系統
✅ 部署到生產環境
✅ 解決常見問題

如需更多幫助，請參考：

- [API 文檔](API_DOCUMENTATION.md)
- [快速開始](QUICK_START.md)
- [安裝指南](INSTALLATION.md)
- [性能監控指南](../examples/performance_monitoring_example.py)

祝您使用愉快！ 🎉
