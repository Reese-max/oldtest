#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
高强度测试脚本
全面验证系统的稳定性、准确性和性能
"""

import sys
import os
import json
import time
from pathlib import Path
from collections import defaultdict, Counter

sys.path.insert(0, '/home/user/oldtest')

from src.processors.archaeology_processor import ArchaeologyProcessor


def find_all_test_pdfs(base_path):
    """查找所有试题PDF"""
    pdf_files = []
    for pdf_path in Path(base_path).rglob("試題.pdf"):
        parent_dir = pdf_path.parent
        answer_path = parent_dir / "答案.pdf"

        parts = str(pdf_path.parent).split('/')
        exam_type = parts[-3] if len(parts) >= 3 else "未知"
        position = parts[-2] if len(parts) >= 2 else "未知"
        subject = parts[-1] if len(parts) >= 1 else "未知"

        pdf_files.append({
            'exam_type': exam_type,
            'position': position,
            'subject': subject,
            'pdf_path': str(pdf_path),
            'answer_path': str(answer_path) if answer_path.exists() else None,
            'full_name': f"{exam_type}/{position}/{subject}"
        })

    return pdf_files


def test_1_completeness(pdf_files, processor):
    """测试1: 完整性验证"""
    print("=" * 80)
    print("🧪 测试1: 完整性验证")
    print("=" * 80)
    print("验证所有解析的题目是否完整、题号是否连续\n")
    
    results = {
        'total': 0,
        'success': 0,
        'issues': []
    }
    
    for pdf_info in pdf_files:
        text = processor.pdf_processor.extract_text(pdf_info['pdf_path'])
        questions = processor._parse_standard(text)
        
        if len(questions) >= 2:
            results['total'] += 1

            # 检查题号连续性（转换为整数）
            try:
                question_nums_int = sorted([int(q['題號']) if isinstance(q['題號'], str) else q['題號'] for q in questions])
            except (ValueError, TypeError):
                question_nums_int = sorted([q['題號'] for q in questions])

            # 检查重复
            num_counts = Counter(question_nums_int)
            duplicates = {num: count for num, count in num_counts.items() if count > 1}

            # 检查缺漏（假设题号应该是1到max连续）
            if question_nums_int:
                expected = list(range(1, max(question_nums_int) + 1))
                missing = set(expected) - set(question_nums_int)
                
                has_issues = False
                issue_details = []
                
                if duplicates:
                    has_issues = True
                    issue_details.append(f"重复题号: {duplicates}")
                
                if missing:
                    has_issues = True
                    issue_details.append(f"缺失题号: {sorted(missing)}")
                
                if has_issues:
                    results['issues'].append({
                        'name': pdf_info['full_name'],
                        'question_count': len(questions),
                        'issues': issue_details
                    })
                else:
                    results['success'] += 1
    
    # 输出结果
    print(f"测试PDF数: {results['total']}")
    print(f"✅ 完整无问题: {results['success']} ({results['success']/results['total']*100:.1f}%)")
    print(f"⚠️  有问题: {len(results['issues'])} ({len(results['issues'])/results['total']*100:.1f}%)")
    
    if results['issues']:
        print("\n问题详情:")
        for issue in results['issues'][:5]:  # 只显示前5个
            print(f"  - {issue['name']}: {', '.join(issue['issues'])}")
    
    return results


def test_2_answer_matching(pdf_files, processor):
    """测试2: 答案匹配验证"""
    print("\n" + "=" * 80)
    print("🧪 测试2: 答案匹配验证")
    print("=" * 80)
    print("验证所有有答案的PDF的匹配率\n")
    
    results = {
        'total_with_answer': 0,
        'perfect_match': 0,
        'partial_match': 0,
        'match_rates': []
    }
    
    for pdf_info in pdf_files:
        if not pdf_info['answer_path']:
            continue
        
        text = processor.pdf_processor.extract_text(pdf_info['pdf_path'])
        questions = processor._parse_standard(text)
        
        if len(questions) >= 2:
            answer_text = processor.pdf_processor.extract_text(pdf_info['answer_path'])
            answers = processor.answer_processor.extract_answers(answer_text)
            
            if answers:
                results['total_with_answer'] += 1
                
                matched = sum(1 for q in questions if str(q['題號']) in answers)
                match_rate = (matched / len(questions)) * 100
                
                results['match_rates'].append(match_rate)
                
                if match_rate == 100:
                    results['perfect_match'] += 1
                else:
                    results['partial_match'] += 1
    
    # 输出结果
    if results['total_with_answer'] > 0:
        avg_match_rate = sum(results['match_rates']) / len(results['match_rates'])
        
        print(f"有答案PDF数: {results['total_with_answer']}")
        print(f"✅ 完美匹配(100%): {results['perfect_match']} ({results['perfect_match']/results['total_with_answer']*100:.1f}%)")
        print(f"⚠️  部分匹配(<100%): {results['partial_match']} ({results['partial_match']/results['total_with_answer']*100:.1f}%)")
        print(f"📊 平均匹配率: {avg_match_rate:.2f}%")
        
        if results['partial_match'] > 0:
            print("\n匹配率分布:")
            for rate in sorted(results['match_rates']):
                if rate < 100:
                    print(f"  - {rate:.1f}%")
    
    return results


def test_3_consistency(pdf_files, processor):
    """测试3: 一致性测试"""
    print("\n" + "=" * 80)
    print("🧪 测试3: 一致性测试")
    print("=" * 80)
    print("重复解析同一PDF 3次，验证结果是否一致\n")
    
    # 随机选择5个PDF进行测试
    import random
    test_pdfs = random.sample(pdf_files, min(5, len(pdf_files)))
    
    results = {
        'total': 0,
        'consistent': 0,
        'inconsistent': 0,
        'details': []
    }
    
    for pdf_info in test_pdfs:
        results['total'] += 1
        
        # 解析3次
        runs = []
        for i in range(3):
            text = processor.pdf_processor.extract_text(pdf_info['pdf_path'])
            questions = processor._parse_standard(text)
            runs.append({
                'count': len(questions),
                'question_nums': sorted([q['題號'] for q in questions])
            })
        
        # 检查一致性
        is_consistent = all(
            run['count'] == runs[0]['count'] and 
            run['question_nums'] == runs[0]['question_nums']
            for run in runs
        )
        
        if is_consistent:
            results['consistent'] += 1
        else:
            results['inconsistent'] += 1
            results['details'].append({
                'name': pdf_info['subject'],
                'runs': runs
            })
    
    # 输出结果
    print(f"测试PDF数: {results['total']}")
    print(f"✅ 结果一致: {results['consistent']} ({results['consistent']/results['total']*100:.1f}%)")
    print(f"❌ 结果不一致: {results['inconsistent']} ({results['inconsistent']/results['total']*100:.1f}%)")
    
    if results['details']:
        print("\n不一致详情:")
        for detail in results['details']:
            print(f"  - {detail['name']}:")
            for i, run in enumerate(detail['runs'], 1):
                print(f"    运行{i}: {run['count']}题")
    
    return results


def test_4_performance(pdf_files, processor):
    """测试4: 性能测试"""
    print("\n" + "=" * 80)
    print("🧪 测试4: 性能测试")
    print("=" * 80)
    print("测试处理速度和性能指标\n")
    
    results = {
        'total_files': 0,
        'total_time': 0,
        'times': [],
        'questions_per_second': []
    }
    
    for pdf_info in pdf_files[:10]:  # 测试前10个
        start_time = time.time()
        
        text = processor.pdf_processor.extract_text(pdf_info['pdf_path'])
        questions = processor._parse_standard(text)
        
        elapsed = time.time() - start_time
        
        results['total_files'] += 1
        results['total_time'] += elapsed
        results['times'].append(elapsed)
        
        if len(questions) > 0:
            qps = len(questions) / elapsed
            results['questions_per_second'].append(qps)
    
    # 输出结果
    if results['total_files'] > 0:
        avg_time = results['total_time'] / results['total_files']
        min_time = min(results['times'])
        max_time = max(results['times'])
        
        print(f"测试文件数: {results['total_files']}")
        print(f"总耗时: {results['total_time']:.2f}秒")
        print(f"平均处理时间: {avg_time:.3f}秒/PDF")
        print(f"最快: {min_time:.3f}秒")
        print(f"最慢: {max_time:.3f}秒")
        
        if results['questions_per_second']:
            avg_qps = sum(results['questions_per_second']) / len(results['questions_per_second'])
            print(f"平均处理速度: {avg_qps:.1f}题/秒")
    
    return results


def test_5_edge_cases(processor):
    """测试5: 边界情况测试"""
    print("\n" + "=" * 80)
    print("🧪 测试5: 边界情况测试")
    print("=" * 80)
    print("测试空文本、特殊字符等边界情况\n")
    
    results = {
        'total': 0,
        'passed': 0,
        'failed': 0,
        'errors': []
    }
    
    test_cases = [
        ("空文本", ""),
        ("只有空格", "    \n\n    "),
        ("只有数字", "1 2 3 4 5"),
        ("特殊字符", "!@#$%^&*()"),
        ("超长文本", "A" * 10000),
    ]
    
    for name, text in test_cases:
        results['total'] += 1
        try:
            questions = processor._parse_standard(text)
            results['passed'] += 1
            print(f"  ✅ {name}: 通过 (解析{len(questions)}题)")
        except Exception as e:
            results['failed'] += 1
            results['errors'].append({
                'name': name,
                'error': str(e)
            })
            print(f"  ❌ {name}: 失败 - {str(e)[:50]}")
    
    return results


def main():
    """主函数"""
    base_path = "考選部考古題完整庫/民國114年"
    
    print("=" * 80)
    print("🚀 高强度测试开始")
    print("=" * 80)
    print(f"测试目录: {base_path}\n")
    
    # 查找所有PDF
    pdf_files = find_all_test_pdfs(base_path)
    print(f"找到 {len(pdf_files)} 个PDF文件\n")
    
    # 初始化处理器
    processor = ArchaeologyProcessor(use_enhanced=True)
    
    # 执行所有测试
    all_results = {}
    
    all_results['test_1'] = test_1_completeness(pdf_files, processor)
    all_results['test_2'] = test_2_answer_matching(pdf_files, processor)
    all_results['test_3'] = test_3_consistency(pdf_files, processor)
    all_results['test_4'] = test_4_performance(pdf_files, processor)
    all_results['test_5'] = test_5_edge_cases(processor)
    
    # 总结
    print("\n" + "=" * 80)
    print("📊 高强度测试总结")
    print("=" * 80)
    
    print("\n✅ 测试通过情况:")
    print(f"  - 完整性测试: {all_results['test_1']['success']}/{all_results['test_1']['total']} ({all_results['test_1']['success']/all_results['test_1']['total']*100:.1f}%)")
    if all_results['test_2']['total_with_answer'] > 0:
        print(f"  - 答案匹配: {all_results['test_2']['perfect_match']}/{all_results['test_2']['total_with_answer']} ({all_results['test_2']['perfect_match']/all_results['test_2']['total_with_answer']*100:.1f}%)")
    print(f"  - 一致性测试: {all_results['test_3']['consistent']}/{all_results['test_3']['total']} ({all_results['test_3']['consistent']/all_results['test_3']['total']*100:.1f}%)")
    print(f"  - 边界情况: {all_results['test_5']['passed']}/{all_results['test_5']['total']} ({all_results['test_5']['passed']/all_results['test_5']['total']*100:.1f}%)")
    
    print("\n⚡ 性能指标:")
    if all_results['test_4']['total_files'] > 0:
        avg_time = all_results['test_4']['total_time'] / all_results['test_4']['total_files']
        print(f"  - 平均处理时间: {avg_time:.3f}秒/PDF")
        if all_results['test_4']['questions_per_second']:
            avg_qps = sum(all_results['test_4']['questions_per_second']) / len(all_results['test_4']['questions_per_second'])
            print(f"  - 平均处理速度: {avg_qps:.1f}题/秒")
    
    # 保存结果
    with open('high_intensity_test_results.json', 'w', encoding='utf-8') as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2, default=str)
    
    print("\n💾 测试结果已保存到: high_intensity_test_results.json")
    
    # 最终评分
    print("\n" + "=" * 80)
    print("🏆 最终评分")
    print("=" * 80)
    
    scores = []
    if all_results['test_1']['total'] > 0:
        scores.append(all_results['test_1']['success'] / all_results['test_1']['total'])
    if all_results['test_2']['total_with_answer'] > 0:
        scores.append(all_results['test_2']['perfect_match'] / all_results['test_2']['total_with_answer'])
    if all_results['test_3']['total'] > 0:
        scores.append(all_results['test_3']['consistent'] / all_results['test_3']['total'])
    if all_results['test_5']['total'] > 0:
        scores.append(all_results['test_5']['passed'] / all_results['test_5']['total'])
    
    if scores:
        final_score = sum(scores) / len(scores) * 100
        print(f"\n总体得分: {final_score:.1f}/100")
        
        if final_score >= 95:
            print("评级: ⭐⭐⭐⭐⭐ 卓越")
        elif final_score >= 85:
            print("评级: ⭐⭐⭐⭐ 优秀")
        elif final_score >= 75:
            print("评级: ⭐⭐⭐ 良好")
        else:
            print("评级: ⭐⭐ 需改进")
    
    print("\n🎉 高强度测试完成！")


if __name__ == '__main__':
    main()
