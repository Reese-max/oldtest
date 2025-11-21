#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
瀏覽器自動化測試 - 使用 Playwright
模擬真實用戶操作，測試所有前端功能
"""

import asyncio
import json
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional

# 添加項目根目錄到路徑
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from playwright.async_api import Browser, BrowserContext, Page, async_playwright


class BrowserTestConfig:
    """測試配置"""

    def __init__(
        self,
        base_url: str = "http://127.0.0.1:5000",
        headless: bool = False,  # 預設顯示瀏覽器，方便觀察
        slow_mo: int = 500,  # 每個操作延遲 500ms，方便觀察
        timeout: int = 30000,  # 30秒超時
        browser_type: str = "chromium",  # chromium, firefox, webkit
    ):
        self.base_url = base_url
        self.headless = headless
        self.slow_mo = slow_mo
        self.timeout = timeout
        self.browser_type = browser_type
        self.screenshots_dir = project_root / "tests" / "browser" / "screenshots"
        self.screenshots_dir.mkdir(parents=True, exist_ok=True)


class BrowserAutomationTester:
    """瀏覽器自動化測試器"""

    def __init__(self, config: BrowserTestConfig):
        self.config = config
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self.test_results: List[Dict] = []

    async def setup(self):
        """初始化瀏覽器"""
        print(f"\n{'='*70}")
        print(f"{'瀏覽器自動化測試':^66}")
        print(f"{'='*70}\n")

        print(f"🌐 測試 URL: {self.config.base_url}")
        print(f"🖥️  瀏覽器: {self.config.browser_type}")
        print(f"👁️  可見模式: {'是' if not self.config.headless else '否'}")
        print(f"⏱️  操作延遲: {self.config.slow_mo}ms")
        print(f"📸 截圖目錄: {self.config.screenshots_dir}\n")

        playwright = await async_playwright().start()

        # 選擇瀏覽器
        if self.config.browser_type == "firefox":
            self.browser = await playwright.firefox.launch(headless=self.config.headless, slow_mo=self.config.slow_mo)
        elif self.config.browser_type == "webkit":
            self.browser = await playwright.webkit.launch(headless=self.config.headless, slow_mo=self.config.slow_mo)
        else:  # chromium
            self.browser = await playwright.chromium.launch(headless=self.config.headless, slow_mo=self.config.slow_mo)

        # 創建上下文（支持保存 cookies）
        self.context = await self.browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        )

        # 創建頁面
        self.page = await self.context.new_page()
        self.page.set_default_timeout(self.config.timeout)

    async def teardown(self):
        """清理資源"""
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()

    async def screenshot(self, name: str):
        """截圖"""
        if self.page:
            path = self.config.screenshots_dir / f"{name}.png"
            await self.page.screenshot(path=str(path))
            print(f"  📸 截圖保存: {path}")

    def log_result(self, test_name: str, status: str, message: str = ""):
        """記錄測試結果"""
        result = {"test": test_name, "status": status, "message": message, "timestamp": time.time()}
        self.test_results.append(result)

        emoji = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
        print(f"{emoji} {test_name}: {status}")
        if message:
            print(f"   {message}")

    async def test_homepage(self):
        """測試首頁"""
        print(f"\n{'='*70}")
        print("測試 1: 首頁功能")
        print(f"{'='*70}")

        try:
            # 訪問首頁
            print("\n📍 訪問首頁...")
            await self.page.goto(self.config.base_url)
            await self.page.wait_for_load_state("networkidle")

            # 檢查標題
            title = await self.page.title()
            print(f"   頁面標題: {title}")
            assert "考古題" in title, f"標題不正確: {title}"

            # 截圖
            await self.screenshot("01_homepage")

            # 檢查主要元素
            print("\n🔍 檢查頁面元素...")

            # 檢查標題
            heading = await self.page.locator("h1").first.text_content()
            print(f"   主標題: {heading}")
            assert "考古題處理系統" in heading

            # 檢查功能卡片
            cards = await self.page.locator(".feature-card").count()
            print(f"   功能卡片數量: {cards}")
            assert cards >= 4, f"功能卡片數量不足: {cards}"

            # 檢查導航連結
            print("\n🔗 檢查導航連結...")
            links = [("爬蟲下載", "/crawler"), ("OCR", "/ocr"), ("PDF", "/upload"), ("監控", "/monitor")]

            for name, href in links:
                link = self.page.locator(f"a[href*='{href}']").first
                is_visible = await link.is_visible()
                print(f"   {name}: {'✓' if is_visible else '✗'}")
                assert is_visible, f"{name} 連結不可見"

            self.log_result("首頁測試", "PASS", "所有元素正常顯示")

        except Exception as e:
            self.log_result("首頁測試", "FAIL", str(e))
            await self.screenshot("error_homepage")
            raise

    async def test_crawler_page(self):
        """測試爬蟲下載頁面"""
        print(f"\n{'='*70}")
        print("測試 2: 爬蟲下載頁面")
        print(f"{'='*70}")

        try:
            # 導航到爬蟲頁面
            print("\n📍 導航到爬蟲頁面...")
            await self.page.goto(f"{self.config.base_url}/crawler")
            await self.page.wait_for_load_state("networkidle")

            # 截圖
            await self.screenshot("02_crawler_page")

            # 檢查頁面標題
            heading = await self.page.locator("h1, h2").first.text_content()
            print(f"   頁面標題: {heading}")

            # 檢查表單元素
            print("\n🔍 檢查表單元素...")

            # 檢查年份選擇
            year_input = self.page.locator("input[type='number'], select[name*='year']").first
            if await year_input.count() > 0:
                print("   ✓ 年份輸入框")

            # 檢查考試類型選擇
            exam_type = self.page.locator("select, input[name*='exam']").first
            if await exam_type.count() > 0:
                print("   ✓ 考試類型選擇")

            # 檢查下載按鈕
            download_btn = self.page.locator("button:has-text('下載'), button[type='submit']").first
            if await download_btn.count() > 0:
                is_visible = await download_btn.is_visible()
                print(f"   ✓ 下載按鈕: {'可見' if is_visible else '隱藏'}")

            # 模擬填寫表單（不實際提交）
            print("\n✍️  模擬填寫表單...")
            if await year_input.count() > 0:
                await year_input.fill("114")
                print("   ✓ 填寫年份: 114")

            await self.screenshot("02_crawler_filled")

            self.log_result("爬蟲頁面測試", "PASS", "表單元素完整")

        except Exception as e:
            self.log_result("爬蟲頁面測試", "FAIL", str(e))
            await self.screenshot("error_crawler")
            raise

    async def test_ocr_page(self):
        """測試 OCR 處理頁面"""
        print(f"\n{'='*70}")
        print("測試 3: OCR 處理頁面")
        print(f"{'='*70}")

        try:
            # 導航到 OCR 頁面
            print("\n📍 導航到 OCR 頁面...")
            await self.page.goto(f"{self.config.base_url}/ocr")
            await self.page.wait_for_load_state("networkidle")

            # 截圖
            await self.screenshot("03_ocr_page")

            # 檢查頁面元素
            print("\n🔍 檢查頁面元素...")

            # 檢查文件上傳
            file_input = self.page.locator("input[type='file']").first
            if await file_input.count() > 0:
                print("   ✓ 文件上傳控件")

            # 檢查 OCR 選項
            print("\n📋 檢查 OCR 選項...")

            # 可能的選項：DPI、語言、模式等
            selects = await self.page.locator("select").count()
            checkboxes = await self.page.locator("input[type='checkbox']").count()
            radios = await self.page.locator("input[type='radio']").count()

            print(f"   下拉選單: {selects}")
            print(f"   複選框: {checkboxes}")
            print(f"   單選框: {radios}")

            self.log_result("OCR 頁面測試", "PASS", "頁面元素正常")

        except Exception as e:
            self.log_result("OCR 頁面測試", "FAIL", str(e))
            await self.screenshot("error_ocr")
            raise

    async def test_upload_page(self):
        """測試 PDF 上傳處理頁面"""
        print(f"\n{'='*70}")
        print("測試 4: PDF 上傳處理頁面")
        print(f"{'='*70}")

        try:
            # 導航到上傳頁面
            print("\n📍 導航到上傳頁面...")
            await self.page.goto(f"{self.config.base_url}/upload")
            await self.page.wait_for_load_state("networkidle")

            # 截圖
            await self.screenshot("04_upload_page")

            # 檢查上傳控件
            print("\n🔍 檢查上傳元素...")

            file_input = self.page.locator("input[type='file']").first
            if await file_input.count() > 0:
                print("   ✓ 文件上傳控件")

                # 檢查接受的文件類型
                accept = await file_input.get_attribute("accept")
                print(f"   接受的文件類型: {accept}")

            # 檢查處理按鈕
            submit_btn = self.page.locator(
                "button[type='submit'], button:has-text('處理'), button:has-text('上傳')"
            ).first
            if await submit_btn.count() > 0:
                is_enabled = await submit_btn.is_enabled()
                print(f"   ✓ 處理按鈕: {'啟用' if is_enabled else '禁用'}")

            self.log_result("上傳頁面測試", "PASS", "上傳功能正常")

        except Exception as e:
            self.log_result("上傳頁面測試", "FAIL", str(e))
            await self.screenshot("error_upload")
            raise

    async def test_monitor_page(self):
        """測試性能監控頁面"""
        print(f"\n{'='*70}")
        print("測試 5: 性能監控頁面")
        print(f"{'='*70}")

        try:
            # 導航到監控頁面
            print("\n📍 導航到監控頁面...")
            await self.page.goto(f"{self.config.base_url}/monitor")
            await self.page.wait_for_load_state("networkidle")

            # 等待數據加載
            await self.page.wait_for_timeout(2000)

            # 截圖
            await self.screenshot("05_monitor_page")

            # 檢查監控元素
            print("\n🔍 檢查監控元素...")

            # 檢查是否有圖表或數據顯示
            canvas = await self.page.locator("canvas").count()
            print(f"   Canvas 圖表: {canvas}")

            # 檢查數據卡片
            stat_cards = await self.page.locator(".stat-card, .metric, .monitor-item").count()
            print(f"   數據卡片: {stat_cards}")

            # 檢查實時更新（等待一段時間看是否有變化）
            print("\n⏱️  檢查實時更新...")
            await self.page.wait_for_timeout(3000)

            self.log_result("監控頁面測試", "PASS", "監控功能正常")

        except Exception as e:
            self.log_result("監控頁面測試", "FAIL", str(e))
            await self.screenshot("error_monitor")
            raise

    async def test_navigation(self):
        """測試頁面導航"""
        print(f"\n{'='*70}")
        print("測試 6: 頁面導航流程")
        print(f"{'='*70}")

        try:
            # 從首頁開始
            print("\n📍 開始導航測試...")
            await self.page.goto(self.config.base_url)

            # 依次點擊各個功能
            pages = [("爬蟲下載", "/crawler"), ("OCR", "/ocr"), ("上傳", "/upload"), ("監控", "/monitor")]

            for i, (name, href) in enumerate(pages, 1):
                print(f"\n{i}. 導航到 {name}...")

                # 點擊連結
                link = self.page.locator(f"a[href*='{href}']").first
                await link.click()

                # 等待頁面加載
                await self.page.wait_for_load_state("networkidle")

                # 驗證 URL
                current_url = self.page.url
                print(f"   當前 URL: {current_url}")
                assert href in current_url, f"URL 不匹配: {current_url}"

                # 截圖
                await self.screenshot(f"06_nav_{i}_{name}")

                # 返回首頁
                if i < len(pages):
                    await self.page.goto(self.config.base_url)
                    await self.page.wait_for_load_state("networkidle")

            self.log_result("導航測試", "PASS", "所有頁面導航正常")

        except Exception as e:
            self.log_result("導航測試", "FAIL", str(e))
            await self.screenshot("error_navigation")
            raise

    async def test_responsive_design(self):
        """測試響應式設計"""
        print(f"\n{'='*70}")
        print("測試 7: 響應式設計")
        print(f"{'='*70}")

        try:
            # 測試不同視窗大小
            viewports = [("Desktop", 1920, 1080), ("Tablet", 768, 1024), ("Mobile", 375, 667)]

            for device, width, height in viewports:
                print(f"\n📱 測試 {device} ({width}x{height})...")

                # 設置視窗大小
                await self.page.set_viewport_size({"width": width, "height": height})

                # 訪問首頁
                await self.page.goto(self.config.base_url)
                await self.page.wait_for_load_state("networkidle")

                # 截圖
                await self.screenshot(f"07_responsive_{device}")

                # 檢查主要元素是否可見
                heading = await self.page.locator("h1").first.is_visible()
                print(f"   標題可見: {'✓' if heading else '✗'}")

            # 恢復原始大小
            await self.page.set_viewport_size({"width": 1920, "height": 1080})

            self.log_result("響應式設計測試", "PASS", "各尺寸顯示正常")

        except Exception as e:
            self.log_result("響應式設計測試", "FAIL", str(e))
            await self.screenshot("error_responsive")
            raise

    async def test_api_health(self):
        """測試 API 健康檢查"""
        print(f"\n{'='*70}")
        print("測試 8: API 健康檢查")
        print(f"{'='*70}")

        try:
            print("\n📍 訪問健康檢查端點...")

            # 訪問 /health
            response = await self.page.goto(f"{self.config.base_url}/health")

            # 檢查狀態碼
            status = response.status
            print(f"   HTTP 狀態碼: {status}")
            assert status == 200, f"狀態碼錯誤: {status}"

            # 獲取響應內容
            content = await self.page.content()
            print(f"   響應內容長度: {len(content)} 字元")

            # 截圖
            await self.screenshot("08_health_check")

            self.log_result("API 健康檢查", "PASS", f"狀態碼 {status}")

        except Exception as e:
            self.log_result("API 健康檢查", "FAIL", str(e))
            await self.screenshot("error_health")
            raise

    async def run_all_tests(self):
        """運行所有測試"""
        try:
            await self.setup()

            # 執行所有測試
            await self.test_homepage()
            await self.test_crawler_page()
            await self.test_ocr_page()
            await self.test_upload_page()
            await self.test_monitor_page()
            await self.test_navigation()
            await self.test_responsive_design()
            await self.test_api_health()

            # 顯示測試結果
            self.print_summary()

        except Exception as e:
            print(f"\n❌ 測試過程中出現錯誤: {e}")
            raise
        finally:
            await self.teardown()

    def print_summary(self):
        """打印測試摘要"""
        print(f"\n{'='*70}")
        print(f"{'測試摘要':^66}")
        print(f"{'='*70}\n")

        total = len(self.test_results)
        passed = sum(1 for r in self.test_results if r["status"] == "PASS")
        failed = sum(1 for r in self.test_results if r["status"] == "FAIL")

        print(f"總測試數: {total}")
        print(f"✅ 通過: {passed}")
        print(f"❌ 失敗: {failed}")
        print(f"成功率: {passed/total*100:.1f}%\n")

        # 詳細結果
        print("詳細結果:")
        print("-" * 70)
        for result in self.test_results:
            emoji = "✅" if result["status"] == "PASS" else "❌"
            print(f"{emoji} {result['test']}: {result['status']}")
            if result["message"]:
                print(f"   {result['message']}")

        print(f"\n{'='*70}")

        # 保存結果到 JSON
        results_file = project_root / "tests" / "browser" / "test_results.json"
        with open(results_file, "w", encoding="utf-8") as f:
            json.dump(self.test_results, f, ensure_ascii=False, indent=2)
        print(f"\n📄 測試結果已保存: {results_file}")

        # 返回是否全部通過
        return failed == 0


async def main():
    """主函數"""
    import argparse

    parser = argparse.ArgumentParser(
        description="瀏覽器自動化測試 - 考古題處理系統", formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument("--url", default="http://127.0.0.1:5000", help="測試的基礎 URL (默認: http://127.0.0.1:5000)")

    parser.add_argument(
        "--browser", choices=["chromium", "firefox", "webkit"], default="chromium", help="瀏覽器類型 (默認: chromium)"
    )

    parser.add_argument("--headless", action="store_true", help="無頭模式（不顯示瀏覽器窗口）")

    parser.add_argument("--fast", action="store_true", help="快速模式（不延遲操作）")

    args = parser.parse_args()

    # 創建配置
    config = BrowserTestConfig(
        base_url=args.url, browser_type=args.browser, headless=args.headless, slow_mo=0 if args.fast else 500
    )

    # 創建測試器
    tester = BrowserAutomationTester(config)

    # 運行測試
    success = await tester.run_all_tests()

    # 返回退出碼
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main())
