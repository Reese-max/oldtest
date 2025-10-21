#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
增強版選項提取器 - 強化選項提取功能
支援多種格式和邊緣情況的選項提取
"""

import re
from typing import List, Dict, Any, Optional, Tuple, Set
import logging

class EnhancedOptionExtractor:
    """增強版選項提取器"""
    
    def __init__(self):
        self.logger = logging.getLogger('EnhancedOptionExtractor')
        self.option_patterns = self._init_option_patterns()
        self.option_starters = self._init_option_starters()
        self.option_endings = self._init_option_endings()
    
    def _init_option_patterns(self) -> List[Dict[str, Any]]:
        """初始化選項檢測模式"""
        return [
            # 標準括號格式
            {
                'pattern': r'[（(]A[）)]\s*(.*?)(?=[（(]B[）)]|$)',
                'type': 'parentheses_standard',
                'priority': 1,
                'description': '標準括號格式 (A) 選項'
            },
            {
                'pattern': r'[（(]B[）)]\s*(.*?)(?=[（(]C[）)]|$)',
                'type': 'parentheses_standard',
                'priority': 1,
                'description': '標準括號格式 (B) 選項'
            },
            {
                'pattern': r'[（(]C[）)]\s*(.*?)(?=[（(]D[）)]|$)',
                'type': 'parentheses_standard',
                'priority': 1,
                'description': '標準括號格式 (C) 選項'
            },
            {
                'pattern': r'[（(]D[）)]\s*(.*?)(?=[（(]E[）)]|$)',
                'type': 'parentheses_standard',
                'priority': 1,
                'description': '標準括號格式 (D) 選項'
            },
            
            # 全形選項格式
            {
                'pattern': r'[ＡＢＣＤ]\s*(.*?)(?=[ＡＢＣＤ]|$)',
                'type': 'full_width',
                'priority': 2,
                'description': '全形選項格式 ＡＢＣＤ'
            },
            
            # 半形選項格式
            {
                'pattern': r'[ABCD]\s*(.*?)(?=[ABCD]|$)',
                'type': 'half_width',
                'priority': 2,
                'description': '半形選項格式 ABCD'
            },
            
            # 數字編號格式
            {
                'pattern': r'(\d+)\s*[：:]\s*(.*?)(?=\d+\s*[：:]|$)',
                'type': 'numbered',
                'priority': 3,
                'description': '數字編號格式 1: 選項'
            },
            
            # 點號格式
            {
                'pattern': r'(\d+)\.\s*(.*?)(?=\d+\.|$)',
                'type': 'dot_numbered',
                'priority': 3,
                'description': '點號格式 1. 選項'
            },
            
            # 破折號格式
            {
                'pattern': r'[ＡＢＣＤABCD]\s*[-–—]\s*(.*?)(?=[ＡＢＣＤABCD]\s*[-–—]|$)',
                'type': 'dash',
                'priority': 4,
                'description': '破折號格式 A - 選項'
            },
            
            # 空格分隔格式
            {
                'pattern': r'[ＡＢＣＤABCD]\s+(.*?)(?=[ＡＢＣＤABCD]\s+|$)',
                'type': 'space_separated',
                'priority': 5,
                'description': '空格分隔格式 A 選項'
            }
        ]
    
    def _init_option_starters(self) -> Set[str]:
        """初始化選項開始詞"""
        return {
            '經', '各', '行', '私', '於', '依', '關', '當', '偶', '下', '應', '若', '原', '該', 
            '法', '警', '義', '褫', '受', '無', '須', '向', '得', '限', '對', '在', '為', '與',
            '是', '有', '可', '能', '會', '將', '已', '被', '由', '從', '至', '及', '或', '但',
            '而', '且', '則', '因', '故', '所', '其', '此', '彼', '他', '她', '它', '們', '的',
            '地', '得', '了', '着', '過', '把', '被', '使', '讓', '叫', '令', '要', '想', '希望',
            '認為', '覺得', '知道', '了解', '明白', '清楚', '確定', '肯定', '相信', '懷疑',
            '擔心', '害怕', '喜歡', '討厭', '愛', '恨', '需要', '想要', '希望', '期待', '盼望'
        }
    
    def _init_option_endings(self) -> Set[str]:
        """初始化選項結束詞"""
        return {
            '。', '，', '；', '：', '！', '？', '、', '）', '）', '】', '」', '』', '》', '》',
            '的', '了', '着', '過', '是', '有', '在', '為', '與', '和', '或', '但', '而', '且',
            '則', '因', '故', '所', '其', '此', '彼', '他', '她', '它', '們', '把', '被', '使',
            '讓', '叫', '令', '要', '想', '希望', '認為', '覺得', '知道', '了解', '明白'
        }
    
    def extract_options(self, text: str, question_number: int = None) -> Dict[str, str]:
        """
        提取選項 - 主要方法
        
        Args:
            text: 包含選項的文字
            question_number: 題號（可選）
            
        Returns:
            選項字典 {A: 選項內容, B: 選項內容, ...}
        """
        self.logger.debug(f"開始提取選項，文字長度: {len(text)}")
        
        # 嘗試不同的提取方法
        methods = [
            self._extract_with_patterns,
            self._extract_with_line_analysis,
            self._extract_with_word_analysis,
            self._extract_with_semantic_analysis
        ]
        
        best_result = {}
        best_score = 0
        
        for method in methods:
            try:
                result = method(text, question_number)
                score = self._evaluate_extraction_quality(result, text)
                
                if score > best_score:
                    best_result = result
                    best_score = score
                    
                self.logger.debug(f"方法 {method.__name__}: {len(result)} 個選項, 分數: {score:.2f}")
                
            except Exception as e:
                self.logger.warning(f"方法 {method.__name__} 失敗: {e}")
                continue
        
        # 如果沒有找到足夠的選項，嘗試組合方法
        if len(best_result) < 2:
            combined_result = self._extract_combined_method(text, question_number)
            combined_score = self._evaluate_extraction_quality(combined_result, text)
            
            if combined_score > best_score:
                best_result = combined_result
                best_score = combined_score
        
        self.logger.info(f"選項提取完成: {len(best_result)} 個選項, 品質分數: {best_score:.2f}")
        return best_result
    
    def _extract_with_patterns(self, text: str, question_number: int = None) -> Dict[str, str]:
        """使用正則表達式模式提取選項"""
        options = {}
        
        # 按優先級排序模式
        sorted_patterns = sorted(self.option_patterns, key=lambda x: x['priority'])
        
        for pattern_info in sorted_patterns:
            pattern = pattern_info['pattern']
            pattern_type = pattern_info['type']
            
            try:
                matches = re.findall(pattern, text, re.DOTALL | re.MULTILINE)
                
                if len(matches) >= 2:  # 至少要有2個選項
                    for i, match in enumerate(matches[:4]):  # 最多4個選項
                        if isinstance(match, tuple):
                            # 如果匹配結果是元組，取最後一個元素
                            option_text = match[-1].strip()
                        else:
                            option_text = match.strip()
                        
                        if option_text and len(option_text) > 1:
                            option_letter = chr(ord('A') + i)
                            options[option_letter] = option_text
                    
                    if len(options) >= 2:
                        break
                        
            except re.error as e:
                self.logger.warning(f"正則表達式錯誤: {pattern} - {e}")
                continue
        
        return options
    
    def _extract_with_line_analysis(self, text: str, question_number: int = None) -> Dict[str, str]:
        """使用行分析提取選項"""
        options = {}
        lines = text.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # 檢查是否為選項行
            option_match = re.match(r'^([ＡＢＣＤABCD])\s*[：:]\s*(.*)', line)
            if option_match:
                option_letter = option_match.group(1)
                option_content = option_match.group(2).strip()
                
                if option_content:
                    options[option_letter] = option_content
            else:
                # 檢查是否為數字編號選項
                number_match = re.match(r'^(\d+)\s*[：:]\s*(.*)', line)
                if number_match:
                    option_num = int(number_match.group(1))
                    if 1 <= option_num <= 4:
                        option_letter = chr(ord('A') + option_num - 1)
                        option_content = number_match.group(2).strip()
                        
                        if option_content:
                            options[option_letter] = option_content
        
        return options
    
    def _extract_with_word_analysis(self, text: str, question_number: int = None) -> Dict[str, str]:
        """使用詞彙分析提取選項"""
        options = {}
        
        # 按空格分割文字
        words = text.split()
        current_option = None
        current_content = []
        
        for word in words:
            # 檢查是否為選項標記
            if re.match(r'^[ＡＢＣＤABCD]$', word):
                # 保存前一個選項
                if current_option and current_content:
                    options[current_option] = ' '.join(current_content).strip()
                
                # 開始新選項
                current_option = word
                current_content = []
            else:
                # 繼續當前選項
                if current_option:
                    current_content.append(word)
        
        # 保存最後一個選項
        if current_option and current_content:
            options[current_option] = ' '.join(current_content).strip()
        
        return options
    
    def _extract_with_semantic_analysis(self, text: str, question_number: int = None) -> Dict[str, str]:
        """使用語義分析提取選項"""
        options = {}
        
        # 尋找選項開始詞
        sentences = re.split(r'[。！？；]', text)
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
            
            # 檢查句子是否以選項開始詞開頭
            for starter in self.option_starters:
                if sentence.startswith(starter):
                    # 嘗試找到對應的選項字母
                    option_letter = self._find_option_letter_for_sentence(sentence, text)
                    if option_letter:
                        options[option_letter] = sentence
                    break
        
        return options
    
    def _find_option_letter_for_sentence(self, sentence: str, full_text: str) -> Optional[str]:
        """為句子找到對應的選項字母"""
        # 在完整文字中尋找包含此句子的選項
        for pattern_info in self.option_patterns:
            pattern = pattern_info['pattern']
            try:
                matches = re.finditer(pattern, full_text, re.DOTALL)
                for match in matches:
                    if sentence in match.group(0):
                        # 找到匹配的選項字母
                        if 'A' in match.group(0):
                            return 'A'
                        elif 'B' in match.group(0):
                            return 'B'
                        elif 'C' in match.group(0):
                            return 'C'
                        elif 'D' in match.group(0):
                            return 'D'
            except re.error:
                continue
        
        return None
    
    def _extract_combined_method(self, text: str, question_number: int = None) -> Dict[str, str]:
        """組合方法提取選項"""
        options = {}
        
        # 方法1: 行分析 + 模式匹配
        line_options = self._extract_with_line_analysis(text, question_number)
        pattern_options = self._extract_with_patterns(text, question_number)
        
        # 合併結果
        for letter in ['A', 'B', 'C', 'D']:
            if letter in pattern_options:
                options[letter] = pattern_options[letter]
            elif letter in line_options:
                options[letter] = line_options[letter]
        
        # 如果還是不夠，嘗試更寬鬆的匹配
        if len(options) < 2:
            loose_options = self._extract_loose_options(text)
            for letter, content in loose_options.items():
                if letter not in options:
                    options[letter] = content
        
        return options
    
    def _extract_loose_options(self, text: str) -> Dict[str, str]:
        """寬鬆的選項提取"""
        options = {}
        
        # 尋找所有可能的選項標記
        option_markers = re.findall(r'[ＡＢＣＤABCD]', text)
        
        if len(option_markers) >= 2:
            # 按位置排序
            marker_positions = []
            for marker in set(option_markers):
                for match in re.finditer(marker, text):
                    marker_positions.append((match.start(), marker))
            
            marker_positions.sort()
            
            # 提取選項內容
            for i, (pos, marker) in enumerate(marker_positions[:4]):
                if i < len(marker_positions) - 1:
                    next_pos = marker_positions[i + 1][0]
                    content = text[pos:next_pos].strip()
                else:
                    content = text[pos:].strip()
                
                # 清理內容
                content = re.sub(r'^[ＡＢＣＤABCD]\s*', '', content)
                content = re.sub(r'\s+', ' ', content).strip()
                
                if content and len(content) > 2:
                    options[marker] = content
        
        return options
    
    def _evaluate_extraction_quality(self, options: Dict[str, str], original_text: str) -> float:
        """評估提取品質"""
        if not options:
            return 0.0
        
        score = 0.0
        
        # 選項數量因子
        option_count = len(options)
        if option_count >= 2:
            score += 0.3
        if option_count >= 4:
            score += 0.2
        
        # 選項長度因子
        avg_length = sum(len(content) for content in options.values()) / option_count
        if avg_length > 5:
            score += 0.2
        if avg_length > 10:
            score += 0.1
        
        # 選項完整性因子
        complete_options = sum(1 for content in options.values() if len(content.strip()) > 2)
        if complete_options == option_count:
            score += 0.2
        
        # 選項多樣性因子
        if option_count > 1:
            lengths = [len(content) for content in options.values()]
            length_variance = max(lengths) - min(lengths)
            if length_variance < 50:  # 長度差異不太大
                score += 0.1
        
        return min(score, 1.0)
    
    def validate_options(self, options: Dict[str, str]) -> Dict[str, Any]:
        """驗證選項"""
        validation_result = {
            'is_valid': True,
            'issues': [],
            'suggestions': []
        }
        
        if not options:
            validation_result['is_valid'] = False
            validation_result['issues'].append('沒有找到任何選項')
            return validation_result
        
        # 檢查選項數量
        if len(options) < 2:
            validation_result['is_valid'] = False
            validation_result['issues'].append(f'選項數量不足: {len(options)} 個')
        
        if len(options) > 4:
            validation_result['issues'].append(f'選項數量過多: {len(options)} 個')
            validation_result['suggestions'].append('考慮只保留前4個選項')
        
        # 檢查選項內容
        for letter, content in options.items():
            if not content or len(content.strip()) < 2:
                validation_result['issues'].append(f'選項 {letter} 內容過短或為空')
            
            if len(content) > 200:
                validation_result['issues'].append(f'選項 {letter} 內容過長: {len(content)} 字元')
                validation_result['suggestions'].append(f'考慮截斷選項 {letter} 的內容')
        
        # 檢查選項重複
        contents = [content.strip().lower() for content in options.values()]
        if len(contents) != len(set(contents)):
            validation_result['issues'].append('存在重複的選項內容')
        
        return validation_result

def main():
    """測試函數"""
    extractor = EnhancedOptionExtractor()
    
    # 測試文字
    test_text = """
    1. 經公務人員考試錄取，接受訓練之人員
    2. 各級學校之軍訓教官
    3. 私立學校之專任教師
    4. 於政府機關擔任臨時人員
    """
    
    options = extractor.extract_options(test_text)
    print(f"提取的選項: {options}")
    
    validation = extractor.validate_options(options)
    print(f"驗證結果: {validation}")

if __name__ == "__main__":
    main()