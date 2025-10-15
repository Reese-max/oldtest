#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
調試PDF內容腳本
檢查真實考古題PDF的內容格式
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.core.pdf_processor import PDFProcessor
from src.utils.logger import logger

def debug_pdf_content():
    """調試PDF內容"""
    
    # 測試檔案
    test_files = [
        "/workspace/考選部考古題完整庫/民國114年/民國114年_警察特考/行政警察/國文(作文與測驗)/試題.pdf",
        "/workspace/考選部考古題完整庫/民國114年/民國114年_警察特考/行政警察/警察法規(包括警察法、行政執行法、社會秩序維護法、警械使用條例、集會遊行法、警察職權行使法、公務人員行政中立法)/試題.pdf"
    ]
    
    processor = PDFProcessor()
    
    for pdf_path in test_files:
        logger.info(f"\n{'='*80}")
        logger.info(f"調試PDF: {os.path.basename(pdf_path)}")
        logger.info(f"{'='*80}")
        
        try:
            # 提取文字
            text = processor.extract_text(pdf_path)
            logger.info(f"文字長度: {len(text)} 字元")
            
            # 顯示前1000字元
            logger.info(f"前1000字元內容:")
            logger.info(f"{text[:1000]}")
            
            # 檢查是否包含題目相關關鍵字
            keywords = ['題', '選擇題', '單選題', '多選題', '1.', '2.', '3.', '4.', '5.']
            found_keywords = []
            for keyword in keywords:
                if keyword in text:
                    found_keywords.append(keyword)
            
            logger.info(f"找到的關鍵字: {found_keywords}")
            
            # 檢查是否有數字開頭的行
            lines = text.split('\n')
            numbered_lines = []
            for i, line in enumerate(lines[:50]):  # 只檢查前50行
                line = line.strip()
                if line and (line[0].isdigit() or line.startswith('(') or line.startswith('（')):
                    numbered_lines.append(f"第{i+1}行: {line}")
            
            logger.info(f"數字開頭的行 (前10行):")
            for line in numbered_lines[:10]:
                logger.info(f"  {line}")
                
        except Exception as e:
            logger.failure(f"調試失敗: {e}")

if __name__ == '__main__':
    debug_pdf_content()