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
- `Ctrl+Alt+L`: lock or unlock the current reading line
- `Ctrl+Alt+Left` / `Ctrl+Alt+Right`: change focus-line padding

All shortcuts and visual settings can be changed from the tray menu.
Mouse-follow mode is enabled by default: moving the pointer selects the nearest
OCR-detected text line without blocking clicks in the underlying application.
Use the tray menu's **Control mode** submenu to switch between mouse-follow and
keyboard-only navigation. The two modes are mutually exclusive.
Runtime diagnostics are written to `%LOCALAPPDATA%\ReadHelper\ReadHelper.log`;
screenshots and recognized text are never logged.

## Build

After the OCR model has been downloaded, build the self-contained Windows app:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\build.ps1
```

The bundled model lets the packaged app run OCR without network access.

Run `Start-ReadHelper.cmd` from the project root after building. Files under
`build/` are intermediate PyInstaller output and cannot be launched directly;
the distributable application is under `dist/ReadHelper/`.
