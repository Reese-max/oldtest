#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
申論題偵測器
用於識別PDF是否為申論題試卷
"""

import re
from typing import Dict, List
from ..utils.logger import logger


class EssayDetector:
    """申論題偵測器"""

    def __init__(self):
        self.logger = logger

        # 申論題關鍵詞
        self.essay_keywords = [
            '試述', '試說明', '試論述', '試分析', '試比較',
            '請說明', '請論述', '請分析', '請比較', '請闡述',
            '論述', '說明', '分析', '比較', '闡述',
            '何謂', '為何', '如何',
        ]

        # 分數標記模式
        self.score_patterns = [
            r'[\(（]\s*\d+\s*分\s*[）\)]',  # (25分) (20分)
            r'\d+\s*分\s*[）\)]',           # 25分) 20分)
            r'[\(（]\s*\d+\s*分',           # (25分
        ]

        # 中文數字題號模式
        self.chinese_number_patterns = [
            r'^[一二三四五六七八九十]\s*[、.]',  # 一、 一.
            r'^\([一二三四五六七八九十]\)',     # (一)
            r'^（[一二三四五六七八九十]）',     # （一）
        ]

        # 選擇題標記模式
        self.choice_patterns = [
            r'^\d+\s+[^一二三四五六七八九十分]',  # 阿拉伯數字題號後跟題目
            r'[ABCD][.、)]\s',                     # A. B、 C) D、
            r'[\(（][ABCD][）\)]',                # (A) (B) （C） （D）
        ]

    def detect_essay_exam(self, text: str) -> Dict[str, any]:
        """
        偵測是否為申論題試卷

        Args:
            text: PDF提取的文本

        Returns:
            {
                'is_essay': bool,        # 是否為申論題
                'confidence': float,     # 信心度 (0-1)
                'features': dict,        # 檢測到的特徵
                'reason': str           # 判定理由
            }
        """
        if not text or len(text) < 50:
            return {
                'is_essay': False,
                'confidence': 0.0,
                'features': {},
                'reason': '文本內容過短，無法判斷'
            }

        features = self._extract_features(text)
        is_essay, confidence, reason = self._make_decision(features)

        return {
            'is_essay': is_essay,
            'confidence': confidence,
            'features': features,
            'reason': reason
        }

    def _extract_features(self, text: str) -> Dict[str, any]:
        """提取特徵"""
        features = {}

        # 1. 檢測申論題關鍵詞
        keyword_count = 0
        found_keywords = []
        for keyword in self.essay_keywords:
            if keyword in text:
                keyword_count += text.count(keyword)
                found_keywords.append(keyword)

        features['essay_keywords'] = {
            'count': keyword_count,
            'found': found_keywords,
            'has_keywords': keyword_count > 0
        }

        # 2. 檢測分數標記
        score_marks = []
        for pattern in self.score_patterns:
            matches = re.findall(pattern, text)
            score_marks.extend(matches)

        features['score_marks'] = {
            'count': len(score_marks),
            'examples': score_marks[:5],  # 最多顯示5個例子
            'has_scores': len(score_marks) > 0
        }

        # 3. 檢測中文數字題號
        chinese_numbers = []
        for pattern in self.chinese_number_patterns:
            matches = re.findall(pattern, text, re.MULTILINE)
            chinese_numbers.extend(matches)

        features['chinese_numbers'] = {
            'count': len(chinese_numbers),
            'examples': chinese_numbers[:5],
            'has_chinese_numbers': len(chinese_numbers) > 0
        }

        # 4. 檢測選擇題標記（反向特徵）
        choice_marks = []
        for pattern in self.choice_patterns:
            matches = re.findall(pattern, text, re.MULTILINE)
            choice_marks.extend(matches)

        features['choice_marks'] = {
            'count': len(choice_marks),
            'examples': choice_marks[:5],
            'has_choice_marks': len(choice_marks) > 0
        }

        # 5. 檢測阿拉伯數字題號（1-50範圍）
        # 更精確的模式：行首的數字，後面跟著非數字字符
        arabic_numbers = re.findall(r'^\d+\s+[^\d]', text, re.MULTILINE)
        features['arabic_numbers'] = {
            'count': len(arabic_numbers),
            'examples': arabic_numbers[:5],
            'has_arabic_numbers': len(arabic_numbers) > 0
        }

        # 6. 文本長度
        features['text_length'] = len(text)

        return features

    def _make_decision(self, features: Dict) -> tuple:
        """
        根據特徵做出判斷

        Returns:
            (is_essay, confidence, reason)
        """
        score = 0.0
        reasons = []

        # 正向特徵（支持申論題）
        if features['essay_keywords']['has_keywords']:
            weight = min(features['essay_keywords']['count'] / 10, 1.0) * 0.3
            score += weight
            reasons.append(
                f"發現 {features['essay_keywords']['count']} 個申論題關鍵詞"
                f"（如：{', '.join(features['essay_keywords']['found'][:3])}）"
            )

        if features['score_marks']['has_scores']:
            weight = min(features['score_marks']['count'] / 5, 1.0) * 0.25
            score += weight
            reasons.append(
                f"發現 {features['score_marks']['count']} 個分數標記"
                f"（如：{', '.join(features['score_marks']['examples'][:2])}）"
            )

        if features['chinese_numbers']['has_chinese_numbers']:
            weight = min(features['chinese_numbers']['count'] / 5, 1.0) * 0.2
            score += weight
            reasons.append(
                f"發現 {features['chinese_numbers']['count']} 個中文數字題號"
            )

        # 反向特徵（支持選擇題）
        if features['choice_marks']['has_choice_marks']:
            penalty = min(features['choice_marks']['count'] / 20, 1.0) * 0.3
            score -= penalty
            reasons.append(
                f"發現 {features['choice_marks']['count']} 個選擇題標記（減分）"
            )

        if features['arabic_numbers']['has_arabic_numbers']:
            # 如果阿拉伯數字題號很多（>10個），可能是選擇題
            if features['arabic_numbers']['count'] > 10:
                penalty = 0.25
                score -= penalty
                reasons.append(
                    f"發現 {features['arabic_numbers']['count']} 個阿拉伯數字題號（減分）"
                )

        # 特殊情況：幾乎沒有任何特徵
        if (not features['essay_keywords']['has_keywords'] and
            not features['score_marks']['has_scores'] and
            not features['chinese_numbers']['has_chinese_numbers'] and
            not features['arabic_numbers']['has_arabic_numbers']):
            reasons.append("未檢測到明確的題型特徵")

        # 將分數歸一化到 0-1 範圍
        confidence = max(0.0, min(1.0, score))

        # 判定閾值
        threshold = 0.3
        is_essay = confidence >= threshold

        # 生成理由字符串
        reason_str = '; '.join(reasons) if reasons else '無明顯特徵'

        if is_essay:
            final_reason = f"✓ 判定為申論題試卷（信心度: {confidence:.2f}）- {reason_str}"
        else:
            final_reason = f"✗ 判定為非申論題試卷（信心度: {confidence:.2f}）- {reason_str}"

        return is_essay, confidence, final_reason

    def get_detailed_report(self, text: str) -> str:
        """
        生成詳細報告

        Args:
            text: PDF文本

        Returns:
            格式化的報告字符串
        """
        result = self.detect_essay_exam(text)

        report = []
        report.append("="*70)
        report.append("申論題偵測報告")
        report.append("="*70)
        report.append(f"判定結果: {'✓ 申論題試卷' if result['is_essay'] else '✗ 非申論題試卷'}")
        report.append(f"信心度: {result['confidence']:.2%}")
        report.append(f"理由: {result['reason']}")
        report.append("")
        report.append("特徵詳情:")
        report.append("-"*70)

        features = result['features']

        # 申論題關鍵詞
        kw = features['essay_keywords']
        report.append(f"  申論題關鍵詞: {kw['count']} 個")
        if kw['found']:
            report.append(f"    發現: {', '.join(kw['found'][:10])}")

        # 分數標記
        sm = features['score_marks']
        report.append(f"  分數標記: {sm['count']} 個")
        if sm['examples']:
            report.append(f"    示例: {', '.join(sm['examples'])}")

        # 中文數字題號
        cn = features['chinese_numbers']
        report.append(f"  中文數字題號: {cn['count']} 個")
        if cn['examples']:
            report.append(f"    示例: {', '.join(cn['examples'])}")

        # 選擇題標記
        cm = features['choice_marks']
        report.append(f"  選擇題標記: {cm['count']} 個")
        if cm['examples']:
            report.append(f"    示例: {', '.join(str(e) for e in cm['examples'])}")

        # 阿拉伯數字題號
        an = features['arabic_numbers']
        report.append(f"  阿拉伯數字題號: {an['count']} 個")

        report.append("="*70)

        return '\n'.join(report)
