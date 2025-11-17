#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OCR處理器 - 整合 PaddleOCR
提供高精度的 PDF 和圖片文字識別功能
"""

import os
import tempfile
import shutil
from typing import Optional, List, Dict, Any, Tuple
from pathlib import Path
from ..utils.logger import logger
from ..utils.exceptions import PDFProcessingError
from ..utils.config import config_manager


class OCRProcessor:
    """OCR處理器 - 使用 PaddleOCR 進行文字識別"""

    def __init__(self, use_gpu: bool = False, lang: str = 'ch'):
        """
        初始化 OCR 處理器

        Args:
            use_gpu: 是否使用 GPU 加速
            lang: 語言設定 ('ch'=中英文, 'en'=英文, 'chinese_cht'=繁體中文)
        """
        self.logger = logger
        self.use_gpu = use_gpu
        self.lang = lang
        self._ocr_engine = None
        self._structure_engine = None
        self._temp_dirs = []  # 追蹤臨時目錄以便清理

    def _init_ocr_engine(self):
        """延遲初始化 OCR 引擎（節省記憶體）"""
        if self._ocr_engine is None:
            try:
                from paddleocr import PaddleOCR

                self.logger.info(f"初始化 PaddleOCR 引擎 (語言: {self.lang}, GPU: {self.use_gpu})")
                self._ocr_engine = PaddleOCR(
                    use_angle_cls=True,  # 支持旋轉文字
                    lang=self.lang,
                    use_gpu=self.use_gpu,
                    show_log=False,
                    enable_mkldnn=True,  # 啟用 Intel CPU 加速
                    det_db_thresh=0.3,   # 文字檢測閾值
                    det_db_box_thresh=0.5,  # 文字框閾值
                    rec_batch_num=6,     # 識別批次大小
                )

                self.logger.success("PaddleOCR 引擎初始化成功")
            except ImportError:
                error_msg = "PaddleOCR 未安裝，請執行: pip install paddlepaddle paddleocr"
                self.logger.failure(error_msg)
                raise ImportError(error_msg)
            except Exception as e:
                error_msg = f"PaddleOCR 引擎初始化失敗: {e}"
                self.logger.failure(error_msg)
                raise PDFProcessingError(error_msg) from e

    def _init_structure_engine(self):
        """初始化結構化分析引擎"""
        if self._structure_engine is None:
            try:
                from paddleocr import PPStructure

                self.logger.info("初始化 PP-Structure 引擎")
                self._structure_engine = PPStructure(
                    use_gpu=self.use_gpu,
                    show_log=False,
                    lang=self.lang,
                    layout=True,        # 啟用版面分析
                    table=True,         # 啟用表格識別
                    ocr=True,           # 啟用 OCR
                    recovery=True,      # 啟用結構恢復
                )

                self.logger.success("PP-Structure 引擎初始化成功")
            except ImportError:
                self.logger.warning("PP-Structure 不可用，僅使用基礎 OCR")
                self._structure_engine = None
            except Exception as e:
                self.logger.warning(f"PP-Structure 引擎初始化失敗: {e}")
                self._structure_engine = None

    def extract_text_from_pdf(self, pdf_path: str,
                             use_structure: bool = False,
                             confidence_threshold: float = 0.5) -> str:
        """
        從 PDF 提取文字

        Args:
            pdf_path: PDF 檔案路徑
            use_structure: 是否使用結構化分析
            confidence_threshold: 信心度閾值（低於此值的識別結果會被過濾）

        Returns:
            提取的文字內容
        """
        if not os.path.exists(pdf_path):
            raise PDFProcessingError(f"PDF檔案不存在: {pdf_path}")

        try:
            self.logger.info(f"使用 OCR 處理 PDF: {pdf_path}")

            # 將 PDF 轉換為圖片
            images = self._pdf_to_images(pdf_path)

            if not images:
                raise PDFProcessingError("PDF 轉圖片失敗")

            # 根據設定選擇處理方式
            if use_structure and self._structure_engine:
                text = self._extract_with_structure(images, confidence_threshold)
            else:
                text = self._extract_with_ocr(images, confidence_threshold)

            self.logger.success(f"OCR 提取完成，共 {len(text)} 字元")
            return text

        except Exception as e:
            error_msg = f"OCR 處理失敗: {e}"
            self.logger.failure(error_msg)
            raise PDFProcessingError(error_msg) from e

    def _pdf_to_images(self, pdf_path: str) -> List[str]:
        """
        將 PDF 轉換為圖片

        Args:
            pdf_path: PDF 檔案路徑

        Returns:
            圖片檔案路徑列表
        """
        try:
            import fitz  # PyMuPDF

            self.logger.info("轉換 PDF 為圖片...")
            images = []

            # 創建臨時目錄並追蹤
            temp_dir = tempfile.mkdtemp(prefix='ocr_')
            self._temp_dirs.append(temp_dir)

            # 打開 PDF（使用 try-finally 確保關閉）
            pdf_document = fitz.open(pdf_path)
            try:
                # 轉換每一頁
                for page_num in range(len(pdf_document)):
                    page = pdf_document[page_num]

                    # 設定較高的解析度以提升 OCR 準確度
                    ocr_config = config_manager.get_ocr_config()
                    zoom = ocr_config.pdf_to_image_zoom  # 使用配置的放大倍數
                    mat = fitz.Matrix(zoom, zoom)
                    pix = page.get_pixmap(matrix=mat, alpha=False)

                    # 儲存圖片
                    image_path = os.path.join(temp_dir, f"page_{page_num + 1}.png")
                    pix.save(image_path)
                    images.append(image_path)

                    self.logger.debug(f"轉換第 {page_num + 1} 頁")

                self.logger.success(f"PDF 轉圖片完成，共 {len(images)} 頁")
                return images
            finally:
                pdf_document.close()

        except ImportError:
            # 降級到使用 pdf2image
            try:
                from pdf2image import convert_from_path

                self.logger.info("使用 pdf2image 轉換...")
                temp_dir = tempfile.mkdtemp(prefix='ocr_')
                self._temp_dirs.append(temp_dir)  # 追蹤臨時目錄

                # 使用配置的 DPI 值
                ocr_config = config_manager.get_ocr_config()
                images_pil = convert_from_path(
                    pdf_path,
                    dpi=ocr_config.pdf_to_image_dpi,  # 使用配置的 DPI
                    fmt='png'
                )

                images = []
                for i, img in enumerate(images_pil):
                    image_path = os.path.join(temp_dir, f"page_{i + 1}.png")
                    img.save(image_path, 'PNG')
                    images.append(image_path)

                self.logger.success(f"PDF 轉圖片完成，共 {len(images)} 頁")
                return images

            except ImportError:
                error_msg = "需要安裝 PyMuPDF 或 pdf2image: pip install PyMuPDF 或 pip install pdf2image"
                self.logger.failure(error_msg)
                raise ImportError(error_msg)

        except Exception as e:
            error_msg = f"PDF 轉圖片失敗: {e}"
            self.logger.failure(error_msg)
            raise PDFProcessingError(error_msg) from e

    def _extract_with_ocr(self, images: List[str],
                         confidence_threshold: float) -> str:
        """
        使用基礎 OCR 提取文字

        Args:
            images: 圖片路徑列表
            confidence_threshold: 信心度閾值

        Returns:
            提取的文字內容
        """
        self._init_ocr_engine()

        all_text = []

        for i, image_path in enumerate(images, 1):
            self.logger.debug(f"OCR 處理第 {i}/{len(images)} 頁")

            try:
                # 執行 OCR
                result = self._ocr_engine.ocr(image_path, cls=True)

                if result and result[0]:
                    page_text = []

                    for line in result[0]:
                        if line:
                            # line 格式: [[[x1,y1], [x2,y2], [x3,y3], [x4,y4]], (text, confidence)]
                            text_info = line[1]
                            text = text_info[0]
                            confidence = text_info[1]

                            # 過濾低信心度的結果
                            if confidence >= confidence_threshold:
                                page_text.append(text)
                            else:
                                self.logger.debug(f"過濾低信心度文字: {text} ({confidence:.2f})")

                    if page_text:
                        all_text.append('\n'.join(page_text))

            except Exception as e:
                self.logger.warning(f"第 {i} 頁 OCR 失敗: {e}")
                continue

        return '\n'.join(all_text)

    def _extract_with_structure(self, images: List[str],
                               confidence_threshold: float) -> str:
        """
        使用結構化分析提取文字

        Args:
            images: 圖片路徑列表
            confidence_threshold: 信心度閾值

        Returns:
            提取的文字內容（保留結構）
        """
        self._init_structure_engine()

        if not self._structure_engine:
            # 降級到基礎 OCR
            return self._extract_with_ocr(images, confidence_threshold)

        all_text = []

        for i, image_path in enumerate(images, 1):
            self.logger.debug(f"結構化分析第 {i}/{len(images)} 頁")

            try:
                # 執行結構化分析
                result = self._structure_engine(image_path)

                if result:
                    page_elements = []

                    for region in result:
                        region_type = region.get('type', 'text')

                        if region_type == 'table':
                            # 表格轉文字
                            table_text = self._parse_table(region)
                            if table_text:
                                page_elements.append(table_text)

                        elif region_type == 'text':
                            # 一般文字
                            text = region.get('res', {}).get('text', '')
                            confidence = region.get('res', {}).get('confidence', 1.0)

                            if text and confidence >= confidence_threshold:
                                page_elements.append(text)

                        elif region_type == 'title':
                            # 標題
                            text = region.get('res', {}).get('text', '')
                            if text:
                                page_elements.append(f"\n{text}\n")

                    if page_elements:
                        all_text.append('\n'.join(page_elements))

            except Exception as e:
                self.logger.warning(f"第 {i} 頁結構化分析失敗: {e}")
                continue

        return '\n'.join(all_text)

    def _parse_table(self, table_region: Dict[str, Any]) -> str:
        """
        解析表格內容

        Args:
            table_region: 表格區域資訊

        Returns:
            表格文字內容
        """
        try:
            table_html = table_region.get('res', {}).get('html', '')

            if table_html:
                # 簡單將 HTML 表格轉為文字
                # 可以使用 BeautifulSoup 進行更精細的處理
                import re

                # 移除 HTML 標籤
                text = re.sub(r'<[^>]+>', ' ', table_html)
                # 清理多餘空白
                text = re.sub(r'\s+', ' ', text).strip()

                return f"\n[表格]\n{text}\n[/表格]\n"

            return ""

        except Exception as e:
            self.logger.warning(f"表格解析失敗: {e}")
            return ""

    def extract_text_from_image(self, image_path: str,
                               confidence_threshold: float = 0.5) -> str:
        """
        從圖片提取文字

        Args:
            image_path: 圖片路徑
            confidence_threshold: 信心度閾值

        Returns:
            提取的文字內容
        """
        if not os.path.exists(image_path):
            raise PDFProcessingError(f"圖片檔案不存在: {image_path}")

        try:
            self.logger.info(f"OCR 處理圖片: {image_path}")

            text = self._extract_with_ocr([image_path], confidence_threshold)

            self.logger.success(f"圖片 OCR 完成，共 {len(text)} 字元")
            return text

        except Exception as e:
            error_msg = f"圖片 OCR 失敗: {e}"
            self.logger.failure(error_msg)
            raise PDFProcessingError(error_msg) from e

    def get_quality_score(self, text: str) -> float:
        """
        評估 OCR 文字品質

        Args:
            text: OCR 提取的文字

        Returns:
            品質分數 (0-1)
        """
        if not text:
            return 0.0

        score = 0.0

        # 長度評分（30%）
        text_length = len(text)
        if text_length > 1000:
            score += 0.3
        elif text_length > 500:
            score += 0.2
        elif text_length > 100:
            score += 0.1

        # 中文字符比例（30%）
        chinese_chars = len([c for c in text if '\u4e00' <= c <= '\u9fff'])
        if text_length > 0:
            chinese_ratio = chinese_chars / text_length
            score += chinese_ratio * 0.3

        # 數字和英文比例（20%）
        alphanumeric = len([c for c in text if c.isalnum()])
        if text_length > 0:
            alphanumeric_ratio = alphanumeric / text_length
            score += alphanumeric_ratio * 0.2

        # 標點符號比例（10%）
        punctuation = len([c for c in text if c in '。，、；：？！""''（）【】《》'])
        if text_length > 0:
            punctuation_ratio = punctuation / text_length
            # 適當的標點符號比例（2-10%）
            if 0.02 <= punctuation_ratio <= 0.1:
                score += 0.1
            elif punctuation_ratio < 0.02:
                score += punctuation_ratio * 5  # 0-0.1

        # 特殊字符比例懲罰（10%）
        special_chars = len([c for c in text if not c.isalnum() and c not in ' \n\t。，、；：？！""''（）【】《》'])
        if text_length > 0:
            special_ratio = special_chars / text_length
            if special_ratio < 0.05:
                score += 0.1
            else:
                score += max(0, 0.1 - special_ratio)

        return min(1.0, score)

    def cleanup(self):
        """清理資源"""
        # 清理 OCR 引擎
        self._ocr_engine = None
        self._structure_engine = None

        # 清理臨時目錄
        for temp_dir in self._temp_dirs:
            try:
                if os.path.exists(temp_dir):
                    shutil.rmtree(temp_dir)
                    self.logger.debug(f"已清理臨時目錄: {temp_dir}")
            except Exception as e:
                self.logger.warning(f"清理臨時目錄失敗 {temp_dir}: {e}")

        self._temp_dirs.clear()
        self.logger.info("OCR 處理器資源已釋放")
