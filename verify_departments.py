#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
學系爬取驗證工具
檢查指定學系的學科是否都成功爬取
"""

import os
import json
import glob
from typing import Dict, List, Any, Tuple
from datetime import datetime
import re

class DepartmentVerifier:
    def __init__(self, base_dir: str = "考選部考古題完整庫"):
        self.base_dir = base_dir
        self.target_departments = [
            "警察人員考試三等考試_行政警察人員類別",
            "警察人員考試三等考試_外事警察人員(選試英語)類別", 
            "警察人員考試三等考試_刑事警察人員類別",
            "警察人員考試三等考試_公共安全人員類別",
            "警察人員考試三等考試_犯罪防治人員類別預防組",
            "警察人員考試三等考試_消防警察人員類別",
            "警察人員考試三等考試_交通警察人員類別交通組",
            "警察人員考試三等考試_警察資訊管理人員類別",
            "警察人員考試三等考試_刑事鑑識人員類別",
            "警察人員考試三等考試_國境警察人員類別",
            "警察人員考試三等考試_水上警察人員類別",
            "警察人員考試三等考試_警察法制人員類別",
            "警察人員考試三等考試_交通警察人員電訊組",
            "警察人員考試三等考試_行政管理人員類別",
            "司法三等考試_監獄官(男)",
            "司法三等考試_監獄官(女)"
        ]
        
        # 學系名稱對應到資料夾名稱的映射
        self.department_folder_mapping = {
            "警察人員考試三等考試_行政警察人員類別": "行政警察",
            "警察人員考試三等考試_外事警察人員(選試英語)類別": "外事警察",
            "警察人員考試三等考試_刑事警察人員類別": "刑事警察", 
            "警察人員考試三等考試_公共安全人員類別": "公共安全",
            "警察人員考試三等考試_犯罪防治人員類別預防組": "犯罪防治",
            "警察人員考試三等考試_消防警察人員類別": "消防警察",
            "警察人員考試三等考試_交通警察人員類別交通組": "交通警察_交通",
            "警察人員考試三等考試_警察資訊管理人員類別": "資訊管理",
            "警察人員考試三等考試_刑事鑑識人員類別": "刑事鑑識",
            "警察人員考試三等考試_國境警察人員類別": "國境警察",
            "警察人員考試三等考試_水上警察人員類別": "水上警察",
            "警察人員考試三等考試_警察法制人員類別": "警察法制",
            "警察人員考試三等考試_交通警察人員電訊組": "交通警察_電訊",
            "警察人員考試三等考試_行政管理人員類別": "行政管理",
            "司法三等考試_監獄官(男)": "監獄官",
            "司法三等考試_監獄官(女)": "監獄官"
        }

    def find_exam_years(self) -> List[str]:
        """找出所有可用的考試年份"""
        years = []
        if os.path.exists(self.base_dir):
            for item in os.listdir(self.base_dir):
                if item.startswith("民國") and item.endswith("年"):
                    years.append(item)
        return sorted(years)

    def find_department_folders(self, year: str) -> Dict[str, List[str]]:
        """找出指定年份中所有學系的資料夾"""
        department_folders = {}
        year_path = os.path.join(self.base_dir, year)
        
        if not os.path.exists(year_path):
            return department_folders
            
        # 掃描所有考試資料夾
        for exam_folder in os.listdir(year_path):
            exam_path = os.path.join(year_path, exam_folder)
            if not os.path.isdir(exam_path):
                continue
                
            # 在考試資料夾中尋找學系資料夾
            for dept_folder in os.listdir(exam_path):
                dept_path = os.path.join(exam_path, dept_folder)
                if not os.path.isdir(dept_path):
                    continue
                    
                # 檢查是否為目標學系
                for target_dept, folder_name in self.department_folder_mapping.items():
                    if dept_folder == folder_name:
                        if target_dept not in department_folders:
                            department_folders[target_dept] = []
                        department_folders[target_dept].append(dept_path)
                        break
        
        return department_folders

    def analyze_department_subjects(self, dept_path: str) -> Dict[str, Any]:
        """分析學系的學科資料"""
        result = {
            'path': dept_path,
            'subjects': [],
            'total_files': 0,
            'question_files': 0,
            'answer_files': 0,
            'years_covered': set(),
            'file_details': []
        }
        
        if not os.path.exists(dept_path):
            return result
            
        # 掃描所有科目資料夾
        for subject_folder in os.listdir(dept_path):
            subject_path = os.path.join(dept_path, subject_folder)
            if not os.path.isdir(subject_path):
                continue
                
            subject_info = {
                'name': subject_folder,
                'files': [],
                'has_question': False,
                'has_answer': False
            }
            
            # 掃描科目資料夾中的檔案
            for file_name in os.listdir(subject_path):
                if not file_name.endswith('.pdf'):
                    continue
                    
                file_path = os.path.join(subject_path, file_name)
                file_size = os.path.getsize(file_path)
                
                file_info = {
                    'name': file_name,
                    'path': file_path,
                    'size': file_size,
                    'type': self.classify_file_type(file_name)
                }
                
                subject_info['files'].append(file_info)
                result['total_files'] += 1
                
                if file_info['type'] == 'question':
                    subject_info['has_question'] = True
                    result['question_files'] += 1
                elif file_info['type'] == 'answer':
                    subject_info['has_answer'] = True
                    result['answer_files'] += 1
                
                result['file_details'].append({
                    'subject': subject_folder,
                    'file': file_name,
                    'type': file_info['type'],
                    'size': file_size
                })
            
            if subject_info['files']:
                result['subjects'].append(subject_info)
                
                # 從路徑中提取年份
                year_match = re.search(r'民國(\d+)年', dept_path)
                if year_match:
                    result['years_covered'].add(int(year_match.group(1)))
        
        result['years_covered'] = sorted(list(result['years_covered']))
        return result

    def classify_file_type(self, filename: str) -> str:
        """根據檔名分類檔案類型"""
        filename_lower = filename.lower()
        
        if any(keyword in filename_lower for keyword in ['答案', '解答', 'answer']):
            return 'answer'
        elif any(keyword in filename_lower for keyword in ['試題', '題目', 'question']):
            return 'question'
        else:
            return 'unknown'

    def verify_all_departments(self) -> Dict[str, Any]:
        """驗證所有目標學系"""
        print("🔍 開始驗證學系爬取情況...")
        print("="*70)
        
        verification_result = {
            'timestamp': datetime.now().isoformat(),
            'base_directory': self.base_dir,
            'target_departments': self.target_departments,
            'years_found': [],
            'department_analysis': {},
            'summary': {
                'total_departments': len(self.target_departments),
                'departments_found': 0,
                'departments_missing': 0,
                'total_subjects': 0,
                'total_files': 0,
                'total_question_files': 0,
                'total_answer_files': 0
            }
        }
        
        # 找出所有年份
        years = self.find_exam_years()
        verification_result['years_found'] = years
        print(f"📅 找到 {len(years)} 個年份: {', '.join(years)}")
        
        # 對每個學系進行分析
        for dept_name in self.target_departments:
            print(f"\n🔍 檢查學系: {dept_name}")
            
            dept_analysis = {
                'found': False,
                'years_available': [],
                'total_subjects': 0,
                'total_files': 0,
                'question_files': 0,
                'answer_files': 0,
                'details': []
            }
            
            # 在所有年份中尋找此學系
            for year in years:
                year_departments = self.find_department_folders(year)
                
                if dept_name in year_departments:
                    dept_analysis['found'] = True
                    dept_analysis['years_available'].append(year)
                    
                    # 分析每個找到的學系資料夾
                    for dept_path in year_departments[dept_name]:
                        analysis = self.analyze_department_subjects(dept_path)
                        dept_analysis['details'].append(analysis)
                        dept_analysis['total_subjects'] += len(analysis['subjects'])
                        dept_analysis['total_files'] += analysis['total_files']
                        dept_analysis['question_files'] += analysis['question_files']
                        dept_analysis['answer_files'] += analysis['answer_files']
            
            verification_result['department_analysis'][dept_name] = dept_analysis
            
            # 更新統計
            if dept_analysis['found']:
                verification_result['summary']['departments_found'] += 1
                verification_result['summary']['total_subjects'] += dept_analysis['total_subjects']
                verification_result['summary']['total_files'] += dept_analysis['total_files']
                verification_result['summary']['total_question_files'] += dept_analysis['question_files']
                verification_result['summary']['total_answer_files'] += dept_analysis['answer_files']
                
                print(f"   ✅ 找到 {len(dept_analysis['years_available'])} 個年份的資料")
                print(f"   📚 科目: {dept_analysis['total_subjects']} 個")
                print(f"   📄 檔案: {dept_analysis['total_files']} 個 (試題: {dept_analysis['question_files']}, 答案: {dept_analysis['answer_files']})")
            else:
                verification_result['summary']['departments_missing'] += 1
                print(f"   ❌ 未找到任何資料")
        
        return verification_result

    def generate_report(self, result: Dict[str, Any]) -> str:
        """生成驗證報告"""
        report_lines = []
        
        report_lines.append("="*70)
        report_lines.append("學系爬取驗證報告")
        report_lines.append("="*70)
        report_lines.append(f"生成時間: {result['timestamp']}")
        report_lines.append(f"基礎目錄: {result['base_directory']}")
        report_lines.append(f"掃描年份: {', '.join(result['years_found'])}")
        report_lines.append("")
        
        # 總體統計
        summary = result['summary']
        report_lines.append("📊 總體統計")
        report_lines.append("-"*40)
        report_lines.append(f"目標學系總數: {summary['total_departments']}")
        report_lines.append(f"找到學系數: {summary['departments_found']}")
        report_lines.append(f"缺失學系數: {summary['departments_missing']}")
        report_lines.append(f"總科目數: {summary['total_subjects']}")
        report_lines.append(f"總檔案數: {summary['total_files']}")
        report_lines.append(f"試題檔案: {summary['total_question_files']}")
        report_lines.append(f"答案檔案: {summary['total_answer_files']}")
        report_lines.append("")
        
        # 詳細分析
        report_lines.append("📋 詳細分析")
        report_lines.append("-"*40)
        
        for dept_name, analysis in result['department_analysis'].items():
            report_lines.append(f"\n🔍 {dept_name}")
            
            if analysis['found']:
                report_lines.append(f"   ✅ 狀態: 已找到")
                report_lines.append(f"   📅 年份: {', '.join(analysis['years_available'])}")
                report_lines.append(f"   📚 科目數: {analysis['total_subjects']}")
                report_lines.append(f"   📄 檔案數: {analysis['total_files']} (試題: {analysis['question_files']}, 答案: {analysis['answer_files']})")
                
                # 列出每個年份的詳細資訊
                for detail in analysis['details']:
                    year_match = re.search(r'民國(\d+)年', detail['path'])
                    year = year_match.group(1) if year_match else "未知"
                    report_lines.append(f"   📁 民國{year}年: {len(detail['subjects'])} 科目, {detail['total_files']} 檔案")
                    
                    # 列出科目
                    for subject in detail['subjects']:
                        report_lines.append(f"      - {subject['name']}: {len(subject['files'])} 檔案")
            else:
                report_lines.append(f"   ❌ 狀態: 未找到")
        
        # 缺失學系清單
        missing_departments = [dept for dept, analysis in result['department_analysis'].items() 
                              if not analysis['found']]
        
        if missing_departments:
            report_lines.append(f"\n⚠️ 缺失學系清單 ({len(missing_departments)} 個)")
            report_lines.append("-"*40)
            for dept in missing_departments:
                report_lines.append(f"   ❌ {dept}")
        
        return "\n".join(report_lines)

    def save_report(self, result: Dict[str, Any], output_file: str = "學系驗證報告.txt"):
        """儲存報告到檔案"""
        report_text = self.generate_report(result)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(report_text)
        
        # 同時儲存JSON格式的詳細資料
        json_file = output_file.replace('.txt', '.json')
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        print(f"\n📄 報告已儲存:")
        print(f"   文字報告: {output_file}")
        print(f"   詳細資料: {json_file}")

def main():
    print("學系爬取驗證工具")
    print("="*70)
    
    # 檢查基礎目錄是否存在
    possible_dirs = [
        "考選部考古題完整庫",
        "考古題",
        "考選部",
        "."
    ]
    
    base_dir = None
    for dir_name in possible_dirs:
        if os.path.exists(dir_name):
            # 檢查是否包含年份資料夾
            years_found = []
            for item in os.listdir(dir_name):
                if item.startswith("民國") and item.endswith("年"):
                    years_found.append(item)
            
            if years_found:
                base_dir = dir_name
                print(f"✅ 找到基礎目錄: {base_dir}")
                print(f"📅 發現年份: {', '.join(sorted(years_found))}")
                break
    
    if not base_dir:
        print(f"❌ 錯誤: 找不到包含考古題資料的目錄")
        print("請先執行爬蟲下載資料，或確認資料目錄位置")
        print("可能的目錄名稱:", ", ".join(possible_dirs))
        return
    
    # 創建驗證器
    verifier = DepartmentVerifier(base_dir)
    
    # 執行驗證
    result = verifier.verify_all_departments()
    
    # 顯示結果
    print("\n" + "="*70)
    print("驗證結果摘要")
    print("="*70)
    
    summary = result['summary']
    print(f"✅ 找到學系: {summary['departments_found']}/{summary['total_departments']}")
    print(f"📚 總科目數: {summary['total_subjects']}")
    print(f"📄 總檔案數: {summary['total_files']}")
    print(f"📅 涵蓋年份: {len(result['years_found'])} 個")
    
    # 生成並儲存報告
    verifier.save_report(result)
    
    # 顯示缺失的學系
    missing = [dept for dept, analysis in result['department_analysis'].items() 
               if not analysis['found']]
    
    if missing:
        print(f"\n⚠️ 缺失學系 ({len(missing)} 個):")
        for dept in missing:
            print(f"   ❌ {dept}")
    else:
        print(f"\n🎉 所有目標學系都已成功爬取！")

if __name__ == "__main__":
    main()