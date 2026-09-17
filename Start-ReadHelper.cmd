@echo off
setlocal
set "READHELPER_EXE=%~dp0dist\ReadHelper\ReadHelper.exe"

if not exist "%READHELPER_EXE%" (
    echo ReadHelper has not been built yet.
    echo Run: powershell -ExecutionPolicy Bypass -File scripts\build.ps1
    pause
    exit /b 1
)

start "" "%READHELPER_EXE%"
