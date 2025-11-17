#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
考古題處理系統 - Web 管理界面啟動腳本

使用方式：
    python run_web.py                    # 開發模式（127.0.0.1:5000）
    python run_web.py --host 0.0.0.0     # 監聽所有網路介面
    python run_web.py --port 8080        # 自訂端口
    python run_web.py --no-debug         # 生產模式（關閉除錯）
"""

import argparse
import os
import sys


def main():
    """主函數"""
    parser = argparse.ArgumentParser(
        description='考古題處理系統 - Web 管理界面',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
範例：
    # 開發模式（預設）
    python run_web.py

    # 允許外部訪問
    python run_web.py --host 0.0.0.0

    # 使用自訂端口
    python run_web.py --port 8080

    # 生產模式
    python run_web.py --no-debug --host 0.0.0.0
        """
    )

    parser.add_argument(
        '--host',
        default='127.0.0.1',
        help='監聽的主機地址（預設：127.0.0.1，使用 0.0.0.0 允許外部訪問）'
    )

    parser.add_argument(
        '--port',
        type=int,
        default=5000,
        help='監聽的端口號（預設：5000）'
    )

    parser.add_argument(
        '--debug',
        action='store_true',
        default=True,
        help='啟用除錯模式（預設：開啟）'
    )

    parser.add_argument(
        '--no-debug',
        action='store_true',
        help='關閉除錯模式（生產環境建議使用）'
    )

    parser.add_argument(
        '--upload-folder',
        default=None,
        help='上傳文件存儲目錄（預設：./uploads）'
    )

    args = parser.parse_args()

    # 處理除錯模式
    debug = args.debug and not args.no_debug

    # 檢查 Flask 是否安裝
    try:
        from src.web.app import run_app
    except ImportError as e:
        print("❌ 錯誤：Flask 未安裝")
        print("\n請先安裝 Web 依賴：")
        print("  pip install -r requirements-web.txt")
        print("\n或使用 setup.py：")
        print("  pip install -e \".[web]\"")
        sys.exit(1)

    # 配置選項
    config = {}
    if args.upload_folder:
        config['UPLOAD_FOLDER'] = os.path.abspath(args.upload_folder)

    # 顯示啟動信息
    print("=" * 60)
    print("🚀 考古題處理系統 - Web 管理界面")
    print("=" * 60)
    print(f"📍 地址：http://{args.host}:{args.port}")
    print(f"🔧 模式：{'開發模式（除錯開啟）' if debug else '生產模式（除錯關閉）'}")
    if args.upload_folder:
        print(f"📁 上傳目錄：{config['UPLOAD_FOLDER']}")
    print("=" * 60)
    print("\n💡 提示：")
    print("  - 按 Ctrl+C 停止服務器")
    if args.host == '127.0.0.1':
        print("  - 目前只允許本機訪問，使用 --host 0.0.0.0 允許外部訪問")
    if debug:
        print("  - 開發模式已啟用，代碼變更會自動重載")
        print("  - 生產環境請使用 --no-debug 參數")
    print("\n🌐 開啟瀏覽器訪問上述地址即可使用")
    print("=" * 60)
    print()

    # 啟動應用
    try:
        run_app(
            host=args.host,
            port=args.port,
            debug=debug,
            config=config
        )
    except KeyboardInterrupt:
        print("\n\n👋 服務器已停止")
    except Exception as e:
        print(f"\n❌ 錯誤：{e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
