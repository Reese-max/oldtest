#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
優化版題組處理器 - 大幅提升題組檢測和選項提取的準確性
"""

import os
import pdfplumber
import pandas as pd
import re
import json
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

class QuestionType(Enum):
    """題目類型枚舉"""
    REGULAR = "regular"
    GROUP = "group"
    MULTIPLE_CHOICE = "multiple_choice"
    TRUE_FALSE = "true_false"

@dataclass
class QuestionGroup:
    """題組資料結構"""
    start_question: int
    end_question: int
    content: str
    question_count: int
    group_id: str
    context_type: str = "passage"  # passage, article, text, etc.

class OptimizedQuestionGroupProcessor:
    """優化版題組處理器"""
    
    def __init__(self):
        # 題組檢測模式 - 更全面的匹配
        self.group_patterns = [
            # 標準格式
            r'請依下文回答第(\d+)題至第(\d+)題[：:]?',
            r'請依上文回答第(\d+)題至第(\d+)題[：:]?',
            r'請根據下列文章回答第(\d+)題至第(\d+)題[：:]?',
            r'請根據下列短文回答第(\d+)題至第(\d+)題[：:]?',
            r'請根據下列內容回答第(\d+)題至第(\d+)題[：:]?',
            r'閱讀下文，回答第(\d+)題至第(\d+)題[：:]?',
            r'閱讀下列文章，回答第(\d+)題至第(\d+)題[：:]?',
            
            # 變體格式
            r'依下文回答第(\d+)題至第(\d+)題[：:]?',
            r'依上文回答第(\d+)題至第(\d+)題[：:]?',
            r'根據下文回答第(\d+)題至第(\d+)題[：:]?',
            r'根據上文回答第(\d+)題至第(\d+)題[：:]?',
            
            # 英文格式
            r'Based on the following passage, answer questions (\d+) to (\d+)[：:]?',
            r'Read the following text and answer questions (\d+) to (\d+)[：:]?',
        ]
        
        # 選項檢測模式 - 支援多種格式
        self.option_patterns = [
            # 中文選項格式
            r'[（(]?[ＡＢＣＤ][）)]?\s*([^ＡＢＣＤ\n]+?)(?=[（(]?[ＢＣＤＥ][）)]?|$)',
            r'[（(]?[ABCD][）)]?\s*([^ABCD\n]+?)(?=[（(]?[BCDE][）)]?|$)',
            
            # 數字選項格式
            r'[（(]?[1-4][）)]?\s*([^1-4\n]+?)(?=[（(]?[2-5][）)]?|$)',
            
            # 簡單格式
            r'[ＡＢＣＤ]\s*([^ＡＢＣＤ\n]+?)(?=[ＡＢＣＤ]|$)',
            r'[ABCD]\s*([^ABCD\n]+?)(?=[ABCD]|$)',
        ]
        
        # 題目檢測模式
        self.question_patterns = [
            # 標準題號格式
            r'第(\d+)題[：:]?\s*(.*?)(?=第\d+題|$)',
            r'(\d+)\.\s*(.*?)(?=\d+\.|$)',
            r'^(\d+)\s+(.*?)(?=^\d+\s+|$)',
            
            # 題組內題目格式
            r'(\d+)\s*[：:]?\s*([^ＡＢＣＤ\n]*?)(?=[ＡＢＣＤ]|$)',
        ]
    
    def detect_question_groups(self, text: str) -> List[QuestionGroup]:
        """檢測題組 - 優化版算法"""
        groups = []
        
        print(f"🔍 開始檢測題組，文字長度: {len(text)} 字元")
        
        for pattern in self.group_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                try:
                    start_q = int(match.group(1))
                    end_q = int(match.group(2))
                    
                    # 驗證題號範圍
                    if start_q > end_q or start_q < 1 or end_q > 1000:
                        continue
                    
                    # 計算題組內容範圍
                    start_pos = match.end()
                    group_content = self._extract_group_content(text, start_pos, pattern)
                    
                    if not group_content or len(group_content.strip()) < 50:
                        continue
                    
                    # 生成題組ID
                    group_id = f"group_{start_q}_{end_q}_{hash(group_content) % 10000}"
                    
                    # 判斷上下文類型
                    context_type = self._determine_context_type(match.group(0))
                    
                    group = QuestionGroup(
                        start_question=start_q,
                        end_question=end_q,
                        content=group_content,
                        question_count=end_q - start_q + 1,
                        group_id=group_id,
                        context_type=context_type
                    )
                    
                    groups.append(group)
                    print(f"   ✅ 檢測到題組 {start_q}-{end_q}: {group.question_count} 題")
                    
                except (ValueError, IndexError) as e:
                    print(f"   ⚠️ 題組解析錯誤: {e}")
                    continue
        
        # 去重複題組
        unique_groups = self._remove_duplicate_groups(groups)
        
        print(f"📊 檢測完成，共找到 {len(unique_groups)} 個題組")
        return unique_groups
    
    def _extract_group_content(self, text: str, start_pos: int, pattern: str) -> str:
        """提取題組內容"""
        # 尋找下一個題組開始位置
        next_group_patterns = [
            r'請依.*?回答第\d+題至第\d+題',
            r'請根據.*?回答第\d+題至第\d+題',
            r'閱讀.*?回答第\d+題至第\d+題',
            r'Based on.*?answer questions \d+ to \d+',
        ]
        
        end_pos = len(text)
        for next_pattern in next_group_patterns:
            next_match = re.search(next_pattern, text[start_pos:], re.IGNORECASE)
            if next_match:
                end_pos = start_pos + next_match.start()
                break
        
        content = text[start_pos:end_pos].strip()
        
        # 清理內容
        content = self._clean_group_content(content)
        
        return content
    
    def _clean_group_content(self, content: str) -> str:
        """清理題組內容"""
        # 移除多餘的空白和換行
        content = re.sub(r'\n\s*\n', '\n', content)
        content = re.sub(r' +', ' ', content)
        
        # 移除頁碼和無關內容
        content = re.sub(r'第\s*\d+\s*頁', '', content)
        content = re.sub(r'Page\s*\d+', '', content)
        
        return content.strip()
    
    def _determine_context_type(self, match_text: str) -> str:
        """判斷上下文類型"""
        if '文章' in match_text or 'article' in match_text.lower():
            return 'article'
        elif '短文' in match_text or 'passage' in match_text.lower():
            return 'passage'
        elif '內容' in match_text or 'content' in match_text.lower():
            return 'content'
        else:
            return 'text'
    
    def _remove_duplicate_groups(self, groups: List[QuestionGroup]) -> List[QuestionGroup]:
        """移除重複的題組"""
        unique_groups = []
        seen_ranges = set()
        
        for group in groups:
            range_key = (group.start_question, group.end_question)
            if range_key not in seen_ranges:
                unique_groups.append(group)
                seen_ranges.add(range_key)
        
        return unique_groups
    
    def extract_questions_from_group(self, group: QuestionGroup) -> List[Dict[str, Any]]:
        """從題組中提取個別題目 - 優化版"""
        questions = []
        group_content = group.content
        
        print(f"   🔍 處理題組 {group.start_question}-{group.end_question}，內容長度: {len(group_content)} 字元")
        
        for q_num in range(group.start_question, group.end_question + 1):
            question_data = self._extract_single_question_from_group(
                q_num, group_content, group
            )
            questions.append(question_data)
        
        return questions
    
    def _extract_single_question_from_group(self, q_num: int, group_content: str, group: QuestionGroup) -> Dict[str, Any]:
        """從題組中提取單一題目"""
        # 尋找題目內容
        question_text = self._find_question_text(q_num, group_content)
        
        # 提取選項
        options = self._extract_options_from_text(question_text or group_content)
        
        # 建立題目資料
        question_data = {
            '題號': str(q_num),
            '題目': question_text or f"題組題目（第{q_num}題）",
            '選項A': options.get('A', ''),
            '選項B': options.get('B', ''),
            '選項C': options.get('C', ''),
            '選項D': options.get('D', ''),
            '題型': '選擇題',
            '正確答案': '',
            '更正答案': '',
            '題組': True,
            '題組編號': f"{group.start_question}-{group.end_question}",
            '題組ID': group.group_id,
            '題組內容': group_content[:300] + '...' if len(group_content) > 300 else group_content,
            '上下文類型': group.context_type,
            '原始題目': question_text or ''
        }
        
        return question_data
    
    def _find_question_text(self, q_num: int, group_content: str) -> Optional[str]:
        """尋找題目文字"""
        # 嘗試多種題目模式
        for pattern in self.question_patterns:
            # 修改模式以匹配題組中的題目
            if '第' in pattern:
                modified_pattern = pattern.replace('第(\\d+)題', f'第{q_num}題')
            else:
                modified_pattern = pattern.replace('(\\d+)', str(q_num))
            
            match = re.search(modified_pattern, group_content, re.DOTALL | re.IGNORECASE)
            if match:
                question_text = match.group(-1).strip()  # 取最後一個分組
                if len(question_text) > 10:  # 確保有足夠的內容
                    return question_text
        
        return None
    
    def _extract_options_from_text(self, text: str) -> Dict[str, str]:
        """從文字中提取選項 - 優化版算法"""
        options = {}
        
        if not text:
            return options
        
        # 嘗試多種選項模式
        for pattern in self.option_patterns:
            matches = re.findall(pattern, text, re.DOTALL | re.IGNORECASE)
            
            if len(matches) >= 2:  # 至少要有2個選項
                option_letters = ['A', 'B', 'C', 'D']
                
                for i, match in enumerate(matches[:4]):  # 最多4個選項
                    if i < len(option_letters):
                        option_content = match.strip()
                        if len(option_content) > 2:  # 選項內容要有一定長度
                            options[option_letters[i]] = option_content
                
                if len(options) >= 2:  # 如果找到足夠的選項就停止
                    break
        
        # 如果沒有找到選項，嘗試更簡單的方法
        if not options:
            options = self._extract_options_simple(text)
        
        return options
    
    def _extract_options_simple(self, text: str) -> Dict[str, str]:
        """簡單的選項提取方法"""
        options = {}
        
        # 按行分割文字
        lines = text.split('\n')
        option_letters = ['A', 'B', 'C', 'D']
        option_index = 0
        
        for line in lines:
            line = line.strip()
            if not line or len(line) < 3:
                continue
            
            # 跳過題目行（包含問號）
            if '？' in line or '?' in line:
                continue
            
            # 檢查是否像選項
            if self._looks_like_option(line):
                if option_index < len(option_letters):
                    options[option_letters[option_index]] = line
                    option_index += 1
                
                if option_index >= 4:  # 最多4個選項
                    break
        
        return options
    
    def _looks_like_option(self, text: str) -> bool:
        """判斷文字是否像選項"""
        # 長度檢查
        if len(text) < 3 or len(text) > 200:
            return False
        
        # 排除明顯不是選項的內容
        exclude_patterns = [
            r'^第\d+題',
            r'^題目',
            r'^答案',
            r'^說明',
            r'^注意',
            r'^\d+\.\s*$',  # 只有數字和點
        ]
        
        for pattern in exclude_patterns:
            if re.match(pattern, text):
                return False
        
        return True
    
    def process_pdf_with_optimized_groups(self, pdf_path: str, output_dir: str = "", 
                                        answer_pdf_path: str = "") -> Tuple[List[str], Dict[str, Any]]:
        """使用優化版處理器處理PDF"""
        
        print(f"\n{'='*70}")
        print(f"📄 {os.path.basename(pdf_path)} (優化版題組處理)")
        print(f"{'='*70}")
        
        try:
            # 提取PDF文字
            with pdfplumber.open(pdf_path) as pdf:
                text = ""
                for page in pdf.pages:
                    text += page.extract_text() or ""
            
            print(f"📊 提取文字長度: {len(text)} 字元")
            
            # 檢測題組
            groups = self.detect_question_groups(text)
            
            questions = []
            
            if groups:
                # 處理題組
                for group in groups:
                    print(f"   📚 題組 {group.start_question}-{group.end_question}: {group.question_count} 題")
                    group_questions = self.extract_questions_from_group(group)
                    questions.extend(group_questions)
            
            if not questions:
                print("❌ 未找到任何題目")
                return [], {}
            
            print(f"✅ 解析出 {len(questions)} 題")
            
            # 儲存CSV
            os.makedirs(output_dir, exist_ok=True)
            base = os.path.splitext(os.path.basename(pdf_path))[0]
            
            # 分類題目
            regular_questions = [q for q in questions if not q.get('題組', False)]
            group_questions = [q for q in questions if q.get('題組', False)]
            
            saved_files = []
            
            if regular_questions:
                path = os.path.join(output_dir, f"{base}_一般題目.csv")
                pd.DataFrame(regular_questions).to_csv(path, index=False, encoding='utf-8-sig')
                print(f"✅ {path} ({len(regular_questions)}題)")
                saved_files.append(path)
            
            if group_questions:
                path = os.path.join(output_dir, f"{base}_題組題目.csv")
                pd.DataFrame(group_questions).to_csv(path, index=False, encoding='utf-8-sig')
                print(f"✅ {path} ({len(group_questions)}題)")
                saved_files.append(path)
            
            # 合併所有題目
            if questions:
                path = os.path.join(output_dir, f"{base}_完整題目.csv")
                pd.DataFrame(questions).to_csv(path, index=False, encoding='utf-8-sig')
                print(f"✅ {path} ({len(questions)}題)")
                saved_files.append(path)
            
            # 生成統計報告
            stats = {
                'total_questions': len(questions),
                'group_questions': len(group_questions),
                'regular_questions': len(regular_questions),
                'question_groups': len(groups),
                'success_rate': len(questions) / max(1, len(groups) * 5) if groups else 0
            }
            
            return saved_files, stats
            
        except Exception as e:
            print(f"❌ 處理失敗: {e}")
            import traceback
            traceback.print_exc()
            return [], {}

def main():
    """主函數"""
    import argparse
    
    parser = argparse.ArgumentParser(description='優化版PDF轉CSV工具 - 強化題組處理')
    parser.add_argument('input', help='輸入PDF檔案')
    parser.add_argument('-o', '--output', default='test_output', help='輸出目錄')
    parser.add_argument('--answer', default='', help='答案PDF檔案路徑')
    
    args = parser.parse_args()
    
    if os.path.isfile(args.input):
        processor = OptimizedQuestionGroupProcessor()
        saved_files, stats = processor.process_pdf_with_optimized_groups(args.input, args.output, args.answer)
        
        if saved_files:
            print(f"\n✅ 已儲存: {saved_files}")
            print(f"📊 統計: {stats}")
        else:
            print("\n❌ 處理失敗")
    else:
        print("❌ 輸入檔案不存在")

if __name__ == "__main__":
    main()