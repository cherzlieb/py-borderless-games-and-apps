import tomli
import tomli_w
from pathlib import Path

class VersionManager:
    def __init__(self, toml_path="pyproject.toml"):
        self.toml_path = toml_path
        self.version_path = Path(toml_path).parent / "version.txt"

    def load_version(self):
        """Load the version from pyproject.toml and version.txt."""
        if Path(self.toml_path).exists():
            with open(self.toml_path, "rb") as f:
                pyproject = tomli.load(f)
                version = pyproject["project"]["version"]
                # Also update version.txt
                self._update_version_txt(version)
                return version
        return "0.0.0"

    def _update_version_txt(self, version):
        """Update the version in version.txt."""
        with open(self.version_path, "w") as f:
            f.write(version)

    def save_version(self, version):
        """Save the version to pyproject.toml and version.txt."""
        # Speichere in pyproject.toml
        with open(self.toml_path, "rb") as f:
            pyproject = tomli.load(f)

        pyproject["project"]["version"] = version

        with open(self.toml_path, "wb") as f:
            tomli_w.dump(pyproject, f)

        # Save to version.txt
        self._update_version_txt(version)

    def increment_version(self, version, part):
        """Increment the version based on the specified part."""
        major, minor, patch = map(int, version.split('.'))

        part_lower = part.lower()
        if part_lower not in ["major", "minor", "patch"]:
            raise ValueError("Ungültige Eingabe. Bitte wähle MAJOR, MINOR oder PATCH.")

        if part_lower == "major":
            major += 1
            minor = 0
            patch = 0
        elif part_lower == "minor":
            minor += 1
            patch = 0
        elif part_lower == "patch":
            patch += 1

        return f"{major}.{minor}.{patch}"

    def set_version(self, part=None):
        """Sets or increments the version based on the input."""
        current_version = self.load_version()
        if part:
            return self.increment_version(current_version, part)
        return current_version
