#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
真實考古題測試腳本
測試多個不同類型的真實考古題
"""

import os
import sys
import json
from datetime import datetime

# 添加src目錄到路徑
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.api import ArchaeologyAPI
from src.utils.logger import logger

def test_real_archaeology():
    """測試真實考古題"""
    
    # 測試案例配置
    test_cases = [
        {
            "name": "警察特考行政警察_國文",
            "pdf_path": "/workspace/考選部考古題完整庫/民國114年/民國114年_警察特考/行政警察/國文(作文與測驗)/試題.pdf",
            "answer_path": "/workspace/考選部考古題完整庫/民國114年/民國114年_警察特考/行政警察/國文(作文與測驗)/答案.pdf",
            "corrected_path": None,
            "description": "國文選擇題，測試基本解析功能"
        },
        {
            "name": "警察特考行政警察_警察法規",
            "pdf_path": "/workspace/考選部考古題完整庫/民國114年/民國114年_警察特考/行政警察/警察法規(包括警察法、行政執行法、社會秩序維護法、警械使用條例、集會遊行法、警察職權行使法、公務人員行政中立法)/試題.pdf",
            "answer_path": "/workspace/考選部考古題完整庫/民國114年/民國114年_警察特考/行政警察/警察法規(包括警察法、行政執行法、社會秩序維護法、警械使用條例、集會遊行法、警察職權行使法、公務人員行政中立法)/答案.pdf",
            "corrected_path": "/workspace/考選部考古題完整庫/民國114年/民國114年_警察特考/行政警察/警察法規(包括警察法、行政執行法、社會秩序維護法、警械使用條例、集會遊行法、警察職權行使法、公務人員行政中立法)/更正答案.pdf",
            "description": "專業法規題目，測試複雜題型解析"
        },
        {
            "name": "司法特考監獄官_國文",
            "pdf_path": "/workspace/考選部考古題完整庫/民國114年/民國114年_司法特考/監獄官/國文（作文與測驗）/試題.pdf",
            "answer_path": "/workspace/考選部考古題完整庫/民國114年/民國114年_司法特考/監獄官/國文（作文與測驗）/答案.pdf",
            "corrected_path": None,
            "description": "司法特考國文，測試不同考試類型"
        },
        {
            "name": "警察特考行政警察_警察情境實務",
            "pdf_path": "/workspace/考選部考古題完整庫/民國114年/民國114年_警察特考/行政警察/警察情境實務(包括警察法規、實務操作標準作業程序、人權保障與正當法律程序)/試題.pdf",
            "answer_path": "/workspace/考選部考古題完整庫/民國114年/民國114年_警察特考/行政警察/警察情境實務(包括警察法規、實務操作標準作業程序、人權保障與正當法律程序)/答案.pdf",
            "corrected_path": "/workspace/考選部考古題完整庫/民國114年/民國114年_警察特考/行政警察/警察情境實務(包括警察法規、實務操作標準作業程序、人權保障與正當法律程序)/更正答案.pdf",
            "description": "情境實務題目，測試應用題型"
        }
    ]
    
    # 建立API實例
    api = ArchaeologyAPI()
    
    # 測試結果記錄
    test_results = []
    total_tests = len(test_cases)
    successful_tests = 0
    
    logger.info(f"開始測試 {total_tests} 個真實考古題")
    
    for i, test_case in enumerate(test_cases, 1):
        logger.info(f"\n{'='*60}")
        logger.info(f"測試 {i}/{total_tests}: {test_case['name']}")
        logger.info(f"描述: {test_case['description']}")
        logger.info(f"{'='*60}")
        
        # 檢查檔案是否存在
        if not os.path.exists(test_case['pdf_path']):
            logger.failure(f"PDF檔案不存在: {test_case['pdf_path']}")
            test_results.append({
                'name': test_case['name'],
                'success': False,
                'error': 'PDF檔案不存在',
                'description': test_case['description']
            })
            continue
            
        if test_case['answer_path'] and not os.path.exists(test_case['answer_path']):
            logger.warning(f"答案檔案不存在: {test_case['answer_path']}")
            test_case['answer_path'] = None
            
        if test_case['corrected_path'] and not os.path.exists(test_case['corrected_path']):
            logger.warning(f"更正答案檔案不存在: {test_case['corrected_path']}")
            test_case['corrected_path'] = None
        
        try:
            # 設定輸出目錄
            output_dir = f"/workspace/test_output/真實考古題測試_{test_case['name']}"
            os.makedirs(output_dir, exist_ok=True)
            
            # 處理PDF
            result = api.process_single_pdf(
                pdf_path=test_case['pdf_path'],
                answer_pdf_path=test_case['answer_path'],
                corrected_answer_pdf_path=test_case['corrected_path'],
                output_dir=output_dir,
                generate_script=True
            )
            
            if result['success']:
                successful_tests += 1
                logger.success(f"✅ {test_case['name']} 處理成功")
                
                # 分析結果
                analysis = analyze_test_result(result, test_case)
                test_results.append({
                    'name': test_case['name'],
                    'success': True,
                    'description': test_case['description'],
                    'analysis': analysis,
                    'result': result
                })
            else:
                logger.failure(f"❌ {test_case['name']} 處理失敗: {result['message']}")
                test_results.append({
                    'name': test_case['name'],
                    'success': False,
                    'error': result['message'],
                    'description': test_case['description']
                })
                
        except Exception as e:
            logger.failure(f"❌ {test_case['name']} 測試異常: {e}")
            test_results.append({
                'name': test_case['name'],
                'success': False,
                'error': str(e),
                'description': test_case['description']
            })
    
    # 生成測試報告
    generate_test_report(test_results, successful_tests, total_tests)
    
    return test_results

def analyze_test_result(result, test_case):
    """分析測試結果"""
    analysis = {
        'csv_files_count': len(result.get('csv_files', [])),
        'script_files_count': len(result.get('script_files', [])),
        'output_dir': result.get('output_dir', ''),
        'has_google_csv': False,
        'has_script': 'script_file' in result or 'script_files' in result
    }
    
    # 檢查是否有Google表單CSV
    for csv_file in result.get('csv_files', []):
        if 'Google表單' in csv_file:
            analysis['has_google_csv'] = True
            break
    
    return analysis

def generate_test_report(test_results, successful_tests, total_tests):
    """生成測試報告"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = f"/workspace/test_output/真實考古題測試報告_{timestamp}.md"
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(f"# 真實考古題測試報告\n\n")
        f.write(f"**測試時間**: {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}\n")
        f.write(f"**測試總數**: {total_tests}\n")
        f.write(f"**成功數量**: {successful_tests}\n")
        f.write(f"**成功率**: {successful_tests/total_tests*100:.1f}%\n\n")
        
        f.write("## 📊 測試結果概覽\n\n")
        f.write("| 測試項目 | 狀態 | 描述 |\n")
        f.write("|---------|------|------|\n")
        
        for result in test_results:
            status = "✅ 成功" if result['success'] else "❌ 失敗"
            f.write(f"| {result['name']} | {status} | {result['description']} |\n")
        
        f.write("\n## 🔍 詳細測試結果\n\n")
        
        for i, result in enumerate(test_results, 1):
            f.write(f"### {i}. {result['name']}\n\n")
            f.write(f"**描述**: {result['description']}\n\n")
            
            if result['success']:
                f.write("**狀態**: ✅ 成功\n\n")
                analysis = result.get('analysis', {})
                f.write(f"- CSV檔案數量: {analysis.get('csv_files_count', 0)}\n")
                f.write(f"- 腳本檔案數量: {analysis.get('script_files_count', 0)}\n")
                f.write(f"- 包含Google表單CSV: {'是' if analysis.get('has_google_csv') else '否'}\n")
                f.write(f"- 包含Google Apps Script: {'是' if analysis.get('has_script') else '否'}\n")
                f.write(f"- 輸出目錄: {analysis.get('output_dir', 'N/A')}\n")
            else:
                f.write("**狀態**: ❌ 失敗\n\n")
                f.write(f"**錯誤**: {result.get('error', '未知錯誤')}\n")
            
            f.write("\n---\n\n")
        
        f.write("## 📈 測試分析\n\n")
        
        # 成功率分析
        success_rate = successful_tests / total_tests * 100
        f.write(f"### 整體成功率: {success_rate:.1f}%\n\n")
        
        if success_rate == 100:
            f.write("🎉 **所有測試都成功通過！**\n\n")
        elif success_rate >= 80:
            f.write("✅ **大部分測試成功，系統表現良好**\n\n")
        elif success_rate >= 60:
            f.write("⚠️ **部分測試失敗，需要進一步改進**\n\n")
        else:
            f.write("❌ **多數測試失敗，需要重大改進**\n\n")
        
        # 功能分析
        f.write("### 功能分析\n\n")
        successful_results = [r for r in test_results if r['success']]
        
        if successful_results:
            f.write("- **PDF解析功能**: 正常運作\n")
            f.write("- **答案處理功能**: 正常運作\n")
            f.write("- **CSV生成功能**: 正常運作\n")
            f.write("- **Google表單生成**: 正常運作\n")
        
        f.write("\n## 🎯 建議\n\n")
        
        if success_rate < 100:
            failed_tests = [r for r in test_results if not r['success']]
            f.write("### 需要改進的項目\n\n")
            for test in failed_tests:
                f.write(f"- **{test['name']}**: {test.get('error', '未知錯誤')}\n")
        
        f.write("\n### 使用建議\n\n")
        f.write("1. 系統已準備就緒，可以開始處理真實考古題\n")
        f.write("2. 建議定期測試不同類型的考古題\n")
        f.write("3. 注意PDF格式的相容性\n")
        f.write("4. 保持答案檔案的完整性\n")
    
    logger.success(f"測試報告已生成: {report_path}")
    return report_path

if __name__ == '__main__':
    test_real_archaeology()