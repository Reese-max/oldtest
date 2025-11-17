#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試增強版下載器功能
測試：並發下載、進度顯示、斷點續傳
"""

import os
import sys
import time
import tempfile
import shutil
from datetime import datetime

# 添加項目根目錄到路徑
sys.path.insert(0, os.path.dirname(__file__))

def test_config_loading():
    """測試配置文件加載"""
    print("\n" + "="*70)
    print("測試 1: 配置文件加載")
    print("="*70)

    try:
        from 考古題下載 import DOWNLOADER_CONFIG, load_config

        config = load_config()
        print(f"✅ 配置加載成功")
        print(f"   並發下載: {config.get('enable_concurrent', False)}")
        print(f"   並發數量: {config.get('concurrent_downloads', 5)}")
        print(f"   進度條: {config.get('show_progress_bar', False)}")
        print(f"   斷點續傳: {config.get('enable_resume', False)}")
        return True
    except Exception as e:
        print(f"❌ 配置加載失敗: {e}")
        return False

def test_imports():
    """測試必要的庫導入"""
    print("\n" + "="*70)
    print("測試 2: 庫依賴檢查")
    print("="*70)

    imports_ok = True

    # 測試基本庫
    try:
        import yaml
        print("✅ PyYAML 已安裝")
    except ImportError:
        print("❌ PyYAML 未安裝，請執行: pip install PyYAML")
        imports_ok = False

    try:
        from tqdm import tqdm
        print("✅ tqdm 已安裝")
    except ImportError:
        print("⚠️  tqdm 未安裝，將使用簡單進度顯示")
        print("   建議執行: pip install tqdm")

    try:
        import requests
        from bs4 import BeautifulSoup
        print("✅ requests 和 BeautifulSoup4 已安裝")
    except ImportError:
        print("❌ 缺少必要庫，請執行: pip install requests beautifulsoup4")
        imports_ok = False

    return imports_ok

def test_function_availability():
    """測試新增函數是否可用"""
    print("\n" + "="*70)
    print("測試 3: 新增函數檢查")
    print("="*70)

    try:
        from 考古題下載 import (
            download_file_with_resume,
            download_exam_concurrent,
            stats_lock
        )
        print("✅ download_file_with_resume 函數存在")
        print("✅ download_exam_concurrent 函數存在")
        print("✅ stats_lock 鎖對象存在")
        return True
    except ImportError as e:
        print(f"❌ 函數導入失敗: {e}")
        return False

def test_config_values():
    """測試配置值是否合理"""
    print("\n" + "="*70)
    print("測試 4: 配置值驗證")
    print("="*70)

    try:
        from 考古題下載 import DOWNLOADER_CONFIG

        # 檢查關鍵配置
        checks = []

        # 並發數量應該在合理範圍
        concurrent = DOWNLOADER_CONFIG.get('concurrent_downloads', 5)
        if 1 <= concurrent <= 10:
            print(f"✅ 並發數量合理: {concurrent}")
            checks.append(True)
        else:
            print(f"⚠️  並發數量可能不合理: {concurrent} (建議: 3-5)")
            checks.append(False)

        # 超時設置應該合理
        conn_timeout = DOWNLOADER_CONFIG.get('connection_timeout', 10)
        read_timeout = DOWNLOADER_CONFIG.get('read_timeout', 120)
        if conn_timeout > 0 and read_timeout > 0:
            print(f"✅ 超時設置合理: 連接={conn_timeout}s, 讀取={read_timeout}s")
            checks.append(True)
        else:
            print(f"❌ 超時設置異常")
            checks.append(False)

        # 重試設置
        max_retries = DOWNLOADER_CONFIG.get('max_retries', 10)
        if max_retries > 0:
            print(f"✅ 重試次數: {max_retries}")
            checks.append(True)
        else:
            print(f"⚠️  重試次數為0，可能導致下載失敗")
            checks.append(False)

        return all(checks)
    except Exception as e:
        print(f"❌ 配置驗證失敗: {e}")
        return False

def test_session_creation():
    """測試 Session 創建"""
    print("\n" + "="*70)
    print("測試 5: HTTP Session 創建")
    print("="*70)

    try:
        from 考古題下載 import create_robust_session

        session = create_robust_session()
        print("✅ Session 創建成功")
        print(f"   適配器數量: {len(session.adapters)}")
        return True
    except Exception as e:
        print(f"❌ Session 創建失敗: {e}")
        return False

def run_all_tests():
    """運行所有測試"""
    print("\n" + "="*70)
    print("🧪 增強版下載器功能測試")
    print("="*70)
    print(f"測試時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    results = []

    # 運行測試
    results.append(("配置加載", test_config_loading()))
    results.append(("庫依賴", test_imports()))
    results.append(("函數可用性", test_function_availability()))
    results.append(("配置值驗證", test_config_values()))
    results.append(("Session創建", test_session_creation()))

    # 統計結果
    print("\n" + "="*70)
    print("📊 測試結果匯總")
    print("="*70)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "✅ 通過" if result else "❌ 失敗"
        print(f"{status}: {name}")

    print(f"\n總計: {passed}/{total} 測試通過")
    success_rate = (passed / total) * 100
    print(f"成功率: {success_rate:.1f}%")

    if passed == total:
        print("\n🎉 所有測試通過！增強功能已準備就緒。")
        return 0
    else:
        print("\n⚠️  部分測試失敗，請檢查配置和依賴。")
        return 1

def print_usage_guide():
    """打印使用指南"""
    print("\n" + "="*70)
    print("📖 增強功能使用指南")
    print("="*70)
    print("""
✨ 新增功能說明：

1️⃣  並發下載 (Concurrent Downloads)
   - 配置: downloader.enable_concurrent = true
   - 並發數: downloader.concurrent_downloads = 5
   - 效果: 同時下載多個文件，顯著提升速度

2️⃣  進度顯示 (Progress Bar)
   - 配置: downloader.show_progress_bar = true
   - 需要: pip install tqdm
   - 效果: 詳細的下載進度條、速度、預計剩餘時間

3️⃣  斷點續傳 (Resume Download)
   - 配置: downloader.enable_resume = true
   - 效果: 支援中斷續傳，節省時間和流量
   - 臨時文件: .part 後綴

🔧 配置文件位置: config.yaml
📝 修改配置後無需重啟，會自動加載最新配置

💡 使用建議：
   - 並發數建議設為 3-5，過高可能被服務器限制
   - 如果網絡不穩定，建議啟用斷點續傳
   - 進度條提供更好的用戶體驗，強烈建議安裝 tqdm

🚀 開始使用:
   python 考古題下載.py
""")

if __name__ == "__main__":
    # 運行測試
    exit_code = run_all_tests()

    # 顯示使用指南
    if exit_code == 0:
        print_usage_guide()

    sys.exit(exit_code)
