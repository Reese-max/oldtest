#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Flask Web 應用主文件 - 安全加固版
"""

import os
import sys
import uuid
import secrets
from pathlib import Path
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for
from werkzeug.utils import secure_filename

# 導入核心處理器
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from src.processors.archaeology_processor import ArchaeologyProcessor
from src.utils.performance_monitor import PerformanceMonitor
from src.i18n import set_language, get_text

# 導入Web模組
from src.web.models import DatabaseManager
from src.web.auth import (
    PasswordHasher, SessionManager,
    login_required, admin_required, csrf_protect, task_owner_required,
    RateLimiter, rate_limit, generate_secret_key
)


def create_app(config=None):
    """
    創建Flask應用（安全加固版）

    Args:
        config: 配置字典

    Returns:
        Flask應用實例
    """
    if config is None:
        config = {}

    app = Flask(__name__)

    # ==================== 安全配置 ====================

    # 生成或使用環境變數中的 SECRET_KEY
    secret_key = os.environ.get('SECRET_KEY')
    if not secret_key:
        # 從配置文件讀取或生成新的
        secret_key = config.get('SECRET_KEY')
        if not secret_key or secret_key == 'exam-processor-secret-key-2025':
            # 如果沒有配置或使用默認值，生成新的並警告
            secret_key = generate_secret_key()
            print("⚠️  警告: 使用臨時生成的 SECRET_KEY")
            print("⚠️  生產環境請設置環境變數 SECRET_KEY")
            print(f"⚠️  建議值: export SECRET_KEY='{secret_key}'")

    app.config['SECRET_KEY'] = secret_key

    # Session 安全配置
    app.config['SESSION_COOKIE_SECURE'] = config.get('SESSION_COOKIE_SECURE', False)  # HTTPS 環境設為 True
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    app.config['PERMANENT_SESSION_LIFETIME'] = 3600  # 1小時

    # ==================== 基本配置 ====================

    app.config['UPLOAD_FOLDER'] = config.get('UPLOAD_FOLDER', './uploads')
    app.config['OUTPUT_FOLDER'] = config.get('OUTPUT_FOLDER', './outputs')
    app.config['MAX_CONTENT_LENGTH'] = config.get('MAX_CONTENT_LENGTH', 50 * 1024 * 1024)
    app.config['ALLOWED_EXTENSIONS'] = {'pdf'}

    # 資料庫配置
    db_url = config.get('DATABASE_URL', 'sqlite:///exam_tasks.db')
    app.config['DATABASE_URL'] = db_url

    # 確保目錄存在
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)

    # ==================== 初始化組件 ====================

    # 資料庫
    db_manager = DatabaseManager(db_url)
    app.config['db_manager'] = db_manager

    # 核心處理器
    processor = ArchaeologyProcessor()
    performance_monitor = PerformanceMonitor()

    # 速率限制器
    rate_limiter = RateLimiter()

    # ==================== 工具函數 ====================

    def allowed_file(filename):
        """檢查文件是否允許"""
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

    def get_safe_filepath(user_id, filename):
        """
        獲取安全的文件路徑（防止路徑遍歷）

        Args:
            user_id: 用戶ID
            filename: 文件名

        Returns:
            安全的文件路徑
        """
        # 確保文件名安全
        safe_filename = secure_filename(filename)

        # 使用用戶ID創建獨立目錄
        user_upload_dir = os.path.join(app.config['UPLOAD_FOLDER'], user_id)
        os.makedirs(user_upload_dir, exist_ok=True)

        # 生成唯一文件名
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        unique_filename = f"{timestamp}_{safe_filename}"

        return os.path.join(user_upload_dir, unique_filename)

    # ==================== 初始化默認管理員 ====================

    def init_default_admin():
        """初始化默認管理員賬戶"""
        admin = db_manager.get_user(username='admin')
        if not admin:
            admin_password = os.environ.get('ADMIN_PASSWORD', 'admin123')
            password_hash = PasswordHasher.hash_password(admin_password)

            db_manager.create_user({
                'id': str(uuid.uuid4()),
                'username': 'admin',
                'password_hash': password_hash,
                'email': 'admin@example.com',
                'is_active': 1,
                'is_admin': 1
            })

            print("✅ 默認管理員已創建")
            print(f"   用戶名: admin")
            print(f"   密碼: {admin_password}")
            if admin_password == 'admin123':
                print("⚠️  警告: 請立即修改默認密碼！")

    with app.app_context():
        init_default_admin()

    # ==================== 認證路由 ====================

    @app.route('/api/auth/register', methods=['POST'])
    @csrf_protect
    @rate_limit(rate_limiter)
    def register():
        """用戶註冊"""
        try:
            data = request.get_json()
            username = data.get('username', '').strip()
            password = data.get('password', '')
            email = data.get('email', '').strip()

            # 驗證輸入
            if not username or len(username) < 3:
                return jsonify({'error': '用戶名至少需要3個字符'}), 400

            if not password or len(password) < 6:
                return jsonify({'error': '密碼至少需要6個字符'}), 400

            # 檢查用戶是否已存在
            existing_user = db_manager.get_user(username=username)
            if existing_user:
                return jsonify({'error': '用戶名已被使用'}), 400

            # 創建用戶
            password_hash = PasswordHasher.hash_password(password)
            user_data = {
                'id': str(uuid.uuid4()),
                'username': username,
                'password_hash': password_hash,
                'email': email if email else None,
                'is_active': 1,
                'is_admin': 0
            }

            user = db_manager.create_user(user_data)

            return jsonify({
                'success': True,
                'message': '註冊成功',
                'user': user
            })

        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/auth/login', methods=['POST'])
    @csrf_protect
    @rate_limit(rate_limiter)
    def login():
        """用戶登入"""
        try:
            data = request.get_json()
            username = data.get('username', '').strip()
            password = data.get('password', '')

            if not username or not password:
                return jsonify({'error': '用戶名和密碼不能為空'}), 400

            # 獲取用戶
            user = db_manager.get_user(username=username)
            if not user:
                return jsonify({'error': '用戶名或密碼錯誤'}), 401

            # 驗證密碼
            if not PasswordHasher.verify_password(password, user.password_hash):
                return jsonify({'error': '用戶名或密碼錯誤'}), 401

            # 檢查賬戶狀態
            if not user.is_active:
                return jsonify({'error': '賬戶已被停用'}), 403

            # 創建會話
            SessionManager.create_session(
                user.id,
                user.username,
                bool(user.is_admin)
            )

            # 更新最後登入時間
            db_manager.update_user(user.id, {'last_login': datetime.utcnow()})

            return jsonify({
                'success': True,
                'message': '登入成功',
                'user': user.to_dict(),
                'csrf_token': SessionManager.get_csrf_token()
            })

        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/auth/logout', methods=['POST'])
    @login_required
    @csrf_protect
    def logout():
        """用戶登出"""
        SessionManager.destroy_session()
        return jsonify({'success': True, 'message': '已登出'})

    @app.route('/api/auth/me')
    @login_required
    def get_current_user():
        """獲取當前用戶信息"""
        user = SessionManager.get_current_user()
        return jsonify(user)

    @app.route('/api/auth/csrf-token')
    def get_csrf_token():
        """獲取 CSRF token"""
        return jsonify({'csrf_token': SessionManager.get_csrf_token()})

    # ==================== 主頁路由 ====================

    @app.route('/')
    def index():
        """首頁"""
        return render_template('index.html')

    @app.route('/login')
    def login_page():
        """登入頁面"""
        if SessionManager.is_authenticated():
            return redirect(url_for('index'))
        return render_template('login.html')

    @app.route('/upload')
    @login_required
    def upload_page():
        """上傳頁面"""
        return render_template('upload.html')

    @app.route('/monitor')
    @login_required
    def monitor_page():
        """監控頁面"""
        return render_template('monitor.html')

    # ==================== 任務管理路由 ====================

    @app.route('/api/upload', methods=['POST'])
    @login_required
    @csrf_protect
    @rate_limit(rate_limiter)
    def upload_file():
        """處理文件上傳"""
        try:
            if 'file' not in request.files:
                return jsonify({'error': '沒有文件'}), 400

            file = request.files['file']

            if file.filename == '':
                return jsonify({'error': '文件名無效'}), 400

            if not allowed_file(file.filename):
                return jsonify({'error': '只允許上傳PDF文件'}), 400

            # 獲取當前用戶
            current_user = SessionManager.get_current_user()
            user_id = current_user['user_id']

            # 生成安全的文件路徑
            filepath = get_safe_filepath(user_id, file.filename)
            file.save(filepath)

            # 創建任務記錄
            task_data = {
                'id': str(uuid.uuid4()),
                'filename': file.filename,
                'filepath': filepath,
                'status': 'uploaded',
                'progress': 0,
                'user_id': user_id
            }

            task = db_manager.create_task(task_data)

            return jsonify({
                'success': True,
                'task_id': task['id'],
                'filename': task['filename'],
                'message': f'文件上傳成功: {file.filename}'
            })

        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/process/<task_id>', methods=['POST'])
    @login_required
    @csrf_protect
    @task_owner_required
    @rate_limit(rate_limiter)
    def process_task(task_id):
        """處理PDF文件"""
        try:
            task = db_manager.get_task(task_id)

            if task['status'] == 'processing':
                return jsonify({'error': '任務正在處理中'}), 400

            # 更新狀態
            db_manager.update_task(task_id, {
                'status': 'processing',
                'progress': 10,
                'started_at': datetime.utcnow()
            })

            # 處理PDF
            filepath = task['filepath']

            # 安全檢查：確保文件路徑在允許的目錄內
            if not os.path.abspath(filepath).startswith(os.path.abspath(app.config['UPLOAD_FOLDER'])):
                db_manager.update_task(task_id, {
                    'status': 'failed',
                    'error_message': '文件路徑無效'
                })
                return jsonify({'error': '文件路徑無效'}), 400

            # 檢查文件是否存在
            if not os.path.exists(filepath):
                db_manager.update_task(task_id, {
                    'status': 'failed',
                    'error_message': '文件不存在'
                })
                return jsonify({'error': '文件不存在'}), 404

            # 執行處理
            performance_monitor.clear_metrics()
            result = processor.process_pdf(filepath)

            if result['status'] == 'success':
                # 生成輸出文件
                current_user = SessionManager.get_current_user()
                user_id = current_user['user_id']

                output_dir = os.path.join(app.config['OUTPUT_FOLDER'], user_id)
                os.makedirs(output_dir, exist_ok=True)

                output_base = os.path.join(output_dir, task_id)
                csv_path = f"{output_base}.csv"
                script_path = f"{output_base}_script.gs"

                # 保存CSV
                import pandas as pd
                df = pd.DataFrame(result['questions'])
                df.to_csv(csv_path, index=False, encoding='utf-8-sig')

                # 保存Google Script
                if result.get('google_script'):
                    with open(script_path, 'w', encoding='utf-8') as f:
                        f.write(result['google_script'])

                # 更新任務
                db_manager.update_task(task_id, {
                    'status': 'completed',
                    'progress': 100,
                    'question_count': result['question_count'],
                    'csv_path': csv_path,
                    'script_path': script_path if result.get('google_script') else None,
                    'completed_at': datetime.utcnow()
                })

                return jsonify({
                    'success': True,
                    'task_id': task_id,
                    'question_count': result['question_count'],
                    'message': f'處理完成，共 {result["question_count"]} 題'
                })

            else:
                # 處理失敗
                error_msg = result.get('message', '處理失敗')
                db_manager.update_task(task_id, {
                    'status': 'failed',
                    'error_message': error_msg,
                    'completed_at': datetime.utcnow()
                })

                return jsonify({'error': error_msg}), 500

        except Exception as e:
            db_manager.update_task(task_id, {
                'status': 'failed',
                'error_message': str(e),
                'completed_at': datetime.utcnow()
            })
            return jsonify({'error': str(e)}), 500

    @app.route('/api/task/<task_id>')
    @login_required
    @task_owner_required
    def get_task(task_id):
        """獲取任務狀態"""
        task = db_manager.get_task(task_id)
        return jsonify(task)

    @app.route('/api/tasks')
    @login_required
    def list_tasks():
        """列出當前用戶的所有任務"""
        current_user = SessionManager.get_current_user()
        user_id = current_user['user_id']

        # 管理員可以看所有任務
        if current_user.get('is_admin'):
            tasks = db_manager.list_tasks()
        else:
            tasks = db_manager.list_tasks(user_id=user_id)

        return jsonify(tasks)

    @app.route('/api/download/<task_id>/<file_type>')
    @login_required
    @task_owner_required
    def download_file(task_id, file_type):
        """下載結果文件"""
        try:
            task = db_manager.get_task(task_id)

            if task['status'] != 'completed':
                return jsonify({'error': '任務未完成'}), 400

            if file_type == 'csv':
                filepath = task['csv_path']
                download_name = f"{task['filename'].rsplit('.', 1)[0]}.csv"
            elif file_type == 'script':
                filepath = task.get('script_path')
                if not filepath:
                    return jsonify({'error': '無Google Script文件'}), 404
                download_name = f"{task['filename'].rsplit('.', 1)[0]}_script.gs"
            else:
                return jsonify({'error': '無效的文件類型'}), 400

            # 安全檢查：確保文件在允許的目錄內
            if not os.path.abspath(filepath).startswith(os.path.abspath(app.config['OUTPUT_FOLDER'])):
                return jsonify({'error': '文件路徑無效'}), 400

            if not os.path.exists(filepath):
                return jsonify({'error': '文件不存在'}), 404

            return send_file(filepath, as_attachment=True, download_name=download_name)

        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/delete/<task_id>', methods=['DELETE'])
    @login_required
    @csrf_protect
    @task_owner_required
    def delete_task(task_id):
        """刪除任務"""
        try:
            task = db_manager.get_task(task_id)

            # 刪除文件
            files_to_delete = [task['filepath']]
            if task['status'] == 'completed':
                if task.get('csv_path'):
                    files_to_delete.append(task['csv_path'])
                if task.get('script_path'):
                    files_to_delete.append(task['script_path'])

            for filepath in files_to_delete:
                if filepath and os.path.exists(filepath):
                    # 安全檢查
                    abs_path = os.path.abspath(filepath)
                    if abs_path.startswith(os.path.abspath(app.config['UPLOAD_FOLDER'])) or \
                       abs_path.startswith(os.path.abspath(app.config['OUTPUT_FOLDER'])):
                        os.remove(filepath)

            # 從資料庫刪除
            db_manager.delete_task(task_id)

            return jsonify({'success': True, 'message': '任務已刪除'})

        except Exception as e:
            return jsonify({'error': str(e)}), 500

    # ==================== 性能監控路由 ====================

    @app.route('/api/monitor/metrics')
    @login_required
    def get_metrics():
        """獲取性能指標"""
        try:
            metrics = performance_monitor.get_summary()
            return jsonify(metrics)
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    # ==================== 健康檢查 ====================

    @app.route('/health')
    def health_check():
        """健康檢查"""
        return jsonify({
            'status': 'healthy',
            'version': '2.0.0',
            'database': 'connected'
        })

    return app


def run_app(host='127.0.0.1', port=5000, debug=False, config=None):
    """
    運行Flask應用

    Args:
        host: 監聽地址
        port: 監聽端口
        debug: 除錯模式
        config: 配置字典
    """
    app = create_app(config)
    app.run(host=host, port=port, debug=debug)


if __name__ == '__main__':
    run_app(debug=True)
