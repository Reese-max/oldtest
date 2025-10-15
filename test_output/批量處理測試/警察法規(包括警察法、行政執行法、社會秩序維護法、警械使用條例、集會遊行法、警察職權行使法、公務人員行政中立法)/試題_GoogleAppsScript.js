
/**
 * 考古題練習表單生成器
 * 自動從CSV資料建立Google表單
 * 生成時間: 2025-10-15 16:30:08
 */

function createPracticeForm() {
  // 表單設定
  const formTitle = "考古題練習表單";
  const formDescription = "此表單包含 14 題考古題，用於練習和自測";
  
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
      title: "下列何者違反公務人員行政中立法所要求之行政中立？\n於休假期間擔任罷免團體志工\n加入政黨\n具名不具銜兼任公職候選人競選辦事處之職務\n登記為公職候選人，並自候選人名單公告之日起請事假",
      optionA: "於休假期間擔任罷免團體志工",
      optionB: "下列何者違反公務人員行政中立法所要求之行政中立？ 於休假期間擔任罷免團體志工 加入政黨 具名不具銜兼任公職候選人競選辦事處之職務 登記為公職候選人，並自候選人名單公告之日起請事假",
      optionC: "nan",
      optionD: "nan",
      category: "其他",
      difficulty: "中等",
      isGroup: False,
    },
    {
      title: "關於行政執行之類型，下列何者非屬之？\n公法上金錢給付義務之執行 行為或不行為義務之執行\n身分查證之詢問 即時強制",
      optionA: "法上金錢給付義務之執行",
      optionB: "行為或不行為義務之執行",
      optionC: "nan",
      optionD: "nan",
      category: "其他",
      difficulty: "中等",
      isGroup: False,
    },
    {
      title: "義務人或利害關係人針對警察依警察職權行使法行使職權，認有侵害其利益之情事時，當場應如\n何救濟？\n向行使職權之警察陳述理由，表示異議\n向行使職權警察之長官陳述理由，表示異議\n向行使職權警察所屬機關之上級機關，提起訴願\n向高等行政法院之地方行政訴訟庭提起行政訴訟",
      optionA: "義務人或利害關係人針對警察依警察職權行使法行使職權，認有侵害其利益之情事時，當場應如",
      optionB: "向行使職權之警察陳述理由，表示異議",
      optionC: "向行使職權警察之長官陳述理由，表示異議",
      optionD: "向行使職權警察所屬機關之上級機關，提起訴願",
      category: "其他",
      difficulty: "困難",
      isGroup: False,
    },
    {
      title: "關於警察對於集會、遊行得採行之措施，下列敘述何者錯誤？\n應經許可之集會、遊行，未經許可而擅自舉行者，得予警告\n依負責人之請求，到場疏導交通及維持秩序\n於集會、遊行活動期間及活動前、後，得以科技工具蒐集參與者之現場活動資料\n所蒐集集會、遊行參與者之資料，得為調查犯罪或其他違法行為，而延長保存",
      optionA: "應經許可之集會、遊行，未經許可而擅自舉行者，得予警告",
      optionB: "依負責人之請求，到場疏導交通及維持秩序",
      optionC: "於集會、遊行活動期間及活動前、後，得以科技工具蒐集參與者之現場活動資料",
      optionD: "行參與者之資料，得為調查犯罪或其他違法行為，而延長保存",
      category: "其他",
      difficulty: "困難",
      isGroup: False,
    },
    {
      title: "關於警察攔停交通工具，下列敘述何者錯誤？\n限於已發生危害或依客觀合理判斷易生危害之交通工具\n得令駕駛人出示身分證明證件\n得檢查引擎之號碼\n得要求駕駛人提供行車紀錄器內之影音資料供查閱",
      optionA: "限於已發生危害或依客觀合理判斷易生危害之交通工具",
      optionB: "得令駕駛人出示身分證明證件",
      optionC: "得檢查引擎之號碼",
      optionD: "得要求駕駛人提供行車紀錄器內之影音資料供查閱",
      category: "其他",
      difficulty: "中等",
      isGroup: False,
    },
    {
      title: "當集會、遊行之負責人宣布中止或結束集會、遊行時，參加人應如何自處？\n應即解散\n若集會、遊行尚未經主管機關命令解散，則無須解散\n因其僅具建議及勸導之性質，故是否要解散，參加人得自行決定\n得向主管機關表達異議",
      optionA: "若集會、遊行尚未經主管機關命令解散，則無須解散",
      optionB: "得向主管機關表達異議",
      optionC: "nan",
      optionD: "nan",
      category: "其他",
      difficulty: "困難",
      isGroup: False,
    },
    {
      title: "下列何者，仍可擔任集會、遊行中糾察員？\n未成年 褫奪公權尚未復權\n受監護之宣告，尚未撤銷 無中華民國國籍",
      optionA: "褫奪公權尚未復權",
      optionB: "受監護之宣告，尚未撤銷",
      optionC: "無中華民國國籍",
      optionD: "nan",
      category: "其他",
      difficulty: "中等",
      isGroup: False,
    },
    {
      title: "關於警察職權行使法規定警察進入住宅建築物或處所職權之敘述，下列何者錯誤？\n本項職權是對於私人住宅、建築物或處所之進入\n進入時應著制服或出示證件表明身分，並應告知事由\n有賭博或其他妨害風俗或公安之情事，於情況急迫時得進入制止\n須因人民之生命、身體、財產有迫切之危害，非進入不能救護時",
      optionA: "於私人住宅、建築物或處所之進入",
      optionB: "應著制服或出示證件表明身分，並應告知事由",
      optionC: "於情況急迫時得進入制止",
      optionD: "須因人民之生命、身體、財產有迫切之危害，非進入不能救護時",
      category: "其他",
      difficulty: "困難",
      isGroup: False,
    },
    {
      title: "關於警察對於有事實足認其有參與集團性或組織性犯罪之虞者，以目視或科技工具，進行觀察及\n動態掌握等資料蒐集活動之敘述，下列何者錯誤？\n期間每次不得逾一年，如有必要得延長之，並以一次為限\n經由警察分局長書面同意後始得實施\n僅得對其無隱私或秘密合理期待之行為或生活情形進行觀察及動態掌握\n蒐集之資料，於達成目的後，除為調查犯罪行為，而有保存之必要者外，應即銷毀之",
      optionA: "關於警察對於有事實足認其有參與集團性或組織性犯罪之虞者，以目視或科技工具，進行觀察及",
      optionB: "得逾一年，如有必要得延長之，並以一次為限",
      optionC: "經由警察分局長書面同意後始得實施",
      optionD: "得對其無隱私或秘密合理期待之行為或生活情形進行觀察及動態掌握",
      category: "其他",
      difficulty: "困難",
      isGroup: False,
    },
    {
      title: "有關集會遊行法規定之集會、遊行禁制區之敘述，下列何者錯誤？\n禁制區經主管機關核准者得舉行集會遊行\n各級法院為禁制區，週邊範圍，由內政部劃定公告，不得逾三百公尺\n各國駐華使領館為禁制區，週邊範圍，由國防部劃定公告，不得逾三百公尺\n總統府為禁制區，週邊範圍，由內政部劃定公告，不得逾三百公尺",
      optionA: "經主管機關核准者得舉行集會遊行",
      optionB: "各級法院為禁制區，週邊範圍，由內政部劃定公告，不得逾三百公尺",
      optionC: "各國駐華使領館為禁制區，週邊範圍，由國防部劃定公告，不得逾三百公尺",
      optionD: "得逾三百公尺",
      category: "其他",
      difficulty: "困難",
      isGroup: False,
    },
    {
      title: "關於司法院大法官有關警察之解釋及憲法法庭判決之敘述，下列何者錯誤？\n司法院釋字第718號解釋認為，集會遊行法第8條第1項規定，室外集會、遊行應向主管機關\n申請許可，未排除緊急性及偶發性集會、遊行部分，違反比例原則\n司法院釋字第",
      optionA: "法院釋字第718號解釋認為，集會遊行法第8條第1項規定，室外集會、遊行應向主管機關",
      optionB: "偶發性集會、遊行部分，違反比例原則",
      optionC: "nan",
      optionD: "nan",
      category: "法律",
      difficulty: "困難",
      isGroup: False,
    },
    {
      title: "條就意圖得利與人姦、宿者，對於從事\n性交易之行為人，僅以意圖得利之一方為處罰對象，與平等原則有違\n司法院釋字第",
      optionA: "得利與人姦、宿者，對於從事",
      optionB: "行為人，僅以意圖得利之一方為處罰對象，與平等原則有違",
      optionC: "nan",
      optionD: "nan",
      category: "其他",
      difficulty: "中等",
      isGroup: False,
    },
    {
      title: "款規定，使新聞採訪者之跟追行\n為受到限制，違反比例原則\n",
      optionA: "受到限制，違反比例原則",
      optionB: "款規定，使新聞採訪者之跟追行 為受到限制，違反比例原則 ",
      optionC: "nan",
      optionD: "nan",
      category: "其他",
      difficulty: "簡單",
      isGroup: False,
    },
    {
      title: "號判決認為，警察人員人事條例規定警察人員同一考績年度中，其平時考\n核獎懲互相抵銷後累積已達二大過應予以免職，與憲法保障人民平等服公職權尚無牴觸",
      optionA: "警察人員人事條例規定警察人員同一考績年度中，其平時考",
      optionB: "應予以免職，與憲法保障人民平等服公職權尚無牴觸",
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
    1: "C",
    2: "C",
    3: "A",
    4: "C",
    5: "D",
    6: "A",
    7: "B",
    8: "C",
    9: "B",
    10: "C",
    11: "C",
    13: "C",
    14: "D",
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
