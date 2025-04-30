# Borderless Games and Apps

A simple tool to make any window borderless. Perfect for games and applications that don't support borderless windowed mode natively.

## Features

- Make any window borderless
- Simple and easy to use interface
- Supports most Windows applications and games
- Version controlled releases
- Blacklist functionality for excluding applications

## Installation

1. Download the latest release from the [Releases](../../releases) page
2. Extract the ZIP file
3. Run `Borderless-Games-and-Apps.exe`

## Development

### Prerequisites

- Python 3.13+
- UV package installer (recommended)
- Virtual environment (recommended)

### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/cherzlieb/py-borderless-games-and-apps

# Create virtual environment
python -m venv .venv

# Activate virtual environment (Windows)
.venv\Scripts\activate

# Install UV (if not already installed)
python -m pip install uv

# Install dependencies using UV
uv pip install -r requirements.txt
```

### Creating a Release

To create a new release:

1. Run the release script:
```bash
python scripts/create_release.py
```

2. Choose version increment:
- MAJOR: for incompatible changes
- MINOR: for adding functionality in a backward compatible manner
- PATCH: for backward compatible bug fixes
- Empty: keep current version

The script will:
- Update version number
- Build the executable
- Create a release package
- Generate a ZIP file

## License

[MIT License](LICENSE)

## Requirements

See [`pyproject.toml`](pyproject.toml ) for detailed dependencies.
