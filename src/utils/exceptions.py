#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自定義異常類別
提供結構化的錯誤處理
"""


class ArchaeologyQuestionsError(Exception):
    """考古題處理系統基礎異常"""
    pass


class PDFProcessingError(ArchaeologyQuestionsError):
    """PDF處理異常"""
    pass


class QuestionParsingError(ArchaeologyQuestionsError):
    """題目解析異常"""
    pass


class AnswerProcessingError(ArchaeologyQuestionsError):
    """答案處理異常"""
    pass


class CSVGenerationError(ArchaeologyQuestionsError):
    """CSV生成異常"""
    pass


class GoogleFormError(ArchaeologyQuestionsError):
    """Google表單處理異常"""
    pass


class ConfigurationError(ArchaeologyQuestionsError):
    """配置異常"""
    pass


class ValidationError(ArchaeologyQuestionsError):
    """驗證異常"""
    pass