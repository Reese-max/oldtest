#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分析真實考古題格式
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.core.pdf_processor import PDFProcessor
from src.utils.logger import logger

def analyze_real_format():
    """分析真實考古題格式"""
    
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
            
            # 分析第一題的詳細格式
            first_question = """1 下列何者非屬準用公務人員行政中立法之人員？
經公務人員考試錄取，接受訓練之人員 各級學校之軍訓教官
行政法人有給專任之理事 私立學校校長及其兼任行政職務之教師"""
            
            logger.info("\n第一題分析:")
            logger.info(f"原始內容: {repr(first_question)}")
            
            # 按行分割
            lines = first_question.split('\n')
            logger.info(f"按行分割: {lines}")
            
            # 按空格分割
            words = first_question.split()
            logger.info(f"按空格分割: {words}")
            
            # 尋找特殊符號
            import re
            special_chars = re.findall(r'[^\w\s\u4e00-\u9fff]', first_question)
            logger.info(f"特殊符號: {special_chars}")
            
            # 分析選項的開始位置
            option_starts = []
            for i, char in enumerate(first_question):
                if char in ['經', '各', '行', '私']:
                    option_starts.append((i, char, first_question[i:i+50]))
            
            logger.info(f"選項開始位置: {option_starts}")
                    
    except Exception as e:
        logger.failure(f"分析失敗: {e}")

if __name__ == '__main__':
    analyze_real_format()