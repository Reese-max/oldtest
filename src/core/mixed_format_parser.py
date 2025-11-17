#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
混合格式处理器
处理包含作文和选择题的混合格式（如国文作文与测验）
"""

import re
from typing import List, Dict, Any, Tuple
from ..utils.logger import logger
from ..utils.regex_patterns import EMBEDDED_SYMBOLS


class MixedFormatParser:
    """混合格式处理器"""
    
    def __init__(self):
        self.logger = logger
    
    def parse_mixed_format(self, text: str) -> List[Dict[str, Any]]:
        """
        解析混合格式题目
        
        Args:
            text: PDF提取的文字
            
        Returns:
            题目列表
        """
        self.logger.info("开始解析混合格式题目")
        
        questions = []
        
        # 1. 解析作文部分
        essay_questions = self._parse_essay_section(text)
        questions.extend(essay_questions)
        
        # 2. 解析测验部分
        test_questions = self._parse_test_section(text)
        questions.extend(test_questions)
        
        self.logger.success(f"混合格式解析完成，共 {len(questions)} 题")
        return questions
    
    def _parse_essay_section(self, text: str) -> List[Dict[str, Any]]:
        """解析作文部分"""
        self.logger.info("解析作文部分")
        
        # 找到作文部分
        essay_start = text.find('甲、作文部分')
        test_start = text.find('乙、測驗部分')
        
        if essay_start == -1 or test_start == -1:
            self.logger.warning("未找到作文或测验部分标记")
            return []
        
        essay_text = text[essay_start:test_start]
        
        # 提取作文题目
        questions = []
        
        # 查找子题标记（一、二、等）
        sub_question_pattern = r'[一二三四五六七八九十]+、(.+?)(?=[一二三四五六七八九十]+、|$)'
        matches = re.finditer(sub_question_pattern, essay_text, re.DOTALL)
        
        for i, match in enumerate(matches, 1):
            question_content = match.group(1).strip()
            
            # 清理题目内容
            question_content = self._clean_question_text(question_content)
            
            # 提取分数信息
            score_match = re.search(r'（(\d+)\s*分）', question_content)
            score = score_match.group(1) if score_match else "未指定"
            
            # 移除分数信息，保留纯题目
            question_text = re.sub(r'（\d+\s*分）', '', question_content).strip()
            
            question_data = {
                '题号': f'作文{i}',
                '题目': question_text,
                '题型': '作文题',
                '分数': score,
                '题组': True,
                '题组编号': 'essay_section',
                '选项A': '',
                '选项B': '',
                '选项C': '',
                '选项D': '',
            }
            
            questions.append(question_data)
            self.logger.info(f"提取作文题 {i}: {question_text[:50]}...")
        
        return questions
    
    def _parse_test_section(self, text: str) -> List[Dict[str, Any]]:
        """解析测验部分"""
        self.logger.info("解析测验部分")
        
        # 找到测验部分
        test_start = text.find('乙、測驗部分')
        if test_start == -1:
            self.logger.warning("未找到测验部分")
            return []
        
        test_text = text[test_start:]
        
        # 提取选择题
        questions = []
        
        # 按行分割，逐行分析
        lines = test_text.split('\n')
        current_question = None
        current_options = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # 检查是否是题目行（以数字开头）
            if re.match(r'^\d+', line):
                # 保存前一个题目
                if current_question and len(current_options) >= 4:
                    current_question['选项A'] = current_options[0] if len(current_options) > 0 else ''
                    current_question['选项B'] = current_options[1] if len(current_options) > 1 else ''
                    current_question['选项C'] = current_options[2] if len(current_options) > 2 else ''
                    current_question['选项D'] = current_options[3] if len(current_options) > 3 else ''
                    questions.append(current_question)
                
                # 开始新题目
                question_num = re.match(r'^(\d+)', line).group(1)
                question_text = re.sub(r'^\d+\s*', '', line)
                question_text = self._clean_question_text(question_text)
                
                current_question = {
                    '题号': question_num,
                    '题目': question_text,
                    '题型': '选择题',
                    '分数': '2',
                    '题组': True,
                    '题组编号': 'test_section',
                    '选项A': '',
                    '选项B': '',
                    '选项C': '',
                    '选项D': '',
                }
                current_options = []
                
            # 检查是否是选项行（包含特殊字符）
            elif re.search(r'[]', line):
                options = self._extract_test_options(line)
                current_options.extend(options)
        
        # 处理最后一个题目
        if current_question and len(current_options) >= 4:
            current_question['选项A'] = current_options[0] if len(current_options) > 0 else ''
            current_question['选项B'] = current_options[1] if len(current_options) > 1 else ''
            current_question['选项C'] = current_options[2] if len(current_options) > 2 else ''
            current_question['选项D'] = current_options[3] if len(current_options) > 3 else ''
            questions.append(current_question)
        
        for q in questions:
            self.logger.info(f"提取选择题 {q['题号']}: {q['题目'][:50]}...")
        
        return questions
    
    def _extract_test_options(self, question_text: str) -> List[str]:
        """提取测验题选项"""
        options = []
        
        # 查找选项模式：特殊字符 + 选项内容
        option_pattern = r'[](\s*[^]+?)(?=[]|$)'
        matches = re.finditer(option_pattern, question_text)
        
        for match in matches:
            option_text = match.group(1).strip()
            if option_text:
                options.append(option_text)
        
        return options
    
    def _clean_question_text(self, text: str) -> str:
        """清理题目文本"""
        # 移除多余的空白字符
        text = re.sub(r'\s+', ' ', text)
        
        # 移除特殊标记
        # 移除特殊标记（選項符號）
        for symbol in EMBEDDED_SYMBOLS:
            text = text.replace(symbol, '')
        # 移除页次信息
        text = re.sub(r'頁次：\d+－\d+', '', text)
        text = re.sub(r'代號：[\d\-]+', '', text)
        
        return text.strip()
    
    def validate_questions(self, questions: List[Dict[str, Any]]) -> Tuple[bool, str]:
        """验证题目完整性"""
        if not questions:
            return False, "未提取到任何题目"
        
        # 检查题目类型分布
        essay_count = sum(1 for q in questions if q['题型'] == '作文题')
        choice_count = sum(1 for q in questions if q['题型'] == '选择题')
        
        self.logger.info(f"题目分布: 作文题 {essay_count} 题, 选择题 {choice_count} 题")
        
        # 检查作文题
        essay_questions = [q for q in questions if q['题型'] == '作文题']
        if essay_questions:
            for q in essay_questions:
                if not q['题目'].strip():
                    return False, f"作文题 {q['题号']} 内容为空"
        
        # 检查选择题
        choice_questions = [q for q in questions if q['题型'] == '选择题']
        if choice_questions:
            for q in choice_questions:
                option_count = sum(1 for opt in ['A', 'B', 'C', 'D'] 
                                 if q.get(f'选项{opt}', '').strip())
                if option_count < 2:
                    return False, f"选择题 {q['题号']} 选项不完整"
        
        return True, f"完整提取{len(questions)}题（作文{essay_count}题，选择{choice_count}题）"
