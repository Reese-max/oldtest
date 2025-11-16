#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Google Apps Script代碼生成器
用於將CSV資料轉換為Google表單
"""

import pandas as pd
import os
from typing import List, Dict, Any

class GoogleAppsScriptGenerator:
    """Google Apps Script代碼生成器"""
    
    def __init__(self):
        self.script_template = """
/**
 * 考古題練習表單生成器
 * 自動從CSV資料建立Google表單
 */

function createPracticeForm() {
  // 表單設定
  const formTitle = "考古題練習 - {exam_title}";
  const formDescription = "此表單包含 {total_questions} 題考古題，用於練習和自測。";
  
  // 建立新表單
  const form = FormApp.create(formTitle);
  form.setDescription(formDescription);
  form.setConfirmationMessage("感謝您的練習！結果將自動計算分數。");
  form.setShowLinkToRespondAgain(false);
  
  // 設定分數計算
  form.setCollectEmail(true);
  form.setRequireLogin(false);
  
  // 添加題目
  addQuestionsToForm(form);
  
  // 添加提交後處理
  addSubmitHandler(form);
  
  // 取得表單連結
  const formUrl = form.getPublishedUrl();
  console.log("表單已建立: " + formUrl);
  
  return formUrl;
}

function addQuestionsToForm(form) {
  // 題目資料（從CSV匯入）
  const questions = {questions_data};
  
  questions.forEach((q, index) => {{
    const questionText = `第${{q.題號}}題: ${{q.題目}}`;
    
    if (q.題型 === '選擇題') {{
      const item = form.addMultipleChoiceItem();
      item.setTitle(questionText);
      item.setChoices([
        item.createChoice(q.選項A, false),
        item.createChoice(q.選項B, false),
        item.createChoice(q.選項C, false),
        item.createChoice(q.選項D, false)
      ]);
      item.setRequired(true);
      
      // 設定正確答案（用於自動評分）
      item.setPoints(1);
    }} else if (q.題型 === '問答題') {{
      const item = form.addParagraphTextItem();
      item.setTitle(questionText);
      item.setRequired(true);
      item.setPoints(1);
    }}
    
    // 添加題目分類標籤
    if (q.分類) {{
      const section = form.addPageBreakItem();
      section.setTitle(`分類: ${{q.分類}}`);
    }}
  }});
}

function addSubmitHandler(form) {{
  // 建立觸發器，在提交後自動評分
  ScriptApp.newTrigger('gradeResponses')
    .forForm(form)
    .onFormSubmit()
    .create();
}}

function gradeResponses(e) {{
  const form = FormApp.getActiveForm();
  const responses = form.getResponses();
  const latestResponse = responses[responses.length - 1];
  
  // 計算分數
  const score = calculateScore(latestResponse);
  
  // 發送結果到試算表
  sendResultsToSheet(latestResponse, score);
}}

function calculateScore(response) {{
  // 正確答案對照表
  const correctAnswers = {correct_answers};
  
  let score = 0;
  let totalQuestions = 0;
  
  const itemResponses = response.getItemResponses();
  itemResponses.forEach(itemResponse => {{
    const questionText = itemResponse.getItem().getTitle();
    const questionNumber = extractQuestionNumber(questionText);
    
    if (questionNumber && correctAnswers[questionNumber]) {{
      totalQuestions++;
      const userAnswer = itemResponse.getResponse();
      const correctAnswer = correctAnswers[questionNumber];
      
      if (userAnswer === correctAnswer) {{
        score++;
      }}
    }}
  }});
  
  return {{
    score: score,
    total: totalQuestions,
    percentage: Math.round((score / totalQuestions) * 100)
  }};
}}

function extractQuestionNumber(questionText) {{
  const match = questionText.match(/第(\d+)題/);
  return match ? match[1] : null;
}}

function sendResultsToSheet(response, score) {{
  // 建立或取得試算表
  const sheetName = "練習結果";
  let sheet = getOrCreateSheet(sheetName);
  
  // 記錄結果
  const timestamp = new Date();
  const email = response.getRespondentEmail() || "匿名";
  
  sheet.appendRow([
    timestamp,
    email,
    score.score,
    score.total,
    score.percentage,
    response.getResponseUrl()
  ]);
}}

function getOrCreateSheet(sheetName) {{
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  let sheet = ss.getSheetByName(sheetName);
  
  if (!sheet) {{
    sheet = ss.insertSheet(sheetName);
    sheet.getRange(1, 1, 1, 6).setValues([
      ["時間", "使用者", "答對題數", "總題數", "正確率", "回應連結"]
    ]);
  }}
  
  return sheet;
}}

// 輔助函數：從CSV資料建立表單
function createFormFromCSV() {{
  // 此函數需要手動匯入CSV資料
  // 或使用Google Apps Script的Drive API讀取CSV檔案
  console.log("請先匯入CSV資料到questions_data變數中");
}}

// 執行主函數
function main() {{
  return createPracticeForm();
}}
"""
    
    def generate_script_from_csv(self, csv_path: str, output_path: str = None) -> str:
        """從CSV檔案生成Google Apps Script代碼"""
        
        # 讀取CSV檔案
        try:
            df = pd.read_csv(csv_path, encoding='utf-8-sig')
        except Exception as e:
            print(f"❌ 無法讀取CSV檔案: {e}")
            return None
        
        # 轉換題目資料為JavaScript格式
        questions_data = self._convert_questions_to_js(df)
        
        # 建立正確答案對照表
        correct_answers = self._create_correct_answers_dict(df)
        
        # 生成腳本
        script_content = self.script_template.format(
            exam_title="考古題練習",
            total_questions=len(df),
            questions_data=questions_data,
            correct_answers=correct_answers
        )
        
        # 儲存腳本
        if not output_path:
            base_name = os.path.splitext(os.path.basename(csv_path))[0]
            output_path = f"{base_name}_GoogleAppsScript.js"
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(script_content)
        
        print(f"✅ Google Apps Script已生成: {output_path}")
        return output_path
    
    def _convert_questions_to_js(self, df: pd.DataFrame) -> str:
        """將題目資料轉換為JavaScript陣列格式"""
        
        questions = []
        for _, row in df.iterrows():
            question = {
                '題號': str(row['題號']),
                '題目': str(row['題目']),
                '題型': str(row['題型']),
                '選項A': str(row['選項A']),
                '選項B': str(row['選項B']),
                '選項C': str(row['選項C']),
                '選項D': str(row['選項D']),
                '分類': str(row.get('分類', '')),
                '難度': str(row.get('難度', ''))
            }
            questions.append(question)
        
        # 轉換為JavaScript格式
        js_array = "[\n"
        for i, q in enumerate(questions):
            js_array += "    {\n"
            for key, value in q.items():
                # 轉義特殊字符
                escaped_value = value.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n')
                js_array += f'        "{key}": "{escaped_value}",\n'
            js_array = js_array.rstrip(',\n') + "\n    }"
            if i < len(questions) - 1:
                js_array += ","
            js_array += "\n"
        js_array += "]"
        
        return js_array
    
    def _create_correct_answers_dict(self, df: pd.DataFrame) -> str:
        """建立正確答案對照表"""
        
        answers = {}
        for _, row in df.iterrows():
            question_num = str(row['題號'])
            final_answer = str(row.get('最終答案', ''))
            if final_answer and final_answer != 'nan':
                answers[question_num] = final_answer
        
        # 轉換為JavaScript物件格式
        js_dict = "{\n"
        for q_num, answer in answers.items():
            js_dict += f'    "{q_num}": "{answer}",\n'
        js_dict = js_dict.rstrip(',\n') + "\n}"
        
        return js_dict
    
    def generate_instructions(self, output_path: str = None) -> str:
        """生成使用說明"""
        
        instructions = """
# Google Apps Script使用說明

## 1. 設定Google Apps Script

1. 前往 [Google Apps Script](https://script.google.com)
2. 建立新專案
3. 將生成的JavaScript代碼複製到編輯器中
4. 儲存專案

## 2. 啟用必要的API

1. 在Apps Script編輯器中，點選「服務」
2. 新增以下服務：
   - Google Forms API
   - Google Sheets API
   - Google Drive API

## 3. 執行腳本

1. 在編輯器中選擇 `main` 函數
2. 點選「執行」
3. 首次執行時需要授權
4. 執行完成後會顯示表單連結

## 4. 自訂設定

### 修改表單標題
在 `createPracticeForm()` 函數中修改：
```javascript
const formTitle = "您的自訂標題";
```

### 修改表單描述
```javascript
const formDescription = "您的自訂描述";
```

### 啟用自動評分
腳本已包含自動評分功能，會在提交後計算分數並記錄到試算表。

## 5. 進階功能

### 添加時間限制
可以在表單設定中添加時間限制：
```javascript
form.setLimitOneResponsePerUser(true);
```

### 自訂評分標準
修改 `calculateScore()` 函數來調整評分邏輯。

### 添加結果通知
可以在 `sendResultsToSheet()` 函數中添加郵件通知功能。

## 6. 故障排除

### 常見問題
1. **權限錯誤**: 確保已啟用所有必要的API
2. **表單無法建立**: 檢查Google帳戶權限
3. **評分不正確**: 檢查正確答案對照表

### 除錯方法
1. 使用 `console.log()` 輸出除錯資訊
2. 檢查執行記錄中的錯誤訊息
3. 確認CSV資料格式正確

## 7. 維護和更新

### 更新題目
1. 修改CSV檔案
2. 重新生成JavaScript代碼
3. 更新Apps Script中的資料

### 備份設定
建議定期備份Apps Script專案和相關的Google表單。
"""
        
        if not output_path:
            output_path = "Google_Apps_Script_使用說明.md"
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(instructions)
        
        print(f"✅ 使用說明已生成: {output_path}")
        return output_path

def main():
    """主程式"""
    print("Google Apps Script代碼生成器")
    print("="*50)
    
    # 測試CSV檔案
    csv_path = "test_output/完整測試_Google表單.csv"
    
    if not os.path.exists(csv_path):
        print(f"❌ CSV檔案不存在: {csv_path}")
        return
    
    # 建立生成器
    generator = GoogleAppsScriptGenerator()
    
    # 生成腳本
    script_path = generator.generate_script_from_csv(csv_path)
    
    if script_path:
        # 生成使用說明
        instructions_path = generator.generate_instructions()
        
        print(f"\n🎉 生成完成！")
        print(f"📄 JavaScript腳本: {script_path}")
        print(f"📋 使用說明: {instructions_path}")
        print(f"\n📝 下一步:")
        print(f"1. 將JavaScript代碼複製到Google Apps Script")
        print(f"2. 執行main()函數建立表單")
        print(f"3. 分享表單連結開始練習")

if __name__ == "__main__":
    main()