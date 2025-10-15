#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
調試選項格式腳本
檢查真實考古題的選項格式
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.core.pdf_processor import PDFProcessor
from src.utils.logger import logger

def debug_options():
    """調試選項格式"""
    
    pdf_path = "/workspace/考選部考古題完整庫/民國114年/民國114年_警察特考/行政警察/警察法規(包括警察法、行政執行法、社會秩序維護法、警械使用條例、集會遊行法、警察職權行使法、公務人員行政中立法)/試題.pdf"
    
    processor = PDFProcessor()
    
    try:
        # 提取文字
        text = processor.extract_text(pdf_path)
        
        # 找到測驗題部分
        start_marker = "乙、測驗題部分"
        start_pos = text.find(start_marker)
        
        if start_pos != -1:
            test_section = text[start_pos:start_pos + 2000]  # 取前2000字元
            logger.info("測驗題部分內容:")
            logger.info(test_section)
            
            # 分析選項格式
            lines = test_section.split('\n')
            for i, line in enumerate(lines):
                line = line.strip()
                if line and (line.startswith('經') or line.startswith('各') or line.startswith('行') or line.startswith('依')):
                    logger.info(f"可能的選項行 {i}: {line}")
                    
    except Exception as e:
        logger.failure(f"調試失敗: {e}")

if __name__ == '__main__':
    debug_options()