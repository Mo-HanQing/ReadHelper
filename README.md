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
