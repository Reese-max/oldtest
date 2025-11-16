#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
嵌入式填空题解析器
处理题号嵌入在文本中的特殊格式（如英文完形填空）
"""

import re
from typing import List, Dict, Any, Tuple
from ..utils.logger import logger


class EmbeddedQuestionParser:
    """嵌入式填空题解析器"""
    
    def __init__(self):
        self.logger = logger
    
    def parse_embedded_questions(self, text: str) -> List[Dict[str, Any]]:
        """
        解析嵌入式填空题
        
        Args:
            text: PDF提取的文字
            
        Returns:
            题目列表
        """
        self.logger.info("开始解析嵌入式填空题")
        
        # 检测题组
        question_groups = self._detect_question_groups(text)
        
        if not question_groups:
            self.logger.warning("未检测到题组")
            return []
        
        questions = []
        for group in question_groups:
            group_questions = self._parse_group(text, group)
            questions.extend(group_questions)
        
        self.logger.success(f"嵌入式填空题解析完成，共 {len(questions)} 题")
        return questions
    
    def _detect_question_groups(self, text: str) -> List[Dict[str, Any]]:
        """检测题组范围"""
        groups = []
        
        # 题组标记模式
        patterns = [
            r'请依下文回答第(\d+)题至第(\d+)题[：:]?',
            r'請依下文回答第(\d+)題至第(\d+)題[：:]?',
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, text)
            for match in matches:
                start_num = int(match.group(1))
                end_num = int(match.group(2))
                
                groups.append({
                    'start': start_num,
                    'end': end_num,
                    'marker_pos': match.start(),
                    'marker_end': match.end()
                })
        
        return groups
    
    def _parse_group(self, text: str, group: Dict[str, Any]) -> List[Dict[str, Any]]:
        """解析单个题组"""
        start_num = group['start']
        end_num = group['end']
        marker_pos = group['marker_pos']
        
        self.logger.info(f"解析题组: 第{start_num}题至第{end_num}题")
        
        # 提取题组内容（从标记开始到下一个题组或文档结束）
        # 需要包含选项行，所以范围要更大
        next_group_pattern = r'请依下文回答第\d+题至第\d+题|請依下文回答第\d+題至第\d+題'
        next_match = re.search(next_group_pattern, text[marker_pos + 200:])
        
        if next_match:
            group_end = marker_pos + 200 + next_match.start()
        else:
            group_end = len(text)
        
        group_text = text[marker_pos:group_end]
        
        # 题组文本已提取
        
        # 提取所有题号和选项
        questions = []
        for question_num in range(start_num, end_num + 1):
            # 在group_text中寻找选项行
            options = self._extract_options_for_question(group_text, question_num)
            
            if len(options) >= 4:
                # 在文本中找到题号的上下文
                pattern = rf'\s+{question_num}\s+'
                match = re.search(pattern, group_text)
                
                if match:
                    # 提取上下文
                    context_start = max(0, match.start() - 150)
                    context_end = min(len(group_text), match.end() + 150)
                    question_context = group_text[context_start:context_end].strip()
                else:
                    question_context = f"第{question_num}题"
                
                question_data = {
                    '题号': str(question_num),
                    '题目': question_context,
                    '题型': '选择题',
                    '选项A': options[0],
                    '选项B': options[1],
                    '选项C': options[2],
                    '选项D': options[3],
                    '题组': True,
                    '题组编号': f'{start_num}-{end_num}',
                }
                
                questions.append(question_data)
            else:
                self.logger.warning(f"题号 {question_num} 选项不足: {len(options)}")
        
        return questions
    
    def _extract_passage(self, group_text: str, start_num: int, end_num: int) -> str:
        """提取题干段落（包含嵌入题号的部分）"""
        # 找到第一个题号出现的位置之前的所有内容
        # 通常嵌入题号的段落会在选项之前
        
        # 分割成行
        lines = group_text.split('\n')
        passage_lines = []
        
        for line in lines:
            # 如果这行包含嵌入的题号（如 " 41 " 在英文句子中）
            # 或者是题干的一部分
            has_embedded_num = bool(re.search(rf'\s+\d{{1,2}}\s+', line))
            
            # 检查是否为选项行（四个单词排列）
            words = line.strip().split()
            is_option_line = (
                len(words) == 4 and 
                all(len(w) > 2 and w[0].islower() for w in words)
            )
            
            if is_option_line:
                break  # 遇到选项行，停止收集题干
            
            if has_embedded_num or len(passage_lines) > 0:
                passage_lines.append(line)
        
        passage = '\n'.join(passage_lines)
        return passage
    
    def _extract_single_question(self, group_text: str, passage: str, 
                                 question_num: int) -> Dict[str, Any]:
        """提取单个题目"""
        
        # 在passage中定位题号
        # 模式：空格 + 数字 + 空格（题号嵌入在英文句子中）
        pattern = rf'\s+{question_num}\s+'
        match = re.search(pattern, passage)
        
        if not match:
            self.logger.warning(f"未找到题号 {question_num} 在题干中的位置")
            return None
        
        # 提取上下文作为题目内容
        context_start = max(0, match.start() - 100)
        context_end = min(len(passage), match.end() + 100)
        question_context = passage[context_start:context_end].strip()
        
        # 提取选项
        options = self._extract_options_for_question(group_text, question_num)
        
        if len(options) < 2:
            self.logger.warning(f"题号 {question_num} 选项不足")
            return None
        
        question_data = {
            '题号': str(question_num),
            '题目': question_context,
            '题型': '选择题',
            '选项A': options[0] if len(options) > 0 else '',
            '选项B': options[1] if len(options) > 1 else '',
            '选项C': options[2] if len(options) > 2 else '',
            '选项D': options[3] if len(options) > 3 else '',
            '题组': True,
            '题组编号': f'embedded_{question_num}',
        }
        
        return question_data
    
    def _extract_options_for_question(self, group_text: str, 
                                      question_num: int) -> List[str]:
        """提取特定题号的选项"""
        # 在文本中找到题号行
        # 格式：题号在开头，后面跟着4个单词选项
        
        lines = group_text.split('\n')
        
        for line in lines:
            line_stripped = line.strip()
            
            # 模式：题号 + 四个单词（空格分隔）
            # 例如：41 compressed abridged extended abbreviated
            # 注意：选项可能包含特殊字符如   等
            pattern = rf'^{question_num}\s+([^\s]+)\s+([^\s]+)\s+([^\s]+)\s+([^\s]+)\s*$'
            match = re.match(pattern, line_stripped)
            
            if match:
                options = [match.group(i) for i in range(1, 5)]
                self.logger.info(f"找到题号 {question_num} 的选项: {options}")
                return options
        
        # 如果没找到，尝试宽松匹配
        for line in lines:
            if line.strip().startswith(str(question_num) + ' '):
                # 提取题号后的所有单词
                parts = line.strip().split()
                if len(parts) >= 5:  # 题号 + 4个选项
                    options = [p for p in parts[1:5] if p.isalpha()]
                    if len(options) == 4:
                        self.logger.info(f"宽松匹配找到题号 {question_num} 的选项: {options}")
                        return options
        
        return []
    
    def validate_questions(self, questions: List[Dict[str, Any]]) -> Tuple[bool, str]:
        """验证题目完整性"""
        if not questions:
            return False, "未提取到任何题目"
        
        # 检查题号连续性
        question_nums = sorted([int(q['题号']) for q in questions])
        expected_nums = list(range(question_nums[0], question_nums[-1] + 1))
        
        if question_nums != expected_nums:
            missing = set(expected_nums) - set(question_nums)
            return False, f"题号不连续，可能遗漏: {sorted(missing)}"
        
        # 检查选项完整性
        incomplete = []
        for q in questions:
            option_count = sum(1 for opt in ['A', 'B', 'C', 'D'] 
                             if q.get(f'选项{opt}', '').strip())
            if option_count < 2:
                incomplete.append(q['题号'])
        
        if incomplete:
            return False, f"以下题目选项不完整: {incomplete}"
        
        return True, f"完整提取{len(questions)}题"

