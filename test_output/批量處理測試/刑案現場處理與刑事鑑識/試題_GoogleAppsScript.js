
/**
 * 考古題練習表單生成器
 * 自動從CSV資料建立Google表單
 * 生成時間: 2025-10-15 16:30:03
 */

function createPracticeForm() {
  // 表單設定
  const formTitle = "考古題練習表單";
  const formDescription = "此表單包含 8 題考古題，用於練習和自測";
  
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
      title: "分）\n承上，我國實務鑑識機關常用性能檢驗法，予以認定槍枝是否具殺傷\n力，請說明何謂性能檢驗法？（",
      optionA: "關常用性能檢驗法，予以認定槍枝是否具殺傷",
      optionB: "分） 承上，我國實務鑑識機關常用性能檢驗法，予以認定槍枝是否具殺傷 力，請說明何謂性能檢驗法？（",
      optionC: "nan",
      optionD: "nan",
      category: "其他",
      difficulty: "簡單",
      isGroup: False,
    },
    {
      title: "個月前進入嫌犯 B 住宅後，因故 A 遭 B 勒死，B\n並在浴室將 A 分屍後，分裝丟棄於附近溪河中；分屍處之浴室牆壁為淺\n色磁磚及地板為深色磁磚材質，且均遭清洗過。您是現場勘察人員，針\n對本案浴室現場，請說明如何依刑案現場物證鑑定步驟及方法要領，進\n行本案血跡類跡證最佳化之處理？（請詳述處理作為及相關運用方法與\n要領等）（",
      optionA: "於附近溪河中；分屍處之浴室牆壁為淺",
      optionB: "依刑案現場物證鑑定步驟及方法要領，進",
      optionC: "nan",
      optionD: "nan",
      category: "其他",
      difficulty: "困難",
      isGroup: False,
    },
    {
      title: "④鞋底圖騰係工廠所製作，故無法產生個化比對之效果\n①② ②③④ ①②③ ①③",
      optionA: "無法產生個化比對之效果",
      optionB: "④鞋底圖騰係工廠所製作，故無法產生個化比對之效果 ①② ②③④ ①②③ ①③",
      optionC: "nan",
      optionD: "nan",
      category: "其他",
      difficulty: "簡單",
      isGroup: False,
    },
    {
      title: "試劑係與指紋中的蛋白質反應 ③深色物面上之血指紋可以直接用415nm\n光源照射，指紋顏色會變深 ④血跡指紋系統化處理之次序，蛋白質或血基質之處理應置於最後\n⑤Leucocrystal Violet（LCV）適用於非吸水性檢體上\n①②③④ ②③⑤ ③④⑤ ②③④",
      optionA: "於非吸水性檢體上",
      optionB: "試劑係與指紋中的蛋白質反應 ③深色物面上之血指紋可以直接用415nm 光源照射，指紋顏色會變深 ④血跡指紋系統化處理之次序，蛋白質或血基質之處理應置於最後 ⑤Leucocrystal Violet（LCV）適用於非吸水性檢體上 ①②③④ ②③⑤ ③④⑤ ②③④",
      optionC: "nan",
      optionD: "nan",
      category: "其他",
      difficulty: "困難",
      isGroup: False,
    },
    {
      title: "③動物毛髮均\n具有髓質，且皮毛中髓質表現最明顯的位置是在皮毛之中端 ④纖維染料分析遇到同色異譜\n（metamerism）之困境時，非破壞性分析方法中以偏光顯微鏡為首選 ⑤同一類之人造纖維，可\n能因製程差異導致橫切面出現明顯變化\n②④⑤ ②③ ①②④⑤ ①②⑤",
      optionA: "法中以偏光顯微鏡為首選",
      optionB: "③動物毛髮均 具有髓質，且皮毛中髓質表現最明顯的位置是在皮毛之中端 ④纖維染料分析遇到同色異譜 （metamerism）之困境時，非破壞性分析方法中以偏光顯微鏡為首選 ⑤同一類之人造纖維，可 能因製程差異導致橫切面出現明顯變化 ②④⑤ ②③ ①②④⑤ ①②⑤",
      optionC: "nan",
      optionD: "nan",
      category: "其他",
      difficulty: "困難",
      isGroup: False,
    },
    {
      title: "依內政部警政署於民國112年修正發布之刑事鑑識手冊中有關槍擊殘跡證物之處理原則，下列何\n者敘述錯誤？\n採取槍擊殘跡，應以黏有雙面碳膠之鋁（銅）座分別黏取不同部位，並分別標示其採證位置\n採取手部槍擊殘跡，宜於案發後8小時內儘速採集未經清洗、擦拭、救護之手部殘跡\n採取其他相關之槍擊殘跡，宜於案發後",
      optionA: "依內政部警政署於民國112年修正發布之刑事鑑識手冊中有關槍擊殘跡證物之處理原則，下列何",
      optionB: "應以黏有雙面碳膠之鋁（銅）座分別黏取不同部位，並分別標示其採證位置",
      optionC: "於案發後8小時內儘速採集未經清洗、擦拭、救護之手部殘跡",
      optionD: "關之槍擊殘跡，宜於案發後",
      category: "其他",
      difficulty: "困難",
      isGroup: False,
    },
    {
      title: "小時內儘速採集未經清洗、血跡污染之最外層衣物\n表面殘跡\n同案有槍彈證物可供鑑定者，以槍擊殘跡證物之鑑定為優先，並將槍彈證物暫時保存，視案情\n需要，再行送鑑",
      optionA: "經清洗、血跡污染之最外層衣物",
      optionB: "小時內儘速採集未經清洗、血跡污染之最外層衣物 表面殘跡 同案有槍彈證物可供鑑定者，以槍擊殘跡證物之鑑定為優先，並將槍彈證物暫時保存，視案情 需要，再行送鑑",
      optionC: "nan",
      optionD: "nan",
      category: "其他",
      difficulty: "中等",
      isGroup: False,
    },
    {
      title: "有一塊磚頭不明原因從天而降，砸死一位路過老婦，鑑識人員於磚頭上發現有數十根可疑紫色纖\n維，欲對紫色纖維上染料進行鑑定，下列檢驗方法敘述何者錯誤？\n比對顯微鏡法（Comparison microscopy）：將纖維放置在載玻片上，並浸在 XMA mounting\nmedium 中，先以白光，後以紫外光為光源，觀察並記錄其差異性\n顯微光譜法（Microspectrophotometry）：將上述載玻片上之纖維以顯微光譜儀繪出波長\n400～700nm 的光譜，以為比對\n溶液光譜法（Solutionspectrometry）：測定纖維染料萃取液在波長280～580nm 之紅外光範圍\n的光譜\n薄層層析法（Thin layer chromatography）：可用以進行纖維染料的分離比對",
      optionA: "原因從天而降，砸死一位路過老婦，鑑識人員於磚頭上發現有數十根可疑紫色纖",
      optionB: "法（Comparison",
      optionC: "法（Microspectrophotometry）：將上述載玻片上之纖維以顯微光譜儀繪出波長",
      optionD: "法（Solutionspectrometry）：測定纖維染料萃取液在波長280～580nm",
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
    1: "B",
    2: "A",
    3: "A",
    4: "B",
    5: "A",
    6: "D",
    7: "A",
    8: "C",
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
