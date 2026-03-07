# -*- coding: utf-8 -*-

import tkinter as tk
from tkinter import filedialog

def select_file_in_dialog():
    #UIの準備
    root = tk.Tk()
    root.withdraw() #Tkウィンドウを非表示にする
    root.attributes("-topmost", True)
    title_text = "学習用データ(Csv)を選択してください"
    fileTypeList = [("Csvファイル", "*.csv")]
    
    #ファイル選択ダイアログを起動
    filePath = filedialog.askopenfilename(parent=root, title=title_text, filetypes=fileTypeList)
    root.destroy() #ウィンドウの終了
    
    return filePath