#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
題目掃描追蹤器測試
測試題目掃描記錄和完整性驗證
"""

import unittest
import tempfile
import json
import os
from src.utils.question_scan_tracker import QuestionScanTracker, QuestionScanStatus


class TestQuestionScanStatus(unittest.TestCase):
    """題目掃描狀態測試"""

    def test_init(self):
        """測試初始化"""
        status = QuestionScanStatus(1)

        self.assertEqual(status.question_num, 1)
        self.assertFalse(status.scanned)
        self.assertIsNone(status.parser_used)
        self.assertIsNone(status.scan_time)
        self.assertEqual(status.content_preview, "")
        self.assertEqual(status.scan_attempts, [])
        self.assertEqual(status.warnings, [])

    def test_mark_scanned(self):
        """測試標記為已掃描"""
        status = QuestionScanStatus(1)
        status.mark_scanned("TestParser", "這是一道測試題目")

        self.assertTrue(status.scanned)
        self.assertEqual(status.parser_used, "TestParser")
        self.assertIsNotNone(status.scan_time)
        self.assertEqual(status.content_preview, "這是一道測試題目")
        self.assertEqual(len(status.scan_attempts), 1)
        self.assertEqual(status.scan_attempts[0]['parser'], "TestParser")
        self.assertTrue(status.scan_attempts[0]['success'])

    def test_add_attempt(self):
        """測試添加掃描嘗試"""
        status = QuestionScanStatus(1)
        status.add_attempt("Parser1", False, "解析失敗")
        status.add_attempt("Parser2", True)

        self.assertEqual(len(status.scan_attempts), 2)
        self.assertFalse(status.scan_attempts[0]['success'])
        self.assertEqual(status.scan_attempts[0]['error'], "解析失敗")
        self.assertTrue(status.scan_attempts[1]['success'])

    def test_add_warning(self):
        """測試添加警告"""
        status = QuestionScanStatus(1)
        status.add_warning("題目內容過短")

        self.assertEqual(len(status.warnings), 1)
        self.assertEqual(status.warnings[0]['message'], "題目內容過短")
        self.assertIn('time', status.warnings[0])

    def test_to_dict(self):
        """測試轉換為字典"""
        status = QuestionScanStatus(1)
        status.mark_scanned("TestParser", "測試題目")

        data = status.to_dict()

        self.assertEqual(data['question_num'], 1)
        self.assertTrue(data['scanned'])
        self.assertEqual(data['parser_used'], "TestParser")
        self.assertIn('scan_time', data)
        self.assertIn('scan_attempts', data)


class TestQuestionScanTracker(unittest.TestCase):
    """題目掃描追蹤器測試"""

    def setUp(self):
        """測試前準備"""
        self.tracker = QuestionScanTracker()

    def test_init(self):
        """測試初始化"""
        tracker = QuestionScanTracker(expected_count=50)

        self.assertEqual(tracker.expected_count, 50)
        self.assertEqual(tracker.scan_status, {})
        self.assertIsNone(tracker.scan_start_time)
        self.assertIsNone(tracker.scan_end_time)
        self.assertEqual(tracker.total_scanned, 0)
        self.assertEqual(tracker.missing_questions, [])
        self.assertEqual(tracker.duplicate_questions, [])

    def test_start_scan(self):
        """測試開始掃描"""
        self.tracker.start_scan(expected_count=60)

        self.assertEqual(self.tracker.expected_count, 60)
        self.assertIsNotNone(self.tracker.scan_start_time)

    def test_register_question(self):
        """測試註冊題目"""
        self.tracker.register_question(1, "TestParser", "這是第一題")
        self.tracker.register_question(2, "TestParser", "這是第二題")

        self.assertEqual(self.tracker.total_scanned, 2)
        self.assertIn(1, self.tracker.scan_status)
        self.assertIn(2, self.tracker.scan_status)
        self.assertTrue(self.tracker.scan_status[1].scanned)
        self.assertEqual(self.tracker.scan_status[1].parser_used, "TestParser")

    def test_register_duplicate_question(self):
        """測試重複註冊題目"""
        self.tracker.register_question(1, "Parser1", "第一次掃描")
        self.tracker.register_question(1, "Parser2", "第二次掃描")

        # 應該檢測到重複
        self.assertIn(1, self.tracker.duplicate_questions)
        # 只記錄一次
        self.assertEqual(self.tracker.total_scanned, 1)

    def test_record_attempt(self):
        """測試記錄掃描嘗試"""
        self.tracker.record_attempt(1, "Parser1", False, "格式不匹配")
        self.tracker.record_attempt(1, "Parser2", True)

        status = self.tracker.scan_status[1]
        self.assertEqual(len(status.scan_attempts), 2)
        self.assertFalse(status.scan_attempts[0]['success'])

    def test_add_warning(self):
        """測試添加警告"""
        self.tracker.add_warning(1, "題目內容可能有誤")

        status = self.tracker.scan_status[1]
        self.assertEqual(len(status.warnings), 1)
        self.assertEqual(status.warnings[0]['message'], "題目內容可能有誤")

    def test_completeness_check_continuous(self):
        """測試連續題號的完整性檢查"""
        self.tracker.start_scan()

        # 註冊連續的題號 1-5
        for i in range(1, 6):
            self.tracker.register_question(i, "TestParser", f"第{i}題")

        self.tracker.end_scan()

        # 應該沒有遺漏
        self.assertEqual(len(self.tracker.missing_questions), 0)
        self.assertTrue(self.tracker.is_complete())

    def test_completeness_check_missing(self):
        """測試有遺漏的完整性檢查"""
        self.tracker.start_scan()

        # 註冊題號 1, 2, 4, 5（缺少 3）
        for i in [1, 2, 4, 5]:
            self.tracker.register_question(i, "TestParser", f"第{i}題")

        self.tracker.end_scan()

        # 應該檢測到缺少題號 3
        self.assertEqual(self.tracker.missing_questions, [3])
        self.assertFalse(self.tracker.is_complete())

    def test_completeness_check_multiple_missing(self):
        """測試多個遺漏的完整性檢查"""
        self.tracker.start_scan()

        # 註冊題號 1, 3, 5, 8（缺少 2, 4, 6, 7）
        for i in [1, 3, 5, 8]:
            self.tracker.register_question(i, "TestParser", f"第{i}題")

        self.tracker.end_scan()

        # 應該檢測到所有遺漏的題號
        self.assertEqual(self.tracker.missing_questions, [2, 4, 6, 7])
        self.assertFalse(self.tracker.is_complete())

    def test_get_scanned_count(self):
        """測試獲取掃描題數"""
        self.tracker.start_scan()

        for i in range(1, 11):
            self.tracker.register_question(i, "TestParser", f"第{i}題")

        self.assertEqual(self.tracker.get_scanned_count(), 10)

    def test_get_missing_questions(self):
        """測試獲取遺漏題號"""
        self.tracker.start_scan()

        for i in [1, 2, 5, 6]:
            self.tracker.register_question(i, "TestParser", f"第{i}題")

        self.tracker.end_scan()

        missing = self.tracker.get_missing_questions()
        self.assertEqual(missing, [3, 4])

    def test_validate_questions_complete(self):
        """測試驗證完整的題目列表"""
        questions = [
            {'題號': 1, '題目': '問題一'},
            {'題號': 2, '題目': '問題二'},
            {'題號': 3, '題目': '問題三'}
        ]

        is_complete, message = self.tracker.validate_questions(questions)

        self.assertTrue(is_complete)
        self.assertIn('完整', message)

    def test_validate_questions_incomplete(self):
        """測試驗證不完整的題目列表"""
        questions = [
            {'題號': 1, '題目': '問題一'},
            {'題號': 3, '題目': '問題三'},  # 缺少題號 2
            {'題號': 4, '題目': '問題四'}
        ]

        is_complete, message = self.tracker.validate_questions(questions)

        self.assertFalse(is_complete)
        self.assertIn('遺漏', message)
        self.assertIn('2', message)

    def test_validate_questions_duplicate(self):
        """測試驗證有重複題號的題目列表"""
        questions = [
            {'題號': 1, '題目': '問題一'},
            {'題號': 2, '題目': '問題二'},
            {'題號': 2, '題目': '問題二（重複）'}
        ]

        is_complete, message = self.tracker.validate_questions(questions)

        self.assertFalse(is_complete)
        self.assertIn('重複', message)

    def test_validate_questions_empty(self):
        """測試驗證空題目列表"""
        questions = []

        is_complete, message = self.tracker.validate_questions(questions)

        self.assertFalse(is_complete)
        self.assertIn('空', message)

    def test_generate_report(self):
        """測試生成掃描報告"""
        self.tracker.start_scan(expected_count=5)

        for i in range(1, 6):
            self.tracker.register_question(i, "TestParser", f"第{i}題")

        report = self.tracker.end_scan()

        # 驗證報告結構
        self.assertIn('scan_summary', report)
        self.assertIn('missing_questions', report)
        self.assertIn('parser_statistics', report)
        self.assertIn('question_details', report)

        # 驗證報告內容
        self.assertEqual(report['scan_summary']['total_scanned'], 5)
        self.assertEqual(report['scan_summary']['expected_count'], 5)
        self.assertTrue(report['scan_summary']['is_complete'])
        self.assertEqual(len(report['missing_questions']), 0)

    def test_save_report(self):
        """測試保存掃描報告"""
        self.tracker.start_scan()

        for i in range(1, 4):
            self.tracker.register_question(i, "TestParser", f"第{i}題")

        self.tracker.end_scan()

        # 保存到臨時文件
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            temp_path = f.name

        try:
            self.tracker.save_report(temp_path)

            # 驗證文件存在且內容正確
            self.assertTrue(os.path.exists(temp_path))

            with open(temp_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            self.assertIn('scan_summary', data)
            self.assertEqual(data['scan_summary']['total_scanned'], 3)
        finally:
            # 清理臨時文件
            if os.path.exists(temp_path):
                os.remove(temp_path)

    def test_parser_statistics(self):
        """測試解析器統計"""
        self.tracker.start_scan()

        # 使用不同解析器
        self.tracker.register_question(1, "Parser1", "題目1")
        self.tracker.register_question(2, "Parser1", "題目2")
        self.tracker.register_question(3, "Parser2", "題目3")

        report = self.tracker.end_scan()

        stats = report['parser_statistics']
        self.assertEqual(stats['Parser1'], 2)
        self.assertEqual(stats['Parser2'], 1)


if __name__ == '__main__':
    unittest.main()
