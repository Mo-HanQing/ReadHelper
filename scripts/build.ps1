$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $PSScriptRoot
$Python = Join-Path $ProjectRoot ".venv\Scripts\python.exe"
$Model = Join-Path $ProjectRoot ".readhelper\paddlex\official_models\PP-OCRv6_tiny_det"
$Icon = Join-Path $ProjectRoot "assets\readhelper.ico"
$env:PADDLE_PDX_CACHE_HOME = Join-Path $ProjectRoot ".readhelper\paddlex"
$env:PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK = "True"

if (-not (Test-Path -LiteralPath $Python)) {
    throw "Project virtual environment not found: $Python"
}
if (-not (Test-Path -LiteralPath $Model)) {
    throw "OCR model not found. Run ReadHelper once to download PP-OCRv6_tiny_det."
}

& $Python -m PyInstaller `
    --noconfirm `
    --clean `
    --windowed `
    --name ReadHelper `
    --icon $Icon `
    --collect-all paddle `
    --collect-all paddlex `
    --collect-all paddleocr `
    --collect-all cv2 `
    --copy-metadata pypdfium2 `
    --copy-metadata pyclipper `
    --add-data "$Model;models\PP-OCRv6_tiny_det" `
    --add-data "$Icon;assets" `
    (Join-Path $ProjectRoot "src\readhelper\__main__.py")
