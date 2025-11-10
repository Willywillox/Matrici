# Setup Access Multi-Utente su Rete Aziendale

## Per Ambiente Intranet Chiuso

Questa guida è per ambienti aziendali con:
- Intranet isolata (nessun accesso internet)
- Microsoft Office già installato
- 10 utenti che lavorano su rete locale
- File server interno disponibile

---

## 🚀 Setup Rapido (15 minuti)

### Fase 1: Preparazione File Server

**Sul server/PC centrale:**

1. **Crea cartella condivisa:**
   ```
   Percorso server: C:\Matrici_Shared
   Nome share: \\NOME-SERVER\Matrici

   oppure se non hai nome server:
   \\192.168.1.100\Matrici
   ```

2. **Configura permessi:**
   ```
   Right-click sulla cartella → Properties → Sharing → Advanced Sharing

   ✓ Share this folder
   Share name: Matrici

   Permissions → Add:
   - Gruppo: Everyone (o gruppo utenti specifico)
   - Permessi: Read + Write + Modify
   ```

3. **Verifica accesso:**
   ```
   Da un altro PC:
   Windows+R → \\NOME-SERVER\Matrici

   Dovresti vedere la cartella vuota
   ```

### Fase 2: Copia File Database

**Sul server:**

1. **Crea database Access:**
   ```
   Opzione A: Usa script Python
   python src/database/db_creator.py

   Opzione B: Esegui create_access_network.bat (vedi sotto)
   ```

2. **Copia database nella share:**
   ```
   copy data\operator_overtime.accdb \\NOME-SERVER\Matrici\
   ```

3. **Verifica permessi file:**
   ```
   Right-click su operator_overtime.accdb → Properties → Security

   Verifica che gli utenti abbiano:
   - Read
   - Write
   - Modify
   ```

### Fase 3: Configurazione Client

**Su OGNI PC utente:**

1. **Crea cartella locale Matrici:**
   ```
   mkdir C:\Matrici
   ```

2. **Copia exe e config:**
   ```
   Copia nella cartella:
   - Matrici.exe
   - database_config.ini (vedi template sotto)
   ```

3. **Configura `database_config.ini`:**
   ```ini
   [database]
   type = access
   # IMPORTANTE: Usa percorso UNC (\\server\share), NON drive mappato (Z:\)
   path = \\NOME-SERVER\Matrici\operator_overtime.accdb

   [multiuser]
   auto_refresh = yes
   refresh_interval = 45  # Secondi (45-60 per Access)
   show_notifications = yes
   user_id = COGNOME.NOME  # es: ROSSI.MARIO

   [access]
   # Ottimizzazioni per Access multi-utente
   use_pessimistic_locking = no
   lock_retry_count = 5
   lock_retry_delay = 1.0
   ```

4. **Test connessione:**
   ```
   Doppio click su Matrici.exe
   Menu Database → Info Database

   Dovrebbe mostrare: "Database: Access" e path di rete
   ```

### Fase 4: Test Multi-Utente

**Test con 2 PC:**

1. **PC 1**: Avvia Matrici, vai a Anagrafica Operatori
2. **PC 2**: Avvia Matrici, vai a Anagrafica Operatori
3. **PC 1**: Inserisci nuovo operatore "Test Utente"
4. **PC 2**: Attendi 45 secondi (auto-refresh) oppure clicca "🔄 Aggiorna"
5. **PC 2**: Dovresti vedere "Test Utente" ✅

---

## 📁 Struttura File Finali

### Sul Server:
```
\\NOME-SERVER\Matrici\
└── operator_overtime.accdb  (300 KB iniziale)
```

### Su Ogni PC Client:
```
C:\Matrici\
├── Matrici.exe
└── database_config.ini
```

---

## ⚙️ Ottimizzazioni Access Multi-Utente

### 1. Impostazioni Database Access

**Apri Access sul server:**

```
1. Apri operator_overtime.accdb con Access
2. File → Options → Current Database
3. Configura:
   ✓ Default open mode: Shared
   ✓ Default record locking: No locks
   ✓ Open databases using record-level locking

4. File → Options → Client Settings
5. Configura:
   Refresh interval: 60 seconds
   Update retry interval: 250 milliseconds
   Number of update retries: 3
```

### 2. Compattazione Automatica

Access su rete tende a gonfiarsi. **Compattalo regolarmente:**

```
Opzione A: Manualmente (1 volta a settimana)
- Chiudi TUTTE le istanze Matrici
- Apri Access
- Database Tools → Compact and Repair Database

Opzione B: Script automatico (vedi sotto)
```

### 3. Backup Giornaliero

**Script batch sul server:**

```batch
@echo off
REM Backup giornaliero database Access
REM Esegui alle 2:00 AM quando nessuno lavora

set SOURCE=\\NOME-SERVER\Matrici\operator_overtime.accdb
set BACKUP_DIR=\\NOME-SERVER\Matrici\Backup
set DATE=%date:~-4%%date:~3,2%%date:~0,2%
set BACKUP_FILE=%BACKUP_DIR%\operator_overtime_%DATE%.accdb

REM Crea cartella backup se non esiste
if not exist "%BACKUP_DIR%" mkdir "%BACKUP_DIR%"

REM Copia database
copy "%SOURCE%" "%BACKUP_FILE%"

REM Mantieni solo ultimi 30 giorni
forfiles /P "%BACKUP_DIR%" /M *.accdb /D -30 /C "cmd /c del @path"

echo Backup completato: %BACKUP_FILE%
```

**Pianifica con Task Scheduler:**
```
1. Apri Task Scheduler su server
2. Create Task → Name: "Matrici Backup"
3. Trigger: Daily at 2:00 AM
4. Action: Start program → backup_matrici.bat
```

---

## 🔧 Risoluzione Problemi Comuni

### Problema: "File in uso" / "Locked"

**Causa:** Troppi utenti o qualcuno ha lasciato Access aperto

**Soluzione:**
```
1. Identifica file .laccdb nella cartella share
   (operator_overtime.laccdb)

2. Questo file mostra chi ha il database aperto

3. Chiedi a tutti di chiudere Matrici

4. Elimina .laccdb manualmente

5. Riavvia Matrici
```

### Problema: Performance Lente

**Causa:** Rete lenta o troppi utenti

**Soluzioni:**
```
1. Aumenta refresh_interval a 60-90 secondi

2. Compatta database (Database Tools → Compact)

3. Verifica velocità rete (dovrebbe essere >100 Mbps)

4. Riduci dimensione database eliminando dati vecchi

5. Considera split database (vedi sotto)
```

### Problema: "Cannot update" / Conflitti

**Causa:** Due utenti modificano stesso record

**Soluzione automatica:**
L'app gestisce automaticamente i conflitti e chiede all'utente cosa fare.

### Problema: Database Corrotto

**Causa:** Interruzione alimentazione, crash durante scrittura

**Soluzione:**
```
1. Chiudi TUTTE le istanze Matrici

2. Apri Access

3. Database Tools → Compact and Repair Database

4. Se non funziona: Ripristina da backup
   copy \\NOME-SERVER\Matrici\Backup\operator_overtime_YYYYMMDD.accdb
        \\NOME-SERVER\Matrici\operator_overtime.accdb
```

---

## 🎯 Best Practices

### ✅ Fare Sempre:

1. **Percorso UNC**: Usa `\\server\share\file.accdb`, NON `Z:\file.accdb`
2. **Backup Automatico**: Configura backup notturno
3. **Compattazione Settimanale**: Ogni venerdì sera
4. **Chiusura Corretta**: Sempre chiudere app, mai kill process
5. **Refresh Adeguato**: 45-60 secondi è ottimale per Access

### ❌ NON Fare Mai:

1. ❌ Aprire .accdb direttamente con Access mentre altri usano Matrici
2. ❌ Copiare database mentre qualcuno lo sta usando
3. ❌ Usare drive mappati (Z:, Y:) invece di percorsi UNC
4. ❌ Lasciare app aperta senza usarla (occupa lock)
5. ❌ Modificare struttura database mentre altri lavorano

---

## 📊 Limiti Access Multi-Utente

**Cosa Aspettarsi:**

| Metrica | Valore |
|---------|--------|
| Max utenti simultanei | 10-15 |
| Utenti consigliati | 5-10 |
| Record max consigliati | 50,000 per tabella |
| Dimensione max file | 2 GB |
| Performance lettura | Buona su LAN veloce |
| Performance scrittura | Media (rischio lock) |

**Quando Migrare a SQL Server:**
- Più di 15 utenti regolari
- Database > 500 MB
- Necessità di accesso remoto/VPN
- Performance non accettabili

---

## 🔄 Split Database (Opzionale - per Performance)

**Per migliorare performance:**

### Concetto:
- **Backend**: Database dati (.accdb) su server
- **Frontend**: Database applicazione su ogni PC locale

### Setup:
```
1. Apri operator_overtime.accdb con Access

2. Database Tools → Access Database

3. Split Database:
   - Backend: \\server\Matrici\operator_overtime_BE.accdb
   - Frontend: C:\Matrici\operator_overtime_FE.accdb

4. Distribuisci frontend (.accdb) su ogni PC

5. Ogni PC ha copia locale del frontend,
   ma tutti puntano allo stesso backend
```

**Vantaggio:** Meno traffico rete, performance migliori

---

## 📋 Checklist Pre-Deploy

Prima di distribuire a tutti i 10 utenti:

- [ ] Share di rete creata con permessi corretti
- [ ] Database Access creato e copiato su share
- [ ] Test connessione da 2-3 PC
- [ ] Test inserimento operatore da PC 1, visibile da PC 2
- [ ] Test modifica concorrente (2 utenti modificano insieme)
- [ ] Backup automatico configurato
- [ ] Script compattazione settimanale impostato
- [ ] Tutti gli utenti hanno Access Database Engine installato
- [ ] Database_config.ini configurato correttamente su ogni PC
- [ ] Documento procedura per utenti (come usare, come chiudere)

---

## 🆘 Supporto Rapido

**Comandi Utili:**

```batch
REM Verifica connessione share
net use \\NOME-SERVER\Matrici

REM Vedi chi ha file aperto
openfiles /query /s NOME-SERVER /fo table

REM Forza chiusura file (SOLO se emergenza)
openfiles /disconnect /s NOME-SERVER /id <ID>

REM Test velocità rete
ping NOME-SERVER
```

---

## 📞 Contatto IT Aziendale

**Info da fornire al reparto IT:**

```
Applicazione: Matrici - Gestione Turni Operatori
Tipo: Desktop application (exe) con database Access condiviso
Requisiti rete:
- File server interno con share accessibile
- Rete LAN veloce (100+ Mbps consigliato)
- Permessi Read/Write/Modify sulla share per utenti
- Porta 445 (SMB) aperta per file sharing

Software necessario:
- Microsoft Access Database Engine (già in Office)
- Windows 10/11

Utenti simultanei: 10
Dimensione database iniziale: ~1 MB
Dimensione prevista dopo 1 anno: ~100-200 MB
```

---

**Setup Access su intranet è semplice e non richiede installazioni esterne!** ✅
