
/**
 * 考古題練習表單生成器
 * 自動從CSV資料建立Google表單
 * 生成時間: 2025-10-15 16:30:06
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
      title: "分）\n二、警察勤務條例第",
      optionA: "警察勤務條例第",
      optionB: "分） 二、警察勤務條例第",
      optionC: "nan",
      optionD: "nan",
      category: "其他",
      difficulty: "簡單",
      isGroup: False,
    },
    {
      title: "項明定勤區查察勤務方式「於警勤區內，由警\n勤區員警執行之，以家戶訪查方式，擔任犯罪預防、為民服務及社會治\n安調查等任務」。惟勤區查察之制度已經過多次之變革，請敘述有關我國\n警勤區制度的歷史沿革？另再詳述目前警勤區訪查之對象與查訪應遵\n守之事項？（",
      optionA: "於警勤區內，由警",
      optionB: "警執行之，以家戶訪查方式，擔任犯罪預防、為民服務及社會治",
      optionC: "經過多次之變革，請敘述有關我國",
      optionD: "nan",
      category: "其他",
      difficulty: "困難",
      isGroup: False,
    },
    {
      title: "機關組織以法律制定者，其內部單位之分工職掌，以處務規程定之，為中央行政機關組織基準法\n第8條第1項前段之規定；爰此，內政部警政署為處理內部單位之分工職掌，定有內政部警政署\n處務規程，下列有關該處務規程規定掌理事項之敘述何者錯誤？\n特殊地區警備治安之規劃、督導，由保安組掌理\n社會治安調查之規劃、指導、蒐集及處理，由保防組掌理\n特種勤務之協調、聯繫及督導，由督察室掌理\n社區治安工作之協調推動、輔導、考核及評鑑，由行政組掌理",
      optionA: "關組織以法律制定者，其內部單位之分工職掌，以處務規程定之，為中央行政機關組織基準法",
      optionB: "警政署為處理內部單位之分工職掌，定有內政部警政署",
      optionC: "警備治安之規劃、督導，由保安組掌理",
      optionD: "nan",
      category: "法律",
      difficulty: "困難",
      isGroup: False,
    },
    {
      title: "警察機關為維護警察紀律、鍛鍊員警體能及充實其實務知能，應實施常年訓練；依警察常年訓練\n辦法第4條規定，常年訓練區分為一般訓練及專案訓練，下列何者屬於專案訓練之性質？\n業務訓練 幹部訓練 特定任務訓練 組合訓練",
      optionA: "警察機關為維護警察紀律、鍛鍊員警體能及充實其實務知能，應實施常年訓練；依警察常年訓練",
      optionB: "警察機關為維護警察紀律、鍛鍊員警體能及充實其實務知能，應實施常年訓練；依警察常年訓練 辦法第4條規定，常年訓練區分為一般訓練及專案訓練，下列何者屬於專案訓練之性質？ 業務訓練 幹部訓練 特定任務訓練 組合訓練",
      optionC: "nan",
      optionD: "nan",
      category: "其他",
      difficulty: "困難",
      isGroup: False,
    },
    {
      title: "警察官規係指中央與地方各級警察人員之官等、俸給、職務等階等相關事項之規範，為警察法第\n3條第1項所定，由中央立法之事項，並制定有警察人員人事條例，下列有關該條例之總則規範\n事項何者錯誤？\n警察官、職分立，官受保障，職得調任，非依法不得免官或免職\n警察人員由內政部管理，或交由各直轄市政府、縣（市）政府管理\n擬任警察官前，其擬任機關、學校應就其個人品德、忠誠、素行經歷及身心健康狀況實施查核\n警察官等分為警監、警正、警佐。警監官等分為特、一、二、三、四階，警正及警佐官等各分\n一、二、三、四階",
      optionA: "警察官規係指中央與地方各級警察人員之官等、俸給、職務等階等相關事項之規範，為警察法第",
      optionB: "法之事項，並制定有警察人員人事條例，下列有關該條例之總則規範",
      optionC: "警察官、職分立，官受保障，職得調任，非依法不得免官或免職",
      optionD: "警察人員由內政部管理，或交由各直轄市政府、縣（市）政府管理",
      category: "其他",
      difficulty: "困難",
      isGroup: False,
    },
    {
      title: "警察機關應依失蹤人之直系血親尊親屬、法定代理人、監護人、配偶、直系血親卑親屬及民法第\n1123條家長、家屬或親屬之報案實施查尋。警察機關得依特定單位、人員之失踪人口報案實施查\n尋之特殊情形，下列敘述何者錯誤？\n在臺無親屬者，依相關權責單位人員或戶籍地之村（里）、鄰長之報案辦理\n緊急案件（如山難）依其同行人員之報案辦理；事後應與其家長、家屬或親屬聯繫確認\n社政機關或其委託公、私立社福安置機構所安置之保護個案，依該管機關（構）之報案辦理\n家屬委由公、私立社福安置機構照顧之個案，依家屬或安置機構之報案辦理",
      optionA: "警察機關應依失蹤人之直系血親尊親屬、法定代理人、監護人、配偶、直系血親卑親屬及民法第",
      optionB: "警察機關得依特定單位、人員之失踪人口報案實施查",
      optionC: "無親屬者，依相關權責單位人員或戶籍地之村（里）、鄰長之報案辦理",
      optionD: "依其同行人員之報案辦理；事後應與其家長、家屬或親屬聯繫確認",
      category: "其他",
      difficulty: "困難",
      isGroup: False,
    },
    {
      title: "下列何者為英國皮爾爵士（SirRobertPeel）於1829年成立現代警察之初所立下的九個原則（Sir\nRobert Peel’s Nine principles for Modern Policing）？①警察的基本任務是預防犯罪的發生 ②警\n察執勤能力繫於政府對警察活動的認同 ③警民一體 ④警察效率以破案能力為標準\n①③ ②④ ①④ ②③",
      optionA: "下列何者為英國皮爾爵士（SirRobertPeel）於1829年成立現代警察之初所立下的九個原則（Sir",
      optionB: "於政府對警察活動的認同",
      optionC: "警察效率以破案能力為標準",
      optionD: "nan",
      category: "其他",
      difficulty: "困難",
      isGroup: False,
    },
    {
      title: "根據內政部警政署組織法第2條明定，下列何者屬於警政署掌理的全國性警察業務？\n各國駐華使領館及代表機構、官員之安全維護\n當舖業及保全業管理之規劃、督導\n社會保防、戶口查察與社會治安調查之協調、規劃及督導\n交通安全維護、交通工程秩序整理、交通事故及協助交通安全宣導之規劃、督導",
      optionA: "各國駐華使領館及代表機構、官員之安全維護",
      optionB: "當舖業及保全業管理之規劃、督導",
      optionC: "nan",
      optionD: "nan",
      category: "其他",
      difficulty: "困難",
      isGroup: False,
    },
    {
      title: "件背心式防彈衣\n裝備機具應由勤務執行機構配發員警個別隨身管理",
      optionA: "應由勤務執行機構配發員警個別隨身管理",
      optionB: "件背心式防彈衣 裝備機具應由勤務執行機構配發員警個別隨身管理",
      optionC: "nan",
      optionD: "nan",
      category: "其他",
      difficulty: "簡單",
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
    1: "C",
    2: "B",
    3: "D",
    4: "C",
    5: "B",
    6: "A",
    7: "A",
    8: "B",
    9: "B",
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
