
/**
 * 考古題練習表單生成器
 * 自動從CSV資料建立Google表單（支援自動評分）
 * 生成時間: 2025-11-17 14:58:09
 * 總題數: 3
 */

function createPracticeForm() {
  try {
    // 表單設定
    const formTitle = "考古題練習表單";
    const formDescription = "此表單包含 3 題考古題，用於練習和自測";

    // 建立新表單（測驗模式以支援自動評分）
    const form = FormApp.create(formTitle);
    form.setDescription(formDescription);
    form.setConfirmationMessage("感謝您完成測驗！您可以查看分數和詳細結果。");
    form.setShowLinkToRespondAgain(true);
    form.setAllowResponseEdits(false);

    // 設定為測驗模式（啟用自動評分）
    form.setIsQuiz(true);

    // 設定收集 Email 和登入要求
    form.setCollectEmail(true);
    form.setRequireLogin(false);

    // 添加題目
    const questionsAdded = addQuestionsToForm(form);
    console.log(`成功添加 ${questionsAdded} 題`);

    // 取得表單連結
    const formUrl = form.getPublishedUrl();
    const editUrl = form.getEditUrl();

    console.log("=" .repeat(60));
    console.log("✅ 表單建立成功！");
    console.log("=" .repeat(60));
    console.log(`📋 表單名稱: ${formTitle}`);
    console.log(`📝 題目數量: ${questionsAdded} 題`);
    console.log(`🔗 表單連結: ${formUrl}`);
    console.log(`✏️  編輯連結: ${editUrl}`);
    console.log("=" .repeat(60));

    return {
      formUrl: formUrl,
      editUrl: editUrl,
      questionsCount: questionsAdded
    };

  } catch (error) {
    console.error("❌ 表單建立失敗:", error);
    throw error;
  }
}

function addQuestionsToForm(form) {
  const questionsData = [
  {
    "title": "下列何者為台灣最高峰？",
    "optionA": "玉山",
    "optionB": "雪山",
    "optionC": "合歡山",
    "optionD": "阿里山",
    "category": "其他",
    "difficulty": "簡單",
    "isGroup": false
  },
  {
    "title": "以下何者不是台灣的直轄市？",
    "optionA": "台北市",
    "optionB": "新北市",
    "optionC": "基隆市",
    "optionD": "桃園市",
    "category": "其他",
    "difficulty": "簡單",
    "isGroup": false
  },
  {
    "title": "台灣的貨幣單位為？",
    "optionA": "人民幣",
    "optionB": "新台幣",
    "optionC": "港幣",
    "optionD": "美金",
    "category": "其他",
    "difficulty": "簡單",
    "isGroup": false
  }
];
  const answersData = {
  "1": "A",
  "2": "C",
  "3": "B"
};
  let addedCount = 0;

  questionsData.forEach((question, index) => {
    try {
      const questionNumber = index + 1;
      const correctAnswer = answersData[questionNumber];

      // 收集非空選項
      const options = [];
      const optionMap = {
        'A': question.optionA,
        'B': question.optionB,
        'C': question.optionC,
        'D': question.optionD
      };

      // 只添加非空選項
      for (const [key, value] of Object.entries(optionMap)) {
        if (value && value.trim() !== '' && value !== 'nan' && value !== 'null') {
          options.push({ key: key, value: value.trim() });
        }
      }

      // 至少需要2個選項才能創建題目
      if (options.length < 2) {
        console.warn(`⚠️  第${questionNumber}題選項不足，跳過 (僅${options.length}個選項)`);
        return;
      }

      // 創建題目
      const item = form.addMultipleChoiceItem();
      item.setTitle(`第${questionNumber}題: ${question.title}`);
      item.setRequired(true);

      // 創建選項（標記正確答案）
      const choices = options.map(opt => {
        const isCorrect = opt.key === correctAnswer;
        if (form.isQuiz()) {
          // 測驗模式：標記正確答案並給分
          return item.createChoice(opt.value, isCorrect);
        } else {
          // 非測驗模式：僅創建選項
          return item.createChoice(opt.value);
        }
      });

      item.setChoices(choices);

      // 設定分數（測驗模式）
      if (form.isQuiz() && correctAnswer) {
        item.setPoints(1);  // 每題1分
      }

      // 添加題目分類和難度標籤
      let helpText = [];
      if (question.category && question.category !== '其他') {
        helpText.push(`分類: ${question.category}`);
      }
      if (question.difficulty) {
        helpText.push(`難度: ${question.difficulty}`);
      }
      if (question.isGroup) {
        helpText.push('📚 題組題目');
      }

      if (helpText.length > 0) {
        item.setHelpText(helpText.join(' | '));
      }

      addedCount++;

    } catch (error) {
      console.error(`❌ 第${index + 1}題添加失敗:`, error);
    }
  });

  return addedCount;
}

// 執行主函數
function main() {
  return createPracticeForm();
}

// 測試函數（僅檢查資料結構不建立表單）
function testFormStructure() {
  const questionsData = [
  {
    "title": "下列何者為台灣最高峰？",
    "optionA": "玉山",
    "optionB": "雪山",
    "optionC": "合歡山",
    "optionD": "阿里山",
    "category": "其他",
    "difficulty": "簡單",
    "isGroup": false
  },
  {
    "title": "以下何者不是台灣的直轄市？",
    "optionA": "台北市",
    "optionB": "新北市",
    "optionC": "基隆市",
    "optionD": "桃園市",
    "category": "其他",
    "difficulty": "簡單",
    "isGroup": false
  },
  {
    "title": "台灣的貨幣單位為？",
    "optionA": "人民幣",
    "optionB": "新台幣",
    "optionC": "港幣",
    "optionD": "美金",
    "category": "其他",
    "difficulty": "簡單",
    "isGroup": false
  }
];
  const answersData = {
  "1": "A",
  "2": "C",
  "3": "B"
};

  console.log(`總題數: ${questionsData.length}`);
  console.log(`答案數: ${Object.keys(answersData).length}`);

  // 檢查每題的選項
  questionsData.forEach((q, i) => {
    const qNum = i + 1;
    const opts = [q.optionA, q.optionB, q.optionC, q.optionD].filter(o => o && o.trim());
    console.log(`第${qNum}題: ${opts.length} 個選項, 答案: ${answersData[qNum] || '無'}`);
  });
}
