import PyInstaller.__main__
import os
from release_version import VersionManager

# Get the absolute path to the project root
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
version_manager = VersionManager("version.txt")
version = version_manager.load_version()

# Get absolute path to main.py
main_script = os.path.join(project_root, 'main.py')

PyInstaller.__main__.run([
    main_script,  # Your main script with absolute path
    f'--name=Borderless-Games-and-Apps',  # Match the name expected in create_release.py
    '--onefile',  # Create a single executable file
    '--windowed',  # Don't show console window
    '--clean',  # Clean cache before building
    '--noconsole',  # No console window
    f'--distpath={os.path.join(project_root, "dist")}',  # Specify dist directory
])
