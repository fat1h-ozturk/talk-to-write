@echo off
chcp 65001 >nul 2>&1
REM ==============================================================================
REM Talk-to-Write: Windows Kaldirici (Uninstaller)
REM Kisayollari, baslangic kayitlarini, sanal ortami ve ayarlari temizler.
REM ==============================================================================

cd /d "%~dp0"

echo ======================================================
echo Talk-to-Write Windows Kaldirma Araci
echo ======================================================
echo.
echo Bu islem Talk-to-Write uygulamasini sisteminizden kaldiracaktir:
echo   - Calisan Talk-to-Write surecleri kapatilacak
echo   - Baslat Menusu ve Baslangic kisayollari silinecek
echo   - Kullanici ayar ve veri dosyalari silinecek
echo   - Sanal ortam (.venv) silinecek
echo.
set /p CONFIRM="Devam etmek istiyor musunuz? (E/H): "
if /i not "%CONFIRM%"=="E" if /i not "%CONFIRM%"=="Y" (
    echo [BILGI] Kaldirma islemi iptal edildi.
    pause
    exit /b 0
)

echo.
echo [1/4] Calisan Talk-to-Write islemleri kapatiliyor...
taskkill /f /im python.exe /fi "WINDOWTITLE eq Talk-to-Write*" >nul 2>&1
taskkill /f /im pythonw.exe /fi "WINDOWTITLE eq Talk-to-Write*" >nul 2>&1

echo [2/4] Sistem entegrasyonu ve ayarlar temizleniyor...
if exist ".venv\Scripts\python.exe" (
    call .venv\Scripts\python.exe -m talk_to_write --purge >nul 2>&1
)

REM Kisayollari ve ayarlari manuel olarak da garantiye al
if defined APPDATA (
    if exist "%APPDATA%\Microsoft\Windows\Start Menu\Programs\Talk-to-Write.lnk" (
        del /f /q "%APPDATA%\Microsoft\Windows\Start Menu\Programs\Talk-to-Write.lnk" >nul 2>&1
    )
    if exist "%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\Talk-to-Write.lnk" (
        del /f /q "%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\Talk-to-Write.lnk" >nul 2>&1
    )
    if exist "%APPDATA%\talk-to-write" (
        rmdir /s /q "%APPDATA%\talk-to-write" >nul 2>&1
    )
)

echo [3/4] Sanal ortam ve derleme artıklari siliniyor...
if exist ".venv" rmdir /s /q ".venv" >nul 2>&1
if exist ".pytest_cache" rmdir /s /q ".pytest_cache" >nul 2>&1
if exist "talk_to_write.egg-info" rmdir /s /q "talk_to_write.egg-info" >nul 2>&1
if exist "build" rmdir /s /q "build" >nul 2>&1
if exist "dist" rmdir /s /q "dist" >nul 2>&1

echo [4/4] Sistem temizligi tamamlandi!
echo.
set /p DEL_FOLDER="Proje klasorunun kendisini de (%~dp0) tamamen silmek istiyor musunuz? (E/H): "
if /i "%DEL_FOLDER%"=="E" (
    echo.
    echo Proje klasoru siliniyor...
    start /b "" cmd /c "timeout /t 2 /nobreak >nul & rmdir /s /q \"%~dp0\""
    exit
) else (
    echo ======================================================
    echo Talk-to-Write sistemden basariyla kaldirildi.
    echo Proje kaynak kodlari korundu.
    echo ======================================================
    pause
)
