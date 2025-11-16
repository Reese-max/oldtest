#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分析114年監獄官8個科目PDF的文本結構和格式特徵
"""

import os
import sys
import json
import re
from typing import Dict, List, Any
from pathlib import Path

# 添加src路徑
sys.path.append('src')

from src.core.pdf_processor import PDFProcessor
from src.utils.logger import logger

class PrisonExamStructureAnalyzer:
    """監獄官考試PDF結構分析器"""
    
    def __init__(self):
        self.pdf_processor = PDFProcessor()
        self.logger = logger
        
    def analyze_prison_exam_pdfs(self) -> Dict[str, Any]:
        """分析監獄官考試PDF結構"""
        
        # 監獄官考試科目列表（基於實際的8個科目）
        prison_subjects = [
            "法學知識與英文（包括中華民國憲法、法學緒論、英文）",
            "國文（作文與測驗）", 
            "監獄學",
            "監獄行刑法與羈押法",
            "刑法與少年事件處理法",
            "犯罪學與再犯預測",
            "刑事政策",
            "諮商與矯正輔導"
        ]
        
        analysis_results = {
            "total_subjects": len(prison_subjects),
            "analyzed_subjects": 0,
            "successful_analysis": 0,
            "subjects": {}
        }
        
        base_dir = "114年考古題/民國114年/民國114年_司法特考/監獄官"
        
        if not os.path.exists(base_dir):
            self.logger.warning(f"監獄官目錄不存在: {base_dir}")
            return analysis_results
        
        for subject in prison_subjects:
            self.logger.info(f"分析科目: {subject}")
            
            subject_dir = os.path.join(base_dir, subject)
            if not os.path.exists(subject_dir):
                self.logger.warning(f"科目目錄不存在: {subject_dir}")
                continue
                
            analysis_results["analyzed_subjects"] += 1
            
            # 查找試題PDF
            pdf_path = None
            for file in os.listdir(subject_dir):
                if file.endswith('.pdf') and '試題' in file:
                    pdf_path = os.path.join(subject_dir, file)
                    break
            
            if not pdf_path:
                self.logger.warning(f"未找到試題PDF: {subject}")
                continue
            
            try:
                # 提取文本
                text = self.pdf_processor.extract_text(pdf_path)
                if not text:
                    self.logger.warning(f"無法提取文本: {subject}")
                    continue
                
                # 分析結構特徵
                structure_features = self._analyze_structure_features(text, subject)
                
                analysis_results["subjects"][subject] = {
                    "pdf_path": pdf_path,
                    "text_length": len(text),
                    "page_count": self.pdf_processor.get_page_count(pdf_path),
                    "structure_features": structure_features,
                    "format_type": self._detect_format_type(text, subject),
                    "question_indicators": self._find_question_indicators(text),
                    "answer_indicators": self._find_answer_indicators(text)
                }
                
                analysis_results["successful_analysis"] += 1
                self.logger.success(f"✓ 成功分析: {subject}")
                
            except Exception as e:
                self.logger.error(f"分析失敗 {subject}: {e}")
        
        return analysis_results
    
    def _analyze_structure_features(self, text: str, subject: str) -> Dict[str, Any]:
        """分析PDF結構特徵"""
        
        features = {
            "has_essay_section": False,
            "has_choice_section": False,
            "has_mixed_format": False,
            "question_patterns": [],
            "option_patterns": [],
            "special_characters": [],
            "section_headers": []
        }
        
        # 檢測申論題部分
        essay_indicators = ["甲、申論題部分", "申論題", "作文", "論述"]
        features["has_essay_section"] = any(indicator in text for indicator in essay_indicators)
        
        # 檢測選擇題部分
        choice_indicators = ["乙、測驗題部分", "測驗題", "選擇題", "單選題"]
        features["has_choice_section"] = any(indicator in text for indicator in choice_indicators)
        
        # 檢測混合格式
        features["has_mixed_format"] = features["has_essay_section"] and features["has_choice_section"]
        
        # 查找題目模式
        question_patterns = [
            r'^\d+\s+',  # 數字開頭
            r'第\d+題',  # 第X題
            r'\(\d+\)',  # (數字)
        ]
        
        for pattern in question_patterns:
            matches = re.findall(pattern, text, re.MULTILINE)
            if matches:
                features["question_patterns"].append({
                    "pattern": pattern,
                    "count": len(matches),
                    "examples": matches[:5]
                })
        
        # 查找選項模式
        option_patterns = [
            r'[A-D]\.',  # A. B. C. D.
            r'\(A\)',    # (A) (B) (C) (D)
            r'[A-D]\)',   # A) B) C) D)
        ]
        
        for pattern in option_patterns:
            matches = re.findall(pattern, text)
            if matches:
                features["option_patterns"].append({
                    "pattern": pattern,
                    "count": len(matches),
                    "examples": matches[:5]
                })
        
        # 檢測特殊字符
        special_chars = ['\ue18c', '\ue18d', '\ue18e', '\ue18f']  # Unicode選項符號
        for char in special_chars:
            if char in text:
                features["special_characters"].append(char)
        
        # 查找章節標題
        section_headers = re.findall(r'[甲乙丙丁]、[^。\n]+', text)
        features["section_headers"] = section_headers[:10]
        
        return features
    
    def _detect_format_type(self, text: str, subject: str) -> str:
        """檢測格式類型"""
        
        # 檢測綜合格式
        if "甲、申論題部分" in text and "乙、測驗題部分" in text:
            return "comprehensive"
        
        # 檢測混合格式
        if "作文" in subject or ("作文部分" in text and "測驗部分" in text):
            return "mixed_format"
        
        # 檢測申論題
        essay_indicators = ["申論題", "論述", "作文"]
        if any(indicator in text for indicator in essay_indicators):
            return "essay"
        
        # 檢測選擇題
        choice_indicators = ["測驗題", "選擇題", "單選題"]
        if any(indicator in text for indicator in choice_indicators):
            return "choice"
        
        return "unknown"
    
    def _find_question_indicators(self, text: str) -> List[str]:
        """查找題目指示符"""
        indicators = []
        
        # 查找題號模式
        question_patterns = [
            r'第\d+題',
            r'^\d+\s+',
            r'\(\d+\)',
        ]
        
        for pattern in question_patterns:
            matches = re.findall(pattern, text, re.MULTILINE)
            indicators.extend(matches[:10])  # 取前10個
        
        return list(set(indicators))  # 去重
    
    def _find_answer_indicators(self, text: str) -> List[str]:
        """查找答案指示符"""
        indicators = []
        
        # 查找答案模式
        answer_patterns = [
            r'答案：[A-D]',
            r'正確答案：[A-D]',
            r'標準答案：[A-D]',
        ]
        
        for pattern in answer_patterns:
            matches = re.findall(pattern, text)
            indicators.extend(matches)
        
        return indicators

def main():
    """主函數"""
    print("=== 114年監獄官考試PDF結構分析 ===")
    
    analyzer = PrisonExamStructureAnalyzer()
    results = analyzer.analyze_prison_exam_pdfs()
    
    # 保存分析結果
    output_file = "test_output/114年監獄官_結構分析.json"
    os.makedirs("test_output", exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    # 生成統計報告
    report_file = "test_output/114年監獄官_分析報告.md"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("# 114年監獄官考試PDF結構分析報告\n\n")
        f.write(f"## 總體統計\n")
        f.write(f"- 總科目數: {results['total_subjects']}\n")
        f.write(f"- 分析科目數: {results['analyzed_subjects']}\n")
        f.write(f"- 成功分析數: {results['successful_analysis']}\n")
        if results['analyzed_subjects'] > 0:
            f.write(f"- 成功率: {results['successful_analysis']/results['analyzed_subjects']*100:.1f}%\n\n")
        else:
            f.write(f"- 成功率: 0.0%\n\n")
        
        f.write("## 各科目詳細分析\n\n")
        for subject, data in results['subjects'].items():
            f.write(f"### {subject}\n")
            f.write(f"- PDF路徑: {data['pdf_path']}\n")
            f.write(f"- 文本長度: {data['text_length']} 字元\n")
            f.write(f"- 頁數: {data['page_count']}\n")
            f.write(f"- 格式類型: {data['format_type']}\n")
            f.write(f"- 申論題部分: {'是' if data['structure_features']['has_essay_section'] else '否'}\n")
            f.write(f"- 選擇題部分: {'是' if data['structure_features']['has_choice_section'] else '否'}\n")
            f.write(f"- 混合格式: {'是' if data['structure_features']['has_mixed_format'] else '否'}\n")
            f.write(f"- 題目指示符: {len(data['question_indicators'])} 個\n")
            f.write(f"- 答案指示符: {len(data['answer_indicators'])} 個\n\n")
    
    print(f"\n=== 分析完成 ===")
    print(f"分析結果已保存至: {output_file}")
    print(f"統計報告已保存至: {report_file}")
    print(f"成功分析: {results['successful_analysis']}/{results['analyzed_subjects']} 科目")

if __name__ == "__main__":
    main()
