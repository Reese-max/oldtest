
/**
 * 考古題練習表單生成器
 * 自動從CSV資料建立Google表單
 * 生成時間: 2025-10-15 16:30:07
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
      title: "分）\n二、在犯罪防治的實務工作上，相關人員常常要面對嶄新或複雜多元的犯罪\n型態，形成重大的犯罪防治挑戰。研究人員必須根據犯罪事件的特性，\n思索可能的切入觀點，並據以形成假設；接著再蒐集相關具代表性的實\n證資料，用以驗證特定切入觀點所形成之假設的準確與否，最後推論出\n可能的問題解答。假設根據警政署的今年度汽車車禍案件數，與往年相\n較，有顯著上升之趨勢。（每小題",
      optionA: "關人員常常要面對嶄新或複雜多元的犯罪",
      optionB: "須根據犯罪事件的特性，",
      optionC: "關具代表性的實",
      optionD: "警政署的今年度汽車車禍案件數，與往年相",
      category: "其他",
      difficulty: "困難",
      isGroup: False,
    },
    {
      title: "分）\n四、近來，犯罪分析的理論觀點，益發多元，與社會科學研究的趨勢一致，\n強調更以整合性的角度，研究分析犯罪行為。尤其在青少年偏差行為的\n研究上，生命歷程分析（Life CourseAnalysis）更成為主流觀點。試以生\n命歷程觀點的重要概念，Locationin time andplace、Linked lives、Human\nAgency 及 Timing of lives，說明如何分析青少年的偏差行為發展過程？\n（",
      optionA: "行為。尤其在青少年偏差行為的",
      optionB: "分） 四、近來，犯罪分析的理論觀點，益發多元，與社會科學研究的趨勢一致， 強調更以整合性的角度，研究分析犯罪行為。尤其在青少年偏差行為的 研究上，生命歷程分析（Life CourseAnalysis）更成為主流觀點。試以生 命歷程觀點的重要概念，Locationin time andplace、Linked lives、Human Agency 及 Timing of lives，說明如何分析青少年的偏差行為發展過程？ （",
      optionC: "nan",
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
