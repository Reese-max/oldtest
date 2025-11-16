#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試申論題解析器，驗證6/7科目處理能力
"""

import os
import sys
import json
from typing import Dict, List, Any

# 添加src路徑
sys.path.append('src')

from src.processors.archaeology_processor import ArchaeologyProcessor
from src.core.essay_question_parser import EssayQuestionParser
from src.utils.logger import logger

class EssayParserTester:
    """申論題解析器測試器"""
    
    def __init__(self):
        self.processor = ArchaeologyProcessor(use_enhanced=True)
        self.essay_parser = EssayQuestionParser()
        self.logger = logger
        
    def test_essay_parser_on_prison_exams(self) -> Dict[str, Any]:
        """測試申論題解析器在監獄官考試上的表現"""
        
        # 監獄官考試科目（8個科目）
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
        
        test_results = {
            "total_subjects": len(prison_subjects),
            "tested_subjects": 0,
            "successful_tests": 0,
            "subjects": {}
        }
        
        base_dir = "114年考古題/民國114年/民國114年_司法特考/監獄官"
        
        for subject in prison_subjects:
            self.logger.info(f"測試申論題解析器: {subject}")
            
            subject_dir = os.path.join(base_dir, subject)
            if not os.path.exists(subject_dir):
                self.logger.warning(f"科目目錄不存在: {subject_dir}")
                continue
                
            test_results["tested_subjects"] += 1
            
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
                # 使用ArchaeologyProcessor處理
                result = self.processor.process_pdf(pdf_path)
                
                if result.get('success', False):
                    questions_count = result.get('questions_count', 0)
                    
                    # 分析題目類型
                    format_type = self._analyze_format_type(result, subject)
                    
                    test_results["subjects"][subject] = {
                        "pdf_path": pdf_path,
                        "questions_count": questions_count,
                        "format_type": format_type,
                        "success": True,
                        "is_essay_subject": self._is_essay_subject(subject, questions_count),
                        "parser_used": self._identify_parser_used(result)
                    }
                    
                    test_results["successful_tests"] += 1
                    self.logger.success(f"✓ 成功處理: {subject} ({questions_count} 題)")
                    
                else:
                    test_results["subjects"][subject] = {
                        "pdf_path": pdf_path,
                        "questions_count": 0,
                        "format_type": "unknown",
                        "success": False,
                        "error": result.get('error', '未知錯誤'),
                        "is_essay_subject": False,
                        "parser_used": "none"
                    }
                    self.logger.error(f"❌ 處理失敗: {subject}")
                    
            except Exception as e:
                test_results["subjects"][subject] = {
                    "pdf_path": pdf_path,
                    "questions_count": 0,
                    "format_type": "unknown",
                    "success": False,
                    "error": str(e),
                    "is_essay_subject": False,
                    "parser_used": "none"
                }
                self.logger.error(f"❌ 處理異常: {subject} - {e}")
        
        return test_results
    
    def _analyze_format_type(self, result: Dict[str, Any], subject: str) -> str:
        """分析格式類型"""
        
        # 基於科目名稱和題數判斷
        if "國文" in subject and "作文" in subject:
            return "mixed_format"
        elif "法學知識與英文" in subject:
            return "comprehensive"
        else:
            # 基於題數判斷
            questions_count = result.get('questions_count', 0)
            if questions_count <= 5:
                return "essay"
            elif questions_count >= 50:
                return "comprehensive"
            else:
                return "unknown"
    
    def _is_essay_subject(self, subject: str, questions_count: int) -> bool:
        """判斷是否為申論題科目"""
        
        # 基於科目名稱判斷
        essay_subjects = [
            "監獄學",
            "監獄行刑法與羈押法", 
            "刑法與少年事件處理法",
            "犯罪學與再犯預測",
            "刑事政策",
            "諮商與矯正輔導"
        ]
        
        if subject in essay_subjects:
            return True
        
        # 基於題數判斷（申論題通常題數較少）
        if questions_count <= 5:
            return True
            
        return False
    
    def _identify_parser_used(self, result: Dict[str, Any]) -> str:
        """識別使用的解析器"""
        
        # 基於統計信息判斷
        statistics = result.get('statistics', {})
        
        if 'essay_questions' in statistics and statistics['essay_questions'] > 0:
            return "essay_parser"
        elif 'choice_questions' in statistics and statistics['choice_questions'] > 0:
            return "choice_parser"
        elif 'mixed_questions' in statistics and statistics['mixed_questions'] > 0:
            return "mixed_parser"
        elif 'comprehensive_questions' in statistics and statistics['comprehensive_questions'] > 0:
            return "ultimate_parser"
        else:
            return "unknown"
    
    def test_essay_parser_directly(self) -> Dict[str, Any]:
        """直接測試申論題解析器"""
        
        # 選擇幾個典型的申論題PDF進行直接測試
        test_pdfs = [
            "114年考古題/民國114年/民國114年_司法特考/監獄官/監獄學/試題.pdf",
            "114年考古題/民國114年/民國114年_司法特考/監獄官/監獄行刑法與羈押法/試題.pdf",
            "114年考古題/民國114年/民國114年_司法特考/監獄官/刑法與少年事件處理法/試題.pdf",
            "114年考古題/民國114年/民國114年_司法特考/監獄官/犯罪學與再犯預測/試題.pdf",
            "114年考古題/民國114年/民國114年_司法特考/監獄官/刑事政策/試題.pdf",
            "114年考古題/民國114年/民國114年_司法特考/監獄官/諮商與矯正輔導/試題.pdf"
        ]
        
        direct_test_results = {
            "total_pdfs": len(test_pdfs),
            "tested_pdfs": 0,
            "successful_parses": 0,
            "results": {}
        }
        
        for pdf_path in test_pdfs:
            if not os.path.exists(pdf_path):
                self.logger.warning(f"PDF不存在: {pdf_path}")
                continue
                
            direct_test_results["tested_pdfs"] += 1
            
            try:
                # 提取文本
                text = self.processor.pdf_processor.extract_text(pdf_path)
                if not text:
                    self.logger.warning(f"無法提取文本: {pdf_path}")
                    continue
                
                # 直接使用申論題解析器
                questions = self.essay_parser.parse_essay_questions(text)
                
                direct_test_results["results"][pdf_path] = {
                    "questions_count": len(questions),
                    "questions": questions[:3] if questions else [],  # 只保存前3題作為示例
                    "success": len(questions) > 0
                }
                
                if len(questions) > 0:
                    direct_test_results["successful_parses"] += 1
                    self.logger.success(f"✓ 申論題解析成功: {os.path.basename(pdf_path)} ({len(questions)} 題)")
                else:
                    self.logger.warning(f"⚠ 申論題解析無結果: {os.path.basename(pdf_path)}")
                    
            except Exception as e:
                direct_test_results["results"][pdf_path] = {
                    "questions_count": 0,
                    "questions": [],
                    "success": False,
                    "error": str(e)
                }
                self.logger.error(f"❌ 申論題解析失敗: {os.path.basename(pdf_path)} - {e}")
        
        return direct_test_results
    
    def generate_test_report(self, test_results: Dict[str, Any], direct_results: Dict[str, Any]) -> str:
        """生成測試報告"""
        
        report = "# 申論題解析器測試報告\n\n"
        
        # 總體統計
        report += f"## 總體統計\n"
        report += f"- 測試科目數: {test_results['tested_subjects']}\n"
        report += f"- 成功處理數: {test_results['successful_tests']}\n"
        report += f"- 成功率: {test_results['successful_tests']/test_results['tested_subjects']*100:.1f}%\n\n"
        
        # 直接測試統計
        report += f"## 直接解析測試\n"
        report += f"- 測試PDF數: {direct_results['tested_pdfs']}\n"
        report += f"- 成功解析數: {direct_results['successful_parses']}\n"
        report += f"- 解析成功率: {direct_results['successful_parses']/direct_results['tested_pdfs']*100:.1f}%\n\n"
        
        # 各科目詳細結果
        report += f"## 各科目處理結果\n\n"
        for subject, data in test_results['subjects'].items():
            report += f"### {subject}\n"
            report += f"- 題數: {data['questions_count']}\n"
            report += f"- 格式類型: {data['format_type']}\n"
            report += f"- 是否申論題: {'是' if data['is_essay_subject'] else '否'}\n"
            report += f"- 使用解析器: {data['parser_used']}\n"
            report += f"- 處理狀態: {'成功' if data['success'] else '失敗'}\n"
            if not data['success'] and 'error' in data:
                report += f"- 錯誤信息: {data['error']}\n"
            report += f"\n"
        
        # 申論題科目分析
        essay_subjects = [s for s, d in test_results['subjects'].items() if d['is_essay_subject']]
        report += f"## 申論題科目分析\n"
        report += f"- 申論題科目數: {len(essay_subjects)}\n"
        report += f"- 申論題科目: {', '.join(essay_subjects)}\n\n"
        
        # 解析器使用情況
        parser_usage = {}
        for subject, data in test_results['subjects'].items():
            parser = data['parser_used']
            parser_usage[parser] = parser_usage.get(parser, 0) + 1
        
        report += f"## 解析器使用情況\n"
        for parser, count in parser_usage.items():
            report += f"- {parser}: {count} 個科目\n"
        report += f"\n"
        
        return report

def main():
    """主函數"""
    print("=== 申論題解析器測試 ===")
    
    tester = EssayParserTester()
    
    # 測試ArchaeologyProcessor
    print("\n1. 測試ArchaeologyProcessor處理監獄官考試...")
    test_results = tester.test_essay_parser_on_prison_exams()
    
    # 直接測試申論題解析器
    print("\n2. 直接測試申論題解析器...")
    direct_results = tester.test_essay_parser_directly()
    
    # 生成報告
    report = tester.generate_test_report(test_results, direct_results)
    
    # 保存結果
    os.makedirs("test_output", exist_ok=True)
    
    # 保存JSON結果
    with open("test_output/申論題解析器測試結果.json", 'w', encoding='utf-8') as f:
        json.dump({
            "test_results": test_results,
            "direct_results": direct_results
        }, f, ensure_ascii=False, indent=2)
    
    # 保存報告
    with open("test_output/申論題解析器測試報告.md", 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\n=== 測試完成 ===")
    print(f"測試結果已保存至: test_output/申論題解析器測試結果.json")
    print(f"測試報告已保存至: test_output/申論題解析器測試報告.md")
    print(f"ArchaeologyProcessor成功率: {test_results['successful_tests']}/{test_results['tested_subjects']} ({test_results['successful_tests']/test_results['tested_subjects']*100:.1f}%)")
    print(f"直接解析成功率: {direct_results['successful_parses']}/{direct_results['tested_pdfs']} ({direct_results['successful_parses']/direct_results['tested_pdfs']*100:.1f}%)")

if __name__ == "__main__":
    main()
