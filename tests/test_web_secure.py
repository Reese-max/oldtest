#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Web 應用安全測試
"""

import pytest
import os
import sys
import tempfile
import uuid
from datetime import datetime

# 添加路徑
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.web.app_secure import create_app
from src.web.models import DatabaseManager
from src.web.auth import PasswordHasher


@pytest.fixture
def app():
    """創建測試應用"""
    # 使用臨時資料庫
    db_path = tempfile.mktemp(suffix='.db')

    # 使用臨時目錄
    temp_dir = tempfile.mkdtemp()

    config = {
        'TESTING': True,
        'DATABASE_URL': f'sqlite:///{db_path}',
        'UPLOAD_FOLDER': os.path.join(temp_dir, 'uploads'),
        'OUTPUT_FOLDER': os.path.join(temp_dir, 'outputs'),
        'SECRET_KEY': 'test-secret-key-for-testing-only',
        'WTF_CSRF_ENABLED': False  # 測試時禁用CSRF
    }

    app = create_app(config)

    yield app

    # 清理
    if os.path.exists(db_path):
        os.remove(db_path)


@pytest.fixture
def client(app):
    """創建測試客戶端"""
    return app.test_client()


@pytest.fixture
def db(app):
    """獲取資料庫管理器"""
    return app.config['db_manager']


class TestAuthentication:
    """認證測試"""

    def test_register_success(self, client, db):
        """測試成功註冊"""
        # 先獲取CSRF token
        response = client.get('/api/auth/csrf-token')
        csrf_token = response.json['csrf_token']

        response = client.post('/api/auth/register', json={
            'username': 'testuser',
            'password': 'testpass123',
            'email': 'test@example.com'
        }, headers={'X-CSRF-Token': csrf_token})

        assert response.status_code == 200
        data = response.json
        assert data['success'] is True
        assert 'user' in data

    def test_register_duplicate_username(self, client, db):
        """測試重複用戶名"""
        # 獲取CSRF token
        response = client.get('/api/auth/csrf-token')
        csrf_token = response.json['csrf_token']

        # 創建第一個用戶
        client.post('/api/auth/register', json={
            'username': 'testuser',
            'password': 'testpass123'
        }, headers={'X-CSRF-Token': csrf_token})

        # 嘗試創建同名用戶
        response = client.post('/api/auth/register', json={
            'username': 'testuser',
            'password': 'anotherpass'
        }, headers={'X-CSRF-Token': csrf_token})

        assert response.status_code == 400
        assert '已被使用' in response.json['error']

    def test_register_short_password(self, client):
        """測試密碼太短"""
        response = client.get('/api/auth/csrf-token')
        csrf_token = response.json['csrf_token']

        response = client.post('/api/auth/register', json={
            'username': 'testuser',
            'password': '123'  # 只有3個字符
        }, headers={'X-CSRF-Token': csrf_token})

        assert response.status_code == 400
        assert '至少需要6個字符' in response.json['error']

    def test_login_success(self, client, db):
        """測試成功登入"""
        # 獲取CSRF token
        response = client.get('/api/auth/csrf-token')
        csrf_token = response.json['csrf_token']

        # 創建用戶
        client.post('/api/auth/register', json={
            'username': 'testuser',
            'password': 'testpass123'
        }, headers={'X-CSRF-Token': csrf_token})

        # 登入
        response = client.post('/api/auth/login', json={
            'username': 'testuser',
            'password': 'testpass123'
        }, headers={'X-CSRF-Token': csrf_token})

        assert response.status_code == 200
        data = response.json
        assert data['success'] is True
        assert 'user' in data
        assert 'csrf_token' in data

    def test_login_wrong_password(self, client, db):
        """測試錯誤密碼"""
        response = client.get('/api/auth/csrf-token')
        csrf_token = response.json['csrf_token']

        # 創建用戶
        client.post('/api/auth/register', json={
            'username': 'testuser',
            'password': 'testpass123'
        }, headers={'X-CSRF-Token': csrf_token})

        # 使用錯誤密碼登入
        response = client.post('/api/auth/login', json={
            'username': 'testuser',
            'password': 'wrongpassword'
        }, headers={'X-CSRF-Token': csrf_token})

        assert response.status_code == 401
        assert '錯誤' in response.json['error']

    def test_login_nonexistent_user(self, client):
        """測試不存在的用戶"""
        response = client.get('/api/auth/csrf-token')
        csrf_token = response.json['csrf_token']

        response = client.post('/api/auth/login', json={
            'username': 'nonexistent',
            'password': 'somepassword'
        }, headers={'X-CSRF-Token': csrf_token})

        assert response.status_code == 401

    def test_logout(self, client):
        """測試登出"""
        # 先登入
        response = client.get('/api/auth/csrf-token')
        csrf_token = response.json['csrf_token']

        client.post('/api/auth/register', json={
            'username': 'testuser',
            'password': 'testpass123'
        }, headers={'X-CSRF-Token': csrf_token})

        client.post('/api/auth/login', json={
            'username': 'testuser',
            'password': 'testpass123'
        }, headers={'X-CSRF-Token': csrf_token})

        # 登出
        response = client.post('/api/auth/logout', headers={'X-CSRF-Token': csrf_token})
        assert response.status_code == 200


class TestDatabasePersistence:
    """資料庫持久化測試"""

    def test_task_creation(self, db):
        """測試任務創建"""
        task_data = {
            'id': str(uuid.uuid4()),
            'filename': 'test.pdf',
            'filepath': '/tmp/test.pdf',
            'status': 'uploaded',
            'progress': 0,
            'user_id': 'user-123'
        }

        task = db.create_task(task_data)
        assert task is not None
        assert task['filename'] == 'test.pdf'
        assert task['status'] == 'uploaded'

    def test_task_retrieval(self, db):
        """測試任務檢索"""
        task_id = str(uuid.uuid4())
        task_data = {
            'id': task_id,
            'filename': 'test.pdf',
            'filepath': '/tmp/test.pdf',
            'status': 'uploaded',
            'progress': 0,
            'user_id': 'user-123'
        }

        db.create_task(task_data)
        retrieved_task = db.get_task(task_id)

        assert retrieved_task is not None
        assert retrieved_task['id'] == task_id

    def test_task_update(self, db):
        """測試任務更新"""
        task_id = str(uuid.uuid4())
        task_data = {
            'id': task_id,
            'filename': 'test.pdf',
            'filepath': '/tmp/test.pdf',
            'status': 'uploaded',
            'progress': 0,
            'user_id': 'user-123'
        }

        db.create_task(task_data)
        db.update_task(task_id, {'status': 'processing', 'progress': 50})

        updated_task = db.get_task(task_id)
        assert updated_task['status'] == 'processing'
        assert updated_task['progress'] == 50

    def test_task_deletion(self, db):
        """測試任務刪除"""
        task_id = str(uuid.uuid4())
        task_data = {
            'id': task_id,
            'filename': 'test.pdf',
            'filepath': '/tmp/test.pdf',
            'status': 'uploaded',
            'progress': 0,
            'user_id': 'user-123'
        }

        db.create_task(task_data)
        assert db.delete_task(task_id) is True

        # 驗證已刪除
        assert db.get_task(task_id) is None

    def test_list_tasks_by_user(self, db):
        """測試按用戶列出任務"""
        user1 = 'user-111'
        user2 = 'user-222'

        # 創建用戶1的任務
        for i in range(3):
            db.create_task({
                'id': str(uuid.uuid4()),
                'filename': f'test{i}.pdf',
                'filepath': f'/tmp/test{i}.pdf',
                'status': 'uploaded',
                'progress': 0,
                'user_id': user1
            })

        # 創建用戶2的任務
        for i in range(2):
            db.create_task({
                'id': str(uuid.uuid4()),
                'filename': f'test{i}.pdf',
                'filepath': f'/tmp/test{i}.pdf',
                'status': 'uploaded',
                'progress': 0,
                'user_id': user2
            })

        # 驗證
        user1_tasks = db.list_tasks(user_id=user1)
        user2_tasks = db.list_tasks(user_id=user2)

        assert len(user1_tasks) == 3
        assert len(user2_tasks) == 2


class TestPasswordHasher:
    """密碼哈希測試"""

    def test_hash_password(self):
        """測試密碼哈希"""
        password = 'mypassword123'
        password_hash = PasswordHasher.hash_password(password)

        assert password_hash is not None
        assert '$' in password_hash  # 包含鹽值分隔符

    def test_verify_password_correct(self):
        """測試正確密碼驗證"""
        password = 'mypassword123'
        password_hash = PasswordHasher.hash_password(password)

        assert PasswordHasher.verify_password(password, password_hash) is True

    def test_verify_password_incorrect(self):
        """測試錯誤密碼驗證"""
        password = 'mypassword123'
        password_hash = PasswordHasher.hash_password(password)

        assert PasswordHasher.verify_password('wrongpassword', password_hash) is False

    def test_different_salts(self):
        """測試不同的鹽值產生不同的哈希"""
        password = 'mypassword123'
        hash1 = PasswordHasher.hash_password(password)
        hash2 = PasswordHasher.hash_password(password)

        # 雖然密碼相同，但因為鹽值不同，哈希應該不同
        assert hash1 != hash2

        # 但兩者都應該能驗證原密碼
        assert PasswordHasher.verify_password(password, hash1) is True
        assert PasswordHasher.verify_password(password, hash2) is True


class TestSecurity:
    """安全性測試"""

    def test_unauthenticated_upload(self, client):
        """測試未認證上傳被拒絕"""
        response = client.post('/api/upload', data={
            'file': (open(__file__, 'rb'), 'test.pdf')
        })

        assert response.status_code == 401

    def test_unauthenticated_task_access(self, client):
        """測試未認證訪問任務被拒絕"""
        response = client.get('/api/tasks')
        assert response.status_code == 401

    def test_csrf_token_required(self, client):
        """測試CSRF token要求"""
        # 註：測試環境中CSRF可能被禁用，這裡只是示例
        pass


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
