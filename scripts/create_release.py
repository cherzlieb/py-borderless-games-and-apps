import os
import shutil
import subprocess
import sys
from pathlib import Path
from release_version import VersionManager
from clear_release_by_error import main as clear_release_by_error


def create_release():
    """Create a release package."""
    original_version = None
    try:
        # Setup paths
        root_dir = Path(__file__).parent.parent
        release_dir = root_dir / "Release"
        dist_dir = root_dir / "dist"
        version_manager = VersionManager("version.txt")
        current_version = version_manager.load_version()
        original_version = current_version  # Speichere originale Version

        part = input("Was möchtest du hochzählen? (MAJOR, MINOR, PATCH, leer lassen für keine Änderung): ")

        # Neue Version setzen oder behalten
        new_version = version_manager.set_version(part if part else None)
        if new_version != current_version:
            version_manager.save_version(new_version)
            current_version = version_manager.load_version()

        zip_name = f"Borderless-Games-and-Apps-{current_version}"

        print(f"Creating release in: {release_dir}")

        # Clean old release files
        if release_dir.exists():
            if release_dir.is_file():
                release_dir.unlink()  # Delete if it's a file
            else:
                shutil.rmtree(release_dir)  # Delete if it's a directory
        release_dir.mkdir(exist_ok=True)  # Create the release directory

        if dist_dir.exists():
            shutil.rmtree(dist_dir)

        # Build executable using absolute path
        build_script = root_dir / "scripts" / "build_exe.py"
        print(f"Building executable using: {build_script}")
        subprocess.run([sys.executable, str(build_script)], check=True)

        # Copy files to release directory
        if dist_dir.exists() and (dist_dir / "Borderless-Games-and-Apps.exe").exists():
            print("Copying files to release directory...")
            # Copy executable
            shutil.copy2(dist_dir / "Borderless-Games-and-Apps.exe", release_dir)

            # Create ZIP file in Release directory
            zip_path = release_dir / f"{zip_name}.zip"
            print(f"Creating ZIP file: {zip_path}")

            # Create archive of all files in release_dir
            release_files_dir = release_dir / "files"

            # Move all release files to a subdirectory
            if release_files_dir.exists():
                shutil.rmtree(release_files_dir)
            release_files_dir.mkdir()

            # Move all files except the zip to the files directory
            for item in release_dir.iterdir():
                if item != release_files_dir and item != zip_path:
                    shutil.move(str(item), str(release_files_dir))

            # Create ZIP from files directory
            shutil.make_archive(str(release_dir / zip_name),
                                'zip', release_files_dir)

            print("Release package created successfully!")

    except Exception as e:
        clear_release_by_error()
        # Setze Version zurück wenn es einen Fehler gab und die Version geändert wurde
        if original_version and original_version != current_version:
            version_manager.save_version(original_version)
            print(f"Version wurde auf {original_version} zurückgesetzt")
        print(f"Error creating release: {str(e)}")
        raise


if __name__ == "__main__":
    create_release()
