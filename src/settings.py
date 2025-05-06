import json
import os

class Settings:
    @staticmethod
    def _get_version():
        try:
            version_file = os.path.join(os.path.dirname(__file__), "..", "version.txt")
            with open(version_file, 'r') as f:
                return "v" + f.read().strip()
        except Exception:
            return "v0.0.0"  # Fallback version

    # Default values wenn keine settings.json existiert
    DEFAULT_SETTINGS = {
        "window": {
            "width": 800,
            "height": 600,
            "title": f"Borderless Games and Apps {_get_version()}",
            "active_theme": "darkly"
        },
        "display": {
            "max_title_length": 100
        },
        "blacklist": []
    }

    def __init__(self):
        self.settings_file = "settings.json"
        self.settings = self.load_settings()

    def load_settings(self):
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    loaded_settings = json.load(f)
                    # Merge with defaults to ensure all required settings exist
                    return self._merge_settings(self.DEFAULT_SETTINGS, loaded_settings)
            except Exception as e:
                print(f"Error loading settings: {e}")
                return self.DEFAULT_SETTINGS.copy()
        return self.DEFAULT_SETTINGS.copy()

    def _merge_settings(self, default, loaded):
        """Recursively merge loaded settings with defaults"""
        merged = default.copy()
        for key, value in loaded.items():
            if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
                merged[key] = self._merge_settings(merged[key], value)
            else:
                merged[key] = value
        return merged

    def get(self, *keys):
        """Get a setting value using dot notation"""
        value = self.settings
        for key in keys:
            value = value.get(key)
            if value is None:
                # If key not found, return default value
                default = self.DEFAULT_SETTINGS
                for k in keys[:-1]:
                    default = default.get(k, {})
                return default.get(keys[-1])
        return value

    def save_settings(self):
        """Save current settings to file"""
        try:
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=4)
        except Exception as e:
            print(f"Error saving settings: {e}")
