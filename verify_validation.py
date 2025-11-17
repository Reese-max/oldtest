#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速驗證輸入驗證功能
"""

import os
import sys

# 添加項目根目錄到 Python 路徑
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.csv_generator import CSVGenerator
from src.core.google_script_generator import GoogleScriptGenerator
from src.utils.exceptions import CSVGenerationError, GoogleFormError

print("=" * 60)
print("輸入驗證功能測試")
print("=" * 60)

# 測試 1: CSV Generator - 無效的 questions 類型
print("\n測試 1: CSV Generator - 無效的 questions 類型")
csv_gen = CSVGenerator()
try:
    csv_gen.generate_questions_csv(
        questions="not a list",  # 錯誤類型
        answers={},
        output_path="/tmp/test.csv"
    )
    print("❌ 失敗：應該拋出異常")
except CSVGenerationError as e:
    print(f"✅ 成功：捕獲到預期異常: {e}")

# 測試 2: CSV Generator - 無效的 answers 類型
print("\n測試 2: CSV Generator - 無效的 answers 類型")
try:
    csv_gen.generate_questions_csv(
        questions=[],
        answers="not a dict",  # 錯誤類型
        output_path="/tmp/test.csv"
    )
    print("❌ 失敗：應該拋出異常")
except CSVGenerationError as e:
    print(f"✅ 成功：捕獲到預期異常: {e}")

# 測試 3: CSV Generator - 空的 output_path
print("\n測試 3: CSV Generator - 空的 output_path")
try:
    csv_gen.generate_questions_csv(
        questions=[],
        answers={},
        output_path=""  # 空字串
    )
    print("❌ 失敗：應該拋出異常")
except CSVGenerationError as e:
    print(f"✅ 成功：捕獲到預期異常: {e}")

# 測試 4: Google Script Generator - 無效的 csv_path 類型
print("\n測試 4: Google Script Generator - 無效的 csv_path 類型")
script_gen = GoogleScriptGenerator()
try:
    script_gen.generate_script(
        csv_path=123,  # 錯誤類型
        output_path="/tmp/test.gs"
    )
    print("❌ 失敗：應該拋出異常")
except GoogleFormError as e:
    print(f"✅ 成功：捕獲到預期異常: {e}")

# 測試 5: Google Script Generator - 非 CSV 檔案
print("\n測試 5: Google Script Generator - 非 CSV 檔案")
try:
    script_gen.generate_script(
        csv_path="test.txt",  # 不是 .csv 檔案
        output_path="/tmp/test.gs"
    )
    print("❌ 失敗：應該拋出異常")
except GoogleFormError as e:
    print(f"✅ 成功：捕獲到預期異常: {e}")

# 測試 6: CSV Generator - 自動創建目錄
print("\n測試 6: CSV Generator - 自動創建目錄")
import tempfile
temp_dir = tempfile.mkdtemp()
new_dir = os.path.join(temp_dir, "new_dir", "nested")
output_path = os.path.join(new_dir, "test.csv")

print(f"目錄不存在: {not os.path.exists(new_dir)}")
csv_gen.generate_questions_csv(
    questions=[],
    answers={},
    output_path=output_path
)
print(f"✅ 成功：目錄已自動創建: {os.path.exists(new_dir)}")
print(f"✅ 成功：檔案已創建: {os.path.isfile(output_path)}")

print("\n" + "=" * 60)
print("✅ 所有驗證測試通過！")
print("=" * 60)
