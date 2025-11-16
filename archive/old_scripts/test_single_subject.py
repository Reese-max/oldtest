#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
sys.path.append('src')

from src.processors.archaeology_processor import ArchaeologyProcessor

def test_single_subject(pdf_path, subject_name):
    """測試單個科目的題目提取"""
    print(f"=== 測試科目: {subject_name} ===")
    
    # 初始化處理器
    processor = ArchaeologyProcessor(use_enhanced=True)
    
    try:
        questions = processor.process_pdf(pdf_path)
        print(f"✅ 成功提取: {len(questions)} 題")
        
        # 顯示前3題的詳細信息
        for i, q in enumerate(questions[:3]):
            question_text = q.get('question_text', '')
            if question_text:
                print(f"  第{i+1}題: {question_text[:50]}...")
            if q.get('options'):
                print(f"    選項: {q['options']}")
        
        return {
            'success': True,
            'question_count': len(questions),
            'questions': questions
        }
    except Exception as e:
        print(f"❌ 提取失敗: {str(e)}")
        return {
            'success': False,
            'question_count': 0,
            'error': str(e)
        }

if __name__ == "__main__":
    # 測試資訊管理類別中的一個科目
    pdf_path = "114年考古題/民國114年/民國114年_警察特考/資訊管理/中華民國憲法與警察專業英文/試題.pdf"
    test_single_subject(pdf_path, "中華民國憲法與警察專業英文")
