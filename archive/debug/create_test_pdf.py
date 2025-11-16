#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
建立測試用的考古題PDF檔案
"""

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os

def create_test_exam_pdf():
    """建立測試用的考古題PDF"""
    
    # 建立輸出資料夾
    os.makedirs("test_pdfs", exist_ok=True)
    
    # 建立PDF檔案
    filename = "test_pdfs/測試考古題_民國114年_警察特考_行政警察_國文.pdf"
    c = canvas.Canvas(filename, pagesize=A4)
    width, height = A4
    
    # 設定字體（使用系統預設字體）
    try:
        # 嘗試註冊中文字體
        pdfmetrics.registerFont(TTFont('SimSun', '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'))
        font_name = 'SimSun'
    except:
        font_name = 'Helvetica'
    
    # 設定頁面標題
    c.setFont(font_name, 16)
    c.drawString(50, height - 50, "民國114年警察人員考試三等考試")
    c.drawString(50, height - 80, "行政警察人員類別")
    c.drawString(50, height - 110, "國文(作文、公文與測驗)")
    c.drawString(50, height - 140, "共25題")
    
    # 題目內容
    y_position = height - 180
    c.setFont(font_name, 12)
    
    questions = [
        "1. 下列各組「」內的字，讀音完全相同的選項是：",
        "   (A) 「緋」聞纏身／「誹」謗他人／「斐」然成章",
        "   (B) 「緋」聞纏身／「誹」謗他人／「斐」然成章", 
        "   (C) 「緋」聞纏身／「誹」謗他人／「斐」然成章",
        "   (D) 「緋」聞纏身／「誹」謗他人／「斐」然成章",
        "",
        "2. 下列文句，完全沒有錯別字的選項是：",
        "   (A) 他做事總是虎頭蛇尾，令人失望",
        "   (B) 他做事總是虎頭蛇尾，令人失望",
        "   (C) 他做事總是虎頭蛇尾，令人失望", 
        "   (D) 他做事總是虎頭蛇尾，令人失望",
        "",
        "3. 下列各組詞語，意義相近的選項是：",
        "   (A) 一蹴可幾／一蹴而就",
        "   (B) 一蹴可幾／一蹴而就",
        "   (C) 一蹴可幾／一蹴而就",
        "   (D) 一蹴可幾／一蹴而就",
        "",
        "4. 下列文句「」內的詞語，使用正確的選項是：",
        "   (A) 他「不恥下問」，虛心向同事請教",
        "   (B) 他「不恥下問」，虛心向同事請教",
        "   (C) 他「不恥下問」，虛心向同事請教",
        "   (D) 他「不恥下問」，虛心向同事請教",
        "",
        "5. 下列各組「」內的字，意思相同的選項是：",
        "   (A) 「舉」世無雙／「舉」重若輕",
        "   (B) 「舉」世無雙／「舉」重若輕",
        "   (C) 「舉」世無雙／「舉」重若輕",
        "   (D) 「舉」世無雙／「舉」重若輕"
    ]
    
    for question in questions:
        if y_position < 50:  # 如果接近頁面底部，開始新頁
            c.showPage()
            y_position = height - 50
            c.setFont(font_name, 12)
        
        c.drawString(50, y_position, question)
        y_position -= 20
    
    # 結束PDF
    c.save()
    print(f"✅ 測試PDF已建立: {filename}")
    return filename

if __name__ == "__main__":
    create_test_exam_pdf()