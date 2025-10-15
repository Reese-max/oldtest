
/**
 * 考古題練習表單生成器
 * 自動從CSV資料建立Google表單
 */

function createPracticeForm() {
  // 表單設定
  const formTitle = "考古題練習";
  const formDescription = "此表單包含 5 題考古題，用於練習和自測。";
  
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
  const questions = [
    {
        "題號": "1",
        "題目": "下列各組「」內的字，讀音完全相同的選項是：",
        "題型": "選擇題",
        "選項A": "「緋」聞纏身／「誹」謗他人／「斐」然成章",
        "選項B": "「緋」聞纏身／「誹」謗他人／「斐」然成章",
        "選項C": "「緋」聞纏身／「誹」謗他人／「斐」然成章",
        "選項D": "「緋」聞纏身／「誹」謗他人／「斐」然成章",
        "分類": "語音",
        "難度": "簡單"
    },
    {
        "題號": "2",
        "題目": "下列文句，完全沒有錯別字的選項是：",
        "題型": "選擇題",
        "選項A": "他做事總是虎頭蛇尾，令人失望",
        "選項B": "他做事總是虎頭蛇尾，令人失望",
        "選項C": "他做事總是虎頭蛇尾，令人失望",
        "選項D": "他做事總是虎頭蛇尾，令人失望",
        "分類": "字形",
        "難度": "簡單"
    },
    {
        "題號": "3",
        "題目": "下列成語使用正確的選項是：",
        "題型": "選擇題",
        "選項A": "他對這個問題一竅不通，卻裝模作樣",
        "選項B": "他對這個問題一竅不通，卻裝模作樣",
        "選項C": "他對這個問題一竅不通，卻裝模作樣",
        "選項D": "他對這個問題一竅不通，卻裝模作樣",
        "分類": "成語",
        "難度": "簡單"
    },
    {
        "題號": "4",
        "題目": "下列句子中，修辭手法相同的選項是：",
        "題型": "選擇題",
        "選項A": "春風又綠江南岸，明月何時照我還",
        "選項B": "春風又綠江南岸，明月何時照我還",
        "選項C": "春風又綠江南岸，明月何時照我還",
        "選項D": "春風又綠江南岸，明月何時照我還",
        "分類": "修辭",
        "難度": "簡單"
    },
    {
        "題號": "5",
        "題目": "下列文句，語法完全正確的選項是：",
        "題型": "選擇題",
        "選項A": "由於天氣不好，所以我們取消了戶外活動",
        "選項B": "由於天氣不好，所以我們取消了戶外活動",
        "選項C": "由於天氣不好，所以我們取消了戶外活動",
        "選項D": "由於天氣不好，所以我們取消了戶外活動",
        "分類": "文法",
        "難度": "簡單"
    }
];
  
  questions.forEach((q, index) => {
    const questionText = "第" + q.題號 + "題: " + q.題目;
    
    if (q.題型 === "選擇題") {
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
    } else if (q.題型 === "問答題") {
      const item = form.addParagraphTextItem();
      item.setTitle(questionText);
      item.setRequired(true);
      item.setPoints(1);
    }
    
    // 添加題目分類標籤
    if (q.分類) {
      const section = form.addPageBreakItem();
      section.setTitle("分類: " + q.分類);
    }
  });
}

function addSubmitHandler(form) {
  // 建立觸發器，在提交後自動評分
  ScriptApp.newTrigger("gradeResponses")
    .forForm(form)
    .onFormSubmit()
    .create();
}

function gradeResponses(e) {
  const form = FormApp.getActiveForm();
  const responses = form.getResponses();
  const latestResponse = responses[responses.length - 1];
  
  // 計算分數
  const score = calculateScore(latestResponse);
  
  // 發送結果到試算表
  sendResultsToSheet(latestResponse, score);
}

function calculateScore(response) {
  // 正確答案對照表
  const correctAnswers = {
    "1": "B",
    "2": "A",
    "3": "C",
    "4": "A",
    "5": "D"
};
  
  let score = 0;
  let totalQuestions = 0;
  
  const itemResponses = response.getItemResponses();
  itemResponses.forEach(itemResponse => {
    const questionText = itemResponse.getItem().getTitle();
    const questionNumber = extractQuestionNumber(questionText);
    
    if (questionNumber && correctAnswers[questionNumber]) {
      totalQuestions++;
      const userAnswer = itemResponse.getResponse();
      const correctAnswer = correctAnswers[questionNumber];
      
      if (userAnswer === correctAnswer) {
        score++;
      }
    }
  });
  
  return {
    score: score,
    total: totalQuestions,
    percentage: Math.round((score / totalQuestions) * 100)
  };
}

function extractQuestionNumber(questionText) {
  const match = questionText.match(/第(\d+)題/);
  return match ? match[1] : null;
}

function sendResultsToSheet(response, score) {
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
}

function getOrCreateSheet(sheetName) {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  let sheet = ss.getSheetByName(sheetName);
  
  if (!sheet) {
    sheet = ss.insertSheet(sheetName);
    sheet.getRange(1, 1, 1, 6).setValues([
      ["時間", "使用者", "答對題數", "總題數", "正確率", "回應連結"]
    ]);
  }
  
  return sheet;
}

// 輔助函數：從CSV資料建立表單
function createFormFromCSV() {
  // 此函數需要手動匯入CSV資料
  // 或使用Google Apps Script的Drive API讀取CSV檔案
  console.log("請先匯入CSV資料到questions_data變數中");
}

// 執行主函數
function main() {
  return createPracticeForm();
}
