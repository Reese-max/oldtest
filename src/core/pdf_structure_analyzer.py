#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF結構分析器 - 實現PDF布局特徵分析
"""

import os
import re
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

from ..utils.logger import logger
from .pdf_processor import PDFProcessor


class QuestionType(Enum):
    """題目類型枚舉"""

    ESSAY = "essay"  # 申論題
    CHOICE = "choice"  # 選擇題
    MIXED = "mixed"  # 混合格式
    COMPREHENSIVE = "comprehensive"  # 綜合格式
    EMBEDDED = "embedded"  # 嵌入式填空題
    UNKNOWN = "unknown"  # 未知格式


@dataclass
class StructureFeatures:
    """PDF結構特徵數據類"""

    # 基本資訊
    text_length: int
    page_count: int
    line_count: int

    # 格式檢測
    question_type: QuestionType
    has_essay_section: bool
    has_choice_section: bool
    has_mixed_format: bool

    # 題目統計
    question_count: int
    essay_question_count: int
    choice_question_count: int

    # 模式匹配
    question_patterns: List[Dict[str, Any]]
    option_patterns: List[Dict[str, Any]]
    answer_patterns: List[Dict[str, Any]]

    # 特殊字符
    special_characters: List[str]
    unicode_symbols: List[str]

    # 章節結構
    section_headers: List[str]
    subsection_headers: List[str]

    # 布局特徵
    has_table_structure: bool
    has_list_structure: bool
    has_numbered_sections: bool


class PDFStructureAnalyzer:
    """PDF結構分析器"""

    def __init__(self):
        self.pdf_processor = PDFProcessor()
        self.logger = logger

        # 預定義模式
        self.question_patterns = {
            "numbered": r"^\d+\s+",  # 數字開頭
            "chinese_numbered": r"第\d+題",  # 第X題
            "parentheses": r"\(\d+\)",  # (數字)
            "roman": r"^[IVX]+\.",  # 羅馬數字
            "letter": r"^[A-Z]\.",  # 字母開頭
        }

        self.option_patterns = {
            "letter_dot": r"[A-D]\.",  # A. B. C. D.
            "letter_paren": r"\([A-D]\)",  # (A) (B) (C) (D)
            "letter_paren_close": r"[A-D]\)",  # A) B) C) D)
            "number_dot": r"\d+\.",  # 1. 2. 3. 4.
            "unicode_symbols": r"[\ue18c-\ue18f]",  # Unicode選項符號
        }

        self.answer_patterns = {
            "answer_colon": r"答案：[A-D]",
            "correct_answer": r"正確答案：[A-D]",
            "standard_answer": r"標準答案：[A-D]",
            "answer_key": r"答案[A-D]",
        }

        self.section_patterns = {
            "chinese_sections": r"[甲乙丙丁戊己庚辛]、[^。\n]+",
            "number_sections": r"^\d+\.\s+",
            "letter_sections": r"^[A-Z]\.\s+",
        }

    def analyze_pdf_structure(self, pdf_path: str) -> StructureFeatures:
        """分析PDF結構特徵"""

        try:
            # 提取文本
            text = self.pdf_processor.extract_text(pdf_path)
            if not text:
                raise ValueError("無法提取PDF文本")

            # 基本統計
            text_length = len(text)
            page_count = self.pdf_processor.get_page_count(pdf_path)
            line_count = len(text.split("\n"))

            # 格式檢測
            question_type = self._detect_question_type(text, pdf_path)
            has_essay_section = self._has_essay_section(text)
            has_choice_section = self._has_choice_section(text)
            has_mixed_format = has_essay_section and has_choice_section

            # 題目統計
            question_count = self._count_questions(text)
            essay_question_count = self._count_essay_questions(text)
            choice_question_count = self._count_choice_questions(text)

            # 模式匹配
            question_patterns = self._analyze_question_patterns(text)
            option_patterns = self._analyze_option_patterns(text)
            answer_patterns = self._analyze_answer_patterns(text)

            # 特殊字符
            special_characters = self._find_special_characters(text)
            unicode_symbols = self._find_unicode_symbols(text)

            # 章節結構
            section_headers = self._find_section_headers(text)
            subsection_headers = self._find_subsection_headers(text)

            # 布局特徵
            has_table_structure = self._has_table_structure(text)
            has_list_structure = self._has_list_structure(text)
            has_numbered_sections = self._has_numbered_sections(text)

            return StructureFeatures(
                text_length=text_length,
                page_count=page_count,
                line_count=line_count,
                question_type=question_type,
                has_essay_section=has_essay_section,
                has_choice_section=has_choice_section,
                has_mixed_format=has_mixed_format,
                question_count=question_count,
                essay_question_count=essay_question_count,
                choice_question_count=choice_question_count,
                question_patterns=question_patterns,
                option_patterns=option_patterns,
                answer_patterns=answer_patterns,
                special_characters=special_characters,
                unicode_symbols=unicode_symbols,
                section_headers=section_headers,
                subsection_headers=subsection_headers,
                has_table_structure=has_table_structure,
                has_list_structure=has_list_structure,
                has_numbered_sections=has_numbered_sections,
            )

        except Exception as e:
            self.logger.error(f"PDF結構分析失敗 {pdf_path}: {e}")
            raise

    def _detect_question_type(self, text: str, pdf_path: str) -> QuestionType:
        """檢測題目類型"""

        filename = os.path.basename(pdf_path).lower()

        # 檢測綜合格式（申論+選擇）
        if "甲、申論題部分" in text and "乙、測驗題部分" in text:
            return QuestionType.COMPREHENSIVE

        # 檢測混合格式（作文+測驗）
        if "國文" in filename or "作文" in filename or ("作文部分" in text and "測驗部分" in text):
            return QuestionType.MIXED

        # 檢測嵌入式填空題
        if ("請依下文回答第" in text and "題至第" in text) and any(
            symbol in text for symbol in ["\ue18c", "\ue18d", "\ue18e", "\ue18f"]
        ):
            return QuestionType.EMBEDDED

        # 檢測申論題
        essay_indicators = ["申論題", "論述", "作文", "英文作文"]
        if any(indicator in text for indicator in essay_indicators):
            return QuestionType.ESSAY

        # 檢測選擇題
        choice_indicators = ["測驗題", "選擇題", "單選題", "測驗部分"]
        if any(indicator in text for indicator in choice_indicators):
            return QuestionType.CHOICE

        return QuestionType.UNKNOWN

    def _has_essay_section(self, text: str) -> bool:
        """檢測是否有申論題部分"""
        essay_indicators = ["甲、申論題部分", "申論題", "作文", "英文作文", "論述"]
        return any(indicator in text for indicator in essay_indicators)

    def _has_choice_section(self, text: str) -> bool:
        """檢測是否有選擇題部分"""
        choice_indicators = ["乙、測驗題部分", "測驗題", "選擇題", "單選題", "測驗部分"]
        return any(indicator in text for indicator in choice_indicators)

    def _count_questions(self, text: str) -> int:
        """統計題目總數"""
        total_count = 0

        # 統計各種題目模式
        for pattern_name, pattern in self.question_patterns.items():
            matches = re.findall(pattern, text, re.MULTILINE)
            total_count += len(matches)

        return total_count

    def _count_essay_questions(self, text: str) -> int:
        """統計申論題數量"""
        essay_patterns = [
            r"第\d+題.*?（.*?分）",  # 第X題（X分）
            r"^\d+\.\s+.*?（.*?分）",  # 數字. 題目（X分）
        ]

        count = 0
        for pattern in essay_patterns:
            matches = re.findall(pattern, text, re.MULTILINE)
            count += len(matches)

        return count

    def _count_choice_questions(self, text: str) -> int:
        """統計選擇題數量"""
        choice_patterns = [
            r"^\d+\s+.*?[A-D]\.",  # 數字開頭，包含選項
            r"第\d+題.*?[A-D]\.",  # 第X題，包含選項
        ]

        count = 0
        for pattern in choice_patterns:
            matches = re.findall(pattern, text, re.MULTILINE | re.DOTALL)
            count += len(matches)

        return count

    def _analyze_question_patterns(self, text: str) -> List[Dict[str, Any]]:
        """分析題目模式"""
        patterns = []

        for pattern_name, pattern in self.question_patterns.items():
            matches = re.findall(pattern, text, re.MULTILINE)
            if matches:
                patterns.append(
                    {"name": pattern_name, "pattern": pattern, "count": len(matches), "examples": matches[:5]}
                )

        return patterns

    def _analyze_option_patterns(self, text: str) -> List[Dict[str, Any]]:
        """分析選項模式"""
        patterns = []

        for pattern_name, pattern in self.option_patterns.items():
            matches = re.findall(pattern, text)
            if matches:
                patterns.append(
                    {"name": pattern_name, "pattern": pattern, "count": len(matches), "examples": matches[:5]}
                )

        return patterns

    def _analyze_answer_patterns(self, text: str) -> List[Dict[str, Any]]:
        """分析答案模式"""
        patterns = []

        for pattern_name, pattern in self.answer_patterns.items():
            matches = re.findall(pattern, text)
            if matches:
                patterns.append(
                    {"name": pattern_name, "pattern": pattern, "count": len(matches), "examples": matches[:5]}
                )

        return patterns

    def _find_special_characters(self, text: str) -> List[str]:
        """查找特殊字符"""
        special_chars = []

        # 查找非ASCII字符
        for char in text:
            if ord(char) > 127 and char not in special_chars:
                special_chars.append(char)

        return special_chars[:20]  # 限制數量

    def _find_unicode_symbols(self, text: str) -> List[str]:
        """查找Unicode符號"""
        unicode_symbols = ["\ue18c", "\ue18d", "\ue18e", "\ue18f"]
        found_symbols = []

        for symbol in unicode_symbols:
            if symbol in text:
                found_symbols.append(symbol)

        return found_symbols

    def _find_section_headers(self, text: str) -> List[str]:
        """查找章節標題"""
        headers = []

        for pattern_name, pattern in self.section_patterns.items():
            matches = re.findall(pattern, text)
            headers.extend(matches)

        return headers[:20]  # 限制數量

    def _find_subsection_headers(self, text: str) -> List[str]:
        """查找子章節標題"""
        subsection_patterns = [
            r"^\d+\.\d+\s+",  # 1.1, 1.2
            r"^\([一二三四五六七八九十]+\)",  # (一), (二)
        ]

        headers = []
        for pattern in subsection_patterns:
            matches = re.findall(pattern, text, re.MULTILINE)
            headers.extend(matches)

        return headers[:20]

    def _has_table_structure(self, text: str) -> bool:
        """檢測是否有表格結構"""
        table_indicators = [
            r"\|.*\|",  # 管道符分隔
            r"\+.*\+",  # 加號分隔
            r"^\s*\w+\s+\w+\s+\w+",  # 多列對齊
        ]

        for pattern in table_indicators:
            if re.search(pattern, text, re.MULTILINE):
                return True

        return False

    def _has_list_structure(self, text: str) -> bool:
        """檢測是否有列表結構"""
        list_indicators = [
            r"^\s*[•·▪▫]\s+",  # 項目符號
            r"^\s*[1-9]\.\s+",  # 數字列表
            r"^\s*[A-Z]\.\s+",  # 字母列表
        ]

        for pattern in list_indicators:
            if re.search(pattern, text, re.MULTILINE):
                return True

        return False

    def _has_numbered_sections(self, text: str) -> bool:
        """檢測是否有編號章節"""
        numbered_patterns = [
            r"^\d+\.\s+",  # 1. 2. 3.
            r"^第[一二三四五六七八九十百千萬]+章",  # 第一章
            r"^第[一二三四五六七八九十百千萬]+節",  # 第一節
        ]

        for pattern in numbered_patterns:
            if re.search(pattern, text, re.MULTILINE):
                return True

        return False

    def generate_structure_report(self, features: StructureFeatures, pdf_path: str) -> str:
        """生成結構分析報告"""

        report = f"# PDF結構分析報告\n\n"
        report += f"**文件路徑**: {pdf_path}\n\n"

        # 基本資訊
        report += f"## 基本資訊\n"
        report += f"- 文本長度: {features.text_length:,} 字元\n"
        report += f"- 頁數: {features.page_count}\n"
        report += f"- 行數: {features.line_count}\n\n"

        # 格式檢測
        report += f"## 格式檢測\n"
        report += f"- 題目類型: {features.question_type.value}\n"
        report += f"- 申論題部分: {'是' if features.has_essay_section else '否'}\n"
        report += f"- 選擇題部分: {'是' if features.has_choice_section else '否'}\n"
        report += f"- 混合格式: {'是' if features.has_mixed_format else '否'}\n\n"

        # 題目統計
        report += f"## 題目統計\n"
        report += f"- 總題數: {features.question_count}\n"
        report += f"- 申論題數: {features.essay_question_count}\n"
        report += f"- 選擇題數: {features.choice_question_count}\n\n"

        # 模式匹配
        report += f"## 模式匹配\n"

        if features.question_patterns:
            report += f"### 題目模式\n"
            for pattern in features.question_patterns:
                report += f"- {pattern['name']}: {pattern['count']} 個\n"
            report += f"\n"

        if features.option_patterns:
            report += f"### 選項模式\n"
            for pattern in features.option_patterns:
                report += f"- {pattern['name']}: {pattern['count']} 個\n"
            report += f"\n"

        if features.answer_patterns:
            report += f"### 答案模式\n"
            for pattern in features.answer_patterns:
                report += f"- {pattern['name']}: {pattern['count']} 個\n"
            report += f"\n"

        # 特殊字符
        if features.special_characters:
            report += f"## 特殊字符\n"
            report += f"- 特殊字符: {len(features.special_characters)} 個\n"
            report += f"- Unicode符號: {features.unicode_symbols}\n\n"

        # 章節結構
        if features.section_headers:
            report += f"## 章節結構\n"
            report += f"- 章節標題: {len(features.section_headers)} 個\n"
            report += f"- 子章節標題: {len(features.subsection_headers)} 個\n\n"

        # 布局特徵
        report += f"## 布局特徵\n"
        report += f"- 表格結構: {'是' if features.has_table_structure else '否'}\n"
        report += f"- 列表結構: {'是' if features.has_list_structure else '否'}\n"
        report += f"- 編號章節: {'是' if features.has_numbered_sections else '否'}\n\n"

        return report
