#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試答案提取功能
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.core.pdf_processor import PDFProcessor
from src.core.answer_processor import AnswerProcessor
from src.utils.logger import logger

def test_answer_extraction():
    """測試答案提取功能"""
    
    # 測試答案檔案
    answer_files = [
        "/workspace/考選部考古題完整庫/民國114年/民國114年_警察特考/行政警察/國文(作文與測驗)/答案.pdf",
        "/workspace/考選部考古題完整庫/民國114年/民國114年_警察特考/行政警察/警察法規(包括警察法、行政執行法、社會秩序維護法、警械使用條例、集會遊行法、警察職權行使法、公務人員行政中立法)/答案.pdf"
    ]
    
    processor = PDFProcessor()
    answer_processor = AnswerProcessor()
    
    for answer_path in answer_files:
        logger.info(f"\n{'='*80}")
        logger.info(f"測試答案檔案: {os.path.basename(answer_path)}")
        logger.info(f"{'='*80}")
        
        try:
            # 提取文字
            text = processor.extract_text(answer_path)
            logger.info(f"文字長度: {len(text)} 字元")
            
            # 提取答案
            answers = answer_processor.extract_answers(text)
            logger.info(f"提取到 {len(answers)} 個答案")
            
            # 顯示前10個答案
            for i, (q_num, answer) in enumerate(list(answers.items())[:10]):
                logger.info(f"第{q_num}題: {answer}")
                
        except Exception as e:
            logger.failure(f"測試失敗: {e}")

if __name__ == '__main__':
    test_answer_extraction()