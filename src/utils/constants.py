#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
系統常數定義
統一管理所有魔法字符串和數值
"""

# PDF格式類型
FORMAT_TYPE_COMPREHENSIVE = "comprehensive"
FORMAT_TYPE_MIXED = "mixed_format"
FORMAT_TYPE_EMBEDDED = "embedded_choice"
FORMAT_TYPE_ESSAY = "essay"
FORMAT_TYPE_STANDARD = "standard_choice"

# 格式檢測關鍵字
KEYWORDS_TEST_SECTION = "乙、測驗題部分"
KEYWORDS_ESSAY_SECTION = "甲、申論題部分"
KEYWORDS_ENGLISH_ESSAY = "英文作文"
KEYWORDS_QUESTION_GROUP_START = "請依下文回答第"
KEYWORDS_QUESTION_GROUP_END = "題至第"
KEYWORDS_ESSAY_PART = "作文部分"
KEYWORDS_TEST_PART = "測驗部分"

# 特殊Unicode符號（嵌入式填空題）
UNICODE_OPTION_SYMBOLS = ["\ue04c", "\ue04d", "\ue04e", "\ue04f"]  # 對應A、B、C、D

# 檔案命名模式
FILE_PATTERN_ANSWER = "_答案.pdf"
FILE_PATTERN_CORRECTED_ANSWER = "_更正答案.pdf"
FILE_PATTERN_GOOGLE_SCRIPT = "_GoogleAppsScript.js"
FILE_PATTERN_GOOGLE_CSV = "_Google表單.csv"

# CSV欄位名稱
CSV_COLUMN_QUESTION_NUM = "題號"
CSV_COLUMN_QUESTION_TEXT = "題目"
CSV_COLUMN_QUESTION_TYPE = "題型"
CSV_COLUMN_OPTION_A = "選項A"
CSV_COLUMN_OPTION_B = "選項B"
CSV_COLUMN_OPTION_C = "選項C"
CSV_COLUMN_OPTION_D = "選項D"
CSV_COLUMN_CORRECT_ANSWER = "正確答案"
CSV_COLUMN_CORRECTED_ANSWER = "更正答案"
CSV_COLUMN_FINAL_ANSWER = "最終答案"
CSV_COLUMN_DIFFICULTY = "難度"
CSV_COLUMN_CATEGORY = "分類"
CSV_COLUMN_QUESTION_GROUP = "題組"
CSV_COLUMN_GROUP_ID = "題組編號"
CSV_COLUMN_NOTES = "備註"

# PDF提取常數
MIN_TEXT_LENGTH = 50  # 最小有效文字長度
QUALITY_SCORE_MIN_LENGTH_THRESHOLD = 500
QUALITY_SCORE_MID_LENGTH_THRESHOLD = 200
QUALITY_SCORE_LOW_LENGTH_THRESHOLD = 50

# 預設值
DEFAULT_OUTPUT_DIR = "output"
DEFAULT_QUESTION_TYPE = "選擇題"
DEFAULT_QUESTION_DIFFICULTY = "簡單"
DEFAULT_QUESTION_CATEGORY = "其他"

# 難度等級
DIFFICULTY_HARD_LENGTH = 100
DIFFICULTY_MEDIUM_LENGTH = 50

# 分類關鍵字
CATEGORY_KEYWORDS = {
    '語音': ['讀音', '發音'],
    '字形': ['錯別字', '字形'],
    '成語': ['成語', '慣用語'],
    '文法': ['文法', '語法'],
    '閱讀理解': ['閱讀', '理解'],
    '英文': ['英文', 'English'],
    '法律': ['憲法', '法律']
}
