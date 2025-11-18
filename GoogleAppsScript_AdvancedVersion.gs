// ============================================
// Google Apps Script - 高级版本
// 智能情境實務測驗表單生成器
// ============================================
//
// 功能：
// 1. 支持选择做多少题（5题、10题、20题或自定义）
// 2. 支持选择年份（110/111/112/113/114或全部）
// 3. 支持随机从选定范围抽题
// 4. 动态生成 Google Form
//
// 使用步骤：
// 1. 执行 createMainForm()
// 2. 填写配置表单
// 3. 自动生成符合条件的测验表单
// ============================================

const SHEET_ID = ''; // 留空则自动创建新 Sheet
const YEARS = ['110年警察特考', '111年警察特考', '112年警察特考', '113年警察特考', '114年警察特考'];

// ==========================================
// 主函数：创建配置表单
// ==========================================
function createMainForm() {
  try {
    // 创建或获取数据 Sheet
    const dataSheet = setupDataSheet();

    // 创建配置表单
    const configForm = FormApp.create('情境實務測驗 - 習題生成器');
    configForm.setTitle('情境實務測驗 - 習題生成器');
    configForm.setDescription(
      '根據你的需求自動生成習題表單\n\n' +
      '✓ 選擇做題數量\n' +
      '✓ 選擇年份範圍\n' +
      '✓ 隨機抽題\n\n' +
      '提交後會自動生成對應的 Google Form 及下載連結'
    );

    // 1. 題數選擇 - 多選
    configForm.addMultipleChoiceItem()
      .setTitle('你想做多少題？')
      .setHelpText('選擇一個數量')
      .setChoiceValues(['5題', '10題', '20題', '30題', '全部（98題）', '自訂數量'])
      .setRequired(true);

    // 2. 自訂題數 - 文字短答
    configForm.addTextItem()
      .setTitle('自訂題數（如上選「自訂數量」時填寫）')
      .setHelpText('輸入 1-98 之間的數字')
      .setRequired(false);

    // 3. 年份選擇 - 複選
    configForm.addCheckboxItem()
      .setTitle('選擇年份（可複選）')
      .setHelpText('不選則為全部年份')
      .setChoiceValues(['110年警察特考', '111年警察特考', '112年警察特考', '113年警察特考', '114年警察特考']);

    // 4. 隨機順序
    configForm.addMultipleChoiceItem()
      .setTitle('題目順序')
      .setChoiceValues(['按原順序', '隨機排序'])
      .setRequired(true);

    // 5. 難度選擇（可選）
    configForm.addMultipleChoiceItem()
      .setTitle('題目難度範圍（可選）')
      .setChoiceValues(['不限', '前半部分（1-10題）', '後半部分（11-20題）', '全部'])
      .setRequired(false);

    // 6. 自動生成處理
    const triggerEmail = Session.getActiveUser().getEmail();
    configForm.setDestination(FormApp.DestinationType.SPREADSHEET, dataSheet.getId());

    Logger.log('✅ 配置表單已建立！');
    Logger.log('');
    Logger.log('分享連結：' + configForm.getPublishedUrl());

    // 設置提交觸發器
    setupTriggers(configForm.getId(), dataSheet.getId());

    Logger.log('');
    Logger.log('✅ 自動觸發器已設置');
    Logger.log('提交表單後會自動生成對應的測驗表單');

    return configForm;

  } catch (error) {
    Logger.log('❌ 錯誤：' + error.toString());
  }
}

// ==========================================
// 設置數據 Sheet
// ==========================================
function setupDataSheet() {
  try {
    let sheet;

    // 如果沒有指定 SHEET_ID，則建立新 Sheet
    if (!SHEET_ID) {
      sheet = SpreadsheetApp.create('情境實務 - 習題數據庫');
      Logger.log('建立新 Sheet：' + sheet.getUrl());
    } else {
      sheet = SpreadsheetApp.openById(SHEET_ID);
    }

    // 設置數據 Sheet
    const dataSheetName = '題目數據';
    let dataSheet = sheet.getSheetByName(dataSheetName);

    if (!dataSheet) {
      dataSheet = sheet.insertSheet(dataSheetName);
      // 添加標題行
      dataSheet.appendRow(['年份', '試題編號', '標準答案', '試題內容']);
    }

    return sheet;

  } catch (error) {
    Logger.log('❌ Sheet 設置失敗：' + error.toString());
  }
}

// ==========================================
// 設置自動觸發器
// ==========================================
function setupTriggers(formId, sheetId) {
  try {
    // 刪除舊觸發器
    const triggers = ScriptApp.getProjectTriggers();
    triggers.forEach(trigger => {
      if (trigger.getHandlerFunction() === 'onFormSubmit') {
        ScriptApp.deleteTrigger(trigger);
      }
    });

    // 建立新觸發器
    ScriptApp.newTrigger('onFormSubmit')
      .forForm(formId)
      .onFormSubmit()
      .create();

  } catch (error) {
    Logger.log('⚠️ 觸發器設置：' + error.toString());
  }
}

// ==========================================
// 表單提交處理
// ==========================================
function onFormSubmit(e) {
  try {
    const responses = e.response;
    const itemResponses = responses.getItemResponses();

    let numQuestions = 10;
    let years = YEARS;
    let randomOrder = false;
    let customNum = null;

    // 解析表單回應
    itemResponses.forEach(itemResponse => {
      const question = itemResponse.getItem().getTitle();
      const answer = itemResponse.getResponse();

      if (question.includes('想做多少題')) {
        if (answer === '自訂數量') {
          customNum = true;
        } else if (answer === '全部') {
          numQuestions = 98;
        } else {
          numQuestions = parseInt(answer);
        }
      } else if (question.includes('自訂題數')) {
        if (answer && !isNaN(parseInt(answer))) {
          numQuestions = Math.min(98, Math.max(1, parseInt(answer)));
          customNum = false;
        }
      } else if (question.includes('選擇年份')) {
        const selectedYears = answer.split(',').map(y => y.trim());
        if (selectedYears.length > 0 && selectedYears[0]) {
          years = selectedYears;
        }
      } else if (question.includes('題目順序')) {
        randomOrder = answer === '隨機排序';
      }
    });

    // 獲取題目數據
    const allQuestions = getAllQuestionsFromSheet();

    // 篩選題目
    let filteredQuestions = allQuestions.filter(q => years.includes(q.year));

    // 隨機抽題
    if (numQuestions < filteredQuestions.length) {
      filteredQuestions = randomSelectQuestions(filteredQuestions, numQuestions);
    }

    // 隨機排序
    if (randomOrder) {
      filteredQuestions = shuffleArray(filteredQuestions);
    }

    // 生成表單
    const newForm = generateTestForm(filteredQuestions, years, numQuestions);

    // 記錄結果
    Logger.log('✅ 測驗表單已生成！');
    Logger.log('題數：' + filteredQuestions.length);
    Logger.log('年份：' + years.join(', '));
    Logger.log('');
    Logger.log('📋 表單連結：');
    Logger.log(newForm.getPublishedUrl());

    // 可選：發送結果給用戶
    // sendResultEmail(itemResponses[0].getItem().getParent().getEditor(), newForm);

  } catch (error) {
    Logger.log('❌ 處理表單提交時出錯：' + error.toString());
  }
}

// ==========================================
// 從 Sheet 獲取所有題目
// ==========================================
function getAllQuestionsFromSheet() {
  try {
    // 這裡需要根據你的實際數據結構調整
    // 暫時返回示例數據，實際應該從上傳的 CSV 讀取

    // 方案 1：直接從文件讀取（如果 CSV 在 Drive）
    const csvFile = DriveApp.getFilesByName('情境實務_全年版.csv');
    if (csvFile.hasNext()) {
      const content = csvFile.next().getBlob().getDataAsString('utf-8');
      return parseCSVToQuestions(content);
    }

    return [];

  } catch (error) {
    Logger.log('❌ 讀取題目數據失敗：' + error.toString());
    return [];
  }
}

// ==========================================
// 解析 CSV 為題目對象
// ==========================================
function parseCSVToQuestions(csvContent) {
  const questions = [];
  const lines = csvContent.split('\n');

  for (let i = 1; i < lines.length; i++) {
    if (lines[i].trim() === '') continue;

    const row = parseCSVLine(lines[i]);
    if (row.length >= 4) {
      questions.push({
        year: row[0].trim(),
        question: row[1].trim(),
        answer: row[2].trim(),
        content: row[3].trim()
      });
    }
  }

  return questions;
}

// ==========================================
// 隨機選擇題目
// ==========================================
function randomSelectQuestions(questions, count) {
  const selected = [];
  const indices = [];

  while (indices.length < Math.min(count, questions.length)) {
    const randomIndex = Math.floor(Math.random() * questions.length);
    if (!indices.includes(randomIndex)) {
      indices.push(randomIndex);
      selected.push(questions[randomIndex]);
    }
  }

  return selected;
}

// ==========================================
// 打亂陣列順序
// ==========================================
function shuffleArray(array) {
  const shuffled = array.slice();
  for (let i = shuffled.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]];
  }
  return shuffled;
}

// ==========================================
// 生成測驗表單
// ==========================================
function generateTestForm(questions, years, totalCount) {
  const yearStr = years.length === 5 ? '全年份' : years.join('、');
  const formTitle = `情境實務測驗 - ${questions.length}題 (${yearStr})`;

  const form = FormApp.create(formTitle);
  form.setTitle(formTitle);
  form.setDescription(
    `測驗題數：${questions.length}題\n` +
    `年份：${yearStr}\n` +
    `建立時間：${new Date().toLocaleString('zh-TW')}\n\n` +
    `說明：此為自動生成的隨機習題表單，供練習參考使用。`
  );

  // 添加題目
  questions.forEach((q, idx) => {
    const title = `${idx + 1}. ${q.question}`;
    const content = q.content;
    const options = extractOptionsFromContent(content);

    const item = form.addMultipleChoiceItem()
      .setTitle(title)
      .setHelpText(`正確答案：${q.answer}`);

    if (options.length === 4) {
      item.setChoiceValues(options);
    }
  });

  // 設置表單選項
  form.setProgressBar(true);
  form.setShowLinkToMinimalForm(false);
  form.setCollectEmail(false);
  form.setLimitOneResponsePerUser(false);

  return form;
}

// ==========================================
// 提取選項內容
// ==========================================
function extractOptionsFromContent(content) {
  const options = [];
  const lines = content.split('\n');

  lines.forEach(line => {
    const match = line.match(/^[A-D]\./);
    if (match) {
      options.push(line.substring(2).trim());
    }
  });

  return options.length === 4 ? options : ['A', 'B', 'C', 'D'];
}

// ==========================================
// 解析 CSV 行
// ==========================================
function parseCSVLine(line) {
  const result = [];
  let current = '';
  let insideQuotes = false;

  for (let i = 0; i < line.length; i++) {
    const char = line[i];

    if (char === '"') {
      insideQuotes = !insideQuotes;
    } else if (char === ',' && !insideQuotes) {
      result.push(current.trim().replace(/^"|"$/g, ''));
      current = '';
    } else {
      current += char;
    }
  }

  result.push(current.trim().replace(/^"|"$/g, ''));
  return result;
}

// ==========================================
// 發送結果郵件（可選）
// ==========================================
function sendResultEmail(userEmail, form) {
  try {
    const subject = '你的情境實務測驗表單已生成';
    const message = `
    表單已成功生成！

    請使用下方連結開始測驗：
    ${form.getPublishedUrl()}

    祝你考試順利！
    `;

    GmailApp.sendEmail(userEmail, subject, message);
  } catch (error) {
    Logger.log('⚠️ 郵件發送失敗：' + error.toString());
  }
}
