
# Google Apps Script使用說明

## 1. 設定Google Apps Script

1. 前往 [Google Apps Script](https://script.google.com)
2. 建立新專案
3. 將生成的JavaScript代碼複製到編輯器中
4. 儲存專案

## 2. 啟用必要的API

1. 在Apps Script編輯器中，點選「服務」
2. 新增以下服務：
   - Google Forms API
   - Google Sheets API
   - Google Drive API

## 3. 執行腳本

1. 在編輯器中選擇 `main` 函數
2. 點選「執行」
3. 首次執行時需要授權
4. 執行完成後會顯示表單連結

## 4. 自訂設定

### 修改表單標題
在 `createPracticeForm()` 函數中修改：
```javascript
const formTitle = "您的自訂標題";
```

### 修改表單描述
```javascript
const formDescription = "您的自訂描述";
```

### 啟用自動評分
腳本已包含自動評分功能，會在提交後計算分數並記錄到試算表。

## 5. 進階功能

### 添加時間限制
可以在表單設定中添加時間限制：
```javascript
form.setLimitOneResponsePerUser(true);
```

### 自訂評分標準
修改 `calculateScore()` 函數來調整評分邏輯。

### 添加結果通知
可以在 `sendResultsToSheet()` 函數中添加郵件通知功能。

## 6. 故障排除

### 常見問題
1. **權限錯誤**: 確保已啟用所有必要的API
2. **表單無法建立**: 檢查Google帳戶權限
3. **評分不正確**: 檢查正確答案對照表

### 除錯方法
1. 使用 `console.log()` 輸出除錯資訊
2. 檢查執行記錄中的錯誤訊息
3. 確認CSV資料格式正確

## 7. 維護和更新

### 更新題目
1. 修改CSV檔案
2. 重新生成JavaScript代碼
3. 更新Apps Script中的資料

### 備份設定
建議定期備份Apps Script專案和相關的Google表單。
