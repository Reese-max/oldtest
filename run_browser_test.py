#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
瀏覽器自動化測試 - 快速啟動腳本
一鍵啟動 Web 服務器並運行瀏覽器測試
"""

import os
import sys
import time
import asyncio
import subprocess
import signal
from pathlib import Path

# 添加項目根目錄到路徑
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


class BrowserTestRunner:
    """瀏覽器測試運行器"""

    def __init__(self):
        self.server_process = None
        self.test_process = None

    def start_web_server(self, host="127.0.0.1", port=5000):
        """啟動 Web 服務器"""
        print("🚀 正在啟動 Web 服務器...")
        print(f"   地址: http://{host}:{port}")

        # 啟動服務器（在後台運行）
        env = os.environ.copy()
        env["FLASK_ENV"] = "development"

        self.server_process = subprocess.Popen(
            [
                sys.executable,
                "run_webui.py",
                "--host", host,
                "--port", str(port),
                "--no-debug"  # 不顯示調試信息
            ],
            cwd=str(project_root),
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        # 等待服務器啟動
        print("   等待服務器啟動...")
        time.sleep(5)

        # 檢查服務器是否正常運行
        if self.server_process.poll() is not None:
            print("❌ 服務器啟動失敗!")
            stdout, stderr = self.server_process.communicate()
            print(f"標準輸出: {stdout.decode()}")
            print(f"錯誤輸出: {stderr.decode()}")
            return False

        print("✅ Web 服務器啟動成功!\n")
        return True

    def stop_web_server(self):
        """停止 Web 服務器"""
        if self.server_process:
            print("\n🛑 正在停止 Web 服務器...")
            self.server_process.terminate()
            try:
                self.server_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.server_process.kill()
            print("✅ Web 服務器已停止")

    async def run_browser_tests(
        self,
        url="http://127.0.0.1:5000",
        browser="chromium",
        headless=False,
        fast=False
    ):
        """運行瀏覽器測試"""
        print("🧪 開始運行瀏覽器測試...\n")

        # 導入測試模組
        from tests.browser.test_browser_automation import (
            BrowserTestConfig,
            BrowserAutomationTester
        )

        # 創建配置
        config = BrowserTestConfig(
            base_url=url,
            browser_type=browser,
            headless=headless,
            slow_mo=0 if fast else 500
        )

        # 創建測試器
        tester = BrowserAutomationTester(config)

        # 運行測試
        success = await tester.run_all_tests()

        return success

    def cleanup(self):
        """清理資源"""
        self.stop_web_server()

    def signal_handler(self, signum, frame):
        """信號處理器"""
        print("\n\n⚠️  收到中斷信號，正在清理...")
        self.cleanup()
        sys.exit(0)


async def main():
    """主函數"""
    import argparse

    parser = argparse.ArgumentParser(
        description="瀏覽器自動化測試 - 一鍵運行",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  # 默認模式（顯示瀏覽器，慢速操作）
  python run_browser_test.py

  # 無頭模式（不顯示瀏覽器）
  python run_browser_test.py --headless

  # 快速模式（不延遲操作）
  python run_browser_test.py --fast

  # 使用 Firefox
  python run_browser_test.py --browser firefox

  # 自定義端口
  python run_browser_test.py --port 8080

  # 僅啟動服務器（不運行測試）
  python run_browser_test.py --server-only
        """
    )

    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="Web 服務器主機 (默認: 127.0.0.1)"
    )

    parser.add_argument(
        "--port",
        type=int,
        default=5000,
        help="Web 服務器端口 (默認: 5000)"
    )

    parser.add_argument(
        "--browser",
        choices=["chromium", "firefox", "webkit"],
        default="chromium",
        help="瀏覽器類型 (默認: chromium)"
    )

    parser.add_argument(
        "--headless",
        action="store_true",
        help="無頭模式（不顯示瀏覽器窗口）"
    )

    parser.add_argument(
        "--fast",
        action="store_true",
        help="快速模式（不延遲操作）"
    )

    parser.add_argument(
        "--server-only",
        action="store_true",
        help="僅啟動服務器（不運行測試）"
    )

    parser.add_argument(
        "--test-only",
        action="store_true",
        help="僅運行測試（假設服務器已啟動）"
    )

    args = parser.parse_args()

    # 創建運行器
    runner = BrowserTestRunner()

    # 註冊信號處理器
    signal.signal(signal.SIGINT, runner.signal_handler)
    signal.signal(signal.SIGTERM, runner.signal_handler)

    try:
        # 啟動服務器（如果需要）
        if not args.test_only:
            if not runner.start_web_server(args.host, args.port):
                print("❌ 無法啟動 Web 服務器")
                return 1

        # 僅啟動服務器模式
        if args.server_only:
            print("\n✅ 服務器已啟動，按 Ctrl+C 停止")
            try:
                # 保持運行
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                pass
            finally:
                runner.cleanup()
            return 0

        # 運行測試
        url = f"http://{args.host}:{args.port}"
        success = await runner.run_browser_tests(
            url=url,
            browser=args.browser,
            headless=args.headless,
            fast=args.fast
        )

        # 清理
        if not args.test_only:
            runner.cleanup()

        # 返回結果
        return 0 if success else 1

    except Exception as e:
        print(f"\n❌ 運行失敗: {e}")
        import traceback
        traceback.print_exc()
        runner.cleanup()
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
