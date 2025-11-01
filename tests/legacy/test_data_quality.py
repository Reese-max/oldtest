#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
資料品質測試
測試系統輸出資料的準確性和完整性
"""

import os
import sys
import tempfile
import pandas as pd
from unittest.mock import patch, MagicMock

# 添加src目錄到路徑
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.api import ArchaeologyAPI
from src.core.question_parser import QuestionParser
from src.core.answer_processor import AnswerProcessor
from src.core.csv_generator import CSVGenerator


def test_question_parsing_accuracy():
    """測試題目解析準確性"""
    print("🧪 測試題目解析準確性")
    print("=" * 50)
    
    parser = QuestionParser()
    
    # 測試各種題目格式
    test_cases = [
        {
            'name': '標準格式',
            'text': """
1 下列何者正確？
(A) 選項A
(B) 選項B
(C) 選項C
(D) 選項D
""",
            'expected_questions': 1,
            'expected_options': 4
        },
        {
            'name': '題組格式',
            'text': """
請依下文回答第1題至第3題

這是一段文章內容...

第1題：根據文章，下列何者正確？
(A) 選項A
(B) 選項B
(C) 選項C
(D) 選項D

第2題：根據文章，下列何者錯誤？
(A) 選項A
(B) 選項B
(C) 選項C
(D) 選項D

第3題：根據文章，下列何者最適合？
(A) 選項A
(B) 選項B
(C) 選項C
(D) 選項D
""",
            'expected_questions': 3,
            'expected_options': 4
        },
        {
            'name': '真實考古題格式',
            'text': """
1 經公務人員考試錄取，接受訓練之人員 各級學校之軍訓教官
(A) 經公務人員考試錄取，接受訓練之人員
(B) 各級學校之軍訓教官
(C) 以上皆是
(D) 以上皆非

2 依公務人員任用法規定，下列何者正確？
(A) 選項A
(B) 選項B
(C) 選項C
(D) 選項D
""",
            'expected_questions': 2,
            'expected_options': 4
        }
    ]
    
    results = []
    
    for case in test_cases:
        questions = parser.parse_questions(case['text'])
        
        # 檢查題目數量
        question_count = len(questions)
        question_count_correct = question_count == case['expected_questions']
        
        # 檢查選項數量
        option_count_correct = True
        if questions:
            for question in questions:
                option_count = sum(1 for opt in ['A', 'B', 'C', 'D'] 
                                 if question.get(f'選項{opt}', '').strip())
                if option_count < case['expected_options']:
                    option_count_correct = False
                    break
        
        # 檢查題目內容完整性
        content_complete = True
        if questions:
            for question in questions:
                if not question.get('題目', '').strip():
                    content_complete = False
                    break
                if not question.get('題號', '').strip():
                    content_complete = False
                    break
        
        result = {
            'name': case['name'],
            'question_count': question_count,
            'expected_questions': case['expected_questions'],
            'question_count_correct': question_count_correct,
            'option_count_correct': option_count_correct,
            'content_complete': content_complete,
            'overall_correct': question_count_correct and option_count_correct and content_complete
        }
        
        results.append(result)
        
        print(f"  {case['name']}:")
        print(f"    題目數量: {question_count}/{case['expected_questions']} {'✅' if question_count_correct else '❌'}")
        print(f"    選項完整: {'✅' if option_count_correct else '❌'}")
        print(f"    內容完整: {'✅' if content_complete else '❌'}")
        print(f"    整體正確: {'✅' if result['overall_correct'] else '❌'}")
    
    # 計算準確率
    correct_count = sum(1 for r in results if r['overall_correct'])
    accuracy = (correct_count / len(results)) * 100
    
    print(f"\n✅ 題目解析準確性: {accuracy:.1f}% ({correct_count}/{len(results)})")
    
    return {
        'accuracy': accuracy,
        'results': results
    }


def test_answer_extraction_accuracy():
    """測試答案提取準確性"""
    print("\n🧪 測試答案提取準確性")
    print("=" * 50)
    
    processor = AnswerProcessor()
    
    # 測試各種答案格式
    test_cases = [
        {
            'name': '標準格式',
            'text': """
答案：
第1題 A
第2題 B
第3題 C
第4題 D
""",
            'expected_answers': {'1': 'A', '2': 'B', '3': 'C', '4': 'D'}
        },
        {
            'name': '表格格式',
            'text': """
題號 第1題 第2題 第3題 第4題
答案 A B C D
""",
            'expected_answers': {'1': 'A', '2': 'B', '3': 'C', '4': 'D'}
        },
        {
            'name': '混合格式',
            'text': """
答案：
1. A
2. B
第3題 C
4 D
""",
            'expected_answers': {'1': 'A', '2': 'B', '3': 'C', '4': 'D'}
        }
    ]
    
    results = []
    
    for case in test_cases:
        answers = processor.extract_answers(case['text'])
        
        # 檢查答案數量
        answer_count = len(answers)
        expected_count = len(case['expected_answers'])
        count_correct = answer_count == expected_count
        
        # 檢查答案內容
        content_correct = True
        for question_num, expected_answer in case['expected_answers'].items():
            if answers.get(question_num) != expected_answer:
                content_correct = False
                break
        
        result = {
            'name': case['name'],
            'answer_count': answer_count,
            'expected_count': expected_count,
            'count_correct': count_correct,
            'content_correct': content_correct,
            'overall_correct': count_correct and content_correct
        }
        
        results.append(result)
        
        print(f"  {case['name']}:")
        print(f"    答案數量: {answer_count}/{expected_count} {'✅' if count_correct else '❌'}")
        print(f"    答案內容: {'✅' if content_correct else '❌'}")
        print(f"    整體正確: {'✅' if result['overall_correct'] else '❌'}")
    
    # 計算準確率
    correct_count = sum(1 for r in results if r['overall_correct'])
    accuracy = (correct_count / len(results)) * 100
    
    print(f"\n✅ 答案提取準確性: {accuracy:.1f}% ({correct_count}/{len(results)})")
    
    return {
        'accuracy': accuracy,
        'results': results
    }


def test_csv_output_quality():
    """測試CSV輸出品質"""
    print("\n🧪 測試CSV輸出品質")
    print("=" * 50)
    
    generator = CSVGenerator()
    
    # 創建測試資料
    test_questions = [
        {
            '題號': '1',
            '題目': '測試題目1',
            '選項A': '選項A1',
            '選項B': '選項B1',
            '選項C': '選項C1',
            '選項D': '選項D1',
            '題型': '選擇題',
            '題組': False
        },
        {
            '題號': '2',
            '題目': '測試題目2',
            '選項A': '選項A2',
            '選項B': '選項B2',
            '選項C': '選項C2',
            '選項D': '選項D2',
            '題型': '選擇題',
            '題組': True,
            '題組編號': '1-2'
        }
    ]
    
    test_answers = {'1': 'A', '2': 'B'}
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # 生成CSV檔案
        output_path = os.path.join(temp_dir, 'quality_test.csv')
        result_path = generator.generate_questions_csv(test_questions, test_answers, output_path)
        
        # 檢查檔案是否存在
        file_exists = os.path.exists(result_path)
        
        # 檢查CSV內容
        csv_valid = False
        csv_columns = []
        csv_data = []
        
        try:
            df = pd.read_csv(result_path, encoding='utf-8-sig')
            csv_valid = True
            csv_columns = list(df.columns)
            csv_data = df.to_dict('records')
        except Exception as e:
            print(f"    CSV讀取失敗: {e}")
        
        # 檢查必要欄位
        required_columns = ['題號', '題目', '選項A', '選項B', '選項C', '選項D', '正確答案']
        columns_complete = all(col in csv_columns for col in required_columns)
        
        # 檢查資料完整性
        data_complete = True
        if csv_data:
            for row in csv_data:
                if not row.get('題號') or not row.get('題目'):
                    data_complete = False
                    break
        
        # 檢查答案對應
        answer_correct = True
        if csv_data:
            for row in csv_data:
                question_num = str(row.get('題號', ''))
                if question_num in test_answers:
                    if row.get('正確答案') != test_answers[question_num]:
                        answer_correct = False
                        break
        
        print(f"  檔案存在: {'✅' if file_exists else '❌'}")
        print(f"  CSV格式有效: {'✅' if csv_valid else '❌'}")
        print(f"  欄位完整: {'✅' if columns_complete else '❌'}")
        print(f"  資料完整: {'✅' if data_complete else '❌'}")
        print(f"  答案正確: {'✅' if answer_correct else '❌'}")
        
        overall_quality = file_exists and csv_valid and columns_complete and data_complete and answer_correct
        print(f"  整體品質: {'✅' if overall_quality else '❌'}")
        
        return {
            'file_exists': file_exists,
            'csv_valid': csv_valid,
            'columns_complete': columns_complete,
            'data_complete': data_complete,
            'answer_correct': answer_correct,
            'overall_quality': overall_quality
        }


def test_data_consistency():
    """測試資料一致性"""
    print("\n🧪 測試資料一致性")
    print("=" * 50)
    
    parser = QuestionParser()
    processor = AnswerProcessor()
    generator = CSVGenerator()
    
    # 創建一致的測試資料
    test_text = """
1 下列何者正確？
(A) 選項A
(B) 選項B
(C) 選項C
(D) 選項D

2 下列何者錯誤？
(A) 選項A
(B) 選項B
(C) 選項C
(D) 選項D
"""
    
    test_answer_text = """
答案：
第1題 A
第2題 B
"""
    
    # 解析題目和答案
    questions = parser.parse_questions(test_text)
    answers = processor.extract_answers(test_answer_text)
    
    # 檢查題目和答案數量一致
    question_count = len(questions)
    answer_count = len(answers)
    count_consistent = question_count == answer_count
    
    # 檢查題號一致
    question_numbers = set(q.get('題號') for q in questions)
    answer_numbers = set(answers.keys())
    number_consistent = question_numbers == answer_numbers
    
    # 生成CSV並檢查
    with tempfile.TemporaryDirectory() as temp_dir:
        output_path = os.path.join(temp_dir, 'consistency_test.csv')
        generator.generate_questions_csv(questions, answers, output_path)
        
        # 讀取CSV檢查一致性
        df = pd.read_csv(output_path, encoding='utf-8-sig')
        csv_question_count = len(df)
        csv_consistent = csv_question_count == question_count
        
        # 檢查CSV中的答案
        csv_answer_consistent = True
        for _, row in df.iterrows():
            question_num = str(row['題號'])
            if question_num in answers:
                if row['正確答案'] != answers[question_num]:
                    csv_answer_consistent = False
                    break
    
    print(f"  題目答案數量一致: {'✅' if count_consistent else '❌'}")
    print(f"  題號一致: {'✅' if number_consistent else '❌'}")
    print(f"  CSV數量一致: {'✅' if csv_consistent else '❌'}")
    print(f"  CSV答案一致: {'✅' if csv_answer_consistent else '❌'}")
    
    overall_consistent = count_consistent and number_consistent and csv_consistent and csv_answer_consistent
    print(f"  整體一致性: {'✅' if overall_consistent else '❌'}")
    
    return {
        'count_consistent': count_consistent,
        'number_consistent': number_consistent,
        'csv_consistent': csv_consistent,
        'csv_answer_consistent': csv_answer_consistent,
        'overall_consistent': overall_consistent
    }


def test_unicode_handling():
    """測試Unicode處理"""
    print("\n🧪 測試Unicode處理")
    print("=" * 50)
    
    parser = QuestionParser()
    processor = AnswerProcessor()
    generator = CSVGenerator()
    
    # 測試包含各種Unicode字符的內容
    unicode_text = """
1 測試題目包含特殊字符：αβγδε 中文標點：，。！？
(A) 選項A包含特殊字符：αβγδε
(B) 選項B包含特殊字符：αβγδε
(C) 選項C包含特殊字符：αβγδε
(D) 選項D包含特殊字符：αβγδε
"""
    
    unicode_answer_text = """
答案：
第1題 A
"""
    
    try:
        # 解析題目
        questions = parser.parse_questions(unicode_text)
        question_unicode_ok = len(questions) > 0
        
        # 提取答案
        answers = processor.extract_answers(unicode_answer_text)
        answer_unicode_ok = len(answers) > 0
        
        # 生成CSV
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = os.path.join(temp_dir, 'unicode_test.csv')
            generator.generate_questions_csv(questions, answers, output_path)
            
            # 讀取CSV檢查Unicode
            df = pd.read_csv(output_path, encoding='utf-8-sig')
            csv_unicode_ok = True
            
            # 檢查是否包含特殊字符
            for _, row in df.iterrows():
                if 'αβγδε' in str(row.get('題目', '')):
                    csv_unicode_ok = True
                    break
                else:
                    csv_unicode_ok = False
        
        print(f"  題目Unicode處理: {'✅' if question_unicode_ok else '❌'}")
        print(f"  答案Unicode處理: {'✅' if answer_unicode_ok else '❌'}")
        print(f"  CSV Unicode處理: {'✅' if csv_unicode_ok else '❌'}")
        
        overall_unicode_ok = question_unicode_ok and answer_unicode_ok and csv_unicode_ok
        print(f"  整體Unicode處理: {'✅' if overall_unicode_ok else '❌'}")
        
        return {
            'question_unicode_ok': question_unicode_ok,
            'answer_unicode_ok': answer_unicode_ok,
            'csv_unicode_ok': csv_unicode_ok,
            'overall_unicode_ok': overall_unicode_ok
        }
        
    except Exception as e:
        print(f"  Unicode處理失敗: {e}")
        return {
            'question_unicode_ok': False,
            'answer_unicode_ok': False,
            'csv_unicode_ok': False,
            'overall_unicode_ok': False
        }


def main():
    """主測試函數"""
    print("🚀 開始資料品質測試")
    print("=" * 60)
    
    results = {}
    
    try:
        # 執行各項品質測試
        results['question_parsing'] = test_question_parsing_accuracy()
        results['answer_extraction'] = test_answer_extraction_accuracy()
        results['csv_output'] = test_csv_output_quality()
        results['data_consistency'] = test_data_consistency()
        results['unicode_handling'] = test_unicode_handling()
        
        # 計算整體品質分數
        quality_scores = []
        
        if 'accuracy' in results['question_parsing']:
            quality_scores.append(results['question_parsing']['accuracy'])
        
        if 'accuracy' in results['answer_extraction']:
            quality_scores.append(results['answer_extraction']['accuracy'])
        
        if results['csv_output']['overall_quality']:
            quality_scores.append(100)
        else:
            quality_scores.append(0)
        
        if results['data_consistency']['overall_consistent']:
            quality_scores.append(100)
        else:
            quality_scores.append(0)
        
        if results['unicode_handling']['overall_unicode_ok']:
            quality_scores.append(100)
        else:
            quality_scores.append(0)
        
        overall_quality = sum(quality_scores) / len(quality_scores) if quality_scores else 0
        
        # 生成品質報告
        print(f"\n📊 資料品質測試報告")
        print("=" * 60)
        print(f"題目解析準確性: {results['question_parsing'].get('accuracy', 0):.1f}%")
        print(f"答案提取準確性: {results['answer_extraction'].get('accuracy', 0):.1f}%")
        print(f"CSV輸出品質: {'✅ 優秀' if results['csv_output']['overall_quality'] else '❌ 需要改進'}")
        print(f"資料一致性: {'✅ 優秀' if results['data_consistency']['overall_consistent'] else '❌ 需要改進'}")
        print(f"Unicode處理: {'✅ 優秀' if results['unicode_handling']['overall_unicode_ok'] else '❌ 需要改進'}")
        print(f"整體品質分數: {overall_quality:.1f}/100")
        
        if overall_quality >= 90:
            print(f"\n✅ 資料品質優秀")
        elif overall_quality >= 80:
            print(f"\n✅ 資料品質良好")
        elif overall_quality >= 70:
            print(f"\n⚠️  資料品質一般，需要改進")
        else:
            print(f"\n❌ 資料品質較差，需要大幅改進")
        
        print(f"\n✅ 資料品質測試完成")
        
    except Exception as e:
        print(f"\n❌ 資料品質測試失敗: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()