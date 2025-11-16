#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Google Apps Script生成器
負責生成Google表單的JavaScript代碼
"""

import os
import pandas as pd
from typing import List, Dict, Any, Optional
from ..utils.logger import logger
from ..utils.exceptions import GoogleFormError
from ..utils.config import config_manager


class GoogleScriptGenerator:
    """Google Apps Script生成器"""
    
    def __init__(self):
        self.logger = logger
        self.google_form_config = config_manager.get_google_form_config()
    
    def generate_script(self, csv_path: str, output_path: str) -> str:
        """
        從CSV檔案生成Google Apps Script代碼
        
        Args:
            csv_path: CSV檔案路徑
            output_path: 輸出JavaScript檔案路徑
            
        Returns:
            生成的JavaScript檔案路徑
        """
        try:
            self.logger.info(f"開始生成Google Apps Script: {csv_path}")
            
            # 讀取CSV檔案
            df = pd.read_csv(csv_path, encoding='utf-8-sig')
            
            # 生成JavaScript代碼
            script_content = self._generate_script_content(df)
            
            # 儲存檔案
            output_dir = os.path.dirname(output_path)
            if output_dir:
                os.makedirs(output_dir, exist_ok=True)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(script_content)
            
            self.logger.success(f"Google Apps Script生成完成: {output_path}")
            return output_path
            
        except Exception as e:
            error_msg = f"Google Apps Script生成失敗: {e}"
            self.logger.failure(error_msg)
            raise GoogleFormError(error_msg) from e
    
    def _generate_script_content(self, df: pd.DataFrame) -> str:
        """生成JavaScript代碼內容"""
        
        # 取得基本資訊
        total_questions = len(df)
        exam_title = self.google_form_config.form_title
        form_description = self.google_form_config.form_description.format(
            total_questions=total_questions
        )
        
        # 生成題目資料
        questions_data = self._generate_questions_data(df)
        
        script_template = f"""
/**
 * 考古題練習表單生成器
 * 自動從CSV資料建立Google表單
 * 生成時間: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}
 */

function createPracticeForm() {{
  // 表單設定
  const formTitle = "{exam_title}";
  const formDescription = "{form_description}";
  
  // 建立新表單
  const form = FormApp.create(formTitle);
  form.setDescription(formDescription);
  form.setConfirmationMessage("感謝您的練習！結果將自動計算分數。");
  form.setShowLinkToRespondAgain(false);
  
  // 設定分數計算
  form.setCollectEmail({str(self.google_form_config.collect_email).lower()});
  form.setRequireLogin({str(self.google_form_config.require_login).lower()});
  
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
  const questions = {questions_data};
  
  questions.forEach((question, index) => {{
    const item = form.addMultipleChoiceItem();
    item.setTitle(`第${{index + 1}}題: ${{question.title}}`);
    item.setChoices([
      item.createChoice(question.optionA, question.optionA),
      item.createChoice(question.optionB, question.optionB),
      item.createChoice(question.optionC, question.optionC),
      item.createChoice(question.optionD, question.optionD)
    ]);
    item.setRequired(true);
    
    // 添加題目分類標籤
    if (question.category) {{
      item.setHelpText(`分類: ${{question.category}} | 難度: ${{question.difficulty}}`);
    }}
  }});
}}

function addSubmitHandler(form) {{
  // 添加提交後處理腳本
  const script = `
    function onSubmit(e) {{
      const responses = e.response.getItemResponses();
      let correctCount = 0;
      let totalCount = responses.length;
      
      const answers = {self._generate_answers_data(df)};
      
      responses.forEach((response, index) => {{
        const questionNumber = index + 1;
        const userAnswer = response.getResponse();
        const correctAnswer = answers[questionNumber];
        
        if (userAnswer === correctAnswer) {{
          correctCount++;
        }}
      }});
      
      const score = Math.round((correctCount / totalCount) * 100);
      
      // 記錄分數到試算表
      const sheet = SpreadsheetApp.getActiveSheet();
      const timestamp = new Date();
      sheet.appendRow([timestamp, score, correctCount, totalCount]);
      
      // 顯示結果
      console.log(`分數: ${{score}}分 (${{correctCount}}/${{totalCount}})`);
    }}
  `;
  
  // 這裡可以添加更複雜的提交處理邏輯
  console.log("提交處理器已設定");
}}

// 執行主函數
function main() {{
  return createPracticeForm();
}}
"""
        
        return script_template
    
    def _generate_questions_data(self, df: pd.DataFrame) -> str:
        """生成題目資料JavaScript陣列"""
        questions = []
        
        for _, row in df.iterrows():
            question = {
                'title': self._escape_js_string(str(row.get('題目', ''))),
                'optionA': self._escape_js_string(str(row.get('選項A', ''))),
                'optionB': self._escape_js_string(str(row.get('選項B', ''))),
                'optionC': self._escape_js_string(str(row.get('選項C', ''))),
                'optionD': self._escape_js_string(str(row.get('選項D', ''))),
                'category': str(row.get('分類', '')),
                'difficulty': str(row.get('難度', '')),
                'isGroup': bool(row.get('題組', False))
            }
            questions.append(question)
        
        # 轉換為JavaScript陣列格式
        js_array = "[\n"
        for i, question in enumerate(questions):
            js_array += "    {\n"
            for key, value in question.items():
                if isinstance(value, str):
                    js_array += f"      {key}: \"{value}\",\n"
                else:
                    js_array += f"      {key}: {value},\n"
            js_array += "    }"
            if i < len(questions) - 1:
                js_array += ","
            js_array += "\n"
        js_array += "  ]"
        
        return js_array
    
    def _generate_answers_data(self, df: pd.DataFrame) -> str:
        """生成答案資料JavaScript物件"""
        answers = {}
        
        for index, row in df.iterrows():
            question_number = index + 1
            answer = str(row.get('最終答案', row.get('正確答案', '')))
            if answer and answer.upper() in ['A', 'B', 'C', 'D']:
                answers[question_number] = answer.upper()
        
        # 轉換為JavaScript物件格式
        js_object = "{\n"
        for question_number, answer in answers.items():
            js_object += f"    {question_number}: \"{answer}\",\n"
        js_object += "  }"
        
        return js_object
    
    def _escape_js_string(self, text: str) -> str:
        """轉義JavaScript字串"""
        if not text:
            return ""
        
        # 轉義特殊字元
        text = text.replace('\\', '\\\\')
        text = text.replace('"', '\\"')
        text = text.replace('\n', '\\n')
        text = text.replace('\r', '\\r')
        text = text.replace('\t', '\\t')
        
        return text