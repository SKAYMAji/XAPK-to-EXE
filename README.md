# XAPK-to-EXE

Simple desktop app that offers two options:

1. Convert XAPK to APK.
2. Convert APK to EXE (Windows installer wrapper built with PyInstaller).

## Requirements

- Python 3.9+
- `pip install pyinstaller` for APK → EXE conversions.

## Usage

```bash
python app.py
```

Follow the GUI prompts to pick the input file and output folder.

## Notes

- The APK → EXE option packages the APK inside a PyInstaller-built executable.
- The generated EXE extracts the APK and optionally installs it via `adb` if available.
