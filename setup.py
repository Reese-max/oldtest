#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
考古題處理系統 - 安裝配置
"""

from setuptools import setup, find_packages
import os

# 讀取 README
def read_file(filename):
    """讀取文件內容"""
    filepath = os.path.join(os.path.dirname(__file__), filename)
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    return ""

# 版本信息
VERSION = "1.7.0"
DESCRIPTION = "考古題處理系統 - 自動化解析考試題目並生成Google表單"
LONG_DESCRIPTION = read_file("README.md")

# 核心依賴 - 基本功能必需
CORE_REQUIREMENTS = [
    "pdfplumber>=0.9.0",        # PDF文字提取（主要工具）
    "pandas>=1.5.0",             # 資料處理
    "numpy>=1.24.0",             # 數值計算
    "regex>=2023.10.0",          # 增強正則表達式
    "python-Levenshtein>=0.21.0",  # 字串相似度
    "PyYAML>=6.0",               # YAML配置
    "psutil>=5.9.0",             # 系統監控
]

# OCR 功能依賴（可選）
OCR_REQUIREMENTS = [
    "paddlepaddle>=2.5.0",       # PaddlePaddle 框架
    "paddleocr>=2.7.0",          # PaddleOCR 引擎
    "pdf2image>=1.16.3",         # PDF轉圖片
    "Pillow>=10.0.0",            # 圖像處理
]

# OCR Tesseract 替代方案（可選）
OCR_TESSERACT_REQUIREMENTS = [
    "pytesseract>=0.3.10",       # Tesseract OCR
    "Pillow>=10.0.0",            # 圖像處理
    "pdf2image>=1.16.3",         # PDF轉圖片
]

# 備用 PDF 處理工具（可選）
PDF_EXTRA_REQUIREMENTS = [
    "PyMuPDF>=1.23.0",           # fitz - 高性能PDF處理
    "pdfminer.six>=20221105",    # 詳細PDF分析
    "pypdf>=3.0.0",              # 輕量級PDF處理
]

# AI 輔助功能（可選 - 目前未使用）
AI_REQUIREMENTS = [
    "google-generativeai>=0.3.0",  # Google Gemini API
    "openai>=1.0.0",                # OpenAI API
]

# Web 管理界面（可選）
WEB_REQUIREMENTS = [
    "Flask>=2.3.0",              # 輕量級Web框架
    "Werkzeug>=2.3.0",           # WSGI工具集
]

# 開發工具依賴
DEV_REQUIREMENTS = [
    "pytest>=7.0.0",             # 測試框架
    "pytest-cov>=4.0.0",         # 測試覆蓋率
    "black>=22.0.0",             # 代碼格式化
    "flake8>=5.0.0",             # 代碼檢查
    "mypy>=1.0.0",               # 類型檢查
    "sphinx>=5.0.0",             # 文檔生成
]

# 完整安裝（所有功能）
FULL_REQUIREMENTS = (
    CORE_REQUIREMENTS +
    OCR_REQUIREMENTS +
    PDF_EXTRA_REQUIREMENTS
)

setup(
    name="exam-question-processor",
    version=VERSION,
    author="Your Name",
    author_email="your.email@example.com",
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/exam-question-processor",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Education",
        "Topic :: Education :: Testing",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",

    # 核心依賴
    install_requires=CORE_REQUIREMENTS,

    # 可選功能依賴
    extras_require={
        # OCR 功能（使用 PaddleOCR）
        "ocr": OCR_REQUIREMENTS,

        # OCR 功能（使用 Tesseract）
        "ocr-tesseract": OCR_TESSERACT_REQUIREMENTS,

        # 備用 PDF 處理工具
        "pdf-extra": PDF_EXTRA_REQUIREMENTS,

        # Web 管理界面
        "web": WEB_REQUIREMENTS,

        # AI 功能（預留，目前未使用）
        "ai": AI_REQUIREMENTS,

        # 開發工具
        "dev": DEV_REQUIREMENTS,

        # 完整安裝（除AI外的所有功能）
        "full": FULL_REQUIREMENTS,

        # 完整安裝（包含所有功能）
        "all": FULL_REQUIREMENTS + WEB_REQUIREMENTS + AI_REQUIREMENTS + DEV_REQUIREMENTS,
    },

    # 入口點
    entry_points={
        "console_scripts": [
            "exam-processor=src.cli:main",
        ],
    },

    # 包含的數據文件
    include_package_data=True,
    package_data={
        "": ["*.yaml", "*.json", "*.md"],
    },

    # 項目URLs
    project_urls={
        "Bug Reports": "https://github.com/yourusername/exam-question-processor/issues",
        "Source": "https://github.com/yourusername/exam-question-processor",
        "Documentation": "https://github.com/yourusername/exam-question-processor/blob/main/docs/API_DOCUMENTATION.md",
    },
)
