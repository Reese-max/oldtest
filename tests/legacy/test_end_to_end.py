#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
端到端測試
測試完整的處理流程從PDF到Google表單
"""

import os
import sys
import tempfile
import time
from unittest.mock import patch, MagicMock

# 添加src目錄到路徑
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.api import ArchaeologyAPI


def test_complete_workflow():
    """測試完整工作流程"""
    print("🧪 測試完整工作流程")
    print("=" * 50)
    
    api = ArchaeologyAPI()
    
    # 創建真實的測試內容
    test_pdf_content = """1 經公務人員考試錄取，接受訓練之人員 各級學校之軍訓教官
(A) 經公務人員考試錄取，接受訓練之人員
(B) 各級學校之軍訓教官
(C) 以上皆是
(D) 以上皆非

2 依公務人員任用法規定，下列何者正確？
(A) 選項A內容
(B) 選項B內容
(C) 選項C內容
(D) 選項D內容

3 公務人員之任用，應本何種原則？
(A) 功績制原則
(B) 年資制原則
(C) 關係制原則
(D) 隨機制原則
"""
    
    test_answer_content = """答案：
第1題 C
第2題 A
第3題 A
"""
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # 創建測試檔案
        pdf_path = os.path.join(temp_dir, 'test_workflow.pdf')
        answer_path = os.path.join(temp_dir, 'test_workflow_答案.pdf')
        
        with open(pdf_path, 'w', encoding='utf-8') as f:
            f.write(test_pdf_content)
        
        with open(answer_path, 'w', encoding='utf-8') as f:
            f.write(test_answer_content)
        
        # 模擬PDF處理
        with patch('src.core.pdf_processor.pdfplumber.open') as mock_open:
            mock_pdf = MagicMock()
            mock_page = MagicMock()
            mock_page.extract_text.return_value = test_pdf_content
            mock_pdf.pages = [mock_page]
            mock_open.return_value.__enter__.return_value = mock_pdf
            
            with patch('src.core.pdf_processor.pdfplumber.open') as mock_answer_open:
                mock_answer_pdf = MagicMock()
                mock_answer_page = MagicMock()
                mock_answer_page.extract_text.return_value = test_answer_content
                mock_answer_pdf.pages = [mock_answer_page]
                mock_answer_open.return_value.__enter__.return_value = mock_answer_pdf
                
                # 執行完整處理流程
                start_time = time.time()
                result = api.process_single_pdf(
                    pdf_path, answer_path, output_dir=temp_dir, generate_script=True
                )
                end_time = time.time()
                
                processing_time = end_time - start_time
                
                # 驗證結果
                print(f"  處理成功: {'✅' if result['success'] else '❌'}")
                
                if result['success']:
                    print(f"  題目數量: {result['questions_count']}")
                    print(f"  答案數量: {result['answers_count']}")
                    print(f"  處理時間: {processing_time:.3f} 秒")
                    print(f"  CSV檔案數: {len(result['csv_files'])}")
                    
                    # 檢查生成的檔案
                    for csv_file in result['csv_files']:
                        if os.path.exists(csv_file):
                            file_size = os.path.getsize(csv_file) / 1024
                            print(f"    {os.path.basename(csv_file)}: {file_size:.1f} KB")
                        else:
                            print(f"    {os.path.basename(csv_file)}: 檔案不存在")
                    
                    # 檢查Google Apps Script
                    if 'script_files' in result:
                        print(f"  Google Apps Script檔案數: {len(result['script_files'])}")
                        for script_file in result['script_files']:
                            if os.path.exists(script_file):
                                file_size = os.path.getsize(script_file) / 1024
                                print(f"    {os.path.basename(script_file)}: {file_size:.1f} KB")
                            else:
                                print(f"    {os.path.basename(script_file)}: 檔案不存在")
                    
                    return {
                        'success': True,
                        'questions_count': result['questions_count'],
                        'answers_count': result['answers_count'],
                        'processing_time': processing_time,
                        'csv_files_count': len(result['csv_files']),
                        'script_files_count': len(result.get('script_files', [])),
                        'all_files_exist': all(os.path.exists(f) for f in result['csv_files'])
                    }
                else:
                    print(f"  錯誤訊息: {result['message']}")
                    return {
                        'success': False,
                        'error': result['message']
                    }


def test_batch_processing():
    """測試批量處理"""
    print("\n🧪 測試批量處理")
    print("=" * 50)
    
    api = ArchaeologyAPI()
    
    # 創建多個測試檔案
    test_files = []
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # 創建測試目錄結構
        test_dir = os.path.join(temp_dir, 'test_pdfs')
        os.makedirs(test_dir)
        
        # 創建多個PDF檔案
        for i in range(3):
            pdf_content = f"""{i+1} 測試題目{i+1}？
(A) 選項A{i+1}
(B) 選項B{i+1}
(C) 選項C{i+1}
(D) 選項D{i+1}
"""
            
            answer_content = f"""答案：
第{i+1}題 {'ABCD'[i % 4]}
"""
            
            pdf_path = os.path.join(test_dir, f'test{i+1}.pdf')
            answer_path = os.path.join(test_dir, f'test{i+1}_答案.pdf')
            
            with open(pdf_path, 'w', encoding='utf-8') as f:
                f.write(pdf_content)
            
            with open(answer_path, 'w', encoding='utf-8') as f:
                f.write(answer_content)
            
            test_files.append(pdf_path)
        
        # 模擬PDF處理
        def mock_pdf_open(pdf_path, **kwargs):
            mock_pdf = MagicMock()
            mock_page = MagicMock()
            
            # 根據檔案名返回不同內容
            if 'test1' in pdf_path:
                mock_page.extract_text.return_value = """1 測試題目1？
(A) 選項A1
(B) 選項B1
(C) 選項C1
(D) 選項D1
"""
            elif 'test2' in pdf_path:
                mock_page.extract_text.return_value = """2 測試題目2？
(A) 選項A2
(B) 選項B2
(C) 選項C2
(D) 選項D2
"""
            elif 'test3' in pdf_path:
                mock_page.extract_text.return_value = """3 測試題目3？
(A) 選項A3
(B) 選項B3
(C) 選項C3
(D) 選項D3
"""
            else:
                mock_page.extract_text.return_value = ""
            
            mock_pdf.pages = [mock_page]
            return mock_pdf
        
        with patch('src.core.pdf_processor.pdfplumber.open', side_effect=mock_pdf_open):
            # 執行批量處理
            start_time = time.time()
            result = api.process_directory(test_dir, temp_dir, generate_script=True)
            end_time = time.time()
            
            processing_time = end_time - start_time
            
            # 驗證結果
            print(f"  處理成功: {'✅' if result['success'] else '❌'}")
            
            if result['success']:
                print(f"  總檔案數: {result['total_files']}")
                print(f"  成功檔案數: {result['successful_files']}")
                print(f"  總題目數: {result['total_questions']}")
                print(f"  處理時間: {processing_time:.3f} 秒")
                print(f"  平均每檔案時間: {processing_time/result['total_files']:.3f} 秒")
                
                # 檢查結果檔案
                if 'results' in result:
                    for i, file_result in enumerate(result['results']):
                        print(f"    檔案{i+1}: {'✅' if file_result['success'] else '❌'} "
                              f"({file_result.get('questions_count', 0)} 題)")
                
                return {
                    'success': True,
                    'total_files': result['total_files'],
                    'successful_files': result['successful_files'],
                    'total_questions': result['total_questions'],
                    'processing_time': processing_time,
                    'avg_time_per_file': processing_time / result['total_files']
                }
            else:
                print(f"  錯誤訊息: {result['message']}")
                return {
                    'success': False,
                    'error': result['message']
                }


def test_real_world_scenarios():
    """測試真實世界場景"""
    print("\n🧪 測試真實世界場景")
    print("=" * 50)
    
    api = ArchaeologyAPI()
    
    # 模擬真實考古題格式
    real_world_content = """1 經公務人員考試錄取，接受訓練之人員 各級學校之軍訓教官
(A) 經公務人員考試錄取，接受訓練之人員
(B) 各級學校之軍訓教官
(C) 以上皆是
(D) 以上皆非

2 依公務人員任用法規定，下列何者正確？
(A) 公務人員之任用，應本功績制原則
(B) 公務人員之任用，應本年資制原則
(C) 公務人員之任用，應本關係制原則
(D) 公務人員之任用，應本隨機制原則

3 公務人員之任用，應本何種原則？
(A) 功績制原則
(B) 年資制原則
(C) 關係制原則
(D) 隨機制原則

4 下列何者為公務人員任用之基本原則？
(A) 功績制
(B) 年資制
(C) 關係制
(D) 隨機制
"""
    
    real_world_answers = """答案：
第1題 C
第2題 A
第3題 A
第4題 A
"""
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # 創建測試檔案
        pdf_path = os.path.join(temp_dir, 'real_world_test.pdf')
        answer_path = os.path.join(temp_dir, 'real_world_test_答案.pdf')
        
        with open(pdf_path, 'w', encoding='utf-8') as f:
            f.write(real_world_content)
        
        with open(answer_path, 'w', encoding='utf-8') as f:
            f.write(real_world_answers)
        
        # 模擬PDF處理
        with patch('src.core.pdf_processor.pdfplumber.open') as mock_open:
            mock_pdf = MagicMock()
            mock_page = MagicMock()
            mock_page.extract_text.return_value = real_world_content
            mock_pdf.pages = [mock_page]
            mock_open.return_value.__enter__.return_value = mock_pdf
            
            with patch('src.core.pdf_processor.pdfplumber.open') as mock_answer_open:
                mock_answer_pdf = MagicMock()
                mock_answer_page = MagicMock()
                mock_answer_page.extract_text.return_value = real_world_answers
                mock_answer_pdf.pages = [mock_answer_page]
                mock_answer_open.return_value.__enter__.return_value = mock_answer_pdf
                
                # 執行處理
                start_time = time.time()
                result = api.process_single_pdf(
                    pdf_path, answer_path, output_dir=temp_dir, generate_script=True
                )
                end_time = time.time()
                
                processing_time = end_time - start_time
                
                # 驗證結果
                print(f"  處理成功: {'✅' if result['success'] else '❌'}")
                
                if result['success']:
                    print(f"  題目數量: {result['questions_count']}")
                    print(f"  答案數量: {result['answers_count']}")
                    print(f"  處理時間: {processing_time:.3f} 秒")
                    
                    # 檢查CSV內容品質
                    csv_files = [f for f in result['csv_files'] if f.endswith('.csv')]
                    if csv_files:
                        import pandas as pd
                        df = pd.read_csv(csv_files[0], encoding='utf-8-sig')
                        
                        # 檢查資料品質
                        valid_questions = 0
                        for _, row in df.iterrows():
                            if (row['題目'].strip() and 
                                row['選項A'].strip() and 
                                row['選項B'].strip() and 
                                row['選項C'].strip() and 
                                row['選項D'].strip() and
                                row['正確答案'].strip()):
                                valid_questions += 1
                        
                        quality_score = (valid_questions / len(df)) * 100
                        print(f"  資料品質分數: {quality_score:.1f}%")
                        
                        return {
                            'success': True,
                            'questions_count': result['questions_count'],
                            'answers_count': result['answers_count'],
                            'processing_time': processing_time,
                            'quality_score': quality_score,
                            'valid_questions': valid_questions,
                            'total_questions': len(df)
                        }
                    else:
                        return {
                            'success': False,
                            'error': '未生成CSV檔案'
                        }
                else:
                    print(f"  錯誤訊息: {result['message']}")
                    return {
                        'success': False,
                        'error': result['message']
                    }


def test_error_recovery():
    """測試錯誤恢復"""
    print("\n🧪 測試錯誤恢復")
    print("=" * 50)
    
    api = ArchaeologyAPI()
    
    # 測試部分失敗的情況
    with tempfile.TemporaryDirectory() as temp_dir:
        # 創建一個有效的PDF和一個無效的PDF
        valid_pdf = os.path.join(temp_dir, 'valid.pdf')
        invalid_pdf = os.path.join(temp_dir, 'invalid.pdf')
        
        with open(valid_pdf, 'w', encoding='utf-8') as f:
            f.write("""1 有效題目？
(A) 選項A
(B) 選項B
(C) 選項C
(D) 選項D
""")
        
        with open(invalid_pdf, 'w', encoding='utf-8') as f:
            f.write("這不是有效的題目格式")
        
        # 模擬PDF處理
        def mock_pdf_open(pdf_path, **kwargs):
            mock_pdf = MagicMock()
            mock_page = MagicMock()
            
            if 'valid' in pdf_path:
                mock_page.extract_text.return_value = """1 有效題目？
(A) 選項A
(B) 選項B
(C) 選項C
(D) 選項D
"""
            else:
                mock_page.extract_text.return_value = "這不是有效的題目格式"
            
            mock_pdf.pages = [mock_page]
            return mock_pdf
        
        with patch('src.core.pdf_processor.pdfplumber.open', side_effect=mock_pdf_open):
            # 測試單一檔案處理
            valid_result = api.process_single_pdf(valid_pdf, output_dir=temp_dir)
            invalid_result = api.process_single_pdf(invalid_pdf, output_dir=temp_dir)
            
            print(f"  有效檔案處理: {'✅' if valid_result['success'] else '❌'}")
            print(f"  無效檔案處理: {'✅' if not invalid_result['success'] else '❌'}")
            
            # 測試目錄處理（包含有效和無效檔案）
            test_dir = os.path.join(temp_dir, 'mixed')
            os.makedirs(test_dir)
            
            import shutil
            shutil.copy2(valid_pdf, os.path.join(test_dir, 'valid.pdf'))
            shutil.copy2(invalid_pdf, os.path.join(test_dir, 'invalid.pdf'))
            
            with patch('src.core.pdf_processor.pdfplumber.open', side_effect=mock_pdf_open):
                mixed_result = api.process_directory(test_dir, temp_dir)
                
                print(f"  混合目錄處理: {'✅' if mixed_result['success'] else '❌'}")
                if mixed_result['success']:
                    print(f"    總檔案數: {mixed_result['total_files']}")
                    print(f"    成功檔案數: {mixed_result['successful_files']}")
                    print(f"    失敗檔案數: {mixed_result['total_files'] - mixed_result['successful_files']}")
                
                return {
                    'valid_file_success': valid_result['success'],
                    'invalid_file_failure': not invalid_result['success'],
                    'mixed_processing_success': mixed_result['success'],
                    'total_files': mixed_result.get('total_files', 0),
                    'successful_files': mixed_result.get('successful_files', 0)
                }


def main():
    """主測試函數"""
    print("🚀 開始端到端測試")
    print("=" * 60)
    
    results = {}
    
    try:
        # 執行各項端到端測試
        results['complete_workflow'] = test_complete_workflow()
        results['batch_processing'] = test_batch_processing()
        results['real_world_scenarios'] = test_real_world_scenarios()
        results['error_recovery'] = test_error_recovery()
        
        # 生成測試報告
        print(f"\n📊 端到端測試報告")
        print("=" * 60)
        
        success_count = 0
        total_tests = len(results)
        
        for test_name, result in results.items():
            if isinstance(result, dict) and result.get('success', False):
                success_count += 1
                print(f"  {test_name}: ✅ 通過")
            else:
                print(f"  {test_name}: ❌ 失敗")
                if isinstance(result, dict) and 'error' in result:
                    print(f"    錯誤: {result['error']}")
        
        success_rate = (success_count / total_tests) * 100
        
        print(f"\n總體結果:")
        print(f"  通過測試: {success_count}/{total_tests}")
        print(f"  成功率: {success_rate:.1f}%")
        
        if success_rate == 100:
            print(f"\n✅ 所有端到端測試通過")
        elif success_rate >= 80:
            print(f"\n✅ 大部分端到端測試通過")
        else:
            print(f"\n⚠️  多個端到端測試失敗，需要檢查")
        
        print(f"\n✅ 端到端測試完成")
        
    except Exception as e:
        print(f"\n❌ 端到端測試失敗: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()