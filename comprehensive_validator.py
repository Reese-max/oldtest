#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
綜合驗證器 - 確保題目資料品質和完整性
"""

import re
import json
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
from enhanced_question_parser import ParsedQuestion, QuestionType, QuestionDifficulty

class ValidationLevel(Enum):
    """驗證等級枚舉"""
    BASIC = "basic"      # 基本驗證
    STANDARD = "standard"  # 標準驗證
    STRICT = "strict"    # 嚴格驗證

class ValidationResult(Enum):
    """驗證結果枚舉"""
    PASS = "pass"
    WARNING = "warning"
    FAIL = "fail"

@dataclass
class ValidationIssue:
    """驗證問題資料結構"""
    issue_type: str
    severity: ValidationResult
    message: str
    question_number: Optional[str] = None
    suggestion: Optional[str] = None

@dataclass
class ValidationReport:
    """驗證報告資料結構"""
    total_questions: int
    passed_questions: int
    warning_questions: int
    failed_questions: int
    issues: List[ValidationIssue]
    overall_score: float
    recommendations: List[str]

class ComprehensiveValidator:
    """綜合驗證器"""
    
    def __init__(self, validation_level: ValidationLevel = ValidationLevel.STANDARD):
        self.validation_level = validation_level
        
        # 驗證規則配置
        self.validation_rules = {
            'min_question_length': 10,
            'max_question_length': 2000,
            'min_option_length': 2,
            'max_option_length': 500,
            'min_options_count': 2,
            'max_options_count': 6,
            'min_confidence_score': 0.3,
            'max_duplicate_content_ratio': 0.8,
        }
        
        # 根據驗證等級調整規則
        if validation_level == ValidationLevel.STRICT:
            self.validation_rules.update({
                'min_question_length': 20,
                'min_option_length': 5,
                'min_confidence_score': 0.6,
                'max_duplicate_content_ratio': 0.5,
            })
        elif validation_level == ValidationLevel.BASIC:
            self.validation_rules.update({
                'min_question_length': 5,
                'min_option_length': 1,
                'min_confidence_score': 0.1,
                'max_duplicate_content_ratio': 0.9,
            })
    
    def validate_questions(self, questions: List[ParsedQuestion]) -> ValidationReport:
        """
        驗證題目列表
        
        Args:
            questions: 要驗證的題目列表
            
        Returns:
            驗證報告
        """
        print(f"🔍 開始驗證 {len(questions)} 題目")
        
        issues = []
        passed_count = 0
        warning_count = 0
        failed_count = 0
        
        for question in questions:
            question_issues = self._validate_single_question(question)
            issues.extend(question_issues)
            
            # 統計結果
            if not question_issues:
                passed_count += 1
            elif any(issue.severity == ValidationResult.FAIL for issue in question_issues):
                failed_count += 1
            else:
                warning_count += 1
        
        # 生成整體驗證報告
        overall_score = self._calculate_overall_score(passed_count, warning_count, failed_count)
        recommendations = self._generate_recommendations(issues)
        
        report = ValidationReport(
            total_questions=len(questions),
            passed_questions=passed_count,
            warning_questions=warning_count,
            failed_questions=failed_count,
            issues=issues,
            overall_score=overall_score,
            recommendations=recommendations
        )
        
        print(f"📊 驗證完成: {passed_count} 通過, {warning_count} 警告, {failed_count} 失敗")
        print(f"📈 整體分數: {overall_score:.2f}")
        
        return report
    
    def _validate_single_question(self, question: ParsedQuestion) -> List[ValidationIssue]:
        """驗證單一題目"""
        issues = []
        
        # 基本驗證
        issues.extend(self._validate_question_basic(question))
        
        # 內容驗證
        issues.extend(self._validate_question_content(question))
        
        # 選項驗證
        issues.extend(self._validate_question_options(question))
        
        # 格式驗證
        issues.extend(self._validate_question_format(question))
        
        # 品質驗證
        issues.extend(self._validate_question_quality(question))
        
        return issues
    
    def _validate_question_basic(self, question: ParsedQuestion) -> List[ValidationIssue]:
        """基本驗證"""
        issues = []
        
        # 題號驗證
        if not question.question_number or not question.question_number.isdigit():
            issues.append(ValidationIssue(
                issue_type="invalid_question_number",
                severity=ValidationResult.FAIL,
                message="題號無效或缺失",
                question_number=question.question_number,
                suggestion="確保題號為有效數字"
            ))
        
        # 題目文字長度驗證
        if len(question.question_text) < self.validation_rules['min_question_length']:
            issues.append(ValidationIssue(
                issue_type="question_too_short",
                severity=ValidationResult.WARNING if self.validation_level == ValidationLevel.BASIC else ValidationResult.FAIL,
                message=f"題目文字過短 ({len(question.question_text)} 字元)",
                question_number=question.question_number,
                suggestion=f"建議至少 {self.validation_rules['min_question_length']} 字元"
            ))
        
        if len(question.question_text) > self.validation_rules['max_question_length']:
            issues.append(ValidationIssue(
                issue_type="question_too_long",
                severity=ValidationResult.WARNING,
                message=f"題目文字過長 ({len(question.question_text)} 字元)",
                question_number=question.question_number,
                suggestion=f"建議不超過 {self.validation_rules['max_question_length']} 字元"
            ))
        
        return issues
    
    def _validate_question_content(self, question: ParsedQuestion) -> List[ValidationIssue]:
        """內容驗證"""
        issues = []
        
        # 檢查是否包含疑問詞
        question_indicators = ['？', '?', '下列', '何者', '哪一', '哪個', '如何', '什麼', '為什麼']
        if not any(indicator in question.question_text for indicator in question_indicators):
            issues.append(ValidationIssue(
                issue_type="missing_question_indicator",
                severity=ValidationResult.WARNING,
                message="題目缺少疑問詞或疑問標點",
                question_number=question.question_number,
                suggestion="添加疑問詞或疑問標點符號"
            ))
        
        # 檢查是否包含明顯的錯誤內容
        error_patterns = [
            r'代號\s*\d+',
            r'頁次\s*\d+',
            r'考試\s*科目',
            r'作答\s*須知',
        ]
        
        for pattern in error_patterns:
            if re.search(pattern, question.question_text):
                issues.append(ValidationIssue(
                    issue_type="contains_metadata",
                    severity=ValidationResult.WARNING,
                    message="題目包含非題目內容（如代號、頁次等）",
                    question_number=question.question_number,
                    suggestion="移除代號、頁次等非題目內容"
                ))
                break
        
        return issues
    
    def _validate_question_options(self, question: ParsedQuestion) -> List[ValidationIssue]:
        """選項驗證"""
        issues = []
        
        if question.question_type != QuestionType.MULTIPLE_CHOICE:
            return issues
        
        options = question.options
        
        # 選項數量驗證
        option_count = len(options)
        if option_count < self.validation_rules['min_options_count']:
            issues.append(ValidationIssue(
                issue_type="insufficient_options",
                severity=ValidationResult.FAIL,
                message=f"選項數量不足 ({option_count} 個)",
                question_number=question.question_number,
                suggestion=f"至少需要 {self.validation_rules['min_options_count']} 個選項"
            ))
        
        if option_count > self.validation_rules['max_options_count']:
            issues.append(ValidationIssue(
                issue_type="too_many_options",
                severity=ValidationResult.WARNING,
                message=f"選項數量過多 ({option_count} 個)",
                question_number=question.question_number,
                suggestion=f"建議不超過 {self.validation_rules['max_options_count']} 個選項"
            ))
        
        # 選項內容驗證
        for letter, content in options.items():
            if len(content) < self.validation_rules['min_option_length']:
                issues.append(ValidationIssue(
                    issue_type="option_too_short",
                    severity=ValidationResult.WARNING,
                    message=f"選項{letter}內容過短 ({len(content)} 字元)",
                    question_number=question.question_number,
                    suggestion=f"建議至少 {self.validation_rules['min_option_length']} 字元"
                ))
            
            if len(content) > self.validation_rules['max_option_length']:
                issues.append(ValidationIssue(
                    issue_type="option_too_long",
                    severity=ValidationResult.WARNING,
                    message=f"選項{letter}內容過長 ({len(content)} 字元)",
                    question_number=question.question_number,
                    suggestion=f"建議不超過 {self.validation_rules['max_option_length']} 字元"
                ))
        
        # 選項重複驗證
        if option_count >= 2:
            duplicate_ratio = self._calculate_duplicate_ratio(list(options.values()))
            if duplicate_ratio > self.validation_rules['max_duplicate_content_ratio']:
                issues.append(ValidationIssue(
                    issue_type="duplicate_options",
                    severity=ValidationResult.WARNING,
                    message=f"選項重複度過高 ({duplicate_ratio:.2f})",
                    question_number=question.question_number,
                    suggestion="檢查並修正重複的選項內容"
                ))
        
        return issues
    
    def _validate_question_format(self, question: ParsedQuestion) -> List[ValidationIssue]:
        """格式驗證"""
        issues = []
        
        # 檢查題目格式
        if question.question_type == QuestionType.MULTIPLE_CHOICE:
            # 檢查是否有選項但沒有選項內容
            if question.options and not any(question.options.values()):
                issues.append(ValidationIssue(
                    issue_type="empty_options",
                    severity=ValidationResult.FAIL,
                    message="選擇題缺少選項內容",
                    question_number=question.question_number,
                    suggestion="添加選項內容或更改題目類型"
                ))
        
        # 檢查題組相關格式
        if question.is_group_question:
            if not question.group_id:
                issues.append(ValidationIssue(
                    issue_type="missing_group_id",
                    severity=ValidationResult.WARNING,
                    message="題組題目缺少題組ID",
                    question_number=question.question_number,
                    suggestion="添加題組ID"
                ))
        
        return issues
    
    def _validate_question_quality(self, question: ParsedQuestion) -> List[ValidationIssue]:
        """品質驗證"""
        issues = []
        
        # 可信度分數驗證
        if question.confidence_score < self.validation_rules['min_confidence_score']:
            issues.append(ValidationIssue(
                issue_type="low_confidence",
                severity=ValidationResult.WARNING,
                message=f"題目可信度分數過低 ({question.confidence_score:.2f})",
                question_number=question.question_number,
                suggestion="檢查題目內容和格式是否正確"
            ))
        
        # 檢查題目是否過於簡單或複雜
        if question.difficulty == QuestionDifficulty.EASY and len(question.question_text) > 200:
            issues.append(ValidationIssue(
                issue_type="difficulty_mismatch",
                severity=ValidationResult.WARNING,
                message="題目標記為簡單但內容較長",
                question_number=question.question_number,
                suggestion="重新評估題目難度等級"
            ))
        
        return issues
    
    def _calculate_duplicate_ratio(self, contents: List[str]) -> float:
        """計算內容重複比例"""
        if len(contents) < 2:
            return 0.0
        
        total_pairs = len(contents) * (len(contents) - 1) // 2
        duplicate_pairs = 0
        
        for i in range(len(contents)):
            for j in range(i + 1, len(contents)):
                if contents[i].strip().lower() == contents[j].strip().lower():
                    duplicate_pairs += 1
        
        return duplicate_pairs / total_pairs if total_pairs > 0 else 0.0
    
    def _calculate_overall_score(self, passed: int, warning: int, failed: int) -> float:
        """計算整體分數"""
        total = passed + warning + failed
        if total == 0:
            return 0.0
        
        # 通過得1分，警告得0.5分，失敗得0分
        score = (passed * 1.0 + warning * 0.5 + failed * 0.0) / total
        return score
    
    def _generate_recommendations(self, issues: List[ValidationIssue]) -> List[str]:
        """生成改進建議"""
        recommendations = []
        
        # 統計問題類型
        issue_types = {}
        for issue in issues:
            issue_types[issue.issue_type] = issue_types.get(issue.issue_type, 0) + 1
        
        # 生成建議
        if issue_types.get('question_too_short', 0) > 0:
            recommendations.append("增加題目文字長度，提供更詳細的題目描述")
        
        if issue_types.get('insufficient_options', 0) > 0:
            recommendations.append("為選擇題添加足夠的選項（至少2個）")
        
        if issue_types.get('duplicate_options', 0) > 0:
            recommendations.append("檢查並修正重複的選項內容")
        
        if issue_types.get('low_confidence', 0) > 0:
            recommendations.append("提高題目解析的準確性，檢查格式和內容")
        
        if issue_types.get('missing_question_indicator', 0) > 0:
            recommendations.append("為題目添加疑問詞或疑問標點符號")
        
        return recommendations
    
    def generate_validation_report(self, report: ValidationReport, output_path: Optional[str] = None) -> str:
        """生成驗證報告"""
        report_content = f"""
# 題目驗證報告

## 總體統計
- 總題數: {report.total_questions}
- 通過: {report.passed_questions} ({report.passed_questions/report.total_questions*100:.1f}%)
- 警告: {report.warning_questions} ({report.warning_questions/report.total_questions*100:.1f}%)
- 失敗: {report.failed_questions} ({report.failed_questions/report.total_questions*100:.1f}%)
- 整體分數: {report.overall_score:.2f}/1.0

## 問題統計
"""
        
        # 問題統計
        issue_types = {}
        for issue in report.issues:
            issue_types[issue.issue_type] = issue_types.get(issue.issue_type, 0) + 1
        
        for issue_type, count in sorted(issue_types.items(), key=lambda x: x[1], reverse=True):
            report_content += f"- {issue_type}: {count} 次\n"
        
        # 詳細問題列表
        if report.issues:
            report_content += "\n## 詳細問題列表\n\n"
            for issue in report.issues:
                severity_icon = "❌" if issue.severity == ValidationResult.FAIL else "⚠️"
                report_content += f"### {severity_icon} 題目 {issue.question_number}: {issue.message}\n"
                if issue.suggestion:
                    report_content += f"**建議**: {issue.suggestion}\n"
                report_content += "\n"
        
        # 改進建議
        if report.recommendations:
            report_content += "## 改進建議\n\n"
            for i, recommendation in enumerate(report.recommendations, 1):
                report_content += f"{i}. {recommendation}\n"
        
        # 儲存報告
        if output_path:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(report_content)
            print(f"📄 驗證報告已儲存: {output_path}")
        
        return report_content

def test_validator():
    """測試驗證器"""
    from enhanced_question_parser import ParsedQuestion, QuestionType, QuestionDifficulty
    
    # 創建測試題目
    test_questions = [
        ParsedQuestion(
            question_number="1",
            question_text="下列何者為公務人員考試錄取人員？",
            options={"A": "選項A", "B": "選項B", "C": "選項C", "D": "選項D"},
            question_type=QuestionType.MULTIPLE_CHOICE,
            difficulty=QuestionDifficulty.MEDIUM,
            is_group_question=False,
            confidence_score=0.8
        ),
        ParsedQuestion(
            question_number="2",
            question_text="太短",
            options={},
            question_type=QuestionType.MULTIPLE_CHOICE,
            difficulty=QuestionDifficulty.EASY,
            is_group_question=False,
            confidence_score=0.2
        ),
        ParsedQuestion(
            question_number="3",
            question_text="下列敘述何者正確？",
            options={"A": "選項A", "B": "選項A"},  # 重複選項
            question_type=QuestionType.MULTIPLE_CHOICE,
            difficulty=QuestionDifficulty.MEDIUM,
            is_group_question=False,
            confidence_score=0.6
        ),
    ]
    
    print("🧪 驗證器測試")
    print("=" * 50)
    
    # 測試不同驗證等級
    for level in [ValidationLevel.BASIC, ValidationLevel.STANDARD, ValidationLevel.STRICT]:
        print(f"\n📊 {level.value.upper()} 驗證等級:")
        validator = ComprehensiveValidator(level)
        report = validator.validate_questions(test_questions)
        
        print(f"  通過: {report.passed_questions}")
        print(f"  警告: {report.warning_questions}")
        print(f"  失敗: {report.failed_questions}")
        print(f"  分數: {report.overall_score:.2f}")
    
    # 生成詳細報告
    validator = ComprehensiveValidator(ValidationLevel.STANDARD)
    report = validator.validate_questions(test_questions)
    report_content = validator.generate_validation_report(report, "test_output/validation_report.md")
    print(f"\n📄 報告長度: {len(report_content)} 字元")

if __name__ == "__main__":
    test_validator()