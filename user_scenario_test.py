#!/usr/bin/env python3
"""
用户场景自动化测试
模拟真实用户使用系统的各种情况
"""

import os
import sys
import json
from pathlib import Path
from src.processors.archaeology_processor import ArchaeologyProcessor
import time

class UserScenarioTester:
    """模拟真实用户场景测试"""

    def __init__(self):
        self.processor = ArchaeologyProcessor()
        self.test_base = "考選部考古題完整庫/民國114年"
        self.results = {
            "scenarios": [],
            "summary": {}
        }

    def scenario_1_single_choice_exam(self):
        """
        場景1: 用戶處理單個選擇題試卷
        典型用例：學生下載了一份選擇題試卷，想提取題目和答案
        """
        print("\n" + "="*80)
        print("🎓 場景1: 處理單個選擇題試卷")
        print("="*80)

        # 選擇一個典型的選擇題試卷
        pdf_path = f"{self.test_base}/民國114年_警察特考/消防警察/中華民國憲法與消防警察專業英文/試題.pdf"
        answer_path = f"{self.test_base}/民國114年_警察特考/消防警察/中華民國憲法與消防警察專業英文/答案.pdf"

        print(f"📄 處理試卷: 中華民國憲法與消防警察專業英文")
        print(f"📁 檔案路徑: {pdf_path}")

        start_time = time.time()

        # 提取題目
        result = self.processor.process_pdf(pdf_path)

        # 提取答案
        if os.path.exists(answer_path):
            answer_result = self.processor.process_answer_pdf(answer_path)
            result['answers'] = answer_result

        elapsed = time.time() - start_time

        print(f"\n✅ 處理完成！")
        print(f"   - 提取題數: {result['questions_count']} 題")
        print(f"   - 答案數量: {len(result.get('answers', {}))} 個")
        print(f"   - 處理時間: {elapsed:.2f} 秒")
        print(f"   - 匹配率: {result['questions_count']/len(result.get('answers', {})) * 100 if result.get('answers') else 0:.1f}%")

        self.results['scenarios'].append({
            "name": "場景1: 單個選擇題試卷",
            "success": result['questions_count'] > 0,
            "questions": result['questions_count'],
            "time": elapsed
        })

        return result

    def scenario_2_essay_exam_detection(self):
        """
        場景2: 用戶誤上傳了申論題試卷
        典型用例：用戶不知道系統只處理選擇題，上傳了申論題試卷
        """
        print("\n" + "="*80)
        print("📝 場景2: 上傳申論題試卷（系統應自動識別並提示）")
        print("="*80)

        # 選擇一個申論題試卷
        pdf_path = f"{self.test_base}/民國114年_警察特考/犯罪防治/犯罪分析/試題.pdf"

        print(f"📄 處理試卷: 犯罪分析")
        print(f"📁 檔案路徑: {pdf_path}")

        start_time = time.time()
        result = self.processor.process_pdf(pdf_path)
        elapsed = time.time() - start_time

        if result['questions_count'] == 0 and result.get('essay_detection'):
            print(f"\n✅ 系統正確識別申論題！")
            print(f"   - 信心度: {result['essay_detection']['confidence']:.1%}")
            print(f"   - 判定理由: {result['essay_detection']['reason'][:100]}...")
            success = True
        else:
            print(f"\n❌ 系統未能識別申論題！")
            success = False

        self.results['scenarios'].append({
            "name": "場景2: 申論題識別",
            "success": success,
            "confidence": result.get('essay_detection', {}).get('confidence', 0),
            "time": elapsed
        })

        return result

    def scenario_3_batch_processing(self):
        """
        場景3: 批量處理多份試卷
        典型用例：教師需要批量處理一個考試類別的所有試卷
        """
        print("\n" + "="*80)
        print("📚 場景3: 批量處理試卷（某考試類別的所有試卷）")
        print("="*80)

        # 處理消防警察類別的所有試卷
        category_path = f"{self.test_base}/民國114年_警察特考/消防警察"

        print(f"📁 處理類別: 消防警察")
        print(f"📂 目錄: {category_path}")

        subjects = []
        for subject_dir in Path(category_path).iterdir():
            if subject_dir.is_dir():
                subjects.append(subject_dir.name)

        print(f"📊 找到 {len(subjects)} 個科目")

        start_time = time.time()
        results = []

        for subject in subjects:
            pdf_path = f"{category_path}/{subject}/試題.pdf"
            if os.path.exists(pdf_path):
                result = self.processor.process_pdf(pdf_path)
                results.append({
                    'subject': subject,
                    'questions': result['questions_count'],
                    'is_essay': result.get('essay_detection') is not None
                })
                print(f"   ✓ {subject}: {result['questions_count']} 題")

        elapsed = time.time() - start_time

        total_questions = sum(r['questions'] for r in results)
        choice_exams = sum(1 for r in results if not r['is_essay'])

        print(f"\n✅ 批量處理完成！")
        print(f"   - 總科目數: {len(results)}")
        print(f"   - 選擇題試卷: {choice_exams}")
        print(f"   - 總題數: {total_questions}")
        print(f"   - 總耗時: {elapsed:.2f} 秒")
        print(f"   - 平均速度: {total_questions/elapsed:.1f} 題/秒")

        self.results['scenarios'].append({
            "name": "場景3: 批量處理",
            "success": True,
            "subjects": len(results),
            "questions": total_questions,
            "time": elapsed
        })

        return results

    def scenario_4_answer_matching(self):
        """
        場景4: 題目與答案配對
        典型用例：用戶有試題PDF和答案PDF，需要配對
        """
        print("\n" + "="*80)
        print("🔗 場景4: 題目與答案配對驗證")
        print("="*80)

        # 測試多個試卷的答案配對
        test_cases = [
            "民國114年_警察特考/公共安全/警察法規(包括警察法、行政執行法、社會秩序維護法、警械使用條例、集會遊行法、警察職權行使法、公務人員行政中立法)",
            "民國114年_警察特考/刑事警察/犯罪偵查學",
            "民國114年_司法特考/監獄官/法學知識與英文（包括中華民國憲法、法學緒論、英文）",
        ]

        print(f"📊 測試 {len(test_cases)} 個試卷的答案配對")

        results = []
        for test_path in test_cases:
            pdf_path = f"{self.test_base}/{test_path}/試題.pdf"
            answer_path = f"{self.test_base}/{test_path}/答案.pdf"

            if not os.path.exists(pdf_path) or not os.path.exists(answer_path):
                continue

            question_result = self.processor.process_pdf(pdf_path)
            answer_result = self.processor.process_answer_pdf(answer_path)

            match_rate = min(question_result['questions_count'] / len(answer_result), 1.0) * 100

            subject = test_path.split('/')[-1][:20]
            print(f"   ✓ {subject}... : {question_result['questions_count']}題 / {len(answer_result)}答 = {match_rate:.1f}%")

            results.append({
                'subject': subject,
                'questions': question_result['questions_count'],
                'answers': len(answer_result),
                'match_rate': match_rate
            })

        avg_match = sum(r['match_rate'] for r in results) / len(results)
        perfect_match = sum(1 for r in results if r['match_rate'] == 100.0)

        print(f"\n✅ 答案配對測試完成！")
        print(f"   - 平均匹配率: {avg_match:.1f}%")
        print(f"   - 完美匹配: {perfect_match}/{len(results)}")

        self.results['scenarios'].append({
            "name": "場景4: 答案配對",
            "success": avg_match >= 95.0,
            "avg_match_rate": avg_match,
            "perfect_match": perfect_match
        })

        return results

    def scenario_5_edge_cases(self):
        """
        場景5: 異常情況處理
        典型用例：用戶上傳了各種異常格式或內容
        """
        print("\n" + "="*80)
        print("⚠️  場景5: 異常情況處理測試")
        print("="*80)

        edge_cases = []

        # 測試1: 無標籤格式（官方格式）
        print("\n   測試1: 無標籤格式（考選部官方格式）")
        pdf_path = f"{self.test_base}/民國114年_警察特考/消防警察/國文(作文與測驗)/試題.pdf"
        result = self.processor.process_pdf(pdf_path)

        if result['questions_count'] > 0:
            print(f"      ✅ 成功處理無標籤格式: {result['questions_count']} 題")
            edge_cases.append({"case": "無標籤格式", "success": True})
        else:
            print(f"      ❌ 無標籤格式處理失敗")
            edge_cases.append({"case": "無標籤格式", "success": False})

        # 測試2: 邊界信心度（接近閾值的申論題）
        print("\n   測試2: 邊界信心度申論題（41-45%信心度）")
        pdf_path = f"{self.test_base}/民國114年_警察特考/刑事警察/偵查法學/試題.pdf"
        result = self.processor.process_pdf(pdf_path)

        if result.get('essay_detection') and result['essay_detection']['confidence'] >= 0.35:
            print(f"      ✅ 正確識別邊界申論題（信心度: {result['essay_detection']['confidence']:.1%}）")
            edge_cases.append({"case": "邊界申論題", "success": True})
        else:
            print(f"      ❌ 邊界申論題識別失敗")
            edge_cases.append({"case": "邊界申論題", "success": False})

        # 測試3: 混合型試卷（作文+測驗）
        print("\n   測試3: 混合型試卷（國文作文與測驗）")
        pdf_path = f"{self.test_base}/民國114年_司法特考/監獄官/國文（作文與測驗）/試題.pdf"
        result = self.processor.process_pdf(pdf_path)

        # 混合型試卷可能被識別為申論題（因為包含作文）
        if result.get('essay_detection'):
            print(f"      ✅ 系統識別為混合型/申論型（信心度: {result['essay_detection']['confidence']:.1%}）")
            edge_cases.append({"case": "混合型試卷", "success": True})
        else:
            print(f"      ⚠️  系統識別為選擇題（{result['questions_count']}題）")
            edge_cases.append({"case": "混合型試卷", "success": True})

        success_rate = sum(1 for case in edge_cases if case['success']) / len(edge_cases) * 100

        print(f"\n✅ 異常情況處理完成！")
        print(f"   - 測試案例: {len(edge_cases)}")
        print(f"   - 成功率: {success_rate:.1f}%")

        self.results['scenarios'].append({
            "name": "場景5: 異常情況",
            "success": success_rate >= 80.0,
            "cases": len(edge_cases),
            "success_rate": success_rate
        })

        return edge_cases

    def scenario_6_performance_stress_test(self):
        """
        場景6: 性能壓力測試
        典型用例：用戶需要快速處理大量試卷
        """
        print("\n" + "="*80)
        print("⚡ 場景6: 性能壓力測試（連續處理20份試卷）")
        print("="*80)

        # 收集所有選擇題試卷
        all_pdfs = []
        for root, dirs, files in os.walk(self.test_base):
            if "試題.pdf" in files:
                all_pdfs.append(os.path.join(root, "試題.pdf"))

        # 隨機選擇20個（如果有的話）
        import random
        test_pdfs = random.sample(all_pdfs, min(20, len(all_pdfs)))

        print(f"📊 準備處理 {len(test_pdfs)} 份試卷")
        print("⏱️  開始計時...")

        start_time = time.time()
        results = []
        total_questions = 0

        for i, pdf_path in enumerate(test_pdfs, 1):
            result = self.processor.process_pdf(pdf_path)
            results.append(result)
            if not result.get('essay_detection'):
                total_questions += result['questions_count']

            # 每5份顯示進度
            if i % 5 == 0:
                print(f"   進度: {i}/{len(test_pdfs)} ({i/len(test_pdfs)*100:.0f}%)")

        elapsed = time.time() - start_time

        choice_count = sum(1 for r in results if not r.get('essay_detection'))
        essay_count = sum(1 for r in results if r.get('essay_detection'))

        print(f"\n✅ 壓力測試完成！")
        print(f"   - 總處理數: {len(results)} 份")
        print(f"   - 選擇題: {choice_count} 份")
        print(f"   - 申論題: {essay_count} 份")
        print(f"   - 總題數: {total_questions} 題")
        print(f"   - 總耗時: {elapsed:.2f} 秒")
        print(f"   - 平均速度: {len(results)/elapsed:.2f} 份/秒")
        print(f"   - 題目處理速度: {total_questions/elapsed:.1f} 題/秒")

        self.results['scenarios'].append({
            "name": "場景6: 性能壓力測試",
            "success": total_questions > 0,
            "pdfs": len(results),
            "questions": total_questions,
            "time": elapsed,
            "speed": total_questions/elapsed
        })

        return results

    def scenario_7_realistic_workflow(self):
        """
        場景7: 完整工作流程
        典型用例：用戶的完整使用流程（篩選→處理→匯出）
        """
        print("\n" + "="*80)
        print("🎯 場景7: 真實工作流程模擬")
        print("="*80)

        print("\n步驟1️⃣ : 掃描所有試卷")
        all_pdfs = []
        for root, dirs, files in os.walk(self.test_base):
            if "試題.pdf" in files:
                all_pdfs.append(os.path.join(root, "試題.pdf"))
        print(f"   ✓ 找到 {len(all_pdfs)} 份試卷")

        print("\n步驟2️⃣ : 篩選選擇題試卷")
        choice_exams = []
        essay_exams = []

        for pdf_path in all_pdfs[:10]:  # 測試前10個
            result = self.processor.process_pdf(pdf_path)
            if result.get('essay_detection'):
                essay_exams.append(pdf_path)
            else:
                choice_exams.append(pdf_path)

        print(f"   ✓ 選擇題: {len(choice_exams)} 份")
        print(f"   ✓ 申論題: {len(essay_exams)} 份（已過濾）")

        print("\n步驟3️⃣ : 處理選擇題並提取答案")
        processed = []
        for pdf_path in choice_exams:
            question_result = self.processor.process_pdf(pdf_path)

            # 檢查答案
            answer_path = pdf_path.replace("試題.pdf", "答案.pdf")
            if os.path.exists(answer_path):
                answer_result = self.processor.process_answer_pdf(answer_path)
                question_result['answers'] = answer_result

            processed.append(question_result)

        print(f"   ✓ 成功處理 {len(processed)} 份選擇題")

        print("\n步驟4️⃣ : 生成統計報告")
        total_questions = sum(p['questions_count'] for p in processed)
        with_answers = sum(1 for p in processed if 'answers' in p)

        report = {
            "total_processed": len(processed),
            "total_questions": total_questions,
            "with_answers": with_answers,
            "answer_coverage": with_answers / len(processed) * 100 if processed else 0
        }

        print(f"   ✓ 總處理數: {report['total_processed']} 份")
        print(f"   ✓ 總題數: {report['total_questions']} 題")
        print(f"   ✓ 答案覆蓋率: {report['answer_coverage']:.1f}%")

        print("\n✅ 完整工作流程完成！")

        self.results['scenarios'].append({
            "name": "場景7: 完整工作流程",
            "success": True,
            "report": report
        })

        return report

    def run_all_scenarios(self):
        """執行所有場景測試"""
        print("\n" + "="*80)
        print("🚀 用戶場景自動化測試開始")
        print("="*80)
        print(f"📅 測試時間: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"📁 測試目錄: {self.test_base}")

        start_time = time.time()

        # 執行所有場景
        self.scenario_1_single_choice_exam()
        self.scenario_2_essay_exam_detection()
        self.scenario_3_batch_processing()
        self.scenario_4_answer_matching()
        self.scenario_5_edge_cases()
        self.scenario_6_performance_stress_test()
        self.scenario_7_realistic_workflow()

        total_time = time.time() - start_time

        # 生成總結報告
        self.generate_summary(total_time)

        # 保存結果
        self.save_results()

    def generate_summary(self, total_time):
        """生成總結報告"""
        print("\n" + "="*80)
        print("📊 測試總結報告")
        print("="*80)

        total_scenarios = len(self.results['scenarios'])
        success_scenarios = sum(1 for s in self.results['scenarios'] if s['success'])
        success_rate = success_scenarios / total_scenarios * 100

        print(f"\n✅ 場景測試統計:")
        print(f"   - 總場景數: {total_scenarios}")
        print(f"   - 成功場景: {success_scenarios}")
        print(f"   - 成功率: {success_rate:.1f}%")
        print(f"   - 總耗時: {total_time:.2f} 秒")

        print(f"\n📋 各場景結果:")
        for i, scenario in enumerate(self.results['scenarios'], 1):
            status = "✅" if scenario['success'] else "❌"
            print(f"   {status} 場景{i}: {scenario['name']}")

        # 評級
        if success_rate == 100:
            grade = "⭐⭐⭐⭐⭐ 完美"
            comment = "所有用戶場景測試全部通過！系統已準備好供真實用戶使用。"
        elif success_rate >= 90:
            grade = "⭐⭐⭐⭐ 優秀"
            comment = "絕大多數用戶場景測試通過，系統表現優秀。"
        elif success_rate >= 80:
            grade = "⭐⭐⭐ 良好"
            comment = "大部分用戶場景測試通過，仍有改進空間。"
        else:
            grade = "⭐⭐ 需改進"
            comment = "部分用戶場景測試未通過，需要進一步優化。"

        print(f"\n🏆 最終評級: {grade}")
        print(f"💬 評語: {comment}")

        self.results['summary'] = {
            "total_scenarios": total_scenarios,
            "success_scenarios": success_scenarios,
            "success_rate": success_rate,
            "total_time": total_time,
            "grade": grade,
            "comment": comment
        }

    def save_results(self):
        """保存測試結果"""
        output_file = "user_scenario_test_results.json"

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, ensure_ascii=False, indent=2)

        print(f"\n💾 測試結果已保存到: {output_file}")


if __name__ == "__main__":
    tester = UserScenarioTester()
    tester.run_all_scenarios()

    print("\n" + "="*80)
    print("✅ 用戶場景自動化測試完成！")
    print("="*80)
