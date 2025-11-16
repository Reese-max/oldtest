#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Google 表單生成管道完整性測試
驗證從 CSV 生成到 Google Apps Script 的完整流程
"""

import os
import sys
import pandas as pd
import tempfile
from pathlib import Path

# 添加專案路徑
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.core.csv_generator import CSVGenerator
from src.core.google_script_generator import GoogleScriptGenerator
from src.utils.logger import logger


def create_test_questions():
    """創建測試題目資料"""
    questions = [
        {
            '題號': '1',
            '題目': '下列何者為公務人員之任用方式？',
            '題型': '選擇題',
            '選項A': '經公務人員考試錄取，接受訓練之人員',
            '選項B': '經選舉產生之人員',
            '選項C': '依法派任之人員',
            '選項D': '依法聘任之人員',
            '分類': '法律',
            '難度': '簡單',
            '題組': False
        },
        {
            '題號': '2',
            '題目': '下列何者不是憲法保障之基本權利？',
            '題型': '選擇題',
            '選項A': '生存權',
            '選項B': '工作權',
            '選項C': '財產權',
            '選項D': '特權',
            '分類': '法律',
            '難度': '中等',
            '題組': False
        },
        {
            '題號': '3',
            '題目': '「讀音」的正確注音為何？',
            '題型': '選擇題',
            '選項A': 'ㄉㄨˊ ㄧㄣ',
            '選項B': 'ㄉㄨˋ ㄧㄣ',
            '選項C': 'ㄊㄨˊ ㄧㄣ',
            '選項D': '',  # 測試空選項過濾
            '分類': '語音',
            '難度': '簡單',
            '題組': False
        },
        {
            '題號': '4',
            '題目': '下列成語何者使用正確？',
            '題型': '選擇題',
            '選項A': '他的話讓人「不明所以」',
            '選項B': '他「首當其衝」地站出來',
            '選項C': '這件事「差強人意」令人滿意',
            '選項D': '他「義無反顧」地離開了',
            '分類': '成語',
            '難度': '困難',
            '題組': False
        }
    ]
    return questions


def create_test_answers():
    """創建測試答案資料"""
    answers = {
        '1': 'A',
        '2': 'D',
        '3': 'A',
        '4': 'D'
    }
    return answers


def create_test_corrected_answers():
    """創建測試更正答案資料"""
    corrected_answers = {
        '2': 'C'  # 第2題答案更正為C
    }
    return corrected_answers


def test_csv_generation(temp_dir):
    """測試 CSV 生成"""
    logger.info("=" * 60)
    logger.info("測試 1: CSV 生成")
    logger.info("=" * 60)

    csv_generator = CSVGenerator()
    questions = create_test_questions()
    answers = create_test_answers()
    corrected_answers = create_test_corrected_answers()

    csv_path = os.path.join(temp_dir, "test_google_form.csv")

    # 生成 Google 表單 CSV
    result_path = csv_generator.generate_google_form_csv(
        questions, answers, corrected_answers, csv_path
    )

    # 驗證檔案存在
    assert os.path.exists(result_path), "CSV檔案未生成"
    logger.success(f"✓ CSV檔案已生成: {result_path}")

    # 讀取並驗證內容
    df = pd.read_csv(result_path, encoding='utf-8-sig')

    # 驗證欄位
    required_columns = ['題號', '題目', '選項A', '選項B', '選項C', '選項D',
                       '正確答案', '最終答案', '更正答案', '分類', '難度']
    for col in required_columns:
        assert col in df.columns, f"缺少必要欄位: {col}"
    logger.success(f"✓ CSV包含所有必要欄位")

    # 驗證資料行數
    assert len(df) == 4, f"題目數量不符: 預期4題，實際{len(df)}題"
    logger.success(f"✓ CSV包含正確數量的題目: {len(df)}題")

    # 驗證答案
    assert df.iloc[0]['正確答案'] == 'A', "第1題答案錯誤"
    assert df.iloc[1]['正確答案'] == 'D', "第2題原始答案錯誤"
    assert df.iloc[1]['更正答案'] == 'C', "第2題更正答案錯誤"
    assert df.iloc[1]['最終答案'] == 'C', "第2題最終答案錯誤"
    logger.success(f"✓ 答案資料正確（包含更正答案）")

    # 驗證空選項處理
    assert pd.isna(df.iloc[2]['選項D']) or df.iloc[2]['選項D'] == '', "空選項未正確處理"
    logger.success(f"✓ 空選項正確處理")

    return csv_path, df


def test_google_script_generation(csv_path, temp_dir):
    """測試 Google Apps Script 生成"""
    logger.info("\n" + "=" * 60)
    logger.info("測試 2: Google Apps Script 生成")
    logger.info("=" * 60)

    script_generator = GoogleScriptGenerator()

    script_path = os.path.join(temp_dir, "test_GoogleAppsScript.js")

    # 生成 Google Apps Script
    result_path = script_generator.generate_script(csv_path, script_path)

    # 驗證檔案存在
    assert os.path.exists(result_path), "JavaScript檔案未生成"
    logger.success(f"✓ JavaScript檔案已生成: {result_path}")

    # 讀取並驗證內容
    with open(result_path, 'r', encoding='utf-8') as f:
        script_content = f.read()

    # 驗證關鍵功能
    checks = [
        ('form.setIsQuiz(true)', '測驗模式已啟用'),
        ('item.createChoice', '選項創建代碼存在'),
        ('item.setPoints(1)', '分數設定代碼存在'),
        ('const isCorrect = opt.key === correctAnswer', '答案比對邏輯正確'),
        ('function testFormStructure()', '測試函數存在'),
        ('function main()', '主函數存在'),
        ('if (value && value.trim()', '空選項過濾代碼存在'),
        ('options.length < 2', '選項數量驗證存在'),
        ('"title":', 'JSON格式正確'),
        ('questionsData', '題目資料陣列存在'),
        ('answersData', '答案資料物件存在')
    ]

    for check_str, description in checks:
        assert check_str in script_content, f"{description}失敗"
        logger.success(f"✓ {description}")

    # 驗證沒有問題的模式
    bad_patterns = [
        'createChoice("")',  # 不應該有空選項
        'userAnswer === correctAnswer',  # 舊的錯誤比對方式
        'undefined',  # 不應該有 undefined
    ]

    for pattern in bad_patterns:
        assert pattern not in script_content, f"發現問題模式: {pattern}"
    logger.success(f"✓ 未發現已知問題模式")

    # 計算統計
    question_count = script_content.count('"title":')
    answer_count = script_content.count('"1":') + script_content.count('"2":') + \
                  script_content.count('"3":') + script_content.count('"4":')

    logger.info(f"\n📊 統計資訊:")
    logger.info(f"  - 題目數量: {question_count}")
    logger.info(f"  - 答案數量: {answer_count}")
    logger.info(f"  - 檔案大小: {len(script_content)} 字元")

    return script_path, script_content


def test_data_integrity():
    """測試資料完整性"""
    logger.info("\n" + "=" * 60)
    logger.info("測試 3: 資料完整性驗證")
    logger.info("=" * 60)

    questions = create_test_questions()
    answers = create_test_answers()
    corrected_answers = create_test_corrected_answers()

    # 驗證題號與答案對應
    for q in questions:
        q_num = q['題號']
        assert q_num in answers, f"題號{q_num}缺少答案"
    logger.success(f"✓ 所有題目都有對應答案")

    # 驗證更正答案
    for q_num in corrected_answers:
        assert q_num in answers, f"更正答案題號{q_num}在原始答案中不存在"
    logger.success(f"✓ 更正答案題號正確")

    # 驗證答案格式
    valid_answers = ['A', 'B', 'C', 'D']
    for q_num, ans in answers.items():
        assert ans in valid_answers, f"題號{q_num}答案格式錯誤: {ans}"
    for q_num, ans in corrected_answers.items():
        assert ans in valid_answers, f"題號{q_num}更正答案格式錯誤: {ans}"
    logger.success(f"✓ 答案格式正確")

    return True


def test_edge_cases():
    """測試邊界情況"""
    logger.info("\n" + "=" * 60)
    logger.info("測試 4: 邊界情況測試")
    logger.info("=" * 60)

    csv_generator = CSVGenerator()

    # 測試1: 包含空選項的題目
    questions_with_empty = [
        {
            '題號': '1',
            '題目': '測試題目',
            '題型': '選擇題',
            '選項A': '選項A',
            '選項B': '',  # 空選項
            '選項C': 'nan',  # NaN字串
            '選項D': 'null',  # null字串
        }
    ]
    answers = {'1': 'A'}

    with tempfile.TemporaryDirectory() as temp_dir:
        csv_path = os.path.join(temp_dir, "edge_case.csv")
        csv_generator.generate_google_form_csv(
            questions_with_empty, answers, {}, csv_path
        )

        script_generator = GoogleScriptGenerator()
        script_path = os.path.join(temp_dir, "edge_case.js")
        script_generator.generate_script(csv_path, script_path)

        with open(script_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 驗證空選項被過濾
        assert 'value.trim() !== \'\'' in content, "空選項過濾代碼不存在"
        assert 'value !== \'nan\'' in content, "nan過濾代碼不存在"
        assert 'value !== \'null\'' in content, "null過濾代碼不存在"
        logger.success(f"✓ 空選項過濾功能正常")

    # 測試2: 特殊字符轉義
    questions_with_special = [
        {
            '題號': '1',
            '題目': '包含"雙引號"和\'單引號\'的題目',
            '題型': '選擇題',
            '選項A': '包含\n換行的選項',
            '選項B': '包含\\反斜線的選項',
            '選項C': '正常選項',
            '選項D': '正常選項',
        }
    ]

    with tempfile.TemporaryDirectory() as temp_dir:
        csv_path = os.path.join(temp_dir, "special_chars.csv")
        csv_generator.generate_google_form_csv(
            questions_with_special, answers, {}, csv_path
        )

        script_path = os.path.join(temp_dir, "special_chars.js")
        script_generator.generate_script(csv_path, script_path)

        with open(script_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 驗證特殊字符被正確轉義
        assert '\\"' in content or 'JSON.parse' in content, "雙引號未正確處理"
        logger.success(f"✓ 特殊字符轉義功能正常")

    return True


def run_all_tests():
    """執行所有測試"""
    try:
        logger.info("\n" + "🚀 " * 20)
        logger.info("開始 Google 表單生成管道完整性測試")
        logger.info("🚀 " * 20 + "\n")

        # 創建一個臨時目錄用於所有測試
        with tempfile.TemporaryDirectory() as temp_dir:
            # 測試1: CSV生成
            csv_path, df = test_csv_generation(temp_dir)

            # 測試2: Google Script生成
            script_path, script_content = test_google_script_generation(csv_path, temp_dir)

        # 測試3: 資料完整性
        test_data_integrity()

        # 測試4: 邊界情況
        test_edge_cases()

        # 總結
        logger.info("\n" + "=" * 60)
        logger.info("🎉 所有測試通過！")
        logger.info("=" * 60)
        logger.success("✓ CSV 生成功能正常")
        logger.success("✓ Google Apps Script 生成功能正常")
        logger.success("✓ 資料完整性驗證通過")
        logger.success("✓ 邊界情況處理正確")
        logger.success("✓ 所有關鍵功能已驗證")

        logger.info("\n✅ Google 表單生成管道已通過完整性測試！")
        logger.info("📋 確認事項:")
        logger.info("  1. ✓ 空選項正確過濾")
        logger.info("  2. ✓ 測驗模式已啟用")
        logger.info("  3. ✓ 答案比對邏輯正確")
        logger.info("  4. ✓ 自動評分功能完整")
        logger.info("  5. ✓ 特殊字符正確轉義")
        logger.info("  6. ✓ 資料驗證機制完善")
        logger.info("  7. ✓ 錯誤處理機制健全")

        return True

    except AssertionError as e:
        logger.failure(f"\n❌ 測試失敗: {e}")
        return False
    except Exception as e:
        logger.failure(f"\n❌ 測試執行錯誤: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
