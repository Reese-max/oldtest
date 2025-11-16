#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
sys.path.append('src')

from src.processors.archaeology_processor import ArchaeologyProcessor

def debug_questions_format():
    """調試題目數據格式"""
    print("=== 調試題目數據格式 ===")
    
    # 初始化處理器
    processor = ArchaeologyProcessor(use_enhanced=True)
    
    # 測試PDF路徑
    pdf_path = "114年考古題/民國114年/民國114年_警察特考/資訊管理/中華民國憲法與警察專業英文/試題.pdf"
    
    try:
        result = processor.process_pdf(pdf_path)
        print(f"✅ 成功提取")
        print(f"數據類型: {type(result)}")
        print(f"結果鍵: {list(result.keys()) if isinstance(result, dict) else 'N/A'}")
        
        if isinstance(result, dict):
            questions_count = result.get('questions_count', 0)
            print(f"題目數量: {questions_count}")
            print(f"成功狀態: {result.get('success', False)}")
            print(f"統計信息: {result.get('statistics', {})}")
        else:
            print(f"結果內容: {result}")
        
        return True
        
    except Exception as e:
        print(f"❌ 提取失敗: {str(e)}")
        return False

if __name__ == "__main__":
    debug_questions_format()
