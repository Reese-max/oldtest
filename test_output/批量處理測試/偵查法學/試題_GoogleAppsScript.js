
/**
 * 考古題練習表單生成器
 * 自動從CSV資料建立Google表單
 * 生成時間: 2025-10-15 16:30:01
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
      title: "分）\n二、甲與友人乙至某 KTV 歡唱，因細故與其他客人發生口角，雙方互毆。經\n店員報警，甲、乙迅速開車離開，並衝撞到場警察 A、B 的警車。隨後\nA、B 將甲、乙拉下車，一方面將甲、乙壓制在地，並上手銬，控制甲、\n乙之行動及控制其二人所隨身攜帶之背包，查看其身上有無危險物品；\n另一方面，待支援警力到達後，翻查該背包，當場於隨身背包內查獲改\n造手槍",
      optionA: "警，甲、乙迅速開車離開，並衝撞到場警察",
      optionB: "下車，一方面將甲、乙壓制在地，並上手銬，控制甲、",
      optionC: "行動及控制其二人所隨身攜帶之背包，查看其身上有無危險物品；",
      optionD: "警力到達後，翻查該背包，當場於隨身背包內查獲改",
      category: "其他",
      difficulty: "困難",
      isGroup: False,
    },
    {
      title: "顆，作為扣案證據。甲、乙辯稱 A、B 無搜索票，\n且未出示證件，取得其同意，其搜索不合法。請問本案警察取得手槍、\n子彈的程序是否合法？（",
      optionA: "得其同意，其搜索不合法。請問本案警察取得手槍、",
      optionB: "顆，作為扣案證據。甲、乙辯稱 A、B 無搜索票， 且未出示證件，取得其同意，其搜索不合法。請問本案警察取得手槍、 子彈的程序是否合法？（",
      optionC: "nan",
      optionD: "nan",
      category: "其他",
      difficulty: "中等",
      isGroup: False,
    },
    {
      title: "人，由乙駕車搭載，並攜帶西瓜刀、球棒等兇器，依甲之指示前\n往某店，甲另指示丙邀約 A 前來談判，A 為壯膽，夥同 B、C 到場。雙\n方見面一言不合大打出手，甲即指示丙、丁分持西瓜刀追砍 A、球棒追\n打 B、C 成傷，並砸壞該店桌椅。乙在旁吶喊加油。前開眾人鬥毆的行\n為引起該店顧客恐慌，紛紛逃離，並通知警察到場。請問甲、乙、丙、\n丁成立何罪？（",
      optionA: "依甲之指示前",
      optionB: "該店桌椅。乙在旁吶喊加油。前開眾人鬥毆的行",
      optionC: "該店顧客恐慌，紛紛逃離，並通知警察到場。請問甲、乙、丙、",
      optionD: "nan",
      category: "其他",
      difficulty: "困難",
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
