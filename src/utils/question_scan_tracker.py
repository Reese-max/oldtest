#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
題目掃描追蹤器
確保每一題都被掃描到，記錄完整的掃描狀態和遺漏題號
"""

import json
from typing import Dict, List, Any, Set, Tuple, Optional
from datetime import datetime
from .logger import logger


class QuestionScanStatus:
    """單一題目掃描狀態"""

    def __init__(self, question_num: int):
        self.question_num = question_num
        self.scanned = False
        self.parser_used = None
        self.scan_time = None
        self.content_preview = ""
        self.scan_attempts = []
        self.warnings = []

    def mark_scanned(self, parser_name: str, content: str = ""):
        """標記為已掃描"""
        self.scanned = True
        self.parser_used = parser_name
        self.scan_time = datetime.now().isoformat()
        self.content_preview = content[:50] if content else ""
        self.scan_attempts.append({
            'parser': parser_name,
            'time': self.scan_time,
            'success': True
        })

    def add_attempt(self, parser_name: str, success: bool, error: str = ""):
        """記錄掃描嘗試"""
        self.scan_attempts.append({
            'parser': parser_name,
            'time': datetime.now().isoformat(),
            'success': success,
            'error': error
        })

    def add_warning(self, message: str):
        """添加警告訊息"""
        self.warnings.append({
            'message': message,
            'time': datetime.now().isoformat()
        })

    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典"""
        return {
            'question_num': self.question_num,
            'scanned': self.scanned,
            'parser_used': self.parser_used,
            'scan_time': self.scan_time,
            'content_preview': self.content_preview,
            'scan_attempts': self.scan_attempts,
            'warnings': self.warnings
        }


class QuestionScanTracker:
    """題目掃描追蹤器 - 確保每一題都被掃描"""

    def __init__(self, expected_count: int = None):
        """
        初始化掃描追蹤器

        Args:
            expected_count: 預期題目數量（如果已知）
        """
        self.logger = logger
        self.expected_count = expected_count
        self.scan_status: Dict[int, QuestionScanStatus] = {}
        self.scan_start_time = None
        self.scan_end_time = None
        self.total_scanned = 0
        self.missing_questions: List[int] = []
        self.duplicate_questions: List[int] = []
        self.parsers_used: Set[str] = set()

    def start_scan(self, expected_count: int = None):
        """開始掃描"""
        self.scan_start_time = datetime.now()
        if expected_count:
            self.expected_count = expected_count

        self.logger.info(f"📊 開始題目掃描追蹤（預期題數: {self.expected_count or '未知'}）")

    def register_question(self, question_num: int, parser_name: str, content: str = ""):
        """
        註冊已掃描的題目

        Args:
            question_num: 題號
            parser_name: 使用的解析器名稱
            content: 題目內容預覽
        """
        # 檢查是否重複
        if question_num in self.scan_status:
            if self.scan_status[question_num].scanned:
                self.duplicate_questions.append(question_num)
                self.logger.warning(f"⚠️  重複掃描: 第{question_num}題 (已由 {self.scan_status[question_num].parser_used} 掃描)")
                return

        # 創建或更新掃描狀態
        if question_num not in self.scan_status:
            self.scan_status[question_num] = QuestionScanStatus(question_num)

        self.scan_status[question_num].mark_scanned(parser_name, content)
        self.parsers_used.add(parser_name)
        self.total_scanned += 1

        self.logger.debug(f"✓ 掃描: 第{question_num}題 [{parser_name}] {content[:30]}...")

    def record_attempt(self, question_num: int, parser_name: str, success: bool, error: str = ""):
        """
        記錄掃描嘗試（包括失敗的嘗試）

        Args:
            question_num: 題號
            parser_name: 解析器名稱
            success: 是否成功
            error: 錯誤訊息（如果失敗）
        """
        if question_num not in self.scan_status:
            self.scan_status[question_num] = QuestionScanStatus(question_num)

        self.scan_status[question_num].add_attempt(parser_name, success, error)

        if not success:
            self.logger.debug(f"✗ 嘗試失敗: 第{question_num}題 [{parser_name}] {error}")

    def add_warning(self, question_num: int, message: str):
        """添加題目警告"""
        if question_num not in self.scan_status:
            self.scan_status[question_num] = QuestionScanStatus(question_num)

        self.scan_status[question_num].add_warning(message)
        self.logger.warning(f"⚠️  第{question_num}題: {message}")

    def end_scan(self):
        """結束掃描並進行完整性檢查"""
        self.scan_end_time = datetime.now()

        # 檢查題號連續性和完整性
        self._check_completeness()

        # 生成報告
        report = self.generate_report()

        # 輸出摘要
        self._log_summary()

        return report

    def _check_completeness(self):
        """檢查題目完整性"""
        if not self.scan_status:
            self.logger.error("❌ 未掃描到任何題目！")
            return

        # 獲取所有已掃描的題號
        scanned_nums = [num for num, status in self.scan_status.items() if status.scanned]
        scanned_nums.sort()

        if not scanned_nums:
            self.logger.error("❌ 所有題目掃描失敗！")
            return

        # 檢查題號連續性
        min_num = scanned_nums[0]
        max_num = scanned_nums[-1]
        expected_nums = set(range(min_num, max_num + 1))
        scanned_set = set(scanned_nums)

        # 找出遺漏的題號
        self.missing_questions = sorted(list(expected_nums - scanned_set))

        # 如果設定了預期題數，也檢查總數
        if self.expected_count:
            if len(scanned_nums) < self.expected_count:
                self.logger.warning(
                    f"⚠️  掃描題數不足: 預期 {self.expected_count} 題，實際 {len(scanned_nums)} 題"
                )

    def _log_summary(self):
        """輸出掃描摘要"""
        self.logger.info("=" * 60)
        self.logger.info("📊 題目掃描完整性報告")
        self.logger.info("=" * 60)

        if self.scan_status:
            scanned_nums = [num for num, status in self.scan_status.items() if status.scanned]
            scanned_nums.sort()

            self.logger.info(f"✅ 成功掃描: {len(scanned_nums)} 題")
            self.logger.info(f"📝 題號範圍: {min(scanned_nums)} ~ {max(scanned_nums)}")

            if self.missing_questions:
                self.logger.error(f"❌ 遺漏題號: {self.missing_questions}")
                self.logger.error(f"   共遺漏 {len(self.missing_questions)} 題")
            else:
                self.logger.success("✅ 題號連續，無遺漏")

            if self.duplicate_questions:
                self.logger.warning(f"⚠️  重複掃描: {set(self.duplicate_questions)}")

            # 解析器使用統計
            parser_stats = {}
            for status in self.scan_status.values():
                if status.scanned and status.parser_used:
                    parser_stats[status.parser_used] = parser_stats.get(status.parser_used, 0) + 1

            self.logger.info(f"🔧 使用的解析器:")
            for parser, count in parser_stats.items():
                self.logger.info(f"   - {parser}: {count} 題")
        else:
            self.logger.error("❌ 未掃描到任何題目")

        # 掃描時間
        if self.scan_start_time and self.scan_end_time:
            duration = (self.scan_end_time - self.scan_start_time).total_seconds()
            self.logger.info(f"⏱️  掃描耗時: {duration:.2f} 秒")

        self.logger.info("=" * 60)

    def generate_report(self) -> Dict[str, Any]:
        """
        生成詳細的掃描報告

        Returns:
            完整的掃描報告字典
        """
        scanned_nums = [num for num, status in self.scan_status.items() if status.scanned]
        scanned_nums.sort()

        # 解析器統計
        parser_stats = {}
        for status in self.scan_status.values():
            if status.scanned and status.parser_used:
                parser_stats[status.parser_used] = parser_stats.get(status.parser_used, 0) + 1

        # 計算掃描時間
        duration = None
        if self.scan_start_time and self.scan_end_time:
            duration = (self.scan_end_time - self.scan_start_time).total_seconds()

        report = {
            'scan_summary': {
                'total_scanned': len(scanned_nums),
                'expected_count': self.expected_count,
                'question_range': f"{min(scanned_nums)} ~ {max(scanned_nums)}" if scanned_nums else "N/A",
                'is_complete': len(self.missing_questions) == 0,
                'missing_count': len(self.missing_questions),
                'duplicate_count': len(self.duplicate_questions),
                'scan_duration': duration
            },
            'missing_questions': self.missing_questions,
            'duplicate_questions': list(set(self.duplicate_questions)),
            'parser_statistics': parser_stats,
            'parsers_used': list(self.parsers_used),
            'question_details': {
                num: status.to_dict()
                for num, status in sorted(self.scan_status.items())
            },
            'scan_times': {
                'start': self.scan_start_time.isoformat() if self.scan_start_time else None,
                'end': self.scan_end_time.isoformat() if self.scan_end_time else None
            }
        }

        return report

    def save_report(self, output_path: str):
        """
        保存詳細報告到文件

        Args:
            output_path: 輸出文件路徑
        """
        report = self.generate_report()

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)

        self.logger.success(f"✅ 掃描報告已保存: {output_path}")

    def get_missing_questions(self) -> List[int]:
        """獲取遺漏的題號列表"""
        return self.missing_questions

    def is_complete(self) -> bool:
        """檢查掃描是否完整（無遺漏）"""
        return len(self.missing_questions) == 0

    def get_scanned_count(self) -> int:
        """獲取成功掃描的題目數量"""
        return sum(1 for status in self.scan_status.values() if status.scanned)

    def validate_questions(self, questions: List[Dict[str, Any]]) -> Tuple[bool, str]:
        """
        驗證題目列表的完整性

        Args:
            questions: 題目列表

        Returns:
            (是否完整, 驗證訊息)
        """
        if not questions:
            return False, "題目列表為空"

        question_nums = [q.get('題號', 0) for q in questions]
        question_nums.sort()

        # 檢查題號連續性
        min_num = question_nums[0]
        max_num = question_nums[-1]
        expected_nums = set(range(min_num, max_num + 1))
        actual_nums = set(question_nums)

        missing = sorted(list(expected_nums - actual_nums))

        if missing:
            return False, f"遺漏題號: {missing}"

        # 檢查重複
        if len(question_nums) != len(set(question_nums)):
            duplicates = [num for num in set(question_nums) if question_nums.count(num) > 1]
            return False, f"重複題號: {duplicates}"

        return True, f"完整無遺漏（{len(question_nums)} 題）"
