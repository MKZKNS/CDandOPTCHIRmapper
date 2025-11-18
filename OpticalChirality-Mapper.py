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
from scipy.constants import *

# Optical Chirality X成分計算用関数
def OCx(Ex, Hx, PhiEx, PhiHx):
# 単位はV/m, A/m
  ret = Ex * mu_0 * Hx * np.sin(np.deg2rad(PhiEx - PhiHx))
  print(ret)
  return(ret)

# Optical Chirality Y成分計算用関数
def OCy(Ey, Hy, PhiEy, PhiHy):
  # 単位はV/m, A/m
  ret = Ey * mu_0 * Hy * np.sin(np.deg2rad(PhiEy - PhiHy))
  return(ret)

# Optical Chirality Z成分用関数
def OCz(Ez, Hz, PhiEz, PhiHz):
    # 単位はV/m, A/m
    ret = Ez * mu_0 * Hz * np.sin(np.deg2rad(PhiEz - PhiHz))
    return(ret)

# Optiral Chirality計算用関数出力段
def OptChr(Freq, OCx, OCy, OCz):
  omega = 2 * np.pi * Freq
  ret = -1 * ((omega * epsilon_0) / 2) * (OCx + OCy + OCz)
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
# Poyntingとの表示を合わせるために、転置を行う。
  ResultArray = ResultArray.T
  return(ResultArray)

# Menu bar commands
def WhatisDOCP():
    print('工事中')

def HowtoUseThis():
    HWindow = Tk()
    HWindow.title("CODE: Optical Chirality 使い方")
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
    LWindow.geometry('350x180')
    LWindow.title("CODE: Optical Chirality ライセンス情報")
    LWindow.minsize(350, 180)
    ttk.Style().theme_use('classic')

    # Main Frame
    Lframe = Frame(LWindow)
    Lframe.pack(fill = BOTH, pady = 10)

    # Making each widget
    LTitle = Label(Lframe, text="CODE: Optical Chirality", font=('Source Han Serif Heavy', '18', 'bold'))
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
    E_READBUTTON = 0 
    M_READBUTTON = 0 # ファイル読み込みボタンの有効化判断用変数 E,M両者が1以上の時、リードボタンが有効化

    def E_ReferenceButton(self):
        
        Ftypes = [("CSVファイル", ".csv"), ("すべてのファイル", ".*")]
        Efile = filedialog.askopenfile(initialdir='./', filetypes=Ftypes)


        if '.csv' not in Efile.name: # 拡張子に.csvが入っていないとき
            error =  messagebox.askyesnocancel("CODE: Optical Chirality", "開こうとしているファイルは拡張子が.csvではありません。\n このファイルを開いてもよろしいですか？")
            if error == False: # いいえを選択したとき
                CM.E_ReferenceButton()
            elif error is None: # キャンセルしたとき
                pass
            else:
                E_Inptfile.set(Efile.name)
                Efile.close
                self.E_READBUTTON = 1
                if self.E_READBUTTON == 1 and self.M_READBUTTON == 1:
                    readb['state'] = 'normal' # 読み込みボタンを有効化

        else: # 拡張子に.csvが入っているとき
            E_Inptfile.set(Efile.name)
            Efile.close
            self.E_READBUTTON = 1
            if self.E_READBUTTON == 1 and self.M_READBUTTON == 1:
                readb['state'] = 'normal' # 読み込みボタンを有効化

    def M_ReferenceButton(self):

        Ftypes = [("CSVファイル", ".csv"), ("すべてのファイル", ".*")]
        Mfile = filedialog.askopenfile(initialdir='./', filetypes=Ftypes)
  

        if '.csv' not in Mfile.name: # 拡張子に.csvが入っていないとき
            error =  messagebox.askyesnocancel("CODE: Optical Chirality", "開こうとしているファイルは拡張子が.csvではありません。\n このファイルを開いてもよろしいですか？")
            if error == False: # いいえを選択したとき
                CM.M_ReferenceButton()
            elif error is None: # キャンセルしたとき
                pass
            else:
                M_Inptfile.set(Mfile.name)
                Mfile.close
            self.M_READBUTTON = 1
            if self.E_READBUTTON == 1 and self.M_READBUTTON == 1:
                readb['state'] = 'normal' # 読み込みボタンを有効化

        else: # 拡張子に.csvが入っているとき
            M_Inptfile.set(Mfile.name)
            Mfile.close
            self.M_READBUTTON = 1
            if self.E_READBUTTON == 1 and self.M_READBUTTON == 1:
                readb['state'] = 'normal' # 読み込みボタンを有効化


    def ReadCSV(self, E_CSVstr, M_CSVstr):

        if E_CSVstr != '' and M_CSVstr != '': #内容のある文字列が渡されたとき
            E_CSVcnt = pd.read_csv(E_CSVstr, header=0) # 電界強度CSVファイル全体をインポート
            M_CSVcnt = pd.read_csv(M_CSVstr, usecols=[' Magnetic Field [mA/m]',' Magnetic Field X-Component [mA/m]',' Magnetic Field Y-Component [mA/m]',
                ' Magnetic Field Z-Component [mA/m]',' Phi(Magnetic Field X-Component) [degree]',' Phi(Magnetic Field Y-Component) [degree]',
                ' Phi(Magnetic Field Z-Component) [degree]'], header=0) # 磁界強度CSVファイル一部をインポート

            # 各種変数をインポート
            Freq = pd.read_csv(E_CSVstr, usecols=['Frequency [GHz]']).values
            Ex = pd.read_csv(E_CSVstr, usecols=[' Electric Field X-Component [mV/m]']).values
            Ey = pd.read_csv(E_CSVstr, usecols=[' Electric Field Y-Component [mV/m]']).values
            Ez = pd.read_csv(E_CSVstr, usecols=[' Electric Field Z-Component [mV/m]']).values
            PhiEx = pd.read_csv(E_CSVstr, usecols=[' Phi(Electric Field X-Component) [degree]']).values
            PhiEy = pd.read_csv(E_CSVstr, usecols=[' Phi(Electric Field Y-Component) [degree]']).values
            PhiEz = pd.read_csv(E_CSVstr, usecols=[' Phi(Electric Field Z-Component) [degree]']).values

            Hx = pd.read_csv(M_CSVstr, usecols=[' Magnetic Field X-Component [mA/m]']).values
            Hy = pd.read_csv(M_CSVstr, usecols=[' Magnetic Field Y-Component [mA/m]']).values
            Hz = pd.read_csv(M_CSVstr, usecols=[' Magnetic Field Z-Component [mA/m]']).values
            PhiHx = pd.read_csv(M_CSVstr, usecols=[' Phi(Magnetic Field X-Component) [degree]']).values
            PhiHy = pd.read_csv(M_CSVstr, usecols=[' Phi(Magnetic Field Y-Component) [degree]']).values
            PhiHz = pd.read_csv(M_CSVstr, usecols=[' Phi(Magnetic Field Z-Component) [degree]']).values

            # mV/mをV/mに変換
            Ex = Ex * 1e-3
            Ey = Ey * 1e-3
            Ez = Ez * 1e-3

            # mA/mをA/mに変換
            Hx = Hx * 1e-3
            Hy = Hy * 1e-3
            Hz = Hz * 1e-3

            # FreqをGHzに変換する
            Freq = Freq * 1e9

            # print(Ex, Ey, Phix, Phiy)

            # 各種変数を計算する
            OCxres = OCx(Ex, Hx, PhiEx, PhiHx)
            OCyres = OCy(Ey, Hy, PhiEy, PhiHy)
            OCzres = OCz(Ez, Hz, PhiEz, PhiHz)
            OptChrres = OptChr(Freq, OCxres, OCyres, OCzres)

            # 行作成
            OCxresDF = pd.DataFrame(OCxres, columns=['Optical Chirality X-Component']) 
            OCyresDF = pd.DataFrame(OCyres, columns=['Optical Chirality Y-Component']) 
            OCzresDF = pd.DataFrame(OCzres, columns=['Optical Chirality Z-Component'])
            OptCherresDF = pd.DataFrame(OptChrres, columns=['Optical Chirality'])

            # 行連結
            CDdata = pd.concat([E_CSVcnt, M_CSVcnt], axis=1)
            CDdata = pd.concat([CDdata, OCxresDF], axis=1)
            CDdata = pd.concat([CDdata, OCyresDF], axis=1)
            CDdata = pd.concat([CDdata, OCzresDF], axis=1)
            CDdata = pd.concat([CDdata, OptCherresDF], axis=1)

            print(CDdata) # 確認用

            self.GCDdata = CDdata # class内変数にCDdataを渡す
            gb['state'] = 'normal' # グラフ描画ボタンを有効化する
            Scsvb['state'] = 'normal' # CSVセーブボタンを有効化する
            self.CSVFileViewer() # CSVビューアを起動

    def GenerateGraph(self):
        # CSVの対象列を格納
        X = self.GCDdata[' X [mm]'].values
        Y = self.GCDdata[' Y [mm]'].values
        C = self.GCDdata['Optical Chirality'].values
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
        plt.colorbar(label='Optical Chirality')
        # 軸ラベル付け
        plt.xlabel("Y [mm]")
        plt.ylabel("X [mm]")
        plt.show()
        
    def SaveCSVFile(self):
        
        # セーブダイアログを出し、セーブ先のパスを取得
        SaveFilePath = filedialog.asksaveasfilename(
            title='名前を付けて保存',
            defaultextension='.csv',
            initialfile='.csv',
            filetypes=[('CSVファイル', '.csv'), ('全てのファイル', '.*')]
            # initialfile=('.csv')
        )

        self.GCDdata.to_csv(SaveFilePath, index=False, encoding='cp932') #  表左端のインデックスを削除して保存

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
        self.tree.grid(row=3, column=0, columnspan=4, sticky= [N, E, W, S])

        # X軸スクロールバーを追加する
        hscrollbar = ttk.Scrollbar(frame1, orient=HORIZONTAL, command=self.tree.xview)
        self.tree.configure(xscrollcommand=lambda f, l: hscrollbar.set(f, l))
        hscrollbar.grid(row=4, column=0,columnspan=4, sticky=(N, E, W))

        # Y軸スクロールバーを追加する
        vscrollbar = ttk.Scrollbar(frame1, orient=VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=vscrollbar.set)
        vscrollbar.grid(row=3, column=5, sticky=(N, W, S))




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
root.title("CODE: Optical Chirality")

# Frame definition
frame1 = ttk.Frame(root, padding=10)
frame1.grid(sticky=(N, E, W, S))
frame1.columnconfigure(0, weight=1)
frame1.rowconfigure(0, weight=1)

root.minsize(1440, 350)

E_Inptfile = StringVar()
M_Inptfile = StringVar()

GCDdata = pd.DataFrame

# Inputed CSV File Path (E-Field)*****************************************
# Label****************************************
Inptlabel = ttk.Label(frame1, text='電界強度のCSVファイルを')
Inptlabel.grid(row=0, column=0, sticky=(W))
# *********************************************
# Path Entry Fourm*****************************
Inptfile_entry = ttk.Entry(
    frame1, textvariable=E_Inptfile, width=200
)
Inptfile_entry.grid(row=0, column=1, columnspan=2, sticky=(E,W))
# *********************************************
# Reference Button*****************************
rb = ttk.Button(
    frame1, text='参照', command=lambda: CM.E_ReferenceButton(), width=8
)
rb.grid(row=0, column=3)
# *********************************************
# *************************************************************

# Inputed CSV File Path (M-Field)*****************************************
# Label****************************************
Inptlabel = ttk.Label(frame1, text='磁界強度のCSVファイルを')
Inptlabel.grid(row=1, column=0, sticky=(W))
# *********************************************
# Path Entry Fourm*****************************
Inptfile_entry = ttk.Entry(
    frame1, textvariable=M_Inptfile, width=200
)
Inptfile_entry.grid(row=1, column=1, columnspan=2, sticky=(E,W))
# *********************************************
# Reference Button*****************************
rb = ttk.Button(
    frame1, text='参照', command=lambda: CM.M_ReferenceButton(), width=8
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
    CommandButtonFrame, text='ファイル読み込み', command=lambda: CM.ReadCSV(E_Inptfile.get(), M_Inptfile.get())
)
if (E_Inptfile.get() == '') or (M_Inptfile.get() == ''): # ファイルパスが無いとき 
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

root.mainloop()