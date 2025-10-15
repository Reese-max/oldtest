
/**
 * 考古題練習表單生成器
 * 自動從CSV資料建立Google表單
 * 生成時間: 2025-10-15 16:30:10
 */

function createPracticeForm() {
  // 表單設定
  const formTitle = "考古題練習表單";
  const formDescription = "此表單包含 3 題考古題，用於練習和自測";
  
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
      title: "分）\n三、精神障礙者可能因特定因素而犯下暴力犯罪，請提出相關犯罪理論來說\n明精神障礙者的暴力犯罪成因，根據刑法第",
      optionA: "下暴力犯罪，請提出相關犯罪理論來說",
      optionB: "分） 三、精神障礙者可能因特定因素而犯下暴力犯罪，請提出相關犯罪理論來說 明精神障礙者的暴力犯罪成因，根據刑法第",
      optionC: "nan",
      optionD: "nan",
      category: "其他",
      difficulty: "中等",
      isGroup: False,
    },
    {
      title: "條規定，對於精\n神障礙犯罪者可處以監護處分，請說明我國對於精神障礙犯罪者的監護\n處分之犯罪預防學理。（",
      optionA: "於精神障礙犯罪者的監護",
      optionB: "條規定，對於精 神障礙犯罪者可處以監護處分，請說明我國對於精神障礙犯罪者的監護 處分之犯罪預防學理。（",
      optionC: "nan",
      optionD: "nan",
      category: "其他",
      difficulty: "中等",
      isGroup: False,
    },
    {
      title: "分）\n四、藥物濫用者的再犯風險評估已從傳統的臨床判斷模式發展至今日的整\n合性風險評估工具。請說明藥物濫用者再犯風險評估的主要面向與核心\n指標，並說明我國再犯風險評估在社區處遇中的應用實務。（",
      optionA: "應用實務。（",
      optionB: "分） 四、藥物濫用者的再犯風險評估已從傳統的臨床判斷模式發展至今日的整 合性風險評估工具。請說明藥物濫用者再犯風險評估的主要面向與核心 指標，並說明我國再犯風險評估在社區處遇中的應用實務。（",
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
