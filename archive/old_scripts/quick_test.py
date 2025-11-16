#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
sys.path.append('src')

import pdfplumber

def quick_pdf_check(pdf_path):
    """快速檢查PDF是否能正常讀取"""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            # 只讀取第一頁來檢查
            first_page = pdf.pages[0]
            text = first_page.extract_text()
            return {
                'success': True,
                'page_count': len(pdf.pages),
                'first_page_chars': len(text) if text else 0,
                'text_preview': text[:200] if text else '',
                'error': None
            }
    except Exception as e:
        return {
            'success': False,
            'page_count': 0,
            'first_page_chars': 0,
            'text_preview': '',
            'error': str(e)
        }

def test_info_management():
    """快速測試資訊管理類別"""
    print("=== 快速測試：資訊管理 ===")
    
    base_dir = "114年考古題/民國114年/民國114年_警察特考/資訊管理"
    
    if not os.path.exists(base_dir):
        print(f"錯誤：找不到目錄 {base_dir}")
        return
    
    results = {}
    total_subjects = 0
    successful_subjects = 0
    
    # 遍歷資訊管理類別下的所有科目
    for subject in sorted(os.listdir(base_dir)):
        subject_path = os.path.join(base_dir, subject)
        if not os.path.isdir(subject_path):
            continue
        
        # 查找試題PDF
        question_pdf = os.path.join(subject_path, "試題.pdf")
        if not os.path.exists(question_pdf):
            print(f"  ⚠️ {subject}: 未找到試題.pdf")
            continue
        
        print(f"  📄 {subject}")
        result = quick_pdf_check(question_pdf)
        results[subject] = result
        
        total_subjects += 1
        if result['success']:
            successful_subjects += 1
            print(f"    → ✅ PDF可讀取: {result['page_count']}頁, {result['first_page_chars']}字元")
            print(f"    → 預覽: {result['text_preview'][:50]}...")
        else:
            print(f"    → ❌ PDF讀取失敗: {result['error']}")
    
    print(f"\n=== 資訊管理快速測試完成 ===")
    print(f"總科目數: {total_subjects}")
    print(f"成功科目數: {successful_subjects}")
    print(f"成功率: {successful_subjects/total_subjects*100:.1f}%")
    
    return results

if __name__ == "__main__":
    test_info_management()
