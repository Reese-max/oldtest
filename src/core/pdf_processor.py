#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF處理器
負責從PDF檔案中提取文字內容
"""

import os
import pdfplumber
from typing import Optional, List
from ..utils.logger import logger
from ..utils.exceptions import PDFProcessingError


class PDFProcessor:
    """PDF處理器"""
    
    def __init__(self):
        self.logger = logger
    
    def extract_text(self, pdf_path: str, max_pages: int = 200) -> str:
        """
        從PDF檔案中提取文字內容

        Args:
            pdf_path: PDF檔案路徑
            max_pages: 最大處理頁數，預設200頁（防止大文件記憶體溢出）

        Returns:
            提取的文字內容

        Raises:
            PDFProcessingError: PDF處理失敗時拋出
        """
        if not os.path.exists(pdf_path):
            raise PDFProcessingError(f"PDF檔案不存在: {pdf_path}")

        try:
            self.logger.info(f"開始處理PDF檔案: {pdf_path}")

            with pdfplumber.open(pdf_path) as pdf:
                text = ""
                total_pages = len(pdf.pages)

                # 警告大文件
                if total_pages > max_pages:
                    self.logger.warning(
                        f"⚠️  PDF檔案過大（{total_pages} 頁），僅處理前 {max_pages} 頁"
                    )

                # 限制處理頁數
                pages_to_process = min(total_pages, max_pages)

                for page_num, page in enumerate(pdf.pages[:pages_to_process], 1):
                    try:
                        page_text = page.extract_text()
                        if page_text:
                            # 處理特殊 Unicode 字符，避免編碼錯誤
                            try:
                                page_text = page_text.encode('utf-8', errors='ignore').decode('utf-8')
                                # 移除常見的問題字符
                                page_text = page_text.replace('\x00', '').replace('\ufeff', '')
                            except UnicodeError as ue:
                                self.logger.warning(f"第 {page_num} 頁 Unicode 清理失敗: {ue}")
                            text += page_text + "\n"

                        # 每處理50頁釋放一次記憶體
                        if page_num % 50 == 0:
                            import gc
                            gc.collect()
                            self.logger.debug(f"已處理 {page_num} 頁，觸發記憶體清理")

                        self.logger.debug(f"處理第 {page_num}/{pages_to_process} 頁")
                    except Exception as e:
                        self.logger.warning(f"第 {page_num} 頁處理失敗: {e}")
                        continue

                self.logger.success(
                    f"✅ PDF文字提取完成，共處理 {pages_to_process}/{total_pages} 頁，{len(text)} 字元"
                )
                return text

        except Exception as e:
            error_msg = f"PDF處理失敗: {e}"
            self.logger.failure(error_msg)
            raise PDFProcessingError(error_msg) from e
    
    def extract_text_from_pages(self, pdf_path: str, page_numbers: List[int]) -> str:
        """
        從指定頁面提取文字內容
        
        Args:
            pdf_path: PDF檔案路徑
            page_numbers: 要提取的頁面編號列表
            
        Returns:
            提取的文字內容
        """
        if not os.path.exists(pdf_path):
            raise PDFProcessingError(f"PDF檔案不存在: {pdf_path}")
        
        try:
            self.logger.info(f"從指定頁面提取文字: {page_numbers}")
            
            with pdfplumber.open(pdf_path) as pdf:
                text = ""
                total_pages = len(pdf.pages)
                
                for page_num in page_numbers:
                    if 1 <= page_num <= total_pages:
                        try:
                            page_text = pdf.pages[page_num - 1].extract_text()
                            if page_text:
                                # 處理特殊 Unicode 字符，避免編碼錯誤
                                try:
                                    page_text = page_text.encode('utf-8', errors='ignore').decode('utf-8')
                                    # 移除常見的問題字符
                                    page_text = page_text.replace('\x00', '').replace('\ufeff', '')
                                except UnicodeError as ue:
                                    self.logger.warning(f"第 {page_num} 頁 Unicode 清理失敗: {ue}")
                                text += page_text + "\n"
                            self.logger.debug(f"處理第 {page_num} 頁")
                        except Exception as e:
                            self.logger.warning(f"第 {page_num} 頁處理失敗: {e}")
                    else:
                        self.logger.warning(f"頁面編號 {page_num} 超出範圍 (1-{total_pages})")
                
                self.logger.success(f"指定頁面文字提取完成，{len(text)} 字元")
                return text
                
        except Exception as e:
            error_msg = f"指定頁面PDF處理失敗: {e}"
            self.logger.failure(error_msg)
            raise PDFProcessingError(error_msg) from e
    
    def get_page_count(self, pdf_path: str) -> int:
        """
        取得PDF頁數
        
        Args:
            pdf_path: PDF檔案路徑
            
        Returns:
            PDF頁數
        """
        if not os.path.exists(pdf_path):
            raise PDFProcessingError(f"PDF檔案不存在: {pdf_path}")
        
        try:
            with pdfplumber.open(pdf_path) as pdf:
                page_count = len(pdf.pages)
                self.logger.info(f"PDF頁數: {page_count}")
                return page_count
        except Exception as e:
            error_msg = f"取得PDF頁數失敗: {e}"
            self.logger.failure(error_msg)
            raise PDFProcessingError(error_msg) from e