#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Google表單考古題轉換器
將PDF考古題轉換為適合Google表單的CSV格式
"""

import os
import pandas as pd
import json
import re
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import glob

class GoogleFormsConverter:
    """Google表單格式轉換器"""
    
    def __init__(self):
        self.question_types = {
            '選擇題': 'MULTIPLE_CHOICE',
            '問答題': 'PARAGRAPH_TEXT'
        }
    
    def parse_answer_file(self, answer_pdf_path: str) -> Dict[str, str]:
        """解析答案檔案，提取正確答案"""
        try:
            import pdfplumber
            
            with pdfplumber.open(answer_pdf_path) as pdf:
                text = ""
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
            
            # 使用正則表達式提取答案
            answers = {}
            
            # 匹配格式如: 1.(A) 2.(B) 3.(C) 等
            pattern1 = r'(\d+)\.\s*\(([A-D])\)'
            matches1 = re.findall(pattern1, text)
            for num, answer in matches1:
                answers[num] = answer
            
            # 匹配格式如: 1A 2B 3C 等
            pattern2 = r'(\d+)([A-D])'
            matches2 = re.findall(pattern2, text)
            for num, answer in matches2:
                if num not in answers:  # 避免覆蓋已存在的答案
                    answers[num] = answer
            
            # 匹配格式如: 1. A 2. B 3. C 等
            pattern3 = r'(\d+)\.\s+([A-D])'
            matches3 = re.findall(pattern3, text)
            for num, answer in matches3:
                if num not in answers:
                    answers[num] = answer
            
            print(f"✅ 從答案檔案解析出 {len(answers)} 個答案")
            return answers
            
        except Exception as e:
            print(f"❌ 解析答案檔案失敗: {e}")
            return {}
    
    def convert_to_google_forms_format(self, questions: List[Dict[str, Any]], 
                                     answers: Dict[str, str] = None) -> List[Dict[str, Any]]:
        """轉換為Google表單格式"""
        google_forms_data = []
        
        for question in questions:
            question_num = question.get('題號', '')
            question_text = question.get('題目', '')
            question_type = question.get('題型', '選擇題')
            
            # 基本問題資訊
            form_question = {
                '題號': question_num,
                '題目': question_text,
                '題型': question_type,
                '正確答案': answers.get(question_num, '') if answers else '',
                '選項A': question.get('選項A', ''),
                '選項B': question.get('選項B', ''),
                '選項C': question.get('選項C', ''),
                '選項D': question.get('選項D', ''),
                '說明': f"正確答案: {answers.get(question_num, '未提供')}" if answers else '',
                '分數': 1,  # 每題1分
                '必答': True
            }
            
            google_forms_data.append(form_question)
        
        return google_forms_data
    
    def create_google_apps_script(self, questions_data: List[Dict[str, Any]], 
                                form_title: str = "考古題練習") -> str:
        """生成Google Apps Script代碼"""
        
        script_template = f'''function createExamForm() {{
  // 建立新的Google表單
  var form = FormApp.create('{form_title}');
  
  // 設定表單描述
  form.setDescription('考古題練習表單 - 自動生成於 {datetime.now().strftime("%Y-%m-%d %H:%M")}');
  
  // 設定為測驗模式
  form.setIsQuiz(true);
  
  // 設定分數
  form.setPoints(100);
  
  // 設定回饋設定
  form.setConfirmationMessage('感謝您的作答！');
  
  // 題目資料
  var questions = {json.dumps(questions_data, ensure_ascii=False, indent=2)};
  
  // 建立題目
  questions.forEach(function(q, index) {{
    var item;
    
    if (q.題型 === '選擇題') {{
      // 建立選擇題
      item = form.addMultipleChoiceItem();
      item.setTitle(q.題目);
      item.setRequired(q.必答);
      
      // 設定選項
      var choices = [];
      if (q.選項A) choices.push(q.選項A);
      if (q.選項B) choices.push(q.選項B);
      if (q.選項C) choices.push(q.選項C);
      if (q.選項D) choices.push(q.選項D);
      
      item.setChoices(choices.map(function(choice, i) {{
        return item.createChoice(choice, i === 0); // 預設第一個選項為正確答案
      }}));
      
      // 設定正確答案
      if (q.正確答案) {{
        var correctAnswer = q.正確答案;
        var correctIndex = ['A', 'B', 'C', 'D'].indexOf(correctAnswer);
        if (correctIndex !== -1 && correctIndex < choices.length) {{
          item.setChoices(choices.map(function(choice, i) {{
            return item.createChoice(choice, i === correctIndex);
          }}));
        }}
      }}
      
      // 設定分數
      item.setPoints(q.分數);
      
    }} else if (q.題型 === '問答題') {{
      // 建立問答題
      item = form.addParagraphTextItem();
      item.setTitle(q.題目);
      item.setRequired(q.必答);
    }}
    
    // 添加說明
    if (q.說明) {{
      item.setHelpText(q.說明);
    }}
  }});
  
  // 設定表單設定
  form.setAcceptingResponses(true);
  form.setShowLinkToRespondAgain(false);
  
  // 回傳表單URL
  Logger.log('表單已建立: ' + form.getPublishedUrl());
  return form.getPublishedUrl();
}}

// 執行函數
function main() {{
  var formUrl = createExamForm();
  console.log('表單URL: ' + formUrl);
}}'''
        
        return script_template
    
    def process_pdf_to_google_forms(self, pdf_path: str, answer_path: str = None, 
                                  output_dir: str = "google_forms_output") -> Dict[str, Any]:
        """處理PDF檔案並生成Google表單相關檔案"""
        
        print(f"\n{'='*70}")
        print(f"📄 處理檔案: {os.path.basename(pdf_path)}")
        print(f"{'='*70}")
        
        # 建立輸出目錄
        os.makedirs(output_dir, exist_ok=True)
        
        # 導入現有的PDF解析功能
        try:
            from pdf_to_csv import process_pdf_to_csv
            csv_files, validation_result = process_pdf_to_csv(pdf_path, output_dir)
        except ImportError:
            print("❌ 無法導入pdf_to_csv模組")
            return {}
        
        if not csv_files:
            print("❌ 沒有成功解析出CSV檔案")
            return {}
        
        # 讀取CSV檔案
        all_questions = []
        for csv_file in csv_files:
            if '選擇題' in csv_file:
                df = pd.read_csv(csv_file, encoding='utf-8-sig')
                questions = df.to_dict('records')
                all_questions.extend(questions)
        
        if not all_questions:
            print("❌ 沒有找到題目資料")
            return {}
        
        print(f"✅ 找到 {len(all_questions)} 題")
        
        # 解析答案檔案
        answers = {}
        if answer_path and os.path.exists(answer_path):
            answers = self.parse_answer_file(answer_path)
        
        # 轉換為Google表單格式
        google_forms_data = self.convert_to_google_forms_format(all_questions, answers)
        
        # 生成檔案名稱
        base_name = os.path.splitext(os.path.basename(pdf_path))[0]
        
        # 儲存Google表單格式的CSV
        google_csv_path = os.path.join(output_dir, f"{base_name}_google_forms.csv")
        df_google = pd.DataFrame(google_forms_data)
        df_google.to_csv(google_csv_path, index=False, encoding='utf-8-sig')
        print(f"✅ Google表單CSV: {google_csv_path}")
        
        # 生成Google Apps Script
        script_content = self.create_google_apps_script(google_forms_data, f"{base_name}考古題練習")
        script_path = os.path.join(output_dir, f"{base_name}_google_apps_script.js")
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(script_content)
        print(f"✅ Google Apps Script: {script_path}")
        
        # 生成使用說明
        readme_content = f"""# {base_name} - Google表單考古題

## 檔案說明
- `{base_name}_google_forms.csv`: Google表單格式的題目資料
- `{base_name}_google_apps_script.js`: Google Apps Script代碼

## 使用步驟

### 方法1: 使用Google Apps Script (推薦)
1. 開啟 [Google Apps Script](https://script.google.com)
2. 建立新專案
3. 複製 `{base_name}_google_apps_script.js` 的內容到編輯器
4. 點擊「執行」按鈕
5. 系統會自動建立Google表單並回傳URL

### 方法2: 手動建立表單
1. 開啟 [Google表單](https://forms.google.com)
2. 建立新表單
3. 參考 `{base_name}_google_forms.csv` 的資料手動輸入題目

## 題目統計
- 總題數: {len(google_forms_data)}
- 選擇題: {len([q for q in google_forms_data if q['題型'] == '選擇題'])}
- 問答題: {len([q for q in google_forms_data if q['題型'] == '問答題'])}
- 有答案的題目: {len([q for q in google_forms_data if q['正確答案']])}

## 注意事項
- 請確認所有題目和選項都正確無誤
- 建議先在測試環境中建立表單進行測試
- 可以根據需要調整表單設定（如時間限制、分數等）

生成時間: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
"""
        
        readme_path = os.path.join(output_dir, f"{base_name}_README.md")
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(readme_content)
        print(f"✅ 使用說明: {readme_path}")
        
        return {
            'google_csv': google_csv_path,
            'script': script_path,
            'readme': readme_path,
            'question_count': len(google_forms_data),
            'answer_count': len(answers)
        }

def main():
    """主程式"""
    print("Google表單考古題轉換器")
    print("="*70)
    
    # 設定路徑
    input_dir = "考選部考古題完整庫/民國114年"
    output_dir = "google_forms_output"
    
    if not os.path.exists(input_dir):
        print(f"❌ 輸入目錄不存在: {input_dir}")
        return
    
    converter = GoogleFormsConverter()
    
    # 尋找PDF檔案
    pdf_files = glob.glob(os.path.join(input_dir, "**", "*.pdf"), recursive=True)
    
    if not pdf_files:
        print("❌ 沒有找到PDF檔案")
        return
    
    print(f"找到 {len(pdf_files)} 個PDF檔案")
    
    # 處理每個PDF檔案
    results = []
    for i, pdf_path in enumerate(pdf_files, 1):
        print(f"\n[{i}/{len(pdf_files)}] 處理: {os.path.basename(pdf_path)}")
        
        # 尋找對應的答案檔案
        answer_path = None
        base_name = os.path.splitext(os.path.basename(pdf_path))[0]
        answer_keywords = ['答案', '解答', 'answer']
        
        for keyword in answer_keywords:
            for ext in ['.pdf', '.PDF']:
                potential_answer = pdf_path.replace(base_name, f"{base_name}_{keyword}").replace('.pdf', f'_{keyword}{ext}')
                if os.path.exists(potential_answer):
                    answer_path = potential_answer
                    break
            if answer_path:
                break
        
        if answer_path:
            print(f"✅ 找到答案檔案: {os.path.basename(answer_path)}")
        else:
            print("⚠️ 未找到答案檔案")
        
        # 處理PDF
        result = converter.process_pdf_to_google_forms(pdf_path, answer_path, output_dir)
        if result:
            results.append(result)
    
    # 生成總報告
    print(f"\n{'='*70}")
    print("處理完成報告")
    print(f"{'='*70}")
    print(f"成功處理: {len(results)} 個檔案")
    print(f"輸出目錄: {output_dir}")
    
    if results:
        total_questions = sum(r['question_count'] for r in results)
        total_answers = sum(r['answer_count'] for r in results)
        print(f"總題數: {total_questions}")
        print(f"有答案的題目: {total_answers}")
        
        # 生成總覽檔案
        overview_content = f"""# Google表單考古題總覽

## 處理統計
- 處理檔案數: {len(results)}
- 總題數: {total_questions}
- 有答案的題目: {total_answers}

## 檔案清單
"""
        
        for i, result in enumerate(results, 1):
            overview_content += f"""
### {i}. {os.path.basename(result['google_csv']).replace('_google_forms.csv', '')}
- 題目數: {result['question_count']}
- 答案數: {result['answer_count']}
- CSV檔案: {os.path.basename(result['google_csv'])}
- Script檔案: {os.path.basename(result['script'])}
"""
        
        overview_path = os.path.join(output_dir, "總覽.md")
        with open(overview_path, 'w', encoding='utf-8') as f:
            f.write(overview_content)
        print(f"✅ 總覽檔案: {overview_path}")

if __name__ == "__main__":
    main()