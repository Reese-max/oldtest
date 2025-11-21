#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
輸入驗證和清理工具
提供安全的輸入驗證和數據清理功能
"""

import os
import re
from typing import Any, List, Optional, Tuple, Union

from werkzeug.utils import secure_filename


class InputValidator:
    """輸入驗證器"""

    # 允許的文件擴展名
    ALLOWED_EXTENSIONS = {"pdf"}

    # 最大文件大小（50MB）
    MAX_FILE_SIZE = 50 * 1024 * 1024

    # 年份範圍（民國年）
    MIN_YEAR = 60
    MAX_YEAR = 150

    # 關鍵字最大長度
    MAX_KEYWORD_LENGTH = 100

    # 路徑最大長度
    MAX_PATH_LENGTH = 500

    @staticmethod
    def validate_year(year: Any) -> Tuple[bool, Optional[str]]:
        """
        驗證年份

        Args:
            year: 年份值

        Returns:
            (是否有效, 錯誤訊息)
        """
        if not isinstance(year, int):
            try:
                year = int(year)
            except (ValueError, TypeError):
                return False, "年份必須是整數"

        if year < InputValidator.MIN_YEAR or year > InputValidator.MAX_YEAR:
            return False, f"年份必須在 {InputValidator.MIN_YEAR} 到 {InputValidator.MAX_YEAR} 之間"

        return True, None

    @staticmethod
    def validate_years(years: Any) -> Tuple[bool, Optional[str], List[int]]:
        """
        驗證年份列表

        Args:
            years: 年份列表

        Returns:
            (是否有效, 錯誤訊息, 清理後的年份列表)
        """
        if not isinstance(years, list):
            return False, "年份必須是列表", []

        if len(years) == 0:
            return False, "至少需要選擇一個年份", []

        if len(years) > 50:
            return False, "年份選擇過多（最多50個）", []

        cleaned_years = []
        for year in years:
            is_valid, error = InputValidator.validate_year(year)
            if not is_valid:
                return False, error, []
            cleaned_years.append(int(year))

        return True, None, cleaned_years

    @staticmethod
    def validate_keyword(keyword: Any) -> Tuple[bool, Optional[str]]:
        """
        驗證關鍵字

        Args:
            keyword: 關鍵字

        Returns:
            (是否有效, 錯誤訊息)
        """
        if not isinstance(keyword, str):
            return False, "關鍵字必須是字符串"

        if len(keyword) == 0:
            return False, "關鍵字不能為空"

        if len(keyword) > InputValidator.MAX_KEYWORD_LENGTH:
            return False, f"關鍵字長度不能超過 {InputValidator.MAX_KEYWORD_LENGTH} 個字符"

        # 檢查是否包含危險字符
        dangerous_chars = ["<", ">", '"', "'", ";", "&", "|", "`", "\n", "\r"]
        if any(char in keyword for char in dangerous_chars):
            return False, "關鍵字包含非法字符"

        return True, None

    @staticmethod
    def validate_keywords(keywords: Any) -> Tuple[bool, Optional[str], List[str]]:
        """
        驗證關鍵字列表

        Args:
            keywords: 關鍵字列表

        Returns:
            (是否有效, 錯誤訊息, 清理後的關鍵字列表)
        """
        if not isinstance(keywords, list):
            return False, "關鍵字必須是列表", []

        if len(keywords) == 0:
            return False, "至少需要選擇一個關鍵字", []

        if len(keywords) > 20:
            return False, "關鍵字選擇過多（最多20個）", []

        cleaned_keywords = []
        for keyword in keywords:
            is_valid, error = InputValidator.validate_keyword(keyword)
            if not is_valid:
                return False, error, []
            cleaned_keywords.append(keyword.strip())

        return True, None, cleaned_keywords

    @staticmethod
    def validate_path(path: Any) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        驗證並清理文件路徑

        Args:
            path: 文件路徑

        Returns:
            (是否有效, 錯誤訊息, 清理後的路徑)
        """
        if path is None or path == "":
            return True, None, None

        if not isinstance(path, str):
            return False, "路徑必須是字符串", None

        if len(path) > InputValidator.MAX_PATH_LENGTH:
            return False, f"路徑長度不能超過 {InputValidator.MAX_PATH_LENGTH} 個字符", None

        # 檢查路徑遍歷攻擊
        if ".." in path or path.startswith("/"):
            return False, "路徑包含非法字符", None

        # 清理路徑
        cleaned_path = os.path.normpath(path)

        # 再次檢查清理後的路徑
        if ".." in cleaned_path:
            return False, "路徑包含非法字符", None

        return True, None, cleaned_path

    @staticmethod
    def validate_filename(filename: Any) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        驗證並清理文件名

        Args:
            filename: 文件名

        Returns:
            (是否有效, 錯誤訊息, 清理後的文件名)
        """
        if not filename or not isinstance(filename, str):
            return False, "文件名無效", None

        # 使用 Werkzeug 的 secure_filename
        cleaned_filename = secure_filename(filename)

        if not cleaned_filename:
            return False, "文件名包含非法字符", None

        # 檢查文件擴展名
        if "." not in cleaned_filename:
            return False, "文件缺少擴展名", None

        ext = cleaned_filename.rsplit(".", 1)[1].lower()
        if ext not in InputValidator.ALLOWED_EXTENSIONS:
            return False, f"不支持的文件類型（僅支持: {', '.join(InputValidator.ALLOWED_EXTENSIONS)}）", None

        return True, None, cleaned_filename

    @staticmethod
    def sanitize_string(text: str, max_length: int = 1000) -> str:
        """
        清理字符串，防止 XSS 攻擊

        Args:
            text: 原始字符串
            max_length: 最大長度

        Returns:
            清理後的字符串
        """
        if not isinstance(text, str):
            return ""

        # 截斷長度
        text = text[:max_length]

        # 移除危險字符
        text = re.sub(r"[<>\"\'&]", "", text)

        # 移除控制字符（保留換行和製表符）
        text = re.sub(r"[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]", "", text)

        return text.strip()

    @staticmethod
    def validate_task_id(task_id: Any) -> Tuple[bool, Optional[str]]:
        """
        驗證任務 ID（UUID 格式）

        Args:
            task_id: 任務 ID

        Returns:
            (是否有效, 錯誤訊息)
        """
        if not isinstance(task_id, str):
            return False, "任務 ID 必須是字符串"

        # UUID 格式驗證（簡化版）
        uuid_pattern = r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"
        if not re.match(uuid_pattern, task_id.lower()):
            return False, "任務 ID 格式無效"

        return True, None

    @staticmethod
    def validate_file_size(file_size: int) -> Tuple[bool, Optional[str]]:
        """
        驗證文件大小

        Args:
            file_size: 文件大小（字節）

        Returns:
            (是否有效, 錯誤訊息)
        """
        if file_size <= 0:
            return False, "文件大小無效"

        if file_size > InputValidator.MAX_FILE_SIZE:
            max_mb = InputValidator.MAX_FILE_SIZE / (1024 * 1024)
            return False, f"文件大小超過限制（最大 {max_mb:.0f}MB）"

        return True, None


def validate_request_data(data: dict, required_fields: List[str]) -> Tuple[bool, Optional[str]]:
    """
    驗證請求數據包含必需字段

    Args:
        data: 請求數據
        required_fields: 必需字段列表

    Returns:
        (是否有效, 錯誤訊息)
    """
    if not isinstance(data, dict):
        return False, "請求數據格式無效"

    for field in required_fields:
        if field not in data:
            return False, f"缺少必需字段: {field}"

    return True, None
