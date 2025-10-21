#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
性能測試
測試系統的處理速度和記憶體使用情況
"""

import time
import psutil
import os
import sys
import tempfile
from unittest.mock import patch, MagicMock

# 添加src目錄到路徑
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.api import ArchaeologyAPI
from src.core.question_parser import QuestionParser
from src.core.answer_processor import AnswerProcessor
from src.core.csv_generator import CSVGenerator


def measure_memory_usage():
    """測量記憶體使用量"""
    process = psutil.Process(os.getpid())
    return process.memory_info().rss / 1024 / 1024  # MB


def test_question_parser_performance():
    """測試題目解析器性能"""
    print("🧪 測試題目解析器性能")
    print("=" * 50)
    
    parser = QuestionParser()
    
    # 創建大量題目的測試文字
    large_text = ""
    for i in range(100):
        large_text += f"""
{i+1} 這是一個測試題目，用來驗證系統的題目解析功能是否正常運作，包含足夠的內容來測試性能。
(A) 選項A內容
(B) 選項B內容
(C) 選項C內容
(D) 選項D內容
"""
    
    # 測量記憶體使用
    start_memory = measure_memory_usage()
    start_time = time.time()
    
    # 執行解析
    questions = parser.parse_questions(large_text)
    
    end_time = time.time()
    end_memory = measure_memory_usage()
    
    # 計算結果
    processing_time = end_time - start_time
    memory_used = end_memory - start_memory
    
    print(f"✅ 解析完成")
    print(f"   題目數量: {len(questions)}")
    print(f"   處理時間: {processing_time:.3f} 秒")
    print(f"   記憶體使用: {memory_used:.2f} MB")
    print(f"   平均每題時間: {processing_time/len(questions)*1000:.2f} ms")
    
    return {
        'questions_count': len(questions),
        'processing_time': processing_time,
        'memory_used': memory_used,
        'avg_time_per_question': processing_time / len(questions) if questions else 0
    }


def test_answer_processor_performance():
    """測試答案處理器性能"""
    print("\n🧪 測試答案處理器性能")
    print("=" * 50)
    
    processor = AnswerProcessor()
    
    # 創建大量答案的測試文字
    large_answer_text = "答案：\n"
    for i in range(100):
        large_answer_text += f"第{i+1}題 {'ABCD'[i % 4]}\n"
    
    # 測量記憶體使用
    start_memory = measure_memory_usage()
    start_time = time.time()
    
    # 執行答案提取
    answers = processor.extract_answers(large_answer_text)
    
    end_time = time.time()
    end_memory = measure_memory_usage()
    
    # 計算結果
    processing_time = end_time - start_time
    memory_used = end_memory - start_memory
    
    print(f"✅ 答案提取完成")
    print(f"   答案數量: {len(answers)}")
    print(f"   處理時間: {processing_time:.3f} 秒")
    print(f"   記憶體使用: {memory_used:.2f} MB")
    print(f"   平均每個答案時間: {processing_time/len(answers)*1000:.2f} ms")
    
    return {
        'answers_count': len(answers),
        'processing_time': processing_time,
        'memory_used': memory_used,
        'avg_time_per_answer': processing_time / len(answers) if answers else 0
    }


def test_csv_generator_performance():
    """測試CSV生成器性能"""
    print("\n🧪 測試CSV生成器性能")
    print("=" * 50)
    
    generator = CSVGenerator()
    
    # 創建大量題目資料
    questions = []
    answers = {}
    
    for i in range(100):
        questions.append({
            '題號': str(i+1),
            '題目': f'這是一個測試題目{i+1}，用來驗證系統的CSV生成功能是否正常運作。',
            '選項A': f'選項A{i+1}',
            '選項B': f'選項B{i+1}',
            '選項C': f'選項C{i+1}',
            '選項D': f'選項D{i+1}',
            '題型': '選擇題',
            '題組': False
        })
        answers[str(i+1)] = 'ABCD'[i % 4]
    
    with tempfile.TemporaryDirectory() as temp_dir:
        output_path = os.path.join(temp_dir, 'performance_test.csv')
        
        # 測量記憶體使用
        start_memory = measure_memory_usage()
        start_time = time.time()
        
        # 執行CSV生成
        result_path = generator.generate_questions_csv(questions, answers, output_path)
        
        end_time = time.time()
        end_memory = measure_memory_usage()
        
        # 計算結果
        processing_time = end_time - start_time
        memory_used = end_memory - start_memory
        file_size = os.path.getsize(result_path) / 1024  # KB
        
        print(f"✅ CSV生成完成")
        print(f"   題目數量: {len(questions)}")
        print(f"   處理時間: {processing_time:.3f} 秒")
        print(f"   記憶體使用: {memory_used:.2f} MB")
        print(f"   檔案大小: {file_size:.2f} KB")
        print(f"   平均每題時間: {processing_time/len(questions)*1000:.2f} ms")
        
        return {
            'questions_count': len(questions),
            'processing_time': processing_time,
            'memory_used': memory_used,
            'file_size': file_size,
            'avg_time_per_question': processing_time / len(questions)
        }


def test_end_to_end_performance():
    """測試端到端性能"""
    print("\n🧪 測試端到端性能")
    print("=" * 50)
    
    api = ArchaeologyAPI()
    
    # 創建大量題目的測試內容
    test_content = ""
    for i in range(50):
        test_content += f"""
{i+1} 這是一個測試題目，用來驗證系統的端到端性能是否正常運作。
(A) 選項A內容
(B) 選項B內容
(C) 選項C內容
(D) 選項D內容
"""
    
    test_answer_content = "答案：\n"
    for i in range(50):
        test_answer_content += f"第{i+1}題 {'ABCD'[i % 4]}\n"
    
    with tempfile.TemporaryDirectory() as temp_dir:
        pdf_path = os.path.join(temp_dir, 'performance_test.pdf')
        answer_path = os.path.join(temp_dir, 'performance_test_答案.pdf')
        
        with open(pdf_path, 'w', encoding='utf-8') as f:
            f.write(test_content)
        
        with open(answer_path, 'w', encoding='utf-8') as f:
            f.write(test_answer_content)
        
        # 模擬PDF處理
        with patch('src.core.pdf_processor.pdfplumber.open') as mock_open:
            mock_pdf = MagicMock()
            mock_page = MagicMock()
            mock_page.extract_text.return_value = test_content
            mock_pdf.pages = [mock_page]
            mock_open.return_value.__enter__.return_value = mock_pdf
            
            with patch('src.core.pdf_processor.pdfplumber.open') as mock_answer_open:
                mock_answer_pdf = MagicMock()
                mock_answer_page = MagicMock()
                mock_answer_page.extract_text.return_value = test_answer_content
                mock_answer_pdf.pages = [mock_answer_page]
                mock_answer_open.return_value.__enter__.return_value = mock_answer_pdf
                
                # 測量記憶體使用
                start_memory = measure_memory_usage()
                start_time = time.time()
                
                # 執行端到端處理
                result = api.process_single_pdf(
                    pdf_path, answer_path, output_dir=temp_dir, generate_script=False
                )
                
                end_time = time.time()
                end_memory = measure_memory_usage()
                
                # 計算結果
                processing_time = end_time - start_time
                memory_used = end_memory - start_memory
                
                print(f"✅ 端到端處理完成")
                print(f"   成功: {result['success']}")
                if result['success']:
                    print(f"   題目數量: {result['questions_count']}")
                    print(f"   處理時間: {processing_time:.3f} 秒")
                    print(f"   記憶體使用: {memory_used:.2f} MB")
                    print(f"   平均每題時間: {processing_time/result['questions_count']*1000:.2f} ms")
                else:
                    print(f"   錯誤: {result['message']}")
                
                return {
                    'success': result['success'],
                    'questions_count': result.get('questions_count', 0),
                    'processing_time': processing_time,
                    'memory_used': memory_used,
                    'avg_time_per_question': processing_time / result.get('questions_count', 1)
                }


def test_memory_leak():
    """測試記憶體洩漏"""
    print("\n🧪 測試記憶體洩漏")
    print("=" * 50)
    
    parser = QuestionParser()
    
    # 重複執行多次解析
    initial_memory = measure_memory_usage()
    memory_usage = []
    
    for i in range(10):
        test_text = f"""
{i+1} 這是一個測試題目，用來驗證系統是否有記憶體洩漏問題。
(A) 選項A
(B) 選項B
(C) 選項C
(D) 選項D
"""
        
        questions = parser.parse_questions(test_text)
        current_memory = measure_memory_usage()
        memory_usage.append(current_memory)
        
        print(f"   第{i+1}次: {len(questions)} 題, 記憶體: {current_memory:.2f} MB")
    
    final_memory = measure_memory_usage()
    memory_increase = final_memory - initial_memory
    
    print(f"✅ 記憶體洩漏測試完成")
    print(f"   初始記憶體: {initial_memory:.2f} MB")
    print(f"   最終記憶體: {final_memory:.2f} MB")
    print(f"   記憶體增加: {memory_increase:.2f} MB")
    
    if memory_increase > 10:  # 如果記憶體增加超過10MB，可能有洩漏
        print("   ⚠️  警告: 可能存在記憶體洩漏")
    else:
        print("   ✅ 無明顯記憶體洩漏")
    
    return {
        'initial_memory': initial_memory,
        'final_memory': final_memory,
        'memory_increase': memory_increase,
        'has_leak': memory_increase > 10
    }


def main():
    """主測試函數"""
    print("🚀 開始性能測試")
    print("=" * 60)
    
    results = {}
    
    try:
        # 測試各個組件性能
        results['question_parser'] = test_question_parser_performance()
        results['answer_processor'] = test_answer_processor_performance()
        results['csv_generator'] = test_csv_generator_performance()
        results['end_to_end'] = test_end_to_end_performance()
        results['memory_leak'] = test_memory_leak()
        
        # 生成性能報告
        print("\n📊 性能測試報告")
        print("=" * 60)
        
        total_questions = 0
        total_time = 0
        total_memory = 0
        
        for component, data in results.items():
            if component != 'memory_leak':
                print(f"\n{component.upper()}:")
                if 'questions_count' in data:
                    print(f"  題目數量: {data['questions_count']}")
                    total_questions += data['questions_count']
                if 'processing_time' in data:
                    print(f"  處理時間: {data['processing_time']:.3f} 秒")
                    total_time += data['processing_time']
                if 'memory_used' in data:
                    print(f"  記憶體使用: {data['memory_used']:.2f} MB")
                    total_memory += data['memory_used']
        
        print(f"\n總計:")
        print(f"  總題目數: {total_questions}")
        print(f"  總處理時間: {total_time:.3f} 秒")
        print(f"  總記憶體使用: {total_memory:.2f} MB")
        
        # 性能評估
        print(f"\n性能評估:")
        if total_time < 5:
            print("  ✅ 處理速度: 優秀")
        elif total_time < 10:
            print("  ✅ 處理速度: 良好")
        else:
            print("  ⚠️  處理速度: 需要優化")
        
        if total_memory < 100:
            print("  ✅ 記憶體使用: 優秀")
        elif total_memory < 200:
            print("  ✅ 記憶體使用: 良好")
        else:
            print("  ⚠️  記憶體使用: 需要優化")
        
        print("\n✅ 性能測試完成")
        
    except Exception as e:
        print(f"\n❌ 性能測試失敗: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()