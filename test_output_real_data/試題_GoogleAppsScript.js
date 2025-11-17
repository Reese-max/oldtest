
/**
 * 考古題練習表單生成器
 * 自動從CSV資料建立Google表單（支援自動評分）
 * 生成時間: 2025-11-17 15:37:16
 * 總題數: 50
 */

function createPracticeForm() {
  try {
    // 表單設定
    const formTitle = "考古題練習表單";
    const formDescription = "此表單包含 50 題考古題，用於練習和自測";

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
    "title": "關於修憲程序，下列敘述何者正確？",
    "optionA": "修憲機關提出之憲法修正案，須先送請監察院人權委員會審查，始能通過施行",
    "optionB": "修憲機關提出之憲法修正案，須先送請憲法法庭審查，始能通過施行",
    "optionC": "行政院若認為修憲機關提出之憲法修正案窒礙難行，得移請修憲機關覆議",
    "optionD": "修憲機關提出之憲法修正案，須經人民投票複決，始能通過施行",
    "category": "其他",
    "difficulty": "簡單",
    "isGroup": false
  },
  {
    "title": "依憲法規定，已逾學齡未受基本教育之國民，如何受補習教育？",
    "optionA": "得自行決定受補習教育，免繳納學費 得自行決定受補習教育，須繳納學費",
    "optionB": "一律受補習教育，免繳納學費 一律受補習教育，須繳納學費",
    "optionC": "",
    "optionD": "",
    "category": "法律",
    "difficulty": "簡單",
    "isGroup": false
  },
  {
    "title": "憲法第16條保障人民之訴訟權，依司法院大法官解釋與憲法法庭判決之意旨，下列敘述何者錯誤？",
    "optionA": "針對軍法判決之特別救濟案，軍事審判法規定，僅許被告不服高等軍事法院宣告有期徒刑之上訴判決者，",
    "optionB": "得以判決違背法令為理由，向高等法院提起上訴，與保障人民訴訟權之意旨有違",
    "optionC": "針對公立大學就不續聘教師之再申訴決定提起行政訴訟案，最高行政法院決議，關於公立大學就不予維",
    "optionD": "持其不續聘教師措施之再申訴決定，不得循序提起行政訴訟部分，牴觸保障訴訟權之意旨",
    "category": "法律",
    "difficulty": "簡單",
    "isGroup": false
  },
  {
    "title": "國家基於犯罪偵查之目的，對被告或犯罪嫌疑人進行通訊監察，並未直接影響受監察人下列何種權利？",
    "optionA": "緘默權 委任律師之辯護權",
    "optionB": "隱私權 閱覽卷宗權",
    "optionC": "",
    "optionD": "",
    "category": "其他",
    "difficulty": "簡單",
    "isGroup": false
  },
  {
    "title": "依司法院大法官解釋，關於原住民文化權及身分認同權，下列敘述何者錯誤？",
    "optionA": "狩獵係原住民族利用自然資源之方式之一，乃長期以來之重要傳統，屬於文化權保障範圍",
    "optionB": "原住民之文化權保障，僅為個人權利，不具有集體權之性質及內涵",
    "optionC": "以漢族之姓氏習慣否定原住民之身分認定，與原住民之身分認同權有違",
    "optionD": "由憲法第22條及憲法增修條文整體觀察，原住民集體身分認同權亦受憲法保障",
    "category": "其他",
    "difficulty": "簡單",
    "isGroup": false
  },
  {
    "title": "依司法院大法官解釋意旨，有關人身自由之保障，下列敘述何者錯誤？",
    "optionA": "對人身自由之剝奪尤應遵循正當法律程序原則",
    "optionB": "刑法規定累犯一律加重最低本刑，使人身自由遭受過苛侵害，牴觸憲法比例原則",
    "optionC": "毒品危害防制條例規定，意圖供製造毒品之用而栽種大麻者，處5年以上有期徒刑，未違憲法比例原則，",
    "optionD": "未侵害人身自由",
    "category": "其他",
    "difficulty": "簡單",
    "isGroup": false
  },
  {
    "title": "依憲法及相關法律規定、司法院大法官解釋意旨，有關立法院審查預算案，下列敘述何者正確？",
    "optionA": "立法院對於預算案，得為增刪修改",
    "optionB": "立法院對於預算案，不得為增加支出之提議",
    "optionC": "立法院對於預算案，得於項目中移動增減金額",
    "optionD": "立法院審議預算案，須受屆期不連續原則之拘束",
    "category": "法律",
    "difficulty": "簡單",
    "isGroup": false
  },
  {
    "title": "下列何種事項，行政院院長無須提交行政院會議議決？",
    "optionA": "應提出於立法院之事項 總統召集院際爭執調解之事項",
    "optionB": "涉及各部會共同關係之事項 依法應提出於立法院之國家重要事項",
    "optionC": "",
    "optionD": "",
    "category": "其他",
    "difficulty": "簡單",
    "isGroup": false
  },
  {
    "title": "依憲法訴訟法規定，下列案件之判決，何者應本於言詞辯論為之？",
    "optionA": "人民聲請法規範憲法審查及裁判憲法審查 法院聲請法規範憲法審查",
    "optionB": "機關權限爭議案件 總統、副總統彈劾案件",
    "optionC": "代號：3101",
    "optionD": "頁次：4－2",
    "category": "法律",
    "difficulty": "簡單",
    "isGroup": false
  },
  {
    "title": "憲法增修條文第4條規定單一選區兩票制、政黨比例代表席次及政黨門檻。下列敘述何者錯誤？",
    "optionA": "憲法之修正條文與本文，屬同等位階，如係依憲法修正程序為之，即不違反憲法",
    "optionB": "依政黨名單投票採比例代表制選舉，並設百分之五席次分配門檻，尚無牴觸憲法平等保護之意旨",
    "optionC": "依憲法規定，各種選舉應以普通、平等、直接及無記名投票之方法行之",
    "optionD": "政黨門檻可能使政黨所得選票與獲得分配席次之百分比有差距，而有選票不等值現象，惟大法官解釋仍",
    "category": "法律",
    "difficulty": "簡單",
    "isGroup": false
  },
  {
    "title": "依司法院大法官解釋及憲法法庭裁判，關於土地徵收制度，下列敘述何者正確？",
    "optionA": "因時效而成立之公用地役關係，屬所有權人社會責任所應忍受之範圍，無須辦理徵收作業",
    "optionB": "未於法定期限內核發土地補償費，不影響原土地徵收處分之合法性",
    "optionC": "文化資產保存法將私人建築物指定為古蹟，已逾越所有權人社會責任所應忍受之範圍，國家應給予相當補償",
    "optionD": "大眾捷運法規定，大眾捷運系統毗鄰地區辦理開發所需之土地，雖非屬捷運交通事業所必需之土地，亦",
    "category": "法律",
    "difficulty": "簡單",
    "isGroup": false
  },
  {
    "title": "憲法第19條規定：「人民有依法律納稅之義務。」下列關於租稅之敘述，何者正確？",
    "optionA": "依據租稅法律主義之要求，有關稅捐稽徵之程序，立法者不得授權以命令定之",
    "optionB": "主管機關於職權範圍內適用租稅法律規定，本於法定職權予以闡釋，如係秉持憲法原則及相關之立法意",
    "optionC": "旨，遵守一般法律解釋方法為之，即與租稅法律主義無違",
    "optionD": "稅捐僅係為了支應國家普通施政支出而課徵，特別公課則係以特別施政用途為目的而課徵",
    "category": "法律",
    "difficulty": "簡單",
    "isGroup": false
  },
  {
    "title": "下列何者並非現行憲法規定之立法院職權？",
    "optionA": "議決法律案 議決預算權",
    "optionB": "行政院院長之人事同意權 議決國家重要事項之權",
    "optionC": "",
    "optionD": "",
    "category": "法律",
    "difficulty": "簡單",
    "isGroup": false
  },
  {
    "title": "有關我國法律違憲審查制度，下列敘述何者錯誤？",
    "optionA": "係採集中制 設有抽象法規審查",
    "optionB": "須有具體個案始得為審查 人民之聲請審查設有期限限制",
    "optionC": "",
    "optionD": "",
    "category": "法律",
    "difficulty": "簡單",
    "isGroup": false
  },
  {
    "title": "有關地方制度之立法，下列何者為憲法所不許？",
    "optionA": "縣設縣議會，縣議會議員由縣民選舉之 縣設縣長，由內政部指派之",
    "optionB": "將鄉（鎮、市）改為非地方自治團體 將省諮議會議員之人數縮減為10人",
    "optionC": "",
    "optionD": "",
    "category": "法律",
    "difficulty": "簡單",
    "isGroup": false
  },
  {
    "title": "乙受僱於甲公司，關於各項請求權消滅時效，下列敘述何者正確？",
    "optionA": "乙對甲公司之工資請求權，因5年間不行使而消滅",
    "optionB": "乙因遭職業災害而致傷害，在醫療中不能工作時，對甲公司應按其原領工資數額予以補償之受領補償權，",
    "optionC": "自得受領之日起，因5年間不行使而消滅",
    "optionD": "乙遭遇普通傷害後失能，並符合勞工保險條例規定之失能給付請領資格，其保險給付請求權，自得請領",
    "category": "其他",
    "difficulty": "簡單",
    "isGroup": false
  },
  {
    "title": "下列關於性傾向在憲法上之評價，何者錯誤？",
    "optionA": "性傾向非憲法第7條明文規定，但仍屬平等權規範之範圍",
    "optionB": "民法規定婚姻為一男一女的結合，是以性傾向為分類標準之差別待遇",
    "optionC": "同性性傾向者為社會上孤立而隔絕之少數，並因受刻板印象之影響，久為政治上之弱勢",
    "optionD": "以性傾向為基礎之差別待遇，應採最嚴格審查標準",
    "category": "法律",
    "difficulty": "簡單",
    "isGroup": false
  },
  {
    "title": "依憲法本文規定，若院與院間發生爭執，何者得召集有關各院院長會商解決之？",
    "optionA": "總統 國民大會議長",
    "optionB": "最高法院院長",
    "optionC": "總統府秘書長",
    "optionD": "",
    "category": "法律",
    "difficulty": "簡單",
    "isGroup": false
  },
  {
    "title": "有關刑法第131條公務員圖利罪，下列敘述何者錯誤？",
    "optionA": "本罪是結果犯",
    "optionB": "本罪是純正身分犯",
    "optionC": "本罪之規範範圍並不包含「對於非主管或監督之事務」之圖利",
    "optionD": "公務員圖利他人而未獲得利益者，成立公務員圖利罪之未遂犯",
    "category": "其他",
    "difficulty": "簡單",
    "isGroup": false
  },
  {
    "title": "有關未遂犯，下列敘述何者錯誤？",
    "optionA": "未遂犯與既遂犯得科處相同刑罰",
    "optionB": "甲開槍射殺乙，乙剛好彎腰綁鞋帶而未中彈，甲構成殺人未遂罪",
    "optionC": "甲持棍棒欲毆打乙手臂，乙閃開沒有受傷，甲構成傷害未遂罪",
    "optionD": "未遂的處罰，須著手於犯罪行為之實行而不遂",
    "category": "其他",
    "difficulty": "簡單",
    "isGroup": false
  },
  {
    "title": "有關「原因自由行為」，下列敘述何者錯誤？",
    "optionA": "行為人於原因行為階段具有責任能力",
    "optionB": "行為人在行為時，處於無責任能力狀態，不符合行為與罪責同時性原則",
    "optionC": "我國刑法尚無明文規定，仍屬學說主張",
    "optionD": "實務見解承認原因自由行為之可罰性",
    "category": "其他",
    "difficulty": "簡單",
    "isGroup": false
  },
  {
    "title": "A公司擬和B公司合併，A公司想了解公司法中有關公司合併之限制，下列敘述何者錯誤？",
    "optionA": "股份有限公司與股份有限公司合併時，存續或新設公司以股份有限公司為限",
    "optionB": "股份有限公司與有限公司合併時，存續或新設公司以股份有限公司為限",
    "optionC": "踐行公司簡易合併時，從屬公司之提出異議的股東可以行使股份收買請求權",
    "optionD": "一旦公司經合併而消滅後，其權利義務亦隨之消滅",
    "category": "其他",
    "difficulty": "簡單",
    "isGroup": false
  },
  {
    "title": "下列何種行為屬於處分行為？",
    "optionA": "甲拋棄其M機器的所有權 甲、乙簽訂的A車買賣契約",
    "optionB": "夫妻甲、乙二人責打其子丙 甲、乙間訂立的B腳踏車贈與契約",
    "optionC": "",
    "optionD": "",
    "category": "其他",
    "difficulty": "簡單",
    "isGroup": false
  },
  {
    "title": "甲將所有之A屋出租於乙，雙方口頭約定租期自下個月初起2年，租金每月新臺幣3萬元。下列敘述何者正確？",
    "optionA": "該租賃契約無效 該租賃契約屬於物權契約",
    "optionB": "甲、乙間成立不定期的租賃契約 該租賃契約不生效力",
    "optionC": "",
    "optionD": "",
    "category": "其他",
    "difficulty": "簡單",
    "isGroup": false
  },
  {
    "title": "關於我國民法規定之習慣法，下列敘述何者正確？",
    "optionA": "習慣法須是長久慣行，只要是反覆進行之社會習慣，就是習慣法",
    "optionB": "依據民法第1條規定，習慣法內容不應違反已經制定之法律規定",
    "optionC": "習慣法來自民間風俗，自無違反民法中公共秩序善良風俗之問題",
    "optionD": "基於私法自治原理，習慣法不會與憲法上平等原則相牴觸或衝突",
    "category": "其他",
    "difficulty": "簡單",
    "isGroup": false
  },
  {
    "title": "臺灣街頭常見「二胎借款」的廣告，「二胎」的意思是「第二順位抵押權」，其乃源自於傳統漢人的「胎借」\\n習慣名稱，加上自日治時期導入的近代抵押權之效力，可謂傳統習慣與近代西方法律交匯後之產物。對此\\n社會現象，下列敘述何者正確？",
    "optionA": "呈現臺灣社會繼受近代西方法律的一過程",
    "optionB": "顯示臺灣社會仍然落後，無法正確使用近代法律用語",
    "optionC": "代表傳統社會習慣已完全被近代西方法取代而消失",
    "optionD": "顯示法律繼受後，臺灣社會仍無法接受使用抵押權",
    "category": "法律",
    "difficulty": "困難",
    "isGroup": false
  },
  {
    "title": "關於行政命令，下列敘述何者正確？",
    "optionA": "法院並無行政命令合法性之審查權",
    "optionB": "行政命令發布後，應即送立法院。如經立法院院會審查後，認有違法情事，經議決後，通知原機關更正或廢止",
    "optionC": "行政命令之廢止，由總統為之",
    "optionD": "須行政命令有明顯重大瑕疵者，始生廢止事由",
    "category": "其他",
    "difficulty": "簡單",
    "isGroup": false
  },
  {
    "title": "行政機關藉由立法制定當時的相關立法文件，探究行政法規之規範意旨，此係運用何種解釋方法？",
    "optionA": "體系解釋",
    "optionB": "歷史解釋",
    "optionC": "目的解釋",
    "optionD": "文義解釋",
    "category": "其他",
    "difficulty": "簡單",
    "isGroup": false
  },
  {
    "title": "依我國著作權法規定，有關著作權的敘述，下列何者正確？",
    "optionA": "著作人死亡後，著作人格權隨之消滅，任何人均得自由利用",
    "optionB": "著作人格權與著作財產權，必然歸屬於同一人",
    "optionC": "未公開發表之著作原件，除作為買賣之標的或經本人允諾者外，不得作為強制執行之標的",
    "optionD": "著作財產權專屬於著作人本身，不得任意讓與他人",
    "category": "其他",
    "difficulty": "簡單",
    "isGroup": false
  },
  {
    "title": "A公司職員甲於開車送貨途中因過失與乙發生車禍，下列敘述何者正確？",
    "optionA": "乙僅得向A或甲其中一人主張損害賠償 乙得向A及甲主張連帶損害賠償",
    "optionB": "乙僅得向甲主張損害賠償 乙僅得向A主張損害賠償",
    "optionC": "",
    "optionD": "",
    "category": "其他",
    "difficulty": "簡單",
    "isGroup": false
  },
  {
    "title": "Herartexhibitwasa ofimaginativesculpturesandpaintingsthatcapturedtheaudience’simagination.",
    "optionA": "kaleidoscope",
    "optionB": "monotony",
    "optionC": "dullness",
    "optionD": "tedium",
    "category": "其他",
    "difficulty": "中等",
    "isGroup": true
  },
  {
    "title": "Thegeneroushostprovideda/an amountoffoodanddrinksforalltheguestsattheparty.",
    "optionA": "ample",
    "optionB": "scarce",
    "optionC": "meager",
    "optionD": "insufficient",
    "category": "其他",
    "difficulty": "中等",
    "isGroup": true
  },
  {
    "title": "AfterIsubmittedthereceipt,thecompanyagreedto meforthetravelexpensesincurredduringthebusinesstrip.",
    "optionA": "subtract",
    "optionB": "reimburse",
    "optionC": "console",
    "optionD": "condone",
    "category": "其他",
    "difficulty": "中等",
    "isGroup": true
  },
  {
    "title": "Evenwithpropertrainingandcare,somewildanimalscannotbecome andaffectionatecompanions.",
    "optionA": "fierce",
    "optionB": "seductive",
    "optionC": "tame",
    "optionD": "flexible",
    "category": "其他",
    "difficulty": "中等",
    "isGroup": true
  },
  {
    "title": "Workingin oftenleadstomistakesthatcouldhavebeenavoidedwithamorecarefulapproach.",
    "optionA": "moderation",
    "optionB": "prudence",
    "optionC": "restraint",
    "optionD": "haste",
    "category": "其他",
    "difficulty": "中等",
    "isGroup": true
  },
  {
    "title": "Theteammembers workedtogether to their efforts, eachcontributingtheir skills and expertise to achieve",
    "optionA": "diminish",
    "optionB": "divide",
    "optionC": "condense",
    "optionD": "coordinate",
    "category": "其他",
    "difficulty": "困難",
    "isGroup": true
  },
  {
    "title": "Theoldmanisas asamule;heneverlistenstoothers’opinions.",
    "optionA": "approximate",
    "optionB": "intimate",
    "optionC": "passionate",
    "optionD": "obstinate",
    "category": "其他",
    "difficulty": "中等",
    "isGroup": true
  },
  {
    "title": "Mythree-yearoldniece showedoffthebirthdaypresentthatshelikedverymuch.",
    "optionA": "gleefully",
    "optionB": "miserably",
    "optionC": "pathetically",
    "optionD": "fluently",
    "category": "其他",
    "difficulty": "中等",
    "isGroup": true
  },
  {
    "title": "Allstudentswere bythepuzzlegivenbytheinstructorasnoneofthemwasabletosolveit.",
    "optionA": "baffled",
    "optionB": "bailed",
    "optionC": "barged",
    "optionD": "banned",
    "category": "其他",
    "difficulty": "中等",
    "isGroup": true
  },
  {
    "title": "Theimminentthreatofathunderstorm ustoquicklygatherourbelongingsandseekshelterindoorsbefore",
    "optionA": "therainstartedpouringdown.",
    "optionB": "promoted prompted prevented preempted",
    "optionC": "代號：3101",
    "optionD": "頁次：4－4",
    "category": "其他",
    "difficulty": "中等",
    "isGroup": false
  },
  {
    "title": "請從以下選項中選出最適當的答案（英文完形填空題41）",
    "optionA": "compressed",
    "optionB": "abridged",
    "optionC": "extended",
    "optionD": "abbreviated",
    "category": "英文",
    "difficulty": "簡單",
    "isGroup": true
  },
  {
    "title": "請從以下選項中選出最適當的答案（英文完形填空題42）",
    "optionA": "capability",
    "optionB": "complexity",
    "optionC": "coincidence",
    "optionD": "connotation",
    "category": "英文",
    "difficulty": "簡單",
    "isGroup": true
  },
  {
    "title": "請從以下選項中選出最適當的答案（英文完形填空題43）",
    "optionA": "prevalent",
    "optionB": "negligible",
    "optionC": "isolated",
    "optionD": "occasional",
    "category": "英文",
    "difficulty": "簡單",
    "isGroup": true
  },
  {
    "title": "請從以下選項中選出最適當的答案（英文完形填空題44）",
    "optionA": "traced",
    "optionB": "spread",
    "optionC": "merged",
    "optionD": "disregarded",
    "category": "英文",
    "difficulty": "簡單",
    "isGroup": true
  },
  {
    "title": "nurtured impaired intact sound",
    "optionA": "請依下文回答第46題至第50題：",
    "optionB": "Pollinators, such as bees, butterflies, and birds, contribute roughly $500 billion a year to global food production.",
    "optionC": "Beingtheprimarypollinatorsofmostwildplantsandmanycrops,beesareparticularlycrucialtobothecosystemstability",
    "optionD": "and agricultural productivity. However, bee populations have been on the decline worldwide over the years, which has",
    "category": "其他",
    "difficulty": "簡單",
    "isGroup": false
  },
  {
    "title": "Whichofthefollowingtitlesbestdescribesthispassage?",
    "optionA": "PollinatorsandTheirNaturalHabitats.",
    "optionB": "CausesforDecliningBeePopulations.",
    "optionC": "PollinatorsandTheirContributiontoFoodProduction.",
    "optionD": "MeasuresforKeepingBeesfromBecomingEndangered.",
    "category": "其他",
    "difficulty": "簡單",
    "isGroup": false
  },
  {
    "title": "Whatisthemainideaofthethirdparagraph?",
    "optionA": "Arecentstudyshoweddeleteriouseffectsofagrochemicalsoneusocialbees.",
    "optionB": "Artificialintelligencetoolshavebeenusedtoexploredecliningbeepopulations.",
    "optionC": "Moreresearchisneededtostudythelinkbetweenpesticideuseandbeedeclines.",
    "optionD": "Researchersaretryingtoprovedamagingeffectsofpesticidesonbeepopulations.",
    "category": "其他",
    "difficulty": "簡單",
    "isGroup": false
  },
  {
    "title": "Accordingtothepassage,whichofthefollowingstatementsisNOTtrue?",
    "optionA": "Bees’naturalhabitatlossisamajordriverfortheirdecliningpopulations.",
    "optionB": "Effectsofmanagementtechniquesonbeedeclineshavebeenwellstudied.",
    "optionC": "Bees’exposuretopesticidehascontributedtodeclinesintheirpopulations.",
    "optionD": "Changesinpublicawarenessaboutwildbeescanhelpreducetheirdeclines.",
    "category": "其他",
    "difficulty": "中等",
    "isGroup": false
  },
  {
    "title": "Whichofthefollowingbestreplaces“disturbances”inthesecondparagraph?",
    "optionA": "Disclosures",
    "optionB": "Disengagements",
    "optionC": "Disruptions",
    "optionD": "Dissatisfactions",
    "category": "其他",
    "difficulty": "中等",
    "isGroup": true
  },
  {
    "title": "Whichofthefollowingstatementscanbeinferredfromthepassage?",
    "optionA": "Decliningbeepopulationsisexpectedtodamageglobalfoodproduction.",
    "optionB": "Controllingclimatechangescanresolvetheproblemofbees\\'habitatloss.",
    "optionC": "Artificialselectionhasreplacednaturalselectionforgeneticdiversityinbees.",
    "optionD": "Groupscientificeffortsarekeytokeepingwildbeesfrombecomingendangered.",
    "category": "其他",
    "difficulty": "中等",
    "isGroup": false
  }
];
  const answersData = {
  "1": "D",
  "2": "C",
  "3": "A",
  "4": "D",
  "5": "B",
  "6": "C",
  "7": "B",
  "8": "B",
  "9": "D",
  "10": "A",
  "11": "C",
  "12": "B",
  "13": "C",
  "14": "C",
  "15": "B",
  "16": "A",
  "17": "D",
  "18": "A",
  "19": "D",
  "20": "C",
  "21": "C",
  "22": "D",
  "23": "A",
  "24": "C",
  "25": "B",
  "26": "A",
  "27": "B",
  "28": "B",
  "29": "C",
  "30": "B",
  "31": "A",
  "32": "A",
  "33": "B",
  "34": "C",
  "35": "D",
  "36": "D",
  "37": "D",
  "38": "A",
  "39": "A",
  "40": "B",
  "41": "C",
  "42": "D",
  "43": "A",
  "44": "A",
  "45": "B",
  "46": "B",
  "47": "D",
  "48": "B",
  "49": "C",
  "50": "A"
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
    "title": "關於修憲程序，下列敘述何者正確？",
    "optionA": "修憲機關提出之憲法修正案，須先送請監察院人權委員會審查，始能通過施行",
    "optionB": "修憲機關提出之憲法修正案，須先送請憲法法庭審查，始能通過施行",
    "optionC": "行政院若認為修憲機關提出之憲法修正案窒礙難行，得移請修憲機關覆議",
    "optionD": "修憲機關提出之憲法修正案，須經人民投票複決，始能通過施行",
    "category": "其他",
    "difficulty": "簡單",
    "isGroup": false
  },
  {
    "title": "依憲法規定，已逾學齡未受基本教育之國民，如何受補習教育？",
    "optionA": "得自行決定受補習教育，免繳納學費 得自行決定受補習教育，須繳納學費",
    "optionB": "一律受補習教育，免繳納學費 一律受補習教育，須繳納學費",
    "optionC": "",
    "optionD": "",
    "category": "法律",
    "difficulty": "簡單",
    "isGroup": false
  },
  {
    "title": "憲法第16條保障人民之訴訟權，依司法院大法官解釋與憲法法庭判決之意旨，下列敘述何者錯誤？",
    "optionA": "針對軍法判決之特別救濟案，軍事審判法規定，僅許被告不服高等軍事法院宣告有期徒刑之上訴判決者，",
    "optionB": "得以判決違背法令為理由，向高等法院提起上訴，與保障人民訴訟權之意旨有違",
    "optionC": "針對公立大學就不續聘教師之再申訴決定提起行政訴訟案，最高行政法院決議，關於公立大學就不予維",
    "optionD": "持其不續聘教師措施之再申訴決定，不得循序提起行政訴訟部分，牴觸保障訴訟權之意旨",
    "category": "法律",
    "difficulty": "簡單",
    "isGroup": false
  },
  {
    "title": "國家基於犯罪偵查之目的，對被告或犯罪嫌疑人進行通訊監察，並未直接影響受監察人下列何種權利？",
    "optionA": "緘默權 委任律師之辯護權",
    "optionB": "隱私權 閱覽卷宗權",
    "optionC": "",
    "optionD": "",
    "category": "其他",
    "difficulty": "簡單",
    "isGroup": false
  },
  {
    "title": "依司法院大法官解釋，關於原住民文化權及身分認同權，下列敘述何者錯誤？",
    "optionA": "狩獵係原住民族利用自然資源之方式之一，乃長期以來之重要傳統，屬於文化權保障範圍",
    "optionB": "原住民之文化權保障，僅為個人權利，不具有集體權之性質及內涵",
    "optionC": "以漢族之姓氏習慣否定原住民之身分認定，與原住民之身分認同權有違",
    "optionD": "由憲法第22條及憲法增修條文整體觀察，原住民集體身分認同權亦受憲法保障",
    "category": "其他",
    "difficulty": "簡單",
    "isGroup": false
  },
  {
    "title": "依司法院大法官解釋意旨，有關人身自由之保障，下列敘述何者錯誤？",
    "optionA": "對人身自由之剝奪尤應遵循正當法律程序原則",
    "optionB": "刑法規定累犯一律加重最低本刑，使人身自由遭受過苛侵害，牴觸憲法比例原則",
    "optionC": "毒品危害防制條例規定，意圖供製造毒品之用而栽種大麻者，處5年以上有期徒刑，未違憲法比例原則，",
    "optionD": "未侵害人身自由",
    "category": "其他",
    "difficulty": "簡單",
    "isGroup": false
  },
  {
    "title": "依憲法及相關法律規定、司法院大法官解釋意旨，有關立法院審查預算案，下列敘述何者正確？",
    "optionA": "立法院對於預算案，得為增刪修改",
    "optionB": "立法院對於預算案，不得為增加支出之提議",
    "optionC": "立法院對於預算案，得於項目中移動增減金額",
    "optionD": "立法院審議預算案，須受屆期不連續原則之拘束",
    "category": "法律",
    "difficulty": "簡單",
    "isGroup": false
  },
  {
    "title": "下列何種事項，行政院院長無須提交行政院會議議決？",
    "optionA": "應提出於立法院之事項 總統召集院際爭執調解之事項",
    "optionB": "涉及各部會共同關係之事項 依法應提出於立法院之國家重要事項",
    "optionC": "",
    "optionD": "",
    "category": "其他",
    "difficulty": "簡單",
    "isGroup": false
  },
  {
    "title": "依憲法訴訟法規定，下列案件之判決，何者應本於言詞辯論為之？",
    "optionA": "人民聲請法規範憲法審查及裁判憲法審查 法院聲請法規範憲法審查",
    "optionB": "機關權限爭議案件 總統、副總統彈劾案件",
    "optionC": "代號：3101",
    "optionD": "頁次：4－2",
    "category": "法律",
    "difficulty": "簡單",
    "isGroup": false
  },
  {
    "title": "憲法增修條文第4條規定單一選區兩票制、政黨比例代表席次及政黨門檻。下列敘述何者錯誤？",
    "optionA": "憲法之修正條文與本文，屬同等位階，如係依憲法修正程序為之，即不違反憲法",
    "optionB": "依政黨名單投票採比例代表制選舉，並設百分之五席次分配門檻，尚無牴觸憲法平等保護之意旨",
    "optionC": "依憲法規定，各種選舉應以普通、平等、直接及無記名投票之方法行之",
    "optionD": "政黨門檻可能使政黨所得選票與獲得分配席次之百分比有差距，而有選票不等值現象，惟大法官解釋仍",
    "category": "法律",
    "difficulty": "簡單",
    "isGroup": false
  },
  {
    "title": "依司法院大法官解釋及憲法法庭裁判，關於土地徵收制度，下列敘述何者正確？",
    "optionA": "因時效而成立之公用地役關係，屬所有權人社會責任所應忍受之範圍，無須辦理徵收作業",
    "optionB": "未於法定期限內核發土地補償費，不影響原土地徵收處分之合法性",
    "optionC": "文化資產保存法將私人建築物指定為古蹟，已逾越所有權人社會責任所應忍受之範圍，國家應給予相當補償",
    "optionD": "大眾捷運法規定，大眾捷運系統毗鄰地區辦理開發所需之土地，雖非屬捷運交通事業所必需之土地，亦",
    "category": "法律",
    "difficulty": "簡單",
    "isGroup": false
  },
  {
    "title": "憲法第19條規定：「人民有依法律納稅之義務。」下列關於租稅之敘述，何者正確？",
    "optionA": "依據租稅法律主義之要求，有關稅捐稽徵之程序，立法者不得授權以命令定之",
    "optionB": "主管機關於職權範圍內適用租稅法律規定，本於法定職權予以闡釋，如係秉持憲法原則及相關之立法意",
    "optionC": "旨，遵守一般法律解釋方法為之，即與租稅法律主義無違",
    "optionD": "稅捐僅係為了支應國家普通施政支出而課徵，特別公課則係以特別施政用途為目的而課徵",
    "category": "法律",
    "difficulty": "簡單",
    "isGroup": false
  },
  {
    "title": "下列何者並非現行憲法規定之立法院職權？",
    "optionA": "議決法律案 議決預算權",
    "optionB": "行政院院長之人事同意權 議決國家重要事項之權",
    "optionC": "",
    "optionD": "",
    "category": "法律",
    "difficulty": "簡單",
    "isGroup": false
  },
  {
    "title": "有關我國法律違憲審查制度，下列敘述何者錯誤？",
    "optionA": "係採集中制 設有抽象法規審查",
    "optionB": "須有具體個案始得為審查 人民之聲請審查設有期限限制",
    "optionC": "",
    "optionD": "",
    "category": "法律",
    "difficulty": "簡單",
    "isGroup": false
  },
  {
    "title": "有關地方制度之立法，下列何者為憲法所不許？",
    "optionA": "縣設縣議會，縣議會議員由縣民選舉之 縣設縣長，由內政部指派之",
    "optionB": "將鄉（鎮、市）改為非地方自治團體 將省諮議會議員之人數縮減為10人",
    "optionC": "",
    "optionD": "",
    "category": "法律",
    "difficulty": "簡單",
    "isGroup": false
  },
  {
    "title": "乙受僱於甲公司，關於各項請求權消滅時效，下列敘述何者正確？",
    "optionA": "乙對甲公司之工資請求權，因5年間不行使而消滅",
    "optionB": "乙因遭職業災害而致傷害，在醫療中不能工作時，對甲公司應按其原領工資數額予以補償之受領補償權，",
    "optionC": "自得受領之日起，因5年間不行使而消滅",
    "optionD": "乙遭遇普通傷害後失能，並符合勞工保險條例規定之失能給付請領資格，其保險給付請求權，自得請領",
    "category": "其他",
    "difficulty": "簡單",
    "isGroup": false
  },
  {
    "title": "下列關於性傾向在憲法上之評價，何者錯誤？",
    "optionA": "性傾向非憲法第7條明文規定，但仍屬平等權規範之範圍",
    "optionB": "民法規定婚姻為一男一女的結合，是以性傾向為分類標準之差別待遇",
    "optionC": "同性性傾向者為社會上孤立而隔絕之少數，並因受刻板印象之影響，久為政治上之弱勢",
    "optionD": "以性傾向為基礎之差別待遇，應採最嚴格審查標準",
    "category": "法律",
    "difficulty": "簡單",
    "isGroup": false
  },
  {
    "title": "依憲法本文規定，若院與院間發生爭執，何者得召集有關各院院長會商解決之？",
    "optionA": "總統 國民大會議長",
    "optionB": "最高法院院長",
    "optionC": "總統府秘書長",
    "optionD": "",
    "category": "法律",
    "difficulty": "簡單",
    "isGroup": false
  },
  {
    "title": "有關刑法第131條公務員圖利罪，下列敘述何者錯誤？",
    "optionA": "本罪是結果犯",
    "optionB": "本罪是純正身分犯",
    "optionC": "本罪之規範範圍並不包含「對於非主管或監督之事務」之圖利",
    "optionD": "公務員圖利他人而未獲得利益者，成立公務員圖利罪之未遂犯",
    "category": "其他",
    "difficulty": "簡單",
    "isGroup": false
  },
  {
    "title": "有關未遂犯，下列敘述何者錯誤？",
    "optionA": "未遂犯與既遂犯得科處相同刑罰",
    "optionB": "甲開槍射殺乙，乙剛好彎腰綁鞋帶而未中彈，甲構成殺人未遂罪",
    "optionC": "甲持棍棒欲毆打乙手臂，乙閃開沒有受傷，甲構成傷害未遂罪",
    "optionD": "未遂的處罰，須著手於犯罪行為之實行而不遂",
    "category": "其他",
    "difficulty": "簡單",
    "isGroup": false
  },
  {
    "title": "有關「原因自由行為」，下列敘述何者錯誤？",
    "optionA": "行為人於原因行為階段具有責任能力",
    "optionB": "行為人在行為時，處於無責任能力狀態，不符合行為與罪責同時性原則",
    "optionC": "我國刑法尚無明文規定，仍屬學說主張",
    "optionD": "實務見解承認原因自由行為之可罰性",
    "category": "其他",
    "difficulty": "簡單",
    "isGroup": false
  },
  {
    "title": "A公司擬和B公司合併，A公司想了解公司法中有關公司合併之限制，下列敘述何者錯誤？",
    "optionA": "股份有限公司與股份有限公司合併時，存續或新設公司以股份有限公司為限",
    "optionB": "股份有限公司與有限公司合併時，存續或新設公司以股份有限公司為限",
    "optionC": "踐行公司簡易合併時，從屬公司之提出異議的股東可以行使股份收買請求權",
    "optionD": "一旦公司經合併而消滅後，其權利義務亦隨之消滅",
    "category": "其他",
    "difficulty": "簡單",
    "isGroup": false
  },
  {
    "title": "下列何種行為屬於處分行為？",
    "optionA": "甲拋棄其M機器的所有權 甲、乙簽訂的A車買賣契約",
    "optionB": "夫妻甲、乙二人責打其子丙 甲、乙間訂立的B腳踏車贈與契約",
    "optionC": "",
    "optionD": "",
    "category": "其他",
    "difficulty": "簡單",
    "isGroup": false
  },
  {
    "title": "甲將所有之A屋出租於乙，雙方口頭約定租期自下個月初起2年，租金每月新臺幣3萬元。下列敘述何者正確？",
    "optionA": "該租賃契約無效 該租賃契約屬於物權契約",
    "optionB": "甲、乙間成立不定期的租賃契約 該租賃契約不生效力",
    "optionC": "",
    "optionD": "",
    "category": "其他",
    "difficulty": "簡單",
    "isGroup": false
  },
  {
    "title": "關於我國民法規定之習慣法，下列敘述何者正確？",
    "optionA": "習慣法須是長久慣行，只要是反覆進行之社會習慣，就是習慣法",
    "optionB": "依據民法第1條規定，習慣法內容不應違反已經制定之法律規定",
    "optionC": "習慣法來自民間風俗，自無違反民法中公共秩序善良風俗之問題",
    "optionD": "基於私法自治原理，習慣法不會與憲法上平等原則相牴觸或衝突",
    "category": "其他",
    "difficulty": "簡單",
    "isGroup": false
  },
  {
    "title": "臺灣街頭常見「二胎借款」的廣告，「二胎」的意思是「第二順位抵押權」，其乃源自於傳統漢人的「胎借」\\n習慣名稱，加上自日治時期導入的近代抵押權之效力，可謂傳統習慣與近代西方法律交匯後之產物。對此\\n社會現象，下列敘述何者正確？",
    "optionA": "呈現臺灣社會繼受近代西方法律的一過程",
    "optionB": "顯示臺灣社會仍然落後，無法正確使用近代法律用語",
    "optionC": "代表傳統社會習慣已完全被近代西方法取代而消失",
    "optionD": "顯示法律繼受後，臺灣社會仍無法接受使用抵押權",
    "category": "法律",
    "difficulty": "困難",
    "isGroup": false
  },
  {
    "title": "關於行政命令，下列敘述何者正確？",
    "optionA": "法院並無行政命令合法性之審查權",
    "optionB": "行政命令發布後，應即送立法院。如經立法院院會審查後，認有違法情事，經議決後，通知原機關更正或廢止",
    "optionC": "行政命令之廢止，由總統為之",
    "optionD": "須行政命令有明顯重大瑕疵者，始生廢止事由",
    "category": "其他",
    "difficulty": "簡單",
    "isGroup": false
  },
  {
    "title": "行政機關藉由立法制定當時的相關立法文件，探究行政法規之規範意旨，此係運用何種解釋方法？",
    "optionA": "體系解釋",
    "optionB": "歷史解釋",
    "optionC": "目的解釋",
    "optionD": "文義解釋",
    "category": "其他",
    "difficulty": "簡單",
    "isGroup": false
  },
  {
    "title": "依我國著作權法規定，有關著作權的敘述，下列何者正確？",
    "optionA": "著作人死亡後，著作人格權隨之消滅，任何人均得自由利用",
    "optionB": "著作人格權與著作財產權，必然歸屬於同一人",
    "optionC": "未公開發表之著作原件，除作為買賣之標的或經本人允諾者外，不得作為強制執行之標的",
    "optionD": "著作財產權專屬於著作人本身，不得任意讓與他人",
    "category": "其他",
    "difficulty": "簡單",
    "isGroup": false
  },
  {
    "title": "A公司職員甲於開車送貨途中因過失與乙發生車禍，下列敘述何者正確？",
    "optionA": "乙僅得向A或甲其中一人主張損害賠償 乙得向A及甲主張連帶損害賠償",
    "optionB": "乙僅得向甲主張損害賠償 乙僅得向A主張損害賠償",
    "optionC": "",
    "optionD": "",
    "category": "其他",
    "difficulty": "簡單",
    "isGroup": false
  },
  {
    "title": "Herartexhibitwasa ofimaginativesculpturesandpaintingsthatcapturedtheaudience’simagination.",
    "optionA": "kaleidoscope",
    "optionB": "monotony",
    "optionC": "dullness",
    "optionD": "tedium",
    "category": "其他",
    "difficulty": "中等",
    "isGroup": true
  },
  {
    "title": "Thegeneroushostprovideda/an amountoffoodanddrinksforalltheguestsattheparty.",
    "optionA": "ample",
    "optionB": "scarce",
    "optionC": "meager",
    "optionD": "insufficient",
    "category": "其他",
    "difficulty": "中等",
    "isGroup": true
  },
  {
    "title": "AfterIsubmittedthereceipt,thecompanyagreedto meforthetravelexpensesincurredduringthebusinesstrip.",
    "optionA": "subtract",
    "optionB": "reimburse",
    "optionC": "console",
    "optionD": "condone",
    "category": "其他",
    "difficulty": "中等",
    "isGroup": true
  },
  {
    "title": "Evenwithpropertrainingandcare,somewildanimalscannotbecome andaffectionatecompanions.",
    "optionA": "fierce",
    "optionB": "seductive",
    "optionC": "tame",
    "optionD": "flexible",
    "category": "其他",
    "difficulty": "中等",
    "isGroup": true
  },
  {
    "title": "Workingin oftenleadstomistakesthatcouldhavebeenavoidedwithamorecarefulapproach.",
    "optionA": "moderation",
    "optionB": "prudence",
    "optionC": "restraint",
    "optionD": "haste",
    "category": "其他",
    "difficulty": "中等",
    "isGroup": true
  },
  {
    "title": "Theteammembers workedtogether to their efforts, eachcontributingtheir skills and expertise to achieve",
    "optionA": "diminish",
    "optionB": "divide",
    "optionC": "condense",
    "optionD": "coordinate",
    "category": "其他",
    "difficulty": "困難",
    "isGroup": true
  },
  {
    "title": "Theoldmanisas asamule;heneverlistenstoothers’opinions.",
    "optionA": "approximate",
    "optionB": "intimate",
    "optionC": "passionate",
    "optionD": "obstinate",
    "category": "其他",
    "difficulty": "中等",
    "isGroup": true
  },
  {
    "title": "Mythree-yearoldniece showedoffthebirthdaypresentthatshelikedverymuch.",
    "optionA": "gleefully",
    "optionB": "miserably",
    "optionC": "pathetically",
    "optionD": "fluently",
    "category": "其他",
    "difficulty": "中等",
    "isGroup": true
  },
  {
    "title": "Allstudentswere bythepuzzlegivenbytheinstructorasnoneofthemwasabletosolveit.",
    "optionA": "baffled",
    "optionB": "bailed",
    "optionC": "barged",
    "optionD": "banned",
    "category": "其他",
    "difficulty": "中等",
    "isGroup": true
  },
  {
    "title": "Theimminentthreatofathunderstorm ustoquicklygatherourbelongingsandseekshelterindoorsbefore",
    "optionA": "therainstartedpouringdown.",
    "optionB": "promoted prompted prevented preempted",
    "optionC": "代號：3101",
    "optionD": "頁次：4－4",
    "category": "其他",
    "difficulty": "中等",
    "isGroup": false
  },
  {
    "title": "請從以下選項中選出最適當的答案（英文完形填空題41）",
    "optionA": "compressed",
    "optionB": "abridged",
    "optionC": "extended",
    "optionD": "abbreviated",
    "category": "英文",
    "difficulty": "簡單",
    "isGroup": true
  },
  {
    "title": "請從以下選項中選出最適當的答案（英文完形填空題42）",
    "optionA": "capability",
    "optionB": "complexity",
    "optionC": "coincidence",
    "optionD": "connotation",
    "category": "英文",
    "difficulty": "簡單",
    "isGroup": true
  },
  {
    "title": "請從以下選項中選出最適當的答案（英文完形填空題43）",
    "optionA": "prevalent",
    "optionB": "negligible",
    "optionC": "isolated",
    "optionD": "occasional",
    "category": "英文",
    "difficulty": "簡單",
    "isGroup": true
  },
  {
    "title": "請從以下選項中選出最適當的答案（英文完形填空題44）",
    "optionA": "traced",
    "optionB": "spread",
    "optionC": "merged",
    "optionD": "disregarded",
    "category": "英文",
    "difficulty": "簡單",
    "isGroup": true
  },
  {
    "title": "nurtured impaired intact sound",
    "optionA": "請依下文回答第46題至第50題：",
    "optionB": "Pollinators, such as bees, butterflies, and birds, contribute roughly $500 billion a year to global food production.",
    "optionC": "Beingtheprimarypollinatorsofmostwildplantsandmanycrops,beesareparticularlycrucialtobothecosystemstability",
    "optionD": "and agricultural productivity. However, bee populations have been on the decline worldwide over the years, which has",
    "category": "其他",
    "difficulty": "簡單",
    "isGroup": false
  },
  {
    "title": "Whichofthefollowingtitlesbestdescribesthispassage?",
    "optionA": "PollinatorsandTheirNaturalHabitats.",
    "optionB": "CausesforDecliningBeePopulations.",
    "optionC": "PollinatorsandTheirContributiontoFoodProduction.",
    "optionD": "MeasuresforKeepingBeesfromBecomingEndangered.",
    "category": "其他",
    "difficulty": "簡單",
    "isGroup": false
  },
  {
    "title": "Whatisthemainideaofthethirdparagraph?",
    "optionA": "Arecentstudyshoweddeleteriouseffectsofagrochemicalsoneusocialbees.",
    "optionB": "Artificialintelligencetoolshavebeenusedtoexploredecliningbeepopulations.",
    "optionC": "Moreresearchisneededtostudythelinkbetweenpesticideuseandbeedeclines.",
    "optionD": "Researchersaretryingtoprovedamagingeffectsofpesticidesonbeepopulations.",
    "category": "其他",
    "difficulty": "簡單",
    "isGroup": false
  },
  {
    "title": "Accordingtothepassage,whichofthefollowingstatementsisNOTtrue?",
    "optionA": "Bees’naturalhabitatlossisamajordriverfortheirdecliningpopulations.",
    "optionB": "Effectsofmanagementtechniquesonbeedeclineshavebeenwellstudied.",
    "optionC": "Bees’exposuretopesticidehascontributedtodeclinesintheirpopulations.",
    "optionD": "Changesinpublicawarenessaboutwildbeescanhelpreducetheirdeclines.",
    "category": "其他",
    "difficulty": "中等",
    "isGroup": false
  },
  {
    "title": "Whichofthefollowingbestreplaces“disturbances”inthesecondparagraph?",
    "optionA": "Disclosures",
    "optionB": "Disengagements",
    "optionC": "Disruptions",
    "optionD": "Dissatisfactions",
    "category": "其他",
    "difficulty": "中等",
    "isGroup": true
  },
  {
    "title": "Whichofthefollowingstatementscanbeinferredfromthepassage?",
    "optionA": "Decliningbeepopulationsisexpectedtodamageglobalfoodproduction.",
    "optionB": "Controllingclimatechangescanresolvetheproblemofbees\\'habitatloss.",
    "optionC": "Artificialselectionhasreplacednaturalselectionforgeneticdiversityinbees.",
    "optionD": "Groupscientificeffortsarekeytokeepingwildbeesfrombecomingendangered.",
    "category": "其他",
    "difficulty": "中等",
    "isGroup": false
  }
];
  const answersData = {
  "1": "D",
  "2": "C",
  "3": "A",
  "4": "D",
  "5": "B",
  "6": "C",
  "7": "B",
  "8": "B",
  "9": "D",
  "10": "A",
  "11": "C",
  "12": "B",
  "13": "C",
  "14": "C",
  "15": "B",
  "16": "A",
  "17": "D",
  "18": "A",
  "19": "D",
  "20": "C",
  "21": "C",
  "22": "D",
  "23": "A",
  "24": "C",
  "25": "B",
  "26": "A",
  "27": "B",
  "28": "B",
  "29": "C",
  "30": "B",
  "31": "A",
  "32": "A",
  "33": "B",
  "34": "C",
  "35": "D",
  "36": "D",
  "37": "D",
  "38": "A",
  "39": "A",
  "40": "B",
  "41": "C",
  "42": "D",
  "43": "A",
  "44": "A",
  "45": "B",
  "46": "B",
  "47": "D",
  "48": "B",
  "49": "C",
  "50": "A"
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
