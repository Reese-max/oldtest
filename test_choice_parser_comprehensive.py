#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試選擇題解析器，分析嵌入式填空題格式
"""

import os
import sys
import json
from typing import Dict, List, Any

# 添加src路徑
sys.path.append('src')

from src.processors.archaeology_processor import ArchaeologyProcessor
from src.core.question_parser import QuestionParser
from src.core.embedded_question_parser import EmbeddedQuestionParser
from src.core.ultimate_question_parser import UltimateQuestionParser
from src.utils.logger import logger

class ChoiceParserTester:
    """選擇題解析器測試器"""
    
    def __init__(self):
        self.processor = ArchaeologyProcessor(use_enhanced=True)
        self.question_parser = QuestionParser()
        self.embedded_parser = EmbeddedQuestionParser()
        self.ultimate_parser = UltimateQuestionParser()
        self.logger = logger
        
    def test_choice_parsers_on_police_exams(self) -> Dict[str, Any]:
        """測試選擇題解析器在警察特考上的表現"""
        
        # 選擇一些典型的選擇題科目進行測試
        test_subjects = [
            "中華民國憲法與警察專業英文",  # 綜合格式（申論+選擇）
            "國文(作文與測驗)",  # 混合格式
            "警察情境實務",  # 申論題
            "警察法規",  # 申論題
        ]
        
        test_results = {
            "total_subjects": len(test_subjects),
            "tested_subjects": 0,
            "successful_tests": 0,
            "subjects": {}
        }
        
        base_dir = "114年考古題/民國114年/民國114年_警察特考/資訊管理"
        
        for subject in test_subjects:
            self.logger.info(f"測試選擇題解析器: {subject}")
            
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
                    
                    # 分析格式類型
                    format_type = self._analyze_format_type(result, subject)
                    
                    # 分析解析器使用情況
                    parser_analysis = self._analyze_parser_usage(result, subject)
                    
                    test_results["subjects"][subject] = {
                        "pdf_path": pdf_path,
                        "questions_count": questions_count,
                        "format_type": format_type,
                        "success": True,
                        "parser_analysis": parser_analysis,
                        "is_choice_subject": self._is_choice_subject(subject, questions_count)
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
                        "parser_analysis": {},
                        "is_choice_subject": False
                    }
                    self.logger.error(f"❌ 處理失敗: {subject}")
                    
            except Exception as e:
                test_results["subjects"][subject] = {
                    "pdf_path": pdf_path,
                    "questions_count": 0,
                    "format_type": "unknown",
                    "success": False,
                    "error": str(e),
                    "parser_analysis": {},
                    "is_choice_subject": False
                }
                self.logger.error(f"❌ 處理異常: {subject} - {e}")
        
        return test_results
    
    def test_embedded_parser_directly(self) -> Dict[str, Any]:
        """直接測試嵌入式填空題解析器"""
        
        # 選擇包含嵌入式填空題的PDF進行測試
        test_pdfs = [
            "114年考古題/民國114年/民國114年_司法特考/監獄官/法學知識與英文（包括中華民國憲法、法學緒論、英文）/試題.pdf",
            "114年考古題/民國114年/民國114年_警察特考/資訊管理/中華民國憲法與警察專業英文/試題.pdf"
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
                
                # 直接使用嵌入式填空題解析器
                questions = self.embedded_parser.parse_embedded_questions(text)
                
                direct_test_results["results"][pdf_path] = {
                    "questions_count": len(questions),
                    "questions": questions[:3] if questions else [],  # 只保存前3題作為示例
                    "success": len(questions) > 0,
                    "parser_type": "embedded"
                }
                
                if len(questions) > 0:
                    direct_test_results["successful_parses"] += 1
                    self.logger.success(f"✓ 嵌入式填空題解析成功: {os.path.basename(pdf_path)} ({len(questions)} 題)")
                else:
                    self.logger.warning(f"⚠ 嵌入式填空題解析無結果: {os.path.basename(pdf_path)}")
                    
            except Exception as e:
                direct_test_results["results"][pdf_path] = {
                    "questions_count": 0,
                    "questions": [],
                    "success": False,
                    "error": str(e),
                    "parser_type": "embedded"
                }
                self.logger.error(f"❌ 嵌入式填空題解析失敗: {os.path.basename(pdf_path)} - {e}")
        
        return direct_test_results
    
    def test_ultimate_parser_directly(self) -> Dict[str, Any]:
        """直接測試終極解析器"""
        
        # 選擇綜合格式的PDF進行測試
        test_pdfs = [
            "114年考古題/民國114年/民國114年_警察特考/資訊管理/中華民國憲法與警察專業英文/試題.pdf"
        ]
        
        ultimate_test_results = {
            "total_pdfs": len(test_pdfs),
            "tested_pdfs": 0,
            "successful_parses": 0,
            "results": {}
        }
        
        for pdf_path in test_pdfs:
            if not os.path.exists(pdf_path):
                self.logger.warning(f"PDF不存在: {pdf_path}")
                continue
                
            ultimate_test_results["tested_pdfs"] += 1
            
            try:
                # 提取文本
                text = self.processor.pdf_processor.extract_text(pdf_path)
                if not text:
                    self.logger.warning(f"無法提取文本: {pdf_path}")
                    continue
                
                # 直接使用終極解析器
                questions = self.ultimate_parser.parse_all_60_questions(text, pdf_path)
                
                ultimate_test_results["results"][pdf_path] = {
                    "questions_count": len(questions),
                    "questions": questions[:3] if questions else [],  # 只保存前3題作為示例
                    "success": len(questions) > 0,
                    "parser_type": "ultimate"
                }
                
                if len(questions) > 0:
                    ultimate_test_results["successful_parses"] += 1
                    self.logger.success(f"✓ 終極解析器成功: {os.path.basename(pdf_path)} ({len(questions)} 題)")
                else:
                    self.logger.warning(f"⚠ 終極解析器無結果: {os.path.basename(pdf_path)}")
                    
            except Exception as e:
                ultimate_test_results["results"][pdf_path] = {
                    "questions_count": 0,
                    "questions": [],
                    "success": False,
                    "error": str(e),
                    "parser_type": "ultimate"
                }
                self.logger.error(f"❌ 終極解析器失敗: {os.path.basename(pdf_path)} - {e}")
        
        return ultimate_test_results
    
    def _analyze_format_type(self, result: Dict[str, Any], subject: str) -> str:
        """分析格式類型"""
        
        # 基於科目名稱和題數判斷
        if "中華民國憲法與警察專業英文" in subject:
            return "comprehensive"
        elif "國文" in subject and "作文" in subject:
            return "mixed_format"
        elif "警察情境實務" in subject or "警察法規" in subject:
            return "essay"
        else:
            return "unknown"
    
    def _analyze_parser_usage(self, result: Dict[str, Any], subject: str) -> Dict[str, Any]:
        """分析解析器使用情況"""
        
        statistics = result.get('statistics', {})
        
        parser_usage = {
            "essay_parser": statistics.get('essay_questions', 0),
            "choice_parser": statistics.get('choice_questions', 0),
            "embedded_parser": statistics.get('embedded_questions', 0),
            "mixed_parser": statistics.get('mixed_questions', 0),
            "ultimate_parser": statistics.get('comprehensive_questions', 0)
        }
        
        # 識別主要使用的解析器
        main_parser = max(parser_usage.items(), key=lambda x: x[1])
        
        return {
            "parser_usage": parser_usage,
            "main_parser": main_parser[0] if main_parser[1] > 0 else "none",
            "main_parser_count": main_parser[1]
        }
    
    def _is_choice_subject(self, subject: str, questions_count: int) -> bool:
        """判斷是否為選擇題科目"""
        
        # 基於科目名稱判斷
        choice_subjects = [
            "中華民國憲法與警察專業英文"
        ]
        
        if subject in choice_subjects:
            return True
        
        # 基於題數判斷（選擇題通常題數較多）
        if questions_count >= 50:
            return True
            
        return False
    
    def generate_test_report(self, test_results: Dict[str, Any], embedded_results: Dict[str, Any], ultimate_results: Dict[str, Any]) -> str:
        """生成測試報告"""
        
        report = "# 選擇題解析器測試報告\n\n"
        
        # 總體統計
        report += f"## 總體統計\n"
        report += f"- 測試科目數: {test_results['tested_subjects']}\n"
        report += f"- 成功處理數: {test_results['successful_tests']}\n"
        report += f"- 成功率: {test_results['successful_tests']/test_results['tested_subjects']*100:.1f}%\n\n"
        
        # 直接測試統計
        report += f"## 直接解析測試\n"
        report += f"### 嵌入式填空題解析器\n"
        report += f"- 測試PDF數: {embedded_results['tested_pdfs']}\n"
        report += f"- 成功解析數: {embedded_results['successful_parses']}\n"
        report += f"- 解析成功率: {embedded_results['successful_parses']/embedded_results['tested_pdfs']*100:.1f}%\n\n"
        
        report += f"### 終極解析器\n"
        report += f"- 測試PDF數: {ultimate_results['tested_pdfs']}\n"
        report += f"- 成功解析數: {ultimate_results['successful_parses']}\n"
        report += f"- 解析成功率: {ultimate_results['successful_parses']/ultimate_results['tested_pdfs']*100:.1f}%\n\n"
        
        # 各科目詳細結果
        report += f"## 各科目處理結果\n\n"
        for subject, data in test_results['subjects'].items():
            report += f"### {subject}\n"
            report += f"- 題數: {data['questions_count']}\n"
            report += f"- 格式類型: {data['format_type']}\n"
            report += f"- 是否選擇題: {'是' if data['is_choice_subject'] else '否'}\n"
            report += f"- 主要解析器: {data['parser_analysis']['main_parser']}\n"
            report += f"- 主要解析器題數: {data['parser_analysis']['main_parser_count']}\n"
            report += f"- 處理狀態: {'成功' if data['success'] else '失敗'}\n"
            if not data['success'] and 'error' in data:
                report += f"- 錯誤信息: {data['error']}\n"
            report += f"\n"
        
        # 解析器使用分析
        report += f"## 解析器使用分析\n"
        parser_stats = {}
        for subject, data in test_results['subjects'].items():
            if data['success']:
                main_parser = data['parser_analysis']['main_parser']
                parser_stats[main_parser] = parser_stats.get(main_parser, 0) + 1
        
        for parser, count in parser_stats.items():
            report += f"- {parser}: {count} 個科目\n"
        report += f"\n"
        
        return report

def main():
    """主函數"""
    print("=== 選擇題解析器測試 ===")
    
    tester = ChoiceParserTester()
    
    # 測試ArchaeologyProcessor
    print("\n1. 測試ArchaeologyProcessor處理警察特考...")
    test_results = tester.test_choice_parsers_on_police_exams()
    
    # 直接測試嵌入式填空題解析器
    print("\n2. 直接測試嵌入式填空題解析器...")
    embedded_results = tester.test_embedded_parser_directly()
    
    # 直接測試終極解析器
    print("\n3. 直接測試終極解析器...")
    ultimate_results = tester.test_ultimate_parser_directly()
    
    # 生成報告
    report = tester.generate_test_report(test_results, embedded_results, ultimate_results)
    
    # 保存結果
    os.makedirs("test_output", exist_ok=True)
    
    # 保存JSON結果
    with open("test_output/選擇題解析器測試結果.json", 'w', encoding='utf-8') as f:
        json.dump({
            "test_results": test_results,
            "embedded_results": embedded_results,
            "ultimate_results": ultimate_results
        }, f, ensure_ascii=False, indent=2)
    
    # 保存報告
    with open("test_output/選擇題解析器測試報告.md", 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\n=== 測試完成 ===")
    print(f"測試結果已保存至: test_output/選擇題解析器測試結果.json")
    print(f"測試報告已保存至: test_output/選擇題解析器測試報告.md")
    print(f"ArchaeologyProcessor成功率: {test_results['successful_tests']}/{test_results['tested_subjects']} ({test_results['successful_tests']/test_results['tested_subjects']*100:.1f}%)")
    print(f"嵌入式解析器成功率: {embedded_results['successful_parses']}/{embedded_results['tested_pdfs']} ({embedded_results['successful_parses']/embedded_results['tested_pdfs']*100:.1f}%)")
    print(f"終極解析器成功率: {ultimate_results['successful_parses']}/{ultimate_results['tested_pdfs']} ({ultimate_results['successful_parses']/ultimate_results['tested_pdfs']*100:.1f}%)")

if __name__ == "__main__":
    main()
