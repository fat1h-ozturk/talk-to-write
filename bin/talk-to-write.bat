@echo off
rem Launcher script for Talk-to-Write on Windows

setlocal
set "DIR=%~dp0.."

if exist "%DIR%\.venv\Scripts\python.exe" (
    set "PYTHON=%DIR%\.venv\Scripts\python.exe"
) else (
    set "PYTHON=python"
)

"%PYTHON%" -m talk_to_write %*
endlocal
