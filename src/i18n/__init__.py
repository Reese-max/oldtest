#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
國際化支持模塊
提供多語言支持功能
"""

from .i18n_manager import I18nManager, get_text, set_language, get_current_language

__all__ = [
    'I18nManager',
    'get_text',
    'set_language',
    'get_current_language',
]
