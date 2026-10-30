
@echo off
setlocal
cd /d "%~dp0"

echo ========================================
echo       HIDRA - COMPILACAO WINDOWS
echo ========================================

where py >nul 2>nul
if errorlevel 1 (
    echo Python nao encontrado.
    echo Instale Python 3.11 ou superior para compilar.
    pause
    exit /b 1
)

py -m pip install --upgrade pip
if errorlevel 1 goto erro

py -m pip install -r requirements.txt
if errorlevel 1 goto erro


py -m PyInstaller --noconfirm --clean --onefile --windowed --name Hidra --hidden-import=plyer.platforms.win.notification main.py
if errorlevel 1 goto erro

echo.
echo Compilacao concluida!
echo Executavel: dist\Hidra.exe
pause
exit /b 0

:erro
echo.
echo A compilacao falhou. Verifique as mensagens acima.
pause
exit /b 1