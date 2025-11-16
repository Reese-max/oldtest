#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量處理工具
支援大量考古題的批量處理
"""

import os
import sys
import json
import glob
from datetime import datetime
from typing import List, Dict, Any

# 添加src目錄到路徑
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.api import ArchaeologyAPI
from src.utils.logger import logger
from src.utils.quality_validator import QualityValidator


class BatchProcessor:
    """批量處理器"""
    
    def __init__(self):
        self.api = ArchaeologyAPI()
        self.quality_validator = QualityValidator()
        self.logger = logger
    
    def process_archaeology_library(self, library_path: str, output_base_dir: str = None) -> Dict[str, Any]:
        """
        批量處理考古題庫
        
        Args:
            library_path: 考古題庫路徑
            output_base_dir: 輸出基礎目錄
            
        Returns:
            處理結果統計
        """
        if not output_base_dir:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_base_dir = f"/workspace/test_output/批量處理_{timestamp}"
        
        os.makedirs(output_base_dir, exist_ok=True)
        
        self.logger.info(f"開始批量處理考古題庫: {library_path}")
        self.logger.info(f"輸出目錄: {output_base_dir}")
        
        # 統計資訊
        stats = {
            'total_exams': 0,
            'successful_exams': 0,
            'failed_exams': 0,
            'total_questions': 0,
            'processing_time': 0,
            'exam_results': [],
            'quality_reports': []
        }
        
        start_time = datetime.now()
        
        # 尋找所有考試目錄
        exam_dirs = self._find_exam_directories(library_path)
        stats['total_exams'] = len(exam_dirs)
        
        self.logger.info(f"找到 {len(exam_dirs)} 個考試目錄")
        
        for exam_dir in exam_dirs:
            try:
                result = self._process_exam_directory(exam_dir, output_base_dir)
                stats['exam_results'].append(result)
                
                if result['success']:
                    stats['successful_exams'] += 1
                    stats['total_questions'] += result['question_count']
                else:
                    stats['failed_exams'] += 1
                
                self.logger.info(f"✅ {result['exam_name']}: {result['question_count']} 題")
                
            except Exception as e:
                self.logger.failure(f"❌ 處理失敗: {exam_dir} - {e}")
                stats['failed_exams'] += 1
                stats['exam_results'].append({
                    'exam_name': os.path.basename(exam_dir),
                    'success': False,
                    'error': str(e),
                    'question_count': 0
                })
        
        # 計算處理時間
        end_time = datetime.now()
        stats['processing_time'] = (end_time - start_time).total_seconds()
        
        # 生成批量處理報告
        self._generate_batch_report(stats, output_base_dir)
        
        self.logger.success(f"批量處理完成: {stats['successful_exams']}/{stats['total_exams']} 成功")
        return stats
    
    def _find_exam_directories(self, library_path: str) -> List[str]:
        """尋找考試目錄"""
        exam_dirs = []
        
        # 尋找所有包含試題PDF的目錄
        for root, dirs, files in os.walk(library_path):
            if '試題.pdf' in files:
                exam_dirs.append(root)
        
        return exam_dirs
    
    def _process_exam_directory(self, exam_dir: str, output_base_dir: str) -> Dict[str, Any]:
        """處理單個考試目錄"""
        exam_name = os.path.basename(exam_dir)
        output_dir = os.path.join(output_base_dir, exam_name)
        
        # 尋找試題和答案檔案
        question_pdf = os.path.join(exam_dir, '試題.pdf')
        answer_pdf = os.path.join(exam_dir, '答案.pdf')
        corrected_pdf = os.path.join(exam_dir, '更正答案.pdf')
        
        if not os.path.exists(question_pdf):
            raise FileNotFoundError(f"找不到試題檔案: {question_pdf}")
        
        # 處理PDF
        result = self.api.process_single_pdf(
            pdf_path=question_pdf,
            answer_pdf_path=answer_pdf if os.path.exists(answer_pdf) else None,
            corrected_answer_pdf_path=corrected_pdf if os.path.exists(corrected_pdf) else None,
            output_dir=output_dir,
            generate_script=True
        )
        
        if not result['success']:
            raise Exception(result['message'])
        
        # 讀取生成的CSV檔案進行品質驗證
        csv_file = os.path.join(output_dir, '試題_Google表單.csv')
        if os.path.exists(csv_file):
            questions = self._load_questions_from_csv(csv_file)
            quality_stats = self.quality_validator.validate_questions(questions)
            
            # 生成品質報告
            quality_report_path = os.path.join(output_dir, '品質報告.md')
            self.quality_validator.generate_quality_report(quality_stats, quality_report_path)
        
        return {
            'exam_name': exam_name,
            'success': True,
            'question_count': result.get('question_count', 0),
            'output_dir': output_dir,
            'quality_stats': quality_stats if 'quality_stats' in locals() else None
        }
    
    def _load_questions_from_csv(self, csv_file: str) -> List[Dict[str, Any]]:
        """從CSV檔案載入題目"""
        import pandas as pd
        
        try:
            df = pd.read_csv(csv_file, encoding='utf-8-sig')
            questions = df.to_dict('records')
            return questions
        except Exception as e:
            self.logger.warning(f"載入CSV失敗: {e}")
            return []
    
    def _generate_batch_report(self, stats: Dict[str, Any], output_base_dir: str):
        """生成批量處理報告"""
        report_path = os.path.join(output_base_dir, '批量處理報告.md')
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("# 批量處理報告\n\n")
            f.write(f"**處理時間**: {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}\n")
            f.write(f"**總耗時**: {stats['processing_time']:.2f} 秒\n\n")
            
            # 基本統計
            f.write("## 📊 處理統計\n\n")
            f.write(f"- **總考試數**: {stats['total_exams']}\n")
            f.write(f"- **成功數**: {stats['successful_exams']}\n")
            f.write(f"- **失敗數**: {stats['failed_exams']}\n")
            f.write(f"- **成功率**: {stats['successful_exams']/stats['total_exams']*100:.1f}%\n")
            f.write(f"- **總題數**: {stats['total_questions']}\n")
            f.write(f"- **平均每考試題數**: {stats['total_questions']/stats['successful_exams'] if stats['successful_exams'] > 0 else 0:.1f}\n\n")
            
            # 詳細結果
            f.write("## 📋 詳細結果\n\n")
            f.write("| 考試名稱 | 狀態 | 題數 | 輸出目錄 |\n")
            f.write("|---------|------|------|----------|\n")
            
            for result in stats['exam_results']:
                status = "✅ 成功" if result['success'] else "❌ 失敗"
                question_count = result.get('question_count', 0)
                output_dir = result.get('output_dir', 'N/A')
                f.write(f"| {result['exam_name']} | {status} | {question_count} | {output_dir} |\n")
            
            # 失敗原因
            failed_exams = [r for r in stats['exam_results'] if not r['success']]
            if failed_exams:
                f.write("\n## ❌ 失敗原因\n\n")
                for result in failed_exams:
                    f.write(f"- **{result['exam_name']}**: {result.get('error', '未知錯誤')}\n")
            
            # 建議
            f.write("\n## 💡 建議\n\n")
            if stats['failed_exams'] > 0:
                f.write("- 檢查失敗的考試，可能需要調整解析邏輯\n")
            if stats['successful_exams'] > 0:
                f.write("- 批量處理成功，系統運行穩定\n")
                f.write("- 建議定期執行批量處理以驗證系統穩定性\n")
        
        self.logger.success(f"批量處理報告已生成: {report_path}")


def main():
    """主函數"""
    import argparse
    
    parser = argparse.ArgumentParser(description='批量處理考古題')
    parser.add_argument('--library-path', required=True, help='考古題庫路徑')
    parser.add_argument('--output-dir', help='輸出目錄')
    
    args = parser.parse_args()
    
    processor = BatchProcessor()
    stats = processor.process_archaeology_library(args.library_path, args.output_dir)
    
    print(f"\n批量處理完成！")
    print(f"成功: {stats['successful_exams']}/{stats['total_exams']}")
    print(f"總題數: {stats['total_questions']}")
    print(f"耗時: {stats['processing_time']:.2f} 秒")


if __name__ == '__main__':
    main()