import win32gui
import win32con
import win32api  # Füge diesen Import hinzu
import tkinter as tk
from tkinter import ttk
import json
import os
import win32process
import psutil

class BorderlessWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Borderless Games and Apps")
        self.root.geometry("800x600")  # Größeres Fenster für zusätzliche Elemente

        # Hole eigenen Prozessnamen
        self.own_process = psutil.Process().name().lower()

        # Lade oder erstelle Blacklist
        self.blacklist_file = "blacklist.json"
        self.blacklist = self.load_blacklist()

        # Füge eigenen Prozess zur Blacklist hinzu
        if self.own_process not in (item.lower() for item in self.blacklist):
            self.blacklist.append(self.own_process)
            self.save_blacklist()

        # Erstelle Notebook für Tabs
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Tab für Hauptfenster
        main_frame = ttk.Frame(notebook)
        notebook.add(main_frame, text="Hauptfenster")

        # Tab für Blacklist
        blacklist_frame = ttk.Frame(notebook)
        notebook.add(blacklist_frame, text="Ausgeschlossene Apps")

        # Liste für Fenster (im Haupttab)
        self.listbox = tk.Listbox(main_frame)
        self.listbox.pack(fill=tk.BOTH, expand=True)

        # Füge Logging-Textfeld hinzu
        self.log_text = tk.Text(main_frame, height=5)
        self.log_text.pack(fill=tk.BOTH, padx=5, pady=5)

        # Frame für Hauptbuttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, padx=5, pady=5)

        # Konfiguriere button_frame für gleichmäßige Verteilung
        button_frame.columnconfigure(0, weight=1)
        button_frame.columnconfigure(1, weight=0)
        button_frame.columnconfigure(2, weight=0)
        button_frame.columnconfigure(3, weight=0)
        button_frame.columnconfigure(4, weight=1)

        # Buttons im Haupttab
        refresh_btn = ttk.Button(button_frame, text="Anwendungsliste aktualisieren",
                               command=self.refresh_windows, width=30)
        refresh_btn.grid(row=0, column=1, padx=5)

        borderless_btn = ttk.Button(button_frame, text="Vollbild Fenstermodus anwenden",
                                  command=self.make_borderless, width=30)
        borderless_btn.grid(row=0, column=2, padx=5)

        add_to_blacklist_btn = ttk.Button(button_frame, text="Zur Blacklist hinzufügen",
                                      command=self.add_to_blacklist, width=30)
        add_to_blacklist_btn.grid(row=0, column=3, padx=5)

        # Blacklist-Verwaltung (im Blacklist-Tab)
        self.blacklist_listbox = tk.Listbox(blacklist_frame)
        self.blacklist_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        blacklist_button_frame = ttk.Frame(blacklist_frame)
        blacklist_button_frame.pack(fill=tk.X, padx=5, pady=5)

        # Button zum Entfernen aus der Blacklist
        remove_btn = ttk.Button(blacklist_button_frame, text="Von Blacklist entfernen",
                             command=self.remove_from_blacklist, width=30)
        remove_btn.pack(side=tk.LEFT, padx=5)

        self.windows = {}
        self.refresh_windows()
        self.update_blacklist_display()

    def load_blacklist(self):
        if os.path.exists(self.blacklist_file):
            try:
                with open(self.blacklist_file, 'r') as f:
                    return json.load(f)
            except:
                return []
        return []

    def save_blacklist(self):
        with open(self.blacklist_file, 'w') as f:
            json.dump(self.blacklist, f)

    def update_blacklist_display(self):
        self.blacklist_listbox.delete(0, tk.END)
        for item in self.blacklist:
            self.blacklist_listbox.insert(tk.END, item)

    def add_to_blacklist(self):
        selection = self.listbox.curselection()
        if not selection:
            return

        title = self.listbox.get(selection[0])
        # Extrahiere den Prozessnamen aus der Anzeige
        process_name = title.split('(')[-1].replace(')', '').strip()
        base_name = process_name.lower().replace('.exe', '')

        if base_name not in (item.lower() for item in self.blacklist):
            self.blacklist.append(base_name)
            self.save_blacklist()
            self.update_blacklist_display()
            self.refresh_windows()

    def remove_from_blacklist(self):
        selection = self.blacklist_listbox.curselection()
        if not selection:
            return

        item = self.blacklist_listbox.get(selection[0])
        self.blacklist.remove(item)
        self.save_blacklist()
        self.update_blacklist_display()
        self.refresh_windows()

    def refresh_windows(self):
        self.listbox.delete(0, tk.END)
        self.windows.clear()

        def enum_windows_callback(hwnd, _):
            if win32gui.IsWindowVisible(hwnd):
                title = win32gui.GetWindowText(hwnd)
                if title:
                    try:
                        # Hole Process ID des Fensters
                        _, pid = win32process.GetWindowThreadProcessId(hwnd)
                        # Hole Prozessname
                        process_name = psutil.Process(pid).name()
                        # Entferne .exe vom Namen
                        base_name = process_name.lower().replace('.exe', '')

                        # Prüfe ob der Prozessname in der Blacklist ist
                        if not any(blocked.lower() == base_name for blocked in self.blacklist):
                            self.windows[title] = hwnd
                            display_title = title[:30] + ('...' if len(title) > 30 else '')
                            self.listbox.insert(tk.END, f"{display_title} ({process_name})")
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        pass

        win32gui.EnumWindows(enum_windows_callback, None)

    def make_borderless(self):
        selection = self.listbox.curselection()
        if not selection:
            self.log("Kein Fenster ausgewählt!")
            return

        selected_text = self.listbox.get(selection[0])
        # Suche das richtige Fenster basierend auf dem angezeigten Text
        hwnd = None
        for window_title, window_hwnd in self.windows.items():
            display_title = window_title[:30] + ('...' if len(window_title) > 30 else '')
            if f"{display_title}" in selected_text:
                hwnd = window_hwnd
                break

        if not hwnd:
            self.log(f"Fenster nicht gefunden: {selected_text}")
            return

        self.log(f"Starte Vollbild-Modus für: {selected_text}")

        try:
            # Entferne alle Fenster-Styles
            style = win32gui.GetWindowLong(hwnd, win32con.GWL_STYLE)
            new_style = (style & ~(
                win32con.WS_CAPTION |
                win32con.WS_THICKFRAME |
                win32con.WS_MINIMIZE |
                win32con.WS_MAXIMIZE |
                win32con.WS_SYSMENU |
                win32con.WS_BORDER |
                win32con.WS_DLGFRAME |
                win32con.WS_OVERLAPPED
            )) | win32con.WS_POPUP

            # Hole Monitor-Informationen (geändert von win32gui zu win32api)
            monitor = win32api.MonitorFromWindow(hwnd, win32con.MONITOR_DEFAULTTONEAREST)
            monitor_info = win32api.GetMonitorInfo(monitor)
            monitor_area = monitor_info['Monitor']

            self.log(f"Monitor-Bereich: {monitor_area}")

            # Setze Fenster auf volle Monitorgröße
            win32gui.SetWindowPos(
                hwnd,
                win32con.HWND_TOP,
                monitor_area[0], monitor_area[1],
                monitor_area[2] - monitor_area[0],
                monitor_area[3] - monitor_area[1],
                win32con.SWP_FRAMECHANGED | win32con.SWP_SHOWWINDOW
            )

            self.log("Fensterposition wurde angepasst")
            self.log("Vollbild-Modus wurde erfolgreich angewendet")

        except Exception as e:
            self.log(f"Fehler beim Anwenden des Vollbild-Modus: {str(e)}")
            import traceback
            self.log(traceback.format_exc())

    def log(self, message):
        """Fügt eine Nachricht zum Log-Textfeld hinzu"""
        self.log_text.insert(tk.END, message + '\n')
        self.log_text.see(tk.END)  # Scrollt automatisch nach unten

    def clear_log(self):
        """Löscht den Inhalt des Log-Textfelds"""
        self.log_text.delete(1.0, tk.END)

if __name__ == "__main__":
    app = BorderlessWindow()
    app.root.mainloop()
