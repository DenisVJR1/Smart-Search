import customtkinter as ctk
from tkinter import filedialog, messagebox
from smart_search import SmartSearcher
import os
import subprocess
import threading
from pathlib import Path
import keyboard
import pystray
from PIL import Image, ImageDraw
import sys

# Переклади
LANGUAGES = {
    "English": {
        "title": "SEARCH PRO",
        "index_folder": "Index Folder",
        "index_all": "SCAN EVERYTHING (C:\\)",
        "stats": "Database: {} files",
        "ready": "Ready",
        "indexing": "Indexing...",
        "done": "Done",
        "error": "Error",
        "search_placeholder": "Enter file name...",
        "find_btn": "FIND",
        "text_search_btn": "Search inside files (text)",
        "results_label": "Found Files",
        "open": "Open",
        "folder": "Folder",
        "not_found": "Nothing found 😕",
        "searching": "Searching..."
    },
    "Українська": {
        "title": "SEARCH PRO",
        "index_folder": "Просканувати папку",
        "index_all": "СКАНУВАТИ ВСЕ (C:\\)",
        "stats": "База: {} файлів",
        "ready": "Готовий",
        "indexing": "Йде сканування...",
        "done": "Сканування завершено",
        "error": "Помилка",
        "search_placeholder": "Введіть назву файлу...",
        "find_btn": "ЗНАЙТИ",
        "text_search_btn": "Пошук по тексту (всередині файлів)",
        "results_label": "Знайдені файли",
        "open": "Відкрити",
        "folder": "Папка",
        "not_found": "Нічого не знайдено 😕",
        "searching": "Пошук..."
    },
    "Русский": {
        "title": "SEARCH PRO",
        "index_folder": "Просканировать папку",
        "index_all": "СКАНИРОВАТЬ ВСЕ (C:\\)",
        "stats": "База: {} файлов",
        "ready": "Готов",
        "indexing": "Идет сканирование...",
        "done": "Сканирование завершено",
        "error": "Ошибка",
        "search_placeholder": "Введите название файла...",
        "find_btn": "НАЙТИ",
        "text_search_btn": "Поиск по тексту (внутри файлов)",
        "results_label": "Найденные файлы",
        "open": "Открыть",
        "folder": "Папка",
        "not_found": "Ничего не найдено 😕",
        "searching": "Поиск..."
    }
}

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

def create_image():
    image = Image.new('RGB', (64, 64), (30, 30, 30))
    dc = ImageDraw.Draw(image)
    dc.ellipse([10, 10, 54, 54], fill=(0, 120, 215))
    return image

class ResultCard(ctk.CTkFrame):
    def __init__(self, master, data, score=None, lang="English", **kwargs):
        super().__init__(master, **kwargs)
        self.data = data
        self.lang = LANGUAGES[lang]
        
        name_text = data['name']
        if score: name_text = f"[{score}%] {name_text}"
            
        self.label_name = ctk.CTkLabel(self, text=name_text, font=ctk.CTkFont(weight="bold"))
        self.label_name.pack(side="top", anchor="w", padx=10, pady=(5, 0))
        
        self.label_path = ctk.CTkLabel(self, text=data['path'], font=ctk.CTkFont(size=10), text_color="gray")
        self.label_path.pack(side="top", anchor="w", padx=10)
        
        self.btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.btn_frame.pack(side="bottom", fill="x", padx=5, pady=5)
        
        self.open_btn = ctk.CTkButton(self.btn_frame, text=self.lang["open"], width=80, height=24, command=self.open_file)
        self.open_btn.pack(side="left", padx=5)
        
        self.folder_btn = ctk.CTkButton(self.btn_frame, text=self.lang["folder"], width=80, height=24, fg_color="#333333", command=self.open_folder)
        self.folder_btn.pack(side="left", padx=5)

    def open_file(self):
        try: os.startfile(self.data['path'])
        except Exception as e: messagebox.showerror("Error", str(e))

    def open_folder(self):
        try: subprocess.run(['explorer', '/select,', self.data['path']])
        except Exception as e: messagebox.showerror("Error", str(e))

class SmartSearchGUI(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.searcher = SmartSearcher()
        self.indexing_in_progress = False
        self.current_lang = "English"
        
        self.title("Smart Search Pro")
        self.geometry("1100x850")
        self.protocol("WM_DELETE_WINDOW", self.hide_window)

        self.setup_ui()
        self.setup_hotkeys()
        self.setup_tray()

    def setup_ui(self):
        l = LANGUAGES[self.current_lang]
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Бокова панель
        self.sidebar = ctk.CTkFrame(self, width=250, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        
        self.logo_label = ctk.CTkLabel(self.sidebar, text=l["title"], font=ctk.CTkFont(size=24, weight="bold"))
        self.logo_label.pack(pady=30, padx=20)

        self.index_folder_btn = ctk.CTkButton(self.sidebar, text=l["index_folder"], command=self.open_index_dialog)
        self.index_folder_btn.pack(pady=10, padx=20)

        self.index_all_btn = ctk.CTkButton(self.sidebar, text=l["index_all"], fg_color="#d35400", command=self.index_all_drives)
        self.index_all_btn.pack(pady=10, padx=20)

        self.stats_label = ctk.CTkLabel(self.sidebar, text=l["stats"].format(self.searcher.get_count()))
        self.stats_label.pack(pady=20, padx=20)

        # Перемикач мов
        self.lang_menu = ctk.CTkOptionMenu(self.sidebar, values=list(LANGUAGES.keys()), command=self.change_language)
        self.lang_menu.set(self.current_lang)
        self.lang_menu.pack(side="bottom", pady=20)

        self.status_label = ctk.CTkLabel(self.sidebar, text=f"● {l['ready']}", text_color="green")
        self.status_label.pack(side="bottom", pady=10)

        # Головна область
        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.grid(row=0, column=1, padx=30, pady=30, sticky="nsew")
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(2, weight=1)

        self.search_container = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.search_container.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        self.search_container.grid_columnconfigure(0, weight=1)

        self.entry = ctk.CTkEntry(self.search_container, placeholder_text=l["search_placeholder"], height=50, font=ctk.CTkFont(size=16))
        self.entry.grid(row=0, column=0, padx=(0, 10), sticky="ew")
        self.entry.bind("<Return>", lambda e: self.search_name())

        self.main_search_btn = ctk.CTkButton(self.search_container, text=l["find_btn"], width=120, height=50, font=ctk.CTkFont(size=16, weight="bold"), command=self.search_name)
        self.main_search_btn.grid(row=0, column=1)

        self.search_text_btn = ctk.CTkButton(self.main_frame, text=l["text_search_btn"], fg_color="transparent", border_width=1, command=self.start_text_search)
        self.search_text_btn.grid(row=1, column=0, pady=(0, 20))

        self.results_frame = ctk.CTkScrollableFrame(self.main_frame, label_text=l["results_label"])
        self.results_frame.grid(row=2, column=0, sticky="nsew")

    def change_language(self, new_lang):
        self.current_lang = new_lang
        for widget in self.winfo_children(): widget.destroy()
        self.setup_ui()

    def start_text_search(self):
        query = self.entry.get()
        if not query: return
        self.status_label.configure(text=f"● {LANGUAGES[self.current_lang]['searching']}", text_color="yellow")
        threading.Thread(target=self.run_text_search, args=(query,), daemon=True).start()

    def run_text_search(self, query):
        results = self.searcher.search_content(query)
        self.after(0, lambda: self.display_results(results))
        self.after(0, lambda: self.status_label.configure(text=f"● {LANGUAGES[self.current_lang]['ready']}", text_color="green"))

    def index_all_drives(self):
        self.start_indexing("C:\\")

    def open_index_dialog(self):
        folder = filedialog.askdirectory()
        if folder: self.start_indexing(folder)

    def start_indexing(self, folder):
        if self.indexing_in_progress: return
        self.indexing_in_progress = True
        l = LANGUAGES[self.current_lang]
        self.status_label.configure(text=f"● {l['indexing']}", text_color="yellow")
        threading.Thread(target=self.run_indexing, args=(folder,), daemon=True).start()

    def run_indexing(self, folder):
        l = LANGUAGES[self.current_lang]
        try:
            self.searcher.index_directory(folder, progress_callback=lambda c: self.stats_label.configure(text=l["stats"].format(c)))
            self.status_label.configure(text=f"● {l['done']}", text_color="green")
        except:
            self.status_label.configure(text=f"● {l['error']}", text_color="red")
        finally:
            self.indexing_in_progress = False

    def setup_hotkeys(self):
        try: keyboard.add_hotkey('alt+shift+s', self.toggle_window)
        except: pass

    def setup_tray(self):
        try:
            menu = pystray.Menu(pystray.MenuItem("Show", self.show_window), pystray.MenuItem("Exit", self.quit_app))
            self.tray = pystray.Icon("SmartSearch", create_image(), "Smart Search Pro", menu)
            threading.Thread(target=self.tray.run, daemon=True).start()
        except: pass

    def toggle_window(self):
        if self.state() == 'iconic' or not self.winfo_viewable(): self.show_window()
        else: self.hide_window()

    def show_window(self, icon=None, item=None):
        self.deiconify()
        self.lift()
        self.focus_force()
        self.entry.focus()

    def hide_window(self): self.withdraw()

    def quit_app(self, icon=None, item=None):
        if hasattr(self, 'tray'): self.tray.stop()
        self.destroy()
        sys.exit()

    def search_name(self):
        query = self.entry.get()
        if not query: return
        results = self.searcher.search_by_name(query)
        self.display_results(results)

    def display_results(self, results):
        for child in self.results_frame.winfo_children(): child.destroy()
        if not results:
            ctk.CTkLabel(self.results_frame, text=LANGUAGES[self.current_lang]["not_found"]).pack(pady=20)
            return
        for item in results:
            data, score = item if isinstance(item, tuple) else (item, None)
            ResultCard(self.results_frame, data, score, self.current_lang).pack(fill="x", padx=10, pady=5)

if __name__ == "__main__":
    app = SmartSearchGUI()
    app.mainloop()
