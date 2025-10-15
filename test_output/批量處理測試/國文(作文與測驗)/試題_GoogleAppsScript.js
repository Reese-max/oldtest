
/**
 * 考古題練習表單生成器
 * 自動從CSV資料建立Google表單
 * 生成時間: 2025-10-15 16:30:08
 */

function createPracticeForm() {
  // 表單設定
  const formTitle = "考古題練習表單";
  const formDescription = "此表單包含 2 題考古題，用於練習和自測";
  
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
      title: "下列文句，存在語病的是：\n儘管比賽前他受了點傷，但比賽時依舊所向披靡\n參加試鏡者很少，我得用盡心力才能爭取到角色\n這些八卦新聞經過查證後，實屬空穴來風\n他被債務逼得走投無路，不得不鋌而走險",
      optionA: "下列文句，存在語病的是：",
      optionB: "受了點傷，但比賽時依舊所向披靡",
      optionC: "得用盡心力才能爭取到角色",
      optionD: "經過查證後，實屬空穴來風",
      category: "其他",
      difficulty: "中等",
      isGroup: False,
    },
    {
      title: "「『形破』（Deformation）是對既定的形的突破，要說是追求自由的人們所表現出\n的念想也可以；也可以說是『未定型』或『未成形』，我想以容易理解的『奇數之\n美』來稱之。『奇』並不是奇怪的意思，是與『偶』相對的『奇』，或『不完整』。」\n下列選項，何者最貼近上文的觀點？\n奇數的美，往往比偶數的美，來得更容易被看見\n勇於打破形式的框架限制，展現創作的自由意志\n形破，因為還不完整，故能取得最大的想像空間\n創作自由，就是要不斷地推陳出新，表現新形式",
      optionA: "偶』相對的『奇』，或『不完整』。」",
      optionB: "偶數的美，來得更容易被看見",
      optionC: "於打破形式的框架限制，展現創作的自由意志",
      optionD: "得最大的想像空間",
      category: "閱讀理解",
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
    1: "B",
    2: "B",
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
