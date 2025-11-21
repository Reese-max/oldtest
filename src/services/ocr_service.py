#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OCR 處理服務
整合增強型 OCR 功能到 Web UI
"""

import os
import sys
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

# 添加項目根目錄到路徑
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import yaml

from src.core.enhanced_ocr_processor import EnhancedOCRProcessor


class OCRService:
    """OCR 處理服務"""

    def __init__(self):
        # 載入配置從 YAML 文件
        self.config = self._load_config()

        # 創建增強型 OCR 處理器
        self.processor = EnhancedOCRProcessor(self.config)

    def _load_config(self):
        """從 YAML 文件載入 OCR 配置"""
        config_path = Path(__file__).parent.parent.parent / "config.yaml"
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                full_config = yaml.safe_load(f)
            return full_config.get("ocr", {})
        except Exception:
            # 返回默認配置
            return {
                "enable_enhanced_ocr": True,
                "auto_detect_scan": True,
                "auto_tune_parameters": True,
                "enable_quality_check": True,
                "enable_hybrid_mode": True,
                "min_dpi": 150,
                "max_dpi": 400,
                "excellent_threshold": 0.9,
                "good_threshold": 0.7,
                "fair_threshold": 0.5,
            }

    def detect_pdf_type(self, pdf_path: str) -> Dict[str, Any]:
        """
        檢測 PDF 類型

        Args:
            pdf_path: PDF 文件路徑

        Returns:
            檢測結果字典
        """
        try:
            pdf_type, analysis = self.processor.detect_pdf_type(pdf_path)

            return {"success": True, "pdf_type": pdf_type, "analysis": analysis}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def optimize_parameters(self, pdf_path: str) -> Dict[str, Any]:
        """
        優化 OCR 參數

        Args:
            pdf_path: PDF 文件路徑

        Returns:
            優化結果字典
        """
        try:
            # 先檢測類型
            pdf_type, analysis = self.processor.detect_pdf_type(pdf_path)

            # 優化參數
            optimized_params = self.processor.optimize_parameters(pdf_type, analysis)

            return {"success": True, "pdf_type": pdf_type, "parameters": optimized_params}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def process_pdf(self, pdf_path: str, custom_params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        處理 PDF 文件

        Args:
            pdf_path: PDF 文件路徑
            custom_params: 自定義參數（可選）

        Returns:
            處理結果字典
        """
        try:
            # 檢測類型
            pdf_type, analysis = self.processor.detect_pdf_type(pdf_path)

            # 優化參數
            if custom_params:
                ocr_params = custom_params
            else:
                ocr_params = self.processor.optimize_parameters(pdf_type, analysis)

            # 處理 PDF（這裡需要調用實際的 OCR 處理邏輯）
            # 由於完整的 OCR 處理需要與 PDF 處理器集成，這裡返回參數建議
            return {
                "success": True,
                "pdf_type": pdf_type,
                "analysis": analysis,
                "ocr_params": ocr_params,
                "message": "OCR 參數已優化，準備處理",
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def validate_quality(self, text: str, pdf_type: str) -> Dict[str, Any]:
        """
        驗證 OCR 質量

        Args:
            text: OCR 提取的文本
            pdf_type: PDF 類型

        Returns:
            質量評估結果
        """
        try:
            quality_score, quality_level, issues = self.processor.validate_ocr_quality(text, pdf_type)

            return {"success": True, "quality_score": quality_score, "quality_level": quality_level, "issues": issues}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_config(self) -> Dict[str, Any]:
        """
        獲取 OCR 配置

        Returns:
            配置字典
        """
        return {
            "enabled": self.config.get("enable_enhanced_ocr", True),
            "auto_detect": self.config.get("auto_detect_scan", True),
            "auto_tune": self.config.get("auto_tune_parameters", True),
            "quality_check": self.config.get("enable_quality_check", True),
            "hybrid_mode": self.config.get("enable_hybrid_mode", True),
            "dpi_range": {"min": self.config.get("min_dpi", 150), "max": self.config.get("max_dpi", 400)},
            "thresholds": {
                "excellent": self.config.get("excellent_threshold", 0.9),
                "good": self.config.get("good_threshold", 0.7),
                "fair": self.config.get("fair_threshold", 0.5),
            },
        }

    def update_config(self, new_config: Dict[str, Any]) -> bool:
        """
        更新 OCR 配置

        Args:
            new_config: 新配置

        Returns:
            是否成功更新
        """
        try:
            self.config.update(new_config)
            # 重新創建處理器
            self.processor = EnhancedOCRProcessor(self.config)
            return True
        except Exception:
            return False


# 全局服務實例
ocr_service = OCRService()
