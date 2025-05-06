import PyInstaller.__main__
import sys
import os
from pathlib import Path
import shutil

def build_executable():
    try:
        # Setup paths
        project_root = Path(__file__).parent.parent
        print(f"Project root: {project_root}")

        # Ensure dist directory is clean
        dist_dir = project_root / "dist"
        if dist_dir.exists():
            print("Cleaning dist directory...")
            shutil.rmtree(dist_dir)

        # Ensure build directory is clean
        build_dir = project_root / "build"
        if build_dir.exists():
            print("Cleaning build directory...")
            shutil.rmtree(build_dir)

        # Setup resource paths
        icon_path = project_root / "src" / "static" / "img" / "icon_32.ico"
        version_path = project_root / "version.txt"

        print(f"Icon path: {icon_path}")
        print(f"Version path: {version_path}")

        if not icon_path.exists():
            print(f"Warning: Icon file not found at {icon_path}")
        if not version_path.exists():
            print(f"Warning: Version file not found at {version_path}")

        # Common PyInstaller arguments
        common_args = [
            '--windowed',
            '--clean',
            '--noconsole',
            '--hidden-import=requests',
            '--hidden-import=packaging',
            '--hidden-import=win32gui',
            '--hidden-import=win32con',
            '--hidden-import=win32process',
            '--hidden-import=win32api',
            '--hidden-import=psutil',
            '--collect-all=requests',
            f'--distpath={dist_dir}',
            '--noconfirm',
        ]

        # Add icon if exists
        if icon_path.exists():
            common_args.extend(['--icon', str(icon_path)])
            common_args.extend(['--add-data', f'{str(icon_path)};src/static/img'])

        # Add version file if exists
        if version_path.exists():
            common_args.extend(['--add-data', f'{str(version_path)};.'])

        # Build main application
        print("\nBuilding main application...")
        main_args = [
            str(project_root / 'main.py'),
            '--name=Borderless-Games-and-Apps',
            '--onefile',
        ] + common_args

        print("PyInstaller args for main app:", ' '.join(main_args))
        PyInstaller.__main__.run(main_args)

        # Build updater
        print("\nBuilding updater...")
        updater_args = [
            str(project_root / 'src' / 'utils' / 'updater.py'),
            '--name=updater',
            '--onefile',
        ] + common_args

        print("PyInstaller args for updater:", ' '.join(updater_args))
        PyInstaller.__main__.run(updater_args)

        # Verify builds
        main_exe = dist_dir / "Borderless-Games-and-Apps.exe"
        updater_exe = dist_dir / "updater.exe"

        if not main_exe.exists():
            raise FileNotFoundError(f"Main executable not found at {main_exe}")
        if not updater_exe.exists():
            raise FileNotFoundError(f"Updater executable not found at {updater_exe}")

        print("\nBuild completed successfully!")
        return True

    except Exception as e:
        print(f"Error building executable: {e}", file=sys.stderr)
        import traceback
        print(traceback.format_exc())
        return False

if __name__ == "__main__":
    success = build_executable()
    sys.exit(0 if success else 1)
