import os
import sys
import json
from typing import List, Dict, Any

# 添加src路徑
sys.path.append('src')

from src.processors.archaeology_processor import ArchaeologyProcessor
from src.utils.logger import logger

class PoliceExamBatchTester:
    """警察特考批量測試器"""
    
    def __init__(self):
        self.processor = ArchaeologyProcessor(use_enhanced=True)
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
        
    def test_all_categories(self) -> Dict[str, Any]:
        """測試所有13個類別"""
        
        test_results = {
            "total_categories": len(self.police_categories),
            "tested_categories": 0,
            "total_subjects": 0,
            "successful_subjects": 0,
            "total_questions_extracted": 0,
            "categories": {}
        }
        
        if not os.path.exists(self.base_dir):
            self.logger.warning(f"警察特考目錄不存在: {self.base_dir}")
            return test_results
        
        for category_name in self.police_categories:
            self.logger.info(f"=== 測試類別: {category_name} ===")
            category_dir = os.path.join(self.base_dir, category_name)
            
            if not os.path.exists(category_dir):
                self.logger.warning(f"類別目錄不存在: {category_dir}")
                continue
                
            category_result = self._test_category(category_name, category_dir)
            test_results["categories"][category_name] = category_result
            test_results["tested_categories"] += 1
            test_results["total_subjects"] += category_result["total_subjects"]
            test_results["successful_subjects"] += category_result["successful_subjects"]
            test_results["total_questions_extracted"] += category_result["total_questions_extracted"]
        
        return test_results
    
    def _test_category(self, category_name: str, category_dir: str) -> Dict[str, Any]:
        """測試單個類別"""
        
        category_result = {
            "category_name": category_name,
            "total_subjects": 0,
            "successful_subjects": 0,
            "total_questions_extracted": 0,
            "subjects": {}
        }
        
        # 遍歷類別目錄下的所有科目
        for root, dirs, files in os.walk(category_dir):
            for file in files:
                if file.endswith('.pdf') and '試題' in file:
                    subject_name = os.path.basename(os.path.dirname(os.path.join(root, file)))
                    pdf_path = os.path.join(root, file)
                    
                    self.logger.info(f"測試科目: {subject_name}")
                    category_result["total_subjects"] += 1
                    
                    try:
                        # 使用ArchaeologyProcessor處理PDF
                        result = self.processor.process_pdf(pdf_path)
                        
                        if result.get('success', False):
                            questions_count = result.get('questions_count', 0)
                            category_result["successful_subjects"] += 1
                            category_result["total_questions_extracted"] += questions_count
                            
                            category_result["subjects"][subject_name] = {
                                "success": True,
                                "questions_count": questions_count,
                                "error": None
                            }
                            
                            self.logger.info(f"✅ 成功: {subject_name} ({questions_count} 題)")
                        else:
                            error_msg = result.get('error', '未知錯誤')
                            category_result["subjects"][subject_name] = {
                                "success": False,
                                "questions_count": 0,
                                "error": error_msg
                            }
                            
                            self.logger.error(f"❌ 失敗: {subject_name} ({error_msg})")
                            
                    except Exception as e:
                        category_result["subjects"][subject_name] = {
                            "success": False,
                            "questions_count": 0,
                            "error": str(e)
                        }
                        
                        self.logger.error(f"❌ 處理失敗: {subject_name} ({str(e)})")
        
        return category_result
    
    def generate_comprehensive_report(self, test_results: Dict[str, Any]) -> str:
        """生成完整對照表報告"""
        
        report = "# 民國114年警察特考_完整對照表\n\n"
        report += f"## 總體統計\n\n"
        report += f"- 總類別數: {test_results['total_categories']}\n"
        report += f"- 已測試類別數: {test_results['tested_categories']}\n"
        report += f"- 總科目數: {test_results['total_subjects']}\n"
        report += f"- 成功處理科目數: {test_results['successful_subjects']}\n"
        report += f"- 整體成功率: {test_results['successful_subjects'] / test_results['total_subjects'] * 100:.1f}%\n"
        report += f"- 總提取題數: {test_results['total_questions_extracted']}\n\n"
        
        report += "## 各類別詳細統計\n\n"
        
        for category_name, category_data in test_results["categories"].items():
            success_rate = category_data["successful_subjects"] / category_data["total_subjects"] * 100 if category_data["total_subjects"] > 0 else 0
            
            report += f"### {category_name}\n\n"
            report += f"- 總科目數: {category_data['total_subjects']}\n"
            report += f"- 成功處理科目數: {category_data['successful_subjects']}\n"
            report += f"- 成功率: {success_rate:.1f}%\n"
            report += f"- 提取題數: {category_data['total_questions_extracted']}\n\n"
            
            report += "| 科目名稱 | 成功 | 題數 | 錯誤信息 |\n"
            report += "|---|---|---|---|\n"
            
            for subject_name, subject_data in category_data["subjects"].items():
                success_icon = "✅" if subject_data["success"] else "❌"
                questions_count = subject_data["questions_count"]
                error_msg = subject_data["error"] if subject_data["error"] else ""
                
                report += f"| {subject_name} | {success_icon} | {questions_count} | {error_msg} |\n"
            
            report += "\n"
        
        # 添加格式類型統計
        report += "## 格式類型統計\n\n"
        
        format_stats = {}
        for category_name, category_data in test_results["categories"].items():
            for subject_name, subject_data in category_data["subjects"].items():
                if subject_data["success"]:
                    # 根據科目名稱推斷格式類型
                    if "中華民國憲法與" in subject_name and "英文" in subject_name:
                        format_type = "comprehensive"
                    elif "國文" in subject_name and "作文與測驗" in subject_name:
                        format_type = "mixed_format"
                    elif "警察情境實務" in subject_name or "警察法規" in subject_name:
                        format_type = "essay"
                    else:
                        format_type = "essay"
                    
                    if format_type not in format_stats:
                        format_stats[format_type] = {"count": 0, "questions": 0}
                    
                    format_stats[format_type]["count"] += 1
                    format_stats[format_type]["questions"] += subject_data["questions_count"]
        
        report += "| 格式類型 | 科目數 | 總題數 | 平均題數 |\n"
        report += "|---|---|---|---|\n"
        
        for format_type, stats in format_stats.items():
            avg_questions = stats["questions"] / stats["count"] if stats["count"] > 0 else 0
            report += f"| {format_type} | {stats['count']} | {stats['questions']} | {avg_questions:.1f} |\n"
        
        report += "\n"
        
        # 添加問題科目分析
        report += "## 問題科目分析\n\n"
        
        failed_subjects = []
        for category_name, category_data in test_results["categories"].items():
            for subject_name, subject_data in category_data["subjects"].items():
                if not subject_data["success"]:
                    failed_subjects.append({
                        "category": category_name,
                        "subject": subject_name,
                        "error": subject_data["error"]
                    })
        
        if failed_subjects:
            report += f"發現 {len(failed_subjects)} 個問題科目:\n\n"
            report += "| 類別 | 科目 | 錯誤信息 |\n"
            report += "|---|---|---|\n"
            
            for failed in failed_subjects:
                report += f"| {failed['category']} | {failed['subject']} | {failed['error']} |\n"
        else:
            report += "✅ 所有科目處理成功，無問題科目\n"
        
        report += "\n"
        
        return report

def main():
    """主函數"""
    logger.info("=== 開始批量測試所有警察特考類別 ===")
    
    tester = PoliceExamBatchTester()
    
    # 執行測試
    test_results = tester.test_all_categories()
    
    # 保存JSON結果
    output_dir = "test_output"
    os.makedirs(output_dir, exist_ok=True)
    
    json_output_path = os.path.join(output_dir, "全部警察特考_測試結果.json")
    with open(json_output_path, 'w', encoding='utf-8') as f:
        json.dump(test_results, f, ensure_ascii=False, indent=4)
    logger.info(f"測試結果已保存至: {json_output_path}")
    
    # 生成完整對照表
    comprehensive_report = tester.generate_comprehensive_report(test_results)
    
    md_output_path = os.path.join(output_dir, "民國114年警察特考_完整對照表.md")
    with open(md_output_path, 'w', encoding='utf-8') as f:
        f.write(comprehensive_report)
    logger.info(f"完整對照表已保存至: {md_output_path}")
    
    logger.info("=== 批量測試完成 ===")

if __name__ == "__main__":
    main()
