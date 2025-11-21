#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
資料品質驗證器
提供資料品質檢查和統計功能
"""

import json
import os
from datetime import datetime
from typing import Any, Dict, List, Tuple

from .logger import logger


class QualityValidator:
    """資料品質驗證器"""

    def __init__(self):
        self.logger = logger

    def validate_questions(self, questions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        驗證題目資料品質

        Args:
            questions: 題目列表

        Returns:
            驗證結果統計
        """
        stats = {
            "total_questions": len(questions),
            "valid_questions": 0,
            "invalid_questions": 0,
            "quality_issues": [],
            "option_statistics": {"A": 0, "B": 0, "C": 0, "D": 0, "empty": 0},
            "answer_statistics": {"A": 0, "B": 0, "C": 0, "D": 0, "empty": 0},
            "question_length_stats": {"min": 0, "max": 0, "avg": 0},
            "option_diversity_score": 0.0,
        }

        if not questions:
            return stats

        valid_count = 0
        question_lengths = []

        for i, question in enumerate(questions):
            # 檢查題目完整性
            issues = self._check_question_quality(question, i + 1)
            if issues:
                stats["quality_issues"].extend(issues)
                stats["invalid_questions"] += 1
            else:
                valid_count += 1

            # 統計選項
            self._count_options(question, stats["option_statistics"])

            # 統計答案
            self._count_answers(question, stats["answer_statistics"])

            # 統計題目長度
            question_text = question.get("題目", "")
            if question_text:
                question_lengths.append(len(question_text))

        stats["valid_questions"] = valid_count

        # 計算題目長度統計
        if question_lengths:
            stats["question_length_stats"] = {
                "min": min(question_lengths),
                "max": max(question_lengths),
                "avg": sum(question_lengths) / len(question_lengths),
            }

        # 計算選項多樣性分數
        stats["option_diversity_score"] = self._calculate_diversity_score(stats["option_statistics"])

        return stats

    def _check_question_quality(self, question: Dict[str, Any], question_num: int) -> List[str]:
        """檢查單個題目的品質"""
        issues = []

        # 檢查必要欄位
        required_fields = ["題號", "題目", "選項A", "選項B", "選項C", "選項D"]
        for field in required_fields:
            value = question.get(field, "")
            if value is None or (isinstance(value, str) and not value.strip()):
                issues.append(f"第{question_num}題缺少{field}")

        # 檢查題目長度
        question_text = question.get("題目", "")
        if len(question_text) < 10:
            issues.append(f"第{question_num}題題目過短")
        elif len(question_text) > 1000:
            issues.append(f"第{question_num}題題目過長")

        # 檢查選項數量
        option_count = sum(1 for opt in ["A", "B", "C", "D"] if question.get(f"選項{opt}", "").strip())
        if option_count < 2:
            issues.append(f"第{question_num}題選項不足（只有{option_count}個）")

        # 檢查選項重複
        options = [
            question.get(f"選項{opt}", "").strip()
            for opt in ["A", "B", "C", "D"]
            if question.get(f"選項{opt}", "").strip()
        ]
        if len(options) != len(set(options)):
            issues.append(f"第{question_num}題有重複選項")

        # 檢查答案格式
        answer = question.get("最終答案", "") or question.get("正確答案", "")
        if answer and answer not in ["A", "B", "C", "D"]:
            issues.append(f"第{question_num}題答案格式不正確: {answer}")

        return issues

    def _count_options(self, question: Dict[str, Any], stats: Dict[str, int]):
        """統計選項"""
        for opt in ["A", "B", "C", "D"]:
            option_text = question.get(f"選項{opt}", "").strip()
            if option_text:
                stats[opt] += 1
            else:
                stats["empty"] += 1

    def _count_answers(self, question: Dict[str, Any], stats: Dict[str, int]):
        """統計答案"""
        answer = question.get("最終答案", "") or question.get("正確答案", "")
        if answer in ["A", "B", "C", "D"]:
            stats[answer] += 1
        else:
            stats["empty"] += 1

    def _calculate_diversity_score(self, option_stats: Dict[str, int]) -> float:
        """計算選項多樣性分數"""
        total_options = sum(option_stats.values()) - option_stats["empty"]
        if total_options == 0:
            return 0.0

        # 計算各選項的分布均勻度
        option_counts = [option_stats[opt] for opt in ["A", "B", "C", "D"]]
        max_count = max(option_counts)
        min_count = min(option_counts)

        if max_count == 0:
            return 0.0

        # 多樣性分數 = 1 - (最大差異 / 總數)
        diversity = 1 - (max_count - min_count) / total_options
        return round(diversity, 3)

    def generate_quality_report(self, stats: Dict[str, Any], output_path: str = None) -> str:
        """生成品質報告"""
        if not output_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            reports_dir = "reports"
            os.makedirs(reports_dir, exist_ok=True)
            output_path = os.path.join(reports_dir, f"資料品質報告_{timestamp}.md")

        # 確保輸出目錄存在
        output_dir = os.path.dirname(output_path)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)

        with open(output_path, "w", encoding="utf-8") as f:
            f.write("# 資料品質驗證報告\n\n")
            f.write(f"**生成時間**: {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}\n\n")

            # 基本統計
            f.write("## 📊 基本統計\n\n")
            f.write(f"- **總題數**: {stats['total_questions']}\n")
            f.write(f"- **有效題數**: {stats['valid_questions']}\n")
            f.write(f"- **無效題數**: {stats['invalid_questions']}\n")
            # 避免除零錯誤
            valid_rate = (
                stats["valid_questions"] / stats["total_questions"] * 100 if stats["total_questions"] > 0 else 0
            )
            f.write(f"- **有效率**: {valid_rate:.1f}%\n\n")

            # 選項統計
            f.write("## 🔤 選項統計\n\n")
            f.write("| 選項 | 數量 | 比例 |\n")
            f.write("|------|------|------|\n")
            total_options = sum(stats["option_statistics"].values()) - stats["option_statistics"]["empty"]
            for opt in ["A", "B", "C", "D"]:
                count = stats["option_statistics"][opt]
                percentage = count / total_options * 100 if total_options > 0 else 0
                f.write(f"| {opt} | {count} | {percentage:.1f}% |\n")
            f.write(f"| 空白 | {stats['option_statistics']['empty']} | - |\n\n")

            # 答案統計
            f.write("## ✅ 答案統計\n\n")
            f.write("| 答案 | 數量 | 比例 |\n")
            f.write("|------|------|------|\n")
            total_answers = sum(stats["answer_statistics"].values()) - stats["answer_statistics"]["empty"]
            for ans in ["A", "B", "C", "D"]:
                count = stats["answer_statistics"][ans]
                percentage = count / total_answers * 100 if total_answers > 0 else 0
                f.write(f"| {ans} | {count} | {percentage:.1f}% |\n")
            f.write(f"| 空白 | {stats['answer_statistics']['empty']} | - |\n\n")

            # 題目長度統計
            f.write("## 📏 題目長度統計\n\n")
            length_stats = stats["question_length_stats"]
            f.write(f"- **最短**: {length_stats['min']} 字元\n")
            f.write(f"- **最長**: {length_stats['max']} 字元\n")
            f.write(f"- **平均**: {length_stats['avg']:.1f} 字元\n\n")

            # 品質分數
            f.write("## 🎯 品質分數\n\n")
            f.write(f"- **選項多樣性分數**: {stats['option_diversity_score']:.3f}\n")
            f.write(f"- **資料完整性**: {stats['valid_questions']/stats['total_questions']*100:.1f}%\n\n")

            # 品質問題
            if stats["quality_issues"]:
                f.write("## ⚠️ 品質問題\n\n")
                for issue in stats["quality_issues"]:
                    f.write(f"- {issue}\n")
                f.write("\n")
            else:
                f.write("## ✅ 品質狀況\n\n")
                f.write("未發現品質問題，資料品質良好！\n\n")

            # 建議
            f.write("## 💡 改進建議\n\n")
            if stats["option_diversity_score"] < 0.7:
                f.write("- 選項多樣性較低，建議檢查選項生成邏輯\n")
            if stats["valid_questions"] / stats["total_questions"] < 0.9:
                f.write("- 資料完整性不足，建議檢查題目解析邏輯\n")
            if stats["answer_statistics"]["empty"] > stats["total_questions"] * 0.1:
                f.write("- 答案缺失較多，建議檢查答案提取邏輯\n")

            if not any(
                [
                    stats["option_diversity_score"] < 0.7,
                    stats["valid_questions"] / stats["total_questions"] < 0.9,
                    stats["answer_statistics"]["empty"] > stats["total_questions"] * 0.1,
                ]
            ):
                f.write("- 資料品質良好，無需特別改進\n")

        self.logger.success(f"品質報告已生成: {output_path}")
        return output_path
