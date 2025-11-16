#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
調試答案格式腳本
分析真實考古題答案的格式
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.core.pdf_processor import PDFProcessor
from src.utils.logger import logger

def debug_answer_format():
    """調試答案格式"""
    
    # 測試答案檔案
    answer_files = [
        "/workspace/考選部考古題完整庫/民國114年/民國114年_警察特考/行政警察/國文(作文與測驗)/答案.pdf",
        "/workspace/考選部考古題完整庫/民國114年/民國114年_警察特考/行政警察/警察法規(包括警察法、行政執行法、社會秩序維護法、警械使用條例、集會遊行法、警察職權行使法、公務人員行政中立法)/答案.pdf"
    ]
    
    processor = PDFProcessor()
    
    for answer_path in answer_files:
        logger.info(f"\n{'='*80}")
        logger.info(f"調試答案檔案: {os.path.basename(answer_path)}")
        logger.info(f"{'='*80}")
        
        try:
            # 提取文字
            text = processor.extract_text(answer_path)
            logger.info(f"文字長度: {len(text)} 字元")
            
            # 顯示前500字元
            logger.info(f"前500字元內容:")
            logger.info(f"{text[:500]}")
            
            # 分析答案格式
            lines = text.split('\n')
            logger.info(f"總行數: {len(lines)}")
            
            # 尋找可能的答案模式
            answer_patterns = []
            for i, line in enumerate(lines):
                line = line.strip()
                if line and len(line) <= 10:  # 答案通常很短
                    # 檢查是否包含字母
                    if any(c in line for c in 'ABCD'):
                        answer_patterns.append(f"第{i+1}行: {line}")
            
            logger.info(f"可能的答案模式 (前10個):")
            for pattern in answer_patterns[:10]:
                logger.info(f"  {pattern}")
            
            # 檢查是否有數字開頭的行
            numbered_lines = []
            for i, line in enumerate(lines[:20]):
                line = line.strip()
                if line and line[0].isdigit():
                    numbered_lines.append(f"第{i+1}行: {line}")
            
            logger.info(f"數字開頭的行 (前10個):")
            for line in numbered_lines[:10]:
                logger.info(f"  {line}")
                
        except Exception as e:
            logger.failure(f"調試失敗: {e}")

if __name__ == '__main__':
    debug_answer_format()