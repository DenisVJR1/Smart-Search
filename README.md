# Smart Search Pro 🚀

**Smart Search Pro** is a high-performance, modern file and content search utility designed specifically for Windows 11. Built with Python and powered by an SQLite backend, it offers near-instant search results across hundreds of thousands of files.

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![OS](https://img.shields.io/badge/OS-Windows%2011-blue.svg)

## ✨ Features

- ⚡ **SQLite Backend**: Blazing fast indexing and searching powered by a relational database.
- ⌨️ **Global Hotkey**: Toggle the search window from anywhere using `Alt + Shift + S`.
- 🌍 **Multi-language Support**: Fully localized in **English (Default)**, **Ukrainian**, and **Russian**.
- 🔍 **Fuzzy Search**: Find files even if you make a typo in the filename.
- 📄 **Content Search**: Search for specific text strings inside files (.py, .txt, .md, etc.) without freezing the UI.
- 📂 **Instant Actions**: Open files or jump to their location in File Explorer with a single click.
-  tray **System Tray Integration**: Runs quietly in the background; minimize to tray and keep working.
- 🎨 **Modern UI**: Sleek Windows 11 dark theme using `CustomTkinter`.

## 📥 Download

If you just want to use the application without installing Python, go to the [Releases](https://github.com/yourusername/SmartSearchPro/releases) page and download the latest `SmartSearchPro.exe`. No installation required!

## 🛠 For Developers

If you want to run from source or modify the code:

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/SmartSearchPro.git
   cd SmartSearchPro
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**:
   ```bash
   python gui_search.py
   ```

## 📦 Building Executable

To package the application into a single standalone `.exe` file:

```powershell
python -m PyInstaller --noconsole --onefile --collect-all customtkinter --name "SmartSearchPro" gui_search.py
```

After the build completes, find your executable in the `dist/` folder.

## 🚀 Usage

1. **Index**: Click on "Index Folder" or "SCAN EVERYTHING (C:\)" to build your initial database.
2. **Search**: Type a filename and hit **Enter** or click **FIND**.
3. **Explore**: Use the "Open" button to launch a file or "Folder" to reveal it in Windows Explorer.
4. **Shortcut**: Use `Alt + Shift + S` to show or hide the application at any time.

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---
*Built with ❤️ and DenisVJR.*
