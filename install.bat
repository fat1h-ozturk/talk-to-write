@echo off
REM ==============================================================================
REM Talk-to-Write: One-Click Windows Setup & Start Menu Registration Script
REM ==============================================================================

echo ======================================================
echo Talk-to-Write Windows Kurulum Sihirbazi
echo ======================================================

where python >nul 2>nul
if %errorlevel% neq 0 (
    echo [HATA] Python bulunamadi! Lutfen Python 3.9 veya ustunu yukleyin ve PATH'e ekleyin.
    pause
    exit /b 1
)

if not exist ".venv" (
    echo [BILGI] Sanal ortam (.venv) olusturuluyor...
    python -m venv .venv
)

echo [BILGI] Bagimliliklar yukleniyor...
call .venv\Scripts\activate.bat
pip install --upgrade pip
pip install -r requirements.txt
pip install -e . --no-deps

echo [BILGI] Baslat Menusune kisayol ekleniyor...
python -m talk_to_write --install

echo ======================================================
echo Kurulum Tamamlandi!
echo Baslat Menusunden "Talk-to-Write" yazarak uygulamayi acabilirsiniz.
echo ======================================================
pause
