#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
考古題處理系統API
提供統一的接口供外部調用
"""

import os
import argparse
from typing import Dict, Any, Optional
from .processors.archaeology_processor import ArchaeologyProcessor
from .core.google_script_generator import GoogleScriptGenerator
from .utils.logger import logger
from .utils.config import config_manager


class ArchaeologyAPI:
    """考古題處理系統API"""
    
    def __init__(self):
        self.logger = logger
        self.processor = ArchaeologyProcessor()
        self.script_generator = GoogleScriptGenerator()
    
    def process_single_pdf(self, pdf_path: str, 
                          answer_pdf_path: Optional[str] = None,
                          corrected_answer_pdf_path: Optional[str] = None,
                          output_dir: str = "output",
                          generate_script: bool = True) -> Dict[str, Any]:
        """
        處理單一PDF檔案
        
        Args:
            pdf_path: PDF檔案路徑
            answer_pdf_path: 答案PDF檔案路徑（可選）
            corrected_answer_pdf_path: 更正答案PDF檔案路徑（可選）
            output_dir: 輸出目錄
            generate_script: 是否生成Google Apps Script
            
        Returns:
            處理結果字典
        """
        try:
            self.logger.info(f"開始處理單一PDF: {pdf_path}")
            
            # 處理PDF
            result = self.processor.process_pdf(
                pdf_path, answer_pdf_path, corrected_answer_pdf_path, output_dir
            )
            
            if not result['success']:
                return result
            
            # 生成Google Apps Script（如果需要）
            if generate_script:
                try:
                    # 尋找Google表單CSV檔案
                    google_csv = None
                    for csv_file in result['csv_files']:
                        if 'Google表單' in csv_file:
                            google_csv = csv_file
                            break
                    
                    if google_csv:
                        script_path = os.path.join(output_dir, f"{os.path.splitext(os.path.basename(pdf_path))[0]}_GoogleAppsScript.js")
                        self.script_generator.generate_script(google_csv, script_path)
                        result['script_file'] = script_path
                        self.logger.success(f"Google Apps Script已生成: {script_path}")
                    else:
                        self.logger.warning("未找到Google表單CSV檔案，跳過Script生成")
                except Exception as e:
                    self.logger.warning(f"Google Apps Script生成失敗: {e}")
            
            return result
            
        except Exception as e:
            error_msg = f"單一PDF處理失敗: {e}"
            self.logger.failure(error_msg)
            return {'success': False, 'message': error_msg}
    
    def process_directory(self, input_dir: str, 
                         output_dir: str = "output",
                         generate_script: bool = True) -> Dict[str, Any]:
        """
        處理目錄中的所有PDF檔案
        
        Args:
            input_dir: 輸入目錄
            output_dir: 輸出目錄
            generate_script: 是否生成Google Apps Script
            
        Returns:
            處理結果字典
        """
        try:
            self.logger.info(f"開始處理目錄: {input_dir}")
            
            # 處理目錄
            result = self.processor.process_directory(input_dir, output_dir)
            
            if not result['success']:
                return result
            
            # 生成Google Apps Script（如果需要）
            if generate_script:
                try:
                    script_files = []
                    for file_result in result['results']:
                        if file_result['success']:
                            # 尋找Google表單CSV檔案
                            google_csv = None
                            for csv_file in file_result['csv_files']:
                                if 'Google表單' in csv_file:
                                    google_csv = csv_file
                                    break
                            
                            if google_csv:
                                script_path = google_csv.replace('.csv', '_GoogleAppsScript.js')
                                self.script_generator.generate_script(google_csv, script_path)
                                script_files.append(script_path)
                    
                    result['script_files'] = script_files
                    self.logger.success(f"已生成 {len(script_files)} 個Google Apps Script檔案")
                except Exception as e:
                    self.logger.warning(f"Google Apps Script生成失敗: {e}")
            
            return result
            
        except Exception as e:
            error_msg = f"目錄處理失敗: {e}"
            self.logger.failure(error_msg)
            return {'success': False, 'message': error_msg}
    
    def generate_script_from_csv(self, csv_path: str, 
                                output_path: Optional[str] = None) -> str:
        """
        從CSV檔案生成Google Apps Script
        
        Args:
            csv_path: CSV檔案路徑
            output_path: 輸出檔案路徑（可選）
            
        Returns:
            生成的JavaScript檔案路徑
        """
        try:
            if output_path is None:
                output_path = csv_path.replace('.csv', '_GoogleAppsScript.js')
            
            self.logger.info(f"從CSV生成Google Apps Script: {csv_path}")
            
            script_path = self.script_generator.generate_script(csv_path, output_path)
            
            self.logger.success(f"Google Apps Script生成完成: {script_path}")
            return script_path
            
        except Exception as e:
            error_msg = f"Google Apps Script生成失敗: {e}"
            self.logger.failure(error_msg)
            raise


def main():
    """命令行接口"""
    parser = argparse.ArgumentParser(description='考古題處理系統')
    parser.add_argument('input', help='輸入PDF檔案或目錄路徑')
    parser.add_argument('-o', '--output', default='output', help='輸出目錄（預設: output）')
    parser.add_argument('-a', '--answer', help='答案PDF檔案路徑')
    parser.add_argument('-c', '--corrected', help='更正答案PDF檔案路徑')
    parser.add_argument('--no-script', action='store_true', help='不生成Google Apps Script')
    parser.add_argument('--config', help='配置檔案路徑')
    
    args = parser.parse_args()
    
    # 載入配置（如果指定）
    if args.config:
        from .utils.config import ConfigManager
        config_manager = ConfigManager(args.config)
    
    # 建立API實例
    api = ArchaeologyAPI()
    
    # 檢查輸入路徑
    if not os.path.exists(args.input):
        logger.failure(f"輸入路徑不存在: {args.input}")
        return 1
    
    try:
        if os.path.isfile(args.input):
            # 處理單一檔案
            result = api.process_single_pdf(
                args.input, 
                args.answer, 
                args.corrected, 
                args.output,
                not args.no_script
            )
        else:
            # 處理目錄
            result = api.process_directory(
                args.input, 
                args.output,
                not args.no_script
            )
        
        if result['success']:
            logger.success("處理完成！")
            print(f"輸出目錄: {result['output_dir']}")
            if 'csv_files' in result:
                print(f"CSV檔案: {len(result['csv_files'])} 個")
            if 'script_files' in result:
                print(f"Script檔案: {len(result['script_files'])} 個")
            return 0
        else:
            logger.failure(f"處理失敗: {result['message']}")
            return 1
            
    except Exception as e:
        logger.failure(f"執行失敗: {e}")
        return 1


if __name__ == '__main__':
    exit(main())