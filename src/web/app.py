#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Flask Web 應用主文件
"""

import os
import json
import logging
import time
from pathlib import Path
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_file, session, g
from flask_wtf.csrf import CSRFProtect, generate_csrf
from flask_compress import Compress
from werkzeug.utils import secure_filename
import uuid

# 導入核心處理器
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from src.processors.archaeology_processor import ArchaeologyProcessor
from src.utils.performance_monitor import PerformanceMonitor, global_monitor
from src.i18n import set_language, get_text
from src.services import crawler_service, ocr_service
from src.web.validators import InputValidator, validate_request_data


def create_app(config=None):
    """
    創建Flask應用

    Args:
        config: 配置字典

    Returns:
        Flask應用實例
    """
    app = Flask(__name__)

    # 配置
    app.config['SECRET_KEY'] = config.get('SECRET_KEY', 'exam-processor-secret-key-2025')
    app.config['UPLOAD_FOLDER'] = config.get('UPLOAD_FOLDER', '/tmp/exam_uploads')
    app.config['OUTPUT_FOLDER'] = config.get('OUTPUT_FOLDER', '/tmp/exam_outputs')
    app.config['MAX_CONTENT_LENGTH'] = config.get('MAX_CONTENT_LENGTH', 50 * 1024 * 1024)  # 50MB
    app.config['ALLOWED_EXTENSIONS'] = {'pdf'}
    app.config['WTF_CSRF_TIME_LIMIT'] = None  # CSRF token 不過期

    # 初始化 CSRF 保護
    csrf = CSRFProtect(app)

    # 初始化響應壓縮（P3-12）
    compress = Compress()
    compress.init_app(app)
    app.config['COMPRESS_MIMETYPES'] = [
        'text/html',
        'text/css',
        'text/javascript',
        'application/json',
        'application/javascript',
        'text/plain'
    ]
    app.config['COMPRESS_LEVEL'] = 6  # 壓縮級別 1-9
    app.config['COMPRESS_MIN_SIZE'] = 500  # 最小壓縮大小（字節）

    # 配置靜態資源緩存（P3-13）
    app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 31536000  # 1 年（靜態資源）

    # 配置日誌系統
    log_dir = config.get('LOG_FOLDER', '/tmp/exam_logs') if config else '/tmp/exam_logs'
    os.makedirs(log_dir, exist_ok=True)

    # 配置日誌格式
    log_format = logging.Formatter(
        '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
    )

    # 文件日誌處理器
    file_handler = logging.FileHandler(os.path.join(log_dir, 'app.log'), encoding='utf-8')
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(log_format)

    # 錯誤日誌處理器
    error_handler = logging.FileHandler(os.path.join(log_dir, 'error.log'), encoding='utf-8')
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(log_format)

    # 添加處理器到 app.logger
    app.logger.addHandler(file_handler)
    app.logger.addHandler(error_handler)
    app.logger.setLevel(logging.INFO)

    # 確保目錄存在
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)

    # 全局變量
    processor = ArchaeologyProcessor()
    performance_monitor = PerformanceMonitor()

    # 處理任務存儲（簡單實現，生產環境應使用數據庫）
    tasks = {}

    def allowed_file(filename):
        """檢查文件是否允許"""
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

    # ==================== 請求日誌中間件 ====================

    @app.before_request
    def before_request_logging():
        """請求前記錄"""
        g.start_time = time.time()
        g.request_id = str(uuid.uuid4())[:8]  # 短 ID 用於追蹤

        # 記錄請求信息（排除靜態文件和健康檢查）
        if not request.path.startswith('/static') and request.path != '/health':
            app.logger.info(
                f"[{g.request_id}] {request.method} {request.path} - "
                f"IP: {request.remote_addr} - "
                f"User-Agent: {request.headers.get('User-Agent', 'Unknown')[:100]}"
            )

    @app.after_request
    def after_request_logging(response):
        """請求後記錄和緩存設置"""
        # 排除靜態文件和健康檢查
        if not request.path.startswith('/static') and request.path != '/health':
            duration = time.time() - g.get('start_time', time.time())
            request_id = g.get('request_id', 'unknown')

            # 記錄響應信息
            app.logger.info(
                f"[{request_id}] {request.method} {request.path} - "
                f"Status: {response.status_code} - "
                f"Duration: {duration:.3f}s"
            )

            # 如果是錯誤響應，記錄詳細信息
            if response.status_code >= 400:
                app.logger.warning(
                    f"[{request_id}] Error Response - "
                    f"Status: {response.status_code} - "
                    f"Path: {request.path} - "
                    f"IP: {request.remote_addr}"
                )

        # 設置緩存頭（P3-13）
        # 靜態資源：長時間緩存
        if request.path.startswith('/static'):
            response.cache_control.public = True
            response.cache_control.max_age = 31536000  # 1 年
        # API 響應：不緩存
        elif request.path.startswith('/api'):
            response.cache_control.no_store = True
            response.cache_control.no_cache = True
            response.cache_control.must_revalidate = True
        # HTML 頁面：短時間緩存
        elif response.content_type and 'text/html' in response.content_type:
            response.cache_control.public = True
            response.cache_control.max_age = 300  # 5 分鐘

        return response

    # ==================== 路由 ====================

    @app.route('/')
    def index():
        """首頁"""
        return render_template('index.html')

    @app.route('/upload')
    def upload_page():
        """上傳頁面"""
        return render_template('upload.html')

    @app.route('/api/upload', methods=['POST'])
    def upload_file():
        """處理文件上傳"""
        try:
            if 'file' not in request.files:
                return jsonify({'error': get_text('errors.file_not_found', path='file')}), 400

            file = request.files['file']

            if file.filename == '':
                return jsonify({'error': get_text('errors.invalid_format', format='filename')}), 400

            # 驗證文件名
            is_valid, error, cleaned_filename = InputValidator.validate_filename(file.filename)
            if not is_valid:
                return jsonify({'error': error}), 400

            # 驗證文件大小
            file.seek(0, os.SEEK_END)
            file_size = file.tell()
            file.seek(0)

            is_valid, error = InputValidator.validate_file_size(file_size)
            if not is_valid:
                return jsonify({'error': error}), 400

            # 保存文件
            filename = cleaned_filename
            task_id = str(uuid.uuid4())
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            saved_filename = f"{task_id}_{timestamp}_{filename}"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], saved_filename)
            file.save(filepath)

            # 創建任務
            tasks[task_id] = {
                'id': task_id,
                'filename': filename,
                'filepath': filepath,
                'status': 'uploaded',
                'created_at': datetime.now().isoformat(),
                'progress': 0
            }

            # 記錄文件上傳日誌
            app.logger.info(
                f"[{g.get('request_id', 'unknown')}] File uploaded - "
                f"TaskID: {task_id}, Filename: {filename}, "
                f"Size: {file_size / 1024:.2f}KB, IP: {request.remote_addr}"
            )

            return jsonify({
                'success': True,
                'task_id': task_id,
                'filename': filename,
                'message': f'文件上傳成功: {filename}'
            })

        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/process/<task_id>', methods=['POST'])
    def process_task(task_id):
        """處理PDF文件"""
        try:
            # 驗證任務 ID
            is_valid, error = InputValidator.validate_task_id(task_id)
            if not is_valid:
                return jsonify({'error': error}), 400

            if task_id not in tasks:
                return jsonify({'error': '任務不存在'}), 404

            task = tasks[task_id]

            if task['status'] == 'processing':
                return jsonify({'error': '任務正在處理中'}), 400

            # 更新狀態
            task['status'] = 'processing'
            task['progress'] = 10
            task['started_at'] = datetime.now().isoformat()

            # 處理PDF
            filepath = task['filepath']
            output_dir = app.config['OUTPUT_FOLDER']

            # 使用性能監控
            performance_monitor.clear_metrics()

            # 執行處理
            result = processor.process_pdf(filepath)

            if result['status'] == 'success':
                # 生成輸出文件
                output_base = os.path.join(output_dir, task_id)
                csv_path = f"{output_base}.csv"
                script_path = f"{output_base}_script.gs"

                # 保存CSV
                import pandas as pd
                df = pd.DataFrame(result['questions'])
                df.to_csv(csv_path, index=False, encoding='utf-8-sig')

                # 生成Google Script（如果有）
                if 'google_script' in result:
                    with open(script_path, 'w', encoding='utf-8') as f:
                        f.write(result['google_script'])

                # 更新任務
                task['status'] = 'completed'
                task['progress'] = 100
                task['completed_at'] = datetime.now().isoformat()
                task['result'] = {
                    'question_count': result['question_count'],
                    'csv_path': csv_path,
                    'script_path': script_path if 'google_script' in result else None
                }

                # 性能統計
                task['performance'] = performance_monitor.get_metrics_summary()

                # 記錄處理完成日誌
                app.logger.info(
                    f"[{g.get('request_id', 'unknown')}] Task completed - "
                    f"TaskID: {task_id}, Questions: {result['question_count']}, "
                    f"Duration: {time.time() - g.get('start_time', time.time()):.2f}s"
                )

                return jsonify({
                    'success': True,
                    'task_id': task_id,
                    'result': task['result'],
                    'message': f'處理完成，共解析 {result["question_count"]} 題'
                })
            else:
                task['status'] = 'failed'
                task['error'] = result.get('error', '處理失敗')

                # 記錄處理失敗日誌
                app.logger.error(
                    f"[{g.get('request_id', 'unknown')}] Task failed - "
                    f"TaskID: {task_id}, Error: {task['error']}"
                )

                return jsonify({'error': task['error']}), 500

        except Exception as e:
            if task_id in tasks:
                tasks[task_id]['status'] = 'failed'
                tasks[task_id]['error'] = str(e)
            return jsonify({'error': str(e)}), 500

    @app.route('/api/task/<task_id>')
    def get_task(task_id):
        """獲取任務狀態"""
        # 驗證任務 ID
        is_valid, error = InputValidator.validate_task_id(task_id)
        if not is_valid:
            return jsonify({'error': error}), 400

        if task_id not in tasks:
            return jsonify({'error': '任務不存在'}), 404

        return jsonify(tasks[task_id])

    @app.route('/api/tasks')
    def get_tasks():
        """獲取所有任務"""
        task_list = list(tasks.values())
        # 按創建時間倒序排列
        task_list.sort(key=lambda x: x['created_at'], reverse=True)
        return jsonify(task_list)

    @app.route('/api/download/<task_id>/<file_type>')
    def download_file(task_id, file_type):
        """下載結果文件"""
        try:
            # 驗證任務 ID
            is_valid, error = InputValidator.validate_task_id(task_id)
            if not is_valid:
                return jsonify({'error': error}), 400

            # 驗證文件類型
            if file_type not in ['csv', 'script']:
                return jsonify({'error': '無效的文件類型'}), 400

            if task_id not in tasks:
                return jsonify({'error': '任務不存在'}), 404

            task = tasks[task_id]

            if task['status'] != 'completed':
                return jsonify({'error': '任務未完成'}), 400

            if file_type == 'csv':
                filepath = task['result']['csv_path']
                download_name = f"{task['filename'].rsplit('.', 1)[0]}.csv"
            elif file_type == 'script':
                filepath = task['result'].get('script_path')
                if not filepath:
                    return jsonify({'error': '無Google Script文件'}), 404
                download_name = f"{task['filename'].rsplit('.', 1)[0]}_script.gs"
            else:
                return jsonify({'error': '無效的文件類型'}), 400

            return send_file(filepath, as_attachment=True, download_name=download_name)

        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/delete/<task_id>', methods=['DELETE'])
    def delete_task(task_id):
        """刪除任務"""
        try:
            # 驗證任務 ID
            is_valid, error = InputValidator.validate_task_id(task_id)
            if not is_valid:
                return jsonify({'error': error}), 400

            if task_id not in tasks:
                return jsonify({'error': '任務不存在'}), 404

            task = tasks[task_id]

            # 刪除文件
            if os.path.exists(task['filepath']):
                os.remove(task['filepath'])

            if task['status'] == 'completed':
                csv_path = task['result'].get('csv_path')
                script_path = task['result'].get('script_path')

                if csv_path and os.path.exists(csv_path):
                    os.remove(csv_path)
                if script_path and os.path.exists(script_path):
                    os.remove(script_path)

            # 刪除任務
            del tasks[task_id]

            return jsonify({'success': True, 'message': '任務已刪除'})

        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/monitor')
    def monitor_page():
        """性能監控頁面"""
        return render_template('monitor.html')

    @app.route('/api/monitor/metrics')
    def get_metrics():
        """獲取性能指標"""
        try:
            summary = global_monitor.get_metrics_summary()
            all_stats = global_monitor.get_all_stats()

            return jsonify({
                'summary': summary,
                'stats': all_stats,
                'metrics': [m.to_dict() for m in global_monitor.metrics[-50:]]  # 最近50條
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/monitor/report')
    def get_monitor_report():
        """獲取性能報告"""
        try:
            report = global_monitor.generate_report()
            return jsonify({'report': report})
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/language/<lang_code>', methods=['POST'])
    def change_language(lang_code):
        """切換語言"""
        try:
            if set_language(lang_code):
                session['language'] = lang_code
                return jsonify({
                    'success': True,
                    'language': lang_code,
                    'message': get_text('i18n.language_changed', language=lang_code)
                })
            else:
                return jsonify({'error': get_text('i18n.language_not_supported', language=lang_code)}), 400
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    # ==================== 爬蟲 API ====================

    @app.route('/crawler')
    def crawler_page():
        """爬蟲控制台頁面"""
        return render_template('crawler.html')

    @app.route('/api/crawler/config')
    def get_crawler_config():
        """獲取爬蟲配置"""
        try:
            return jsonify({
                'success': True,
                'available_years': crawler_service.get_available_years(),
                'default_keywords': crawler_service.get_default_keywords()
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/crawler/start', methods=['POST'])
    def start_crawler():
        """啟動爬蟲任務"""
        try:
            data = request.get_json()

            # 驗證請求數據
            is_valid, error = validate_request_data(data, ['years', 'keywords'])
            if not is_valid:
                return jsonify({'error': error}), 400

            # 驗證年份
            is_valid, error, years = InputValidator.validate_years(data['years'])
            if not is_valid:
                return jsonify({'error': error}), 400

            # 驗證關鍵字
            is_valid, error, keywords = InputValidator.validate_keywords(data['keywords'])
            if not is_valid:
                return jsonify({'error': error}), 400

            # 驗證保存目錄（可選）
            save_dir = data.get('save_dir')
            if save_dir:
                is_valid, error, save_dir = InputValidator.validate_path(save_dir)
                if not is_valid:
                    return jsonify({'error': error}), 400
            else:
                save_dir = os.path.join(app.config['OUTPUT_FOLDER'], '考古題')

            # 創建任務
            task_id = crawler_service.create_task(years, keywords, save_dir)

            # 啟動任務
            if crawler_service.start_task(task_id):
                # 記錄爬蟲任務啟動日誌
                app.logger.info(
                    f"[{g.get('request_id', 'unknown')}] Crawler task started - "
                    f"TaskID: {task_id}, Years: {len(years)}, "
                    f"Keywords: {len(keywords)}, IP: {request.remote_addr}"
                )

                return jsonify({
                    'success': True,
                    'task_id': task_id,
                    'message': '爬蟲任務已啟動'
                })
            else:
                app.logger.error(
                    f"[{g.get('request_id', 'unknown')}] Crawler task start failed - "
                    f"TaskID: {task_id}"
                )
                return jsonify({'error': '啟動任務失敗'}), 500

        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/crawler/status/<task_id>')
    def get_crawler_status(task_id):
        """獲取爬蟲任務狀態"""
        # 驗證任務 ID
        is_valid, error = InputValidator.validate_task_id(task_id)
        if not is_valid:
            return jsonify({'error': error}), 400

        task = crawler_service.get_task(task_id)
        if not task:
            return jsonify({'error': '任務不存在'}), 404

        return jsonify(task)

    @app.route('/api/crawler/stop/<task_id>', methods=['POST'])
    def stop_crawler(task_id):
        """停止爬蟲任務"""
        # 驗證任務 ID
        is_valid, error = InputValidator.validate_task_id(task_id)
        if not is_valid:
            return jsonify({'error': error}), 400

        if crawler_service.stop_task(task_id):
            return jsonify({
                'success': True,
                'message': '任務已停止'
            })
        else:
            return jsonify({'error': '停止任務失敗'}), 400

    @app.route('/api/crawler/tasks')
    def get_crawler_tasks():
        """獲取所有爬蟲任務"""
        tasks = crawler_service.get_all_tasks()
        return jsonify(tasks)

    @app.route('/api/crawler/delete/<task_id>', methods=['DELETE'])
    def delete_crawler_task(task_id):
        """刪除爬蟲任務"""
        # 驗證任務 ID
        is_valid, error = InputValidator.validate_task_id(task_id)
        if not is_valid:
            return jsonify({'error': error}), 400

        if crawler_service.delete_task(task_id):
            return jsonify({
                'success': True,
                'message': '任務已刪除'
            })
        else:
            return jsonify({'error': '刪除任務失敗'}), 404

    # ==================== OCR API ====================

    @app.route('/ocr')
    def ocr_page():
        """OCR 控制台頁面"""
        return render_template('ocr.html')

    @app.route('/api/ocr/config')
    def get_ocr_config():
        """獲取 OCR 配置"""
        try:
            config = ocr_service.get_config()
            return jsonify({
                'success': True,
                'config': config
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/ocr/detect', methods=['POST'])
    def detect_pdf_type():
        """檢測 PDF 類型"""
        try:
            if 'file' not in request.files:
                return jsonify({'error': '未找到文件'}), 400

            file = request.files['file']
            if file.filename == '':
                return jsonify({'error': '文件名為空'}), 400

            # 驗證文件名
            is_valid, error, cleaned_filename = InputValidator.validate_filename(file.filename)
            if not is_valid:
                return jsonify({'error': error}), 400

            # 驗證文件大小
            file.seek(0, os.SEEK_END)
            file_size = file.tell()
            file.seek(0)

            is_valid, error = InputValidator.validate_file_size(file_size)
            if not is_valid:
                return jsonify({'error': error}), 400

            # 保存文件
            filename = cleaned_filename
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            # 檢測類型
            result = ocr_service.detect_pdf_type(filepath)

            return jsonify(result)

        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/ocr/optimize', methods=['POST'])
    def optimize_ocr_parameters():
        """優化 OCR 參數"""
        try:
            if 'file' not in request.files:
                return jsonify({'error': '未找到文件'}), 400

            file = request.files['file']
            if file.filename == '':
                return jsonify({'error': '文件名為空'}), 400

            # 驗證文件名
            is_valid, error, cleaned_filename = InputValidator.validate_filename(file.filename)
            if not is_valid:
                return jsonify({'error': error}), 400

            # 驗證文件大小
            file.seek(0, os.SEEK_END)
            file_size = file.tell()
            file.seek(0)

            is_valid, error = InputValidator.validate_file_size(file_size)
            if not is_valid:
                return jsonify({'error': error}), 400

            # 保存文件
            filename = cleaned_filename
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            # 優化參數
            result = ocr_service.optimize_parameters(filepath)

            return jsonify(result)

        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/health')
    @csrf.exempt  # 健康檢查不需要 CSRF 保護
    def health_check():
        """健康檢查"""
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'tasks_count': len(tasks),
            'version': '2.0.0'  # 更新版本號
        })

    @app.route('/api/csrf-token')
    def get_csrf_token():
        """獲取 CSRF Token"""
        token = generate_csrf()
        return jsonify({'csrf_token': token})

    # ==================== 錯誤處理器 ====================

    @app.errorhandler(400)
    def bad_request(error):
        """處理 400 錯誤請求"""
        return jsonify({
            'error': '請求格式錯誤',
            'message': str(error.description) if hasattr(error, 'description') else '無效的請求參數',
            'code': 400
        }), 400

    @app.errorhandler(404)
    def not_found(error):
        """處理 404 未找到錯誤"""
        return jsonify({
            'error': '資源不存在',
            'message': '請求的資源未找到',
            'code': 404
        }), 404

    @app.errorhandler(405)
    def method_not_allowed(error):
        """處理 405 方法不允許錯誤"""
        return jsonify({
            'error': '方法不允許',
            'message': '不支持的 HTTP 方法',
            'code': 405
        }), 405

    @app.errorhandler(413)
    def request_entity_too_large(error):
        """處理 413 請求實體過大錯誤"""
        max_mb = app.config.get('MAX_CONTENT_LENGTH', 50 * 1024 * 1024) / (1024 * 1024)
        return jsonify({
            'error': '文件過大',
            'message': f'文件大小超過限制（最大 {max_mb:.0f}MB）',
            'code': 413
        }), 413

    @app.errorhandler(500)
    def internal_server_error(error):
        """處理 500 內部服務器錯誤"""
        # 記錄錯誤到日誌
        app.logger.error(f'Internal Server Error: {str(error)}')
        return jsonify({
            'error': '服務器內部錯誤',
            'message': '服務器處理請求時發生錯誤，請稍後再試',
            'code': 500
        }), 500

    @app.errorhandler(Exception)
    def handle_exception(error):
        """處理所有未捕獲的異常"""
        # 記錄錯誤到日誌
        app.logger.error(f'Unhandled Exception: {str(error)}', exc_info=True)

        # 如果是 HTTP 異常，返回對應的狀態碼
        if hasattr(error, 'code'):
            return jsonify({
                'error': '請求錯誤',
                'message': str(error),
                'code': error.code
            }), error.code

        # 其他異常返回 500
        return jsonify({
            'error': '服務器錯誤',
            'message': '處理請求時發生意外錯誤',
            'code': 500
        }), 500

    return app


def run_app(host='127.0.0.1', port=5000, debug=True):
    """
    運行Flask應用

    Args:
        host: 主機地址
        port: 端口號
        debug: 調試模式
    """
    app = create_app()
    app.run(host=host, port=port, debug=debug)


if __name__ == '__main__':
    run_app()
