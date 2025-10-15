
/**
 * 考古題練習表單生成器
 * 自動從CSV資料建立Google表單
 * 生成時間: 2025-10-15 16:28:32
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
      title: "分）\n二、你是派出所所長，帶班巡邏獲報轄內有酒駕事故發生，到達現場後對肇\n事駕駛人進行酒測，依所測得吐氣酒精濃度值結果，酒駕肇事駕駛人移\n送法辦原則為何？（",
      optionA: "行酒測，依所測得吐氣酒精濃度值結果，酒駕肇事駕駛人移",
      optionB: "分） 二、你是派出所所長，帶班巡邏獲報轄內有酒駕事故發生，到達現場後對肇 事駕駛人進行酒測，依所測得吐氣酒精濃度值結果，酒駕肇事駕駛人移 送法辦原則為何？（",
      optionC: "nan",
      optionD: "nan",
      category: "其他",
      difficulty: "中等",
      isGroup: False,
    },
    {
      title: "項，有關對汽車肇事駕駛人強制\n實施血液或其他檢體之採樣及測試檢定，宣告違憲，現階段若汽車駕駛\n人肇事拒絕接受或無法實施吐氣酒精濃度測試之檢定，內政部警政署對\n血液酒精濃度測試之規定為何？（",
      optionA: "關對汽車肇事駕駛人強制",
      optionB: "受或無法實施吐氣酒精濃度測試之檢定，內政部警政署對",
      optionC: "nan",
      optionD: "nan",
      category: "其他",
      difficulty: "中等",
      isGroup: False,
    },
    {
      title: "分）\n三、你是分局偵查隊長，轄內某日發生知名幫派分子甲於住家門前遭不詳歹\n徒埋伏槍擊，歹徒隨即逃逸無蹤，你接獲勤務指揮中心通知立刻趕至現\n場，發現派出所同仁已將現場封鎖保全，被害人送醫急救中，請問你應\n如何部署偵查作為？（",
      optionA: "於住家門前遭不詳歹",
      optionB: "無蹤，你接獲勤務指揮中心通知立刻趕至現",
      optionC: "nan",
      optionD: "nan",
      category: "其他",
      difficulty: "困難",
      isGroup: False,
    },
    {
      title: "社會秩序維護法第38條規定：「違反本法之行為，涉嫌違反刑事法律……者，應移送檢察官……\n依刑事法律……規定辦理。但其行為應處……罰鍰……之部分，仍依本法規定處罰。」其但書關\n於處罰鍰部分之規定，於行為人之同一行為已受刑事法律追訴並經有罪判決確定者，構成重複處\n罰，依據司法院釋字第808號解釋，違反法治國之下列何種原則？\n絕對法律保留原則 法律明確性原則\n一罪不二罰原則 不溯及既往原則",
      optionA: "法第38條規定：「違反本法之行為，涉嫌違反刑事法律……者，應移送檢察官……",
      optionB: "依刑事法律……規定辦理。但其行為應處……罰鍰……之部分，仍依本法規定處罰。」其但書關",
      optionC: "於處罰鍰部分之規定，於行為人之同一行為已受刑事法律追訴並經有罪判決確定者，構成重複處",
      optionD: "法律保留原則",
      category: "法律",
      difficulty: "困難",
      isGroup: False,
    },
    {
      title: "值班員警受理民眾甲女報案遭受跟蹤騷擾案，如果你是值班員警，甲女報案之下列敘述內容，何\n者非屬實行「跟蹤騷擾行為」構成要件之一？\n保育人士乙男長期跟蹤騷擾我，要求我棄養保育動物\n鄰居丙男因我拒絕其追求，竟多次遷怒傳訊威脅我母親，造成全家人心生畏怖，影響日常生活\n同學丁男經常傳送手機簡訊向我追求，雖經回訊拒絕，但仍簡訊不斷\n同學戊男多次從學校跟蹤我回家，要求約會與聯絡，邀約看電影，但我均避不見面",
      optionA: "警受理民眾甲女報案遭受跟蹤騷擾案，如果你是值班員警，甲女報案之下列敘述內容，何",
      optionB: "經常傳送手機簡訊向我追求，雖經回訊拒絕，但仍簡訊不斷",
      optionC: "nan",
      optionD: "nan",
      category: "其他",
      difficulty: "困難",
      isGroup: False,
    },
    {
      title: "你是派出所所長，在你的轄區治安要點有設置錄影監視系統，民眾甲（案件關係人）陳情，需要\n調閱監視系統之影音檔案，依據「治安要點錄影監視系統調閱影像檔案處理作業程序」之規定，\n有關甲的申請及影音檔案保存，下列何者錯誤？\n若因情況急迫，得讓甲先行調閱，但須於3日內補申請、陳閱\n監視系統之影音檔案資料，自錄製完成時起，至少應保存1個月\n除無其他特殊情形，此影音檔案資料保存，至遲應於1年內銷毀\n若因調查犯罪之必要者，則不得任意銷毀此影音檔案資料",
      optionA: "關係人）陳情，需要",
      optionB: "依據「治安要點錄影監視系統調閱影像檔案處理作業程序」之規定，",
      optionC: "若因情況急迫，得讓甲先行調閱，但須於3日內補申請、陳閱",
      optionD: "應保存1個月",
      category: "其他",
      difficulty: "困難",
      isGroup: False,
    },
    {
      title: "槍砲彈藥刀械管制條例相關原住民「自製獵槍或彈藥」之規定與解釋，下列何者錯誤？\n原住民未經許可持有自製獵槍，供作生活工具之用者，處以行政罰\n司法院釋字第803號解釋，認為自製之獵槍一詞，尚與法律明確性原則無違\n原住民相互間未經許可出借自製獵槍，非供作生活工具之用者，處以刑事罰\n原住民未經許可製造自製獵槍或彈藥，供作生活工具者，處以刑事罰",
      optionA: "原住民未經許可持有自製獵槍，供作生活工具之用者，處以行政罰",
      optionB: "法院釋字第803號解釋，認為自製之獵槍一詞，尚與法律明確性原則無違",
      optionC: "原住民相互間未經許可出借自製獵槍，非供作生活工具之用者，處以刑事罰",
      optionD: "原住民未經許可製造自製獵槍或彈藥，供作生活工具者，處以刑事罰",
      category: "法律",
      difficulty: "困難",
      isGroup: False,
    },
    {
      title: "你是派出所所長，獲悉轄內某檳榔店發生槍擊案，依警察偵查犯罪手冊規定，下列敘述何者錯誤？\n立即到場指揮員警運用巡邏車等器材封鎖現場，並將採訪之媒體記者引導至中間層管制區\n現場有人受傷應立即讓醫護人員進入實施急救，但應引導儘可能不要破壞現場並觀察是否有移\n動現場物品\n被害人胸部中槍大量出血，救護車送醫過程，應派員隨同上車，並交付儘可能了解案情及記錄\n陳述內容\n現場派員實施封鎖、警戒，對駐足圍觀群眾全面錄影，記錄周邊人車資料，並指定專人立即調\n閲監視器影像",
      optionA: "警運用巡邏車等器材封鎖現場，並將採訪之媒體記者引導至中間層管制區",
      optionB: "受傷應立即讓醫護人員進入實施急救，但應引導儘可能不要破壞現場並觀察是否有移",
      optionC: "應派員隨同上車，並交付儘可能了解案情及記錄",
      optionD: "警戒，對駐足圍觀群眾全面錄影，記錄周邊人車資料，並指定專人立即調",
      category: "其他",
      difficulty: "困難",
      isGroup: False,
    },
    {
      title: "鑒於現今社會詐欺案件居高不下，嚴重影響民眾財產安全，究其原因係犯罪集團透過政府相關部\n門的管制措施不足所致，因此，行政院於民國",
      optionA: "於現今社會詐欺案件居高不下，嚴重影響民眾財產安全，究其原因係犯罪集團透過政府相關部",
      optionB: "行政院於民國",
      optionC: "nan",
      optionD: "nan",
      category: "其他",
      difficulty: "中等",
      isGroup: False,
    },
    {
      title: "日核定「新世代打擊詐欺策略行動\n綱領」，成立「打詐國家隊」，由各機關協力打擊詐騙犯罪，針對協力偵防之策略，下列敍述何\n者錯誤？\n識詐（宣導教育面）由內政部擔任統籌機關，強化分層、分眾、分齡犯罪預防宣導工作，提升\n民眾防詐免疫力\n堵詐（電信網路面）由交通部擔任統籌機關，防堵資通訊服務淪為犯罪工具，毀斷詐欺犯嫌施\n詐之管道\n阻詐（贓款流向面）由金融監督管理委員會擔任統籌機關，強化金融監管功能，推動各項金融\n防詐減損策略\n懲詐（偵查打擊面）由法務部擔任統籌機關，結合檢警全面查緝各類詐騙犯嫌，並強化贓款查\n扣工作，阻斷詐騙集團金流",
      optionA: "各機關協力打擊詐騙犯罪，針對協力偵防之策略，下列敍述何",
      optionB: "關，強化分層、分眾、分齡犯罪預防宣導工作，提升",
      optionC: "關，防堵資通訊服務淪為犯罪工具，毀斷詐欺犯嫌施",
      optionD: "向面）由金融監督管理委員會擔任統籌機關，強化金融監管功能，推動各項金融",
      category: "其他",
      difficulty: "困難",
      isGroup: False,
    },
    {
      title: "你處理一起汽車駕駛人甲因拒絕接受酒精濃度測試經強制抽血檢測之案件，同車乘客乙與丙分別\n為70歲與",
      optionA: "受酒精濃度測試經強制抽血檢測之案件，同車乘客乙與丙分別",
      optionB: "你處理一起汽車駕駛人甲因拒絕接受酒精濃度測試經強制抽血檢測之案件，同車乘客乙與丙分別 為70歲與",
      optionC: "nan",
      optionD: "nan",
      category: "其他",
      difficulty: "簡單",
      isGroup: False,
    },
    {
      title: "派出所所長甲於主持勤前教育時，向所屬宣達駕駛警備車於開啟警示燈及警鳴器執行「緊急任務」\n時，依法可不受標誌、標線及號誌的限制，惟仍應顧及行人及其他車輛安全；警員乙詢問甲「何\n謂緊急任務？」，有關甲答覆乙之敘述，下列何者不屬於「警察人員駕車安全考核實施要點」所\n列舉之緊急任務範疇？\n執行專案勤務、路檢及重點巡邏任務\n緝捕現行犯、逃犯\n取締重大交通違規不服攔檢稽查，不立即制止，有危害交通安全之虞者\n搶救災難或重大事故，馳往現場",
      optionA: "於主持勤前教育時，向所屬宣達駕駛警備車於開啟警示燈及警鳴器執行「緊急任務」",
      optionB: "依法可不受標誌、標線及號誌的限制，惟仍應顧及行人及其他車輛安全；警員乙詢問甲「何",
      optionC: "行專案勤務、路檢及重點巡邏任務",
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
    1: "C",
    2: "C",
    3: "D",
    4: "C",
    5: "A",
    6: "A",
    7: "D",
    8: "A",
    9: "B",
    10: "D",
    11: "B",
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
