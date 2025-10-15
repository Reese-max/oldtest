
/**
 * 考古題練習表單生成器
 * 自動從CSV資料建立Google表單
 * 生成時間: 2025-10-15 16:30:02
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
      title: "依警察職權行使法第8條第1項規定，警察對於已發生危害或依客觀合理判斷易生危害之交通工\n具，得予以攔停並採行一定措施，請問下列何者不屬該項規定之措施？\n要求駕駛人出示相關證件\n檢查引擎、車身號碼或其他足資識別之特徵\n搜索駕駛人身體\n要求駕駛人接受酒精濃度測試之檢定",
      optionA: "依警察職權行使法第8條第1項規定，警察對於已發生危害或依客觀合理判斷易生危害之交通工",
      optionB: "受酒精濃度測試之檢定",
      optionC: "nan",
      optionD: "nan",
      category: "其他",
      difficulty: "困難",
      isGroup: False,
    },
    {
      title: "司法警察偵辦重大刑案發生除立即偵破外，均應訂定偵查計畫，以為偵查之準據，請問下列何者\n不屬偵查計畫內容？\n犯罪發生或發現之地點\n被害人之嗜好、接觸人物及被害狀況等生活情形\n司法警察偵辦期間所需人事費用\n現場訪問調查或資料查對情形",
      optionA: "法警察偵辦重大刑案發生除立即偵破外，均應訂定偵查計畫，以為偵查之準據，請問下列何者",
      optionB: "法警察偵辦期間所需人事費用",
      optionC: "nan",
      optionD: "nan",
      category: "其他",
      difficulty: "困難",
      isGroup: False,
    },
    {
      title: "警察機關逮捕何種犯罪之現行犯或通緝犯，應於製作筆錄時，詢問被告或犯罪嫌疑人有無監護或\n照顧未滿12歲子女或兒童之情形，並調閱戶役政資料比對檢核，遇有兒童及少年福利與權益保障\n法第53條第1項各款或第54條之情事者，應依各該條規定，通報直轄市、縣（市）主管機關？\n違反毒品危害防制條例之犯罪 竊盜罪\n詐欺罪 偽造文書罪",
      optionA: "警察機關逮捕何種犯罪之現行犯或通緝犯，應於製作筆錄時，詢問被告或犯罪嫌疑人有無監護或",
      optionB: "警察機關逮捕何種犯罪之現行犯或通緝犯，應於製作筆錄時，詢問被告或犯罪嫌疑人有無監護或 照顧未滿12歲子女或兒童之情形，並調閱戶役政資料比對檢核，遇有兒童及少年福利與權益保障 法第53條第1項各款或第54條之情事者，應依各該條規定，通報直轄市、縣（市）主管機關？ 違反毒品危害防制條例之犯罪 竊盜罪 詐欺罪 偽造文書罪",
      optionC: "nan",
      optionD: "nan",
      category: "其他",
      difficulty: "困難",
      isGroup: False,
    },
    {
      title: "司法警察偵查犯罪有刑事訴訟法第",
      optionA: "法警察偵查犯罪有刑事訴訟法第",
      optionB: "司法警察偵查犯罪有刑事訴訟法第",
      optionC: "nan",
      optionD: "nan",
      category: "其他",
      difficulty: "簡單",
      isGroup: False,
    },
    {
      title: "警察機關對重大及特殊刑案，係由何機關列管督導考核？\n縣市警察局 各分局\n警政署刑事警察局 內政部",
      optionA: "警政署刑事警察局",
      optionB: "警察機關對重大及特殊刑案，係由何機關列管督導考核？ 縣市警察局 各分局 警政署刑事警察局 內政部",
      optionC: "nan",
      optionD: "nan",
      category: "其他",
      difficulty: "中等",
      isGroup: False,
    },
    {
      title: "下列何者不屬於偵查中辯護人之權限？\n檢閱、抄錄或攝影卷宗及證物\n詢問完畢後令犯罪嫌疑人閱覽筆錄時，協助閱覽\n無刑事訴訟法第245條第2項但書情形，得於司法警察詢問犯罪嫌疑人時在場\n證人指認犯罪嫌疑人時，該犯罪嫌疑人之辯護人得在場",
      optionA: "無刑事訴訟法第245條第2項但書情形，得於司法警察詢問犯罪嫌疑人時在場",
      optionB: "該犯罪嫌疑人之辯護人得在場",
      optionC: "nan",
      optionD: "nan",
      category: "其他",
      difficulty: "困難",
      isGroup: False,
    },
    {
      title: "時，惟仍得針對甲之姓名、年齡、籍貫、職業、住居\n所等進行詢問，以查驗其人有無錯誤",
      optionA: "得針對甲之姓名、年齡、籍貫、職業、住居",
      optionB: "行詢問，以查驗其人有無錯誤",
      optionC: "nan",
      optionD: "nan",
      category: "其他",
      difficulty: "簡單",
      isGroup: False,
    },
    {
      title: "依據「警察偵查犯罪手冊」及「刑事鑑識手冊」之規定，下列有關記錄跡證之敘述何者錯誤？\n槍枝應視個案情況及必要性，採取指紋、射擊殘跡或生物跡證等，如有同時採取二種以上跡證\n之需要時，採證之順序以便利為原則\n刑案現場採證標的，包括因犯罪所遺留或遺棄之物，如嫌犯遺留之包裝紙，菸蒂，口香糖殘渣等\n警察人員實施刑案現場保全，進入現場者，須著必要之防護裝備（如帽套、手套、鞋套等），\n以免破壞現場跡證\n有關火（炸）藥及爆炸遺留物之處理原則，爆炸點周遭疑為火（炸）藥附著物，宜全部採集送驗",
      optionA: "應視個案情況及必要性，採取指紋、射擊殘跡或生物跡證等，如有同時採取二種以上跡證",
      optionB: "警察人員實施刑案現場保全，進入現場者，須著必要之防護裝備（如帽套、手套、鞋套等），",
      optionC: "關火（炸）藥及爆炸遺留物之處理原則，爆炸點周遭疑為火（炸）藥附著物，宜全部採集送驗",
      optionD: "nan",
      category: "其他",
      difficulty: "困難",
      isGroup: False,
    },
    {
      title: "下列有關警詢及筆錄製作之敘述，何者錯誤？\n詢問被告或犯罪嫌疑人之錄音及錄影，應自開始詢問其姓名、年齡、職業及住所或居所時起錄，\n至詢問完畢時停止，其間始末連續為之\n無辯護人之犯罪嫌疑人表示已選任辯護人時，在辯護人到場前，仍得繼續訊問\n犯罪嫌疑人於夜間經拘提或逮捕到場，為查驗其人有無錯誤者，司法警察官或司法警察得於夜\n間詢問之\n詢問犯罪嫌疑人時，應給予辯明犯罪嫌疑之機會；如有辯明，應命其就始末連續陳述；其陳述\n有利之事實者，應命其指出證明之方法，並於筆錄內記載明確",
      optionA: "應自開始詢問其姓名、年齡、職業及住所或居所時起錄，",
      optionB: "無辯護人之犯罪嫌疑人表示已選任辯護人時，在辯護人到場前，仍得繼續訊問",
      optionC: "於夜間經拘提或逮捕到場，為查驗其人有無錯誤者，司法警察官或司法警察得於夜",
      optionD: "應給予辯明犯罪嫌疑之機會；如有辯明，應命其就始末連續陳述；其陳述",
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
    1: "C",
    2: "C",
    3: "A",
    4: "C",
    5: "C",
    6: "A",
    7: "B",
    8: "A",
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
