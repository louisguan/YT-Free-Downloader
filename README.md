# 官帥老師YT影片下載神器

![Windows](https://img.shields.io/badge/Platform-Windows-0078D6?style=for-the-badge&logo=windows)
![Python](https://img.shields.io/badge/Python-3.x-3776AB?style=for-the-badge&logo=python)
![GUI](https://img.shields.io/badge/GUI-Tkinter-orange?style=for-the-badge)

這是一款專為 Windows 使用者設計的、擁有現代化圖形介面 (GUI) 的影片下載工具。它基於強大的命令列工具 `yt-dlp` 進行封裝，讓任何人都能輕鬆、直觀地從數百個網站下載影片和音訊，無需記憶任何複雜的指令。

<!-- 請將此處的截圖換成您程式的實際執行畫面 -->
![應用程式截圖](<img width="800" height="841" alt="image" src="https://github.com/user-attachments/assets/96a573df-9059-42e9-8185-72931a7b5fd6" />) 

## ✨ 主要功能

*   **直觀的圖形介面**：告別黑色命令列，所有操作皆在圖形化視窗中完成。
*   **批量下載**：支援貼上多行影片網址，程式會自動將它們加入佇列並逐一下載。
*   **多樣的格式選擇**：
    *   下載最高畫質的影片並自動合併為 **MP4** 檔案。
    *   一鍵下載並轉換為純音訊 **MP3** 或 **M4A** 檔案。
*   **智慧驗證處理**：
    *   有效繞過 YouTube 的「機器人驗證」和年齡限制。
    *   支援**自動讀取瀏覽器 Cookie**，模擬登入狀態。
    *   支援**手動載入 `cookies.txt`** 檔案，解決最頑固的權限問題。
*   **進階下載選項**：
    *   支援下載影片字幕，並可選擇性地將字幕嵌入影片中。
    *   可選擇是否嵌入影片封面縮圖和元數據。
    *   智慧忽略播放清單，只下載網址指向的單一影片。
*   **個性化介面**：擁有清爽的點陣背景、醒目的操作按鈕和可愛的機器貓吉祥物，提供愉悅的使用體驗。

## 🚀 開始使用 (給一般使用者)

1.  前往本專案的 [**Releases**](https://github.com/your-username/your-repository/releases) 頁面。
2.  下載最新版本的 `官帥老師YT影片下載神器.exe` 檔案。
3.  將 `.exe` 檔案放置在您喜歡的任何資料夾中。
4.  直接雙擊執行 `.exe` 檔案即可開始使用！

## 🛠️ 使用教學

1.  **貼上網址**：在頂部的「影片網址」文字框中，貼上一個或多個影片網址（一行一個）。
2.  **選擇儲存位置**：點擊「瀏覽...」按鈕，選擇您希望影片儲存的資料夾。
3.  **設定進階選項 (可選)**：根據您的需求調整下載格式、字幕、Cookie 等選項。
4.  **開始下載**：點擊橘色的「開始批量下載」按鈕，進度將會顯示在下方的日誌框中。

### 🚨 如何解決「登入」或「機器人驗證」錯誤？

當日誌中出現 `Sign in to confirm you’re not a bot` 或類似錯誤時，請使用「驗證方式」下拉選單：

*   **方法 A (推薦，最可靠): 使用 `cookies.txt` 檔案**
    1.  為您的瀏覽器 (Chrome/Firefox) 安裝 `Get cookies.txt LOCALLY` 或類似的擴充功能。
    2.  在瀏覽器中**登入 YouTube**。
    3.  點擊擴充功能圖示，匯出 YouTube 的 Cookie 檔案。
    4.  將匯出的檔案重新命名為 `cookies.txt`。
    5.  將 `cookies.txt` 檔案**放置在與 `.exe` 程式完全相同的資料夾中**。
    6.  在下載器的「驗證方式」中選擇「**使用 cookies.txt 檔案**」，然後重新下載。

*   **方法 B (較方便): 從瀏覽器讀取**
    1.  在「驗證方式」中，選擇您已登入 YouTube 的瀏覽器（例如 Chrome）。
    2.  重新下載。
    3.  **注意**：此方法有時可能會被防毒軟體或系統權限阻止。如果失敗，請使用方法 A。

## 👨‍💻 給開發者 (如何從原始碼執行)

1.  **前置需求**：
    *   安裝 [Python 3](https://www.python.org/) (請在安裝時勾選 `Add Python to PATH`)。
    *   下載並將 `yt-dlp.exe` 和 `ffmpeg.exe` 放置在本專案的根目錄。

2.  **設定環境**：
    ```bash
    # 複製本專案
    git clone https://github.com/your-username/your-repository.git
    cd your-repository

    # 建立並啟用虛擬環境 (建議)
    python -m venv venv
    .\venv\Scripts\activate

    # 安裝必要的 Python 函式庫
    pip install -r requirements.txt
    ```

3.  **建立 `requirements.txt`**：
    在專案根目錄建立一個 `requirements.txt` 檔案，內容如下：
    ```
    Pillow
    ```

4.  **執行程式**：
    ```bash
    python downloader_app.py
    ```

### 📦 如何打包成 `.exe` 檔案

1.  安裝 PyInstaller：
    ```bash
    pip install pyinstaller
    ```
2.  執行打包指令（請確保所有資源檔案都在根目錄）：
    ```bash
    pyinstaller --name "官帥老師YT影片下載神器" --onefile --windowed --add-data "icon.ico;." --add-data "download_icon.png;." --add-data "robot_cat.png;." --add-binary "yt-dlp.exe;." --add-binary "ffmpeg.exe;." downloader_app.py
    ```
3.  打包完成的 `.exe` 檔案將位於 `dist` 資料夾中。

## 🙏 致謝

*   本專案的核心功能由 [yt-dlp](https://github.com/yt-dlp/yt-dlp) 提供。
*   影片/音訊合併功能由 [FFmpeg](https://ffmpeg.org/) 提供。
*   感謝所有為這些開源專案做出貢獻的人。
