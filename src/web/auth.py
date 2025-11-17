#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
認證和授權模組
"""

import secrets
import hashlib
import uuid
from datetime import datetime, timedelta
from functools import wraps
from flask import session, request, jsonify, current_app


class PasswordHasher:
    """密碼哈希工具"""

    @staticmethod
    def hash_password(password, salt=None):
        """
        哈希密碼

        Args:
            password: 明文密碼
            salt: 鹽值（可選）

        Returns:
            (hash, salt) 元組
        """
        if salt is None:
            salt = secrets.token_hex(32)

        # 使用 PBKDF2 哈希算法
        hash_obj = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt.encode('utf-8'),
            100000  # 迭代次數
        )
        hash_hex = hash_obj.hex()

        # 組合 salt 和 hash
        password_hash = f"{salt}${hash_hex}"
        return password_hash

    @staticmethod
    def verify_password(password, password_hash):
        """
        驗證密碼

        Args:
            password: 明文密碼
            password_hash: 存儲的哈希值

        Returns:
            bool: 是否匹配
        """
        try:
            salt, stored_hash = password_hash.split('$')
            new_hash = PasswordHasher.hash_password(password, salt)
            return new_hash == password_hash
        except Exception:
            return False


class SessionManager:
    """會話管理器"""

    @staticmethod
    def create_session(user_id, username, is_admin=False):
        """創建用戶會話"""
        session['user_id'] = user_id
        session['username'] = username
        session['is_admin'] = is_admin
        session['login_time'] = datetime.utcnow().isoformat()

        # 生成 CSRF token
        session['csrf_token'] = secrets.token_hex(32)

    @staticmethod
    def destroy_session():
        """銷毀會話"""
        session.clear()

    @staticmethod
    def get_current_user():
        """獲取當前用戶"""
        return {
            'user_id': session.get('user_id'),
            'username': session.get('username'),
            'is_admin': session.get('is_admin', False),
            'login_time': session.get('login_time')
        }

    @staticmethod
    def is_authenticated():
        """檢查是否已認證"""
        return 'user_id' in session

    @staticmethod
    def get_csrf_token():
        """獲取 CSRF token"""
        if 'csrf_token' not in session:
            session['csrf_token'] = secrets.token_hex(32)
        return session['csrf_token']

    @staticmethod
    def verify_csrf_token(token):
        """驗證 CSRF token"""
        return token == session.get('csrf_token')


def login_required(f):
    """登入要求裝飾器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not SessionManager.is_authenticated():
            return jsonify({'error': '需要登入'}), 401
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    """管理員要求裝飾器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not SessionManager.is_authenticated():
            return jsonify({'error': '需要登入'}), 401

        user = SessionManager.get_current_user()
        if not user.get('is_admin'):
            return jsonify({'error': '需要管理員權限'}), 403

        return f(*args, **kwargs)
    return decorated_function


def csrf_protect(f):
    """CSRF 保護裝飾器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # GET, HEAD, OPTIONS 請求不需要 CSRF 保護
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return f(*args, **kwargs)

        # 檢查 CSRF token
        token = request.headers.get('X-CSRF-Token') or request.form.get('csrf_token')

        if not token:
            return jsonify({'error': 'CSRF token 缺失'}), 403

        if not SessionManager.verify_csrf_token(token):
            return jsonify({'error': 'CSRF token 無效'}), 403

        return f(*args, **kwargs)
    return decorated_function


class RateLimiter:
    """簡易速率限制器（基於記憶體）"""

    def __init__(self):
        self.requests = {}  # {ip: [(timestamp, count)]}
        self.max_requests = 100  # 每分鐘最大請求數
        self.window = 60  # 時間窗口（秒）

    def is_allowed(self, identifier):
        """
        檢查是否允許請求

        Args:
            identifier: 識別符（通常是 IP 地址）

        Returns:
            bool: 是否允許
        """
        now = datetime.utcnow()

        # 清理過期記錄
        if identifier in self.requests:
            self.requests[identifier] = [
                ts for ts in self.requests[identifier]
                if (now - ts).total_seconds() < self.window
            ]

        # 檢查請求數
        if identifier not in self.requests:
            self.requests[identifier] = []

        if len(self.requests[identifier]) >= self.max_requests:
            return False

        # 記錄請求
        self.requests[identifier].append(now)
        return True


def rate_limit(limiter):
    """速率限制裝飾器"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # 使用 IP 地址作為識別符
            identifier = request.remote_addr

            if not limiter.is_allowed(identifier):
                return jsonify({
                    'error': '請求過於頻繁，請稍後再試'
                }), 429

            return f(*args, **kwargs)
        return decorated_function
    return decorator


def generate_secret_key():
    """生成安全的 SECRET_KEY"""
    return secrets.token_hex(32)


def task_owner_required(f):
    """任務擁有者要求裝飾器"""
    @wraps(f)
    def decorated_function(task_id, *args, **kwargs):
        from flask import current_app

        if not SessionManager.is_authenticated():
            return jsonify({'error': '需要登入'}), 401

        # 從資料庫獲取任務
        db = current_app.config['db_manager']
        task = db.get_task(task_id)

        if not task:
            return jsonify({'error': '任務不存在'}), 404

        # 檢查擁有權
        current_user = SessionManager.get_current_user()
        if task['user_id'] != current_user['user_id'] and not current_user.get('is_admin'):
            return jsonify({'error': '無權訪問此任務'}), 403

        return f(task_id, *args, **kwargs)
    return decorated_function
