#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
增強版驗證系統 - 確保資料品質
提供全面的題目、選項和內容驗證功能
"""

import re
import logging
from typing import List, Dict, Any, Optional, Tuple, Set
from datetime import datetime
import json
import statistics

class EnhancedValidationSystem:
    """增強版驗證系統"""
    
    def __init__(self):
        self.logger = logging.getLogger('EnhancedValidationSystem')
        self.validation_rules = self._init_validation_rules()
        self.quality_metrics = self._init_quality_metrics()
    
    def _init_validation_rules(self) -> Dict[str, Dict[str, Any]]:
        """初始化驗證規則"""
        return {
            'question_number': {
                'required': True,
                'pattern': r'^\d+$',
                'min_length': 1,
                'max_length': 3,
                'description': '題號必須是1-3位數字'
            },
            'question_text': {
                'required': True,
                'min_length': 10,
                'max_length': 1000,
                'forbidden_keywords': ['代號', '頁次', '考試', '科目', '時間', '座號'],
                'required_indicators': ['？', '?', '什麼', '何者', '哪個'],
                'description': '題目文字長度和內容驗證'
            },
            'options': {
                'min_count': 2,
                'max_count': 4,
                'min_length': 2,
                'max_length': 200,
                'required_letters': ['A', 'B', 'C', 'D'],
                'description': '選項數量和內容驗證'
            },
            'question_group': {
                'max_questions': 20,
                'min_content_length': 50,
                'description': '題組驗證'
            }
        }
    
    def _init_quality_metrics(self) -> Dict[str, Any]:
        """初始化品質指標"""
        return {
            'completeness_weight': 0.3,
            'accuracy_weight': 0.3,
            'consistency_weight': 0.2,
            'readability_weight': 0.2
        }
    
    def validate_questions(self, questions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        驗證題目列表
        
        Args:
            questions: 題目列表
            
        Returns:
            驗證結果
        """
        self.logger.info(f"開始驗證 {len(questions)} 個題目")
        
        validation_result = {
            'total_questions': len(questions),
            'valid_questions': 0,
            'invalid_questions': 0,
            'warnings': [],
            'errors': [],
            'quality_score': 0.0,
            'detailed_results': [],
            'statistics': {}
        }
        
        if not questions:
            validation_result['errors'].append('沒有題目需要驗證')
            return validation_result
        
        # 逐題驗證
        for i, question in enumerate(questions):
            question_result = self._validate_single_question(question, i)
            validation_result['detailed_results'].append(question_result)
            
            if question_result['is_valid']:
                validation_result['valid_questions'] += 1
            else:
                validation_result['invalid_questions'] += 1
                validation_result['errors'].extend(question_result['errors'])
            
            validation_result['warnings'].extend(question_result['warnings'])
        
        # 計算品質分數
        validation_result['quality_score'] = self._calculate_quality_score(validation_result)
        
        # 生成統計資訊
        validation_result['statistics'] = self._generate_statistics(validation_result)
        
        self.logger.info(f"驗證完成: {validation_result['valid_questions']} 有效, {validation_result['invalid_questions']} 無效")
        
        return validation_result
    
    def _validate_single_question(self, question: Dict[str, Any], index: int) -> Dict[str, Any]:
        """驗證單一題目"""
        result = {
            'index': index,
            'question_number': question.get('題號', ''),
            'is_valid': True,
            'errors': [],
            'warnings': [],
            'scores': {}
        }
        
        # 驗證題號
        number_result = self._validate_question_number(question.get('題號', ''))
        result['scores']['question_number'] = number_result['score']
        if not number_result['is_valid']:
            result['is_valid'] = False
            result['errors'].extend(number_result['errors'])
        result['warnings'].extend(number_result['warnings'])
        
        # 驗證題目文字
        text_result = self._validate_question_text(question.get('題目', ''))
        result['scores']['question_text'] = text_result['score']
        if not text_result['is_valid']:
            result['is_valid'] = False
            result['errors'].extend(text_result['errors'])
        result['warnings'].extend(text_result['warnings'])
        
        # 驗證選項
        options_result = self._validate_options(question)
        result['scores']['options'] = options_result['score']
        if not options_result['is_valid']:
            result['is_valid'] = False
            result['errors'].extend(options_result['errors'])
        result['warnings'].extend(options_result['warnings'])
        
        # 驗證題組（如果是題組題目）
        if question.get('題組', False):
            group_result = self._validate_question_group(question)
            result['scores']['question_group'] = group_result['score']
            if not group_result['is_valid']:
                result['warnings'].extend(group_result['warnings'])
        
        # 計算總分
        result['total_score'] = sum(result['scores'].values()) / len(result['scores'])
        
        return result
    
    def _validate_question_number(self, question_number: str) -> Dict[str, Any]:
        """驗證題號"""
        result = {
            'is_valid': True,
            'score': 0.0,
            'errors': [],
            'warnings': []
        }
        
        if not question_number:
            result['is_valid'] = False
            result['errors'].append('題號不能為空')
            return result
        
        # 檢查格式
        if not re.match(self.validation_rules['question_number']['pattern'], question_number):
            result['is_valid'] = False
            result['errors'].append(f'題號格式不正確: {question_number}')
            return result
        
        # 檢查長度
        if len(question_number) < self.validation_rules['question_number']['min_length']:
            result['is_valid'] = False
            result['errors'].append('題號長度不足')
            return result
        
        if len(question_number) > self.validation_rules['question_number']['max_length']:
            result['warnings'].append('題號長度過長')
        
        result['score'] = 1.0
        return result
    
    def _validate_question_text(self, question_text: str) -> Dict[str, Any]:
        """驗證題目文字"""
        result = {
            'is_valid': True,
            'score': 0.0,
            'errors': [],
            'warnings': []
        }
        
        if not question_text:
            result['is_valid'] = False
            result['errors'].append('題目文字不能為空')
            return result
        
        # 檢查長度
        if len(question_text) < self.validation_rules['question_text']['min_length']:
            result['is_valid'] = False
            result['errors'].append(f'題目文字過短: {len(question_text)} 字元')
            return result
        
        if len(question_text) > self.validation_rules['question_text']['max_length']:
            result['warnings'].append(f'題目文字過長: {len(question_text)} 字元')
        
        # 檢查禁止關鍵詞
        for keyword in self.validation_rules['question_text']['forbidden_keywords']:
            if keyword in question_text:
                result['warnings'].append(f'題目包含不當關鍵詞: {keyword}')
        
        # 檢查題目指示詞
        has_indicator = any(indicator in question_text for indicator in self.validation_rules['question_text']['required_indicators'])
        if not has_indicator:
            result['warnings'].append('題目缺少疑問詞或問號')
        
        # 計算分數
        score = 1.0
        if len(question_text) < 20:
            score -= 0.2
        if not has_indicator:
            score -= 0.3
        if any(keyword in question_text for keyword in self.validation_rules['question_text']['forbidden_keywords']):
            score -= 0.2
        
        result['score'] = max(0.0, score)
        return result
    
    def _validate_options(self, question: Dict[str, Any]) -> Dict[str, Any]:
        """驗證選項"""
        result = {
            'is_valid': True,
            'score': 0.0,
            'errors': [],
            'warnings': []
        }
        
        options = {}
        for letter in self.validation_rules['options']['required_letters']:
            options[letter] = question.get(f'選項{letter}', '').strip()
        
        # 檢查選項數量
        non_empty_options = [opt for opt in options.values() if opt]
        option_count = len(non_empty_options)
        
        if option_count < self.validation_rules['options']['min_count']:
            result['is_valid'] = False
            result['errors'].append(f'選項數量不足: {option_count} 個')
            return result
        
        if option_count > self.validation_rules['options']['max_count']:
            result['warnings'].append(f'選項數量過多: {option_count} 個')
        
        # 檢查選項內容
        for letter, content in options.items():
            if content:
                if len(content) < self.validation_rules['options']['min_length']:
                    result['warnings'].append(f'選項 {letter} 內容過短')
                
                if len(content) > self.validation_rules['options']['max_length']:
                    result['warnings'].append(f'選項 {letter} 內容過長')
        
        # 檢查選項重複
        contents = [opt for opt in options.values() if opt]
        if len(contents) != len(set(contents)):
            result['warnings'].append('存在重複的選項內容')
        
        # 計算分數
        score = 1.0
        if option_count < 4:
            score -= 0.2
        if any(len(opt) < 5 for opt in contents):
            score -= 0.1
        if len(contents) != len(set(contents)):
            score -= 0.2
        
        result['score'] = max(0.0, score)
        return result
    
    def _validate_question_group(self, question: Dict[str, Any]) -> Dict[str, Any]:
        """驗證題組"""
        result = {
            'is_valid': True,
            'score': 1.0,
            'warnings': []
        }
        
        group_content = question.get('題組內容', '')
        if len(group_content) < self.validation_rules['question_group']['min_content_length']:
            result['warnings'].append('題組內容過短')
            result['score'] -= 0.3
        
        return result
    
    def _calculate_quality_score(self, validation_result: Dict[str, Any]) -> float:
        """計算品質分數"""
        if not validation_result['detailed_results']:
            return 0.0
        
        # 計算各項指標
        completeness = validation_result['valid_questions'] / validation_result['total_questions']
        
        # 計算平均準確性分數
        accuracy_scores = [result['total_score'] for result in validation_result['detailed_results']]
        accuracy = statistics.mean(accuracy_scores) if accuracy_scores else 0.0
        
        # 計算一致性（基於警告數量）
        warning_count = len(validation_result['warnings'])
        max_warnings = validation_result['total_questions'] * 2  # 假設每題最多2個警告
        consistency = max(0.0, 1.0 - (warning_count / max_warnings))
        
        # 計算可讀性（基於題目長度分佈）
        readability = self._calculate_readability_score(validation_result['detailed_results'])
        
        # 加權計算總分
        weights = self.quality_metrics
        total_score = (
            completeness * weights['completeness_weight'] +
            accuracy * weights['accuracy_weight'] +
            consistency * weights['consistency_weight'] +
            readability * weights['readability_weight']
        )
        
        return min(1.0, max(0.0, total_score))
    
    def _calculate_readability_score(self, detailed_results: List[Dict[str, Any]]) -> float:
        """計算可讀性分數"""
        if not detailed_results:
            return 0.0
        
        # 基於題目長度分佈計算可讀性
        text_scores = [result['scores'].get('question_text', 0.0) for result in detailed_results]
        return statistics.mean(text_scores) if text_scores else 0.0
    
    def _generate_statistics(self, validation_result: Dict[str, Any]) -> Dict[str, Any]:
        """生成統計資訊"""
        stats = {
            'total_questions': validation_result['total_questions'],
            'valid_questions': validation_result['valid_questions'],
            'invalid_questions': validation_result['invalid_questions'],
            'validation_rate': validation_result['valid_questions'] / validation_result['total_questions'] if validation_result['total_questions'] > 0 else 0.0,
            'quality_score': validation_result['quality_score'],
            'error_count': len(validation_result['errors']),
            'warning_count': len(validation_result['warnings']),
            'average_score': 0.0
        }
        
        # 計算平均分數
        if validation_result['detailed_results']:
            scores = [result['total_score'] for result in validation_result['detailed_results']]
            stats['average_score'] = statistics.mean(scores)
        
        return stats
    
    def generate_validation_report(self, validation_result: Dict[str, Any], 
                                 output_path: Optional[str] = None) -> str:
        """生成驗證報告"""
        report_lines = [
            "# 題目驗證報告",
            f"生成時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "## 總體統計",
            f"- 總題數: {validation_result['total_questions']}",
            f"- 有效題數: {validation_result['valid_questions']}",
            f"- 無效題數: {validation_result['invalid_questions']}",
            f"- 驗證率: {validation_result['statistics']['validation_rate']:.2%}",
            f"- 品質分數: {validation_result['quality_score']:.2f}",
            f"- 錯誤數量: {validation_result['statistics']['error_count']}",
            f"- 警告數量: {validation_result['statistics']['warning_count']}",
            "",
            "## 詳細結果"
        ]
        
        # 添加詳細結果
        for result in validation_result['detailed_results']:
            status = "✅ 有效" if result['is_valid'] else "❌ 無效"
            report_lines.append(f"### 題目 {result['question_number']} {status}")
            report_lines.append(f"- 總分: {result['total_score']:.2f}")
            
            if result['errors']:
                report_lines.append("- 錯誤:")
                for error in result['errors']:
                    report_lines.append(f"  - {error}")
            
            if result['warnings']:
                report_lines.append("- 警告:")
                for warning in result['warnings']:
                    report_lines.append(f"  - {warning}")
            
            report_lines.append("")
        
        # 添加錯誤和警告摘要
        if validation_result['errors']:
            report_lines.append("## 錯誤摘要")
            for error in validation_result['errors']:
                report_lines.append(f"- {error}")
            report_lines.append("")
        
        if validation_result['warnings']:
            report_lines.append("## 警告摘要")
            for warning in validation_result['warnings']:
                report_lines.append(f"- {warning}")
            report_lines.append("")
        
        report_content = "\n".join(report_lines)
        
        if output_path:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(report_content)
        
        return report_content

def main():
    """測試函數"""
    validator = EnhancedValidationSystem()
    
    # 測試題目
    test_questions = [
        {
            '題號': '1',
            '題目': '下列何者為公務人員考試法所稱之公務人員？',
            '選項A': '經公務人員考試錄取，接受訓練之人員',
            '選項B': '各級學校之軍訓教官',
            '選項C': '私立學校之專任教師',
            '選項D': '於政府機關擔任臨時人員',
            '題型': '選擇題',
            '題組': False
        },
        {
            '題號': '2',
            '題目': '依公務人員考試法規定，公務人員考試分為幾種？',
            '選項A': '一種',
            '選項B': '二種',
            '選項C': '三種',
            '選項D': '四種',
            '題型': '選擇題',
            '題組': False
        }
    ]
    
    # 執行驗證
    result = validator.validate_questions(test_questions)
    
    print(f"驗證結果:")
    print(f"總題數: {result['total_questions']}")
    print(f"有效題數: {result['valid_questions']}")
    print(f"無效題數: {result['invalid_questions']}")
    print(f"品質分數: {result['quality_score']:.2f}")
    
    # 生成報告
    report = validator.generate_validation_report(result)
    print(f"\n報告:\n{report}")

if __name__ == "__main__":
    main()