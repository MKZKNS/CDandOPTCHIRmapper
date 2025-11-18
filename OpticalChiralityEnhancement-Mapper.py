from ast import Global
from cProfile import label
from email.errors import HeaderParseError
from fileinput import close
import string
from textwrap import fill
from tkinter import *
from tkinter import ttk
from tkinter import filedialog
import tkinter.font as f
from tkinter import messagebox
from turtle import width
import pandas as pd
import re
import numpy as np
import matplotlib.pyplot as plt
import sys


# Optical Chirality X成分計算用関数
def OCx(Ex, Hx, PhiEx, PhiHx):
  ret = Ex * Hx * np.sin((PhiEx - PhiHx)*np.pi/180)
  print(ret)
  return(ret)

# Optical Chirality Y成分計算用関数
def OCy(Ey, Hy, PhiEy, PhiHy):
  ret = Ey * Hy * np.sin((PhiEy - PhiHy)*np.pi/180)
  return(ret)

# Optical Chirality Z成分用関数
def OCz(Ez, Hz, PhiEz, PhiHz):
    ret = Ez * Hz * np.sin((PhiEz - PhiHz)*np.pi/180)
    return(ret)

# Optiral Chirality計算用関数出力段
def OptChr(Freq, OCx, OCy, OCz):
  ret = (2 * np.pi * Freq/(2 * np.power(299792458, 2))) * (OCx + OCy + OCz)
  return(ret)

# グラフ作成用関数
# XとYの二列で表された、n行2列の配列をn/2行n/2列の配列に変換する
def TwoColumn2Array(X, Y, C):
  i = 0
  j = 0
  k = 0
  # Arrayのサイズを把握
  x = np.unique(X)
  y = np.unique(Y)
  
  # ResultArrayの大きさを定義
  ResultArray = np.empty((np.size(y), np.size(x)))
  print(ResultArray.shape)

  # 求めたサイズの分だけ、forを繰り返し、ヒートマップを示す配列を作る
  for i in range(np.size(y)):
    for j in range(np.size(x)):
      ResultArray[i, j] = C[k]
      k = k + 1

  return(ResultArray)

# Menu bar commands
def WhatisDOCP():
    print('工事中')

def HowtoUseThis():
    HWindow = Tk()
    HWindow.title("CODE: Optical Chirality =Enhancement= 使い方")
    HWindow.minsize(450, 50)
    ttk.Style().theme_use('classic')

    # Main Frame
    Hframe = Frame(HWindow)
    Hframe.pack(fill = BOTH, pady = 10)

    # Making each widget
    step1 = Label(Hframe,anchor='w', justify='left', text="その一、「参照」ボタンをクリックし、円偏光度のグラフを作りたい元のcsvファイルを選択する。\nその二、「ファイル読み込み」をクリックし、csvファイルを読み込ませ、円偏光度を計算する。\nその三、「グラフ生成」をクリックし、円偏光度の分布図を作成する。\nその四、「CSVファイルを保存」をクリックすればcsvファイルを保存できる。\nその五、グラフの描かれたウィンドウの保存マークを押せば、グラフも保存できる。\nその六、研究を頑張る。")
    button = Button(Hframe, text='OK', command=close)

    # Location of widgets
    step1.pack(side='left')
    # button.pack()

def Licence():
    LWindow = Tk()
    LWindow.geometry('550x180')
    LWindow.title("CODE: Optical Chirality =Enhancement= ライセンス情報")
    LWindow.minsize(350, 180)
    ttk.Style().theme_use('classic')

    # Main Frame
    Lframe = Frame(LWindow)
    Lframe.pack(fill = BOTH, pady = 10)

    # Making each widget
    LTitle = Label(Lframe, text="CODE: Optical Chirality =Enhancement=", font=('Source Han Serif Heavy', '18', 'bold'))
    CopyLightLabel = Label(Lframe, justify='center', text='バージョン 1.00 \n(C) 2022 小西優一 \nスペシャルサンクス: 大川拓樹 橋谷田俊 西山黎 \n 中央大学 河野研究室', font=('Source Han Serif', '10'))
    button = Button(Lframe, text='OK', command=close)

    # Location of widgets
    LTitle.pack()
    CopyLightLabel.pack()
    # button.pack()

def SaveGraph():
    print('SaveGraph')



class CSVmanipulator:

    GCDdata = pd.DataFrame() # class内pandasデータ格納用変数
    tree = None # CSVファイルビューア用変数
    Obj_READBUTTON = 0 
    Ref_READBUTTON = 0 # ファイル読み込みボタンの有効化判断用変数 E,M両者が1以上の時、リードボタンが有効化

    def Obj_ReferenceButton(self):
        
        Ftypes = [("CSVファイル", ".csv"), ("すべてのファイル", ".*")]
        Objfile = filedialog.askopenfile(initialdir='./', filetypes=Ftypes)


        if '.csv' not in Objfile.name: # 拡張子に.csvが入っていないとき
            error =  messagebox.askyesnocancel("CODE: Optical Chirality =Enhancement=", "開こうとしているファイルは拡張子が.csvではありません。\n このファイルを開いてもよろしいですか？")
            if error == False: # いいえを選択したとき
                CM.Obj_ReferenceButton()
            elif error is None: # キャンセルしたとき
                pass
            else:
                Obj_Inptfile.set(Objfile.name)
                Objfile.close
                self.Obj_READBUTTON = 1
                if self.Obj_READBUTTON == 1 and self.Ref_READBUTTON == 1:
                    readb['state'] = 'normal' # 読み込みボタンを有効化

        else: # 拡張子に.csvが入っているとき
            Obj_Inptfile.set(Objfile.name)
            Objfile.close
            self.Obj_READBUTTON = 1
            if self.Obj_READBUTTON == 1 and self.Ref_READBUTTON == 1:
                readb['state'] = 'normal' # 読み込みボタンを有効化

    def Ref_ReferenceButton(self):

        Ftypes = [("CSVファイル", ".csv"), ("すべてのファイル", ".*")]
        Reffile = filedialog.askopenfile(initialdir='./', filetypes=Ftypes)
  

        if '.csv' not in Reffile.name: # 拡張子に.csvが入っていないとき
            error =  messagebox.askyesnocancel("CODE: Optical Chirality =Enhancement=", "開こうとしているファイルは拡張子が.csvではありません。\n このファイルを開いてもよろしいですか？")
            if error == False: # いいえを選択したとき
                CM.Ref_ReferenceButton()
            elif error is None: # キャンセルしたとき
                pass
            else:
                Ref_Inptfile.set(Reffile.name)
                Reffile.close
            self.Ref_READBUTTON = 1
            if self.Obj_READBUTTON == 1 and self.Ref_READBUTTON == 1:
                readb['state'] = 'normal' # 読み込みボタンを有効化

        else: # 拡張子に.csvが入っているとき
            Ref_Inptfile.set(Reffile.name)
            Reffile.close
            self.Ref_READBUTTON = 1
            if self.Obj_READBUTTON == 1 and self.Ref_READBUTTON == 1:
                readb['state'] = 'normal' # 読み込みボタンを有効化


    def ReadCSV(self, Obj_CSVstr, Ref_CSVstr):

        if Obj_CSVstr != '' and Ref_CSVstr != '': #内容のある文字列が渡されたとき
            Location_CSVcnt = pd.read_csv(Obj_CSVstr, usecols=[' X [mm]',' Y [mm]',' Z [mm]'], header=0) # X, Y, Z座標の取得
        
            # 各種変数をインポート
            Obj_Optical_Chirality = pd.read_csv(Obj_CSVstr, usecols=['Optical Chirality']).values
            Ref_Optical_Chirality = pd.read_csv(Ref_CSVstr, usecols=['Optical Chirality']).values


            # print(Ex, Ey, Phix, Phiy)

            # 各種変数を計算する
            Obj_PER_Ref_Optical_Chirality = Obj_Optical_Chirality / abs(Ref_Optical_Chirality)
            

            # 行作成
            ObjOpticalChiralityDF = pd.DataFrame(Obj_Optical_Chirality, columns=['Object - Optical Chirality']) 
            RefOpticalChiralityDF = pd.DataFrame(Ref_Optical_Chirality, columns=['Reference - Optical Chirality']) 
            ObjPERRefOpticalChiralityDF = pd.DataFrame(Obj_PER_Ref_Optical_Chirality, columns=['Optical Chirality Enhancement'])
            

            # 行連結
            CDdata = pd.concat([Location_CSVcnt, ObjOpticalChiralityDF], axis=1)
            CDdata = pd.concat([CDdata, RefOpticalChiralityDF], axis=1)
            CDdata = pd.concat([CDdata, ObjPERRefOpticalChiralityDF], axis=1)
            

            print(CDdata) # 確認用

            self.GCDdata = CDdata # class内変数にCDdataを渡す
            gb['state'] = 'normal' # グラフ描画ボタンを有効化する
            Scsvb['state'] = 'normal' # CSVセーブボタンを有効化する
            self.CSVFileViewer() # CSVビューアを起動

    def GenerateGraph(self):
        # CSVの対象列を格納
        X = self.GCDdata[' X [mm]'].values
        Y = self.GCDdata[' Y [mm]'].values
        C = self.GCDdata['Optical Chirality Enhancement'].values
        # Optical Chiralityの最大値を求める
        Cmax = max(C)
        # Optical Chiralityの最小値を求める
        Cmin = min(C)
        # Optical Chiralityの最小値と最大値の絶対値を比較
        if abs(Cmin) <= abs(Cmax):
            limit = abs(Cmax)
        else:
            limit = abs(Cmin)

        print('C.shape', C.shape)

        # ヒートマップの生成
        plt.imshow(TwoColumn2Array(X, Y, C), cmap='bwr', extent=(min(Y), max(Y), max(X), min(X)), vmin=-1*limit, vmax=limit)
        # plt.axis('equal')
        plt.colorbar(label='Optical Chirality Enhancement')
        # 軸ラベル付け
        plt.xlabel("Y [$\mathrm{\mu}$m]")
        plt.ylabel("X [$\mathrm{\mu}$m]")
        plt.show()
        
    def SaveCSVFile(self):
        
        # セーブダイアログを出し、セーブ先のパスを取得
        SavObjfilePath = filedialog.asksaveasfilename(
            title='名前を付けて保存',
            defaultextension='.csv',
            initialfile='.csv',
            filetypes=[('CSVファイル', '.csv'), ('全てのファイル', '.*')]
            # initialfile=('.csv')
        )

        self.GCDdata.to_csv(SavObjfilePath, index=False, encoding='cp932') #  表左端のインデックスを削除して保存

    def CSVFileViewer(self):
        # Making Tree View

        self.tree = ttk.Treeview(frame1, show='headings')
        # 列名を把握
        self.tree['column'] = tuple(self.GCDdata.columns.values)
        self.tree.column('#0', width=10, anchor=W)

        print(self.tree['column'])

        # 列名を記入
        for i in self.tree['column']:
            self.tree.column(i, width=50)
            self.tree.heading(i, text=str(i))

        # レコード追加
        for i in range(len(self.GCDdata)):
            self.tree.insert(parent='', index='end', iid=i, values=tuple(self.GCDdata.iloc[i]))

        self.tree.grid(padx = 5, pady = 5, ipadx = 5, ipady = 5)
        # 1列目を可変サイズとする
        self.tree.columnconfigure(0, weight=1)
        # 1行目を可変サイズとする        
        self.tree.rowconfigure(0, weight=1)
        # 内部のサイズに合わせたフレームサイズとしない
        self.tree.grid_propagate(False)
        self.tree.grid(row=4, column=0, columnspan=4, sticky= [N, E, W, S])

        # X軸スクロールバーを追加する
        hscrollbar = ttk.Scrollbar(frame1, orient=HORIZONTAL, command=self.tree.xview)
        self.tree.configure(xscrollcommand=lambda f, l: hscrollbar.set(f, l))
        hscrollbar.grid(row=5, column=0,columnspan=4, sticky=(N, E, W))

        # Y軸スクロールバーを追加する
        vscrollbar = ttk.Scrollbar(frame1, orient=VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=vscrollbar.set)
        vscrollbar.grid(row=4, column=5, sticky=(N, W, S))




# Main Program

CM = CSVmanipulator()
root = Tk()
#Style
s = ttk.Style()
s.theme_use('classic')



menubar = Menu(root)

# File Menu
filemenu = Menu(menubar, tearoff=0)
filemenu.add_command(label='閉じる', command=lambda: sys.exit())

# Help Menu
helpmenu = Menu(menubar, tearoff=0)
# helpmenu.add_command(label='円偏光度とは？', command=WhatisDOCP)
helpmenu.add_command(label='このソフトの使い方', command=HowtoUseThis)
helpmenu.add_separator()
helpmenu.add_command(label='ライセンス', command=Licence)

# Add these menus
menubar.add_cascade(label='ファイル', menu=filemenu)
menubar.add_cascade(label='ヘルプ', menu=helpmenu)

root.config(menu=menubar)

# root Settings
root.title("CODE: Optical Chirality =Enhancement=")

# Frame definition
frame1 = ttk.Frame(root, padding=10)
frame1.grid(sticky=(N, E, W, S))
frame1.columnconfigure(0, weight=1)
frame1.rowconfigure(0, weight=1)

root.minsize(863, 350)

Obj_Inptfile = StringVar()
Ref_Inptfile = StringVar()

GCDdata = pd.DataFrame

# Inputed CSV File Path (Object)*****************************************
# Label****************************************
Inptlabel = ttk.Label(frame1, text='構造付きのOptical ChiralityマップのCSVファイルを')
Inptlabel.grid(row=0, column=0, sticky=(W))
# *********************************************
# Path Entry Fourm*****************************
Inptfile_entry = ttk.Entry(
    frame1, textvariable=Obj_Inptfile, width=100
)
Inptfile_entry.grid(row=0, column=1, columnspan=2, sticky=(E,W))
# *********************************************
# Reference Button*****************************
rb = ttk.Button(
    frame1, text='参照', command=lambda: CM.Obj_ReferenceButton(), width=8
)
rb.grid(row=0, column=3)
# *********************************************
# *************************************************************

# Inputed CSV File Path (Reference)*****************************************
# Label****************************************
Inptlabel = ttk.Label(frame1, text='ReferenceのOptical ChiralityマップのCSVファイルを')
Inptlabel.grid(row=1, column=0, sticky=(W))
# *********************************************
# Path Entry Fourm*****************************
Inptfile_entry = ttk.Entry(
    frame1, textvariable=Ref_Inptfile, width=100
)
Inptfile_entry.grid(row=1, column=1, columnspan=2, sticky=(E,W))
# *********************************************
# Reference Button*****************************
rb = ttk.Button(
    frame1, text='参照', command=lambda: CM.Ref_ReferenceButton(), width=8
)
rb.grid(row=1, column=3)
# *********************************************
# *************************************************************

# Graph and CSV File Console Buttons***************************
# ボタン用フレーム
CommandButtonFrame = ttk.Labelframe(
    frame1, relief=FLAT
)
CommandButtonFrame.grid(row=2, column=0, columnspan=4)
# Read CSV File Button*************************
readb = ttk.Button(
    CommandButtonFrame, text='ファイル読み込み', command=lambda: CM.ReadCSV(Obj_Inptfile.get(), Ref_Inptfile.get())
)
if (Obj_Inptfile.get() == '') or (Ref_Inptfile.get() == ''): # ファイルパスが無いとき 
    readb.state(['disabled']) # 無効にする

readb.grid(row=2, column=0)
# *********************************************
# Generate Graph Button************************
gb = ttk.Button(
    CommandButtonFrame, text='グラフ生成', command=lambda: CM.GenerateGraph()
)
gb.state(['disabled']) # 無効にする
gb.grid(row=2, column=1)
# *********************************************
# Save CSV File Button*************************
Scsvb = ttk.Button(
    CommandButtonFrame, text='CSVファイルを保存', command=lambda: CM.SaveCSVFile() # ファイルを保存したい。かっこ内に生成したcsvデータを入れたい。
)
Scsvb.state(['disabled'])
Scsvb.grid(row=2, column=2)
# *********************************************
# # Save Graph Button****************************
# SGraphb = ttk.Button(
#     frame1, text='グラフを保存', command=SaveGraph
# )
# SGraphb.grid(row=1, column=3)
# # *********************************************
# *************************************************************
Inptlabel = ttk.Label(frame1, text='注意：構造は直線偏光、Referenceは円偏光にしてください。Referenceの電界強度は半分になります。')
Inptlabel.grid(row=3, column=0,  columnspan=4)

root.mainloop()