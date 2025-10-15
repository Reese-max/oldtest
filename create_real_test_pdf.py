#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
創建真實的測試PDF檔案
"""

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os

def create_test_pdf():
    """創建包含真實題目的測試PDF"""
    
    # 創建PDF
    c = canvas.Canvas("test_pdfs/真實測試考古題.pdf", pagesize=A4)
    width, height = A4
    
    # 設置字體（使用系統預設字體）
    c.setFont("Helvetica", 12)
    
    # 標題
    c.drawString(50, height - 50, "民國114年 警察特考 行政警察 國文")
    c.drawString(50, height - 70, "共25題")
    
    # 題目內容
    y_position = height - 100
    
    questions = [
        {
            "num": "1",
            "title": "下列各組「」內的字，讀音完全相同的選項是：",
            "options": {
                "A": "「緋」聞纏身／「誹」謗他人／「斐」然成章",
                "B": "「緋」聞纏身／「誹」謗他人／「斐」然成章", 
                "C": "「緋」聞纏身／「誹」謗他人／「斐」然成章",
                "D": "「緋」聞纏身／「誹」謗他人／「斐」然成章"
            }
        },
        {
            "num": "2", 
            "title": "下列文句，完全沒有錯別字的選項是：",
            "options": {
                "A": "他做事總是虎頭蛇尾，令人失望",
                "B": "他做事總是虎頭蛇尾，令人失望",
                "C": "他做事總是虎頭蛇尾，令人失望", 
                "D": "他做事總是虎頭蛇尾，令人失望"
            }
        },
        {
            "num": "3",
            "title": "下列成語使用正確的選項是：",
            "options": {
                "A": "他對這個問題一竅不通，卻裝模作樣",
                "B": "他對這個問題一竅不通，卻裝模作樣",
                "C": "他對這個問題一竅不通，卻裝模作樣",
                "D": "他對這個問題一竅不通，卻裝模作樣"
            }
        },
        {
            "num": "4",
            "title": "下列句子中，修辭手法相同的選項是：",
            "options": {
                "A": "春風又綠江南岸，明月何時照我還",
                "B": "春風又綠江南岸，明月何時照我還",
                "C": "春風又綠江南岸，明月何時照我還",
                "D": "春風又綠江南岸，明月何時照我還"
            }
        },
        {
            "num": "5",
            "title": "下列文句，語法完全正確的選項是：",
            "options": {
                "A": "由於天氣不好，所以我們取消了戶外活動",
                "B": "由於天氣不好，所以我們取消了戶外活動",
                "C": "由於天氣不好，所以我們取消了戶外活動",
                "D": "由於天氣不好，所以我們取消了戶外活動"
            }
        }
    ]
    
    for q in questions:
        # 題號和題目
        c.drawString(50, y_position, f"{q['num']}. {q['title']}")
        y_position -= 30
        
        # 選項
        for option, text in q['options'].items():
            c.drawString(70, y_position, f"({option}) {text}")
            y_position -= 25
        
        y_position -= 20  # 題目間距
        
        # 如果頁面空間不足，換頁
        if y_position < 100:
            c.showPage()
            y_position = height - 50
    
    c.save()
    print("✅ 測試PDF已創建: test_pdfs/真實測試考古題.pdf")

if __name__ == "__main__":
    # 確保目錄存在
    os.makedirs("test_pdfs", exist_ok=True)
    create_test_pdf()