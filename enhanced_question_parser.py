#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
增強版題目解析器 - 改進題目解析邏輯
提供更精確的題目識別、解析和驗證功能
"""

import re
import logging
from typing import List, Dict, Any, Optional, Tuple, Set
from datetime import datetime
import json

class EnhancedQuestionParser:
    """增強版題目解析器"""
    
    def __init__(self):
        self.logger = logging.getLogger('EnhancedQuestionParser')
        self.question_patterns = self._init_question_patterns()
        self.filter_keywords = self._init_filter_keywords()
        self.question_indicators = self._init_question_indicators()
        self.option_extractor = None  # 將在需要時初始化
    
    def _init_question_patterns(self) -> List[Dict[str, Any]]:
        """初始化題目檢測模式"""
        return [
            # 標準題目格式
            {
                'pattern': r'第(\d+)題[：:]?\s*(.*?)(?=第\d+題|$)',
                'type': 'numbered_standard',
                'priority': 1,
                'description': '標準編號格式 第X題'
            },
            {
                'pattern': r'(\d+)\.\s*(.*?)(?=\d+\.|$)',
                'type': 'dot_numbered',
                'priority': 1,
                'description': '點號編號格式 X.'
            },
            {
                'pattern': r'^(\d+)\s+(.*?)(?=^\d+\s+|$)',
                'type': 'space_numbered',
                'description': '空格編號格式 X 題目'
            },
            
            # 真實考古題格式
            {
                'pattern': r'^(\d+)\s+(.*?)(?=^\d+\s+|$)',
                'type': 'real_exam',
                'priority': 2,
                'description': '真實考古題格式'
            },
            
            # 括號格式
            {
                'pattern': r'(\d+)\s*[（(]\s*.*?\s*[）)]\s*(.*?)(?=\d+\s*[（(]|$)',
                'type': 'parentheses',
                'priority': 3,
                'description': '括號格式 (X) 題目'
            },
            
            # 冒號格式
            {
                'pattern': r'(\d+)\s*[：:]\s*(.*?)(?=\d+\s*[：:]|$)',
                'type': 'colon',
                'priority': 3,
                'description': '冒號格式 X: 題目'
            }
        ]
    
    def _init_filter_keywords(self) -> Set[str]:
        """初始化過濾關鍵詞"""
        return {
            '代號', '頁次', '考試', '科目', '時間', '座號', '注意', '禁止', '使用',
            '本試題', '單一選擇題', '選出', '適當', '答案', '共', '每題',
            '須用', '鉛筆', '試卡', '依題號', '清楚', '劃記', '作答者', '不予', '計分',
            '試題說明', '作答注意事項', '考試規則', '評分標準', '考試時間',
            '姓名', '准考證號', '班級', '學號', '日期', '年', '月', '日',
            '請在', '請將', '請依', '請根據', '請參考', '請注意', '請務必',
            '以下', '上述', '下列', '上文', '下文', '前述', '後述',
            '說明', '注意', '提醒', '警告', '重要', '特別', '必須', '應該'
        }
    
    def _init_question_indicators(self) -> Set[str]:
        """初始化題目指示詞"""
        return {
            '？', '?', '什麼', '何者', '何種', '哪個', '哪一', '哪個是', '哪一個',
            '如何', '怎樣', '為什麼', '為何', '何故', '原因', '理由',
            '正確', '錯誤', '適當', '不當', '合適', '不合適',
            '最', '最適', '最佳', '最不', '最可能', '最不可能',
            '主要', '次要', '重要', '不重要', '關鍵', '核心',
            '根據', '依據', '按照', '依照', '根據', '基於',
            '下列', '以下', '上述', '上文', '下文', '前述', '後述',
            '何時', '何地', '何人', '何事', '何物', '何因', '何果'
        }
    
    def parse_questions(self, text: str, min_question_length: int = 10, 
                       max_question_length: int = 1000) -> List[Dict[str, Any]]:
        """
        解析題目 - 主要方法
        
        Args:
            text: 包含題目的文字內容
            min_question_length: 最小題目長度
            max_question_length: 最大題目長度
            
        Returns:
            解析的題目列表
        """
        self.logger.info(f"開始解析題目，文字長度: {len(text)}")
        
        # 預處理文字
        processed_text = self._preprocess_text(text)
        
        # 檢測題組
        question_groups = self._detect_question_groups(processed_text)
        
        if question_groups:
            self.logger.info(f"檢測到 {len(question_groups)} 個題組")
            questions = self._parse_question_groups(processed_text, question_groups)
        else:
            self.logger.info("未檢測到題組，解析一般題目")
            questions = self._parse_regular_questions(processed_text, min_question_length, max_question_length)
        
        # 後處理和驗證
        validated_questions = self._post_process_questions(questions, min_question_length, max_question_length)
        
        self.logger.info(f"題目解析完成: {len(validated_questions)} 題")
        return validated_questions
    
    def _preprocess_text(self, text: str) -> str:
        """預處理文字"""
        # 移除多餘的空白行
        text = re.sub(r'\n\s*\n', '\n', text)
        
        # 移除頁碼
        text = re.sub(r'第\s*\d+\s*頁', '', text)
        text = re.sub(r'頁次：\s*\d+', '', text)
        
        # 統一換行符
        text = text.replace('\r\n', '\n').replace('\r', '\n')
        
        return text.strip()
    
    def _detect_question_groups(self, text: str) -> List[Dict[str, Any]]:
        """檢測題組"""
        question_groups = []
        
        # 題組檢測模式
        group_patterns = [
            r'請依下文回答第(\d+)題至第(\d+)題',
            r'請根據下列文章回答第(\d+)題至第(\d+)題',
            r'閱讀下文，回答第(\d+)題至第(\d+)題',
            r'根據下列文章，回答第(\d+)題至第(\d+)題',
            r'請根據下文回答第(\d+)題至第(\d+)題'
        ]
        
        for pattern in group_patterns:
            matches = re.finditer(pattern, text, re.MULTILINE | re.DOTALL)
            for match in matches:
                start_num = int(match.group(1))
                end_num = int(match.group(2))
                
                if self._validate_question_range(start_num, end_num):
                    question_groups.append({
                        'start': start_num,
                        'end': end_num,
                        'pattern': pattern,
                        'match_start': match.start(),
                        'match_end': match.end()
                    })
        
        return question_groups
    
    def _validate_question_range(self, start_num: int, end_num: int) -> bool:
        """驗證題號範圍"""
        if start_num <= 0 or end_num <= 0:
            return False
        if start_num > end_num:
            return False
        if end_num - start_num > 20:  # 題組不應超過20題
            return False
        return True
    
    def _parse_question_groups(self, text: str, question_groups: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """解析題組題目"""
        questions = []
        
        for group in question_groups:
            start_num = group['start']
            end_num = group['end']
            
            self.logger.info(f"解析題組: 第{start_num}題至第{end_num}題")
            
            # 提取題組內容
            group_content = self._extract_group_content(text, group)
            
            # 解析題組中的個別題目
            group_questions = self._parse_group_questions(group_content, start_num, end_num)
            questions.extend(group_questions)
        
        return questions
    
    def _extract_group_content(self, text: str, group: Dict[str, Any]) -> str:
        """提取題組內容"""
        start_pos = group['match_start']
        
        # 尋找下一個題組或文檔結束
        next_group_pattern = r'請依.*?回答第\d+題至第\d+題|請根據.*?回答第\d+題至第\d+題|閱讀.*?回答第\d+題至第\d+題'
        next_match = re.search(next_group_pattern, text[start_pos + 100:])
        
        if next_match:
            end_pos = start_pos + 100 + next_match.start()
        else:
            end_pos = len(text)
        
        return text[start_pos:end_pos]
    
    def _parse_group_questions(self, group_content: str, start_num: int, end_num: int) -> List[Dict[str, Any]]:
        """解析題組中的個別題目"""
        questions = []
        
        for question_num in range(start_num, end_num + 1):
            question_data = {
                '題號': str(question_num),
                '題目': '',
                '選項A': '',
                '選項B': '',
                '選項C': '',
                '選項D': '',
                '題型': '選擇題',
                '題組': True,
                '題組編號': f"{start_num}-{end_num}",
                '題組內容': group_content[:200] + '...' if len(group_content) > 200 else group_content
            }
            
            # 提取題目內容
            question_text = self._extract_question_text_from_group(group_content, question_num)
            if question_text:
                question_data['題目'] = question_text
                
                # 提取選項
                options = self._extract_options_from_question(question_text)
                for i, option in enumerate(['A', 'B', 'C', 'D']):
                    if i < len(options):
                        question_data[f'選項{option}'] = options[i]
            
            questions.append(question_data)
        
        return questions
    
    def _extract_question_text_from_group(self, group_content: str, question_num: int) -> str:
        """從題組中提取題目文字"""
        # 尋找題目模式
        question_patterns = [
            rf'{question_num}\s*[：:]\s*(.*?)(?={question_num+1}\s*[：:]|$)',
            rf'第{question_num}題[：:]?\s*(.*?)(?=第{question_num+1}題|$)',
            rf'{question_num}\.\s*(.*?)(?={question_num+1}\.|$)',
        ]
        
        for pattern in question_patterns:
            match = re.search(pattern, group_content, re.DOTALL)
            if match:
                return match.group(1).strip()
        
        return ""
    
    def _parse_regular_questions(self, text: str, min_length: int, max_length: int) -> List[Dict[str, Any]]:
        """解析一般題目"""
        questions = []
        
        # 按優先級排序模式
        sorted_patterns = sorted(self.question_patterns, key=lambda x: x.get('priority', 999))
        
        for pattern_info in sorted_patterns:
            pattern = pattern_info['pattern']
            pattern_type = pattern_info['type']
            
            try:
                matches = re.finditer(pattern, text, re.MULTILINE | re.DOTALL)
                
                for match in matches:
                    question_num = match.group(1)
                    question_text = match.group(2).strip()
                    
                    # 過濾非題目內容
                    if self._is_not_a_question(question_num, question_text):
                        continue
                    
                    if len(question_text) < min_length or len(question_text) > max_length:
                        continue
                    
                    question_data = {
                        '題號': question_num,
                        '題目': question_text,
                        '選項A': '',
                        '選項B': '',
                        '選項C': '',
                        '選項D': '',
                        '題型': '選擇題',
                        '題組': False,
                        '解析模式': pattern_type
                    }
                    
                    # 提取選項
                    options = self._extract_options_from_question(question_text)
                    for i, option in enumerate(['A', 'B', 'C', 'D']):
                        if i < len(options):
                            question_data[f'選項{option}'] = options[i]
                    
                    questions.append(question_data)
                    
            except re.error as e:
                self.logger.warning(f"正則表達式錯誤: {pattern} - {e}")
                continue
        
        return questions
    
    def _is_not_a_question(self, question_num: str, question_text: str) -> bool:
        """判斷是否不是題目"""
        # 過濾代號
        if len(question_num) > 3:
            return True
        
        # 過濾包含特定關鍵詞的內容
        for keyword in self.filter_keywords:
            if keyword in question_text:
                return True
        
        # 過濾太短的內容
        if len(question_text) < 10:
            return True
        
        # 檢查是否包含題目指示詞
        has_question_indicator = any(indicator in question_text for indicator in self.question_indicators)
        if not has_question_indicator:
            return True
        
        return False
    
    def _extract_options_from_question(self, question_text: str) -> List[str]:
        """從題目文字中提取選項"""
        if not self.option_extractor:
            from enhanced_option_extractor import EnhancedOptionExtractor
            self.option_extractor = EnhancedOptionExtractor()
        
        options_dict = self.option_extractor.extract_options(question_text)
        return [options_dict.get(letter, '') for letter in ['A', 'B', 'C', 'D']]
    
    def _post_process_questions(self, questions: List[Dict[str, Any]], 
                               min_length: int, max_length: int) -> List[Dict[str, Any]]:
        """後處理題目"""
        processed_questions = []
        
        for question in questions:
            # 清理題目文字
            question['題目'] = self._clean_question_text(question['題目'])
            
            # 驗證題目
            if self._validate_question(question, min_length, max_length):
                processed_questions.append(question)
            else:
                self.logger.warning(f"題目 {question.get('題號', '?')} 驗證失敗，跳過")
        
        return processed_questions
    
    def _clean_question_text(self, text: str) -> str:
        """清理題目文字"""
        # 移除多餘空白
        text = re.sub(r'\s+', ' ', text)
        
        # 移除選項標記
        text = re.sub(r'[（(][ＡＢＣＤABCD][）)]', '', text)
        
        # 移除行首的選項字母
        text = re.sub(r'^[ＡＢＣＤABCD]\s*', '', text, flags=re.MULTILINE)
        
        return text.strip()
    
    def _validate_question(self, question: Dict[str, Any], min_length: int, max_length: int) -> bool:
        """驗證題目"""
        # 檢查題目長度
        question_text = question.get('題目', '')
        if len(question_text) < min_length or len(question_text) > max_length:
            return False
        
        # 檢查選項
        option_count = sum(1 for opt in ['A', 'B', 'C', 'D'] if question.get(f'選項{opt}', '').strip())
        if option_count < 2:
            return False
        
        # 檢查題號
        question_num = question.get('題號', '')
        if not question_num or not question_num.isdigit():
            return False
        
        return True
    
    def get_parsing_statistics(self, questions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """獲取解析統計資訊"""
        if not questions:
            return {'total': 0}
        
        stats = {
            'total': len(questions),
            'question_groups': len([q for q in questions if q.get('題組', False)]),
            'regular_questions': len([q for q in questions if not q.get('題組', False)]),
            'with_options': len([q for q in questions if any(q.get(f'選項{opt}', '').strip() for opt in ['A', 'B', 'C', 'D'])]),
            'pattern_usage': {}
        }
        
        # 統計解析模式使用情況
        for question in questions:
            pattern = question.get('解析模式', 'unknown')
            stats['pattern_usage'][pattern] = stats['pattern_usage'].get(pattern, 0) + 1
        
        return stats

def main():
    """測試函數"""
    parser = EnhancedQuestionParser()
    
    # 測試文字
    test_text = """
    1. 下列何者為公務人員考試法所稱之公務人員？
    經公務人員考試錄取，接受訓練之人員
    各級學校之軍訓教官
    私立學校之專任教師
    於政府機關擔任臨時人員
    
    2. 依公務人員考試法規定，公務人員考試分為幾種？
    一種
    二種
    三種
    四種
    """
    
    questions = parser.parse_questions(test_text)
    print(f"解析出 {len(questions)} 題")
    
    for question in questions:
        print(f"題號: {question['題號']}")
        print(f"題目: {question['題目']}")
        print(f"選項: A.{question['選項A']} B.{question['選項B']} C.{question['選項C']} D.{question['選項D']}")
        print()
    
    stats = parser.get_parsing_statistics(questions)
    print(f"統計資訊: {stats}")

if __name__ == "__main__":
    main()