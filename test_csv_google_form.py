#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試CSV檔案是否適合用於Google表單製作
"""

import pandas as pd
import os
import json

def test_csv_google_form_compatibility():
    """測試CSV檔案的Google表單適用性"""
    
    print("🧪 測試CSV檔案的Google表單適用性")
    print("="*60)
    
    # 檢查現有CSV檔案
    csv_files = [
        "test_output/測試考古題_選擇題.csv",
        "test_output/測試考古題_Google表單.csv",
        "test_output/完整工作流程測試.csv"
    ]
    
    for csv_file in csv_files:
        if os.path.exists(csv_file):
            print(f"\n📄 分析檔案: {csv_file}")
            analyze_csv_file(csv_file)
        else:
            print(f"⚠️ 檔案不存在: {csv_file}")
    
    # 創建理想的測試CSV
    print(f"\n🔧 創建理想的測試CSV...")
    create_ideal_test_csv()

def analyze_csv_file(csv_path: str):
    """分析單個CSV檔案"""
    
    try:
        # 讀取CSV
        df = pd.read_csv(csv_path, encoding='utf-8-sig')
        
        print(f"   📊 資料筆數: {len(df)}")
        print(f"   📋 欄位: {list(df.columns)}")
        
        # 檢查必要欄位
        required_fields = ['題號', '題目', '題型', '選項A', '選項B', '選項C', '選項D']
        missing_fields = [field for field in required_fields if field not in df.columns]
        
        if missing_fields:
            print(f"   ❌ 缺少必要欄位: {missing_fields}")
        else:
            print(f"   ✅ 必要欄位完整")
        
        # 檢查答案欄位
        answer_fields = ['正確答案', '更正答案', '最終答案']
        has_answer_fields = any(field in df.columns for field in answer_fields)
        
        if has_answer_fields:
            print(f"   ✅ 包含答案欄位")
            for field in answer_fields:
                if field in df.columns:
                    non_empty = df[field].notna().sum()
                    print(f"      {field}: {non_empty} 筆有資料")
        else:
            print(f"   ⚠️ 缺少答案欄位")
        
        # 檢查選項差異性
        check_option_diversity(df)
        
        # 檢查資料品質
        check_data_quality(df)
        
    except Exception as e:
        print(f"   ❌ 讀取失敗: {e}")

def check_option_diversity(df):
    """檢查選項差異性"""
    
    print(f"   🔍 檢查選項差異性...")
    
    option_columns = ['選項A', '選項B', '選項C', '選項D']
    duplicate_options = 0
    
    for _, row in df.iterrows():
        options = [str(row[col]) for col in option_columns if col in df.columns]
        if len(set(options)) < len(options):
            duplicate_options += 1
    
    if duplicate_options > 0:
        print(f"      ⚠️ {duplicate_options} 題有重複選項")
    else:
        print(f"      ✅ 選項差異性良好")

def check_data_quality(df):
    """檢查資料品質"""
    
    print(f"   🔍 檢查資料品質...")
    
    # 檢查空值
    empty_questions = df['題目'].isna().sum()
    if empty_questions > 0:
        print(f"      ⚠️ {empty_questions} 題題目為空")
    
    # 檢查題目長度
    short_questions = (df['題目'].str.len() < 10).sum()
    if short_questions > 0:
        print(f"      ⚠️ {short_questions} 題題目過短")
    
    # 檢查題號連續性
    if '題號' in df.columns:
        try:
            question_numbers = pd.to_numeric(df['題號'])
            expected_range = set(range(1, len(df) + 1))
            actual_range = set(question_numbers)
            missing_numbers = expected_range - actual_range
            if missing_numbers:
                print(f"      ⚠️ 缺少題號: {sorted(missing_numbers)}")
            else:
                print(f"      ✅ 題號連續性良好")
        except:
            print(f"      ⚠️ 題號格式有問題")

def create_ideal_test_csv():
    """創建理想的測試CSV檔案"""
    
    # 理想的測試資料
    ideal_data = [
        {
            '題號': '1',
            '題目': '下列各組「」內的字，讀音完全相同的選項是：',
            '題型': '選擇題',
            '選項A': '「緋」聞纏身／「誹」謗他人／「斐」然成章',
            '選項B': '「緋」聞纏身／「誹」謗他人／「斐」然成章',
            '選項C': '「緋」聞纏身／「誹」謗他人／「斐」然成章',
            '選項D': '「緋」聞纏身／「誹」謗他人／「斐」然成章',
            '正確答案': 'A',
            '更正答案': '',
            '最終答案': 'A',
            '難度': '中等',
            '分類': '國文',
            '備註': ''
        },
        {
            '題號': '2',
            '題目': '下列文句，完全沒有錯別字的選項是：',
            '題型': '選擇題',
            '選項A': '他做事總是虎頭蛇尾，令人失望',
            '選項B': '他做事總是虎頭蛇尾，令人失望',
            '選項C': '他做事總是虎頭蛇尾，令人失望',
            '選項D': '他做事總是虎頭蛇尾，令人失望',
            '正確答案': 'B',
            '更正答案': 'C',
            '最終答案': 'C',
            '難度': '簡單',
            '分類': '國文',
            '備註': ''
        },
        {
            '題號': '3',
            '題目': '下列成語使用正確的選項是：',
            '題型': '選擇題',
            '選項A': '他做事總是虎頭蛇尾，令人失望',
            '選項B': '他做事總是虎頭蛇尾，令人失望',
            '選項C': '他做事總是虎頭蛇尾，令人失望',
            '選項D': '他做事總是虎頭蛇尾，令人失望',
            '正確答案': 'C',
            '更正答案': '',
            '最終答案': 'C',
            '難度': '困難',
            '分類': '國文',
            '備註': ''
        }
    ]
    
    # 創建DataFrame
    df = pd.DataFrame(ideal_data)
    
    # 儲存CSV
    output_path = "test_output/理想格式_Google表單.csv"
    os.makedirs("test_output", exist_ok=True)
    df.to_csv(output_path, index=False, encoding='utf-8-sig')
    
    print(f"   ✅ 已創建: {output_path}")
    
    # 分析創建的檔案
    print(f"   📊 分析創建的檔案...")
    analyze_csv_file(output_path)
    
    # 生成Google Apps Script
    print(f"\n🔧 生成Google Apps Script...")
    generate_google_apps_script(df, "test_output/理想格式_GoogleAppsScript.js")

def generate_google_apps_script(df, output_path):
    """生成Google Apps Script代碼"""
    
    # 轉換題目資料為JavaScript格式
    questions_js = convert_to_js_array(df)
    
    # 建立正確答案對照表
    answers_js = create_answers_dict(df)
    
    # 生成腳本內容
    script_content = f"""
/**
 * 考古題練習表單生成器
 * 自動從CSV資料建立Google表單
 */

function createPracticeForm() {{
  // 表單設定
  const formTitle = "考古題練習 - 理想格式測試";
  const formDescription = "此表單包含 {len(df)} 題考古題，用於練習和自測。";
  
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
}}

function addQuestionsToForm(form) {{
  // 題目資料（從CSV匯入）
  const questions = {questions_js};
  
  questions.forEach((q, index) => {{
    const questionText = "第" + q.題號 + "題: " + q.題目;
    
    if (q.題型 === "選擇題") {{
      const item = form.addMultipleChoiceItem();
      item.setTitle(questionText);
      item.setChoices([
        item.createChoice(q.選項A, false),
        item.createChoice(q.選項B, false),
        item.createChoice(q.選項C, false),
        item.createChoice(q.選項D, false)
      ]);
      item.setRequired(true);
      item.setPoints(1);
    }} else if (q.題型 === "問答題") {{
      const item = form.addParagraphTextItem();
      item.setTitle(questionText);
      item.setRequired(true);
      item.setPoints(1);
    }}
  }});
}}

function addSubmitHandler(form) {{
  // 建立觸發器，在提交後自動評分
  ScriptApp.newTrigger("gradeResponses")
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
  const correctAnswers = {answers_js};
  
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
  const match = questionText.match(/第(\\d+)題/);
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

// 執行主函數
function main() {{
  return createPracticeForm();
}}
"""
    
    # 儲存腳本
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(script_content)
    
    print(f"   ✅ Google Apps Script已生成: {output_path}")

def convert_to_js_array(df):
    """將DataFrame轉換為JavaScript陣列格式"""
    
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

def create_answers_dict(df):
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

if __name__ == "__main__":
    test_csv_google_form_compatibility()
    print("\n🎉 測試完成！")