#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
真實數據端到端測試
使用考選部真實考古題測試完整流程
"""

import os
import sys
sys.path.insert(0, '/home/user/oldtest')

from src.api import ArchaeologyAPI

def test_real_exam_data():
    """使用真實考古題數據測試完整流程"""

    print("\n" + "="*80)
    print("🧪 真實數據端到端測試")
    print("="*80)
    print("測試範圍: PDF提取 → 題目解析 → 答案處理 → CSV生成 → Google Apps Script")
    print("="*80)

    # 測試數據路徑
    base_path = "考選部考古題完整庫/民國114年/民國114年_司法特考/監獄官"
    test_cases = [
        {
            "name": "法學知識與英文",
            "path": f"{base_path}/法學知識與英文（包括中華民國憲法、法學緒論、英文）",
            "exam_pdf": "試題.pdf",
            "answer_pdf": "答案.pdf"
        },
    ]

    # 輸出目錄
    output_dir = "test_output_real_data"
    os.makedirs(output_dir, exist_ok=True)

    # 創建API實例
    api = ArchaeologyAPI()

    results = []

    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{'='*80}")
        print(f"測試案例 {i}: {test_case['name']}")
        print(f"{'='*80}")

        exam_path = os.path.join(test_case['path'], test_case['exam_pdf'])
        answer_path = os.path.join(test_case['path'], test_case['answer_pdf'])

        # 檢查文件是否存在
        if not os.path.exists(exam_path):
            print(f"❌ 試題文件不存在: {exam_path}")
            results.append({"name": test_case['name'], "success": False, "error": "試題文件不存在"})
            continue

        if not os.path.exists(answer_path):
            print(f"⚠️  答案文件不存在: {answer_path}")
            answer_path = None

        print(f"\n📄 試題文件: {exam_path}")
        if answer_path:
            print(f"📄 答案文件: {answer_path}")
        else:
            print(f"⚠️  答案文件: 無")

        print(f"\n開始處理...")

        try:
            # 處理PDF
            result = api.process_single_pdf(
                pdf_path=exam_path,
                answer_pdf_path=answer_path,
                output_dir=output_dir,
                generate_script=True
            )

            if result.get('success'):
                print(f"\n✅ 處理成功！")
                print(f"\n📊 處理結果:")
                print(f"   ├─ 題目數量: {result.get('questions_count', 0)} 題")
                print(f"   ├─ 答案數量: {result.get('answers_count', 0)} 個")
                print(f"   ├─ 更正答案: {result.get('corrected_answers_count', 0)} 個")
                print(f"   └─ CSV文件: {len(result.get('csv_files', []))} 個")

                # 顯示生成的文件
                print(f"\n📁 生成的文件:")
                for csv_file in result.get('csv_files', []):
                    file_size = os.path.getsize(csv_file) if os.path.exists(csv_file) else 0
                    print(f"   ├─ {os.path.basename(csv_file)} ({file_size} bytes)")

                if result.get('script_file'):
                    script_size = os.path.getsize(result['script_file']) if os.path.exists(result['script_file']) else 0
                    print(f"   └─ {os.path.basename(result['script_file'])} ({script_size} bytes)")

                # 顯示統計信息
                if 'statistics' in result:
                    stats = result['statistics']
                    print(f"\n📈 統計信息:")
                    print(f"   ├─ 一般題目: {stats.get('regular_questions', 0)} 題")
                    print(f"   ├─ 題組題目: {stats.get('group_questions', 0)} 題")
                    print(f"   └─ 題組數量: {stats.get('question_groups', 0)} 組")

                    if 'answer_statistics' in stats:
                        ans_stats = stats['answer_statistics']
                        print(f"\n   答案分布:")
                        for opt in ['A', 'B', 'C', 'D']:
                            print(f"   ├─ {opt}: {ans_stats.get(opt, 0)} 題")
                        if ans_stats.get('無效', 0) > 0:
                            print(f"   └─ 無效: {ans_stats.get('無效', 0)} 題")

                # 顯示前3題預覽
                if result.get('questions_count', 0) > 0:
                    print(f"\n📝 題目預覽 (前3題):")
                    # 讀取CSV文件查看內容
                    csv_files = result.get('csv_files', [])
                    if csv_files:
                        try:
                            import pandas as pd
                            df = pd.read_csv(csv_files[0], encoding='utf-8-sig')
                            for idx, row in df.head(3).iterrows():
                                print(f"\n   題 {idx+1}:")
                                print(f"   題號: {row.get('題號', 'N/A')}")
                                print(f"   題目: {str(row.get('題目', ''))[:60]}...")
                                print(f"   答案: {row.get('正確答案', 'N/A')}")
                        except Exception as e:
                            print(f"   ⚠️  無法讀取CSV預覽: {e}")

                results.append({
                    "name": test_case['name'],
                    "success": True,
                    "questions": result.get('questions_count', 0),
                    "answers": result.get('answers_count', 0),
                    "files": len(result.get('csv_files', [])) + (1 if result.get('script_file') else 0)
                })
            else:
                error_msg = result.get('message', '未知錯誤')
                print(f"\n❌ 處理失敗: {error_msg}")
                results.append({
                    "name": test_case['name'],
                    "success": False,
                    "error": error_msg
                })

        except Exception as e:
            print(f"\n❌ 發生異常: {e}")
            import traceback
            traceback.print_exc()
            results.append({
                "name": test_case['name'],
                "success": False,
                "error": str(e)
            })

    # 總結報告
    print(f"\n{'='*80}")
    print("📊 測試總結")
    print(f"{'='*80}")

    success_count = sum(1 for r in results if r.get('success', False))
    total_count = len(results)

    print(f"\n測試案例: {total_count} 個")
    print(f"成功: {success_count} 個")
    print(f"失敗: {total_count - success_count} 個")
    print(f"成功率: {success_count/total_count*100:.1f}%")

    print(f"\n詳細結果:")
    for r in results:
        status = "✅ PASS" if r.get('success', False) else "❌ FAIL"
        print(f"\n{status}: {r['name']}")
        if r.get('success'):
            print(f"   ├─ 題目數: {r.get('questions', 0)}")
            print(f"   ├─ 答案數: {r.get('answers', 0)}")
            print(f"   └─ 文件數: {r.get('files', 0)}")
        else:
            print(f"   └─ 錯誤: {r.get('error', '未知')}")

    # 檢查輸出文件
    print(f"\n{'='*80}")
    print("📁 輸出目錄內容")
    print(f"{'='*80}")

    if os.path.exists(output_dir):
        files = os.listdir(output_dir)
        if files:
            print(f"\n生成的文件 ({len(files)} 個):")
            for f in sorted(files):
                file_path = os.path.join(output_dir, f)
                file_size = os.path.getsize(file_path)
                print(f"   ├─ {f} ({file_size:,} bytes)")
        else:
            print(f"\n⚠️  輸出目錄為空")
    else:
        print(f"\n⚠️  輸出目錄不存在")

    # 最終評估
    print(f"\n{'='*80}")
    print("✅ 最終評估")
    print(f"{'='*80}")

    if success_count == total_count:
        print(f"\n🎉 所有測試案例通過！")
        print(f"✅ 系統能正確處理真實考古題數據")
        print(f"✅ 完整流程運作正常")
        return 0
    elif success_count > 0:
        print(f"\n⚠️  部分測試案例通過 ({success_count}/{total_count})")
        print(f"建議檢查失敗的案例")
        return 1
    else:
        print(f"\n❌ 所有測試案例失敗")
        print(f"請檢查系統配置和PDF文件")
        return 1

if __name__ == '__main__':
    exit(test_real_exam_data())
