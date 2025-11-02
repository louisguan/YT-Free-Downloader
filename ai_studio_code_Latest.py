import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext, font as tkFont
import subprocess
import threading
import os
import locale
import webbrowser
import sys
from PIL import Image, ImageTk, ImageDraw

class DownloaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("官帥老師YT影片下載神器")
        self.root.geometry("800x720")
        self.root.minsize(750, 800)
        
        self.COLOR_BG = "#FFFBF5"; self.COLOR_DOT = "#E0E0E0"; self.COLOR_PANEL = "#FFFFFF"
        self.COLOR_PRIMARY = "#FF6F00"; self.COLOR_PRIMARY_HOVER = "#FF8F40"
        self.COLOR_TEXT = "#333333"; self.COLOR_TEXT_HEAD = "#000000"
        self.FONT_TITLE = ("Segoe UI", 14, "bold"); self.FONT_BODY = ("Segoe UI", 11)
        self.FONT_BUTTON = ("Segoe UI", 12, "bold")

        try:
            self.base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
            icon_path = os.path.join(self.base_path, 'icon.ico')
            self.root.iconbitmap(icon_path)
        except Exception: print("提醒：找不到 icon.ico 檔案。")
            
        self.bg_canvas = tk.Canvas(self.root); self.bg_canvas.pack(fill="both", expand=True)
        self.root.bind("<Configure>", self._draw_dotted_background)
        main_frame = ttk.Frame(self.bg_canvas, style='App.TFrame', padding=30)
        self.bg_canvas.create_window((0, 0), window=main_frame, anchor="nw", tags="main_frame")
        
        def on_canvas_configure(event): self.bg_canvas.itemconfig("main_frame", width=event.width, height=event.height)
        self.bg_canvas.bind("<Configure>", on_canvas_configure, add="+")

        style = ttk.Style(self.root); style.theme_use('clam')
        # ... (樣式設定與之前相同) ...
        style.configure('.', background=self.COLOR_PANEL, foreground=self.COLOR_TEXT, font=self.FONT_BODY, borderwidth=0)
        style.configure('App.TFrame', background=self.COLOR_PANEL)
        style.configure('TLabel', background=self.COLOR_PANEL, foreground=self.COLOR_TEXT)
        style.configure('TCheckbutton', background=self.COLOR_PANEL, foreground=self.COLOR_TEXT)
        style.map('TCheckbutton', background=[('active', '#f0f0f0')])
        style.configure('TEntry', fieldbackground="#fdfdfd", foreground=self.COLOR_TEXT, borderwidth=1, relief=tk.SOLID)
        style.map('TEntry', bordercolor=[('focus', self.COLOR_PRIMARY)])
        style.configure('TCombobox', fieldbackground="#fdfdfd", foreground=self.COLOR_TEXT, arrowcolor=self.COLOR_TEXT)
        style.map('TCombobox', fieldbackground=[('readonly', "#fdfdfd")])
        style.configure('TLabelframe', background=self.COLOR_PANEL, borderwidth=0)
        style.configure('TLabelframe.Label', background=self.COLOR_PANEL, foreground=self.COLOR_PRIMARY, font=("Segoe UI", 12, "bold"))

        self.process = None; main_frame.columnconfigure(0, weight=1)

        ttk.Label(main_frame, text="影片網址 (一行一個，可貼上多行):", font=self.FONT_TITLE, foreground=self.COLOR_TEXT_HEAD).pack(pady=(5, 5), anchor="w")
        self.url_entry = scrolledtext.ScrolledText(main_frame, height=5, font=("Segoe UI", 11), relief=tk.SOLID, bd=1, bg="#fdfdfd", fg=self.COLOR_TEXT)
        self.url_entry.pack(fill=tk.X, expand=True)
        self.url_entry.bind("<Return>", self._on_url_enter); self.url_entry.bind("<KP_Enter>", self._on_url_enter)

        ttk.Label(main_frame, text="儲存到:", font=self.FONT_TITLE, foreground=self.COLOR_TEXT_HEAD).pack(pady=(15, 5), anchor="w")
        path_frame = ttk.Frame(main_frame, style='App.TFrame'); path_frame.pack(fill=tk.X, expand=True)
        self.path_entry = ttk.Entry(path_frame, font=("Segoe UI", 12)); self.path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=5)
        self.browse_button = ttk.Button(path_frame, text="瀏覽...", command=self.select_folder); self.browse_button.pack(side=tk.RIGHT, padx=(10, 0), ipady=5)
        default_path = os.path.join(os.path.expanduser("~"), "Desktop", "VideoDownloads"); self.path_entry.insert(0, default_path)
        
        options_frame = ttk.LabelFrame(main_frame, text="進階選項", padding="15"); options_frame.pack(fill=tk.X, expand=True, pady=20); options_frame.columnconfigure(1, weight=1)
        
        ttk.Label(options_frame, text="下載格式:").grid(row=0, column=0, sticky="w", padx=5, pady=10)
        self.format_var = tk.StringVar(); self.format_options = {"最高畫質 MP4 (推薦)": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best", "最高畫質 (任何格式)": "bestvideo+bestaudio/best", "僅音訊 (轉換為 MP3)": "bestaudio/best", "僅音訊 (轉換為 M4A)": "bestaudio/best"}; self.format_menu = ttk.Combobox(options_frame, textvariable=self.format_var, values=list(self.format_options.keys()), state="readonly"); self.format_menu.grid(row=0, column=1, sticky="ew", padx=5, pady=10); self.format_menu.current(0)
        
        # --- 核心改造：新增 "使用 cookies.txt" 選項 ---
        ttk.Label(options_frame, text="驗證方式:").grid(row=1, column=0, sticky="w", padx=5, pady=10)
        self.cookie_var = tk.StringVar()
        self.cookie_options = ["不使用 (預設)", "使用 cookies.txt 檔案", "從 Chrome 讀取", "從 Firefox 讀取", "從 Edge 讀取"]
        self.cookie_menu = ttk.Combobox(options_frame, textvariable=self.cookie_var, values=self.cookie_options, state="readonly"); self.cookie_menu.grid(row=1, column=1, sticky="ew", padx=5, pady=10); self.cookie_menu.current(0)
        # --- 改造結束 ---

        self.no_playlist_var = tk.BooleanVar(value=True); ttk.Checkbutton(options_frame, text="僅下載單一影片 (忽略播放清單)", variable=self.no_playlist_var).grid(row=2, column=0, columnspan=2, sticky="w", padx=5, pady=10)
        self.subs_var = tk.BooleanVar(); subs_check = ttk.Checkbutton(options_frame, text="下載字幕", variable=self.subs_var, command=self.toggle_subtitle_options); subs_check.grid(row=3, column=0, sticky="w", padx=5, pady=10)
        subs_options_frame = ttk.Frame(options_frame, style='App.TFrame'); subs_options_frame.grid(row=3, column=1, sticky="ew")
        ttk.Label(subs_options_frame, text="語言:").pack(side=tk.LEFT, padx=(5, 5))
        self.sub_lang_var = tk.StringVar(value="en,zh-Hant"); self.sub_lang_entry = ttk.Entry(subs_options_frame, textvariable=self.sub_lang_var); self.sub_lang_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.embed_subs_var = tk.BooleanVar(); self.embed_subs_check = ttk.Checkbutton(subs_options_frame, text="嵌入字幕", variable=self.embed_subs_var); self.embed_subs_check.pack(side=tk.LEFT, padx=10)
        metadata_frame = ttk.Frame(options_frame, style='App.TFrame'); metadata_frame.grid(row=4, column=0, columnspan=2, sticky="w", padx=5, pady=10)
        self.embed_thumbnail_var = tk.BooleanVar(value=True); ttk.Checkbutton(metadata_frame, text="嵌入縮圖", variable=self.embed_thumbnail_var).pack(side=tk.LEFT)
        self.embed_metadata_var = tk.BooleanVar(); ttk.Checkbutton(metadata_frame, text="嵌入元數據", variable=self.embed_metadata_var).pack(side=tk.LEFT, padx=20)
        
        try:
            icon_path = os.path.join(self.base_path, 'download_icon.png'); self.download_icon = tk.PhotoImage(file=icon_path)
            style.configure('Accent.TButton', font=self.FONT_BUTTON, background=self.COLOR_PRIMARY, foreground='white', borderwidth=0, relief=tk.FLAT, padding=10)
            style.map('Accent.TButton', background=[('active', self.COLOR_PRIMARY_HOVER)])
            self.download_button = ttk.Button(main_frame, text="開始批量下載", command=self.start_download, style='Accent.TButton', image=self.download_icon, compound='left')
        except tk.TclError: self.download_button = ttk.Button(main_frame, text="開始批量下載", command=self.start_download, style='Accent.TButton')
        self.download_button.pack(pady=20, ipadx=30, ipady=8)
        log_area_bg = "#f5f5f5"; log_container = tk.Frame(main_frame, bg=log_area_bg, bd=1, relief=tk.SOLID); log_container.pack(fill=tk.BOTH, expand=True)
        log_container.rowconfigure(0, weight=1); log_container.columnconfigure(1, weight=1)
        try:
            cat_image_path = os.path.join(self.base_path, 'robot_cat.png'); cat_pil_image = Image.open(cat_image_path)
            cat_height = 120; cat_aspect_ratio = cat_pil_image.width / cat_pil_image.height
            cat_width = int(cat_height * cat_aspect_ratio); cat_pil_image = cat_pil_image.resize((cat_width, cat_height), Image.Resampling.LANCZOS)
            self.robot_cat_photo = ImageTk.PhotoImage(cat_pil_image)
            cat_label = tk.Label(log_container, image=self.robot_cat_photo, bg=log_area_bg, bd=0); cat_label.grid(row=0, column=0, sticky='sw', padx=5, pady=5)
            self.status_log = scrolledtext.ScrolledText(log_container, height=8, state='disabled', relief=tk.FLAT, bd=0, font=("Courier New", 10), bg=log_area_bg, fg="#555555"); self.status_log.grid(row=0, column=1, sticky='nsew', pady=1, padx=(0,1))
        except Exception as e:
            log_container.columnconfigure(0, weight=1); self.status_log = scrolledtext.ScrolledText(log_container, height=8, state='disabled', relief=tk.FLAT, bd=0, font=("Courier New", 10), bg=log_area_bg, fg="#555555"); self.status_log.grid(row=0, column=0, sticky='nsew')
            self.log(f"==================== 警告 ====================\n無法載入機器貓圖片 (robot_cat.png)！\n錯誤詳情: {e}\n============================================\n")
        author_frame = ttk.Frame(main_frame, style='App.TFrame'); author_frame.pack(fill=tk.X, pady=(10,0))
        self.author_url = "https://www.facebook.com/guan.shuai.2025/"; author_label = tk.Label(author_frame, text="關於作者: 官帥老師", fg=self.COLOR_PRIMARY, cursor="hand2", bg=self.COLOR_PANEL); author_label.pack(side=tk.RIGHT); underline_font = tkFont.Font(author_label, author_label.cget("font")); underline_font.configure(underline=True); author_label.configure(font=underline_font); author_label.bind("<Button-1>", self.open_author_link)
        self.toggle_subtitle_options()

    def build_command(self, url, path):
        command = ['yt-dlp']
        format_key = self.format_var.get(); format_code = self.format_options[format_key]
        if "僅音訊" in format_key: command.extend(['-x', '--audio-format', 'mp3' if 'MP3' in format_key else 'm4a'])
        command.extend(['-f', format_code, '--merge-output-format', 'mp4'])
        
        # --- 核心改造：處理新的驗證選項 ---
        selected_cookie_option = self.cookie_var.get()
        if selected_cookie_option == "使用 cookies.txt 檔案":
            cookie_file_path = os.path.join(self.base_path, 'cookies.txt')
            if os.path.exists(cookie_file_path):
                command.extend(['--cookies', cookie_file_path])
            else:
                self.log("錯誤：已選擇 '使用 cookies.txt' 但在程式目錄找不到該檔案！\n")
        elif selected_cookie_option != "不使用 (預設)":
            browser = selected_cookie_option.split(' ')[-1].lower()
            command.extend(['--cookies-from-browser', browser])
        # --- 改造結束 ---

        if self.no_playlist_var.get(): command.append('--no-playlist')
        if self.subs_var.get():
            if self.sub_lang_var.get(): command.extend(['--sub-lang', self.sub_lang_var.get()])
            command.append('--write-subs') # 將 --write-subs 移到後面
            if self.embed_subs_var.get(): command.append('--embed-subs')
        if self.embed_thumbnail_var.get(): command.append('--embed-thumbnail')
        if self.embed_metadata_var.get(): command.append('--embed-metadata')
        command.extend(['--progress', '-P', path, url]); return command

    # ... (所有其他函數保持不變) ...
    def _on_url_enter(self, event): self.url_entry.insert(tk.INSERT, "\n"); return "break"
    def _draw_dotted_background(self, event=None):
        width, height = self.bg_canvas.winfo_width(), self.bg_canvas.winfo_height();
        if width < 2 or height < 2: return
        image = Image.new("RGB", (width, height), self.COLOR_BG); draw = ImageDraw.Draw(image)
        dot_spacing = 25
        for x in range(0, width, dot_spacing):
            for y in range(0, height, dot_spacing): draw.point((x, y), fill=self.COLOR_DOT)
        self.dotted_image = ImageTk.PhotoImage(image); self.bg_canvas.create_image(0, 0, anchor="nw", image=self.dotted_image); self.bg_canvas.tag_raise("main_frame")
    def open_author_link(self, event): webbrowser.open_new(self.author_url)
    def select_folder(self):
        folder_selected = filedialog.askdirectory()
        if folder_selected: self.path_entry.delete(0, tk.END); self.path_entry.insert(0, folder_selected)
    def toggle_subtitle_options(self):
        state = 'normal' if self.subs_var.get() else 'disabled'; self.sub_lang_entry.config(state=state); self.embed_subs_check.config(state=state)
    def log(self, message): self.root.after(0, self._log_threadsafe, message)
    def _log_threadsafe(self, message):
        self.status_log.config(state='normal'); self.status_log.insert(tk.END, message)
        self.status_log.see(tk.END); self.status_log.config(state='disabled')
    def start_download(self):
        all_text = self.url_entry.get("1.0", tk.END); urls = [line.strip() for line in all_text.strip().splitlines() if line.strip()]; path = self.path_entry.get().strip()
        if not urls or not path: messagebox.showerror("錯誤", "網址列表和儲存路徑不能為空！"); return
        self.download_button.config(state='disabled'); self.browse_button.config(state='disabled')
        self.status_log.config(state='normal'); self.status_log.delete(1.0, tk.END); self.status_log.config(state='disabled')
        thread = threading.Thread(target=self.run_batch_download, args=(urls, path)); thread.daemon = True; thread.start()
    def run_batch_download(self, urls, path):
        total_tasks, success_count, fail_count = len(urls), 0, 0
        self.log(f"======= 準備開始批量下載，共 {total_tasks} 個任務 =======\n")
        for i, url in enumerate(urls):
            task_num = i + 1; self.log(f"\n--- [任務 {task_num}/{total_tasks}] 開始下載 ---\nURL: {url}\n")
            try:
                command = self.build_command(url, path); self.log(f"▶ 執行的指令: {' '.join(command)}\n")
                command[0] = os.path.join(self.base_path, 'yt-dlp.exe')
                process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding=(locale.getpreferredencoding() or 'utf-8'), errors='replace', creationflags=subprocess.CREATE_NO_WINDOW)
                for line in iter(process.stdout.readline, ''): self.log(line)
                process.wait()
                if process.returncode == 0: self.log(f"--- [任務 {task_num}/{total_tasks}] 下載成功 ---\n"); success_count += 1
                else: self.log(f"--- [任務 {task_num}/{total_tasks}] 下載失敗 ---\n"); fail_count += 1
            except Exception as e: self.log(f"--- [任務 {task_num}/{total_tasks}] 發生嚴重錯誤: {e} ---\n"); fail_count += 1
        self.log(f"\n======= 所有批量任務已完成 =======\n成功: {success_count} 個, 失敗: {fail_count} 個\n")
        self.root.after(0, messagebox.showinfo, "批量下載完成", f"所有任務已結束。\n\n成功: {success_count}\n失敗: {fail_count}")
        self.root.after(0, self.reset_ui)
    def reset_ui(self): self.download_button.config(state='normal'); self.browse_button.config(state='normal')

if __name__ == "__main__":
    root = tk.Tk()
    app = DownloaderApp(root)
    root.mainloop()
