import os
import sys
import json
import re
from typing import List, Dict, Any
from pathlib import Path

# 添加src路徑
sys.path.append('src')

from src.core.pdf_processor import PDFProcessor
from src.utils.logger import logger

class PoliceExamBatchAnalyzer:
    """警察特考批量分析器"""
    
    def __init__(self):
        self.pdf_processor = PDFProcessor()
        self.logger = logger
        
        # 13個警察特考類別
        self.police_categories = [
            "交通警察_交通",
            "公共安全", 
            "刑事警察",
            "刑事鑑識",
            "國境警察",
            "外事警察",
            "水上警察",
            "消防警察",
            "犯罪防治",
            "行政管理",
            "行政警察",
            "警察法制",
            "資訊管理"
        ]
        
        self.base_dir = "114年考古題/民國114年/民國114年_警察特考"
        
    def analyze_all_categories(self) -> Dict[str, Any]:
        """分析所有13個類別"""
        
        analysis_results = {
            "total_categories": len(self.police_categories),
            "analyzed_categories": 0,
            "total_subjects": 0,
            "successful_subjects": 0,
            "categories": {}
        }
        
        if not os.path.exists(self.base_dir):
            self.logger.warning(f"警察特考目錄不存在: {self.base_dir}")
            return analysis_results
        
        for category_name in self.police_categories:
            self.logger.info(f"=== 分析類別: {category_name} ===")
            category_dir = os.path.join(self.base_dir, category_name)
            
            if not os.path.exists(category_dir):
                self.logger.warning(f"類別目錄不存在: {category_dir}")
                continue
                
            category_result = self._analyze_category(category_name, category_dir)
            analysis_results["categories"][category_name] = category_result
            analysis_results["analyzed_categories"] += 1
            analysis_results["total_subjects"] += category_result["total_subjects"]
            analysis_results["successful_subjects"] += category_result["successful_subjects"]
        
        return analysis_results
    
    def _analyze_category(self, category_name: str, category_dir: str) -> Dict[str, Any]:
        """分析單個類別"""
        
        category_result = {
            "category_name": category_name,
            "total_subjects": 0,
            "successful_subjects": 0,
            "subjects": {}
        }
        
        # 遍歷類別目錄下的所有科目
        for root, dirs, files in os.walk(category_dir):
            for file in files:
                if file.endswith('.pdf') and '試題' in file:
                    subject_name = os.path.basename(os.path.dirname(os.path.join(root, file)))
                    pdf_path = os.path.join(root, file)
                    
                    self.logger.info(f"分析科目: {subject_name}")
                    category_result["total_subjects"] += 1
                    
                    try:
                        # 提取PDF文本
                        text = self.pdf_processor.extract_text(pdf_path)
                        if text:
                            # 分析PDF結構
                            structure_analysis = self._analyze_pdf_structure(text, pdf_path)
                            structure_analysis["success"] = True
                            category_result["successful_subjects"] += 1
                        else:
                            structure_analysis = {
                                "success": False,
                                "error": "PDF文本提取失敗"
                            }
                    except Exception as e:
                        structure_analysis = {
                            "success": False,
                            "error": str(e)
                        }
                    
                    category_result["subjects"][subject_name] = structure_analysis
        
        return category_result
    
    def _analyze_pdf_structure(self, text: str, pdf_path: str) -> Dict[str, Any]:
        """分析PDF結構特徵"""
        
        analysis = {
            "pdf_path": pdf_path,
            "text_length": len(text),
            "format_indicators": {},
            "question_indicators": {},
            "estimated_questions": 0,
            "format_type": "unknown"
        }
        
        # 檢測格式指示器
        format_indicators = {
            "essay_part": "甲、申論題部分" in text or "申論題" in text,
            "test_part": "乙、測驗題部分" in text or "測驗題" in text,
            "composition_part": "作文部分" in text or "作文" in text,
            "mixed_format": "作文部分" in text and "測驗部分" in text,
            "comprehensive_format": "甲、申論題部分" in text and "乙、測驗題部分" in text,
            "embedded_choice": "請依下文回答第" in text and any(symbol in text for symbol in ['\ue18c', '\ue18d', '\ue18e', '\ue18f']),
            "question_groups": "請依下文回答第" in text and "題至第" in text
        }
        
        analysis["format_indicators"] = format_indicators
        
        # 檢測題目指示器
        question_indicators = {
            "standard_questions": len(re.findall(r'^\d+\s+', text, re.MULTILINE)),
            "essay_questions": len(re.findall(r'^\d+\.\s*', text, re.MULTILINE)),
            "group_questions": len(re.findall(r'請依下文回答第\d+題至第\d+題', text)),
            "composition_questions": len(re.findall(r'作文|論述', text))
        }
        
        analysis["question_indicators"] = question_indicators
        
        # 估算題目數量
        estimated_questions = 0
        
        # 標準選擇題 (1-50題)
        standard_count = len(re.findall(r'^(\d+)\s+', text, re.MULTILINE))
        if standard_count > 0:
            estimated_questions += min(standard_count, 50)
        
        # 申論題
        essay_count = len(re.findall(r'^\d+\.\s*', text, re.MULTILINE))
        if essay_count > 0:
            estimated_questions += essay_count
        
        # 題組題 (51-60題)
        group_matches = re.findall(r'請依下文回答第(\d+)題至第(\d+)題', text)
        for start, end in group_matches:
            estimated_questions += int(end) - int(start) + 1
        
        # 作文題
        if "作文" in text:
            estimated_questions += 1
        
        analysis["estimated_questions"] = estimated_questions
        
        # 判斷格式類型
        if format_indicators["comprehensive_format"]:
            analysis["format_type"] = "comprehensive"
        elif format_indicators["mixed_format"]:
            analysis["format_type"] = "mixed_format"
        elif format_indicators["embedded_choice"]:
            analysis["format_type"] = "embedded_choice"
        elif format_indicators["essay_part"]:
            analysis["format_type"] = "essay"
        elif format_indicators["test_part"]:
            analysis["format_type"] = "standard_choice"
        else:
            analysis["format_type"] = "unknown"
        
        return analysis
    
    def generate_statistics_report(self, analysis_results: Dict[str, Any]) -> str:
        """生成統計報告"""
        
        report = "# 民國114年警察特考_統計報告\n\n"
        report += f"## 總體統計\n\n"
        report += f"- 總類別數: {analysis_results['total_categories']}\n"
        report += f"- 已分析類別數: {analysis_results['analyzed_categories']}\n"
        report += f"- 總科目數: {analysis_results['total_subjects']}\n"
        report += f"- 成功分析科目數: {analysis_results['successful_subjects']}\n"
        report += f"- 整體成功率: {analysis_results['successful_subjects'] / analysis_results['total_subjects'] * 100:.1f}%\n\n"
        
        report += "## 各類別詳細統計\n\n"
        
        for category_name, category_data in analysis_results["categories"].items():
            report += f"### {category_name}\n\n"
            report += f"- 總科目數: {category_data['total_subjects']}\n"
            report += f"- 成功分析科目數: {category_data['successful_subjects']}\n"
            report += f"- 成功率: {category_data['successful_subjects'] / category_data['total_subjects'] * 100:.1f}%\n\n"
            
            report += "| 科目名稱 | 格式類型 | 預估題數 | 狀態 |\n"
            report += "|---|---|---|---|\n"
            
            for subject_name, subject_data in category_data["subjects"].items():
                if subject_data["success"]:
                    format_type = subject_data.get("format_type", "unknown")
                    estimated_questions = subject_data.get("estimated_questions", 0)
                    status = "✅ 成功"
                else:
                    format_type = "unknown"
                    estimated_questions = 0
                    status = f"❌ {subject_data.get('error', '未知錯誤')}"
                
                report += f"| {subject_name} | {format_type} | {estimated_questions} | {status} |\n"
            
            report += "\n"
        
        return report

def main():
    """主函數"""
    logger.info("=== 開始批量分析所有警察特考類別 ===")
    
    analyzer = PoliceExamBatchAnalyzer()
    
    # 執行分析
    analysis_results = analyzer.analyze_all_categories()
    
    # 保存JSON結果
    output_dir = "test_output"
    os.makedirs(output_dir, exist_ok=True)
    
    json_output_path = os.path.join(output_dir, "全部警察特考_結構分析.json")
    with open(json_output_path, 'w', encoding='utf-8') as f:
        json.dump(analysis_results, f, ensure_ascii=False, indent=4)
    logger.info(f"結構分析結果已保存至: {json_output_path}")
    
    # 生成統計報告
    statistics_report = analyzer.generate_statistics_report(analysis_results)
    
    md_output_path = os.path.join(output_dir, "全部警察特考_統計報告.md")
    with open(md_output_path, 'w', encoding='utf-8') as f:
        f.write(statistics_report)
    logger.info(f"統計報告已保存至: {md_output_path}")
    
    logger.info("=== 批量分析完成 ===")

if __name__ == "__main__":
    main()
