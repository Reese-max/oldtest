#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
準確率分析腳本
分析題目提取的準確率和質量
"""

import os
import json
import csv
from typing import Dict, List, Any, Tuple
from pathlib import Path

class AccuracyAnalyzer:
    """準確率分析器"""
    
    def __init__(self, results_file: str):
        self.results_file = results_file
        self.results = self._load_results()
        self.analysis = {
            "overall_accuracy": 0.0,
            "category_accuracy": {},
            "subject_accuracy": {},
            "quality_metrics": {},
            "recommendations": []
        }
    
    def _load_results(self) -> Dict[str, Any]:
        """載入測試結果"""
        with open(self.results_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def analyze_overall_accuracy(self) -> float:
        """分析整體準確率"""
        total_subjects = self.results["test_info"]["total_subjects"]
        successful = self.results["test_info"]["successful_extractions"]
        
        accuracy = (successful / total_subjects * 100) if total_subjects > 0 else 0
        self.analysis["overall_accuracy"] = accuracy
        return accuracy
    
    def analyze_category_accuracy(self) -> Dict[str, float]:
        """分析各類別準確率"""
        category_accuracy = {}
        
        for category_name, category_data in self.results["categories"].items():
            total = category_data["total_subjects"]
            successful = category_data["successful"]
            accuracy = (successful / total * 100) if total > 0 else 0
            category_accuracy[category_name] = accuracy
        
        self.analysis["category_accuracy"] = category_accuracy
        return category_accuracy
    
    def analyze_subject_quality(self) -> Dict[str, Dict[str, Any]]:
        """分析各科目質量指標"""
        subject_quality = {}
        
        for category_name, category_data in self.results["categories"].items():
            for subject_name, subject_data in category_data["subjects"].items():
                if subject_data["success"]:
                    quality_metrics = self._calculate_quality_metrics(subject_data)
                    subject_quality[f"{category_name}_{subject_name}"] = quality_metrics
        
        self.analysis["subject_accuracy"] = subject_quality
        return subject_quality
    
    def _calculate_quality_metrics(self, subject_data: Dict[str, Any]) -> Dict[str, Any]:
        """計算科目質量指標"""
        metrics = {
            "extraction_success": True,
            "csv_generation_success": False,
            "script_generation_success": False,
            "answer_processing_success": False,
            "question_count": 0,
            "answer_count": 0,
            "quality_score": 0.0
        }
        
        # CSV生成成功指標
        csv_files = subject_data.get("csv_files", [])
        if len(csv_files) >= 4:  # 標準4個CSV檔案
            metrics["csv_generation_success"] = True
        
        # 腳本生成成功指標
        if "script_file" in subject_data and subject_data["script_file"]:
            metrics["script_generation_success"] = True
        
        # 答案處理成功指標
        answers_count = subject_data.get("answers_count", 0)
        if answers_count > 0:
            metrics["answer_processing_success"] = True
            metrics["answer_count"] = answers_count
        
        # 題目數量
        questions_count = subject_data.get("questions_count", 0)
        metrics["question_count"] = questions_count
        
        # 計算質量分數
        quality_score = 0
        if metrics["extraction_success"]:
            quality_score += 25
        if metrics["csv_generation_success"]:
            quality_score += 25
        if metrics["script_generation_success"]:
            quality_score += 25
        if metrics["answer_processing_success"]:
            quality_score += 25
        
        metrics["quality_score"] = quality_score
        return metrics
    
    def analyze_quality_metrics(self) -> Dict[str, Any]:
        """分析整體質量指標"""
        quality_metrics = {
            "high_quality_subjects": 0,  # 質量分數 >= 75
            "medium_quality_subjects": 0,  # 質量分數 50-74
            "low_quality_subjects": 0,  # 質量分數 < 50
            "total_questions_extracted": 0,
            "total_answers_processed": 0,
            "csv_generation_rate": 0.0,
            "script_generation_rate": 0.0,
            "answer_processing_rate": 0.0
        }
        
        total_subjects = 0
        csv_success_count = 0
        script_success_count = 0
        answer_success_count = 0
        
        for category_name, category_data in self.results["categories"].items():
            for subject_name, subject_data in category_data["subjects"].items():
                if subject_data["success"]:
                    total_subjects += 1
                    
                    # 統計CSV生成
                    csv_files = subject_data.get("csv_files", [])
                    if len(csv_files) >= 4:
                        csv_success_count += 1
                    
                    # 統計腳本生成
                    if "script_file" in subject_data and subject_data["script_file"]:
                        script_success_count += 1
                    
                    # 統計答案處理
                    if subject_data.get("answers_count", 0) > 0:
                        answer_success_count += 1
                    
                    # 統計題目數量
                    questions_count = subject_data.get("questions_count", 0)
                    quality_metrics["total_questions_extracted"] += questions_count
                    
                    # 統計答案數量
                    answers_count = subject_data.get("answers_count", 0)
                    quality_metrics["total_answers_processed"] += answers_count
                    
                    # 質量分數分類
                    quality_score = self._calculate_quality_metrics(subject_data)["quality_score"]
                    if quality_score >= 75:
                        quality_metrics["high_quality_subjects"] += 1
                    elif quality_score >= 50:
                        quality_metrics["medium_quality_subjects"] += 1
                    else:
                        quality_metrics["low_quality_subjects"] += 1
        
        # 計算比率
        if total_subjects > 0:
            quality_metrics["csv_generation_rate"] = (csv_success_count / total_subjects) * 100
            quality_metrics["script_generation_rate"] = (script_success_count / total_subjects) * 100
            quality_metrics["answer_processing_rate"] = (answer_success_count / total_subjects) * 100
        
        self.analysis["quality_metrics"] = quality_metrics
        return quality_metrics
    
    def generate_recommendations(self) -> List[str]:
        """生成改進建議"""
        recommendations = []
        
        # 基於整體準確率
        overall_accuracy = self.analysis["overall_accuracy"]
        if overall_accuracy >= 95:
            recommendations.append("✅ 整體準確率優秀 (≥95%)，系統表現良好")
        elif overall_accuracy >= 90:
            recommendations.append("⚠️ 整體準確率良好 (90-95%)，可進一步優化")
        else:
            recommendations.append("❌ 整體準確率需要改進 (<90%)，建議檢查系統配置")
        
        # 基於質量指標
        quality_metrics = self.analysis["quality_metrics"]
        
        if quality_metrics["csv_generation_rate"] < 100:
            recommendations.append(f"📊 CSV生成率 {quality_metrics['csv_generation_rate']:.1f}%，建議檢查CSV生成邏輯")
        
        if quality_metrics["script_generation_rate"] < 100:
            recommendations.append(f"📝 腳本生成率 {quality_metrics['script_generation_rate']:.1f}%，建議檢查Google Apps Script生成")
        
        if quality_metrics["answer_processing_rate"] < 80:
            recommendations.append(f"🔍 答案處理率 {quality_metrics['answer_processing_rate']:.1f}%，建議改進答案提取算法")
        
        # 基於科目質量分布
        high_quality = quality_metrics["high_quality_subjects"]
        medium_quality = quality_metrics["medium_quality_subjects"]
        low_quality = quality_metrics["low_quality_subjects"]
        total = high_quality + medium_quality + low_quality
        
        if total > 0:
            high_quality_rate = (high_quality / total) * 100
            if high_quality_rate >= 80:
                recommendations.append("🌟 高質量科目比例優秀，系統穩定性良好")
            elif high_quality_rate >= 60:
                recommendations.append("📈 高質量科目比例良好，可進一步提升")
            else:
                recommendations.append("🔧 高質量科目比例偏低，建議優化處理流程")
        
        self.analysis["recommendations"] = recommendations
        return recommendations
    
    def generate_report(self) -> str:
        """生成分析報告"""
        report = "# 考古題提取系統準確率分析報告\n\n"
        
        # 整體統計
        report += "## 整體統計\n\n"
        report += f"- **總科目數**: {self.results['test_info']['total_subjects']}\n"
        report += f"- **成功提取數**: {self.results['test_info']['successful_extractions']}\n"
        report += f"- **失敗提取數**: {self.results['test_info']['failed_extractions']}\n"
        report += f"- **整體準確率**: {self.analysis['overall_accuracy']:.1f}%\n\n"
        
        # 各類別準確率
        report += "## 各類別準確率\n\n"
        for category, accuracy in self.analysis["category_accuracy"].items():
            report += f"- **{category}**: {accuracy:.1f}%\n"
        report += "\n"
        
        # 質量指標
        quality_metrics = self.analysis["quality_metrics"]
        report += "## 質量指標分析\n\n"
        report += f"- **高質量科目數**: {quality_metrics['high_quality_subjects']}\n"
        report += f"- **中等質量科目數**: {quality_metrics['medium_quality_subjects']}\n"
        report += f"- **低質量科目數**: {quality_metrics['low_quality_subjects']}\n"
        report += f"- **總提取題目數**: {quality_metrics['total_questions_extracted']}\n"
        report += f"- **總處理答案數**: {quality_metrics['total_answers_processed']}\n"
        report += f"- **CSV生成率**: {quality_metrics['csv_generation_rate']:.1f}%\n"
        report += f"- **腳本生成率**: {quality_metrics['script_generation_rate']:.1f}%\n"
        report += f"- **答案處理率**: {quality_metrics['answer_processing_rate']:.1f}%\n\n"
        
        # 改進建議
        report += "## 改進建議\n\n"
        for recommendation in self.analysis["recommendations"]:
            report += f"- {recommendation}\n"
        report += "\n"
        
        # 詳細科目分析
        report += "## 詳細科目分析\n\n"
        report += "| 科目名稱 | 準確率 | 題目數 | 答案數 | 質量分數 | 狀態 |\n"
        report += "|---|---|---|---|---|---|\n"
        
        for subject_key, quality_metrics in self.analysis["subject_accuracy"].items():
            status = "✅ 優秀" if quality_metrics["quality_score"] >= 75 else "⚠️ 良好" if quality_metrics["quality_score"] >= 50 else "❌ 需改進"
            report += f"| {subject_key} | {quality_metrics['quality_score']:.0f}% | {quality_metrics['question_count']} | {quality_metrics['answer_count']} | {quality_metrics['quality_score']:.0f} | {status} |\n"
        
        return report
    
    def save_analysis(self, output_file: str):
        """保存分析結果"""
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.analysis, f, ensure_ascii=False, indent=4)

def main():
    """主函數"""
    results_file = "test_output/comprehensive_test/comprehensive_test_results.json"
    
    if not os.path.exists(results_file):
        print(f"結果檔案不存在: {results_file}")
        return
    
    print("=== 開始準確率分析 ===")
    
    analyzer = AccuracyAnalyzer(results_file)
    
    # 執行分析
    overall_accuracy = analyzer.analyze_overall_accuracy()
    category_accuracy = analyzer.analyze_category_accuracy()
    subject_quality = analyzer.analyze_subject_quality()
    quality_metrics = analyzer.analyze_quality_metrics()
    recommendations = analyzer.generate_recommendations()
    
    # 生成報告
    report = analyzer.generate_report()
    
    # 保存結果
    output_dir = "test_output/accuracy_analysis"
    os.makedirs(output_dir, exist_ok=True)
    
    # 保存分析結果
    analysis_file = os.path.join(output_dir, "accuracy_analysis.json")
    analyzer.save_analysis(analysis_file)
    print(f"分析結果已保存至: {analysis_file}")
    
    # 保存報告
    report_file = os.path.join(output_dir, "accuracy_analysis_report.md")
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    print(f"分析報告已保存至: {report_file}")
    
    # 輸出總結
    print(f"\n=== 準確率分析完成 ===")
    print(f"整體準確率: {overall_accuracy:.1f}%")
    print(f"高質量科目: {quality_metrics['high_quality_subjects']}")
    print(f"總提取題目: {quality_metrics['total_questions_extracted']}")
    print(f"總處理答案: {quality_metrics['total_answers_processed']}")

if __name__ == "__main__":
    main()
