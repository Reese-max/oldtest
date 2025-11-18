#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
考古題處理系統 - Web UI 啟動腳本
"""

import os
import sys
import argparse
from pathlib import Path

# 添加項目根目錄到 Python 路徑
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.web.app import create_app


def main():
    """主函數"""
    parser = argparse.ArgumentParser(
        description='考古題處理系統 Web UI',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
示例用法:
  # 使用默認設置啟動 (127.0.0.1:5000)
  python run_webui.py

  # 指定主機和端口
  python run_webui.py --host 0.0.0.0 --port 8080

  # 生產模式（關閉調試）
  python run_webui.py --no-debug

  # 自定義上傳和輸出目錄
  python run_webui.py --upload-dir /tmp/uploads --output-dir /tmp/outputs

功能說明:
  🕷️  爬蟲下載: http://localhost:5000/crawler
  🔍 OCR處理: http://localhost:5000/ocr
  📄 PDF處理: http://localhost:5000/upload
  ⏱️  性能監控: http://localhost:5000/monitor

訪問地址:
  主頁: http://localhost:5000/
  API文檔: http://localhost:5000/health
        '''
    )

    parser.add_argument(
        '--host',
        default='127.0.0.1',
        help='主機地址 (默認: 127.0.0.1, 使用 0.0.0.0 允許外部訪問)'
    )

    parser.add_argument(
        '--port',
        type=int,
        default=5000,
        help='端口號 (默認: 5000)'
    )

    parser.add_argument(
        '--no-debug',
        action='store_true',
        help='關閉調試模式（生產環境）'
    )

    parser.add_argument(
        '--upload-dir',
        default=None,
        help='上傳目錄 (默認: /tmp/exam_uploads)'
    )

    parser.add_argument(
        '--output-dir',
        default=None,
        help='輸出目錄 (默認: /tmp/exam_outputs)'
    )

    parser.add_argument(
        '--secret-key',
        default=None,
        help='Flask secret key (默認: 自動生成)'
    )

    args = parser.parse_args()

    # 構建配置
    config = {}

    if args.secret_key:
        config['SECRET_KEY'] = args.secret_key

    if args.upload_dir:
        config['UPLOAD_FOLDER'] = args.upload_dir

    if args.output_dir:
        config['OUTPUT_FOLDER'] = args.output_dir

    # 創建應用
    app = create_app(config if config else None)

    # 顯示啟動信息
    print("\n" + "="*70)
    print(" " * 15 + "考古題處理系統 Web UI v2.0")
    print("="*70)
    print(f"\n🌐 啟動地址: http://{args.host}:{args.port}/")
    print(f"📂 上傳目錄: {app.config['UPLOAD_FOLDER']}")
    print(f"📁 輸出目錄: {app.config['OUTPUT_FOLDER']}")
    print(f"🔧 調試模式: {'開啟' if not args.no_debug else '關閉'}")
    print("\n功能模塊:")
    print(f"  🕷️  爬蟲下載: http://{args.host}:{args.port}/crawler")
    print(f"  🔍 OCR處理: http://{args.host}:{args.port}/ocr")
    print(f"  📄 PDF處理: http://{args.host}:{args.port}/upload")
    print(f"  ⏱️  性能監控: http://{args.host}:{args.port}/monitor")
    print("\n提示:")
    print("  - 按 Ctrl+C 停止服務器")
    print("  - 訪問 /health 端點查看系統健康狀態")
    print("="*70 + "\n")

    # 運行應用
    try:
        app.run(
            host=args.host,
            port=args.port,
            debug=not args.no_debug,
            threaded=True  # 啟用多線程支持
        )
    except KeyboardInterrupt:
        print("\n\n👋 服務器已停止")
    except Exception as e:
        print(f"\n❌ 啟動失敗: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
