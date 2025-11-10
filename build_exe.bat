@echo off
REM Script per creare l'eseguibile Windows

echo Creazione eseguibile Matrici...
echo.

REM Verifica installazione PyInstaller
python -m pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo PyInstaller non trovato. Installazione in corso...
    python -m pip install pyinstaller
)

REM Crea l'eseguibile
echo Compilazione in corso...
pyinstaller build_exe.spec

echo.
if exist "dist\Matrici.exe" (
    echo ✓ Eseguibile creato con successo!
    echo Percorso: dist\Matrici.exe
) else (
    echo ✗ Errore nella creazione dell'eseguibile
)

pause
