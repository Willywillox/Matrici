@echo off
REM Script per creare e configurare database Access per rete aziendale
REM Uso: create_access_network.bat

echo ============================================================
echo MATRICI - Setup Database Access per Rete Aziendale
echo ============================================================
echo.

REM Verifica Python installato
python --version >nul 2>&1
if errorlevel 1 (
    echo ERRORE: Python non trovato
    echo Installare Python o eseguire script manualmente
    pause
    exit /b 1
)

echo Step 1: Creazione database Access...
python src\database\db_creator.py
if errorlevel 1 (
    echo ERRORE: Creazione database fallita
    pause
    exit /b 1
)

echo.
echo Step 2: Richiesta informazioni rete...
echo.

set /p SERVER_NAME="Inserisci nome server o IP (es: SERVER01 o 192.168.1.100): "
set /p SHARE_NAME="Inserisci nome share (default: Matrici): "

if "%SHARE_NAME%"=="" set SHARE_NAME=Matrici

set NETWORK_PATH=\\%SERVER_NAME%\%SHARE_NAME%

echo.
echo Percorso rete configurato: %NETWORK_PATH%
echo.

REM Crea file configurazione
echo Step 3: Creazione file configurazione...
(
echo # Configurazione Database Access Multi-Utente
echo # Generato automaticamente per rete aziendale
echo.
echo [database]
echo type = access
echo path = %NETWORK_PATH%\operator_overtime.accdb
echo.
echo [multiuser]
echo auto_refresh = yes
echo refresh_interval = 45
echo show_notifications = yes
echo user_id =
echo.
echo [access]
echo use_pessimistic_locking = no
echo lock_retry_count = 5
echo lock_retry_delay = 1.0
) > database_config.ini

echo File database_config.ini creato con successo!
echo.

echo ============================================================
echo SETUP COMPLETATO!
echo ============================================================
echo.
echo Prossimi passi:
echo.
echo 1. Crea share di rete sul server:
echo    - Percorso: %NETWORK_PATH%
echo    - Permessi: Read + Write + Modify per tutti gli utenti
echo.
echo 2. Copia database sulla share:
echo    copy data\operator_overtime.accdb %NETWORK_PATH%\
echo.
echo 3. Su ogni PC client:
echo    - Copia Matrici.exe
echo    - Copia database_config.ini
echo    - Avvia applicazione
echo.
echo 4. Test multi-utente:
echo    - Avvia da 2 PC diversi
echo    - Inserisci operatore dal PC 1
echo    - Aggiorna dal PC 2 (bottone Refresh)
echo    - Verifica che vedi l'operatore inserito
echo.
echo Per dettagli completi: docs\ACCESS_NETWORK_SETUP.md
echo.

pause
