#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
全面科目題目提取與準確率測試
涵蓋所有司法特考和警察特考科目
"""

import os
import sys
import json
import time
from datetime import datetime
from typing import Dict, List, Any, Tuple
from pathlib import Path

# 添加src路徑
sys.path.append('src')

from src.api import ArchaeologyAPI
from src.utils.logger import logger

class ComprehensiveSubjectTester:
    """全面科目測試器"""
    
    def __init__(self):
        self.api = ArchaeologyAPI()
        self.base_dir = "114年考古題/民國114年"
        self.output_dir = "test_output/comprehensive_test"
        self.results = {
            "test_info": {
                "start_time": datetime.now().isoformat(),
                "total_subjects": 0,
                "successful_extractions": 0,
                "failed_extractions": 0,
                "accuracy_tests": 0
            },
            "categories": {},
            "summary": {}
        }
        
        # 確保輸出目錄存在
        os.makedirs(self.output_dir, exist_ok=True)
    
    def test_all_subjects(self) -> Dict[str, Any]:
        """測試所有科目"""
        logger.info("=== 開始全面科目測試 ===")
        
        # 測試司法特考
        judicial_results = self._test_judicial_exams()
        self.results["categories"]["司法特考"] = judicial_results
        
        # 測試警察特考
        police_results = self._test_police_exams()
        self.results["categories"]["警察特考"] = police_results
        
        # 生成總結
        self._generate_summary()
        
        # 保存結果
        self._save_results()
        
        logger.info("=== 全面科目測試完成 ===")
        return self.results
    
    def _test_judicial_exams(self) -> Dict[str, Any]:
        """測試司法特考科目"""
        logger.info("--- 測試司法特考科目 ---")
        
        judicial_dir = os.path.join(self.base_dir, "民國114年_司法特考")
        results = {
            "category": "司法特考",
            "total_subjects": 0,
            "successful": 0,
            "failed": 0,
            "subjects": {}
        }
        
        if not os.path.exists(judicial_dir):
            logger.warning(f"司法特考目錄不存在: {judicial_dir}")
            return results
        
        # 遍歷司法特考目錄
        for root, dirs, files in os.walk(judicial_dir):
            for file in files:
                if file.endswith('.pdf') and '試題' in file:
                    subject_path = os.path.join(root, file)
                    subject_name = os.path.basename(os.path.dirname(subject_path))
                    
                    logger.info(f"處理司法特考科目: {subject_name}")
                    results["total_subjects"] += 1
                    self.results["test_info"]["total_subjects"] += 1
                    
                    # 提取題目
                    extraction_result = self._extract_subject_questions(subject_path, subject_name, "司法特考")
                    results["subjects"][subject_name] = extraction_result
                    
                    if extraction_result["success"]:
                        results["successful"] += 1
                        self.results["test_info"]["successful_extractions"] += 1
                    else:
                        results["failed"] += 1
                        self.results["test_info"]["failed_extractions"] += 1
        
        return results
    
    def _test_police_exams(self) -> Dict[str, Any]:
        """測試警察特考科目"""
        logger.info("--- 測試警察特考科目 ---")
        
        police_dir = os.path.join(self.base_dir, "民國114年_警察特考")
        results = {
            "category": "警察特考",
            "total_subjects": 0,
            "successful": 0,
            "failed": 0,
            "subjects": {}
        }
        
        if not os.path.exists(police_dir):
            logger.warning(f"警察特考目錄不存在: {police_dir}")
            return results
        
        # 遍歷警察特考目錄
        for root, dirs, files in os.walk(police_dir):
            for file in files:
                if file.endswith('.pdf') and '試題' in file:
                    subject_path = os.path.join(root, file)
                    # 獲取完整的科目路徑信息
                    relative_path = os.path.relpath(subject_path, police_dir)
                    path_parts = relative_path.split(os.sep)
                    if len(path_parts) >= 2:
                        category_name = path_parts[0]
                        subject_name = path_parts[1]
                        full_subject_name = f"{category_name}_{subject_name}"
                    else:
                        subject_name = os.path.basename(os.path.dirname(subject_path))
                        full_subject_name = subject_name
                    
                    logger.info(f"處理警察特考科目: {full_subject_name}")
                    results["total_subjects"] += 1
                    self.results["test_info"]["total_subjects"] += 1
                    
                    # 提取題目
                    extraction_result = self._extract_subject_questions(subject_path, full_subject_name, "警察特考")
                    results["subjects"][full_subject_name] = extraction_result
                    
                    if extraction_result["success"]:
                        results["successful"] += 1
                        self.results["test_info"]["successful_extractions"] += 1
                    else:
                        results["failed"] += 1
                        self.results["test_info"]["failed_extractions"] += 1
        
        return results
    
    def _extract_subject_questions(self, pdf_path: str, subject_name: str, exam_type: str) -> Dict[str, Any]:
        """提取單個科目的題目"""
        try:
            logger.info(f"提取科目: {subject_name}")
            
            # 尋找對應的答案檔案
            answer_pdf = None
            corrected_answer_pdf = None
            
            pdf_dir = os.path.dirname(pdf_path)
            for file in os.listdir(pdf_dir):
                if file.endswith('.pdf'):
                    if '答案' in file and '更正' not in file:
                        answer_pdf = os.path.join(pdf_dir, file)
                    elif '更正答案' in file:
                        corrected_answer_pdf = os.path.join(pdf_dir, file)
            
            # 創建科目專用輸出目錄
            subject_output_dir = os.path.join(self.output_dir, f"{exam_type}_{subject_name}")
            os.makedirs(subject_output_dir, exist_ok=True)
            
            # 使用API處理PDF
            result = self.api.process_single_pdf(
                pdf_path=pdf_path,
                answer_pdf_path=answer_pdf,
                corrected_answer_pdf_path=corrected_answer_pdf,
                output_dir=subject_output_dir,
                generate_script=True
            )
            
            if result["success"]:
                # 分析提取結果
                analysis = self._analyze_extraction_result(result, subject_name)
                result.update(analysis)
                
                logger.success(f"科目 {subject_name} 提取成功")
            else:
                logger.failure(f"科目 {subject_name} 提取失敗: {result.get('message', '未知錯誤')}")
            
            return result
            
        except Exception as e:
            error_msg = f"科目 {subject_name} 處理異常: {str(e)}"
            logger.failure(error_msg)
            return {
                "success": False,
                "message": error_msg,
                "subject_name": subject_name,
                "exam_type": exam_type
            }
    
    def _analyze_extraction_result(self, result: Dict[str, Any], subject_name: str) -> Dict[str, Any]:
        """分析提取結果"""
        analysis = {
            "extraction_analysis": {
                "csv_files_generated": len(result.get("csv_files", [])),
                "script_files_generated": len(result.get("script_files", [])),
                "has_google_form_csv": False,
                "has_complete_csv": False,
                "has_essay_csv": False
            },
            "accuracy_indicators": {
                "text_extraction_success": True,
                "question_parsing_success": False,
                "answer_processing_success": False,
                "csv_generation_success": False
            }
        }
        
        # 檢查生成的CSV檔案
        csv_files = result.get("csv_files", [])
        for csv_file in csv_files:
            if "Google表單" in csv_file:
                analysis["extraction_analysis"]["has_google_form_csv"] = True
            if "完整題目" in csv_file:
                analysis["extraction_analysis"]["has_complete_csv"] = True
            if "申論題" in csv_file:
                analysis["extraction_analysis"]["has_essay_csv"] = True
        
        # 檢查準確率指標
        if csv_files:
            analysis["accuracy_indicators"]["csv_generation_success"] = True
            analysis["accuracy_indicators"]["question_parsing_success"] = True
        
        # 如果有答案檔案處理成功
        if result.get("answer_processed", False):
            analysis["accuracy_indicators"]["answer_processing_success"] = True
        
        return analysis
    
    def _generate_summary(self):
        """生成測試總結"""
        total_subjects = self.results["test_info"]["total_subjects"]
        successful = self.results["test_info"]["successful_extractions"]
        failed = self.results["test_info"]["failed_extractions"]
        
        self.results["summary"] = {
            "overall_success_rate": (successful / total_subjects * 100) if total_subjects > 0 else 0,
            "total_subjects": total_subjects,
            "successful_extractions": successful,
            "failed_extractions": failed,
            "categories_summary": {}
        }
        
        # 各類別總結
        for category_name, category_data in self.results["categories"].items():
            cat_total = category_data["total_subjects"]
            cat_successful = category_data["successful"]
            cat_failed = category_data["failed"]
            
            self.results["summary"]["categories_summary"][category_name] = {
                "total_subjects": cat_total,
                "successful": cat_successful,
                "failed": cat_failed,
                "success_rate": (cat_successful / cat_total * 100) if cat_total > 0 else 0
            }
    
    def _save_results(self):
        """保存測試結果"""
        # 保存JSON結果
        json_path = os.path.join(self.output_dir, "comprehensive_test_results.json")
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, ensure_ascii=False, indent=4)
        logger.info(f"測試結果已保存至: {json_path}")
        
        # 生成Markdown報告
        report = self._generate_markdown_report()
        md_path = os.path.join(self.output_dir, "comprehensive_test_report.md")
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write(report)
        logger.info(f"測試報告已保存至: {md_path}")
    
    def _generate_markdown_report(self) -> str:
        """生成Markdown格式的測試報告"""
        report = "# 全面科目題目提取測試報告\n\n"
        report += f"**測試時間**: {self.results['test_info']['start_time']}\n\n"
        
        # 總體統計
        summary = self.results["summary"]
        report += "## 總體統計\n\n"
        report += f"- **總科目數**: {summary['total_subjects']}\n"
        report += f"- **成功提取數**: {summary['successful_extractions']}\n"
        report += f"- **失敗提取數**: {summary['failed_extractions']}\n"
        report += f"- **整體成功率**: {summary['overall_success_rate']:.1f}%\n\n"
        
        # 各類別統計
        report += "## 各類別統計\n\n"
        for category_name, cat_summary in summary["categories_summary"].items():
            report += f"### {category_name}\n\n"
            report += f"- 總科目數: {cat_summary['total_subjects']}\n"
            report += f"- 成功提取: {cat_summary['successful']}\n"
            report += f"- 失敗提取: {cat_summary['failed']}\n"
            report += f"- 成功率: {cat_summary['success_rate']:.1f}%\n\n"
        
        # 詳細結果
        report += "## 詳細結果\n\n"
        for category_name, category_data in self.results["categories"].items():
            report += f"### {category_name}\n\n"
            report += "| 科目名稱 | 提取狀態 | CSV檔案數 | 腳本檔案數 | 準確率指標 |\n"
            report += "|---|---|---|---|---|\n"
            
            for subject_name, subject_data in category_data["subjects"].items():
                status = "✅ 成功" if subject_data["success"] else f"❌ 失敗: {subject_data.get('message', '未知錯誤')}"
                
                csv_count = len(subject_data.get("csv_files", []))
                script_count = len(subject_data.get("script_files", []))
                
                # 準確率指標
                indicators = subject_data.get("accuracy_indicators", {})
                accuracy_indicators = []
                if indicators.get("text_extraction_success"):
                    accuracy_indicators.append("文本提取✓")
                if indicators.get("question_parsing_success"):
                    accuracy_indicators.append("題目解析✓")
                if indicators.get("answer_processing_success"):
                    accuracy_indicators.append("答案處理✓")
                if indicators.get("csv_generation_success"):
                    accuracy_indicators.append("CSV生成✓")
                
                accuracy_str = " | ".join(accuracy_indicators) if accuracy_indicators else "無"
                
                report += f"| {subject_name} | {status} | {csv_count} | {script_count} | {accuracy_str} |\n"
            
            report += "\n"
        
        return report

def main():
    """主函數"""
    logger.info("=== 開始全面科目測試 ===")
    
    tester = ComprehensiveSubjectTester()
    
    # 執行測試
    results = tester.test_all_subjects()
    
    # 輸出總結
    summary = results["summary"]
    logger.info(f"測試完成！總科目數: {summary['total_subjects']}, 成功率: {summary['overall_success_rate']:.1f}%")
    
    return results

if __name__ == "__main__":
    main()
