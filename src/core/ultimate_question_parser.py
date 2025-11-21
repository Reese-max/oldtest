#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
終極題目解析器 - 處理所有格式的60題
"""

import os
import re
from typing import Any, Dict, List, Tuple

from ..utils.logger import logger
from ..utils.regex_patterns import EMBEDDED_SYMBOLS


class UltimateQuestionParser:
    """終極題目解析器 - 處理所有格式"""

    def __init__(self):
        self.logger = logger

    def parse_all_60_questions(self, text: str, pdf_path: str) -> List[Dict[str, Any]]:
        """解析所有60題"""
        questions = []

        # 1. 解析申論題（第1-2題實際上是英文作文）
        essay_questions = self._parse_essay_questions(text)
        questions.extend(essay_questions)

        # 2. 解析測驗題部分的所有題目（第1-60題）
        test_questions = self._parse_all_test_questions(text)
        questions.extend(test_questions)

        self.logger.info(f"✅ 終極解析完成：申論題 {len(essay_questions)} 題，測驗題 {len(test_questions)} 題")

        return questions

    def _parse_essay_questions(self, text: str) -> List[Dict[str, Any]]:
        """解析申論題"""
        questions = []

        # 尋找英文作文題目
        essay_pattern = r"英文作文：\s*(.*?)(?=第\d+題|乙、測驗題|$)"
        match = re.search(essay_pattern, text, re.DOTALL)

        if match:
            question_text = match.group(1).strip()
            if len(question_text) > 50:
                questions.append(
                    {
                        "題號": "申論題",
                        "題目": question_text,
                        "題型": "申論題",
                        "選項A": "",
                        "選項B": "",
                        "選項C": "",
                        "選項D": "",
                        "正確答案": "",
                        "分數": 25,
                        "題組": False,
                        "題組編號": "",
                    }
                )
                self.logger.info(f"✓ 提取申論題: {question_text[:50]}...")

        return questions

    def _parse_all_test_questions(self, text: str) -> List[Dict[str, Any]]:
        """解析測驗題部分的所有題目"""
        questions = []

        # 找到測驗題部分
        test_section_match = re.search(r"乙、測驗題部分.*?(?=請依下文回答|$)", text, re.DOTALL)
        if not test_section_match:
            return questions

        test_section = test_section_match.group()

        # 1. 先處理題組題（51-60題）
        group_questions = self._parse_group_questions(text)
        questions.extend(group_questions)

        # 2. 處理標準題（1-50題）
        question_pattern = r"^\s*(\d+)\.?\s+(.+?)(?=^\s*\d+\.?\s+|$)"
        matches = re.finditer(question_pattern, test_section, re.MULTILINE | re.DOTALL)

        for match in matches:
            question_num = int(match.group(1))
            if 1 <= question_num <= 50:  # 只處理1-50題
                question_text = match.group(2).strip()

                # 清理題目文本
                question_text = self._clean_question_text(question_text)

                # 提取選項
                options = self._extract_options_for_question(test_section, question_num)

                # 降低選項要求：只要有選項就接受
                if len(options) >= 2:  # 降低到2個選項
                    # 確保有4個選項
                    while len(options) < 4:
                        options.append("")

                    questions.append(
                        {
                            "題號": str(question_num),
                            "題目": question_text,
                            "題型": "選擇題",
                            "選項A": options[0],
                            "選項B": options[1],
                            "選項C": options[2],
                            "選項D": options[3],
                            "正確答案": "",
                            "分數": 1.25,
                            "題組": False,
                            "題組編號": "",
                        }
                    )
                    self.logger.info(
                        f"✓ 提取測驗題 {question_num}: {question_text[:30]}... (選項: {len([o for o in options if o])})"
                    )

        return questions

    def _clean_question_text(self, text: str) -> str:
        """清理題目文本"""
        # 移除多餘的空白
        text = re.sub(r"\s+", " ", text)
        # 移除開頭的數字和空格
        text = re.sub(r"^\d+\s+", "", text)
        return text.strip()

    def _extract_options_for_question(self, test_section: str, question_num: int) -> List[str]:
        """為特定題號提取選項"""
        lines = test_section.split("\n")

        # 找到題目所在的行
        question_line_idx = -1
        for i, line in enumerate(lines):
            # Handle both "1. " and "1 " formats
            if line.strip().startswith(f"{question_num}. ") or line.strip().startswith(f"{question_num} "):
                question_line_idx = i
                break

        if question_line_idx == -1:
            return []

        options = []

        # 從題目行開始，向後查找選項
        for i in range(question_line_idx + 1, min(question_line_idx + 10, len(lines))):
            line = lines[i].strip()

            # 如果遇到下一題，停止
            if re.match(r"^\d+\.?\s+", line):
                break

            if not line:
                continue

            # 處理選項行
            line_options = self._parse_option_line(line)
            options.extend(line_options)

            # 如果已經找到4個選項，停止
            if len(options) >= 4:
                break

        # 如果選項不足，嘗試在同一行查找
        if len(options) < 4:
            question_line = lines[question_line_idx].strip()
            # 檢查題目行是否包含選項
            if any(c in question_line for c in ["", "", "", ""]):
                line_options = self._parse_option_line(question_line)
                options.extend(line_options)

        return options[:4]

    def _parse_group_questions(self, text: str) -> List[Dict[str, Any]]:
        """解析題組題（51-60題）"""
        questions = []

        # 尋找題組標記
        group_pattern = r"請依下文回答第(\d+)題至第(\d+)題"
        matches = re.finditer(group_pattern, text)

        for match in matches:
            start_num = int(match.group(1))
            end_num = int(match.group(2))

            self.logger.info(f"找到題組: 第{start_num}題至第{end_num}題")

            # 提取題組內容（擴大範圍以包含所有題目）
            group_start = match.end()
            group_text = text[group_start : group_start + 4000]  # 取4000字元

            # 生成題組編號
            group_id = f"group_{start_num}_{end_num}"

            # 解析題組中的每個題目
            for question_num in range(start_num, end_num + 1):
                # 檢查是否為填空題格式（如：51 thereaderwouldgetforacceptingtheoffer）
                if f"{question_num} " in group_text:
                    pos = group_text.find(f"{question_num} ")
                    question_text = group_text[pos : pos + 200].strip()

                    # 清理題目文本
                    question_text = self._clean_question_text(question_text)

                    # 檢查是否為填空題（題目文本本身沒有選項符號）
                    # 只檢查題目文本的前100字元，避免檢查到後面的選項
                    question_part = question_text[:100]
                    # 使用從 regex_patterns 引入的 Unicode 字符
                    if not any(c in question_part for c in EMBEDDED_SYMBOLS):
                        # 填空題：創建標準選項
                        questions.append(
                            {
                                "題號": str(question_num),
                                "題目": f"第{question_num}題填空",
                                "題型": "填空題",
                                "選項A": "A",
                                "選項B": "B",
                                "選項C": "C",
                                "選項D": "D",
                                "正確答案": "",
                                "分數": 1.25,
                                "題組": True,
                                "題組編號": group_id,
                            }
                        )
                        self.logger.info(f"✓ 提取填空題 {question_num}: 填空題格式")
                    else:
                        # 標準選擇題
                        options = self._extract_options_for_question(group_text, question_num)

                        if len(options) >= 2:
                            # 確保有4個選項
                            while len(options) < 4:
                                options.append("")

                            questions.append(
                                {
                                    "題號": str(question_num),
                                    "題目": question_text,
                                    "題型": "選擇題",
                                    "選項A": options[0],
                                    "選項B": options[1],
                                    "選項C": options[2],
                                    "選項D": options[3],
                                    "正確答案": "",
                                    "分數": 1.25,
                                    "題組": True,
                                    "題組編號": group_id,
                                }
                            )
                            self.logger.info(
                                f"✓ 提取題組題 {question_num}: {question_text[:30]}... (選項: {len([o for o in options if o])})"
                            )

        return questions

    def _parse_option_line(self, line: str) -> List[str]:
        """解析選項行"""
        options = []

        # 首先檢查標準格式: (A) 選項內容 or （A） 選項內容
        standard_pattern = r'[（(]([ABCD])[）)]\s*([^（(]+)'
        standard_matches = list(re.finditer(standard_pattern, line))
        if standard_matches:
            for match in standard_matches:
                content = match.group(2).strip()
                if content:
                    options.append(content)
            return options

        # 定義選項符號（使用Unicode碼點）
        option_symbols = ["\ue18c", "\ue18d", "\ue18e", "\ue18f"]

        # 檢查是否包含選項符號
        has_symbols = any(symbol in line for symbol in option_symbols)

        if has_symbols:
            # 提取所有選項
            for symbol in option_symbols:
                if symbol in line:
                    positions = [i for i, char in enumerate(line) if char == symbol]
                    for pos in positions:
                        start = pos + 1
                        end = len(line)

                        # 找到下一個符號的位置
                        for next_symbol in option_symbols:
                            next_pos = line.find(next_symbol, start)
                            if next_pos != -1 and next_pos < end:
                                end = next_pos

                        content = line[start:end].strip()
                        if content:
                            options.append(content)

        # 如果沒有符號，嘗試空格分隔
        elif " " in line:
            parts = line.split()
            if len(parts) >= 4:
                for part in parts:
                    if part and len(part) > 1 and not part.isdigit():
                        options.append(part)
            else:
                if line and len(line) > 1:
                    options.append(line)

        # 單個選項
        else:
            if line and len(line) > 1:
                options.append(line)

        return options
