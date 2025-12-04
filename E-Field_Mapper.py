import sys
import re
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.path import Path
from tkinter import (Tk, Menu, Frame, ttk, Label, messagebox, filedialog,
                     StringVar, DoubleVar, IntVar)

# --- 計算用関数 ---
def ExEy(Ex, Ey):
    return np.sqrt(np.power(Ex, 2) + np.power(Ey, 2))

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
                        "4. 「CSVを保存」で結果を保存。\n"
                        "5. グラフウィンドウの保存ボタンで画像も保存できます。")

def show_licence():
    messagebox.showinfo("ライセンス",
                        "電界強度・・・ッ！\n"
                        "バージョン 1.02 (Final)\n"
                        "(C) 2022 小西優一\n"
                        "中央大学 河野研究室")

# --- メインアプリケーションクラス ---
class CSVmanipulator:
    def __init__(self, tree_frame):
        self.GCDdata = pd.DataFrame()
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

    def read_csv(self, CSVstr):
        try:
            if not CSVstr:
                return
            
            CSVcnt = pd.read_csv(CSVstr, header=0)
            CSVhdr = CSVcnt.columns
            try:
                self.unit = re.findall(r'\[(.*m)\]', CSVhdr.values[2])[0]
                spiral_unit_label.config(text=f'({self.unit})')
            except (IndexError, TypeError):
                self.unit = 'a.u.'

            Ex = CSVcnt[' Electric Field X-Component [mV/m]'].values
            Ey = CSVcnt[' Electric Field Y-Component [mV/m]'].values
            Ez = CSVcnt[' Electric Field Z-Component [mV/m]'].values
            ExEyres = ExEy(Ex, Ey)

            CDdata = pd.concat([CSVcnt, pd.DataFrame({
                'SQRT(Ex^2+Ey^2)': ExEyres.flatten(),
                'Ez': Ez.flatten(),
                'Ex': Ex.flatten(),
                'Ey': Ey.flatten()
            })], axis=1)

            self.GCDdata = CDdata
            gb['state'], Scsvb['state'] = 'normal', 'normal'
            self.csv_file_viewer()
        except Exception as e:
            messagebox.showerror("エラー", f"ファイルの処理中にエラーが発生しました:\n{e}")

    def generate_graph(self):
        if self.GCDdata.empty: return

        unit_label_str = self.unit.replace("u", r"$\mu$")
        xlabel, ylabel = f'Y [{unit_label_str}]', f'X [{unit_label_str}]'

        X = self.GCDdata[f' X [{self.unit}]'].values
        Y = self.GCDdata[f' Y [{self.unit}]'].values
        
        # 描画するデータを準備
        data_to_plot = {
            'Ex': self.GCDdata['Ex'].values,
            'Ey': self.GCDdata['Ey'].values,
            'Ez': self.GCDdata['Ez'].values,
            'SQRT(Ex^2+Ey^2)': self.GCDdata['SQRT(Ex^2+Ey^2)'].values
        }
        titles = {
            'Ex': r'$E_x$', 'Ey': r'$E_y$', 'Ez': r'$E_z$',
            'SQRT(Ex^2+Ey^2)': r'$\sqrt{E_x^2+E_y^2}$'
        }
        
        fig, axs = plt.subplots(2, 2, figsize=(10, 10))
        
        # 各サブプロットにヒートマップを描画
        positions = [(0, 1), (1, 0), (1, 1), (0, 0)]
        keys = ['Ex', 'Ey', 'Ez', 'SQRT(Ex^2+Ey^2)']
        
        for ax, key, pos in zip(axs.flat, keys, positions):
            ax_pos = axs[pos[0], pos[1]]
            im = ax_pos.imshow(TwoColumn2Array(X, Y, data_to_plot[key]), cmap='rainbow',
                               extent=(min(Y), max(Y), max(X), min(X)))
            fig.colorbar(im, ax=ax_pos, label='Electric Field [mV/m]')
            ax_pos.set_title(titles[key])
        
        # 全てのサブプロットに透かしと軸設定を適用
        for ax in axs.flat:
            self._draw_watermarks_on_plot(X, Y, ax)
            ax.set_xlabel(xlabel)
            ax.set_ylabel(ylabel)
            ax.set_aspect('equal', adjustable='box')
            ax.set_xlim(min(Y), max(Y))
            ax.set_ylim(max(X), min(X))

        fig.tight_layout()
        plt.savefig("Emap.png")
        plt.show()

    def _draw_watermarks_on_plot(self, X, Y, ax):
        x_center, y_center = (min(Y) + max(Y)) / 2, (min(X) + max(X)) / 2
        
        try: radius = aperture_radius_var.get()
        except Exception: radius = 0

        if radius > 0:
            left, right, bottom, top = ax.get_xlim()[0], ax.get_xlim()[1], ax.get_ylim()[0], ax.get_ylim()[1]
            rect_path = Path([(left, top), (right, top), (right, bottom), (left, bottom), (left, top)])
            circle_path = Path.circle(center=(x_center, y_center), radius=radius)
            # ax.add_patch(patches.PathPatch(Path.make_compound_path(rect_path, circle_path), facecolor='gray', alpha=0.5, linewidth=0))
            ax.add_patch(plt.Circle((x_center, y_center), radius, fill=False, color='black', linestyle='--', linewidth=1.5, alpha=0.9))
        
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
            y_sign = 1.0 if is_lh else -1.0
            base_arm_x, base_arm_y = r * np.cos(theta), y_sign * r * np.sin(theta)

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
                    ax.add_patch(plt.Polygon(verts + [x_center, y_center], color='green', alpha=0.7, linewidth=0))

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
    root.title("電界強度・・・ッ！")
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
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)
    main_frame.columnconfigure(0, weight=1)
    main_frame.rowconfigure(2, weight=1)
    root.minsize(800, 550)

    # --- 変数 ---
    Inptfile = StringVar()
    aperture_radius_var, spiral_spacing_var = DoubleVar(value=10.0), DoubleVar(value=20.0)
    draw_spiral_var, shade_spirals_var = IntVar(value=0), IntVar(value=0)
    spiral_hand_var = StringVar(value='LH')

    # --- レイアウト ---
    file_frame = ttk.Frame(main_frame)
    file_frame.grid(row=0, column=0, sticky='ew', pady=5)
    file_frame.columnconfigure(1, weight=1)
    ttk.Label(file_frame, text='開くファイル:').grid(row=0, column=0, sticky='w')
    ttk.Entry(file_frame, textvariable=Inptfile).grid(row=0, column=1, sticky='ew')
    
    command_frame = ttk.Frame(main_frame)
    command_frame.grid(row=1, column=0, sticky='ew', pady=5)
    
    # --- データ表示エリア ---
    tree_frame = ttk.Frame(main_frame)
    tree_frame.grid(row=2, column=0, sticky='nsew', padx=5, pady=5)
    tree_frame.rowconfigure(0, weight=1)
    tree_frame.columnconfigure(0, weight=1)

    app = CSVmanipulator(tree_frame)

    ttk.Button(file_frame, text='参照', command=app.reference_button, width=8).grid(row=0, column=2, padx=5)
    
    readb = ttk.Button(command_frame, text='ファイル読み込み', state='disabled', command=lambda: app.read_csv(Inptfile.get()))
    readb.pack(side='left', padx=2)
    gb = ttk.Button(command_frame, text='グラフ生成', state='disabled', command=app.generate_graph)
    gb.pack(side='left', padx=2)
    Scsvb = ttk.Button(command_frame, text='CSV保存', state='disabled', command=app.save_csv_file)
    Scsvb.pack(side='left', padx=2)

    # --- 構造物オプション ---
    StructFrame = ttk.LabelFrame(command_frame, text="構造物", padding=5)
    StructFrame.pack(side='left', fill='x', expand=True, padx=10)
    ttk.Label(StructFrame, text='開口半径:').grid(row=0, column=0, sticky='w')
    ttk.Entry(StructFrame, textvariable=aperture_radius_var, width=8).grid(row=0, column=1)
    ttk.Label(StructFrame, text='アーム間距離:').grid(row=0, column=2, sticky='e')
    ttk.Entry(StructFrame, textvariable=spiral_spacing_var, width=8).grid(row=0, column=3)
    spiral_unit_label = ttk.Label(StructFrame, text='(unit)')
    spiral_unit_label.grid(row=0, column=4, sticky='w')
    ttk.Checkbutton(StructFrame, text="螺旋描画", variable=draw_spiral_var).grid(row=1, column=0)
    ttk.Checkbutton(StructFrame, text="網掛け", variable=shade_spirals_var).grid(row=1, column=1)
    ttk.Radiobutton(StructFrame, text="LH", variable=spiral_hand_var, value="LH").grid(row=1, column=2)
    ttk.Radiobutton(StructFrame, text="RH", variable=spiral_hand_var, value="RH").grid(row=1, column=3)

    root.mainloop()