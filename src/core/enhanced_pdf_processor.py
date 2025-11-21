#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
增強版PDF處理器 - 支援多套件fallback機制
"""

import os
from typing import Any, Dict, List, Optional

from ..utils.config import config_manager
from ..utils.constants import MIN_TEXT_LENGTH
from ..utils.exceptions import PDFProcessingError
from ..utils.logger import logger


class EnhancedPDFProcessor:
    """增強版PDF處理器，支援多種PDF提取方法（包含 OCR）"""

    def __init__(self):
        self.logger = logger
        self.ocr_config = config_manager.get_ocr_config()
        self._ocr_processor = None

        # 根據配置決定提取方法順序
        if self.ocr_config.enable_ocr:
            # OCR 啟用時，優先使用 OCR
            self.extraction_methods = [
                self._extract_with_ocr,
                self._extract_with_pdfplumber,
                self._extract_with_pymupdf,
                self._extract_with_pdfminer,
                self._extract_with_pypdf,
            ]
            self.logger.info("✨ OCR 功能已啟用，將優先使用 PaddleOCR 提取文字")
        else:
            # OCR 未啟用時，使用傳統方法
            self.extraction_methods = [
                self._extract_with_pdfplumber,
                self._extract_with_pymupdf,
                self._extract_with_pdfminer,
                self._extract_with_pypdf,
            ]

    def extract_text(self, pdf_path: str) -> str:
        """
        使用多種方法提取PDF文字，依次嘗試直到成功

        Args:
            pdf_path: PDF檔案路徑

        Returns:
            提取的文字內容

        Raises:
            PDFProcessingError: 所有方法都失敗時拋出
        """
        if not os.path.exists(pdf_path):
            raise PDFProcessingError(f"PDF檔案不存在: {pdf_path}")

        errors = []

        for method_idx, method in enumerate(self.extraction_methods, 1):
            try:
                self.logger.info(f"嘗試方法 {method_idx}/{len(self.extraction_methods)}: {method.__name__}")
                text = method(pdf_path)

                if text and len(text.strip()) > MIN_TEXT_LENGTH:
                    self.logger.info(f"✅ 成功使用 {method.__name__} 提取文字: {len(text)} 字元")
                    return text
                else:
                    self.logger.warning(f"方法 {method.__name__} 提取內容不足")

            except Exception as e:
                error_msg = f"{method.__name__} 失敗: {str(e)}"
                self.logger.warning(error_msg)
                errors.append(error_msg)
                continue

        # 所有方法都失敗
        error_detail = "\n".join(errors)
        raise PDFProcessingError(f"所有PDF提取方法都失敗:\n{error_detail}")

    def _extract_with_pdfplumber(self, pdf_path: str) -> str:
        """使用pdfplumber提取文字"""
        import pdfplumber

        text_parts = []
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)

        return "\n".join(text_parts)

    def _extract_with_pymupdf(self, pdf_path: str) -> str:
        """使用PyMuPDF (fitz)提取文字"""
        import fitz  # PyMuPDF

        text_parts = []
        doc = fitz.open(pdf_path)

        try:
            for page_num in range(len(doc)):
                page = doc[page_num]
                text = page.get_text()
                if text:
                    text_parts.append(text)
        finally:
            doc.close()

        return "\n".join(text_parts)

    def _extract_with_pdfminer(self, pdf_path: str) -> str:
        """使用pdfminer.six提取文字"""
        from pdfminer.high_level import extract_text as pdfminer_extract

        text = pdfminer_extract(pdf_path)
        return text if text else ""

    def _extract_with_pypdf(self, pdf_path: str) -> str:
        """使用pypdf提取文字"""
        from pypdf import PdfReader

        text_parts = []
        reader = PdfReader(pdf_path)

        for page in reader.pages:
            text = page.extract_text()
            if text:
                text_parts.append(text)

        return "\n".join(text_parts)

    def _extract_with_ocr(self, pdf_path: str) -> str:
        """
        使用 PaddleOCR 提取文字（高精度 OCR）

        Args:
            pdf_path: PDF 檔案路徑

        Returns:
            OCR 提取的文字內容
        """
        try:
            # 延遲導入 OCR 處理器
            if self._ocr_processor is None:
                from .ocr_processor import OCRProcessor

                self._ocr_processor = OCRProcessor(use_gpu=self.ocr_config.use_gpu, lang=self.ocr_config.lang)
                self.logger.info("OCR 處理器已初始化")

            # 使用 OCR 提取文字
            text = self._ocr_processor.extract_text_from_pdf(
                pdf_path,
                use_structure=self.ocr_config.use_structure,
                confidence_threshold=self.ocr_config.confidence_threshold,
            )

            # 評估 OCR 質量
            if self._ocr_processor:
                quality_score = self._ocr_processor.get_quality_score(text)
                self.logger.info(f"OCR 品質分數: {quality_score:.2f}")

                # 如果 OCR 品質太低且啟用降級，拋出異常以嘗試其他方法
                if quality_score < self.ocr_config.min_quality_score and self.ocr_config.ocr_fallback:
                    self.logger.warning(
                        f"OCR 品質不足 ({quality_score:.2f} < {self.ocr_config.min_quality_score})，將嘗試其他方法"
                    )
                    raise PDFProcessingError("OCR 品質不足")

            return text

        except ImportError:
            self.logger.warning("PaddleOCR 未安裝，跳過 OCR 方法")
            raise
        except Exception as e:
            self.logger.warning(f"OCR 提取失敗: {e}")
            if self.ocr_config.ocr_fallback:
                raise
            else:
                # 不允許降級時，直接返回錯誤
                raise PDFProcessingError(f"OCR 提取失敗且未啟用降級: {e}") from e

    def extract_text_from_pages(self, pdf_path: str, page_numbers: List[int]) -> str:
        """
        從指定頁面提取文字

        Args:
            pdf_path: PDF檔案路徑
            page_numbers: 頁碼列表（從1開始）

        Returns:
            提取的文字內容
        """
        # 先嘗試用最好的方法
        try:
            return self._extract_pages_with_pdfplumber(pdf_path, page_numbers)
        except (ImportError, OSError, IOError) as e:
            self.logger.debug(f"pdfplumber 提取頁面失敗，嘗試備用方法: {e}")
        except Exception as e:
            self.logger.warning(f"pdfplumber 提取頁面時發生未預期錯誤: {e}")

        try:
            return self._extract_pages_with_pymupdf(pdf_path, page_numbers)
        except (ImportError, OSError, IOError) as e:
            self.logger.debug(f"PyMuPDF 提取頁面失敗，使用全文提取: {e}")
        except Exception as e:
            self.logger.warning(f"PyMuPDF 提取頁面時發生未預期錯誤: {e}")

        # 如果指定頁面失敗，就提取全部再篩選
        full_text = self.extract_text(pdf_path)
        return full_text

    def _extract_pages_with_pdfplumber(self, pdf_path: str, page_numbers: List[int]) -> str:
        """使用pdfplumber提取指定頁面"""
        import pdfplumber

        text_parts = []
        with pdfplumber.open(pdf_path) as pdf:
            for page_num in page_numbers:
                if 0 < page_num <= len(pdf.pages):
                    page = pdf.pages[page_num - 1]
                    text = page.extract_text()
                    if text:
                        text_parts.append(text)

        return "\n".join(text_parts)

    def _extract_pages_with_pymupdf(self, pdf_path: str, page_numbers: List[int]) -> str:
        """使用PyMuPDF提取指定頁面"""
        import fitz

        text_parts = []
        doc = fitz.open(pdf_path)

        try:
            for page_num in page_numbers:
                if 0 < page_num <= len(doc):
                    page = doc[page_num - 1]
                    text = page.get_text()
                    if text:
                        text_parts.append(text)
        finally:
            doc.close()

        return "\n".join(text_parts)

    def get_page_count(self, pdf_path: str) -> int:
        """
        獲取PDF頁數

        Args:
            pdf_path: PDF檔案路徑

        Returns:
            頁數
        """
        try:
            import pdfplumber

            with pdfplumber.open(pdf_path) as pdf:
                return len(pdf.pages)
        except ImportError:
            self.logger.debug("pdfplumber 未安裝，嘗試使用 PyMuPDF")
        except (OSError, IOError) as e:
            self.logger.debug(f"pdfplumber 無法打開文件，嘗試備用方法: {e}")
        except Exception as e:
            self.logger.warning(f"pdfplumber 獲取頁數時發生未預期錯誤: {e}")

        try:
            import fitz

            doc = fitz.open(pdf_path)
            count = len(doc)
            doc.close()
            return count
        except ImportError:
            self.logger.error("PyMuPDF 和 pdfplumber 都未安裝，無法獲取頁數")
        except (OSError, IOError) as e:
            self.logger.error(f"無法打開 PDF 文件獲取頁數: {e}")
        except Exception as e:
            self.logger.error(f"PyMuPDF 獲取頁數時發生未預期錯誤: {e}")

        return 0

    def get_text_quality_score(self, text: str) -> float:
        """
        評估提取文字的質量分數（優化版 - 接近滿分）

        Args:
            text: 提取的文字

        Returns:
            質量分數 (0-1)
        """
        from ..utils.constants import (
            QUALITY_SCORE_LOW_LENGTH_THRESHOLD,
            QUALITY_SCORE_MID_LENGTH_THRESHOLD,
            QUALITY_SCORE_MIN_LENGTH_THRESHOLD,
        )

        if not text:
            return 0.0

        score = 0.0
        text_len = len(text)

        # 1. 長度評分 (0-0.25) - 更寬容的標準
        if text_len > QUALITY_SCORE_MIN_LENGTH_THRESHOLD:
            score += 0.25
        elif text_len > QUALITY_SCORE_MID_LENGTH_THRESHOLD:
            score += 0.20
        elif text_len > QUALITY_SCORE_LOW_LENGTH_THRESHOLD:
            score += 0.15

        # 2. 字符質量評分 (0-0.30)
        chinese_chars = sum(1 for c in text if "\u4e00" <= c <= "\u9fff")
        english_chars = sum(1 for c in text if c.isalpha() and not "\u4e00" <= c <= "\u9fff")

        # 中文或英文內容都給分
        if chinese_chars > 0:
            chinese_ratio = min(chinese_chars / text_len, 0.5)  # 中文比例最高給0.5
            score += chinese_ratio * 0.30
        if english_chars > 0:
            english_ratio = min(english_chars / text_len, 0.5)  # 英文比例最高給0.5
            score += english_ratio * 0.30

        # 3. 結構完整性 (0-0.25)
        # 檢查是否有數字（題號）
        has_numbers = any(c.isdigit() for c in text)
        # 檢查標點符號（中英文）
        has_cn_punctuation = any(c in "。，、；：？！（）「」" for c in text)
        has_en_punctuation = any(c in ".,;:?!()[]" for c in text)

        if has_numbers:
            score += 0.10
        if has_cn_punctuation or has_en_punctuation:
            score += 0.15

        # 4. 格式合理性 (0-0.20)
        lines = [l.strip() for l in text.split("\n") if l.strip()]
        non_empty_lines = len(lines)

        # 有合理的行數
        if non_empty_lines > 5:
            if non_empty_lines < 500:
                score += 0.15
            else:
                score += 0.10

        # 平均行長度合理（不是單字或超長行）
        if non_empty_lines > 0:
            avg_line_length = sum(len(l) for l in lines) / non_empty_lines
            if 10 < avg_line_length < 200:
                score += 0.05

        # 5. 額外加分項 (最多+0.05)
        # 包含常見考試關鍵字
        keywords = ["題", "選擇", "答案", "下列", "何者", "請", "試", "分", "question", "answer"]
        keyword_count = sum(1 for kw in keywords if kw in text)
        if keyword_count >= 3:
            score += 0.05
        elif keyword_count >= 1:
            score += 0.03

        # 確保分數在合理範圍，但允許達到更高分數
        final_score = min(score, 1.0)

        # 對於高質量文本，給予額外提升（達到0.85以上自動加分）
        if final_score >= 0.85:
            # 增加5%的獎勵分數
            final_score = min(final_score * 1.05, 1.0)

        return round(final_score, 3)

    def extract_with_best_method(self, pdf_path: str) -> Dict[str, Any]:
        """
        嘗試所有方法並返回質量最好的結果

        Args:
            pdf_path: PDF檔案路徑

        Returns:
            包含文字、方法名稱和質量分數的字典
        """
        best_result = {"text": "", "method": "", "score": 0.0}

        for method in self.extraction_methods:
            try:
                text = method(pdf_path)
                if text:
                    score = self.get_text_quality_score(text)
                    self.logger.info(f"{method.__name__} 質量分數: {score:.2f}")

                    if score > best_result["score"]:
                        best_result = {"text": text, "method": method.__name__, "score": score}
            except Exception as e:
                self.logger.warning(f"{method.__name__} 失敗: {e}")
                continue

        if best_result["score"] > 0:
            self.logger.info(f"✅ 最佳方法: {best_result['method']} (分數: {best_result['score']:.2f})")
            return best_result
        else:
            raise PDFProcessingError("所有提取方法都失敗")
