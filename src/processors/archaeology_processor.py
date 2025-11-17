#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
考古題處理器
主要的處理邏輯整合
"""

import os
from typing import List, Dict, Any, Optional, Tuple
from ..core.pdf_processor import PDFProcessor
from ..core.enhanced_pdf_processor import EnhancedPDFProcessor
from ..core.question_parser import QuestionParser
from ..core.ai_question_parser import AIQuestionParser
from ..core.essay_question_parser import EssayQuestionParser
from ..core.mixed_format_parser import MixedFormatParser
from ..core.embedded_question_parser import EmbeddedQuestionParser
from ..core.comprehensive_question_parser import ComprehensiveQuestionParser
from ..core.ultimate_question_parser import UltimateQuestionParser
from ..core.answer_processor import AnswerProcessor
from ..core.csv_generator import CSVGenerator
from ..utils.logger import logger
from ..utils.exceptions import ArchaeologyQuestionsError
from ..utils.constants import (
    FORMAT_TYPE_COMPREHENSIVE, FORMAT_TYPE_MIXED, FORMAT_TYPE_EMBEDDED,
    FORMAT_TYPE_ESSAY, FORMAT_TYPE_STANDARD,
    KEYWORDS_TEST_SECTION, KEYWORDS_ESSAY_SECTION, KEYWORDS_ENGLISH_ESSAY,
    KEYWORDS_QUESTION_GROUP_START, KEYWORDS_QUESTION_GROUP_END,
    KEYWORDS_ESSAY_PART, KEYWORDS_TEST_PART,
    FILE_PATTERN_ANSWER, FILE_PATTERN_CORRECTED_ANSWER, FILE_PATTERN_GOOGLE_CSV,
    DEFAULT_OUTPUT_DIR, UNICODE_OPTION_SYMBOLS
)


class ArchaeologyProcessor:
    """考古題處理器"""
    
    def __init__(self, use_enhanced: bool = True):
        self.logger = logger
        self.use_enhanced = use_enhanced
        
        # 根據設定選擇處理器
        if use_enhanced:
            self.pdf_processor = EnhancedPDFProcessor()
            self.question_parser_enhanced = AIQuestionParser()
        else:
            self.pdf_processor = PDFProcessor()
        
        self.question_parser = QuestionParser()
        self.essay_parser = EssayQuestionParser()  # 申論題解析器
        self.mixed_parser = MixedFormatParser()  # 混合格式解析器
        self.embedded_parser = EmbeddedQuestionParser()  # 嵌入式填空題解析器
        self.comprehensive_parser = ComprehensiveQuestionParser()  # 綜合解析器
        self.ultimate_parser = UltimateQuestionParser()  # 終極解析器
        self.answer_processor = AnswerProcessor()
        self.csv_generator = CSVGenerator()
    
    def process_pdf(self, pdf_path: str,
                   answer_pdf_path: Optional[str] = None,
                   corrected_answer_pdf_path: Optional[str] = None,
                   output_dir: str = "output") -> Dict[str, Any]:
        """
        處理PDF檔案，生成CSV（重構後的主流程）

        Args:
            pdf_path: PDF檔案路徑
            answer_pdf_path: 答案PDF檔案路徑（可選）
            corrected_answer_pdf_path: 更正答案PDF檔案路徑（可選）
            output_dir: 輸出目錄

        Returns:
            處理結果字典
        """
        try:
            self.logger.info(f"開始處理PDF檔案: {pdf_path}")

            # 1. 提取問題文本並解析
            questions = self._extract_and_parse_questions(pdf_path)
            if not questions:
                return {'success': False, 'message': '未找到任何題目'}

            # 2. 提取並合併答案
            answers, corrected_answers = self._extract_and_merge_answers(
                answer_pdf_path, corrected_answer_pdf_path
            )

            # 3. 生成輸出檔案
            csv_files = self._generate_csv_files(
                questions, answers, corrected_answers, pdf_path, output_dir
            )

            # 4. 構建結果
            result = self._build_result(
                pdf_path, output_dir, csv_files,
                questions, answers, corrected_answers
            )

            self.logger.success(f"PDF處理完成: {len(questions)} 題，{len(csv_files)} 個CSV檔案")
            return result

        except Exception as e:
            error_msg = f"PDF處理失敗: {e}"
            self.logger.failure(error_msg)
            return {'success': False, 'message': error_msg}

    def _extract_and_parse_questions(self, pdf_path: str) -> List[Dict[str, Any]]:
        """
        提取PDF文本並解析題目

        Args:
            pdf_path: PDF檔案路徑

        Returns:
            題目列表
        """
        # 提取PDF文字
        text = self._extract_pdf_text(pdf_path)

        # 智能格式檢測和解析
        questions = self._smart_parse_questions(text, pdf_path)

        if not questions:
            self.logger.warning("未找到任何題目")

        return questions

    def _extract_and_merge_answers(self,
                                   answer_pdf_path: Optional[str],
                                   corrected_answer_pdf_path: Optional[str]) -> Tuple[Dict[str, str], Dict[str, str]]:
        """
        提取並合併答案

        Args:
            answer_pdf_path: 答案PDF檔案路徑
            corrected_answer_pdf_path: 更正答案PDF檔案路徑

        Returns:
            (答案字典, 更正答案字典) 元組
        """
        # 提取原始答案
        answers = self._extract_answers_from_pdf(answer_pdf_path)

        # 提取更正答案
        corrected_answers = self._extract_corrected_answers_from_pdf(
            corrected_answer_pdf_path
        )

        return answers, corrected_answers

    def _extract_answers_from_pdf(self, pdf_path: Optional[str]) -> Dict[str, str]:
        """
        從PDF提取答案

        Args:
            pdf_path: PDF檔案路徑

        Returns:
            答案字典
        """
        if not pdf_path or not os.path.exists(pdf_path):
            return {}

        answer_text = self.pdf_processor.extract_text(pdf_path)
        if not answer_text:
            self.logger.warning(f"無法從答案PDF提取文字: {pdf_path}")
            return {}

        return self.answer_processor.extract_answers(answer_text)

    def _extract_corrected_answers_from_pdf(self, pdf_path: Optional[str]) -> Dict[str, str]:
        """
        從PDF提取更正答案

        Args:
            pdf_path: PDF檔案路徑

        Returns:
            更正答案字典
        """
        if not pdf_path or not os.path.exists(pdf_path):
            return {}

        corrected_text = self.pdf_processor.extract_text(pdf_path)
        if not corrected_text:
            self.logger.warning(f"無法從更正答案PDF提取文字: {pdf_path}")
            return {}

        return self.answer_processor.extract_corrected_answers(corrected_text)

    def _build_result(self,
                     pdf_path: str,
                     output_dir: str,
                     csv_files: List[str],
                     questions: List[Dict[str, Any]],
                     answers: Dict[str, str],
                     corrected_answers: Dict[str, str]) -> Dict[str, Any]:
        """
        構建處理結果字典

        Args:
            pdf_path: PDF檔案路徑
            output_dir: 輸出目錄
            csv_files: CSV檔案列表
            questions: 題目列表
            answers: 答案字典
            corrected_answers: 更正答案字典

        Returns:
            處理結果字典
        """
        stats = self._generate_statistics(questions, answers, corrected_answers)

        return {
            'success': True,
            'pdf_path': pdf_path,
            'output_dir': output_dir,
            'csv_files': csv_files,
            'questions_count': len(questions),
            'answers_count': len(answers),
            'corrected_answers_count': len(corrected_answers),
            'statistics': stats
        }
    
    def _smart_parse_questions(self, text: str, pdf_path: str) -> List[Dict[str, Any]]:
        """智能格式检测和解析"""
        questions = []
        
        # 检测格式类型
        format_type = self._detect_format_type(text, pdf_path)
        self.logger.info(f"检测到格式类型: {format_type}")
        
        # 根據格式類型選擇對應的解析器
        format_parsers = {
            FORMAT_TYPE_COMPREHENSIVE: lambda: self._parse_comprehensive(text, pdf_path),
            FORMAT_TYPE_MIXED: lambda: self._parse_mixed(text),
            FORMAT_TYPE_EMBEDDED: lambda: self._parse_embedded(text),
            FORMAT_TYPE_ESSAY: lambda: self._parse_essay(text),
            FORMAT_TYPE_STANDARD: lambda: self._parse_standard(text)
        }
        
        parser_func = format_parsers.get(format_type, format_parsers[FORMAT_TYPE_STANDARD])
        questions = parser_func()
        
        return questions
    
    def _parse_comprehensive(self, text: str, pdf_path: str) -> List[Dict[str, Any]]:
        """解析綜合格式"""
        questions = self.ultimate_parser.parse_all_60_questions(text, pdf_path)
        if questions:
            self.logger.success(f"✓ 終極解析成功: {len(questions)} 題")
        return questions
    
    def _parse_mixed(self, text: str) -> List[Dict[str, Any]]:
        """解析混合格式"""
        questions = self.mixed_parser.parse_mixed_format(text)
        if questions:
            self.logger.success(f"✓ 混合格式解析成功: {len(questions)} 題")
        return questions
    
    def _parse_embedded(self, text: str) -> List[Dict[str, Any]]:
        """解析嵌入式填空題"""
        questions = self.embedded_parser.parse_embedded_questions(text)
        if questions:
            self.logger.success(f"✓ 嵌入式填空題解析成功: {len(questions)} 題")
        return questions
    
    def _parse_essay(self, text: str) -> List[Dict[str, Any]]:
        """解析申論題"""
        questions = self.essay_parser.parse_essay_questions(text)
        if questions:
            self.logger.success(f"✓ 申論題解析成功: {len(questions)} 題")
        return questions
    
    def _parse_standard(self, text: str) -> List[Dict[str, Any]]:
        """解析標準選擇題"""
        questions = []
        
        # 優先使用增強解析器
        if self.use_enhanced:
            questions = self.question_parser_enhanced.parse_questions_intelligent(text)
            if len(questions) >= 2:
                self.logger.success(f"✓ 增強解析器成功: {len(questions)} 題")
        
        # 如果增強解析器結果不足，使用標準解析器
        if len(questions) < 2:
            questions = self.question_parser.parse_questions(text)
            if questions:
                self.logger.success(f"✓ 標準解析器成功: {len(questions)} 題")
        
        return questions
    
    def _detect_format_type(self, text: str, pdf_path: str) -> str:
        """
        檢測PDF格式類型
        
        Args:
            text: PDF文字內容
            pdf_path: PDF檔案路徑
            
        Returns:
            格式類型字符串
        """
        filename = os.path.basename(pdf_path).lower()
        
        # 檢測綜合格式（包含多種題型）
        if self._is_comprehensive_format(text):
            return FORMAT_TYPE_COMPREHENSIVE
        
        # 檢測混合格式（國文作文與測驗）
        if self._is_mixed_format(filename, text):
            return FORMAT_TYPE_MIXED
        
        # 檢測嵌入式填空題
        if self._is_embedded_format(text):
            return FORMAT_TYPE_EMBEDDED
        
        # 檢測申論題
        if self._is_essay_format(text):
            return FORMAT_TYPE_ESSAY
        
        # 默認標準選擇題
        self.logger.info("默認標準選擇題格式")
        return FORMAT_TYPE_STANDARD
    
    def _is_comprehensive_format(self, text: str) -> bool:
        """檢測是否為綜合格式"""
        has_test_section = KEYWORDS_TEST_SECTION in text
        has_essay = KEYWORDS_ESSAY_SECTION in text or KEYWORDS_ENGLISH_ESSAY in text
        has_question_groups = (KEYWORDS_QUESTION_GROUP_START in text and 
                             KEYWORDS_QUESTION_GROUP_END in text)
        
        # 同時有測驗題部分和申論題
        if has_test_section and has_essay:
            self.logger.info("檢測到綜合格式（測驗+申論）")
            return True
        
        # 有測驗題部分且有題組（通常前面還有標準題）
        if has_test_section and has_question_groups:
            # 檢查是否有標準題（第1-50題範圍）
            has_standard_questions = any(f'{i} ' in text for i in range(1, 10))
            if has_standard_questions:
                self.logger.info("檢測到綜合格式（標準題+題組）")
                return True
        
        return False
    
    def _is_mixed_format(self, filename: str, text: str) -> bool:
        """檢測是否為混合格式"""
        is_chinese_exam = "國文" in filename or "作文" in filename
        has_mixed_parts = (KEYWORDS_ESSAY_PART in text and KEYWORDS_TEST_PART in text)
        
        if is_chinese_exam or has_mixed_parts:
            self.logger.info("檢測到混合格式")
            return True
        
        return False
    
    def _is_embedded_format(self, text: str) -> bool:
        """檢測是否為嵌入式填空題"""
        has_question_groups = (KEYWORDS_QUESTION_GROUP_START in text and
                             KEYWORDS_QUESTION_GROUP_END in text)
        has_special_symbols = any(symbol in text for symbol in UNICODE_OPTION_SYMBOLS)
        
        if has_question_groups and has_special_symbols:
            self.logger.info("檢測到嵌入式填空題")
            return True
        
        return False
    
    def _is_essay_format(self, text: str) -> bool:
        """檢測是否為申論題格式"""
        # 避免誤判混合格式
        is_mixed = KEYWORDS_ESSAY_PART in text and KEYWORDS_TEST_PART in text
        
        if not is_mixed:
            essay_questions = self.essay_parser.parse_essay_questions(text)
            if essay_questions:
                self.logger.info("檢測到申論題")
                return True
        
        return False
    
    def process_directory(self, input_dir: str, 
                         output_dir: str = DEFAULT_OUTPUT_DIR) -> Dict[str, Any]:
        """
        處理目錄中的所有PDF檔案
        
        Args:
            input_dir: 輸入目錄
            output_dir: 輸出目錄
            
        Returns:
            處理結果字典
        """
        try:
            self.logger.info(f"開始處理目錄: {input_dir}")
            
            if not os.path.exists(input_dir):
                raise ArchaeologyQuestionsError(f"輸入目錄不存在: {input_dir}")
            
            # 尋找PDF檔案
            pdf_files = []
            for root, dirs, files in os.walk(input_dir):
                for file in files:
                    if file.lower().endswith('.pdf'):
                        pdf_files.append(os.path.join(root, file))
            
            if not pdf_files:
                self.logger.warning("目錄中未找到PDF檔案")
                return {'success': False, 'message': '目錄中未找到PDF檔案'}
            
            # 處理每個PDF檔案
            results = []
            total_questions = 0
            
            for pdf_path in pdf_files:
                self.logger.info(f"處理檔案: {os.path.basename(pdf_path)}")
                
                # 尋找對應的答案檔案
                base_name = os.path.splitext(pdf_path)[0]
                answer_pdf = f"{base_name}{FILE_PATTERN_ANSWER}"
                corrected_answer_pdf = f"{base_name}{FILE_PATTERN_CORRECTED_ANSWER}"
                
                result = self.process_pdf(
                    pdf_path,
                    answer_pdf if os.path.exists(answer_pdf) else None,
                    corrected_answer_pdf if os.path.exists(corrected_answer_pdf) else None,
                    output_dir
                )
                
                results.append(result)
                if result['success']:
                    total_questions += result['questions_count']
            
            # 統計結果
            successful_count = sum(1 for r in results if r['success'])
            
            summary = {
                'success': True,
                'input_dir': input_dir,
                'output_dir': output_dir,
                'total_files': len(pdf_files),
                'successful_files': successful_count,
                'total_questions': total_questions,
                'results': results
            }
            
            self.logger.success(f"目錄處理完成: {successful_count}/{len(pdf_files)} 個檔案成功，共 {total_questions} 題")
            return summary
            
        except Exception as e:
            error_msg = f"目錄處理失敗: {e}"
            self.logger.failure(error_msg)
            return {'success': False, 'message': error_msg}
    
    def _generate_statistics(self, questions: List[Dict[str, Any]], 
                           answers: Dict[str, str],
                           corrected_answers: Dict[str, str]) -> Dict[str, Any]:
        """生成統計資訊"""
        try:
            # 題目統計
            regular_questions = [q for q in questions if not q.get('題組', False)]
            group_questions = [q for q in questions if q.get('題組', False)]
            
            # 題組統計
            question_groups = {}
            for q in group_questions:
                group_id = q.get('題組編號', 'unknown')
                if group_id not in question_groups:
                    question_groups[group_id] = 0
                question_groups[group_id] += 1
            
            # 答案統計
            answer_stats = self.answer_processor.get_answer_statistics(answers)
            
            stats = {
                'total_questions': len(questions),
                'regular_questions': len(regular_questions),
                'group_questions': len(group_questions),
                'question_groups': len(question_groups),
                'question_group_details': question_groups,
                'answers_count': len(answers),
                'corrected_answers_count': len(corrected_answers),
                'answer_statistics': answer_stats
            }
            
            return stats
            
        except Exception as e:
            self.logger.warning(f"統計資訊生成失敗: {e}")
            return {}
    
    def _extract_pdf_text(self, pdf_path: str) -> str:
        """
        提取PDF文字內容
        
        Args:
            pdf_path: PDF檔案路徑
            
        Returns:
            提取的文字內容
        """
        if self.use_enhanced:
            result = self.pdf_processor.extract_with_best_method(pdf_path)
            text = result['text']
            self.logger.info(f"使用 {result['method']} 提取，質量分數: {result['score']:.2f}")
            return text
        else:
            return self.pdf_processor.extract_text(pdf_path)
    
    def _generate_csv_files(self, questions: List[Dict[str, Any]], 
                           answers: Dict[str, str],
                           corrected_answers: Dict[str, str],
                           pdf_path: str,
                           output_dir: str) -> List[str]:
        """
        生成所有CSV檔案
        
        Args:
            questions: 題目列表
            answers: 答案字典
            corrected_answers: 更正答案字典
            pdf_path: PDF檔案路徑
            output_dir: 輸出目錄
            
        Returns:
            CSV檔案路徑列表
        """
        os.makedirs(output_dir, exist_ok=True)
        base_name = os.path.splitext(os.path.basename(pdf_path))[0]
        csv_files = []
        
        # 一般CSV
        general_csv = os.path.join(output_dir, f"{base_name}.csv")
        self.csv_generator.generate_questions_csv(questions, answers, general_csv)
        csv_files.append(general_csv)
        
        # Google表單CSV
        google_csv = os.path.join(output_dir, f"{base_name}{FILE_PATTERN_GOOGLE_CSV}")
        self.csv_generator.generate_google_form_csv(questions, answers, corrected_answers, google_csv)
        csv_files.append(google_csv)
        
        # 題組分類CSV
        group_csvs = self.csv_generator.generate_question_groups_csv(questions, answers, output_dir)
        csv_files.extend(group_csvs)
        
        return csv_files