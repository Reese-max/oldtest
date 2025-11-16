#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Google Apps Script生成器（優化版）
負責生成Google表單的JavaScript代碼，支援自動評分和完善錯誤處理
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

            # 驗證CSV檔案
            if not os.path.exists(csv_path):
                raise GoogleFormError(f"CSV檔案不存在: {csv_path}")

            # 讀取CSV檔案
            df = pd.read_csv(csv_path, encoding='utf-8-sig')

            if df.empty:
                raise GoogleFormError("CSV檔案為空")

            self.logger.info(f"讀取到 {len(df)} 題")

            # 驗證必要欄位
            self._validate_csv_columns(df)

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

    def _validate_csv_columns(self, df: pd.DataFrame) -> None:
        """驗證CSV檔案必要欄位"""
        required_columns = ['題號', '題目', '選項A', '選項B', '選項C', '選項D']
        missing_columns = [col for col in required_columns if col not in df.columns]

        if missing_columns:
            raise GoogleFormError(f"CSV檔案缺少必要欄位: {', '.join(missing_columns)}")

        # 檢查是否有題目
        if df['題目'].isna().all():
            raise GoogleFormError("CSV檔案中沒有題目內容")

    def _generate_script_content(self, df: pd.DataFrame) -> str:
        """生成JavaScript代碼內容"""

        # 取得基本資訊
        total_questions = len(df)
        exam_title = self.google_form_config.form_title

        # 安全處理 form_description 格式化
        try:
            form_description = self.google_form_config.form_description.format(
                total_questions=total_questions
            )
        except (KeyError, AttributeError):
            form_description = f"{self.google_form_config.form_description} (共 {total_questions} 題)"

        # 轉義描述文字中的特殊字符
        form_description = self._escape_js_string(form_description)

        # 生成題目資料和答案資料
        questions_data = self._generate_questions_data(df)
        answers_data = self._generate_answers_data(df)

        # 判斷是否啟用自動評分
        enable_scoring = str(self.google_form_config.enable_auto_scoring).lower()

        script_template = f"""
/**
 * 考古題練習表單生成器
 * 自動從CSV資料建立Google表單（支援自動評分）
 * 生成時間: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}
 * 總題數: {total_questions}
 */

function createPracticeForm() {{
  try {{
    // 表單設定
    const formTitle = "{exam_title}";
    const formDescription = "{form_description}";

    // 建立新表單（測驗模式以支援自動評分）
    const form = FormApp.create(formTitle);
    form.setDescription(formDescription);
    form.setConfirmationMessage("感謝您完成測驗！您可以查看分數和詳細結果。");
    form.setShowLinkToRespondAgain(true);
    form.setAllowResponseEdits(false);

    // 設定為測驗模式（啟用自動評分）
    form.setIsQuiz({enable_scoring});

    // 設定收集 Email 和登入要求
    form.setCollectEmail({str(self.google_form_config.collect_email).lower()});
    form.setRequireLogin({str(self.google_form_config.require_login).lower()});

    // 添加題目
    const questionsAdded = addQuestionsToForm(form);
    console.log(`成功添加 ${{questionsAdded}} 題`);

    // 取得表單連結
    const formUrl = form.getPublishedUrl();
    const editUrl = form.getEditUrl();

    console.log("=" .repeat(60));
    console.log("✅ 表單建立成功！");
    console.log("=" .repeat(60));
    console.log(`📋 表單名稱: ${{formTitle}}`);
    console.log(`📝 題目數量: ${{questionsAdded}} 題`);
    console.log(`🔗 表單連結: ${{formUrl}}`);
    console.log(`✏️  編輯連結: ${{editUrl}}`);
    console.log("=" .repeat(60));

    return {{
      formUrl: formUrl,
      editUrl: editUrl,
      questionsCount: questionsAdded
    }};

  }} catch (error) {{
    console.error("❌ 表單建立失敗:", error);
    throw error;
  }}
}}

function addQuestionsToForm(form) {{
  const questionsData = {questions_data};
  const answersData = {answers_data};
  let addedCount = 0;

  questionsData.forEach((question, index) => {{
    try {{
      const questionNumber = index + 1;
      const correctAnswer = answersData[questionNumber];

      // 收集非空選項
      const options = [];
      const optionMap = {{
        'A': question.optionA,
        'B': question.optionB,
        'C': question.optionC,
        'D': question.optionD
      }};

      // 只添加非空選項
      for (const [key, value] of Object.entries(optionMap)) {{
        if (value && value.trim() !== '' && value !== 'nan' && value !== 'null') {{
          options.push({{ key: key, value: value.trim() }});
        }}
      }}

      // 至少需要2個選項才能創建題目
      if (options.length < 2) {{
        console.warn(`⚠️  第${{questionNumber}}題選項不足，跳過 (僅${{options.length}}個選項)`);
        return;
      }}

      // 創建題目
      const item = form.addMultipleChoiceItem();
      item.setTitle(`第${{questionNumber}}題: ${{question.title}}`);
      item.setRequired(true);

      // 創建選項（標記正確答案）
      const choices = options.map(opt => {{
        const isCorrect = opt.key === correctAnswer;
        if (form.isQuiz()) {{
          // 測驗模式：標記正確答案並給分
          return item.createChoice(opt.value, isCorrect);
        }} else {{
          // 非測驗模式：僅創建選項
          return item.createChoice(opt.value);
        }}
      }});

      item.setChoices(choices);

      // 設定分數（測驗模式）
      if (form.isQuiz() && correctAnswer) {{
        item.setPoints(1);  // 每題1分
      }}

      // 添加題目分類和難度標籤
      let helpText = [];
      if (question.category && question.category !== '其他') {{
        helpText.push(`分類: ${{question.category}}`);
      }}
      if (question.difficulty) {{
        helpText.push(`難度: ${{question.difficulty}}`);
      }}
      if (question.isGroup) {{
        helpText.push('📚 題組題目');
      }}

      if (helpText.length > 0) {{
        item.setHelpText(helpText.join(' | '));
      }}

      addedCount++;

    }} catch (error) {{
      console.error(`❌ 第${{index + 1}}題添加失敗:`, error);
    }}
  }});

  return addedCount;
}}

// 執行主函數
function main() {{
  return createPracticeForm();
}}

// 測試函數（僅檢查資料結構不建立表單）
function testFormStructure() {{
  const questionsData = {questions_data};
  const answersData = {answers_data};

  console.log(`總題數: ${{questionsData.length}}`);
  console.log(`答案數: ${{Object.keys(answersData).length}}`);

  // 檢查每題的選項
  questionsData.forEach((q, i) => {{
    const qNum = i + 1;
    const opts = [q.optionA, q.optionB, q.optionC, q.optionD].filter(o => o && o.trim());
    console.log(`第${{qNum}}題: ${{opts.length}} 個選項, 答案: ${{answersData[qNum] || '無'}}`);
  }});
}}
"""

        return script_template

    def _generate_questions_data(self, df: pd.DataFrame) -> str:
        """生成題目資料JavaScript陣列"""
        questions = []

        for _, row in df.iterrows():
            # 安全獲取並轉換值
            question = {
                'title': self._safe_get_and_escape(row, '題目'),
                'optionA': self._safe_get_and_escape(row, '選項A'),
                'optionB': self._safe_get_and_escape(row, '選項B'),
                'optionC': self._safe_get_and_escape(row, '選項C'),
                'optionD': self._safe_get_and_escape(row, '選項D'),
                'category': str(row.get('分類', '其他')),
                'difficulty': str(row.get('難度', '簡單')),
                'isGroup': bool(row.get('題組', False))
            }
            questions.append(question)

        # 轉換為JavaScript陣列格式（使用JSON格式更安全）
        import json
        return json.dumps(questions, ensure_ascii=False, indent=2)

    def _generate_answers_data(self, df: pd.DataFrame) -> str:
        """生成答案資料JavaScript物件"""
        answers = {}

        for index, row in df.iterrows():
            question_number = index + 1
            # 優先使用最終答案，其次正確答案
            answer = str(row.get('最終答案', row.get('正確答案', '')))

            # 驗證答案格式
            if answer and answer.upper() in ['A', 'B', 'C', 'D']:
                answers[question_number] = answer.upper()
            else:
                self.logger.warning(f"第 {question_number} 題沒有有效答案: {answer}")

        # 轉換為JavaScript物件格式
        import json
        return json.dumps(answers, ensure_ascii=False, indent=2)

    def _safe_get_and_escape(self, row: pd.Series, column: str) -> str:
        """安全獲取並轉義字串值"""
        value = row.get(column, '')

        # 處理 NaN, None, 空值
        if pd.isna(value) or value is None:
            return ''

        # 轉換為字串並轉義
        text = str(value).strip()

        # 過濾明顯的無效值
        if text.lower() in ['nan', 'none', 'null', '']:
            return ''

        return self._escape_js_string(text)

    def _escape_js_string(self, text: str) -> str:
        """轉義JavaScript字串"""
        if not text:
            return ""

        # 轉義特殊字元
        text = text.replace('\\', '\\\\')  # 反斜線
        text = text.replace('"', '\\"')    # 雙引號
        text = text.replace('\n', '\\n')   # 換行
        text = text.replace('\r', '\\r')   # 回車
        text = text.replace('\t', '\\t')   # Tab
        text = text.replace("'", "\\'")    # 單引號（增加）

        return text
