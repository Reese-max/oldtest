#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
sys.path.append('src')

from src.processors.archaeology_processor import ArchaeologyProcessor

def simple_test():
    """簡單測試題目提取"""
    print("=== 簡單測試 ===")
    
    # 初始化處理器
    processor = ArchaeologyProcessor(use_enhanced=True)
    
    # 測試PDF路徑
    pdf_path = "114年考古題/民國114年/民國114年_警察特考/資訊管理/中華民國憲法與警察專業英文/試題.pdf"
    
    try:
        questions = processor.process_pdf(pdf_path)
        print(f"✅ 成功提取: {len(questions)} 題")
        
        # 簡單顯示題目類型統計
        essay_count = sum(1 for q in questions if q.get('question_type') == 'essay')
        choice_count = sum(1 for q in questions if q.get('question_type') == 'choice')
        fill_count = sum(1 for q in questions if q.get('question_type') == 'fill_blank')
        
        print(f"  申論題: {essay_count} 題")
        print(f"  選擇題: {choice_count} 題")
        print(f"  填空題: {fill_count} 題")
        
        return True
        
    except Exception as e:
        print(f"❌ 提取失敗: {str(e)}")
        return False

if __name__ == "__main__":
    simple_test()
