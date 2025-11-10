# 🚀 GUIDA COMPLETA - Matrici su SharePoint/Teams
## Passo-Passo Dettagliato dall'Inizio alla Fine

---

## 📦 PARTE 1: PREPARAZIONE PC (Fai una sola volta)

### ✅ PASSO 1.1: Installa Python

**1. Scarica Python:**
- Vai su: https://www.python.org/downloads/
- Click su **"Download Python 3.11.x"** (pulsante giallo grande)
- Salva il file (es. `python-3.11.9-amd64.exe`)

**2. Installa Python:**
- Doppio click sul file scaricato
- ⚠️ **IMPORTANTE**: Seleziona la casella **"Add Python to PATH"** (in basso)
- Click su **"Install Now"**
- Aspetta che finisca (2-3 minuti)
- Click **"Close"**

**3. Verifica installazione:**
- Premi `Win+R`
- Scrivi: `cmd` e premi Invio
- Nel Prompt dei comandi scrivi: `python --version`
- Dovresti vedere: `Python 3.11.x`
- ✅ Se lo vedi, Python è installato!

---

### ✅ PASSO 1.2: Scarica Matrici

**1. Scarica il codice:**
- Vai alla pagina GitHub di Matrici (o dove hai il codice)
- Click su **"Code"** → **"Download ZIP"**
- Salva e estrai in: `C:\Matrici`

**2. Verifica cartella:**
- Apri `C:\Matrici`
- Dovresti vedere cartelle: `src`, `scripts`, `docs`, ecc.
- ✅ Se le vedi, hai il codice!

---

### ✅ PASSO 1.3: Installa Dipendenze Python

**1. Apri Prompt dei comandi:**
- Premi `Win+R`
- Scrivi: `cmd` e premi Invio

**2. Vai alla cartella Matrici:**
```cmd
cd C:\Matrici
```

**3. Installa le dipendenze:**
```cmd
pip install -r requirements.txt
```

**Cosa succede:**
- Scarica e installa tutti i pacchetti necessari
- Durata: 2-5 minuti (dipende da internet)
- Vedrai tante righe che scorrono
- Alla fine vedi: `Successfully installed ...`

**4. Verifica installazione:**
```cmd
python verifica_setup.py
```

**Risultato atteso:**
```
============================================================
  MATRICI - VERIFICA SETUP
============================================================
✅ Python Version
✅ Dipendenze
✅ Configurazione DB (potrebbe essere ❌ se non hai ancora configurato)
✅ Struttura Progetto
✅ PyInstaller
✅ Driver Access
❌ Database (normale, non l'hai ancora creato)
```

- ✅ Se vedi almeno 5/7 check verdi → OK!

---

## 🗄️ PARTE 2: CREAZIONE DATABASE SU SHAREPOINT

### ✅ PASSO 2.1: Crea Cartella in Teams

**1. Apri Microsoft Teams:**
- Avvia Teams sul tuo PC
- Vai al tuo Team (es. "Gestione Operatori" o come si chiama)

**2. Vai sui Files:**
- Click sul tab **"Files"** in alto

**3. Crea cartella per Matrici:**
- Click su **"+ New"** → **"Folder"**
- Nome cartella: `Matrici`
- Premi Invio

**4. Entra nella cartella:**
- Doppio click su `Matrici`
- ✅ Ora sei dentro la cartella vuota

---

### ✅ PASSO 2.2: Ottieni Percorso SharePoint

**1. Apri SharePoint:**
- Dentro Teams, nella cartella `Matrici`
- Click sui **3 puntini** `...` in alto a destra
- Click su **"Open in SharePoint"**
- Si apre il browser con SharePoint

**2. Copia URL dalla barra del browser:**
Esempio URL che vedi:
```
https://acmecorp.sharepoint.com/sites/GestioneOperatori/Shared%20Documents/General/Matrici
```

**3. Converti in percorso UNC:**

**DA (URL browser):**
```
https://acmecorp.sharepoint.com/sites/GestioneOperatori/Shared%20Documents/General/Matrici
```

**A (percorso UNC per database_config.ini):**
```
\\acmecorp.sharepoint.com@SSL\sites\GestioneOperatori\Shared Documents\General\Matrici
```

**Regole conversione:**
- Togli: `https://`
- Cambia primo `/` in `\`
- Aggiungi: `@SSL` dopo `.sharepoint.com`
- Cambia tutti gli altri `/` in `\`
- Cambia `%20` in spazio (es. `Shared%20Documents` → `Shared Documents`)

**4. Scrivi il TUO percorso qui (compilalo tu):**
```
\\________________.sharepoint.com@SSL\sites\_________________\Shared Documents\________\Matrici
```

---

### ✅ PASSO 2.3: Crea Database Access AUTOMATICAMENTE

⚠️ **IMPORTANTE**: Lo script crea il database CON TUTTI I CAMPI AUTOMATICAMENTE! Non devi fare niente manualmente!

**OPZIONE A - Crea in locale, poi carica (PIÙ FACILE):**

**1. Crea database in locale:**
```cmd
cd C:\Matrici
python src/database/db_creator.py --db-type access --path "C:\Matrici\data\matrici.accdb"
```

**Cosa succede:**
- Crea cartella `C:\Matrici\data\` se non esiste
- Crea file `matrici.accdb` VUOTO con tutte le tabelle e campi
- Vedrai:
```
Database creato con successo: C:\Matrici\data\matrici.accdb
Tabelle create:
  ✓ Anagrafica_Operatori (48 campi)
  ✓ Cambio_Skill
  ✓ Forecast
  ✓ Produttivita
```

**2. Carica su SharePoint:**
- Torna su Teams → Files → cartella `Matrici`
- Click su **"Upload"** → **"Files"**
- Seleziona: `C:\Matrici\data\matrici.accdb`
- Click **"Open"**
- Aspetta upload (pochi secondi)
- ✅ Ora `matrici.accdb` è su SharePoint!

**OPZIONE B - Crea direttamente su SharePoint:**

```cmd
cd C:\Matrici
python src/database/db_creator.py --db-type access --path "\\acmecorp.sharepoint.com@SSL\sites\GestioneOperatori\Shared Documents\General\Matrici\matrici.accdb"
```

⚠️ **Sostituisci** `acmecorp...` con il TUO percorso del PASSO 2.2!

**Cosa succede:**
- Ti chiede credenziali Microsoft la prima volta
- Crea database direttamente su SharePoint
- ✅ Pronto!

---

### ✅ PASSO 2.4: Verifica Database Creato

**1. Controlla su Teams:**
- Teams → Files → cartella `Matrici`
- Dovresti vedere: `matrici.accdb` (circa 500 KB)

**2. Apri Access per verificare (opzionale):**
- Doppio click su `matrici.accdb` in Teams
- Si apre con Microsoft Access
- Vai su **"Strumenti database"** → **"Relazioni"** (per vedere tabelle)
- Dovresti vedere 4 tabelle:
  - **Anagrafica_Operatori** ← Qui vanno gli operatori
  - Cambio_Skill
  - Forecast
  - Produttivita

**3. Guarda dentro tabella Anagrafica_Operatori:**
- Doppio click su tabella `Anagrafica_Operatori`
- Vedrai **48 colonne vuote:**
  - ID, Nome, Cognome, ID_SAP
  - Tipo_Contratto, FTE, Ore_Settimana
  - Ora_Inizio_Turno, Ora_Fine_Turno
  - Inizio_Strao_1, Fine_Strao_1, ... (3 straordinari)
  - Inizio_Pausa_1, Fine_Pausa_1, ... (5 pause)
  - Tipo_Giust_1, Inizio_Giust_1, Fine_Giust_1, ... (5 giustificativi)
  - Etichetta_Skill, Data_Riferimento, **Postazione**
- ✅ Tutti i campi sono già pronti! Lo script li ha creati automaticamente!

---

## ⚙️ PARTE 3: CONFIGURAZIONE

### ✅ PASSO 3.1: Configura Connessione Database

**1. Copia file di esempio:**
```cmd
cd C:\Matrici
copy database_config.ini.example database_config.ini
```

**2. Apri con Notepad:**
- Click destro su `database_config.ini`
- **"Apri con"** → **"Blocco note"**

**3. Modifica il file:**

Cerca questa sezione:
```ini
[database]
type = access

[access]
path = \\SERVER-AZIENDALE\Condivisa\Matrici\matrici.accdb
```

**Cambia in (usa il TUO percorso del PASSO 2.2!):**
```ini
[database]
type = access

[access]
path = \\acmecorp.sharepoint.com@SSL\sites\GestioneOperatori\Shared Documents\General\Matrici\matrici.accdb
auto_compact_size_mb = 100
```

⚠️ **IMPORTANTE**: Sostituisci con il TUO percorso SharePoint!

**4. Salva e chiudi:**
- `Ctrl+S` per salvare
- Chiudi Notepad

---

### ✅ PASSO 3.2: Testa Connessione

```cmd
cd C:\Matrici
python verifica_setup.py
```

**Risultato atteso:**
```
============================================================
  MATRICI - VERIFICA SETUP
============================================================
✅ Python Version
✅ Dipendenze
✅ Configurazione DB
✅ Struttura Progetto
✅ PyInstaller
✅ Driver Access
✅ Database              ← QUESTO ORA DEVE ESSERE VERDE!
============================================================
  RISULTATO: 7/7 check superati
============================================================

🎉 TUTTO OK! Sei pronto per costruire l'exe
```

- ✅ Se vedi 7/7 → **PERFETTO!**
- ❌ Se vedi errori → Verifica percorso in `database_config.ini`

---

## 🏗️ PARTE 4: COSTRUIRE L'ESEGUIBILE (EXE)

### ✅ PASSO 4.1: Costruisci EXE

```cmd
cd C:\Matrici
pyinstaller build_exe.spec
```

**Cosa succede:**
- PyInstaller compila tutto
- Crea cartella `dist\Matrici\`
- Durata: 3-5 minuti
- Vedrai tantissime righe che scorrono
- Alla fine: `Building EXE from EXE-00.toc completed successfully.`

**Risultato:**
```
C:\Matrici\dist\Matrici\
├── Matrici.exe          ← Questo è il programma!
├── python311.dll
├── _tkinter.pyd
└── (tante altre dll e file)
```

---

### ✅ PASSO 4.2: Testa l'EXE in Locale

**1. Vai nella cartella:**
```cmd
cd C:\Matrici\dist\Matrici
```

**2. Esegui il programma:**
```cmd
Matrici.exe
```

**Cosa succede:**
- Si apre la finestra di Matrici
- Vedrai 4 tab: Anagrafica, Capability, Riepilogo, Forecast
- Tab Anagrafica: Tabella vuota (normale, non hai ancora operatori)
- ✅ Se si apre → **FUNZIONA!**

**3. Testa inserimento operatore:**
- Click su **"➕ Nuovo Operatore"**
- Compila:
  - Nome: `Test`
  - Cognome: `Prova`
  - ID_SAP: `99999`
  - Data: (lascia oggi)
  - Contratto: `Full Time`
  - FTE: `1`
  - Turno Inizio: `09:00`
  - Turno Fine: `18:00`
  - Skill: `Test`
  - Postazione: `Sede`
- Click **"Salva"**
- ✅ Se vedi l'operatore nella tabella → **DATABASE FUNZIONA!**

**4. Verifica su SharePoint:**
- Torna su Teams → Files → `matrici.accdb`
- Il file è stato modificato (vedi orario modifica aggiornato)
- ✅ Dati salvati su SharePoint!

**5. Chiudi Matrici:**
- Click su X per chiudere

---

## 📤 PARTE 5: DISTRIBUZIONE AI 10 UTENTI

### ✅ PASSO 5.1: Prepara Cartella Distribuzione su SharePoint

**1. Crea cartella Installazione in Teams:**
- Teams → Files → cartella `Matrici`
- Click **"+ New"** → **"Folder"**
- Nome: `Installazione`

**2. Carica file necessari:**
- Vai su `C:\Matrici\dist\Matrici\`
- Seleziona **TUTTI i file e cartelle** (circa 100+ file)
- Trascina su Teams nella cartella `Installazione`
- Aspetta upload (2-3 minuti)

**3. Carica anche database_config.ini:**
- Vai su `C:\Matrici\`
- Trascina `database_config.ini` nella cartella `Installazione`
- ⚠️ **IMPORTANTE**: Questo file contiene il percorso SharePoint già configurato!

**Risultato su SharePoint:**
```
Teams → Files → Matrici
├── matrici.accdb              ← Database condiviso
└── Installazione/             ← Cartella per utenti
    ├── Matrici.exe
    ├── database_config.ini    ← Già configurato!
    ├── python311.dll
    └── (tutti gli altri file)
```

---

### ✅ PASSO 5.2: Crea Istruzioni per Utenti

**1. Crea file di testo:**
- Teams → Files → Matrici → Installazione
- Click **"+ New"** → **"Word document"** (o usa Notepad)
- Nome: `ISTRUZIONI_INSTALLAZIONE.txt`

**2. Scrivi queste istruzioni:**

```
═══════════════════════════════════════════════════════
  MATRICI - Istruzioni Installazione
═══════════════════════════════════════════════════════

INSTALLAZIONE (5 minuti):

1. Apri Microsoft Teams
   → Files → Matrici → Installazione

2. Seleziona TUTTI i file nella cartella Installazione
   (Ctrl+A per selezionare tutto)

3. Click "Download"
   (I file vengono scaricati in una cartella ZIP)

4. Vai nella cartella Download
   Trova: Installazione.zip

5. Click destro → "Estrai tutto"
   Estrai in: C:\Programmi\Matrici
   (Crea cartella se non esiste)

6. Vai in C:\Programmi\Matrici

7. Doppio click su: Matrici.exe

8. PRIMA APERTURA:
   - Ti chiede credenziali Microsoft
   - Inserisci le tue credenziali aziendali
   - Seleziona "Ricorda credenziali"
   - ✅ Il programma si apre!

═══════════════════════════════════════════════════════

USO QUOTIDIANO:

• Inserire nuovo operatore:
  Tab Anagrafica → ➕ Nuovo Operatore

• Modifiche rapide (cambi turno, straordinari, assenze):
  Tab Anagrafica → Seleziona operatore → ⚡ Modifiche Rapide

• Vedere copertura:
  Tab Capability → Seleziona data e intervallo (15/30 min)

• Report:
  Tab Riepilogo → Esporta Excel

• Importare da Excel:
  Tab Anagrafica → 📊 Importa Excel

═══════════════════════════════════════════════════════

AGGIORNAMENTO AUTOMATICO:
Il programma si aggiorna automaticamente ogni 45 secondi.
Vedrai le modifiche degli altri utenti.

PROBLEMI?
Contatta: [Tuo nome/email]

═══════════════════════════════════════════════════════
```

**3. Salva il file**

---

### ✅ PASSO 5.3: Invia Messaggio su Teams

**Invia questo messaggio nel Team:**

```
📢 NUOVO TOOL: MATRICI - Gestione Operatori

Ciao team! 👋

Da oggi usiamo Matrici per gestire turni, straordinari e copertura operatori.

🚀 INSTALLAZIONE:
1. Files → Matrici → Installazione
2. Scarica tutti i file (Download)
3. Estrai in C:\Programmi\Matrici
4. Esegui Matrici.exe
5. Inserisci credenziali Microsoft quando richiesto

📖 ISTRUZIONI:
Leggi il file "ISTRUZIONI_INSTALLAZIONE.txt" nella cartella Installazione

💡 CARATTERISTICHE:
✅ Tutti vediamo gli stessi dati in tempo reale
✅ Aggiornamento automatico ogni 45 secondi
✅ Modifiche rapide giornaliere
✅ Import massivo da Excel
✅ Report e capability dashboard

❓ Domande? Chiedete pure!
```

---

## 🎉 PARTE 6: PRIMO UTILIZZO

### ✅ PASSO 6.1: Inserisci Primi Operatori

**OPZIONE A - Manualmente (per pochi operatori):**

**1. Apri Matrici:**
- Doppio click su `Matrici.exe`

**2. Vai su Anagrafica:**
- Click su tab **"Anagrafica"**

**3. Inserisci operatore:**
- Click **"➕ Nuovo Operatore"**
- Compila tutti i campi:

**Sezione ANAGRAFICA:**
- Nome: `Mario`
- Cognome: `Rossi`
- ID_SAP: `12345`
- Data: `2025-01-15` (o data desiderata)
- Contratto: `Full Time`
- FTE: `1`
- Ore Settimana: `40`

**Sezione TURNO:**
- ID Turno: `T1`
- Ora Inizio: `09:00`
- Ora Fine: `18:00`

**Sezione POSTAZIONE:**
- Postazione: `Sede` (o Smart Working)

**Sezione STRAORDINARI (opzionale):**
- Se ha straordinario:
  - Inizio Strao 1: `18:00`
  - Fine Strao 1: `20:00`

**Sezione PAUSE:**
- Inizio Pausa 1: `12:00`
- Fine Pausa 1: `13:00`

**Sezione SKILL:**
- Etichetta Skill: `Customer Care`

**4. Salva:**
- Click **"Salva"**
- ✅ Operatore appare nella tabella!

**5. Ripeti per altri operatori**

---

**OPZIONE B - Da Excel (per tanti operatori):**

**1. Crea template Excel:**
```cmd
cd C:\Matrici
python scripts/create_excel_template.py
```

- Crea file: `templates/template_import_operatori.xlsx`

**2. Apri template con Excel:**
```cmd
start templates\template_import_operatori.xlsx
```

**3. Compila righe:**
- Riga 2: Primo operatore (esempio già compilato, modificalo)
- Riga 3: Secondo operatore
- Riga 4: Terzo operatore
- ... (quanti ne vuoi)

**Colonne obbligatorie (sfondo rosso):**
- Nome
- Cognome
- ID_SAP
- Data_Riferimento

**4. Salva come:**
- `C:\Dati\operatori_gennaio.xlsx`

**5. Importa in Matrici:**
- Apri Matrici.exe
- Tab **Anagrafica**
- Click **"📊 Importa Excel"**
- Seleziona: `C:\Dati\operatori_gennaio.xlsx`
- Click **"Apri"**
- Conferma import
- Aspetta... (vedi progresso in tempo reale)
- ✅ Tutti gli operatori importati!

---

### ✅ PASSO 6.2: Usa Modifiche Rapide

**Scenario:** Devi cambiare turno a Mario Rossi

**1. Cerca operatore:**
- Campo `🔍 Cerca`: scrivi `Mario`
- Vedi solo "Mario Rossi"

**2. Apri modifiche rapide:**
- Click su riga "Mario Rossi"
- Click **"⚡ Modifiche Rapide"**

**3. Si apre finestra con 4 tab:**

**Tab POSTAZIONE:**
- Seleziona: 🏠 Smart Working (se lavora da casa oggi)

**Tab CAMBIO TURNO:**
- Modifica orari:
  - Nuovo Inizio: `14:00`
  - Nuovo Fine: `22:00`

**Tab STRAORDINARIO:**
- Aggiungi straordinario:
  - Inizio Strao 1: `22:00`
  - Fine Strao 1: `24:00`

**Tab GIUSTIFICATIVO:**
- Aggiungi assenza:
  - Tipo Giust 1: `Permesso`
  - Inizio: `09:00`
  - Fine: `11:00`

**4. Salva:**
- Click **"Salva"**
- ✅ Modifiche salvate su SharePoint!
- Tutti gli altri utenti vedranno le modifiche dopo 45 secondi

---

### ✅ PASSO 6.3: Visualizza Capability

**1. Vai su tab Capability:**
- Click su tab **"Capability"**

**2. Seleziona parametri:**
- Data: `2025-01-15` (o data desiderata)
- Intervallo: `15 minuti` (o 30 minuti)
- Click **"Calcola Capability"**

**3. Vedi tabella:**
```
Fascia     | FTE    | Presenti | In Pausa | In Prod | Strao | Forecast | Delta
-----------|--------|----------|----------|---------|-------|----------|------
09:00-09:15| 10.0   | 10       | 0        | 10.0    | 0     | 8.0      | +2.0
09:15-09:30| 10.0   | 10       | 0        | 10.0    | 0     | 8.0      | +2.0
...
12:00-12:15| 10.0   | 10       | 5        | 5.0     | 0     | 8.0      | -3.0  ← ROSSO
```

**Colori:**
- 🟢 Verde: Copertura OK (>= forecast)
- 🟡 Giallo: Attenzione (80-99% forecast)
- 🔴 Rosso: Critico (< 80% forecast)

**4. Esporta Excel:**
- Click **"📊 Esporta Excel"**
- Salva dove vuoi
- ✅ File Excel pronto per analisi!

---

## 🔧 MANUTENZIONE

### ✅ Compattazione Database (Settimanale)

**Ogni venerdì sera:**

```cmd
cd C:\Matrici
python scripts\optimize_access_multiuser.py
```

**Cosa fa:**
- Compatta database Access
- Velocizza le query
- Libera spazio

**Oppure da Access:**
- Apri `matrici.accdb` con Microsoft Access
- Menu **"Strumenti database"** → **"Compatta e ripristina database"**

---

### ✅ Backup (Automatico con SharePoint)

**SharePoint ha versioning automatico!**

**Per ripristinare versione precedente:**
1. Teams → Files → `matrici.accdb`
2. Click **"..."** → **"Version history"**
3. Vedi tutte le versioni salvate
4. Click **"Restore"** su versione desiderata

---

## ❓ DOMANDE FREQUENTI

### Q: Il database viene creato con tutti i campi automaticamente?
✅ **SÌ!** Lo script `db_creator.py` crea TUTTE le 48 colonne automaticamente. Tu non devi fare NIENTE manualmente in Access.

### Q: Posso aprire il database con Access mentre Matrici è aperto?
⚠️ **NO!** Se apri con Access in modalità esclusiva, Matrici non può accedere. Usa sempre Access in modalità condivisa.

### Q: Come faccio se ho già un database Excel con gli operatori?
✅ Usa la funzione Import Excel: Tab Anagrafica → 📊 Importa Excel

### Q: I 10 utenti vedono i dati in tempo reale?
✅ **SÌ!** Aggiornamento automatico ogni 45 secondi. Oppure click "🔄 Aggiorna Lista".

### Q: Cosa succede se 2 utenti modificano lo stesso operatore?
⚠️ L'ultimo salvataggio sovrascrive. Usare Modifiche Rapide per operazioni veloci.

### Q: Posso usare OneDrive sync per la cartella Matrici?
❌ **NO!** Disattiva sync OneDrive per cartella Matrici. Usa sempre percorso UNC SharePoint.

---

## ✅ CHECKLIST FINALE

Prima di distribuire, verifica:

**Configurazione:**
- [ ] Python 3.11+ installato
- [ ] Dipendenze installate (`pip install -r requirements.txt`)
- [ ] Database creato su SharePoint (`matrici.accdb`)
- [ ] `database_config.ini` configurato con percorso SharePoint
- [ ] Percorso ha `@SSL` dopo `.sharepoint.com`
- [ ] Sync OneDrive DISABILITATO per cartella Matrici

**EXE:**
- [ ] EXE costruito (`pyinstaller build_exe.spec`)
- [ ] Testato in locale (si apre, salva operatore)
- [ ] Verifica salvataggio su SharePoint

**Distribuzione:**
- [ ] Cartella Installazione caricata su SharePoint
- [ ] `database_config.ini` incluso
- [ ] Istruzioni create
- [ ] Messaggio Teams inviato
- [ ] Utenti hanno permessi SharePoint

**Operativo:**
- [ ] Almeno 1 operatore di test inserito
- [ ] Capability funziona
- [ ] Export Excel funziona
- [ ] Modifiche Rapide funziona
- [ ] Import Excel testato

---

## 🎉 FATTO!

Ora hai Matrici completamente funzionante su SharePoint/Teams!

**Cosa hai ottenuto:**
✅ Database Access su SharePoint con 48 campi auto-creati
✅ EXE distribuibile ai 10 utenti
✅ Dati condivisi in tempo reale
✅ Backup automatico con versioning SharePoint
✅ Import massivo da Excel
✅ Dashboard capability e report

**Prossimi passi:**
1. Inserisci operatori (manualmente o da Excel)
2. Testa con 2-3 utenti prima
3. Distribuisci a tutti i 10 utenti
4. Usa quotidianamente!

Hai domande su qualche passaggio specifico? 😊
