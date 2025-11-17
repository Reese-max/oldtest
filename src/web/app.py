#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Flask Web 應用主文件
"""

import os
import json
from pathlib import Path
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_file, session
from werkzeug.utils import secure_filename
import uuid

# 導入核心處理器
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from src.processors.archaeology_processor import ArchaeologyProcessor
from src.utils.performance_monitor import PerformanceMonitor, global_monitor
from src.i18n import set_language, get_text


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

            if not allowed_file(file.filename):
                return jsonify({'error': '只允許上傳PDF文件'}), 400

            # 保存文件
            filename = secure_filename(file.filename)
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

                return jsonify({
                    'success': True,
                    'task_id': task_id,
                    'result': task['result'],
                    'message': f'處理完成，共解析 {result["question_count"]} 題'
                })
            else:
                task['status'] = 'failed'
                task['error'] = result.get('error', '處理失敗')
                return jsonify({'error': task['error']}), 500

        except Exception as e:
            if task_id in tasks:
                tasks[task_id]['status'] = 'failed'
                tasks[task_id]['error'] = str(e)
            return jsonify({'error': str(e)}), 500

    @app.route('/api/task/<task_id>')
    def get_task(task_id):
        """獲取任務狀態"""
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

    @app.route('/health')
    def health_check():
        """健康檢查"""
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'tasks_count': len(tasks),
            'version': '1.9.0'
        })

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
