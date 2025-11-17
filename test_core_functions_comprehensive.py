#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
核心功能綜合測試
從模擬數據到Google Apps Script的完整流程測試
"""

import os
import json
import sys
sys.path.insert(0, '/home/user/oldtest')

from src.core.question_parser import QuestionParser
from src.core.answer_processor import AnswerProcessor
from src.core.csv_generator import CSVGenerator
from src.core.google_script_generator import GoogleScriptGenerator

# 測試數據
TEST_QUESTIONS = [
    {
        '題號': '1',
        '題目': '下列何者為台灣最高峰？',
        '題型': '選擇題',
        '選項A': '玉山',
        '選項B': '雪山',
        '選項C': '合歡山',
        '選項D': '阿里山',
        '題組': False,
        '題組編號': ''
    },
    {
        '題號': '2',
        '題目': '以下何者不是台灣的直轄市？',
        '題型': '選擇題',
        '選項A': '台北市',
        '選項B': '新北市',
        '選項C': '基隆市',
        '選項D': '桃園市',
        '題組': False,
        '題組編號': ''
    },
    {
        '題號': '3',
        '題目': '台灣的貨幣單位為？',
        '題型': '選擇題',
        '選項A': '人民幣',
        '選項B': '新台幣',
        '選項C': '港幣',
        '選項D': '美金',
        '題組': False,
        '題組編號': ''
    }
]

TEST_ANSWERS = {
    '1': 'A',
    '2': 'C',
    '3': 'B'
}

TEST_CORRECTED_ANSWERS = {}  # 沒有更正答案

def test_01_question_parser():
    """測試題目解析器"""
    print("\n" + "="*60)
    print("測試 1: 題目解析器")
    print("="*60)

    parser = QuestionParser()

    # 測試文本
    test_text = """
    1. 下列何者為台灣最高峰？
    (A) 玉山
    (B) 雪山
    (C) 合歡山
    (D) 阿里山

    2. 以下何者不是台灣的直轄市？
    (A) 台北市
    (B) 新北市
    (C) 基隆市
    (D) 桃園市
    """

    try:
        questions = parser.parse_questions(test_text)
        print(f"✅ 成功解析 {len(questions)} 題")

        if questions:
            print(f"\n第一題預覽:")
            q = questions[0]
            print(f"  題號: {q.get('題號')}")
            print(f"  題目: {q.get('題目', '')[:50]}...")
            print(f"  選項A: {q.get('選項A', '')}")

        return True
    except Exception as e:
        print(f"❌ 錯誤: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_02_answer_processor():
    """測試答案處理器"""
    print("\n" + "="*60)
    print("測試 2: 答案處理器")
    print("="*60)

    processor = AnswerProcessor()

    # 測試文本
    test_text = """
    答案:
    1. A
    2. C
    3. B
    """

    try:
        answers = processor.extract_answers(test_text)
        print(f"✅ 成功提取 {len(answers)} 個答案")
        print(f"   答案: {answers}")

        # 測試答案統計
        stats = processor.get_answer_statistics(answers)
        print(f"   統計: {stats}")

        return True
    except Exception as e:
        print(f"❌ 錯誤: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_03_csv_generator():
    """測試CSV生成器"""
    print("\n" + "="*60)
    print("測試 3: CSV生成器")
    print("="*60)

    generator = CSVGenerator()
    output_dir = 'test_output_comprehensive'
    os.makedirs(output_dir, exist_ok=True)

    try:
        # 生成一般CSV
        csv_path = os.path.join(output_dir, 'test_questions.csv')
        generator.generate_questions_csv(
            TEST_QUESTIONS,
            TEST_ANSWERS,
            csv_path
        )
        print(f"✅ 成功生成CSV: {csv_path}")
        print(f"   檔案大小: {os.path.getsize(csv_path)} bytes")

        # 生成Google表單CSV
        google_csv_path = os.path.join(output_dir, 'test_questions_google.csv')
        generator.generate_google_form_csv(
            TEST_QUESTIONS,
            TEST_ANSWERS,
            TEST_CORRECTED_ANSWERS,
            google_csv_path
        )
        print(f"✅ 成功生成Google表單CSV: {google_csv_path}")
        print(f"   檔案大小: {os.path.getsize(google_csv_path)} bytes")

        # 讀取並顯示前幾行
        with open(csv_path, 'r', encoding='utf-8-sig') as f:
            lines = f.readlines()[:5]
            print(f"\n   CSV內容預覽 (前5行):")
            for line in lines:
                print(f"   {line.strip()}")

        return True
    except Exception as e:
        print(f"❌ 錯誤: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_04_google_script_generator():
    """測試Google Apps Script生成器"""
    print("\n" + "="*60)
    print("測試 4: Google Apps Script生成器")
    print("="*60)

    generator = GoogleScriptGenerator()
    output_dir = 'test_output_comprehensive'

    try:
        # 生成Google Apps Script
        csv_path = os.path.join(output_dir, 'test_questions_google.csv')
        script_path = os.path.join(output_dir, 'test_GoogleAppsScript.js')

        generator.generate_script(
            csv_path,
            script_path
        )
        print(f"✅ 成功生成Google Apps Script: {script_path}")
        print(f"   檔案大小: {os.path.getsize(script_path)} bytes")

        # 讀取並顯示前幾行
        with open(script_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()[:20]
            print(f"\n   Script內容預覽 (前20行):")
            for i, line in enumerate(lines, 1):
                print(f"   {i:3d}: {line.rstrip()}")

        return True
    except Exception as e:
        print(f"❌ 錯誤: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_05_end_to_end():
    """測試完整端到端流程"""
    print("\n" + "="*60)
    print("測試 5: 完整端到端流程")
    print("="*60)

    output_dir = 'test_output_comprehensive'
    os.makedirs(output_dir, exist_ok=True)

    try:
        # 1. CSV生成
        csv_gen = CSVGenerator()
        google_csv_path = os.path.join(output_dir, 'end_to_end_google.csv')
        csv_gen.generate_google_form_csv(
            TEST_QUESTIONS,
            TEST_ANSWERS,
            TEST_CORRECTED_ANSWERS,
            google_csv_path
        )
        print(f"✅ 步驟1: CSV生成完成")

        # 2. Script生成
        script_gen = GoogleScriptGenerator()
        script_path = os.path.join(output_dir, 'end_to_end_GoogleAppsScript.js')
        script_gen.generate_script(google_csv_path, script_path)
        print(f"✅ 步驟2: Google Apps Script生成完成")

        # 3. 驗證輸出
        assert os.path.exists(google_csv_path), "CSV文件不存在"
        assert os.path.exists(script_path), "Script文件不存在"
        assert os.path.getsize(google_csv_path) > 0, "CSV文件為空"
        assert os.path.getsize(script_path) > 0, "Script文件為空"

        print(f"✅ 步驟3: 文件驗證通過")
        print(f"\n生成的文件:")
        print(f"  - {google_csv_path} ({os.path.getsize(google_csv_path)} bytes)")
        print(f"  - {script_path} ({os.path.getsize(script_path)} bytes)")

        return True
    except Exception as e:
        print(f"❌ 錯誤: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_06_script_validation():
    """測試Script內容驗證"""
    print("\n" + "="*60)
    print("測試 6: Script內容驗證")
    print("="*60)

    script_path = 'test_output_comprehensive/end_to_end_GoogleAppsScript.js'

    try:
        with open(script_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 檢查必要的函數和配置
        checks = [
            ('main()', 'main函數'),
            ('createForm()', 'createForm函數'),
            ('addQuestion(', 'addQuestion函數'),
            ('setCorrectAnswer(', 'setCorrectAnswer函數'),
            ('FormApp.create', 'FormApp API'),
            ('setIsQuiz(true)', 'Quiz模式設定'),
        ]

        all_passed = True
        for check_str, desc in checks:
            if check_str in content:
                print(f"✅ 包含 {desc}")
            else:
                print(f"❌ 缺少 {desc}")
                all_passed = False

        # 檢查題目數量
        question_count = content.count('addQuestion(form,')
        print(f"\n✅ Script中包含 {question_count} 個題目")

        # 檢查自動評分設定
        if 'setPoints(' in content:
            print(f"✅ 包含自動評分設定")
        else:
            print(f"⚠️  未發現自動評分設定")

        return all_passed
    except Exception as e:
        print(f"❌ 錯誤: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """執行所有測試"""
    print("\n" + "="*60)
    print("🧪 核心功能綜合測試")
    print("="*60)
    print("測試範圍: 題目解析 → 答案處理 → CSV生成 → Google Apps Script")

    tests = [
        ("題目解析器", test_01_question_parser),
        ("答案處理器", test_02_answer_processor),
        ("CSV生成器", test_03_csv_generator),
        ("Google Apps Script生成器", test_04_google_script_generator),
        ("完整端到端流程", test_05_end_to_end),
        ("Script內容驗證", test_06_script_validation),
    ]

    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n❌ 測試 '{name}' 執行失敗: {e}")
            results.append((name, False))

    # 總結
    print("\n" + "="*60)
    print("📊 測試總結")
    print("="*60)

    passed = sum(1 for _, r in results if r)
    total = len(results)

    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {name}")

    print(f"\n總計: {passed}/{total} 測試通過 ({passed/total*100:.1f}%)")

    if passed == total:
        print("\n🎉 所有測試通過！系統功能正常。")
        return 0
    else:
        print(f"\n⚠️  {total-passed} 個測試失敗，請檢查。")
        return 1

if __name__ == '__main__':
    exit(main())
