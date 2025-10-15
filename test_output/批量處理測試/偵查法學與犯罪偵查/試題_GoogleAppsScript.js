
/**
 * 考古題練習表單生成器
 * 自動從CSV資料建立Google表單
 * 生成時間: 2025-10-15 16:30:05
 */

function createPracticeForm() {
  // 表單設定
  const formTitle = "考古題練習表單";
  const formDescription = "此表單包含 12 題考古題，用於練習和自測";
  
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
      title: "分）\n二、A 警察為了調查甲殺乙之案件，分別通知犯罪嫌疑人甲和目擊證人丙\n到派出所說明，並於案發後即刻前往醫院詢問乙，對甲、乙、丙三人\n之詢問均做成筆錄。甲陳述：「凶刀丟棄在某大水溝裡」，A 警循線\n尋獲該把凶刀，但當初詢問甲時，為了偵查便利，故意不告知甲得保\n持緘默及選任辯護人。丙陳述：「有看到甲用刀刺向乙」，但在法院\n審理時翻供稱：「未看到甲殺乙」。乙陳述：「是被甲用刀刺中腹部\n才受傷的」，法院開庭時，乙因傷重已於醫院死亡。請問上述 A 警察\n對甲、乙、丙所做的調查筆錄及所尋獲之凶刀有無證據能力？請分別\n附理由說明之。（",
      optionA: "警察為了調查甲殺乙之案件，分別通知犯罪嫌疑人甲和目擊證人丙",
      optionB: "於案發後即刻前往醫院詢問乙，對甲、乙、丙三人",
      optionC: "該把凶刀，但當初詢問甲時，為了偵查便利，故意不告知甲得保",
      optionD: "向乙」，但在法院",
      category: "其他",
      difficulty: "困難",
      isGroup: False,
    },
    {
      title: "關於夜間搜索之案例，下列何者是為合法？\n警方於晚間12點到A所經營之KTV，該KTV門口亮著招牌燈，但實際上已經停止營業，\n並且上鎖；警方未確認營業狀態，即破門搜索\n警方下午",
      optionA: "警方於晚間12點到A所經營之KTV，該KTV門口亮著招牌燈，但實際上已經停止營業，",
      optionB: "警方未確認營業狀態，即破門搜索",
      optionC: "nan",
      optionD: "nan",
      category: "其他",
      difficulty: "中等",
      isGroup: False,
    },
    {
      title: "點開始在 B 的住宅進行搜索，晚間",
      optionA: "行搜索，晚間",
      optionB: "點開始在 B 的住宅進行搜索，晚間",
      optionC: "nan",
      optionD: "nan",
      category: "其他",
      difficulty: "簡單",
      isGroup: False,
    },
    {
      title: "點再\n自行返回繼續搜索\n警方於晚上9點持搜索票到C 經營的旅館，雖然大廳仍開燈，但實際上已停止接待顧客，\n僅有員工打掃，警方未經負責人同意即進行搜索\n警方下午3點到D所經營之營業中酒吧搜索，搜索進行至晚上8點仍未結束，期間酒吧正\n常營業",
      optionA: "行返回繼續搜索",
      optionB: "警方於晚上9點持搜索票到C",
      optionC: "經營的旅館，雖然大廳仍開燈，但實際上已停止接待顧客，",
      optionD: "警方未經負責人同意即進行搜索",
      category: "其他",
      difficulty: "困難",
      isGroup: False,
    },
    {
      title: "關於警察機關處理家暴案件之程序重點，下列何者錯誤？\n在完成身分識別方面，要了解當事人關係是否為家庭暴力防治法之家庭成員或年滿",
      optionA: "當事人關係是否為家庭暴力防治法之家庭成員或年滿",
      optionB: "關於警察機關處理家暴案件之程序重點，下列何者錯誤？ 在完成身分識別方面，要了解當事人關係是否為家庭暴力防治法之家庭成員或年滿",
      optionC: "nan",
      optionD: "nan",
      category: "其他",
      difficulty: "中等",
      isGroup: False,
    },
    {
      title: "歲\n以上遭未同居親密關係加害人施暴保護範圍\n在查明保護令狀態方面，包括有無保護令、保護令之效期及款項，如有違反家暴防治法之\n情事，應即時啟動相關保護措施\n關於啟動安全措施方面，包括聲請保護令、護送安置或就醫、查訪告誡相對人、及視個案\n轉介網絡單位進行戒癮治療等其他必要危害防止措施\n在責任通報方面，執行職務知有疑似家暴，應立即通報當地主管機關，至遲不得逾",
      optionA: "關係加害人施暴保護範圍",
      optionB: "無保護令、保護令之效期及款項，如有違反家暴防治法之",
      optionC: "應即時啟動相關保護措施",
      optionD: "關於啟動安全措施方面，包括聲請保護令、護送安置或就醫、查訪告誡相對人、及視個案",
      category: "其他",
      difficulty: "困難",
      isGroup: False,
    },
    {
      title: "小\n時，如有違反，得處新臺幣6千元以上3萬元以下之罰鍰",
      optionA: "得處新臺幣6千元以上3萬元以下之罰鍰",
      optionB: "小 時，如有違反，得處新臺幣6千元以上3萬元以下之罰鍰",
      optionC: "nan",
      optionD: "nan",
      category: "其他",
      difficulty: "簡單",
      isGroup: False,
    },
    {
      title: "警察人員在執行酒測勤務時，如果未完整告知受測人拒絕酒測之「全部」法律效果，如警\n員 P 未事先告知受測人 A 拒絕酒測將會被施以交通安全講習，是否仍得裁罰該拒絕酒測之\n受測人？\n不可以，因為警員P 所實施之處分為裁罰性質，必須事先告知；未告知者不得處罰\n可以，因為警員P 所實施之處分並非行政罰，參加講習並非咎責，所以未告知也不影響法\n律效果\n可以，因為警員P 雖未告知，但道路交通管理處罰條例已有明文，用路人本有知法之義務，\n不得主張不知法律而不罰\n要視情況加以區分，只要是屬於裁罰性的處分，如罰鍰、吊銷駕照、施以講習等必須事先\n告知；但不具有裁罰性質者，不用告知，仍然生效",
      optionA: "警察人員在執行酒測勤務時，如果未完整告知受測人拒絕酒測之「全部」法律效果，如警",
      optionB: "得裁罰該拒絕酒測之",
      optionC: "須事先告知；未告知者不得處罰",
      optionD: "行政罰，參加講習並非咎責，所以未告知也不影響法",
      category: "法律",
      difficulty: "困難",
      isGroup: False,
    },
    {
      title: "項各款情形之一，且情況急迫不及報告檢察官者，得逕行\n拘提之。惟於執行後，應即報請檢察官簽發拘票，如檢察官不簽發拘票時，應即將被拘提\n人釋放。故本件P 逕行拘提甲之行為合法",
      optionA: "各款情形之一，且情況急迫不及報告檢察官者，得逕行",
      optionB: "於執行後，應即報請檢察官簽發拘票，如檢察官不簽發拘票時，應即將被拘提",
      optionC: "行拘提甲之行為合法",
      optionD: "nan",
      category: "其他",
      difficulty: "中等",
      isGroup: False,
    },
    {
      title: "個月至警察局代甲提出刑事告訴，並表示甲因\n為害怕報復而不敢親自前來提告\n乙目睹扒手行竊，便到最近的派出所舉報，描述了整個犯罪經過，卻因為無法提供扒手的\n真實姓名而無法完成告訴\n丙在1月1日發現自己的手機被同學B偷走，但拖到7月15日才到警局對B提出告訴；\n該告訴因已逾告訴期間而不合法，檢察官僅能以不起訴終結程序\n丁因遭C 誹謗後不久意外死亡，其兄至警察局代為對C 提起告訴，該告訴應屬合法有效，\n警方應予受理",
      optionA: "警察局代甲提出刑事告訴，並表示甲因",
      optionB: "行竊，便到最近的派出所舉報，描述了整個犯罪經過，卻因為無法提供扒手的",
      optionC: "無法完成告訴",
      optionD: "警局對B提出告訴；",
      category: "其他",
      difficulty: "困難",
      isGroup: False,
    },
    {
      title: "司法警察於命案發生後在現場進行勘察屍體時，若於屍體上發現下列何種外部徵狀者，得供\n為辨明死者可能係自殺之初步參據？\n上吊屍體之頸後部沒有繩索溝痕者 槍傷屍體之射擊距離在20公分以上者\n屍體已掩埋且現場跡證被湮滅者 屍體上有2種以上之兇器創傷者",
      optionA: "法警察於命案發生後在現場進行勘察屍體時，若於屍體上發現下列何種外部徵狀者，得供",
      optionB: "司法警察於命案發生後在現場進行勘察屍體時，若於屍體上發現下列何種外部徵狀者，得供 為辨明死者可能係自殺之初步參據？ 上吊屍體之頸後部沒有繩索溝痕者 槍傷屍體之射擊距離在20公分以上者 屍體已掩埋且現場跡證被湮滅者 屍體上有2種以上之兇器創傷者",
      optionC: "nan",
      optionD: "nan",
      category: "其他",
      difficulty: "困難",
      isGroup: False,
    },
    {
      title: "依托咪酯（Etomidate，又稱為喪屍菸彈）屬於中樞神經鎮定劑的麻醉藥物；吩坦尼（Fentanyl，\n又稱為芬太尼），是強效合成的鴉片類止痛藥物。請問：這2類藥物在臺灣目前被核定為那\n一級的毒品？\n前者為第二級毒品，後者為第二級毒品 前者為第二級毒品，後者為第三級毒品\n前者為第三級毒品，後者為第二級毒品 前者為第三級毒品，後者為第三級毒品",
      optionA: "依托咪酯（Etomidate，又稱為喪屍菸彈）屬於中樞神經鎮定劑的麻醉藥物；吩坦尼（Fentanyl，",
      optionB: "依托咪酯（Etomidate，又稱為喪屍菸彈）屬於中樞神經鎮定劑的麻醉藥物；吩坦尼（Fentanyl， 又稱為芬太尼），是強效合成的鴉片類止痛藥物。請問：這2類藥物在臺灣目前被核定為那 一級的毒品？ 前者為第二級毒品，後者為第二級毒品 前者為第二級毒品，後者為第三級毒品 前者為第三級毒品，後者為第二級毒品 前者為第三級毒品，後者為第三級毒品",
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
    2: "D",
    3: "A",
    4: "B",
    5: "A",
    6: "C",
    7: "A",
    8: "B",
    9: "B",
    10: "D",
    11: "A",
    12: "A",
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
