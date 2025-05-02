import win32gui
import win32con
import win32api
import tkinter as tk
from tkinter import ttk
import json
import os
import sys
import win32process
import psutil
from src.settings import Settings

class BorderlessWindow:
    def __init__(self):
        self.settings = Settings()
        self.root = tk.Tk()

        # Use settings
        window_width = self.settings.get("window", "width")
        window_height = self.settings.get("window", "height")
        self.root.geometry(f"{window_width}x{window_height}")
        self.root.title(self.settings.get("window", "title"))

        self.max_title_length = self.settings.get("display", "max_title_length")

        # Get own process name and remove .exe
        self.own_process = psutil.Process().name().lower().replace('.exe', '')

        # Use blacklist directly from settings
        self.blacklist = self.settings.get("blacklist")

        # Add own process to blacklist if not already present
        if self.own_process not in (item.lower() for item in self.blacklist):
            self.blacklist.append(self.own_process)
            self.save_blacklist()

        self.root.protocol("WM_DELETE_WINDOW", self.root.quit)

        # Icon path with fallback
        bundle_dir = getattr(sys, '_MEIPASS', os.path.dirname(__file__))
        icon_path = os.path.join(bundle_dir, "src", "static", "img", "icon_32.ico")
        try:
            self.root.iconbitmap(icon_path)
        except Exception as e:
            print(f"Could not load icon: {e}")
            # Try an alternative path
            alt_icon_path = os.path.join(os.path.dirname(__file__), "src", "static", "img", "icon_32.ico")
            try:
                self.root.iconbitmap(alt_icon_path)
            except Exception as e:
                print(f"Could not load alternative icon either: {e}")

        # Create notebook for tabs
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Tab for main window
        main_frame = ttk.Frame(notebook)
        notebook.add(main_frame, text="Hauptfenster")

        # Tab for blacklist
        blacklist_frame = ttk.Frame(notebook)
        notebook.add(blacklist_frame, text="Ausgeschlossene Apps")

        # List for windows (in the main tab)
        self.listbox = tk.Listbox(main_frame)
        self.listbox.pack(fill=tk.BOTH, expand=True)

        # Add logging text field
        self.log_text = tk.Text(main_frame, height=5)
        self.log_text.pack(fill=tk.BOTH, padx=5, pady=5)

        # Frame for main buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, padx=5, pady=5)

        # Configure button_frame for even distribution
        button_frame.columnconfigure(0, weight=1)
        button_frame.columnconfigure(1, weight=0)
        button_frame.columnconfigure(2, weight=0)
        button_frame.columnconfigure(3, weight=0)
        button_frame.columnconfigure(4, weight=1)

        # Buttons in the main tab
        refresh_btn = ttk.Button(button_frame, text="Anwendungsliste aktualisieren",
                               command=self.refresh_windows, width=30)
        refresh_btn.grid(row=0, column=1, padx=5)

        borderless_btn = ttk.Button(button_frame, text="Vollbild Fenstermodus anwenden",
                                  command=self.make_borderless, width=30)
        borderless_btn.grid(row=0, column=2, padx=5)

        add_to_blacklist_btn = ttk.Button(button_frame, text="Zur Blacklist hinzufügen",
                                      command=self.add_to_blacklist, width=30)
        add_to_blacklist_btn.grid(row=0, column=3, padx=5)

        # Blacklist management (in the Blacklist tab)
        self.blacklist_listbox = tk.Listbox(blacklist_frame)
        self.blacklist_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        blacklist_button_frame = ttk.Frame(blacklist_frame)
        blacklist_button_frame.pack(fill=tk.X, padx=5, pady=5)

        # Button to remove from the blacklist
        remove_btn = ttk.Button(blacklist_button_frame, text="Von Blacklist entfernen",
                             command=self.remove_from_blacklist, width=30)
        remove_btn.pack(side=tk.LEFT, padx=5)

        self.windows = {}
        self.refresh_windows()
        self.update_blacklist_display()

    def load_blacklist(self):
        return self.settings.get("blacklist")

    def save_blacklist(self):
        self.settings.settings["blacklist"] = self.blacklist
        self.settings.save_settings()

    def update_blacklist_display(self):
        self.blacklist_listbox.delete(0, tk.END)
        for item in self.blacklist:
            self.blacklist_listbox.insert(tk.END, item)

    def add_to_blacklist(self):
        selection = self.listbox.curselection()
        if not selection:
            return

        title = self.listbox.get(selection[0])
        # Extract the process name from the display (format is now “process_name (Title: display_title)”)
        process_name = title.split(' (Title:')[0]  # Take everything before “ (Title:”
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
                        # Get process ID of the window
                        _, pid = win32process.GetWindowThreadProcessId(hwnd)
                        # Get processname
                        process_name = psutil.Process(pid).name().replace('.exe', '')
                        # Remove .exe from the name
                        base_name = process_name.lower()

                        # Check whether the process name is in the blacklist
                        if not any(blocked.lower() == base_name for blocked in self.blacklist):
                            self.windows[title] = hwnd
                            display_title = title[:self.max_title_length] + ('...' if len(title) > self.max_title_length else '')
                            self.listbox.insert(tk.END, f"{process_name} (Title: {display_title})")
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        pass

        win32gui.EnumWindows(enum_windows_callback, None)

    def make_borderless(self):
        selection = self.listbox.curselection()
        if not selection:
            self.log("Kein Fenster ausgewählt!")
            return

        selected_text = self.listbox.get(selection[0])
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
            # Remove extended window styles
            ex_style = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
            new_ex_style = ex_style & ~(
                win32con.WS_EX_DLGMODALFRAME |
                win32con.WS_EX_COMPOSITED |
                win32con.WS_EX_WINDOWEDGE |
                win32con.WS_EX_CLIENTEDGE |
                win32con.WS_EX_LAYERED |
                win32con.WS_EX_STATICEDGE |
                win32con.WS_EX_TOOLWINDOW |
                win32con.WS_EX_APPWINDOW
            )
            win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, new_ex_style)

            # Remove normal window styles (already available)
            style = win32gui.GetWindowLong(hwnd, win32con.GWL_STYLE)
            new_style = (style & ~(
                win32con.WS_CAPTION |
                win32con.WS_THICKFRAME |
                win32con.WS_MINIMIZE |
                win32con.WS_MAXIMIZE |
                win32con.WS_SYSMENU |
                win32con.WS_BORDER |
                win32con.WS_DLGFRAME
            )) | win32con.WS_POPUP

            # Important: Set the new style
            win32gui.SetWindowLong(hwnd, win32con.GWL_STYLE, new_style)

            # Get monitor information
            monitor = win32api.MonitorFromWindow(hwnd, win32con.MONITOR_DEFAULTTONEAREST)
            monitor_info = win32api.GetMonitorInfo(monitor)
            monitor_area = monitor_info['Monitor']

            # Set the position
            win32gui.SetWindowPos(
                hwnd,
                win32con.HWND_TOP,
                monitor_area[0], monitor_area[1],
                monitor_area[2] - monitor_area[0],
                monitor_area[3] - monitor_area[1],
                win32con.SWP_FRAMECHANGED |
                win32con.SWP_SHOWWINDOW |
                win32con.SWP_NOACTIVATE
            )

            # Force redrawing of the window
            win32gui.ShowWindow(hwnd, win32con.SW_HIDE)
            win32gui.ShowWindow(hwnd, win32con.SW_SHOW)
            win32gui.UpdateWindow(hwnd)

            self.log("Vollbild-Modus wurde erfolgreich angewendet")

        except Exception as e:
            self.log(f"Fehler beim Anwenden des Vollbild-Modus: {str(e)}")
            import traceback
            self.log(traceback.format_exc())

    def log(self, message):
        """Adds a message to the log text field"""
        self.log_text.insert(tk.END, message + '\n')
        self.log_text.see(tk.END)

    def clear_log(self):
        """Deletes the content of the log text field"""
        self.log_text.delete(1.0, tk.END)

if __name__ == "__main__":
    app = BorderlessWindow()
    app.root.mainloop()
