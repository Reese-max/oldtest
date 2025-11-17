#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
資料庫模型
使用 SQLAlchemy ORM
"""

from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

Base = declarative_base()


class Task(Base):
    """任務模型"""
    __tablename__ = 'tasks'

    id = Column(String(36), primary_key=True)  # UUID
    filename = Column(String(255), nullable=False)
    filepath = Column(String(512), nullable=False)
    status = Column(String(20), nullable=False, default='uploaded')
    # 狀態: uploaded, processing, completed, failed

    progress = Column(Integer, default=0)
    question_count = Column(Integer, nullable=True)

    csv_path = Column(String(512), nullable=True)
    script_path = Column(String(512), nullable=True)

    error_message = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)

    # 用戶ID（為未來的多用戶支持預留）
    user_id = Column(String(36), nullable=True)

    def to_dict(self):
        """轉換為字典"""
        return {
            'id': self.id,
            'filename': self.filename,
            'filepath': self.filepath,
            'status': self.status,
            'progress': self.progress,
            'question_count': self.question_count,
            'csv_path': self.csv_path,
            'script_path': self.script_path,
            'error_message': self.error_message,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'user_id': self.user_id
        }


class User(Base):
    """用戶模型"""
    __tablename__ = 'users'

    id = Column(String(36), primary_key=True)  # UUID
    username = Column(String(80), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    email = Column(String(120), unique=True, nullable=True)

    is_active = Column(Integer, default=1)  # SQLite doesn't have Boolean
    is_admin = Column(Integer, default=0)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_login = Column(DateTime, nullable=True)

    def to_dict(self):
        """轉換為字典（不包含密碼）"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'is_active': bool(self.is_active),
            'is_admin': bool(self.is_admin),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }


class DatabaseManager:
    """資料庫管理器"""

    def __init__(self, db_url='sqlite:///exam_tasks.db'):
        """
        初始化資料庫

        Args:
            db_url: 資料庫連接URL
                - SQLite: sqlite:///path/to/database.db
                - PostgreSQL: postgresql://user:password@localhost/dbname
        """
        self.engine = create_engine(db_url, echo=False)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

    def get_session(self):
        """獲取資料庫會話"""
        return self.Session()

    def create_task(self, task_data):
        """創建任務"""
        session = self.get_session()
        try:
            task = Task(**task_data)
            session.add(task)
            session.commit()
            result = task.to_dict()
            return result
        finally:
            session.close()

    def get_task(self, task_id):
        """獲取任務"""
        session = self.get_session()
        try:
            task = session.query(Task).filter_by(id=task_id).first()
            return task.to_dict() if task else None
        finally:
            session.close()

    def update_task(self, task_id, updates):
        """更新任務"""
        session = self.get_session()
        try:
            task = session.query(Task).filter_by(id=task_id).first()
            if not task:
                return None

            for key, value in updates.items():
                if hasattr(task, key):
                    setattr(task, key, value)

            session.commit()
            return task.to_dict()
        finally:
            session.close()

    def delete_task(self, task_id):
        """刪除任務"""
        session = self.get_session()
        try:
            task = session.query(Task).filter_by(id=task_id).first()
            if not task:
                return False

            session.delete(task)
            session.commit()
            return True
        finally:
            session.close()

    def list_tasks(self, user_id=None, limit=100):
        """列出任務"""
        session = self.get_session()
        try:
            query = session.query(Task)
            if user_id:
                query = query.filter_by(user_id=user_id)

            tasks = query.order_by(Task.created_at.desc()).limit(limit).all()
            return [task.to_dict() for task in tasks]
        finally:
            session.close()

    def create_user(self, user_data):
        """創建用戶"""
        session = self.get_session()
        try:
            user = User(**user_data)
            session.add(user)
            session.commit()
            return user.to_dict()
        finally:
            session.close()

    def get_user(self, user_id=None, username=None):
        """獲取用戶"""
        session = self.get_session()
        try:
            if user_id:
                user = session.query(User).filter_by(id=user_id).first()
            elif username:
                user = session.query(User).filter_by(username=username).first()
            else:
                return None

            return user if user else None
        finally:
            session.close()

    def update_user(self, user_id, updates):
        """更新用戶"""
        session = self.get_session()
        try:
            user = session.query(User).filter_by(id=user_id).first()
            if not user:
                return None

            for key, value in updates.items():
                if hasattr(user, key):
                    setattr(user, key, value)

            session.commit()
            return user.to_dict()
        finally:
            session.close()
