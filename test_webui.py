#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Web UI 功能測試腳本
"""

import sys
import os
from pathlib import Path

# 添加項目根目錄到路徑
sys.path.insert(0, str(Path(__file__).parent))


class WebUITester:
    """Web UI 測試器"""

    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.errors = []

    def test_imports(self):
        """測試模塊導入"""
        print("\n【測試 1/7】模塊導入測試")
        print("-" * 70)

        tests = [
            ("Flask", lambda: __import__('flask')),
            ("Werkzeug", lambda: __import__('werkzeug')),
            ("crawler_service", lambda: __import__('src.services.crawler_service')),
            ("ocr_service", lambda: __import__('src.services.ocr_service')),
            ("Flask App", lambda: __import__('src.web.app')),
        ]

        for name, test_func in tests:
            try:
                test_func()
                print(f"  ✅ {name} 導入成功")
                self.passed += 1
            except Exception as e:
                print(f"  ❌ {name} 導入失敗: {e}")
                self.failed += 1
                self.errors.append(f"{name}: {e}")

    def test_flask_app_creation(self):
        """測試 Flask 應用創建"""
        print("\n【測試 2/7】Flask 應用創建")
        print("-" * 70)

        try:
            from src.web.app import create_app
            app = create_app({'TESTING': True})
            print(f"  ✅ Flask 應用創建成功")
            print(f"     版本: {app.config.get('version', '2.0.0')}")
            self.passed += 1
            return app
        except Exception as e:
            print(f"  ❌ Flask 應用創建失敗: {e}")
            self.failed += 1
            self.errors.append(f"Flask App: {e}")
            return None

    def test_routes(self, app):
        """測試路由"""
        print("\n【測試 3/7】路由測試")
        print("-" * 70)

        if not app:
            print("  ⏭️  跳過（應用未創建）")
            return

        expected_routes = [
            ('/', 'index'),
            ('/crawler', 'crawler_page'),
            ('/ocr', 'ocr_page'),
            ('/upload', 'upload_page'),
            ('/monitor', 'monitor_page'),
            ('/api/crawler/config', 'get_crawler_config'),
            ('/api/ocr/config', 'get_ocr_config'),
            ('/health', 'health_check'),
        ]

        with app.app_context():
            for path, endpoint in expected_routes:
                try:
                    # 獲取所有規則
                    found = False
                    for rule in app.url_map.iter_rules():
                        if rule.endpoint == endpoint:
                            found = True
                            break

                    if found:
                        print(f"  ✅ 路由 {path} ({endpoint}) 存在")
                        self.passed += 1
                    else:
                        print(f"  ❌ 路由 {path} ({endpoint}) 不存在")
                        self.failed += 1
                except Exception as e:
                    print(f"  ❌ 路由 {path} 測試失敗: {e}")
                    self.failed += 1

    def test_crawler_service(self):
        """測試爬蟲服務"""
        print("\n【測試 4/7】爬蟲服務測試")
        print("-" * 70)

        try:
            from src.services import crawler_service

            # 測試獲取可用年份
            years = crawler_service.get_available_years()
            print(f"  ✅ 可用年份獲取成功: {len(years)} 個年份")
            print(f"     範圍: 民國 {years[0]} - {years[-1]} 年")
            self.passed += 1

            # 測試獲取默認關鍵字
            keywords = crawler_service.get_default_keywords()
            print(f"  ✅ 默認關鍵字獲取成功: {len(keywords)} 個")
            print(f"     關鍵字: {', '.join(keywords[:3])}...")
            self.passed += 1

            # 測試創建任務（不實際執行）
            task_id = crawler_service.create_task([113], keywords, "/tmp/test")
            print(f"  ✅ 任務創建成功: {task_id[:8]}...")
            self.passed += 1

            # 測試獲取任務
            task = crawler_service.get_task(task_id)
            if task and task['status'] == 'pending':
                print(f"  ✅ 任務獲取成功，狀態: {task['status']}")
                self.passed += 1
            else:
                print(f"  ❌ 任務狀態異常")
                self.failed += 1

            # 清理任務
            crawler_service.delete_task(task_id)

        except Exception as e:
            print(f"  ❌ 爬蟲服務測試失敗: {e}")
            self.failed += 1
            self.errors.append(f"Crawler Service: {e}")

    def test_ocr_service(self):
        """測試 OCR 服務"""
        print("\n【測試 5/7】OCR 服務測試")
        print("-" * 70)

        try:
            from src.services import ocr_service

            # 測試獲取配置
            config = ocr_service.get_config()
            print(f"  ✅ OCR 配置獲取成功")
            print(f"     啟用增強: {config.get('enabled')}")
            print(f"     自動檢測: {config.get('auto_detect')}")
            print(f"     智能調優: {config.get('auto_tune')}")
            print(f"     DPI 範圍: {config['dpi_range']['min']}-{config['dpi_range']['max']}")
            self.passed += 1

        except Exception as e:
            print(f"  ❌ OCR 服務測試失敗: {e}")
            self.failed += 1
            self.errors.append(f"OCR Service: {e}")

    def test_templates(self):
        """測試模板文件"""
        print("\n【測試 6/7】模板文件測試")
        print("-" * 70)

        templates = [
            'base.html',
            'index.html',
            'crawler.html',
            'ocr.html',
            'upload.html',
            'monitor.html',
        ]

        templates_dir = Path(__file__).parent / 'src' / 'web' / 'templates'

        for template in templates:
            template_path = templates_dir / template
            if template_path.exists():
                print(f"  ✅ 模板 {template} 存在")
                self.passed += 1
            else:
                print(f"  ❌ 模板 {template} 不存在")
                self.failed += 1

    def test_configuration(self):
        """測試配置文件"""
        print("\n【測試 7/7】配置文件測試")
        print("-" * 70)

        config_file = Path(__file__).parent / 'config.yaml'

        if config_file.exists():
            print(f"  ✅ 配置文件存在: {config_file}")
            self.passed += 1

            try:
                import yaml
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = yaml.safe_load(f)

                # 檢查關鍵配置項
                checks = [
                    ('downloader', '爬蟲配置'),
                    ('ocr', 'OCR 配置'),
                    ('processing', 'PDF 處理配置'),
                ]

                for key, name in checks:
                    if key in config:
                        print(f"  ✅ {name} 存在")
                        self.passed += 1
                    else:
                        print(f"  ❌ {name} 缺失")
                        self.failed += 1

            except Exception as e:
                print(f"  ❌ 配置文件解析失敗: {e}")
                self.failed += 1

        else:
            print(f"  ❌ 配置文件不存在")
            self.failed += 1

    def run_all_tests(self):
        """運行所有測試"""
        print("\n" + "="*70)
        print(" " * 20 + "Web UI 功能測試")
        print("="*70)

        self.test_imports()
        app = self.test_flask_app_creation()
        self.test_routes(app)
        self.test_crawler_service()
        self.test_ocr_service()
        self.test_templates()
        self.test_configuration()

        # 顯示結果
        print("\n" + "="*70)
        print("測試結果")
        print("="*70)
        print(f"✅ 通過: {self.passed} 個")
        print(f"❌ 失敗: {self.failed} 個")

        if self.errors:
            print("\n錯誤詳情:")
            for error in self.errors:
                print(f"  ❌ {error}")

        total = self.passed + self.failed
        if total > 0:
            success_rate = (self.passed / total) * 100
            print(f"\n成功率: {success_rate:.1f}%")

            if success_rate >= 95:
                print("🎉 優秀！所有核心功能正常")
                return 0
            elif success_rate >= 80:
                print("👍 良好！大部分功能正常")
                return 0
            else:
                print("⚠️  警告：部分功能異常，請檢查錯誤")
                return 1
        else:
            print("❌ 沒有運行任何測試")
            return 1


def main():
    """主函數"""
    tester = WebUITester()
    return tester.run_all_tests()


if __name__ == '__main__':
    sys.exit(main())
