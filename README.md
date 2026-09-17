# ReadHelper

ReadHelper is a Windows focus-line overlay. It dims the current monitor while
leaving the active OCR-detected text line clear.

## Development

Python 3.10 or 3.11 is recommended.

```powershell
python -m venv .venv
.venv\Scripts\python -m pip install -e ".[dev]"
.venv\Scripts\python -m readhelper
```

The first OCR model setup requires network access. Runtime OCR is local and
screenshots are never persisted.

## Shortcuts

- `Ctrl+Alt+Space`: toggle the overlay
- `Alt+Up` / `Alt+Down`: move between detected lines
- `Ctrl+Alt+R`: refresh OCR immediately
- `Ctrl+Alt+Left` / `Ctrl+Alt+Right`: change focus-line padding

All shortcuts and visual settings can be changed from the tray menu.

## Build

After the OCR model has been downloaded, build the self-contained Windows app:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\build.ps1
```

The bundled model lets the packaged app run OCR without network access.
