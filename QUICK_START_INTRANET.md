# 🚀 Guida Rapida - Setup Intranet Aziendale

## Per Ambienti Senza Accesso Internet

Questa guida è per configurare Matrici in **10 minuti** su una rete aziendale chiusa.

---

## ✅ Prerequisiti

- ✅ File server interno accessibile
- ✅ Microsoft Office installato (con Access)
- ✅ 10 PC sulla stessa rete LAN
- ✅ **NO internet necessario**

---

## 📋 Setup in 5 Step

### Step 1: Prepara File Server (2 min)

**Sul server/PC centrale:**

```
1. Crea cartella: C:\Matrici_Shared

2. Click destro → Properties → Sharing → Advanced Sharing
   ✓ Share this folder
   Share name: Matrici
   Permissions: Everyone → Full Control

3. Testa da altro PC:
   Windows+R → \\NOME-SERVER\Matrici
   (Dovresti vedere cartella vuota)
```

### Step 2: Crea Database (2 min)

**Sul server:**

```
1. Doppio click su: create_access_network.bat

2. Segui wizard:
   - Inserisci nome server (es: SERVER01)
   - Inserisci nome share (default: Matrici)

3. Il script crea:
   ✓ Database Access
   ✓ File configurazione
```

### Step 3: Copia Database su Share (1 min)

**Sul server:**

```cmd
copy data\operator_overtime.accdb \\NOME-SERVER\Matrici\
```

Oppure trascina il file nella cartella condivisa.

### Step 4: Configura PC Client (5 min x 10 PC)

**Su OGNI PC utente:**

```
1. Crea cartella: C:\Matrici

2. Copia nella cartella:
   ✓ Matrici.exe
   ✓ database_config.ini

3. Modifica database_config.ini:
   [database]
   path = \\NOME-SERVER\Matrici\operator_overtime.accdb

   [multiuser]
   user_id = TUO.COGNOME  ← Cambia qui!

4. Salva e chiudi
```

### Step 5: Test! (1 min)

**Test multi-utente:**

```
PC 1:
- Doppio click Matrici.exe
- Tab "Anagrafica Operatori"
- Click "➕ Nuovo Operatore"
- Inserisci: Nome=Test, Cognome=Utente, ID_SAP=TEST001
- Click Salva

PC 2:
- Doppio click Matrici.exe
- Tab "Anagrafica Operatori"
- Click "🔄 Aggiorna"
- Dovresti vedere "Test Utente" ✅
```

**Se vedi l'operatore: FUNZIONA! 🎉**

---

## 🎯 Deployment Rapido per Tutti i 10 PC

### Metodo Veloce: USB o Rete

```
1. Sul PC 1, prepara:
   C:\Matrici_Deploy\
   ├── Matrici.exe
   ├── database_config.ini (già configurato)
   └── ISTRUZIONI.txt

2. ISTRUZIONI.txt:
   "
   1. Copia cartella Matrici_Deploy su C:\
   2. Rinomina in C:\Matrici
   3. Apri database_config.ini
   4. Cambia user_id = TUO.COGNOME
   5. Salva e chiudi
   6. Doppio click su Matrici.exe
   "

3. Copia cartella su:
   - USB stick → Distribuisci a ogni PC
   - Oppure: \\server\software\Matrici → Ogni utente copia
```

---

## 📞 Supporto IT

**Cosa dire al reparto IT:**

```
Richiesta: Share di rete per applicazione gestione turni

Dettagli:
- Nome applicazione: Matrici
- Tipo: Desktop app con database Access condiviso
- File server: Share accessibile a 10 utenti
- Permessi: Read/Write/Modify
- Dimensione iniziale: 1 MB
- Dimensione stimata: 100 MB dopo 1 anno
- Porta: 445 (SMB file sharing - standard Windows)

Software richiesto:
- Nessuno (Office già installato)

Installazioni da internet:
- Nessuna (tutto su intranet)
```

---

## ⚠️ Cosa NON Fare

- ❌ NON aprire .accdb con Access mentre altri usano Matrici
- ❌ NON usare drive mappati (Z:) → Usa percorso UNC (\\server\share)
- ❌ NON copiare database mentre qualcuno lavora
- ❌ NON lasciare app aperta inutilmente

---

## ✅ Cosa Fare

- ✅ Usa sempre "🔄 Aggiorna" per vedere modifiche altrui
- ✅ Chiudi sempre app correttamente (X in alto a destra)
- ✅ Compatta database ogni venerdì (vedi sotto)
- ✅ Backup settimanale del .accdb

---

## 🔧 Manutenzione Settimanale (5 min)

**Ogni venerdì sera:**

```
1. Chiedi a TUTTI di chiudere Matrici

2. Sul server, esegui:
   compact_access.bat

3. Backup:
   copy \\server\Matrici\operator_overtime.accdb
        \\server\Matrici\Backup\operator_overtime_YYYYMMDD.accdb
```

---

## 🆘 Troubleshooting Rapido

### "Impossibile aprire database"

**Soluzione:**
```
1. Verifica percorso: \\NOME-SERVER\Matrici accessibile?
2. Prova aprire cartella da Esplora File
3. Verifica permessi: Read+Write sulla share?
```

### "File in uso" / "Locked"

**Soluzione:**
```
1. Chiedi a tutti di chiudere Matrici
2. Attendi 2 minuti
3. Riprova
4. Se persiste: Riavvia server
```

### "Non vedo dati inseriti da altri"

**Soluzione:**
```
1. Click "🔄 Aggiorna"
2. Attendi 45 secondi (auto-refresh)
3. Verifica che tutti puntano allo stesso file:
   \\NOME-SERVER\Matrici\operator_overtime.accdb
```

### Performance Lente

**Soluzione:**
```
1. Compatta database (vedi manutenzione)
2. Aumenta refresh_interval a 60 secondi
3. Verifica velocità rete (ping server)
```

---

## 📊 Verifica Sistema

**Comando rapido per verificare tutto OK:**

```cmd
REM Su ogni PC client, esegui:
ping NOME-SERVER
net use \\NOME-SERVER\Matrici
dir \\NOME-SERVER\Matrici\operator_overtime.accdb
```

Tutti i comandi devono avere successo.

---

## 📚 Documentazione Completa

- **Setup Dettagliato**: `docs\ACCESS_NETWORK_SETUP.md`
- **Guida Interfaccia**: `docs\GUI_GUIDE.md`
- **Esempi Uso**: `docs\QUICK_START.md`

---

## 🎉 Fatto!

Ora tutti i 10 utenti possono:
- ✅ Vedere stessi dati
- ✅ Inserire/modificare operatori
- ✅ Vedere modifiche altrui (auto-refresh 45 sec)
- ✅ Lavorare contemporaneamente

**Nessuna installazione internet necessaria!** 🚀

---

**Domande?** Vedi `docs\ACCESS_NETWORK_SETUP.md` per dettagli completi.
