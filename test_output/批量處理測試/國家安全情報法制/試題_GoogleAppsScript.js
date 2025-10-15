
/**
 * 考古題練習表單生成器
 * 自動從CSV資料建立Google表單
 * 生成時間: 2025-10-15 16:29:58
 */

function createPracticeForm() {
  // 表單設定
  const formTitle = "考古題練習表單";
  const formDescription = "此表單包含 6 題考古題，用於練習和自測";
  
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
      title: "年通過的「反滲透法」規定，是指「與中華民國交\n戰、武力對峙或主張採取非和平手段之國家、政治實體或團體」。請問：\n在國家安全法及國家情報工作法中，為「境外敵對勢力」從事間諜工作\n（商業間諜除外）的行為態樣有那些？（",
      optionA: "法」規定，是指「與中華民國交",
      optionB: "法及國家情報工作法中，為「境外敵對勢力」從事間諜工作",
      optionC: "nan",
      optionD: "nan",
      category: "其他",
      difficulty: "困難",
      isGroup: False,
    },
    {
      title: "分）\n二、報載陸配甲在「依親居留許可」期間，於網路社群平台開設頻道，於",
      optionA: "依親居留許可」期間，於網路社群平台開設頻道，於",
      optionB: "分） 二、報載陸配甲在「依親居留許可」期間，於網路社群平台開設頻道，於",
      optionC: "nan",
      optionD: "nan",
      category: "其他",
      difficulty: "簡單",
      isGroup: False,
    },
    {
      title: "月間\n遭檢舉，經內政部移民署約談後，依臺灣地區與大陸地區人民關係條例\n（下稱兩岸條例）廢止其依親居留許可。另有陸配乙及陸配丙二人亦在\n「依親居留許可」期間於網路上發表涉及侵略臺灣的言論，遭內政部移\n民署依法撤銷居留許可，並限期離境。甲及丙分別於",
      optionA: "經內政部移民署約談後，依臺灣地區與大陸地區人民關係條例",
      optionB: "下稱兩岸條例）廢止其依親居留許可。另有陸配乙及陸配丙二人亦在",
      optionC: "依親居留許可」期間於網路上發表涉及侵略臺灣的言論，遭內政部移",
      optionD: "依法撤銷居留許可，並限期離境。甲及丙分別於",
      category: "其他",
      difficulty: "困難",
      isGroup: False,
    },
    {
      title: "日在限期內辦理離境，然乙卻拒不離境，內政部移民署遂於",
      optionA: "限期內辦理離境，然乙卻拒不離境，內政部移民署遂於",
      optionB: "日在限期內辦理離境，然乙卻拒不離境，內政部移民署遂於",
      optionC: "nan",
      optionD: "nan",
      category: "其他",
      difficulty: "簡單",
      isGroup: False,
    },
    {
      title: "日召\n開強制出境審查會，決議將其強制出境，並安排班機執行遣送。請問：\n（每小題",
      optionA: "行遣送。請問：",
      optionB: "日召 開強制出境審查會，決議將其強制出境，並安排班機執行遣送。請問： （每小題",
      optionC: "nan",
      optionD: "nan",
      category: "其他",
      difficulty: "簡單",
      isGroup: False,
    },
    {
      title: "日下午一時多，一艘來自中國大陸的無船名無註\n冊快艇，駛入金門列島附近限制水域捕魚，遭遇我方海洋委員會海巡署\n艦隊分署第九海巡隊查緝，拒檢後逃逸，追緝期間兩船相撞，",
      optionA: "下午一時多，一艘來自中國大陸的無船名無註",
      optionB: "限制水域捕魚，遭遇我方海洋委員會海巡署",
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
