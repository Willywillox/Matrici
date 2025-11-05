@echo off
REM Script batch per creare template Excel import operatori
REM Uso: Doppio click su questo file

echo.
echo ============================================================
echo   CREAZIONE TEMPLATE EXCEL IMPORT OPERATORI
echo ============================================================
echo.

REM Vai alla directory root del progetto
cd /d %~dp0\..

echo Creazione template in corso...
echo.

python scripts\create_excel_template.py

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ============================================================
    echo   TEMPLATE CREATO CON SUCCESSO!
    echo ============================================================
    echo.
    echo File creato: templates\template_import_operatori.xlsx
    echo.
    echo PROSSIMI PASSI:
    echo   1. Apri il template con Excel
    echo   2. Compila i dati degli operatori
    echo   3. Salva con un nuovo nome
    echo   4. Importa da GUI: Anagrafica -^> Importa Excel
    echo.
    echo Premi un tasto per aprire il template...
    pause >nul
    start templates\template_import_operatori.xlsx
) else (
    echo.
    echo ============================================================
    echo   ERRORE CREAZIONE TEMPLATE
    echo ============================================================
    echo.
    echo Possibili cause:
    echo   - Python non installato
    echo   - openpyxl non installato (pip install openpyxl)
    echo.
    echo Soluzione:
    echo   Assicurati di aver eseguito: pip install -r requirements.txt
    echo.
    pause
)
