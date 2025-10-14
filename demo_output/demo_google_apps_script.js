function createExamForm() {
  // 建立新的Google表單
  var form = FormApp.create('警察法規考古題練習');
  
  // 設定表單描述
  form.setDescription('考古題練習表單 - 自動生成於 2025-10-14 23:13');
  
  // 設定為測驗模式
  form.setIsQuiz(true);
  
  // 設定分數
  form.setPoints(100);
  
  // 設定回饋設定
  form.setConfirmationMessage('感謝您的作答！');
  
  // 題目資料
  var questions = [
  {
    "題號": "1",
    "題目": "下列何者為警察法第2條所規定之警察任務？",
    "題型": "選擇題",
    "正確答案": "D",
    "選項A": "維護社會秩序",
    "選項B": "保護人民生命財產",
    "選項C": "促進人民福利",
    "選項D": "以上皆是",
    "說明": "正確答案: D",
    "分數": 1,
    "必答": true
  },
  {
    "題號": "2",
    "題目": "警察人員執行職務時，應遵守之基本原則為何？",
    "題型": "選擇題",
    "正確答案": "D",
    "選項A": "依法行政",
    "選項B": "比例原則",
    "選項C": "正當程序",
    "選項D": "以上皆是",
    "說明": "正確答案: D",
    "分數": 1,
    "必答": true
  },
  {
    "題號": "3",
    "題目": "請說明警察人員在執行職務時應具備的基本素養。",
    "題型": "問答題",
    "正確答案": "專業知識、法律素養、溝通技巧、危機處理能力等",
    "選項A": "",
    "選項B": "",
    "選項C": "",
    "選項D": "",
    "說明": "正確答案: 專業知識、法律素養、溝通技巧、危機處理能力等",
    "分數": 1,
    "必答": true
  }
];
  
  // 建立題目
  questions.forEach(function(q, index) {
    var item;
    
    if (q.題型 === '選擇題') {
      // 建立選擇題
      item = form.addMultipleChoiceItem();
      item.setTitle(q.題目);
      item.setRequired(q.必答);
      
      // 設定選項
      var choices = [];
      if (q.選項A) choices.push(q.選項A);
      if (q.選項B) choices.push(q.選項B);
      if (q.選項C) choices.push(q.選項C);
      if (q.選項D) choices.push(q.選項D);
      
      item.setChoices(choices.map(function(choice, i) {
        return item.createChoice(choice, i === 0); // 預設第一個選項為正確答案
      }));
      
      // 設定正確答案
      if (q.正確答案) {
        var correctAnswer = q.正確答案;
        var correctIndex = ['A', 'B', 'C', 'D'].indexOf(correctAnswer);
        if (correctIndex !== -1 && correctIndex < choices.length) {
          item.setChoices(choices.map(function(choice, i) {
            return item.createChoice(choice, i === correctIndex);
          }));
        }
      }
      
      // 設定分數
      item.setPoints(q.分數);
      
    } else if (q.題型 === '問答題') {
      // 建立問答題
      item = form.addParagraphTextItem();
      item.setTitle(q.題目);
      item.setRequired(q.必答);
    }
    
    // 添加說明
    if (q.說明) {
      item.setHelpText(q.說明);
    }
  });
  
  // 設定表單設定
  form.setAcceptingResponses(true);
  form.setShowLinkToRespondAgain(false);
  
  // 回傳表單URL
  Logger.log('表單已建立: ' + form.getPublishedUrl());
  return form.getPublishedUrl();
}

// 執行函數
function main() {
  var formUrl = createExamForm();
  console.log('表單URL: ' + formUrl);
}