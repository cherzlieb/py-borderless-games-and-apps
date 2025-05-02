import PyInstaller.__main__
from pathlib import Path
from release_version import VersionManager

project_root = Path(__file__).parent.parent
icon_path = project_root / "src" / "img" / "icon_32.ico"

version_manager = VersionManager(project_root / "pyproject.toml")
current_version = version_manager.load_version()

PyInstaller.__main__.run([
    str(project_root / 'main.py'),
    f'--name=Borderless-Games-and-Apps',
    '--onefile',
    '--windowed',
    '--clean',
    '--noconsole',
    '--icon', str(icon_path),
    '--add-data', f'{str(project_root / "version.txt")};.',
    '--add-data', f'{str(icon_path)};src/img',
    f'--distpath={str(project_root / "dist")}',
    '--noconfirm',
])
