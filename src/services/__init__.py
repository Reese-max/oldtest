#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
服務模塊
"""

from .crawler_service import CrawlerService, crawler_service
from .ocr_service import OCRService, ocr_service

__all__ = ["CrawlerService", "crawler_service", "OCRService", "ocr_service"]
