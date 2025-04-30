# Borderless Games and Apps

A simple tool to make any window borderless. Perfect for games and applications that don't support borderless windowed mode natively.

## Features

- Make any window borderless
- Simple and easy to use interface
- Supports most Windows applications and games
- Version controlled releases

## Installation

1. Download the latest release from the [Releases](../../releases) page
2. Extract the ZIP file
3. Run `Borderless-Games-and-Apps.exe`

## Development

### Prerequisites

- Python 3.x
- Virtual environment (recommended)

### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/cherzlieb/py-borderless-games-and-apps

# Create and activate virtual environment
python -m venv .venv
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Creating a Release

To create a new release:

1. Run the release script:
```bash
python scripts/create_release.py
```

2. Choose version increment:
- MAJOR: for incompatible API changes
- MINOR: for adding functionality in a backward compatible manner
- PATCH: for backward compatible bug fixes
- Empty: keep current version

The script will:
- Update version number
- Build the executable
- Create a release package
- Generate a ZIP file

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request

## License

MIT License
