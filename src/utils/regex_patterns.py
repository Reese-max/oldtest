#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
正則表達式模式常數模組
統一管理所有正則表達式模式，預編譯以提升性能
"""

import re
from typing import List, Pattern, Optional

# ==================== 題目檢測模式 ====================

# 題組檢測模式
QUESTION_GROUP_PATTERNS: List[Pattern] = [
    re.compile(r'請依下文回答第(\d+)題至第(\d+)題', re.UNICODE),
    re.compile(r'請根據下列文章回答第(\d+)題至第(\d+)題', re.UNICODE),
    re.compile(r'閱讀下文，回答第(\d+)題至第(\d+)題', re.UNICODE),
]

# 一般題目檢測模式
QUESTION_PATTERNS: List[Pattern] = [
    re.compile(r'第(\d+)題[：:]?\s*(.*?)(?=第\d+題|$)', re.DOTALL),
    re.compile(r'(\d+)\.\s*(.*?)(?=\d+\.|$)', re.DOTALL),
    re.compile(r'^(\d+)\s+(.*?)(?=^\d+\s+|$)', re.MULTILINE | re.DOTALL),
    re.compile(r'(\d+)\s+(.*?)(?=\d+\s+|$)', re.DOTALL),
]

# 題號模式
QUESTION_NUMBER_PATTERNS: List[Pattern] = [
    re.compile(r'^\s*第(\d+)題[：:]', re.MULTILINE),
    re.compile(r'^\s*第(\d+)題[：:]', re.UNICODE),
    re.compile(r'^(\d+)[：:]?\s*', re.MULTILINE),
]

# ==================== 選項提取模式 ====================

# 標準選項格式：(A) 選項內容
STANDARD_OPTION_PATTERNS: List[Pattern] = [
    re.compile(r'[（(]A[）)]\s*(.*?)(?=[（(]B[）)]|$)', re.DOTALL),
    re.compile(r'[（(]B[）)]\s*(.*?)(?=[（(]C[）)]|$)', re.DOTALL),
    re.compile(r'[（(]C[）)]\s*(.*?)(?=[（(]D[）)]|$)', re.DOTALL),
    re.compile(r'[（(]D[）)]\s*(.*?)(?=[（(]E[）)]|$)', re.DOTALL),
]

# ==================== 答案提取模式 ====================

# 標準答案格式
ANSWER_PATTERNS: List[Pattern] = [
    re.compile(r'第(\d+)題[：:]?\s*([ABCD])', re.UNICODE),
    re.compile(r'(\d+)[：:]?\s*([ABCD])', re.UNICODE),
    re.compile(r'題號\s*(\d+)[：:]?\s*答案\s*([ABCD])', re.UNICODE),
    re.compile(r'(\d+)\.\s*([ABCD])', re.UNICODE),
]

# 更正答案格式
CORRECTED_ANSWER_PATTERNS: List[Pattern] = [
    re.compile(r'更正\s*(\d+)\.\s*([ABCD])', re.UNICODE),
    re.compile(r'更正答案\s*(\d+)\.\s*([ABCD])', re.UNICODE),
    re.compile(r'更正\s*第(\d+)題\s*([ABCD])', re.UNICODE),
    re.compile(r'更正\s*(\d+)\s*[：:]\s*([ABCD])', re.UNICODE),
]

# 表格答案格式
TABLE_ANSWER_PATTERNS: List[Pattern] = [
    re.compile(r'第(\d+)題', re.UNICODE),
]

# ==================== 申論題模式 ====================

# 申論題檢測模式
ESSAY_PATTERNS: List[Pattern] = [
    re.compile(r'申論題|問答題|簡答題|論述題', re.UNICODE),
    re.compile(r'甲、申論題|一、申論題', re.UNICODE),
]

# 申論題分數提取
ESSAY_SCORE_PATTERNS: List[Pattern] = [
    re.compile(r'[（(](\d+)\s*分[）)]', re.UNICODE),
    re.compile(r'（(\d+)\s*分）', re.UNICODE),
]

# ==================== 混合格式模式 ====================

# 混合格式檢測
MIXED_FORMAT_PATTERNS: List[Pattern] = [
    re.compile(r'甲、申論題部分.*?乙、測驗題部分', re.DOTALL),
    re.compile(r'作文部分.*?測驗部分', re.DOTALL),
]

# ==================== 嵌入式填空題模式 ====================

# Unicode符號選項（修正為正確的碼點 U+E18C-U+E18F）
EMBEDDED_SYMBOLS = ['\ue18c', '\ue18d', '\ue18e', '\ue18f']

# 嵌入式填空題檢測（修正為正確的碼點）
EMBEDDED_PATTERNS: List[Pattern] = [
    re.compile(r'[\ue18c\ue18d\ue18e\ue18f]', re.UNICODE),
]

# ==================== 題組相關模式 ====================

# 題組標記位置查找
NEXT_GROUP_PATTERN: Pattern = re.compile(
    r'請依下文回答第\d+題至第\d+題|請根據下列文章回答第\d+題至第\d+題|閱讀下文，回答第\d+題至第\d+題',
    re.UNICODE
)

# ==================== 過濾模式 ====================

# 非題目內容過濾關鍵詞
NON_QUESTION_KEYWORDS = [
    '代號', '頁次', '考試', '科目', '時間', '座號', '注意', '禁止', '使用',
    '本試題', '單一選擇題', '選出', '正確', '適當', '答案', '共', '每題',
    '須用', '鉛筆', '試卡', '依題號', '清楚', '劃記', '作答者', '不予', '計分'
]

# ==================== 輔助函數 ====================

def match_patterns(text: str, patterns: List[Pattern]) -> List[re.Match]:
    """
    使用多個模式匹配文字
    
    Args:
        text: 要匹配的文字
        patterns: 正則表達式模式列表
        
    Returns:
        所有匹配結果列表
    """
    matches = []
    for pattern in patterns:
        matches.extend(pattern.finditer(text))
    return matches


def find_first_match(text: str, patterns: List[Pattern]) -> Optional[re.Match]:
    """
    使用多個模式查找第一個匹配
    
    Args:
        text: 要匹配的文字
        patterns: 正則表達式模式列表
        
    Returns:
        第一個匹配結果，如果沒有則返回None
    """
    for pattern in patterns:
        match = pattern.search(text)
        if match:
            return match
    return None

