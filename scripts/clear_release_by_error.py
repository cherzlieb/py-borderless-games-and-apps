import os
import shutil
import glob

def delete_files_with_pattern(pattern):
    files = glob.glob(pattern)  # search for files matching the pattern
    for file in files:
        try:
            os.remove(file)
            print(f"Datei '{file}' wurde gelöscht.")
        except Exception as e:
            print(f"Fehler beim Löschen von '{file}': {e}")

# function to delete a folder
def delete_folder(folder_name):
    if os.path.exists(folder_name) and os.path.isdir(folder_name):
        try:
            shutil.rmtree(folder_name)
            print(f"Ordner '{folder_name}' wurde gelöscht.")
        except Exception as e:
            print(f"Fehler beim Löschen von '{folder_name}': {e}")

def main():
    print("Lösche Verzeichnisse...")

    # this is the list of folders to delete
    folders_to_delete = ["build", "dist", "release"]
    for folder in folders_to_delete:
        delete_folder(folder)

    delete_files_with_pattern("Borderless-Games-and-Apps*.spec")
