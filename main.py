#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
考古題處理系統主程序
重構後的主要入口點
"""

import sys
import os

# 添加src目錄到路徑
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.api import main

if __name__ == '__main__':
    sys.exit(main())