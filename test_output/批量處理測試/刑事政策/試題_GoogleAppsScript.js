
/**
 * 考古題練習表單生成器
 * 自動從CSV資料建立Google表單
 * 生成時間: 2025-10-15 16:30:09
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
      title: "條通姦罪之法律規定：「有\n配偶而與人通姦者，處一年以下有期徒刑。其相姦者亦同」，已然違反憲\n法。試問，該號解釋用以判定通姦罪違憲的憲法原則為何？其如何應用\n該憲法原則審查通姦罪之合憲性？（",
      optionA: "法律規定：「有",
      optionB: "偶而與人通姦者，處一年以下有期徒刑。其相姦者亦同」，已然違反憲",
      optionC: "nan",
      optionD: "nan",
      category: "法律",
      difficulty: "中等",
      isGroup: False,
    },
    {
      title: "年）及對 B 犯無故拍攝性影\n像罪（法定刑",
      optionA: "無故拍攝性影",
      optionB: "年）及對 B 犯無故拍攝性影 像罪（法定刑",
      optionC: "nan",
      optionD: "nan",
      category: "其他",
      difficulty: "簡單",
      isGroup: False,
    },
    {
      title: "年以下），兩罪均於同一刑事程序經檢察官起訴，並由臺\n北地方法院合併審理。臺北地方法院並就前罪宣告五年有期徒刑，後罪\n宣告三個月有期徒刑並得以 1,",
      optionA: "下），兩罪均於同一刑事程序經檢察官起訴，並由臺",
      optionB: "法院合併審理。臺北地方法院並就前罪宣告五年有期徒刑，後罪",
      optionC: "nan",
      optionD: "nan",
      category: "其他",
      difficulty: "中等",
      isGroup: False,
    },
    {
      title: "日而易科罰金。試問臺北地\n方法院就上述兩罪，得否於同判決中，依刑法第",
      optionA: "法院就上述兩罪，得否於同判決中，依刑法第",
      optionB: "日而易科罰金。試問臺北地 方法院就上述兩罪，得否於同判決中，依刑法第",
      optionC: "nan",
      optionD: "nan",
      category: "其他",
      difficulty: "簡單",
      isGroup: False,
    },
    {
      title: "分）\n四、毒品犯罪危害社會嚴重，近期在刑事政策上有主張必須引入美國法制之\n「毒品法庭」，以作為解決毒品問題之法律架構，試說明「毒品法庭」之\n概念，並分析其制度之優、缺點。（",
      optionA: "須引入美國法制之",
      optionB: "法庭」，以作為解決毒品問題之法律架構，試說明「毒品法庭」之",
      optionC: "nan",
      optionD: "nan",
      category: "法律",
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
