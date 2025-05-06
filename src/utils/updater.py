import requests
import os
import sys
import subprocess
from pathlib import Path
from packaging import version

class Updater:
    def __init__(self):
        self.GITHUB_REPO = "cherzlieb/py-borderless-games-and-apps"  # Prüfe ob dies dein korrektes Repository ist
        self.APP_NAME = "Borderless-Games-and-Apps.exe"
        self.current_version = self._get_current_version()
        print(f"Initialisiere Updater. Aktuelle Version: {self.current_version}")

    def _get_current_version(self):
        """Get current version from version.txt"""
        try:
            # Erste Methode: Relative zum Script
            version_file = Path(__file__).parent.parent / "version.txt"

            # Zweite Methode: Relative zum Bundle
            if not version_file.exists() and hasattr(sys, '_MEIPASS'):
                version_file = Path(sys._MEIPASS) / "version.txt"

            print(f"Suche Version in: {version_file}")

            if version_file.exists():
                with open(version_file, 'r') as f:
                    version = f.read().strip()
                    print(f"Gefundene Version: {version}")
                    return version
            else:
                print("Version.txt nicht gefunden!")
                return "0.0.0"
        except Exception as e:
            print(f"Fehler beim Lesen der Version: {e}")
            return "0.0.0"

    def check_for_updates(self):
        """Check GitHub for newer version"""
        try:
            print(f"Prüfe Updates für Version {self.current_version}")
            api_url = f"https://api.github.com/repos/{self.GITHUB_REPO}/releases/latest"
            print(f"API URL: {api_url}")

            response = requests.get(api_url)
            print(f"API Response Status: {response.status_code}")

            if response.status_code == 200:
                latest_release = response.json()
                latest_version = latest_release["tag_name"].replace("v", "").strip()
                print(f"Neueste Version auf GitHub: {latest_version}")

                current_ver = version.parse(self.current_version)
                latest_ver = version.parse(latest_version)

                print(f"Vergleiche Versionen: {current_ver} vs {latest_ver}")

                if latest_ver > current_ver:
                    print("Update verfügbar!")
                    return {
                        "available": True,
                        "version": latest_version,
                        "download_url": latest_release["assets"][0]["browser_download_url"],
                        "description": latest_release["body"]
                    }
                print("Keine Updates verfügbar")
            else:
                print(f"GitHub API Fehler: {response.status_code}")
                return {"available": False, "error": f"GitHub API Fehler: {response.status_code}"}

            return {"available": False}

        except Exception as e:
            print(f"Fehler beim Prüfen auf Updates: {e}")
            import traceback
            print(traceback.format_exc())
            return {"available": False, "error": str(e)}

    def download_and_install_update(self, download_url):
        """Download and install the update"""
        try:
            print("Starting update process...")
            response = requests.get(download_url, stream=True)
            temp_file = "update.zip"
            new_exe = f"new_{self.APP_NAME}"

            # Get current directory - using different methods to ensure correct path
            if hasattr(sys, '_MEIPASS'):
                current_dir = os.path.dirname(sys.executable)
            else:
                current_dir = os.path.dirname(os.path.abspath(__file__))
                current_dir = os.path.dirname(current_dir)  # Go up one level

            print(f"Current directory: {current_dir}")
            print(f"Executable path: {sys.executable}")

            # Use absolute paths
            temp_file = os.path.join(current_dir, temp_file)
            new_exe = os.path.join(current_dir, new_exe)
            app_exe = os.path.join(current_dir, self.APP_NAME)

            print(f"Target exe path: {app_exe}")

            # Download the update
            print(f"Downloading update to {temp_file}...")
            with open(temp_file, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            # Create update batch script with improved path handling
            batch_content = f'''@echo off
echo Starting update process...
cd /d "{current_dir}"
timeout /t 2 /nobreak

echo Current directory: %CD%
echo Target exe: {app_exe}

echo Extracting update...
if not exist update_temp mkdir update_temp
tar -xf "{temp_file}" -C update_temp

echo Moving new version...
for /R update_temp %%f in ({self.APP_NAME}) do (
    if exist "%%f" (
        echo Found exe at: %%f
        move "%%f" "{new_exe}"
    )
)

echo Checking files...
if not exist "{new_exe}" (
    echo ERROR: New executable not found!
    pause
    exit /b 1
)

echo Cleaning up temp files...
rmdir /S /Q update_temp
del "{temp_file}"

echo Replacing old version...
taskkill /F /IM "{self.APP_NAME}" >nul 2>&1
timeout /t 2 /nobreak

if exist "{app_exe}" (
    echo Deleting old version...
    del "{app_exe}"
)

echo Moving new version to final location...
move "{new_exe}" "{app_exe}"

echo Verifying installation...
if exist "{app_exe}" (
    echo Starting new version...
    start "" "{app_exe}"
) else (
    echo ERROR: Update failed!
    pause
)

echo Cleanup...
del "%~f0"
'''
            batch_file = os.path.join(current_dir, "update.bat")
            print(f"Creating update script at {batch_file}...")
            with open(batch_file, "w", encoding='utf-8') as f:
                f.write(batch_content)

            print("Executing update script...")
            subprocess.Popen(f'start /B "" cmd /C "{batch_file}"', shell=True)
            sys.exit()

        except Exception as e:
            print(f"Error installing update: {e}")
            import traceback
            print(traceback.format_exc())
            return False

    def show_update_prompt(self, update_info):
        """Show update prompt dialog and return True if user wants to update"""
        try:
            import tkinter as tk
            from tkinter import messagebox

            # Create hidden root window
            root = tk.Tk()
            root.withdraw()

            message = f"""Eine neue Version ist verfügbar!
Aktuelle Version: {self.current_version}
Neue Version: {update_info['version']}

{update_info.get('description', 'Keine Beschreibung verfügbar')}

Möchten Sie das Update jetzt installieren?"""

            return messagebox.askyesno("Update verfügbar", message)
        except Exception as e:
            print(f"Fehler beim Anzeigen des Update-Dialogs: {e}")
            return True  # Im Fehlerfall Update trotzdem durchführen

    def run_standalone_update(self, silent_mode=False):
        """Run updater in standalone mode"""
        try:
            print("Prüfe auf Updates...")
            update_info = self.check_for_updates()

            if update_info.get("available"):
                # Wenn auto-install Parameter gesetzt ist, überspringe die Abfrage
                auto_install = "--auto-install" in sys.argv
                if silent_mode and auto_install:
                    print("Auto-Installation des Updates...")
                    self.download_and_install_update(update_info["download_url"])
                elif not silent_mode:
                    # Zeige Abfrage nur im normalen Modus
                    if self.show_update_prompt(update_info):
                        print("Starte Update-Installation...")
                        self.download_and_install_update(update_info["download_url"])
                    else:
                        print("Update wurde abgebrochen.")
            else:
                if not silent_mode:  # Zeige Meldung nur im nicht-stillen Modus
                    import tkinter as tk
                    from tkinter import messagebox
                    root = tk.Tk()
                    root.withdraw()

                    if "error" in update_info:
                        messagebox.showerror("Fehler",
                            f"Fehler beim Prüfen auf Updates:\n{update_info['error']}")
                    else:
                        messagebox.showinfo("Keine Updates",
                            "Sie verwenden bereits die neueste Version.")

        except Exception as e:
            print(f"Fehler beim Update-Prozess: {e}")
            import traceback
            print(traceback.format_exc())

def main():
    try:
        updater = Updater()
        # Prüfe ob "--silent" als Parameter übergeben wurde
        silent_mode = "--silent" in sys.argv
        updater.run_standalone_update(silent_mode)
    except Exception as e:
        print(f"Fehler: {e}")
        return 1
    return 0

if __name__ == "__main__":
    sys.exit(main())
