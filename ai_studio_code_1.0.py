# --- downloader_app.py (更新版) ---
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import subprocess
import threading
import os

class DownloaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("影片下載器 (yt-dlp)")
        self.root.geometry("700x500")
        self.root.resizable(False, True)

        self.process = None

        tk.Label(root, text="影片網址:", font=("Arial", 12)).pack(pady=(10, 0))
        self.url_entry = tk.Entry(root, width=70, font=("Arial", 11))
        self.url_entry.pack(padx=20, fill=tk.X)

        tk.Label(root, text="儲存到:", font=("Arial", 12)).pack(pady=(10, 0))
        path_frame = tk.Frame(root)
        path_frame.pack(padx=20, fill=tk.X)
        self.path_entry = tk.Entry(path_frame, width=55, font=("Arial", 11))
        self.path_entry.pack(side=tk.LEFT, expand=True, fill=tk.X)
        self.browse_button = tk.Button(path_frame, text="瀏覽...", command=self.select_folder)
        self.browse_button.pack(side=tk.RIGHT, padx=(5, 0))

        default_path = os.path.join(os.path.expanduser("~"), "Desktop", "VideoDownloads")
        self.path_entry.insert(0, default_path)

        self.download_button = tk.Button(root, text="開始下載", font=("Arial", 12, "bold"), bg="#4CAF50", fg="white", command=self.start_download)
        self.download_button.pack(pady=20, ipadx=10, ipady=5)

        tk.Label(root, text="下載進度:", font=("Arial", 12)).pack()
        self.status_log = scrolledtext.ScrolledText(root, height=15, width=80, state='disabled', bg="#f0f0f0")
        self.status_log.pack(padx=20, pady=10, expand=True, fill=tk.BOTH)

    def select_folder(self):
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.path_entry.delete(0, tk.END)
            self.path_entry.insert(0, folder_selected)

    def log(self, message):
        self.status_log.config(state='normal')
        self.status_log.insert(tk.END, message)
        self.status_log.see(tk.END)
        self.status_log.config(state='disabled')
        self.root.update_idletasks()

    def start_download(self):
        url = self.url_entry.get().strip()
        path = self.path_entry.get().strip()

        if not url or not path:
            messagebox.showerror("錯誤", "網址和儲存路徑不能為空！")
            return

        self.download_button.config(state='disabled', text="下載中...", bg="#FF9800")
        self.browse_button.config(state='disabled')
        
        self.status_log.config(state='normal')
        self.status_log.delete(1.0, tk.END)
        self.status_log.config(state='disabled')

        thread = threading.Thread(target=self.run_download_process, args=(url, path))
        thread.daemon = True
        thread.start()

    def run_download_process(self, url, path):
        try:
            os.makedirs(path, exist_ok=True)
            self.log(f"準備下載: {url}\n")
            self.log(f"儲存位置: {path}\n")
            self.log("-" * 40 + "\n")

            command = [
                'yt-dlp', '--no-playlist',
                '-f', 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
                '--merge-output-format', 'mp4',
                '--progress', '-P', path, url
            ]
            
            # 【關鍵修改】新增 errors='replace' 來避免程式因編碼錯誤而崩潰
            self.process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                text=True, encoding='utf-8', errors='replace', # <--- 修改在這裡
                creationflags=subprocess.CREATE_NO_WINDOW
            )

            for line in iter(self.process.stdout.readline, ''):
                self.log(line)
            
            self.process.wait()

            if self.process.returncode == 0:
                self.log("\n" + "-" * 40 + "\n✅ 下載成功！\n")
                messagebox.showinfo("完成", "影片下載成功！")
            else:
                self.log(f"\n" + "-" * 40 + f"\n❌ 下載失敗，返回碼: {self.process.returncode}\n")
                messagebox.showerror("錯誤", "下載過程中發生錯誤，請檢查日誌輸出。")

        except FileNotFoundError as e:
            # 檢查是哪個檔案找不到
            missing_file = e.filename if e.filename else "依賴檔案"
            self.log(f"錯誤：找不到 '{missing_file}'。\n請確保所有依賴 (yt-dlp.exe, ffmpeg.exe) 都與主程式在同一個資料夾中。\n")
            messagebox.showerror("依賴缺失", f"找不到 {missing_file}！請將它放置在與主程式相同的資料夾中。")
        except Exception as e:
            self.log(f"發生未預期的錯誤: {e}\n")
            messagebox.showerror("嚴重錯誤", f"發生未預期的錯誤: {e}")
        finally:
            self.download_button.config(state='normal', text="開始下載", bg="#4CAF50")
            self.browse_button.config(state='normal')

if __name__ == "__main__":
    root = tk.Tk()
    app = DownloaderApp(root)
    root.mainloop()