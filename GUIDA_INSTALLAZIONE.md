# 📘 Guida Installazione Matrici - Passo Passo

## 🎯 Prerequisiti

Prima di iniziare, assicurati di avere:
- **Windows 10/11**
- **Microsoft Office** con Access installato (hai già la suite Microsoft)
- **Python 3.8+** (solo per costruire l'exe, poi non serve più)
- **Diritti di amministrazione** per installare software

---

## 📦 FASE 1: Installazione Python e Dipendenze

### Passo 1.1: Scarica Python (da PC con internet)
Se il tuo PC non ha internet, scarica da un altro PC:
1. Vai su https://www.python.org/downloads/
2. Scarica **Python 3.11** (file .exe per Windows)
3. Copia il file su chiavetta USB

### Passo 1.2: Installa Python
1. Esegui il file `python-3.11.x-amd64.exe`
2. ✅ **IMPORTANTE**: Seleziona "Add Python to PATH"
3. Clicca "Install Now"
4. Aspetta che finisca

### Passo 1.3: Verifica installazione
Apri **Prompt dei comandi** (CMD) e digita:
```cmd
python --version
```
Dovresti vedere: `Python 3.11.x`

### Passo 1.4: Installa dipendenze

**OPZIONE A - Con Internet:**
```cmd
cd C:\percorso\dove\hai\scaricato\Matrici
pip install -r requirements.txt
```

**OPZIONE B - Senza Internet (Intranet):**
1. Da PC con internet, scarica i pacchetti:
```cmd
pip download -r requirements.txt -d pacchetti_python
```
2. Copia la cartella `pacchetti_python` su chiavetta USB
3. Sul PC in intranet:
```cmd
pip install --no-index --find-links=pacchetti_python -r requirements.txt
```

---

## 🗄️ FASE 2: Creazione Database Access

### Passo 2.1: Scegli dove mettere il database
Per uso multi-utente (10 persone), serve una **cartella di rete condivisa**.

Hai **3 opzioni**:

#### **OPZIONE 1 - SharePoint/Teams (RACCOMANDATO se usi Microsoft 365)** 🌟
- Percorso: `\\tuaazienda.sharepoint.com@SSL\sites\NomeTeam\Shared Documents\Matrici\`
- Integrato con Microsoft Teams
- Backup automatico con versioning
- **📖 Segui la guida:** `docs/SHAREPOINT_SETUP.md`

#### **OPZIONE 2 - File Server Aziendale**
- Percorso: `\\SERVER-AZIENDALE\Condivisa\Matrici\`
- Server file tradizionale
- Chiedi all'IT di creare la cartella condivisa

#### **OPZIONE 3 - Locale (solo per test)**
- Percorso: `C:\Matrici\data\`
- Solo 1 utente alla volta
- Solo per testing, NON per produzione

### Passo 2.2: Crea il database
Hai due opzioni:

**OPZIONE A - Automatica (raccomandato):**
1. Apri il file `scripts\create_access_network.bat`
2. Quando chiede il percorso, inserisci: `\\SERVER-AZIENDALE\Condivisa\Matrici\matrici.accdb`
3. Lo script crea tutto automaticamente

**OPZIONE B - Manuale:**
```cmd
cd C:\percorso\Matrici
python src/database/db_creator.py --db-type access --path "\\SERVER-AZIENDALE\Condivisa\Matrici\matrici.accdb"
```

### Passo 2.3: Verifica creazione
Controlla che il file `matrici.accdb` esista nella cartella di rete.

---

## 🔧 FASE 3: Configurazione Database

### Passo 3.1: Crea file configurazione
1. Copia il file `database_config.ini.example` → `database_config.ini`
2. Apri `database_config.ini` con Notepad
3. Modifica così:

```ini
[database]
# Tipo database: access (per intranet), sqlite (test locale), sqlserver (internet)
type = access

[access]
# Percorso UNC al database Access condiviso (NON usare lettere di unità come Z:)
path = \\SERVER-AZIENDALE\Condivisa\Matrici\matrici.accdb

# Compatta automaticamente quando supera questa dimensione (MB)
auto_compact_size_mb = 100

[sqlite]
# Configurazione per test locali (ignora se usi Access)
path = data/matrici.db

[sqlserver]
# Ignora questa sezione se usi Access
server =
database =
username =
password =
```

**⚠️ IMPORTANTE**:
- Usa percorso UNC (`\\server\cartella`) NON lettere di unità (`Z:\`)
- Tutti i 10 utenti devono usare lo stesso file `database_config.ini` con lo stesso percorso

---

## 🏗️ FASE 4: Costruire l'Eseguibile (EXE)

### Passo 4.1: Installa PyInstaller
```cmd
pip install pyinstaller
```

### Passo 4.2: Costruisci l'EXE
```cmd
cd C:\percorso\Matrici
pyinstaller build_exe.spec
```

Aspetta 2-5 minuti. Quando finisce trovi:
- `dist\Matrici\Matrici.exe` - Questo è l'eseguibile!
- `dist\Matrici\` - Tutta la cartella da distribuire

### Passo 4.3: Testa l'EXE localmente
```cmd
cd dist\Matrici
Matrici.exe
```

Se si apre la finestra principale, funziona! ✅

---

## 📤 FASE 5: Distribuzione agli Altri Utenti

### Passo 5.1: Prepara pacchetto distribuzione
Crea una cartella con:
```
Matrici_v1.0/
├── Matrici.exe               (da dist\Matrici\)
├── (tutte le altre dll e file)  (da dist\Matrici\)
├── database_config.ini       (configurato con percorso rete)
└── ISTRUZIONI_UTENTE.txt     (crea tu, vedi sotto)
```

### Passo 5.2: Istruzioni per utenti finali
Crea file `ISTRUZIONI_UTENTE.txt`:
```
MATRICI - Gestione Anagrafica Operatori

INSTALLAZIONE:
1. Copia tutta la cartella "Matrici_v1.0" sul tuo PC
   (esempio: C:\Programmi\Matrici)

2. Controlla di avere accesso alla cartella di rete:
   \\SERVER-AZIENDALE\Condivisa\Matrici\
   (Apri Esplora File e prova ad accedere)

3. Fai doppio click su Matrici.exe

PRIMO AVVIO:
- L'applicazione si connette al database condiviso
- Vedrai i dati inseriti da tutti gli altri utenti
- Aggiornamento automatico ogni 45 secondi

UTILIZZO QUOTIDIANO:
- Usa "⚡ Modifiche Rapide" per inserimenti veloci
- Usa "Nuovo Operatore" per anagrafica completa
- Usa tab "Capability" per vedere copertura
- Usa tab "Riepilogo" per report

PROBLEMI?
- Verifica di avere accesso alla cartella di rete
- Chiedi all'IT se il database è accessibile
- Controlla che nessuno abbia il database aperto in esclusiva con Access
```

### Passo 5.3: Distribuisci
- Metti la cartella `Matrici_v1.0` su una cartella condivisa
- Invia mail ai 10 utenti con il percorso
- Oppure copia su chiavetta e distribuisci manualmente

---

## 🚀 FASE 6: Primo Utilizzo

### Passo 6.1: Inserisci dati di test
Per testare, puoi usare:
```cmd
python scripts/populate_test_data.py
```
Questo crea 5 operatori di esempio con turni, straordinari, ecc.

### Passo 6.2: Apri l'applicazione
```cmd
Matrici.exe
```

### Passo 6.3: Esplora le funzioni

**TAB 1 - ANAGRAFICA:**
- Click "Nuovo Operatore" → Compila form → Salva
- Doppio click su operatore → Modifica dati
- Click "⚡ Modifiche Rapide" → Inserimenti veloci giornalieri

**TAB 2 - CAPABILITY:**
- Seleziona data con calendario
- Seleziona intervallo (15 min / 30 min)
- Vedi:
  - 🟢 Verde = copertura ok (>= forecast)
  - 🟡 Giallo = attenzione (80-99% forecast)
  - 🔴 Rosso = critico (< 80% forecast)
- Click "📊 Esporta Excel" per salvare

**TAB 3 - RIEPILOGO:**
- Vista "Per Servizio": ore per capability
- Vista "Per Persona": ore per operatore
- Filtri: Giorno/Settimana/Mese
- Esporta in Excel

---

## 🔧 FASE 7: Manutenzione

### Compattazione Database (Settimanale)
Ogni settimana, uno degli utenti deve:
```cmd
python scripts/optimize_access_multiuser.py
```
Oppure chiudi Access e fai:
- Apri Access
- File → Apri → `matrici.accdb`
- Strumenti Database → Compatta e Ripristina

### Backup (Giornaliero/Settimanale)
```cmd
copy "\\SERVER-AZIENDALE\Condivisa\Matrici\matrici.accdb" "\\SERVER-AZIENDALE\Backup\matrici_AAAAMMGG.accdb"
```

---

## ❓ Problemi Comuni

### "Impossibile connettersi al database"
✅ Verifica percorso UNC in `database_config.ini`
✅ Verifica accesso cartella di rete
✅ Verifica che nessuno abbia database aperto in esclusiva

### "Database bloccato"
✅ Chiudi tutte le istanze di Access
✅ Elimina file `.laccdb` nella stessa cartella del database
✅ Riavvia applicazione

### "Modifiche non si vedono"
✅ Aspetta 45 secondi (aggiornamento automatico)
✅ Oppure chiudi e riapri l'applicazione

### Performance lente
✅ Esegui compattazione database
✅ Verifica velocità rete (Access su rete può essere lento)
✅ Se più di 15 utenti, considera migrazione a SQL Server

---

## 📞 Supporto

Per problemi tecnici:
1. Leggi questa guida
2. Controlla `docs/ACCESS_NETWORK_SETUP.md` (guida dettagliata)
3. Controlla `docs/GUI_GUIDE.md` (guida interfaccia)
4. Chiedi all'IT aziendale per problemi di rete/permessi

---

## 🎉 Sei Pronto!

Ora hai Matrici configurato e pronto per gestire:
- ✅ Anagrafica operatori
- ✅ Turni e straordinari
- ✅ Capability e copertura
- ✅ Report giornalieri/settimanali/mensili
- ✅ 10 utenti contemporanei

Buon lavoro! 🚀
