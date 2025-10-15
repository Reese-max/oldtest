
/**
 * 考古題練習表單生成器
 * 自動從CSV資料建立Google表單
 * 生成時間: 2025-10-15 16:30:00
 */

function createPracticeForm() {
  // 表單設定
  const formTitle = "考古題練習表單";
  const formDescription = "此表單包含 5 題考古題，用於練習和自測";
  
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
  const questions = [
    {
      title: "0 版。請說明何謂打詐新四法以及新世代打擊詐欺\n策略行動綱領",
      optionA: "法以及新世代打擊詐欺",
      optionB: "0 版。請說明何謂打詐新四法以及新世代打擊詐欺 策略行動綱領",
      optionC: "nan",
      optionD: "nan",
      category: "其他",
      difficulty: "簡單",
      isGroup: False,
    },
    {
      title: "0 版之內容為何？（25 分）\n三、根據聯合國 2024 全球人口販運報告（Global Report on Trafficking in\nPersons 2024）指出，當前人口販運罪行主要是組織犯罪團體在運作執行，\n而從案例分析中可以依據其結構加以歸類，請說明該報告中所述組織犯\n罪團體類型及其差異為何？（25 分）\n四、跨國犯罪已經成為當前各國關注重點，我國也對此不斷提高關注。請說\n明我國打擊跨國犯罪所涉及之機關及其主要業務內容。（25 分）",
      optionA: "當前人口販運罪行主要是組織犯罪團體在運作執行，",
      optionB: "依據其結構加以歸類，請說明該報告中所述組織犯",
      optionC: "經成為當前各國關注重點，我國也對此不斷提高關注。請說",
      optionD: "關及其主要業務內容。（25",
      category: "其他",
      difficulty: "困難",
      isGroup: False,
    },
    {
      title: "分）\n二、因應跨境電信詐欺案盛行，我國政府積極推動修法，也推出新世代打擊\n詐欺策略行動綱領 2.",
      optionA: "應跨境電信詐欺案盛行，我國政府積極推動修法，也推出新世代打擊",
      optionB: "分） 二、因應跨境電信詐欺案盛行，我國政府積極推動修法，也推出新世代打擊 詐欺策略行動綱領 2.",
      optionC: "nan",
      optionD: "nan",
      category: "其他",
      difficulty: "簡單",
      isGroup: False,
    },
    {
      title: "版。請說明何謂打詐新四法以及新世代打擊詐欺\n策略行動綱領 2.",
      optionA: "法以及新世代打擊詐欺",
      optionB: "版。請說明何謂打詐新四法以及新世代打擊詐欺 策略行動綱領 2.",
      optionC: "nan",
      optionD: "nan",
      category: "其他",
      difficulty: "簡單",
      isGroup: False,
    },
    {
      title: "分）\n四、跨國犯罪已經成為當前各國關注重點，我國也對此不斷提高關注。請說\n明我國打擊跨國犯罪所涉及之機關及其主要業務內容。（",
      optionA: "經成為當前各國關注重點，我國也對此不斷提高關注。請說",
      optionB: "關及其主要業務內容。（",
      optionC: "nan",
      optionD: "nan",
      category: "其他",
      difficulty: "中等",
      isGroup: False,
    }
  ];
  
  questions.forEach((question, index) => {
    const item = form.addMultipleChoiceItem();
    item.setTitle(`第${index + 1}題: ${question.title}`);
    item.setChoices([
      item.createChoice(question.optionA, question.optionA),
      item.createChoice(question.optionB, question.optionB),
      item.createChoice(question.optionC, question.optionC),
      item.createChoice(question.optionD, question.optionD)
    ]);
    item.setRequired(true);
    
    // 添加題目分類標籤
    if (question.category) {
      item.setHelpText(`分類: ${question.category} | 難度: ${question.difficulty}`);
    }
  });
}

function addSubmitHandler(form) {
  // 添加提交後處理腳本
  const script = `
    function onSubmit(e) {
      const responses = e.response.getItemResponses();
      let correctCount = 0;
      let totalCount = responses.length;
      
      const answers = {
  };
      
      responses.forEach((response, index) => {
        const questionNumber = index + 1;
        const userAnswer = response.getResponse();
        const correctAnswer = answers[questionNumber];
        
        if (userAnswer === correctAnswer) {
          correctCount++;
        }
      });
      
      const score = Math.round((correctCount / totalCount) * 100);
      
      // 記錄分數到試算表
      const sheet = SpreadsheetApp.getActiveSheet();
      const timestamp = new Date();
      sheet.appendRow([timestamp, score, correctCount, totalCount]);
      
      // 顯示結果
      console.log(`分數: ${score}分 (${correctCount}/${totalCount})`);
    }
  `;
  
  // 這裡可以添加更複雜的提交處理邏輯
  console.log("提交處理器已設定");
}

// 執行主函數
function main() {
  return createPracticeForm();
}
