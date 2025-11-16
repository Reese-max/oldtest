#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試改進後的題目解析器
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.core.pdf_processor import PDFProcessor
from src.core.question_parser import QuestionParser
from src.utils.logger import logger

def test_improved_parser():
    """測試改進後的解析器"""
    
    # 測試檔案
    test_files = [
        "/workspace/考選部考古題完整庫/民國114年/民國114年_警察特考/行政警察/國文(作文與測驗)/試題.pdf",
        "/workspace/考選部考古題完整庫/民國114年/民國114年_警察特考/行政警察/警察法規(包括警察法、行政執行法、社會秩序維護法、警械使用條例、集會遊行法、警察職權行使法、公務人員行政中立法)/試題.pdf"
    ]
    
    processor = PDFProcessor()
    parser = QuestionParser()
    
    for pdf_path in test_files:
        logger.info(f"\n{'='*80}")
        logger.info(f"測試檔案: {os.path.basename(pdf_path)}")
        logger.info(f"{'='*80}")
        
        try:
            # 提取文字
            text = processor.extract_text(pdf_path)
            logger.info(f"文字長度: {len(text)} 字元")
            
            # 只取測驗題部分
            start_marker = "乙、測驗題部分"
            start_pos = text.find(start_marker)
            
            if start_pos != -1:
                test_section = text[start_pos:start_pos + 3000]  # 取前3000字元
                logger.info("測驗題部分內容:")
                logger.info(test_section[:500] + "...")
                
                # 解析題目
                questions = parser.parse_questions(test_section)
                logger.info(f"解析到 {len(questions)} 題")
                
                # 顯示前3題的詳細內容
                for i, question in enumerate(questions[:3]):
                    logger.info(f"\n第 {i+1} 題:")
                    logger.info(f"題號: {question.get('題號', 'N/A')}")
                    logger.info(f"題目: {question.get('題目', 'N/A')[:100]}...")
                    logger.info(f"選項A: {question.get('選項A', 'N/A')}")
                    logger.info(f"選項B: {question.get('選項B', 'N/A')}")
                    logger.info(f"選項C: {question.get('選項C', 'N/A')}")
                    logger.info(f"選項D: {question.get('選項D', 'N/A')}")
            else:
                logger.warning("未找到測驗題部分")
                
        except Exception as e:
            logger.failure(f"測試失敗: {e}")

if __name__ == '__main__':
    test_improved_parser()