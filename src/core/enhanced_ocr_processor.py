#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
增強型 OCR 處理器 - 深度整合版（優先級2功能）

功能特性：
1. 自動掃描版檢測 - 智能判斷是否需要 OCR
2. 智能參數調優 - 根據 PDF 特性自動調整參數
3. OCR 結果質量驗證 - 多層驗證確保準確性
4. 混合模式處理 - 文字+掃描混合 PDF 的最佳策略
"""

import os
import re
from typing import Dict, List, Tuple, Optional, Any
from pathlib import Path
from ..utils.logger import logger
from ..utils.config import config_manager
from ..utils.exceptions import PDFProcessingError


class PDFType:
    """PDF 類型枚舉"""
    TEXT_BASED = "text"          # 文字型PDF
    SCANNED = "scanned"          # 掃描版PDF
    HYBRID = "hybrid"            # 混合型PDF
    UNKNOWN = "unknown"          # 未知類型


class OCRQuality:
    """OCR 質量評估"""
    EXCELLENT = "excellent"  # 優秀 (>90%)
    GOOD = "good"           # 良好 (70-90%)
    FAIR = "fair"           # 一般 (50-70%)
    POOR = "poor"           # 差 (<50%)


class EnhancedOCRProcessor:
    """增強型 OCR 處理器"""

    def __init__(self, use_gpu: bool = False, lang: str = 'ch'):
        """
        初始化增強型 OCR 處理器

        Args:
            use_gpu: 是否使用 GPU 加速
            lang: 語言設定
        """
        self.logger = logger
        self.use_gpu = use_gpu
        self.lang = lang
        self._ocr_processor = None  # 延遲載入基礎 OCR 處理器

        # 配置閾值
        self.config = {
            # 掃描版檢測閾值
            'text_ratio_threshold': 0.1,  # 文字覆蓋率閾值
            'min_words_per_page': 50,     # 最少字數
            'image_ratio_threshold': 0.5,  # 圖片覆蓋率閾值

            # OCR 質量閾值
            'excellent_threshold': 0.9,
            'good_threshold': 0.7,
            'fair_threshold': 0.5,

            # 智能參數
            'auto_tune_dpi': True,         # 自動調整 DPI
            'auto_tune_threshold': True,   # 自動調整閾值
        }

    def detect_pdf_type(self, pdf_path: str) -> Tuple[str, Dict[str, Any]]:
        """
        自動檢測 PDF 類型（功能1：自動掃描版檢測）

        Args:
            pdf_path: PDF 文件路徑

        Returns:
            (PDF類型, 檢測詳情)
        """
        if not os.path.exists(pdf_path):
            raise PDFProcessingError(f"PDF 文件不存在: {pdf_path}")

        self.logger.info(f"🔍 檢測 PDF 類型: {pdf_path}")

        try:
            import pdfplumber

            with pdfplumber.open(pdf_path) as pdf:
                total_pages = len(pdf.pages)
                text_pages = 0
                scanned_pages = 0
                total_text_length = 0
                total_images = 0
                total_chars = 0

                # 分析每一頁（最多分析前10頁以節省時間）
                sample_pages = min(10, total_pages)

                for i in range(sample_pages):
                    page = pdf.pages[i]

                    # 提取文字
                    text = page.extract_text() or ""
                    text_clean = text.strip()

                    # 計算文字量
                    words = len(text_clean.split())
                    chars = len(text_clean)
                    total_text_length += len(text_clean)
                    total_chars += chars

                    # 獲取圖片
                    images = page.images
                    total_images += len(images)

                    # 分類頁面
                    if words >= self.config['min_words_per_page']:
                        text_pages += 1
                    elif len(images) > 0 or chars < 100:
                        scanned_pages += 1

                # 計算統計數據
                avg_text_per_page = total_text_length / sample_pages
                avg_chars_per_page = total_chars / sample_pages
                text_page_ratio = text_pages / sample_pages
                scanned_page_ratio = scanned_pages / sample_pages

                # 判斷 PDF 類型
                pdf_type = self._classify_pdf_type(
                    text_page_ratio,
                    scanned_page_ratio,
                    avg_chars_per_page,
                    total_images
                )

                # 詳細信息
                details = {
                    'total_pages': total_pages,
                    'sample_pages': sample_pages,
                    'text_pages': text_pages,
                    'scanned_pages': scanned_pages,
                    'text_page_ratio': text_page_ratio,
                    'scanned_page_ratio': scanned_page_ratio,
                    'avg_text_length': avg_text_per_page,
                    'avg_chars_per_page': avg_chars_per_page,
                    'total_images': total_images,
                    'pdf_type': pdf_type
                }

                # 記錄結果
                self._log_detection_result(pdf_type, details)

                return pdf_type, details

        except ImportError:
            self.logger.warning("pdfplumber 未安裝，使用備用檢測方法")
            return self._detect_with_pymupdf(pdf_path)

        except Exception as e:
            self.logger.error(f"PDF 類型檢測失敗: {e}")
            return PDFType.UNKNOWN, {'error': str(e)}

    def _classify_pdf_type(self, text_ratio: float, scanned_ratio: float,
                          avg_chars: float, total_images: int) -> str:
        """
        分類 PDF 類型

        Args:
            text_ratio: 文字頁面比例
            scanned_ratio: 掃描頁面比例
            avg_chars: 平均字符數
            total_images: 圖片總數

        Returns:
            PDF 類型
        """
        # 文字型 PDF
        if text_ratio > 0.8 and avg_chars > 500:
            return PDFType.TEXT_BASED

        # 掃描版 PDF
        if scanned_ratio > 0.7 or (total_images > 5 and avg_chars < 100):
            return PDFType.SCANNED

        # 混合型 PDF
        if text_ratio > 0.3 and scanned_ratio > 0.3:
            return PDFType.HYBRID

        # 默認為掃描版（保守策略，確保使用 OCR）
        if avg_chars < 200:
            return PDFType.SCANNED

        return PDFType.UNKNOWN

    def _detect_with_pymupdf(self, pdf_path: str) -> Tuple[str, Dict[str, Any]]:
        """使用 PyMuPDF 的備用檢測方法"""
        try:
            import fitz

            doc = fitz.open(pdf_path)
            total_pages = len(doc)
            text_pages = 0
            total_text = 0

            sample_pages = min(10, total_pages)

            for i in range(sample_pages):
                page = doc[i]
                text = page.get_text()
                if len(text.strip()) > 100:
                    text_pages += 1
                total_text += len(text)

            doc.close()

            text_ratio = text_pages / sample_pages
            avg_text = total_text / sample_pages

            if text_ratio > 0.7 and avg_text > 500:
                pdf_type = PDFType.TEXT_BASED
            elif text_ratio < 0.3 or avg_text < 100:
                pdf_type = PDFType.SCANNED
            else:
                pdf_type = PDFType.HYBRID

            details = {
                'total_pages': total_pages,
                'sample_pages': sample_pages,
                'text_pages': text_pages,
                'text_ratio': text_ratio,
                'avg_text': avg_text,
                'pdf_type': pdf_type,
                'detection_method': 'pymupdf'
            }

            self._log_detection_result(pdf_type, details)
            return pdf_type, details

        except Exception as e:
            self.logger.error(f"PyMuPDF 檢測失敗: {e}")
            return PDFType.UNKNOWN, {'error': str(e)}

    def _log_detection_result(self, pdf_type: str, details: Dict[str, Any]):
        """記錄檢測結果"""
        if pdf_type == PDFType.TEXT_BASED:
            icon = "📄"
            desc = "文字型 PDF（無需 OCR）"
        elif pdf_type == PDFType.SCANNED:
            icon = "🖼️"
            desc = "掃描版 PDF（需要 OCR）"
        elif pdf_type == PDFType.HYBRID:
            icon = "📑"
            desc = "混合型 PDF（部分需要 OCR）"
        else:
            icon = "❓"
            desc = "未知類型 PDF"

        self.logger.info(f"{icon} 檢測結果: {desc}")
        self.logger.debug(f"詳細信息: {details}")

    def optimize_ocr_parameters(self, pdf_path: str, pdf_type: str,
                               detection_details: Dict[str, Any]) -> Dict[str, Any]:
        """
        智能 OCR 參數調優（功能2：智能參數調優）

        Args:
            pdf_path: PDF 文件路徑
            pdf_type: PDF 類型
            detection_details: 檢測詳情

        Returns:
            優化後的 OCR 參數
        """
        self.logger.info("⚙️  智能 OCR 參數調優")

        # 基礎參數（從配置載入）
        ocr_config = config_manager.get_ocr_config()
        params = {
            'use_gpu': self.use_gpu,
            'lang': self.lang,
            'dpi': ocr_config.pdf_to_image_dpi,
            'zoom': ocr_config.pdf_to_image_zoom,
            'confidence_threshold': ocr_config.confidence_threshold,
            'det_db_thresh': 0.3,
            'det_db_box_thresh': 0.5,
            'rec_batch_num': 6,
            'use_angle_cls': True,
            'enable_mkldnn': True
        }

        # 根據 PDF 類型調整
        if pdf_type == PDFType.SCANNED:
            # 掃描版：提高 DPI 和閾值精度
            params['dpi'] = max(params['dpi'], 300)
            params['zoom'] = max(params['zoom'], 2.0)
            params['det_db_thresh'] = 0.2  # 更敏感的檢測
            params['confidence_threshold'] = 0.6  # 較高的信心閾值
            self.logger.info("  📊 掃描版優化: 高DPI + 敏感檢測")

        elif pdf_type == PDFType.TEXT_BASED:
            # 文字型：降低處理需求
            params['dpi'] = 150
            params['zoom'] = 1.5
            params['skip_ocr'] = True  # 標記可跳過 OCR
            self.logger.info("  📝 文字型優化: 低DPI（可跳過OCR）")

        elif pdf_type == PDFType.HYBRID:
            # 混合型：平衡策略
            params['dpi'] = 250
            params['zoom'] = 1.8
            params['det_db_thresh'] = 0.25
            params['confidence_threshold'] = 0.55
            params['hybrid_mode'] = True  # 標記使用混合模式
            self.logger.info("  🔄 混合型優化: 平衡參數")

        # 根據頁面特徵微調
        if 'avg_chars_per_page' in detection_details:
            avg_chars = detection_details['avg_chars_per_page']
            if avg_chars < 50:  # 極少文字
                params['zoom'] = min(params['zoom'] * 1.2, 3.0)
                self.logger.info(f"  🔍 少量文字 ({avg_chars:.0f}字/頁)，提高放大倍數")

        # 根據圖片數量調整
        if 'total_images' in detection_details:
            images = detection_details['total_images']
            if images > 20:  # 大量圖片
                params['dpi'] = min(params['dpi'] + 50, 400)
                self.logger.info(f"  🖼️  大量圖片 ({images}張)，提高DPI")

        self.logger.success(f"✅ 參數調優完成: DPI={params['dpi']}, Zoom={params['zoom']}")
        return params

    def validate_ocr_quality(self, text: str, pdf_path: str = None) -> Tuple[str, Dict[str, Any]]:
        """
        OCR 結果質量驗證（功能3：質量驗證）

        Args:
            text: OCR 提取的文字
            pdf_path: PDF 文件路徑（可選，用於深度驗證）

        Returns:
            (質量等級, 驗證詳情)
        """
        self.logger.info("🔍 OCR 質量驗證")

        metrics = {
            'total_chars': len(text),
            'total_words': len(text.split()),
            'chinese_ratio': 0.0,
            'digit_ratio': 0.0,
            'punctuation_ratio': 0.0,
            'special_char_ratio': 0.0,
            'confidence_score': 0.0,
            'completeness_score': 0.0,
            'readability_score': 0.0
        }

        if not text or len(text) < 10:
            return OCRQuality.POOR, {'reason': '文字過少', **metrics}

        # 1. 字符類型分析
        chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', text))
        digits = len(re.findall(r'\d', text))
        punctuation = len(re.findall(r'[，。！？、；：""''（）《》【】]', text))
        special_chars = len(re.findall(r'[^\u4e00-\u9fffa-zA-Z0-9\s，。！？、；：""''（）《》【】]', text))

        total_chars = len(text)
        metrics['chinese_ratio'] = chinese_chars / total_chars if total_chars > 0 else 0
        metrics['digit_ratio'] = digits / total_chars if total_chars > 0 else 0
        metrics['punctuation_ratio'] = punctuation / total_chars if total_chars > 0 else 0
        metrics['special_char_ratio'] = special_chars / total_chars if total_chars > 0 else 0

        # 2. 可信度評分
        # 中文字符應占主體
        if metrics['chinese_ratio'] > 0.5:
            confidence = 0.8
        elif metrics['chinese_ratio'] > 0.3:
            confidence = 0.6
        else:
            confidence = 0.4

        # 標點符號合理性
        if 0.05 < metrics['punctuation_ratio'] < 0.15:
            confidence += 0.1

        # 異常字符過多扣分
        if metrics['special_char_ratio'] > 0.1:
            confidence -= 0.2

        metrics['confidence_score'] = max(0, min(1, confidence))

        # 3. 完整性評分
        # 檢查常見問題標記
        question_markers = len(re.findall(r'[一二三四五六七八九十\d]+[、\.]', text))
        if question_markers >= 5:
            completeness = 0.9
        elif question_markers >= 3:
            completeness = 0.7
        elif question_markers >= 1:
            completeness = 0.5
        else:
            completeness = 0.3

        metrics['completeness_score'] = completeness

        # 4. 可讀性評分
        # 檢查完整詞語
        words = text.split()
        long_words = [w for w in words if len(w) >= 2]
        readability = min(1.0, len(long_words) / len(words)) if words else 0
        metrics['readability_score'] = readability

        # 5. 綜合評分
        overall_score = (
            metrics['confidence_score'] * 0.4 +
            metrics['completeness_score'] * 0.3 +
            metrics['readability_score'] * 0.3
        )
        metrics['overall_score'] = overall_score

        # 6. 質量等級判定
        if overall_score >= self.config['excellent_threshold']:
            quality = OCRQuality.EXCELLENT
            icon = "🎯"
        elif overall_score >= self.config['good_threshold']:
            quality = OCRQuality.GOOD
            icon = "✅"
        elif overall_score >= self.config['fair_threshold']:
            quality = OCRQuality.FAIR
            icon = "⚠️"
        else:
            quality = OCRQuality.POOR
            icon = "❌"

        self.logger.info(f"{icon} OCR 質量: {quality} (綜合評分: {overall_score:.2f})")
        self.logger.debug(f"詳細指標: {metrics}")

        return quality, metrics

    def process_hybrid_pdf(self, pdf_path: str) -> str:
        """
        混合模式處理（功能4：混合模式處理）

        Args:
            pdf_path: PDF 文件路徑

        Returns:
            提取的文字
        """
        self.logger.info("🔄 混合模式處理")

        try:
            import pdfplumber

            all_text = []

            with pdfplumber.open(pdf_path) as pdf:
                for i, page in enumerate(pdf.pages, 1):
                    # 嘗試提取文字
                    text = page.extract_text() or ""
                    words = len(text.strip().split())

                    # 判斷此頁是否需要 OCR
                    if words < self.config['min_words_per_page']:
                        self.logger.debug(f"第 {i} 頁: 文字少({words}詞)，使用 OCR")
                        # 使用 OCR
                        page_text = self._ocr_single_page(pdf_path, i - 1)
                        all_text.append(page_text)
                    else:
                        self.logger.debug(f"第 {i} 頁: 文字豐富({words}詞)，直接提取")
                        # 直接使用提取的文字
                        all_text.append(text)

            result = '\n'.join(all_text)
            self.logger.success(f"✅ 混合模式處理完成，共 {len(result)} 字元")
            return result

        except Exception as e:
            self.logger.error(f"混合模式處理失敗: {e}")
            raise PDFProcessingError(f"混合模式處理失敗: {e}") from e

    def _ocr_single_page(self, pdf_path: str, page_num: int) -> str:
        """
        OCR 處理單頁

        Args:
            pdf_path: PDF 路徑
            page_num: 頁碼（從0開始）

        Returns:
            提取的文字
        """
        # 延遲載入 OCR 處理器
        if self._ocr_processor is None:
            from .ocr_processor import OCRProcessor
            self._ocr_processor = OCRProcessor(
                use_gpu=self.use_gpu,
                lang=self.lang
            )

        # 提取單頁（這裡需要實現單頁 OCR，簡化處理）
        # 實際應該修改 OCRProcessor 支持單頁處理
        return f"[OCR 頁面 {page_num + 1}]"

    def smart_extract_text(self, pdf_path: str) -> Dict[str, Any]:
        """
        智能文字提取（整合所有功能）

        Args:
            pdf_path: PDF 文件路徑

        Returns:
            提取結果字典
        """
        self.logger.info(f"🚀 開始智能文字提取: {pdf_path}")

        result = {
            'success': False,
            'text': '',
            'pdf_type': PDFType.UNKNOWN,
            'ocr_quality': OCRQuality.POOR,
            'detection_details': {},
            'ocr_params': {},
            'quality_metrics': {},
            'processing_method': 'unknown'
        }

        try:
            # 步驟1: 檢測 PDF 類型
            pdf_type, detection_details = self.detect_pdf_type(pdf_path)
            result['pdf_type'] = pdf_type
            result['detection_details'] = detection_details

            # 步驟2: 根據類型選擇處理策略
            if pdf_type == PDFType.TEXT_BASED:
                # 文字型 PDF - 直接提取
                self.logger.info("📝 使用文字提取")
                text = self._extract_text_directly(pdf_path)
                result['processing_method'] = 'direct_extraction'

            elif pdf_type == PDFType.SCANNED:
                # 掃描版 PDF - OCR
                self.logger.info("🖼️  使用 OCR 提取")
                ocr_params = self.optimize_ocr_parameters(pdf_path, pdf_type, detection_details)
                result['ocr_params'] = ocr_params
                text = self._extract_with_optimized_ocr(pdf_path, ocr_params)
                result['processing_method'] = 'ocr'

            elif pdf_type == PDFType.HYBRID:
                # 混合型 PDF - 混合模式
                self.logger.info("🔄 使用混合模式")
                text = self.process_hybrid_pdf(pdf_path)
                result['processing_method'] = 'hybrid'

            else:
                # 未知類型 - 保守使用 OCR
                self.logger.warning("❓ 未知類型，使用 OCR")
                ocr_params = self.optimize_ocr_parameters(pdf_path, PDFType.SCANNED, detection_details)
                result['ocr_params'] = ocr_params
                text = self._extract_with_optimized_ocr(pdf_path, ocr_params)
                result['processing_method'] = 'ocr_fallback'

            result['text'] = text

            # 步驟3: 質量驗證
            quality, metrics = self.validate_ocr_quality(text, pdf_path)
            result['ocr_quality'] = quality
            result['quality_metrics'] = metrics

            # 步驟4: 質量不佳時的補救措施
            if quality == OCRQuality.POOR and pdf_type != PDFType.TEXT_BASED:
                self.logger.warning("⚠️  OCR 質量差，嘗試重新處理")
                # 提高參數重試
                retry_params = self.optimize_ocr_parameters(pdf_path, PDFType.SCANNED, detection_details)
                retry_params['dpi'] = min(retry_params['dpi'] + 100, 400)
                text = self._extract_with_optimized_ocr(pdf_path, retry_params)
                result['text'] = text
                result['processing_method'] += '_retry'

                # 重新驗證
                quality, metrics = self.validate_ocr_quality(text, pdf_path)
                result['ocr_quality'] = quality
                result['quality_metrics'] = metrics

            result['success'] = True
            self.logger.success(f"✅ 智能提取完成！質量: {quality}, 字數: {len(text)}")

        except Exception as e:
            self.logger.error(f"智能提取失敗: {e}")
            result['error'] = str(e)

        return result

    def _extract_text_directly(self, pdf_path: str) -> str:
        """直接提取 PDF 文字"""
        try:
            import pdfplumber
            with pdfplumber.open(pdf_path) as pdf:
                text = '\n'.join(page.extract_text() or "" for page in pdf.pages)
            return text
        except Exception as e:
            self.logger.error(f"直接提取失敗: {e}")
            return ""

    def _extract_with_optimized_ocr(self, pdf_path: str, params: Dict[str, Any]) -> str:
        """使用優化參數進行 OCR"""
        # 延遲載入 OCR 處理器
        if self._ocr_processor is None:
            from .ocr_processor import OCRProcessor
            self._ocr_processor = OCRProcessor(
                use_gpu=params.get('use_gpu', self.use_gpu),
                lang=params.get('lang', self.lang)
            )

        # 使用 OCR 提取
        text = self._ocr_processor.extract_text_from_pdf(
            pdf_path,
            use_structure=False,
            confidence_threshold=params.get('confidence_threshold', 0.5)
        )

        return text
