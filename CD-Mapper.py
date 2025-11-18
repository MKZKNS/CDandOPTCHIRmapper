import sys
import re
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.path import Path
from tkinter import (Tk, Menu, Frame, ttk, Label, messagebox, filedialog,
                     StringVar, DoubleVar, IntVar)

# --- 計算用関数群 ---
def S1(Ex, Ey):
    return np.power(Ex, 2) - np.power(Ey, 2)

def S2(Ex, Ey, Phiy, Phix):
    return 2 * Ex * Ey * np.cos((Phiy - Phix) * np.pi / 180)

def S3(Ex, Ey, Phiy, Phix):
    return 2 * Ex * Ey * np.sin((Phiy - Phix) * np.pi / 180)

def S0(Ex, Ey):
    return np.power(Ex, 2) + np.power(Ey, 2)

def C(S3, S0):
    return np.divide(S3, S0, out=np.zeros_like(S3, dtype=float), where=S0 != 0)

def opt_rot(S2, S1):
    return np.rad2deg(0.5 * np.arctan2(S2, S1))

def opt_rot_rembg(S2, S1, offset):
    angle_map = {0: 0, 1: -np.pi / 2, 2: -np.pi, 3: -3 * np.pi / 2}
    angle = angle_map.get(offset, 0)
    rotx = S1 * np.cos(angle) - S2 * np.sin(angle)
    roty = S1 * np.sin(angle) + S2 * np.cos(angle)
    return np.rad2deg(0.5 * np.arctan2(roty, rotx))

def TwoColumn2Array(X, Y, C):
    x, y = np.unique(X), np.unique(Y)
    ResultArray = np.empty((y.size, x.size))
    k = 0
    for i in range(y.size):
        for j in range(x.size):
            ResultArray[i, j] = C[k]
            k += 1
    return ResultArray.T

# --- ヘルプメニュー用関数 ---
def show_how_to_use():
    messagebox.showinfo("使い方",
                        "1. 「参照」ボタンでCSVファイルを選択。\n"
                        "2. 「ファイル読み込み」でデータを計算。\n"
                        "3. オプションを選んで「グラフ生成」。\n"
                        "4. 「CSV保存」で結果を保存。\n"
                        "5. グラフウィンドウの保存ボタンで画像も保存できます。")

def show_licence():
    messagebox.showinfo("ライセンス",
                        "えんへんこうっ！ with 旋光度\n"
                        "バージョン 1.06 (Final)\n"
                        "(C) 2022 小西優一\n"
                        "中央大学 河野研究室")

# --- メインアプリケーションクラス ---
class CSVmanipulator:
    def __init__(self, tree_frame):
        self.GCDdata = pd.DataFrame()
        self.BGflag = 0
        self.unit = ' '
        self.tree_frame = tree_frame

    def _file_dialog(self, entry_var):
        file = filedialog.askopenfile(initialdir='./', filetypes=[("CSVファイル", ".csv"), ("すべてのファイル", ".*")])
        if file:
            entry_var.set(file.name)
            readb['state'] = 'normal'
            file.close()

    def reference_button(self):
        self._file_dialog(Inptfile)

    def bg_button(self):
        self._file_dialog(BGfile)

    def read_csv(self, CSVstr, BGstr):
        try:
            if not CSVstr: return
            
            CSVcnt = pd.read_csv(CSVstr, header=0)
            CSVhdr = CSVcnt.columns
            try:
                self.unit = re.findall(r'\[(.*m)\]', CSVhdr.values[2])[0]
                spiral_unit_label.config(text=f'({self.unit})')
            except (IndexError, TypeError): self.unit = 'a.u.'
            
            Ex = CSVcnt[' Electric Field X-Component [mV/m]'].values * 1e-3
            Ey = CSVcnt[' Electric Field Y-Component [mV/m]'].values * 1e-3
            Phix = CSVcnt[' Phi(Electric Field X-Component) [degree]'].values
            Phiy = CSVcnt[' Phi(Electric Field Y-Component) [degree]'].values
            S0res, S1res, S2res, S3res = S0(Ex, Ey), S1(Ex, Ey), S2(Ex, Ey, Phiy, Phix), S3(Ex, Ey, Phiy, Phix)
            CDdata = pd.concat([CSVcnt, pd.DataFrame({
                'S0': S0res.flatten(), 'S1': S1res.flatten(), 'S2': S2res.flatten(), 'S3': S3res.flatten(),
                'サンプルの円偏光度': C(S3res, S0res).flatten(), 'サンプルの旋光度': opt_rot(S2res, S1res).flatten()
            })], axis=1)
            
            self.BGflag = 0
            if BGstr:
                BGcnt = pd.read_csv(BGstr, header=0)
                BG_Ex, BG_Ey = BGcnt[' Electric Field X-Component [mV/m]'].values * 1e-3, BGcnt[' Electric Field Y-Component [mV/m]'].values * 1e-3
                BG_Phix, BG_Phiy = BGcnt[' Phi(Electric Field X-Component) [degree]'].values, BGcnt[' Phi(Electric Field Y-Component) [degree]'].values
                BG_S0res, BG_S1res, BG_S2res, BG_S3res = S0(BG_Ex, BG_Ey), S1(BG_Ex, BG_Ey), S2(BG_Ex, BG_Ey, BG_Phiy, BG_Phix), S3(BG_Ex, BG_Ey, BG_Phiy, BG_Phix)
                CDdata = pd.concat([CDdata, pd.DataFrame({
                    'サンプル-Refの円偏光度': (C(S3res, S0res) - C(BG_S3res, BG_S0res)).flatten(),
                    'サンプル-定義したRefの旋光度': opt_rot_rembg(S2res, S1res, optrdovar.get()).flatten()
                })], axis=1)
                self.BGflag = 1

            self.GCDdata = CDdata
            gb['state'], Scsvb['state'] = 'normal', 'normal'
            self.csv_file_viewer()
        except Exception as e: messagebox.showerror("エラー", f"ファイルの処理中にエラーが発生しました:\n{e}")

    def generate_graph(self):
        if self.GCDdata.empty: return

        unit_label_str = self.unit.replace("u", r"$\mu$")
        xlabel, ylabel = f'Y [{unit_label_str}]', f'X [{unit_label_str}]'
        
        self._draw_heatmap_with_watermarks(xlabel, ylabel)
            
    def _draw_heatmap_with_watermarks(self, xlabel, ylabel):
        if or_cd_var.get() == 0:
            col, label_text_base, ref_col, vmin_max, vmax_max = ('サンプルの円偏光度', 'DOCP', 'サンプル-Refの円偏光度', -1, 1)
        else:
            col, label_text_base, ref_col, vmin_max, vmax_max = ('サンプルの旋光度', 'Optical Rotation [degrees]', 'サンプル-定義したRefの旋光度', -90, 90)
        
        C = self.GCDdata[ref_col] if self.BGflag else self.GCDdata[col]
        label_text = label_text_base + (' (Ref removed)' if self.BGflag else '')
        limit = max(abs(C.min()), abs(C.max()))
        vmin, vmax = (vmin_max, vmax_max) if rdovar.get() == 0 else (-limit, limit)
        
        X = self.GCDdata[f' X [{self.unit}]'].values
        Y = self.GCDdata[f' Y [{self.unit}]'].values
        
        plt.figure()
        plt.imshow(TwoColumn2Array(X, Y, C.values), cmap='bwr', extent=(min(Y), max(Y), max(X), min(X)), vmin=vmin, vmax=vmax)
        self._draw_watermarks_on_plot(X, Y)
        plt.colorbar(label=label_text)
        
        ax = plt.gca()
        ax.set_xlabel(xlabel); ax.set_ylabel(ylabel)
        ax.set_aspect('equal', adjustable='box')
        ax.set_xlim(min(Y), max(Y)); ax.set_ylim(max(X), min(X))
        
        plt.tight_layout()
        plt.show()

    def _draw_watermarks_on_plot(self, X, Y):
        ax = plt.gca()
        x_center, y_center = (min(Y) + max(Y)) / 2, (min(X) + max(X)) / 2
        
        try: radius = aperture_radius_var.get()
        except Exception: radius = 0

        # ★★★ 開口部外側の背景網掛け（最終修正版） ★★★
        if radius > 0:
            left, right = min(Y), max(Y)
            top, bottom = min(X), max(X)
            
            # # 描画領域全体を覆う四角形のパス（時計回り）と、くり抜く円のパス（反時計回り）を作成
            # rect_path = Path([(left, top), (right, top), (right, bottom), (left, bottom), (left, top)])
            # circle_path = Path.circle(center=(x_center, y_center), radius=radius)
            
            # # 2つのパスを合成して、中央に穴の空いた図形を作成
            # compound_path = Path.make_compound_path(rect_path, circle_path)
            # ax.add_patch(patches.PathPatch(compound_path, facecolor='gray', alpha=0.2, linewidth=0))
        
        # --- 開口部の境界線 ---
        if radius > 0:
            ax.add_patch(plt.Circle((x_center, y_center), radius, fill=False, color='black', linestyle='--', linewidth=1.5, alpha=0.9))
        
        # --- 螺旋の描画 ---
        if draw_spiral_var.get() == 1:
            try:
                spacing = spiral_spacing_var.get()
                if spacing <= 0: return
            except Exception: return
            
            a = spacing / np.pi
            x_max_dist = 2 * max(abs(min(Y) - x_center), abs(max(Y) - x_center))
            y_max_dist = 2 * max(abs(min(X) - y_center), abs(max(X) - y_center))
            theta_max = np.sqrt(x_max_dist**2 + y_max_dist**2) / a if a > 0 else 0
            theta_min = radius / a if radius > 0 and a > 0 else 0
            if theta_min >= theta_max: return
            
            theta = np.linspace(theta_min, theta_max, 1500)
            r = a * theta
            is_lh = spiral_hand_var.get() == 'LH'
            base_arm_x, base_arm_y = r * np.cos(theta), (1.0 if is_lh else -1.0) * r * np.sin(theta)

            arms_rel = [(base_arm_x, base_arm_y), (-base_arm_y, base_arm_x), (-base_arm_x, -base_arm_y), (base_arm_y, -base_arm_x)] if is_lh else \
                       [(base_arm_x, base_arm_y), (base_arm_y, -base_arm_x), (-base_arm_x, -base_arm_y), (-base_arm_y, base_arm_x)]
            arc_angles = [(theta_min, theta_min + np.pi/2), (theta_min + np.pi, theta_min + 3*np.pi/2)] if is_lh else \
                         [(-theta_min, -theta_min - np.pi/2), (-theta_min - np.pi, -theta_min - 3*np.pi/2)]

            if shade_spirals_var.get() == 1:
                polygons_data = [(arms_rel[0], arms_rel[1], arc_angles[0]), (arms_rel[2], arms_rel[3], arc_angles[1])]
                for arm_a, arm_b, (t_start, t_end) in polygons_data:
                    verts = np.vstack([np.column_stack(arm_a), np.column_stack(arm_b)[::-1]])
                    if radius > 0:
                        arc_theta = np.linspace(t_end, t_start, 50)
                        arc_pts = np.column_stack([radius * np.cos(arc_theta), radius * np.sin(arc_theta)])
                        verts = np.vstack([verts, arc_pts])
                    ax.add_patch(plt.Polygon(verts + [x_center, y_center], color='green', alpha=0.4, linewidth=0))

            for x_arm, y_arm in arms_rel:
                ax.plot(x_arm + x_center, y_arm + y_center, color='gray', linestyle=':', linewidth=1.2)

    def save_csv_file(self):
        if not self.GCDdata.empty:
            if SaveFilePath := filedialog.asksaveasfilename(title='名前を付けて保存', defaultextension='.csv', initialfile='result.csv', filetypes=[('CSVファイル', '.csv')]):
                self.GCDdata.to_csv(SaveFilePath, index=False, encoding='cp932')

    def csv_file_viewer(self):
        for widget in self.tree_frame.winfo_children():
            widget.destroy()
        
        tree = ttk.Treeview(self.tree_frame, show='headings', columns=list(self.GCDdata.columns))
        for col in self.GCDdata.columns:
            tree.heading(col, text=col)
            tree.column(col, width=100, anchor='center')
        for i, row in self.GCDdata.iterrows():
            tree.insert("", "end", values=list(row))
        
        hscroll = ttk.Scrollbar(self.tree_frame, orient='horizontal', command=tree.xview)
        vscroll = ttk.Scrollbar(self.tree_frame, orient='vertical', command=tree.yview)
        tree.configure(xscrollcommand=hscroll.set, yscrollcommand=vscroll.set)
        
        tree.grid(row=0, column=0, sticky='nsew')
        hscroll.grid(row=1, column=0, sticky='ew')
        vscroll.grid(row=0, column=1, sticky='ns')

# --- GUI設定 ---
if __name__ == "__main__":
    root = Tk()
    root.title("えんへんこうっ！ with 旋光度")
    s = ttk.Style()
    s.theme_use('classic')
    
    menubar = Menu(root)
    filemenu = Menu(menubar, tearoff=0)
    filemenu.add_command(label='閉じる', command=sys.exit)
    helpmenu = Menu(menubar, tearoff=0)
    helpmenu.add_command(label='使い方', command=show_how_to_use)
    helpmenu.add_separator()
    helpmenu.add_command(label='ライセンス', command=show_licence)
    menubar.add_cascade(label='ファイル', menu=filemenu)
    menubar.add_cascade(label='ヘルプ', menu=helpmenu)
    root.config(menu=menubar)
    
    main_frame = ttk.Frame(root, padding=10)
    main_frame.grid(sticky='nsew')
    root.columnconfigure(0, weight=1); root.rowconfigure(0, weight=1)
    main_frame.columnconfigure(1, weight=1); main_frame.rowconfigure(3, weight=1)
    root.minsize(900, 550)

    Inptfile, BGfile = StringVar(), StringVar()
    aperture_radius_var, spiral_spacing_var = DoubleVar(value=10.0), DoubleVar(value=20.0)
    draw_spiral_var, shade_spirals_var = IntVar(value=0), IntVar(value=0)
    rdovar, or_cd_var, optrdovar = IntVar(value=0), IntVar(value=0), IntVar(value=0)
    spiral_hand_var = StringVar(value='LH')

    ttk.Label(main_frame, text='開くファイル:').grid(row=0, column=0, sticky='w', pady=2)
    ttk.Entry(main_frame, textvariable=Inptfile).grid(row=0, column=1, columnspan=2, sticky='ew')
    ttk.Label(main_frame, text='Ref用ファイル:').grid(row=1, column=0, sticky='w', pady=2)
    ttk.Entry(main_frame, textvariable=BGfile).grid(row=1, column=1, columnspan=2, sticky='ew')
    
    CommandFrame = ttk.Frame(main_frame, padding=(0, 10))
    CommandFrame.grid(row=2, column=0, columnspan=4, sticky='ew')
    
    OptionFrame = ttk.LabelFrame(CommandFrame, text="オプション", padding=5)
    OptionFrame.pack(side='left', padx=10, fill='x', expand=True)
    ttk.Label(OptionFrame, text='マップ:').grid(row=0, column=0)
    ttk.Radiobutton(OptionFrame, value=0, variable=or_cd_var, text="円偏光度").grid(row=0, column=1)
    ttk.Radiobutton(OptionFrame, value=1, variable=or_cd_var, text="旋光度").grid(row=0, column=2)
    ttk.Label(OptionFrame, text='範囲:').grid(row=1, column=0)
    ttk.Radiobutton(OptionFrame, value=0, variable=rdovar, text="固定").grid(row=1, column=1)
    ttk.Radiobutton(OptionFrame, value=1, variable=rdovar, text="自動").grid(row=1, column=2)

    StructFrame = ttk.LabelFrame(CommandFrame, text="構造物", padding=5)
    StructFrame.pack(side='left', fill='x', expand=True)
    ttk.Label(StructFrame, text='開口半径:').grid(row=0, column=0, sticky='w')
    ttk.Entry(StructFrame, textvariable=aperture_radius_var, width=8).grid(row=0, column=1)
    ttk.Label(StructFrame, text='アーム間距離:').grid(row=0, column=2, sticky='e')
    ttk.Entry(StructFrame, textvariable=spiral_spacing_var, width=8).grid(row=0, column=3)
    spiral_unit_label = ttk.Label(StructFrame, text='(unit)'); spiral_unit_label.grid(row=0, column=4, sticky='w')
    ttk.Checkbutton(StructFrame, text="螺旋描画", variable=draw_spiral_var).grid(row=1, column=0)
    ttk.Checkbutton(StructFrame, text="網掛け", variable=shade_spirals_var).grid(row=1, column=1)
    ttk.Radiobutton(StructFrame, text="LH", variable=spiral_hand_var, value="LH").grid(row=1, column=2)
    ttk.Radiobutton(StructFrame, text="RH", variable=spiral_hand_var, value="RH").grid(row=1, column=3)

    IncidentFrame = ttk.LabelFrame(CommandFrame, text="入射偏光", padding=5)
    IncidentFrame.pack(side='left', padx=10, fill='x')
    for i, txt in enumerate(["0° (X)", "45°", "90° (Y)", "135°"]):
        ttk.Radiobutton(IncidentFrame, value=i, variable=optrdovar, text=txt).pack(anchor='w')
    
    tree_frame = ttk.Frame(main_frame)
    tree_frame.grid(row=3, column=0, columnspan=4, sticky='nsew', padx=5, pady=5)
    tree_frame.rowconfigure(0, weight=1)
    tree_frame.columnconfigure(0, weight=1)

    app = CSVmanipulator(tree_frame)

    ttk.Button(main_frame, text='参照', command=app.reference_button, width=8).grid(row=0, column=3, padx=5)
    ttk.Button(main_frame, text='参照', command=app.bg_button, width=8).grid(row=1, column=3, padx=5)
    
    readb = ttk.Button(CommandFrame, text='ファイル読み込み', state='disabled', command=lambda: app.read_csv(Inptfile.get(), BGfile.get()))
    readb.pack(side='left', padx=2)
    gb = ttk.Button(CommandFrame, text='グラフ生成', state='disabled', command=app.generate_graph)
    gb.pack(side='left', padx=2)
    Scsvb = ttk.Button(CommandFrame, text='CSV保存', state='disabled', command=app.save_csv_file)
    Scsvb.pack(side='left', padx=2)

    root.mainloop()