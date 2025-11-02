import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import subprocess
import threading
import os
import locale

class DownloaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("官帥老師YT影片下載神器")
        
        # --- 設定視窗圖示 (這是新增的一行) ---
        # 這會讓視窗左上角和工作列顯示你的 Logo
        try:
            self.root.iconbitmap('icon.ico')
        except tk.TclError:
            print("提醒：找不到 icon.ico 檔案，將使用預設圖示。")
        # ------------------------------------

        self.root.geometry("750x650")
        self.root.minsize(750, 600)

        self.process = None

        # ... (程式碼的其餘部分與之前完全相同) ...
        main_frame = ttk.Frame(root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        ttk.Label(main_frame, text="影片網址:", font=("Arial", 12)).pack(pady=(5, 2), anchor="w")
        self.url_entry = ttk.Entry(main_frame, width=80, font=("Arial", 11))
        self.url_entry.pack(fill=tk.X, expand=True)
        ttk.Label(main_frame, text="儲存到:", font=("Arial", 12)).pack(pady=(10, 2), anchor="w")
        path_frame = ttk.Frame(main_frame)
        path_frame.pack(fill=tk.X, expand=True)
        self.path_entry = ttk.Entry(path_frame, font=("Arial", 11))
        self.path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.browse_button = ttk.Button(path_frame, text="瀏覽...", command=self.select_folder)
        self.browse_button.pack(side=tk.RIGHT, padx=(5, 0))
        default_path = os.path.join(os.path.expanduser("~"), "Desktop", "VideoDownloads")
        self.path_entry.insert(0, default_path)
        options_frame = ttk.LabelFrame(main_frame, text="進階選項", padding="10")
        options_frame.pack(fill=tk.X, expand=True, pady=15)
        ttk.Label(options_frame, text="下載格式:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.format_var = tk.StringVar()
        self.format_options = {
            "最高畫質 MP4 (推薦)": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
            "最高畫質 (任何格式)": "bestvideo+bestaudio/best",
            "僅音訊 (轉換為 MP3)": "bestaudio/best",
            "僅音訊 (轉換為 M4A)": "bestaudio/best"
        }
        self.format_menu = ttk.Combobox(options_frame, textvariable=self.format_var, values=list(self.format_options.keys()), state="readonly")
        self.format_menu.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        self.format_menu.current(0)
        self.no_playlist_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="僅下載單一影片 (忽略播放清單)", variable=self.no_playlist_var).grid(row=1, column=0, columnspan=2, sticky="w", padx=5, pady=5)
        self.subs_var = tk.BooleanVar()
        subs_check = ttk.Checkbutton(options_frame, text="下載字幕", variable=self.subs_var, command=self.toggle_subtitle_options)
        subs_check.grid(row=2, column=0, sticky="w", padx=5, pady=5)
        subs_options_frame = ttk.Frame(options_frame)
        subs_options_frame.grid(row=2, column=1, sticky="ew")
        ttk.Label(subs_options_frame, text="語言 (例如 en,zh-Hant):").pack(side=tk.LEFT, padx=(0, 5))
        self.sub_lang_var = tk.StringVar(value="en,zh-Hant")
        self.sub_lang_entry = ttk.Entry(subs_options_frame, textvariable=self.sub_lang_var)
        self.sub_lang_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.embed_subs_var = tk.BooleanVar()
        self.embed_subs_check = ttk.Checkbutton(subs_options_frame, text="嵌入字幕", variable=self.embed_subs_var)
        self.embed_subs_check.pack(side=tk.LEFT, padx=5)
        metadata_frame = ttk.Frame(options_frame)
        metadata_frame.grid(row=3, column=0, columnspan=2, sticky="w", padx=5, pady=5)
        self.embed_thumbnail_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(metadata_frame, text="嵌入縮圖", variable=self.embed_thumbnail_var).pack(side=tk.LEFT)
        self.embed_metadata_var = tk.BooleanVar()
        ttk.Checkbutton(metadata_frame, text="嵌入元數據", variable=self.embed_metadata_var).pack(side=tk.LEFT, padx=10)
        self.download_button = ttk.Button(main_frame, text="開始下載", command=self.start_download, style='Accent.TButton')
        self.download_button.pack(pady=15, ipadx=20, ipady=8)
        self.status_log = scrolledtext.ScrolledText(main_frame, height=10, state='disabled', bg="#f0f0f0", relief=tk.SOLID, bd=1)
        self.status_log.pack(fill=tk.BOTH, expand=True)
        self.toggle_subtitle_options()
        style = ttk.Style(root)
        style.configure('Accent.TButton', font=('Arial', 12, 'bold'))
    def select_folder(self):
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.path_entry.delete(0, tk.END)
            self.path_entry.insert(0, folder_selected)
    def toggle_subtitle_options(self):
        state = 'normal' if self.subs_var.get() else 'disabled'
        self.sub_lang_entry.config(state=state)
        self.embed_subs_check.config(state=state)
    def log(self, message):
        self.root.after(0, self._log_threadsafe, message)
    def _log_threadsafe(self, message):
        self.status_log.config(state='normal')
        self.status_log.insert(tk.END, message)
        self.status_log.see(tk.END)
        self.status_log.config(state='disabled')
    def build_command(self, url, path):
        command = ['yt-dlp']
        selected_format_key = self.format_var.get()
        format_code = self.format_options[selected_format_key]
        if "僅音訊" in selected_format_key:
            command.extend(['-x', '--audio-format', 'mp3' if 'MP3' in selected_format_key else 'm4a'])
        command.extend(['-f', format_code])
        command.extend(['--merge-output-format', 'mp4'])
        if self.no_playlist_var.get():
            command.append('--no-playlist')
        if self.subs_var.get():
            command.append('--write-subs')
            if self.sub_lang_var.get():
                command.extend(['--sub-lang', self.sub_lang_var.get()])
            if self.embed_subs_var.get():
                command.append('--embed-subs')
        if self.embed_thumbnail_var.get():
            command.append('--embed-thumbnail')
        if self.embed_metadata_var.get():
            command.append('--embed-metadata')
        command.extend(['--progress', '-P', path, url])
        return command
    def start_download(self):
        url = self.url_entry.get().strip()
        path = self.path_entry.get().strip()
        if not url or not path:
            messagebox.showerror("錯誤", "網址和儲存路徑不能為空！")
            return
        self.download_button.config(state='disabled', text="下載中...")
        self.browse_button.config(state='disabled')
        self.status_log.config(state='normal')
        self.status_log.delete(1.0, tk.END)
        self.status_log.config(state='disabled')
        command = self.build_command(url, path)
        self.log("▶ 執行的指令: " + " ".join(f'"{arg}"' if " " in arg else arg for arg in command) + "\n\n")
        thread = threading.Thread(target=self.run_download_process, args=(command,))
        thread.daemon = True
        thread.start()
    def run_download_process(self, command):
        try:
            os.makedirs(self.path_entry.get().strip(), exist_ok=True)
            system_encoding = locale.getpreferredencoding() or 'utf-8'
            self.process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                text=True, 
                encoding=system_encoding,
                errors='replace',
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            for line in iter(self.process.stdout.readline, ''):
                self.log(line)
            self.process.wait()
            if self.process.returncode == 0:
                self.log("\n" + "-" * 40 + "\n✅ 下載成功！\n")
                self.root.after(0, messagebox.showinfo, "完成", "影片下載成功！")
            else:
                self.log(f"\n" + "-" * 40 + f"\n❌ 下載失敗，返回碼: {self.process.returncode}\n")
                self.root.after(0, messagebox.showerror, "錯誤", "下載過程中發生錯誤，請檢查日誌輸出。")
        except FileNotFoundError as e:
            msg = f"錯誤：找不到 '{e.filename}'。\n請確保 yt-dlp.exe 和 ffmpeg.exe 與主程式在同一個資料夾中。\n"
            self.log(msg)
            self.root.after(0, messagebox.showerror, "依賴缺失", msg)
        except Exception as e:
            self.log(f"發生未預期的錯誤: {e}\n")
            self.root.after(0, messagebox.showerror, "嚴重錯誤", f"發生未預期的錯誤: {e}")
        finally:
            self.root.after(0, self.reset_ui)
    def reset_ui(self):
        self.download_button.config(state='normal', text="開始下載")
        self.browse_button.config(state='normal')

if __name__ == "__main__":
    root = tk.Tk()
    app = DownloaderApp(root)
    root.mainloop()
