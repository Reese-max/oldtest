#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
調試選項D提取問題
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.core.pdf_processor import PDFProcessor
from src.core.question_parser import QuestionParser
from src.utils.logger import logger

def debug_option_d():
    """調試選項D提取問題"""
    
    pdf_path = "/workspace/考選部考古題完整庫/民國114年/民國114年_警察特考/行政警察/警察法規(包括警察法、行政執行法、社會秩序維護法、警械使用條例、集會遊行法、警察職權行使法、公務人員行政中立法)/試題.pdf"
    
    processor = PDFProcessor()
    parser = QuestionParser()
    
    try:
        # 提取文字
        text = processor.extract_text(pdf_path)
        
        # 找到測驗題部分
        start_marker = "乙、測驗題部分"
        start_pos = text.find(start_marker)
        
        if start_pos != -1:
            test_section = text[start_pos:start_pos + 2000]  # 取前2000字元
            
            # 分析第一題的選項
            first_question = """1 下列何者非屬準用公務人員行政中立法之人員？
經公務人員考試錄取，接受訓練之人員 各級學校之軍訓教官
行政法人有給專任之理事 私立學校校長及其兼任行政職務之教師"""
            
            logger.info("第一題分析:")
            logger.info(f"原始內容: {repr(first_question)}")
            
            # 測試選項提取
            options = parser._extract_options(first_question)
            logger.info(f"提取到的選項: {options}")
            
            # 分析選項提取過程
            lines = first_question.split('\n')
            logger.info(f"按行分割: {lines}")
            
            for i, line in enumerate(lines):
                line = line.strip()
                if not line:
                    continue
                    
                # 跳過題目行
                if '？' in line or '?' in line:
                    logger.info(f"跳過題目行: {line}")
                    continue
                    
                # 按空格分割這一行
                words = line.split()
                logger.info(f"第{i+1}行單詞: {words}")
                
                current_option = ""
                for word in words:
                    option_starters = ['經', '各', '行', '私', '於', '依', '關', '當', '偶', '下', '應', '若', '原', '該', '法', '警', '義', '偶', '褫', '受', '無', '須', '向', '得', '限']
                    
                    if word in option_starters and current_option:
                        logger.info(f"找到選項開始詞 '{word}', 保存當前選項: '{current_option}'")
                        current_option = word
                    else:
                        if current_option:
                            current_option += " " + word
                        else:
                            current_option = word
                
                logger.info(f"最終選項: '{current_option}'")
                
    except Exception as e:
        logger.failure(f"調試失敗: {e}")

if __name__ == '__main__':
    debug_option_d()