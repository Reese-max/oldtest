// Google Apps Script - 自动生成情境實務測驗 Google Form
// 使用說明：
// 1. 前往 https://script.google.com
// 2. 複製此代碼到編輯器
// 3. 點擊 "runCreateForm()" 並授權
// 4. 將生成的 Google Form 連結複製到瀏覽器

const SCENARIO_DATA = [
  {
    "年份": "110年警察特考",
    "試題編號": "第1題",
    "標準答案": "D",
    "試題內容（含ABCD選項）": "1你是警察分局巡官，在督導派出所勤務時，對於執勤同仁作為，下列敘述何者正確？\nA.警察臨檢之規定，授權警察人員得不顧時間、地點及對象任意臨檢，亦得為攔檢及隨機檢查\nB.警察執法之心證確定程度與職權干預強度應成反比，故應有相當理由才能攔停交通工具\nC.警察執法應遵守比例原則，得由現場員警決定採取報復性或懲罰性執行手段，以達成執行績效\nD.警察執法應基於法定要件與程序之正當合理性，並以整體考量，以形諸裁量是否採取攔檢措施之基礎"
  }
];

function runCreateForm() {
  // 取得 CSV 資料
  const file = DriveApp.getFilesByName('情境實務_全年版.csv').next();
  const blob = file.getBlob().getDataAsString('utf-8');

  // 解析 CSV
  const lines = blob.split('\n');
  const headers = lines[0].split(',').map(h => h.trim().replace(/^"|"$/g, ''));

  const data = [];
  for (let i = 1; i < lines.length; i++) {
    if (lines[i].trim() === '') continue;

    // 簡單的 CSV 解析（處理引號）
    const row = parseCSVLine(lines[i]);
    if (row.length >= 4) {
      data.push({
        '年份': row[0],
        '試題編號': row[1],
        '標準答案': row[2],
        '試題內容': row[3]
      });
    }
  }

  // 建立表單
  const form = FormApp.create(`情境實務測驗 - ${new Date().toLocaleDateString('zh-TW')}`);
  form.setTitle('警察特考 - 情境實務測驗');
  form.setDescription('110-114 年三特警察特考情境實務試題\n共 98 題\n\n注意：此表單僅供練習參考');

  // 按年份分組
  const byYear = {};
  data.forEach(item => {
    if (!byYear[item['年份']]) {
      byYear[item['年份']] = [];
    }
    byYear[item['年份']].push(item);
  });

  // 為每個年份建立分頁
  let pageNumber = 1;
  Object.keys(byYear).sort().forEach(year => {
    const questions = byYear[year];

    if (pageNumber > 1) {
      form.addPageBreakItem()
        .setTitle(`${year} - 共 ${questions.length} 題`);
    }

    form.addSectionHeaderItem()
      .setTitle(`${year}`)
      .setHelpText(`共 ${questions.length} 題`);

    // 為每題添加多選題
    questions.forEach((q, idx) => {
      const content = q['試題內容'];
      const options = extractOptions(content);

      const item = form.addMultipleChoiceItem()
        .setTitle(`${q['試題編號']} - ${content.split('\n')[0]}`)
        .setHelpText(`正確答案：${q['標準答案']}（供參考，提交時隱藏）`);

      // 添加選項
      if (options.length > 0) {
        item.setChoiceValues(options);
      } else {
        item.setChoiceValues(['A', 'B', 'C', 'D']);
      }

      // 可選：設置正確答案（需要 Forms API）
      // setCorrectAnswer(item, q['標準答案']);
    });

    pageNumber++;
  });

  // 配置表單設定
  form.setProgressBar(true);
  form.setShowLinkToMinimalForm(true);
  form.setCollectEmail(false);
  form.setLimitOneResponsePerUser(false);

  const formUrl = form.getPublishedUrl();
  const editUrl = form.getEditUrl();

  Logger.log('=== Google Form 已建立 ===');
  Logger.log('表單編輯：' + editUrl);
  Logger.log('表單連結：' + formUrl);
  Logger.log('\n複製以下連結到瀏覽器：');
  Logger.log(formUrl);

  // 建立一個說明文件
  const doc = DocumentApp.create(`情境實務 Google Form 連結 - ${new Date().toLocaleDateString('zh-TW')}`);
  const body = doc.getBody();
  body.appendParagraph('Google Form 已建立！');
  body.appendParagraph('表單名稱：警察特考 - 情境實務測驗');
  body.appendParagraph('');
  body.appendParagraph('編輯連結（僅你可見）：').setLinkUrl(0, 30, editUrl);
  body.appendParagraph('');
  body.appendParagraph('分享連結（可分享給他人）：').setLinkUrl(0, 30, formUrl);

  Logger.log('\n說明文件建立完成');
}

// 解析 CSV 行（處理引號和逗號）
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

// 提取選項（A、B、C、D）
function extractOptions(content) {
  const options = [];
  const lines = content.split('\n');

  lines.forEach(line => {
    const match = line.match(/^[A-D]\./);
    if (match) {
      options.push(line.replace(/^[A-D]\./, '').trim());
    }
  });

  return options.length === 4 ? options : ['A', 'B', 'C', 'D'];
}

// 設置正確答案（需要 Forms API v1）
function setCorrectAnswer(item, answer) {
  // 注意：Google Forms API 的 setCorrectAnswer 需要特殊權限
  // 這個功能可能需要額外配置
  try {
    item.setCorrectAnswer(answer);
  } catch (e) {
    Logger.log('設置正確答案需要 Forms API v1 權限');
  }
}