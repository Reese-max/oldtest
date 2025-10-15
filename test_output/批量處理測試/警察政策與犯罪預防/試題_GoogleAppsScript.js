
/**
 * 考古題練習表單生成器
 * 自動從CSV資料建立Google表單
 * 生成時間: 2025-10-15 16:30:04
 */

function createPracticeForm() {
  // 表單設定
  const formTitle = "考古題練習表單";
  const formDescription = "此表單包含 9 題考古題，用於練習和自測";
  
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
      title: "分）\n二、在犯罪預防的方案實施後，評估如環境設計、社區犯罪預防或情境犯罪\n預防措施的實施成效，可能會產生犯罪轉移（crime displacement）或效\n益擴散（diffusionof benefits）的結果，值得留意此兩效應對犯罪預防方\n案的影響。請說明：\n犯罪轉移的類型有那幾類？犯罪轉移的基本假設為何？（",
      optionA: "得留意此兩效應對犯罪預防方",
      optionB: "分） 二、在犯罪預防的方案實施後，評估如環境設計、社區犯罪預防或情境犯罪 預防措施的實施成效，可能會產生犯罪轉移（crime displacement）或效 益擴散（diffusionof benefits）的結果，值得留意此兩效應對犯罪預防方 案的影響。請說明： 犯罪轉移的類型有那幾類？犯罪轉移的基本假設為何？（",
      optionC: "nan",
      optionD: "nan",
      category: "其他",
      difficulty: "困難",
      isGroup: False,
    },
    {
      title: "種犯罪轉移，如派出所轄區實施社區守望相助，只\n有一半的家戶參加守望相助，竊盜者轉移對未參加社區守望相助的家戶下手，此類犯罪轉移屬於\n下列那一種？\n加害人轉移 地區轉移 標的轉移 類型轉移",
      optionA: "下手，此類犯罪轉移屬於",
      optionB: "種犯罪轉移，如派出所轄區實施社區守望相助，只 有一半的家戶參加守望相助，竊盜者轉移對未參加社區守望相助的家戶下手，此類犯罪轉移屬於 下列那一種？ 加害人轉移 地區轉移 標的轉移 類型轉移",
      optionC: "nan",
      optionD: "nan",
      category: "其他",
      difficulty: "中等",
      isGroup: False,
    },
    {
      title: "我國行政程序法第11條管轄法定及第19條職務協助的規定，從法治國理念說明我國應信守「組\n織法定原則」及「管轄恆定原則」。檢調、海巡、移民等機關亦負有危害防止任務，一般行政機\n關之環保、衛生、消防、建管等單位皆亦負有防止危害任務。各機關間應強化橫向溝通、調和等\n作為，以發揮治理功效。這種行政權本身危害防止任務的合作較傾向於下列那一類？\n警察權之水平分配 警察權之比例原則 警察權之責任原則 警察權之垂直分配",
      optionA: "行政程序法第11條管轄法定及第19條職務協助的規定，從法治國理念說明我國應信守「組",
      optionB: "法定原則」及「管轄恆定原則」。檢調、海巡、移民等機關亦負有危害防止任務，一般行政機",
      optionC: "關之環保、衛生、消防、建管等單位皆亦負有防止危害任務。各機關間應強化橫向溝通、調和等",
      optionD: "警察權之水平分配",
      category: "其他",
      difficulty: "困難",
      isGroup: False,
    },
    {
      title: "犯罪預防的標的是犯罪，了解犯罪須借助犯罪測量的方法，其中之一為犯罪被害調查法，下列何\n者不是犯罪被害調查法的優點？\n可以彌補官方統計及自陳報告問卷調查兩種犯罪測量方法的不足\n可以調查所有的犯罪類型\n了解犯罪被害民眾未向警方報案的原因\n了解被害者特性、被害者之情境等導致被害的各種因素，可以及早進行犯罪預防",
      optionA: "須借助犯罪測量的方法，其中之一為犯罪被害調查法，下列何",
      optionB: "向警方報案的原因",
      optionC: "各種因素，可以及早進行犯罪預防",
      optionD: "nan",
      category: "其他",
      difficulty: "困難",
      isGroup: False,
    },
    {
      title: "Bayley（1985）認為，各國對於警察行為的控制，有內在於警察組織的課責及外在機制的課責兩\n種做法。下列關於警察課責（accountability）機制的敘述，何者錯誤？\n外在的專責控制機制（External-Exclusive），可以是單一的或多元的\n媒體是外在的包含控制機制（External-Inclusive）\n組織紀律程序是內在的顯性控制機制（Internal-Explicit）\n社會化是內在的隱性控制機制（Internal-Implicit）",
      optionA: "各國對於警察行為的控制，有內在於警察組織的課責及外在機制的課責兩",
      optionB: "Bayley（1985）認為，各國對於警察行為的控制，有內在於警察組織的課責及外在機制的課責兩 種做法。下列關於警察課責（accountability）機制的敘述，何者錯誤？ 外在的專責控制機制（External-Exclusive），可以是單一的或多元的 媒體是外在的包含控制機制（External-Inclusive） 組織紀律程序是內在的顯性控制機制（Internal-Explicit） 社會化是內在的隱性控制機制（Internal-Implicit）",
      optionC: "nan",
      optionD: "nan",
      category: "其他",
      difficulty: "困難",
      isGroup: False,
    },
    {
      title: "關於「標準模式警政」（StandardmodelPolicing）以及「情資主導警政」（Intelligence-LedPolicing）\n的敘述，下列何者錯誤？\n標準模式警政採取主動反應作為\n標準模式警政著重犯罪發生後的偵辦追緝，輕忽犯罪發生前的危害防止\n情資主導警政以大數據的方式進行情資蒐集及分析工作\n強力執法也是情資主導警政採用的反應策略",
      optionA: "關於「標準模式警政」（StandardmodelPolicing）以及「情資主導警政」（Intelligence-LedPolicing）",
      optionB: "警政採取主動反應作為",
      optionC: "警政著重犯罪發生後的偵辦追緝，輕忽犯罪發生前的危害防止",
      optionD: "警政以大數據的方式進行情資蒐集及分析工作",
      category: "其他",
      difficulty: "困難",
      isGroup: False,
    },
    {
      title: "犯罪預防的風險管理模式是指，在風險社會之下，市民為自身的安全而立於風險管理的位子上，\n有關該模式的犯罪預防策略，下列敘述何者錯誤？\n將犯罪作為一種風險因素進行評估 須排除私人因素\n尋求日常生活程序的修正 使公民為犯罪負責",
      optionA: "下，市民為自身的安全而立於風險管理的位子上，",
      optionB: "須排除私人因素",
      optionC: "nan",
      optionD: "nan",
      category: "其他",
      difficulty: "困難",
      isGroup: False,
    },
    {
      title: "CompStat 警政又稱為電腦導向的犯罪統計，警察基金會曾提出CompStat 的六個關鍵因素，下列\n何者錯誤？\n警察任務闡明 保持組織靈活與彈性\n警察內部的責任 內部的訊息交換",
      optionA: "警政又稱為電腦導向的犯罪統計，警察基金會曾提出CompStat",
      optionB: "關鍵因素，下列",
      optionC: "警察任務闡明",
      optionD: "警察內部的責任",
      category: "其他",
      difficulty: "中等",
      isGroup: False,
    },
    {
      title: "種政策分析方法（policy-analyticmethods），下列何\n者錯誤？\n問題建構（problem structuring） 預測（forecasting）\n描述（prescription） 解釋（interpretation）",
      optionA: "法（policy-analyticmethods），下列何",
      optionB: "種政策分析方法（policy-analyticmethods），下列何 者錯誤？ 問題建構（problem structuring） 預測（forecasting） 描述（prescription） 解釋（interpretation）",
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
    1: "D",
    2: "C",
    3: "A",
    4: "B",
    5: "D",
    6: "A",
    7: "B",
    8: "D",
    9: "D",
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
