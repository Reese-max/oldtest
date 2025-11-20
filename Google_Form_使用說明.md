# Google Apps Script - 自動生成情境實務 Google Form

## 📋 快速開始

### 步驟 1：上傳 CSV 到 Google Drive

1. 前往 [Google Drive](https://drive.google.com)
2. 上傳 `情境實務_全年版.csv` 檔案
3. 記下檔案名稱（預設：`情境實務_全年版.csv`）

### 步驟 2：開啟 Google Apps Script

1. 前往 [Google Apps Script](https://script.google.com)
2. 建立新專案
3. 複製下面的完整代碼到編輯器

### 步驟 3：執行腳本

1. 在編輯器中，選擇函數 `runCreateForm()`
2. 點擊 ▶️ 執行按鈕
3. 授權應用程式存取你的 Google Drive
4. 等待執行完成

### 步驟 4：取得 Google Form 連結

1. 執行完成後，查看 **執行記錄**（底部）
2. 找到類似這樣的行：
   ```
   表單連結：https://forms.gle/xxxxxxxxxxxxxx
   ```
3. 複製連結到瀏覽器

---

## 🔧 Google Apps Script 代碼

將此代碼複製到 Google Apps Script 編輯器中：

\`\`\`javascript
function runCreateForm() {
  try {
    // 取得 CSV 檔案
    const files = DriveApp.getFilesByName('情境實務_全年版.csv');

    if (!files.hasNext()) {
      Logger.log('❌ 錯誤：找不到 CSV 檔案');
      Logger.log('請確保已上傳 "情境實務_全年版.csv" 到 Google Drive');
      return;
    }

    const file = files.next();
    const csvContent = file.getBlob().getDataAsString('utf-8');

    // 解析 CSV
    const lines = csvContent.split('\\n');
    const data = [];

    for (let i = 1; i < lines.length; i++) {
      if (lines[i].trim() === '') continue;

      const row = parseCSVLine(lines[i]);
      if (row.length >= 4) {
        data.push({
          year: row[0].trim(),
          question: row[1].trim(),
          answer: row[2].trim(),
          content: row[3].trim()
        });
      }
    }

    if (data.length === 0) {
      Logger.log('❌ 錯誤：CSV 資料為空');
      return;
    }

    // 建立新表單
    const form = FormApp.create('警察特考 - 情境實務測驗');
    form.setTitle('警察特考 - 情境實務測驗');
    form.setDescription('110-114 年三特警察特考情境實務試題\\n共 ' + data.length + ' 題\\n\\n說明：此表單僅供練習參考');

    // 按年份分組
    const byYear = {};
    data.forEach(item => {
      if (!byYear[item.year]) {
        byYear[item.year] = [];
      }
      byYear[item.year].push(item);
    });

    // 為每個年份建立分頁
    let isFirst = true;
    Object.keys(byYear).sort().forEach(year => {
      const questions = byYear[year];

      if (!isFirst) {
        form.addPageBreakItem().setTitle(year + ' - 共 ' + questions.length + ' 題');
      }
      isFirst = false;

      form.addSectionHeaderItem()
        .setTitle(year)
        .setHelpText('共 ' + questions.length + ' 題');

      // 為每題添加選擇題
      questions.forEach((q) => {
        const content = q.content;
        const options = extractOptions(content);

        const item = form.addMultipleChoiceItem()
          .setTitle(q.question + ' - ' + content.split('\\n')[0].substring(1))
          .setHelpText('正確答案：' + q.answer);

        // 設置選項
        if (options.length === 4) {
          item.setChoiceValues(options);
        } else {
          // 如果提取不到，使用 ABCD
          const choices = [];
          const lines = content.split('\\n');
          lines.forEach(line => {
            const match = line.match(/^A\.|^B\.|^C\.|^D\./);
            if (match) {
              choices.push(line.substring(2).trim());
            }
          });

          if (choices.length === 4) {
            item.setChoiceValues(choices);
          }
        }
      });
    });

    // 設置表單選項
    form.setProgressBar(true);
    form.setShowLinkToMinimalForm(true);
    form.setCollectEmail(false);

    const publishedUrl = form.getPublishedUrl();
    const editUrl = form.getEditUrl();

    Logger.log('✅ Google Form 已成功建立！');
    Logger.log('');
    Logger.log('編輯連結（僅你可編輯）：');
    Logger.log(editUrl);
    Logger.log('');
    Logger.log('分享連結（可分享給他人填寫）：');
    Logger.log(publishedUrl);
    Logger.log('');
    Logger.log('複製分享連結到瀏覽器即可使用');

  } catch (error) {
    Logger.log('❌ 發生錯誤：');
    Logger.log(error.toString());
  }
}

function parseCSVLine(line) {
  const result = [];
  let current = '';
  let insideQuotes = false;

  for (let i = 0; i < line.length; i++) {
    const char = line[i];

    if (char === '\"') {
      insideQuotes = !insideQuotes;
    } else if (char === ',' && !insideQuotes) {
      result.push(current.trim().replace(/^\"|\"$/g, ''));
      current = '';
    } else {
      current += char;
    }
  }

  result.push(current.trim().replace(/^\"|\"$/g, ''));
  return result;
}

function extractOptions(content) {
  const options = [];
  const lines = content.split('\\n');

  for (let i = 1; i < lines.length; i++) {
    const line = lines[i];
    if (line.match(/^[A-D]\./)) {
      options.push(line.substring(2).trim());
    }
  }

  return options.length === 4 ? options : [];
}
\`\`\`

---

## 📌 注意事項

### CSV 檔案位置
- 確保 `情境實務_全年版.csv` 已上傳到 Google Drive
- 檔案名稱必須完全相符

### 權限
- 首次執行會要求授權
- 請點選 "授予權限" 允許應用程式存取你的 Google Drive

### 執行結果
- Google Form 會自動建立並儲存到 Google Drive
- 執行日誌會顯示表單的兩個連結：
  - **編輯連結**：僅你可編輯（管理員用）
  - **分享連結**：可分享給他人填寫（學生用）

---

## 🎯 表單特色

✅ **自動分頁** - 按年份自動分頁（110年、111年...）
✅ **完整試題** - 包含所有 ABCD 選項
✅ **進度條** - 填寫時顯示進度
✅ **答案提示** - 每題下方顯示正確答案（可編輯後隱藏）
✅ **共 98 題** - 包含 5 年份的所有試題

---

## 🔗 表單分享

1. **給個別學生**：複製分享連結，貼到電子郵件
2. **公開分享**：在表單編輯頁面點選 "分享"，設為 "任何有連結的人可存取"
3. **嵌入網站**：可將表單嵌入到教學網站或 Google Classroom

---

## ⚙️ 進階設定

執行後，你可以在 Google Form 編輯頁面進行以下調整：

1. **隱藏答案提示**：編輯每題，刪除或隱藏幫助文字
2. **更改主題**：使用表單上方的 "自訂" 按鈕更改佈景主題
3. **設置必填題**：編輯每題，勾選 "必填"
4. **限制回覆**：設置 "只允許每個人回覆一次"

---

## 🆘 常見問題

**Q：找不到 CSV 檔案的錯誤？**
A：確保 CSV 檔案名稱是 `情境實務_全年版.csv`，且已上傳到 Google Drive（不是 Google Classroom）

**Q：表單建立了但沒有出現題目？**
A：檢查 CSV 檔案是否正確無損，嘗試重新上傳

**Q：如何修改題目順序？**
A：在 Google Form 編輯頁面，拖拽題目卡片可重新排序

---

## 📧 聯繫支援

如有問題，請檢查 Google Apps Script 的 **執行記錄** 查看詳細的錯誤訊息。