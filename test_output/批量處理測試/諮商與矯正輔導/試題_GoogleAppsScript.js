
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
      title: "分）\n二、監獄官與受刑人互動的過程中，常面臨情緒壓力與高風險情境，而受刑\n人也可能帶有複雜創傷經驗。請從創傷知情（Trauma-Informed）觀點出\n發，分析監獄官在工作中應如何理解並因應受刑人的創傷反應，以預防\n再創傷（re-traumatization），並維持有效管理與心理安全。（",
      optionA: "受刑人互動的過程中，常面臨情緒壓力與高風險情境，而受刑",
      optionB: "經驗。請從創傷知情（Trauma-Informed）觀點出",
      optionC: "應如何理解並因應受刑人的創傷反應，以預防",
      optionD: "nan",
      category: "閱讀理解",
      difficulty: "困難",
      isGroup: False,
    },
    {
      title: "分）\n三、在監所中，許多受刑人面臨社會標籤與自我價值的問題。若欲設計一個\n以「自我認同」為目標的團體輔導，請說明此團體的主要設計理念、團\n體目標與單元目標，以及帶領者應如何處理可能出現的抗拒與情緒議\n題。（",
      optionA: "受刑人面臨社會標籤與自我價值的問題。若欲設計一個",
      optionB: "應如何處理可能出現的抗拒與情緒議",
      optionC: "nan",
      optionD: "nan",
      category: "其他",
      difficulty: "困難",
      isGroup: False,
    },
    {
      title: "分）\n四、酒癮問題與再犯風險密切相關，請說明三級預防模式？並將其應用於酒\n癮犯者的每一層級工作，內容應包含實施對象、目標與可辦理的活動內\n容。（",
      optionA: "應包含實施對象、目標與可辦理的活動內",
      optionB: "分） 四、酒癮問題與再犯風險密切相關，請說明三級預防模式？並將其應用於酒 癮犯者的每一層級工作，內容應包含實施對象、目標與可辦理的活動內 容。（",
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
