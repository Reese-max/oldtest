#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
增強版題組處理器 - 優化題組選取和功能強化
提供更精確的題組檢測、選項提取和題目解析功能
"""

import os
import pdfplumber
import pandas as pd
import re
import json
from typing import List, Dict, Any, Optional, Tuple, Set
from datetime import datetime
import logging

class EnhancedQuestionGroupProcessor:
    """增強版題組處理器"""
    
    def __init__(self):
        self.logger = self._setup_logger()
        self.question_group_patterns = self._init_question_group_patterns()
        self.option_patterns = self._init_option_patterns()
        self.question_patterns = self._init_question_patterns()
        
    def _setup_logger(self) -> logging.Logger:
        """設置日誌記錄器"""
        logger = logging.getLogger('EnhancedQuestionGroupProcessor')
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def _init_question_group_patterns(self) -> List[Dict[str, Any]]:
        """初始化題組檢測模式"""
        return [
            {
                'pattern': r'請依下文回答第(\d+)題至第(\d+)題：?',
                'type': 'standard',
                'description': '標準題組格式'
            },
            {
                'pattern': r'請依上文回答第(\d+)題至第(\d+)題：?',
                'type': 'standard',
                'description': '上文題組格式'
            },
            {
                'pattern': r'請依下列文章回答第(\d+)題至第(\d+)題：?',
                'type': 'article',
                'description': '文章題組格式'
            },
            {
                'pattern': r'請依下列短文回答第(\d+)題至第(\d+)題：?',
                'type': 'short_article',
                'description': '短文題組格式'
            },
            {
                'pattern': r'請依下列內容回答第(\d+)題至第(\d+)題：?',
                'type': 'content',
                'description': '內容題組格式'
            },
            {
                'pattern': r'閱讀下文，回答第(\d+)題至第(\d+)題：?',
                'type': 'reading',
                'description': '閱讀題組格式'
            },
            {
                'pattern': r'根據下列文章，回答第(\d+)題至第(\d+)題：?',
                'type': 'article_based',
                'description': '基於文章的題組格式'
            },
            {
                'pattern': r'請根據下文回答第(\d+)題至第(\d+)題：?',
                'type': 'based_on_text',
                'description': '基於下文的題組格式'
            }
        ]
    
    def _init_option_patterns(self) -> List[Dict[str, Any]]:
        """初始化選項檢測模式"""
        return [
            {
                'pattern': r'[（(]A[）)]\s*(.*?)(?=[（(]B[）)]|$)',
                'type': 'parentheses',
                'description': '括號格式選項'
            },
            {
                'pattern': r'[（(]B[）)]\s*(.*?)(?=[（(]C[）)]|$)',
                'type': 'parentheses',
                'description': '括號格式選項'
            },
            {
                'pattern': r'[（(]C[）)]\s*(.*?)(?=[（(]D[）)]|$)',
                'type': 'parentheses',
                'description': '括號格式選項'
            },
            {
                'pattern': r'[（(]D[）)]\s*(.*?)(?=[（(]E[）)]|$)',
                'type': 'parentheses',
                'description': '括號格式選項'
            },
            {
                'pattern': r'[ＡＢＣＤ]\s*(.*?)(?=[ＡＢＣＤ]|$)',
                'type': 'full_width',
                'description': '全形選項格式'
            },
            {
                'pattern': r'[ABCD]\s*(.*?)(?=[ABCD]|$)',
                'type': 'half_width',
                'description': '半形選項格式'
            }
        ]
    
    def _init_question_patterns(self) -> List[Dict[str, Any]]:
        """初始化題目檢測模式"""
        return [
            {
                'pattern': r'第(\d+)題[：:]?\s*(.*?)(?=第\d+題|$)',
                'type': 'numbered',
                'description': '編號題目格式'
            },
            {
                'pattern': r'(\d+)\.\s*(.*?)(?=\d+\.|$)',
                'type': 'dot_numbered',
                'description': '點號編號格式'
            },
            {
                'pattern': r'^(\d+)\s+(.*?)(?=^\d+\s+|$)',
                'type': 'space_numbered',
                'description': '空格編號格式'
            }
        ]
    
    def detect_question_groups(self, text: str) -> List[Dict[str, Any]]:
        """
        檢測題組 - 增強版算法
        
        Args:
            text: 要分析的文字內容
            
        Returns:
            檢測到的題組列表
        """
        self.logger.info("開始檢測題組")
        
        groups = []
        processed_positions = set()  # 避免重複處理
        
        for pattern_info in self.question_group_patterns:
            pattern = pattern_info['pattern']
            pattern_type = pattern_info['type']
            
            try:
                matches = re.finditer(pattern, text, re.MULTILINE | re.DOTALL)
                
                for match in matches:
                    start_pos = match.start()
                    end_pos = match.end()
                    
                    # 避免重複處理相同位置
                    if any(start_pos <= pos <= end_pos for pos in processed_positions):
                        continue
                    
                    try:
                        start_q = int(match.group(1))
                        end_q = int(match.group(2))
                        
                        # 驗證題號範圍的合理性
                        if not self._validate_question_range(start_q, end_q):
                            self.logger.warning(f"題號範圍不合理: {start_q}-{end_q}")
                            continue
                        
                        # 提取題組內容
                        group_content = self._extract_group_content(text, match, start_q, end_q)
                        
                        if not group_content or len(group_content.strip()) < 50:
                            self.logger.warning(f"題組內容過短: {len(group_content)} 字元")
                            continue
                        
                        group = {
                            'start_question': start_q,
                            'end_question': end_q,
                            'content': group_content,
                            'question_count': end_q - start_q + 1,
                            'pattern_type': pattern_type,
                            'pattern_description': pattern_info['description'],
                            'start_position': start_pos,
                            'end_position': end_pos,
                            'content_length': len(group_content),
                            'detection_confidence': self._calculate_detection_confidence(group_content, start_q, end_q)
                        }
                        
                        groups.append(group)
                        processed_positions.update(range(start_pos, end_pos))
                        
                        self.logger.info(f"檢測到題組 {start_q}-{end_q}: {group['question_count']} 題, 信心度: {group['detection_confidence']:.2f}")
                        
                    except (ValueError, IndexError) as e:
                        self.logger.warning(f"解析題組失敗: {e}")
                        continue
                        
            except re.error as e:
                self.logger.error(f"正則表達式錯誤: {pattern} - {e}")
                continue
        
        # 按題號排序
        groups.sort(key=lambda x: x['start_question'])
        
        # 合併重疊的題組
        merged_groups = self._merge_overlapping_groups(groups)
        
        self.logger.info(f"題組檢測完成: 原始 {len(groups)} 個, 合併後 {len(merged_groups)} 個")
        
        return merged_groups
    
    def _validate_question_range(self, start_q: int, end_q: int) -> bool:
        """驗證題號範圍的合理性"""
        if start_q <= 0 or end_q <= 0:
            return False
        if start_q > end_q:
            return False
        if end_q - start_q > 20:  # 題組不應超過20題
            return False
        return True
    
    def _extract_group_content(self, text: str, match: re.Match, start_q: int, end_q: int) -> str:
        """提取題組內容"""
        start_pos = match.end()
        
        # 尋找下一個題組或文檔結束
        next_group_patterns = [
            r'請依.*?回答第\d+題至第\d+題',
            r'請根據.*?回答第\d+題至第\d+題',
            r'閱讀.*?回答第\d+題至第\d+題',
            r'根據.*?回答第\d+題至第\d+題'
        ]
        
        next_match = None
        for pattern in next_group_patterns:
            next_match = re.search(pattern, text[start_pos:])
            if next_match:
                break
        
        if next_match:
            end_pos = start_pos + next_match.start()
        else:
            # 尋找可能的結束標記
            end_markers = [
                r'第\d+題\s*[：:]?\s*[ＡＢＣＤ]',  # 下一題開始
                r'\n\d+\s+[ＡＢＣＤ]',  # 下一題開始
                r'答案：',  # 答案開始
                r'解答：',  # 解答開始
            ]
            
            for marker in end_markers:
                marker_match = re.search(marker, text[start_pos:])
                if marker_match:
                    end_pos = start_pos + marker_match.start()
                    break
            else:
                end_pos = len(text)
        
        content = text[start_pos:end_pos].strip()
        
        # 清理內容
        content = self._clean_group_content(content)
        
        return content
    
    def _clean_group_content(self, content: str) -> str:
        """清理題組內容"""
        # 移除多餘的空白行
        content = re.sub(r'\n\s*\n', '\n', content)
        
        # 移除頁碼
        content = re.sub(r'第\s*\d+\s*頁', '', content)
        
        # 移除頁次標記
        content = re.sub(r'頁次：\s*\d+', '', content)
        
        return content.strip()
    
    def _calculate_detection_confidence(self, content: str, start_q: int, end_q: int) -> float:
        """計算檢測信心度"""
        confidence = 0.0
        
        # 內容長度因子
        if len(content) > 100:
            confidence += 0.2
        if len(content) > 500:
            confidence += 0.2
        
        # 題目數量因子
        expected_questions = end_q - start_q + 1
        if 2 <= expected_questions <= 10:
            confidence += 0.2
        
        # 選項檢測因子
        option_count = len(re.findall(r'[ＡＢＣＤ]', content))
        if option_count >= expected_questions * 4:
            confidence += 0.3
        
        # 題號檢測因子
        question_numbers = re.findall(rf'第?{start_q}|第?{start_q+1}|第?{end_q}', content)
        if len(question_numbers) >= expected_questions:
            confidence += 0.3
        
        return min(confidence, 1.0)
    
    def _merge_overlapping_groups(self, groups: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """合併重疊的題組"""
        if not groups:
            return groups
        
        merged = []
        current_group = groups[0]
        
        for group in groups[1:]:
            # 檢查是否重疊
            if (group['start_question'] <= current_group['end_question'] and 
                group['end_question'] >= current_group['start_question']):
                
                # 合併題組
                current_group['end_question'] = max(current_group['end_question'], group['end_question'])
                current_group['question_count'] = current_group['end_question'] - current_group['start_question'] + 1
                current_group['content'] = current_group['content'] + '\n\n' + group['content']
                current_group['content_length'] = len(current_group['content'])
                current_group['detection_confidence'] = max(current_group['detection_confidence'], group['detection_confidence'])
                
                self.logger.info(f"合併重疊題組: {current_group['start_question']}-{current_group['end_question']}")
            else:
                merged.append(current_group)
                current_group = group
        
        merged.append(current_group)
        return merged
    
    def extract_questions_from_group(self, group: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        從題組中提取個別題目 - 增強版算法
        
        Args:
            group: 題組資料
            
        Returns:
            提取的題目列表
        """
        self.logger.info(f"開始提取題組 {group['start_question']}-{group['end_question']} 的題目")
        
        questions = []
        start_q = group['start_question']
        end_q = group['end_question']
        group_content = group['content']
        
        for q_num in range(start_q, end_q + 1):
            try:
                question = self._extract_single_question(group_content, q_num, group)
                if question:
                    questions.append(question)
                    self.logger.debug(f"成功提取題目 {q_num}")
                else:
                    self.logger.warning(f"未能提取題目 {q_num}")
                    # 創建基本題目結構
                    questions.append(self._create_basic_question(q_num, group))
                    
            except Exception as e:
                self.logger.error(f"提取題目 {q_num} 時發生錯誤: {e}")
                questions.append(self._create_basic_question(q_num, group))
        
        self.logger.info(f"題組 {start_q}-{end_q} 提取完成: {len(questions)} 題")
        return questions
    
    def _extract_single_question(self, content: str, q_num: int, group: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """提取單一題目"""
        # 尋找題目位置
        question_patterns = [
            rf'{q_num}\s*[：:]\s*(.*?)(?={q_num+1}\s*[：:]|$)',
            rf'第{q_num}題[：:]?\s*(.*?)(?=第{q_num+1}題|$)',
            rf'{q_num}\.\s*(.*?)(?={q_num+1}\.|$)',
        ]
        
        question_text = ""
        for pattern in question_patterns:
            match = re.search(pattern, content, re.DOTALL)
            if match:
                question_text = match.group(1).strip()
                break
        
        if not question_text:
            # 嘗試更寬鬆的匹配
            loose_patterns = [
                rf'{q_num}\s+.*?(?={q_num+1}\s+|$)',
                rf'第{q_num}題.*?(?=第{q_num+1}題|$)',
            ]
            
            for pattern in loose_patterns:
                match = re.search(pattern, content, re.DOTALL)
                if match:
                    question_text = match.group(0).strip()
                    break
        
        if not question_text:
            return None
        
        # 提取選項
        options = self._extract_options_from_text(question_text)
        
        # 建立題目資料
        question = {
            '題號': str(q_num),
            '題目': self._clean_question_text(question_text),
            '選項A': options.get('A', ''),
            '選項B': options.get('B', ''),
            '選項C': options.get('C', ''),
            '選項D': options.get('D', ''),
            '題型': '選擇題',
            '正確答案': '',
            '更正答案': '',
            '題組': True,
            '題組編號': f"{group['start_question']}-{group['end_question']}",
            '題組內容': group['content'][:300] + '...' if len(group['content']) > 300 else group['content'],
            '原始題目': question_text,
            '提取信心度': self._calculate_extraction_confidence(question_text, options),
            '選項數量': len([opt for opt in options.values() if opt.strip()])
        }
        
        return question
    
    def _extract_options_from_text(self, text: str) -> Dict[str, str]:
        """從文字中提取選項 - 增強版算法"""
        options = {}
        
        # 嘗試不同的選項模式
        for pattern_info in self.option_patterns:
            pattern = pattern_info['pattern']
            option_type = pattern_info['type']
            
            try:
                matches = re.findall(pattern, text, re.DOTALL)
                if len(matches) >= 2:  # 至少要有2個選項
                    for i, match in enumerate(matches[:4]):  # 最多4個選項
                        if match and len(match.strip()) > 1:
                            option_letter = chr(ord('A') + i)
                            options[option_letter] = match.strip()
                    
                    if len(options) >= 2:
                        break
                        
            except re.error as e:
                self.logger.warning(f"選項模式錯誤: {pattern} - {e}")
                continue
        
        # 如果標準模式失敗，嘗試更簡單的方法
        if len(options) < 2:
            options = self._extract_options_simple(text)
        
        return options
    
    def _extract_options_simple(self, text: str) -> Dict[str, str]:
        """簡單的選項提取方法"""
        options = {}
        
        # 按行分割
        lines = text.split('\n')
        current_option = None
        current_content = ""
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # 檢查是否為選項開始
            option_match = re.match(r'^([ＡＢＣＤABCD])\s*(.*)', line)
            if option_match:
                # 保存前一個選項
                if current_option and current_content:
                    options[current_option] = current_content.strip()
                
                # 開始新選項
                current_option = option_match.group(1)
                current_content = option_match.group(2)
            else:
                # 繼續當前選項
                if current_option and current_content:
                    current_content += " " + line
        
        # 保存最後一個選項
        if current_option and current_content:
            options[current_option] = current_content.strip()
        
        return options
    
    def _clean_question_text(self, text: str) -> str:
        """清理題目文字"""
        # 移除選項標記
        text = re.sub(r'[（(][ＡＢＣＤABCD][）)]', '', text)
        text = re.sub(r'^[ＡＢＣＤABCD]\s*', '', text, flags=re.MULTILINE)
        
        # 移除多餘空白
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'\n\s*\n', '\n', text)
        
        return text.strip()
    
    def _calculate_extraction_confidence(self, question_text: str, options: Dict[str, str]) -> float:
        """計算提取信心度"""
        confidence = 0.0
        
        # 題目長度因子
        if len(question_text) > 20:
            confidence += 0.2
        if len(question_text) > 50:
            confidence += 0.2
        
        # 選項數量因子
        option_count = len([opt for opt in options.values() if opt.strip()])
        if option_count >= 2:
            confidence += 0.3
        if option_count >= 4:
            confidence += 0.2
        
        # 選項長度因子
        avg_option_length = sum(len(opt) for opt in options.values() if opt.strip()) / max(option_count, 1)
        if avg_option_length > 5:
            confidence += 0.1
        
        return min(confidence, 1.0)
    
    def _create_basic_question(self, q_num: int, group: Dict[str, Any]) -> Dict[str, Any]:
        """創建基本題目結構"""
        return {
            '題號': str(q_num),
            '題目': f"題組題目（第{q_num}題）",
            '選項A': '',
            '選項B': '',
            '選項C': '',
            '選項D': '',
            '題型': '選擇題',
            '正確答案': '',
            '更正答案': '',
            '題組': True,
            '題組編號': f"{group['start_question']}-{group['end_question']}",
            '題組內容': group['content'][:300] + '...' if len(group['content']) > 300 else group['content'],
            '原始題目': '',
            '提取信心度': 0.0,
            '選項數量': 0
        }
    
    def process_pdf_with_enhanced_groups(self, pdf_path: str, output_dir: str = "", 
                                       answer_pdf_path: str = "") -> Tuple[List[str], Dict[str, Any]]:
        """
        使用增強版處理器處理PDF
        
        Args:
            pdf_path: PDF檔案路徑
            output_dir: 輸出目錄
            answer_pdf_path: 答案PDF檔案路徑
            
        Returns:
            (保存的檔案列表, 統計資訊)
        """
        self.logger.info(f"開始處理PDF: {pdf_path}")
        
        print(f"\n{'='*70}")
        print(f"📄 {os.path.basename(pdf_path)} (增強版題組處理)")
        print(f"{'='*70}")
        
        try:
            # 提取PDF文字
            with pdfplumber.open(pdf_path) as pdf:
                text = ""
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
            
            self.logger.info(f"PDF文字提取完成: {len(text)} 字元")
            print(f"📊 提取文字長度: {len(text)} 字元")
            
            # 檢測題組
            groups = self.detect_question_groups(text)
            print(f"🔍 檢測到 {len(groups)} 個題組")
            
            questions = []
            group_stats = []
            
            if groups:
                # 處理題組
                for group in groups:
                    print(f"   📚 題組 {group['start_question']}-{group['end_question']}: {group['question_count']} 題 (信心度: {group['detection_confidence']:.2f})")
                    
                    group_questions = self.extract_questions_from_group(group)
                    questions.extend(group_questions)
                    
                    group_stats.append({
                        'start_question': group['start_question'],
                        'end_question': group['end_question'],
                        'question_count': group['question_count'],
                        'extracted_count': len(group_questions),
                        'confidence': group['detection_confidence']
                    })
            
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
            
            # 儲存一般題目
            if regular_questions:
                path = os.path.join(output_dir, f"{base}_一般題目.csv")
                pd.DataFrame(regular_questions).to_csv(path, index=False, encoding='utf-8-sig')
                print(f"✅ {path} ({len(regular_questions)}題)")
                saved_files.append(path)
            
            # 儲存題組題目
            if group_questions:
                path = os.path.join(output_dir, f"{base}_題組題目.csv")
                pd.DataFrame(group_questions).to_csv(path, index=False, encoding='utf-8-sig')
                print(f"✅ {path} ({len(group_questions)}題)")
                saved_files.append(path)
            
            # 儲存完整題目
            if questions:
                path = os.path.join(output_dir, f"{base}_完整題目.csv")
                pd.DataFrame(questions).to_csv(path, index=False, encoding='utf-8-sig')
                print(f"✅ {path} ({len(questions)}題)")
                saved_files.append(path)
            
            # 儲存統計報告
            stats_path = os.path.join(output_dir, f"{base}_處理統計.json")
            stats = {
                'total_questions': len(questions),
                'regular_questions': len(regular_questions),
                'group_questions': len(group_questions),
                'question_groups': group_stats,
                'processing_time': datetime.now().isoformat(),
                'pdf_file': pdf_path,
                'output_directory': output_dir
            }
            
            with open(stats_path, 'w', encoding='utf-8') as f:
                json.dump(stats, f, ensure_ascii=False, indent=2)
            
            print(f"✅ {stats_path}")
            saved_files.append(stats_path)
            
            return saved_files, stats
            
        except Exception as e:
            error_msg = f"處理失敗: {e}"
            self.logger.error(error_msg)
            print(f"❌ {error_msg}")
            import traceback
            traceback.print_exc()
            return [], {}

def main():
    """主函數"""
    import argparse
    
    parser = argparse.ArgumentParser(description='增強版PDF轉CSV工具 - 優化題組處理')
    parser.add_argument('input', help='輸入PDF檔案')
    parser.add_argument('-o', '--output', default='test_output', help='輸出目錄')
    parser.add_argument('--answer', default='', help='答案PDF檔案路徑')
    
    args = parser.parse_args()
    
    if os.path.isfile(args.input):
        processor = EnhancedQuestionGroupProcessor()
        saved_files, stats = processor.process_pdf_with_enhanced_groups(args.input, args.output, args.answer)
        
        if saved_files:
            print(f"\n✅ 已儲存: {saved_files}")
            print(f"📊 統計: {stats}")
        else:
            print("\n❌ 處理失敗")
    else:
        print("❌ 輸入檔案不存在")

if __name__ == "__main__":
    main()