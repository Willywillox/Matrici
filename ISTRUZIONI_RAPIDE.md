# 🚀 Matrici - Istruzioni Rapide

## Per te (Amministratore/Configuratore)

### Setup Iniziale (fai una sola volta)

**1. Installa Python:**
```cmd
- Scarica Python 3.11 da python.org
- Installa con "Add to PATH" selezionato
```

**2. Installa dipendenze:**
```cmd
cd C:\percorso\Matrici
pip install -r requirements.txt
```

**3. Crea database Access su rete:**
```cmd
- Doppio click su: scripts\create_access_network.bat
- Inserisci percorso tipo: \\SERVER\Condivisa\Matrici\matrici.accdb
```

**4. Configura connessione:**
```cmd
- Copia: database_config.ini.example → database_config.ini
- Apri database_config.ini e modifica:
  type = access
  path = \\SERVER\Condivisa\Matrici\matrici.accdb
```

**5. Crea exe:**
```cmd
pyinstaller build_exe.spec
```

**6. Distribuisci:**
```cmd
- Copia cartella dist\Matrici su rete condivisa
- Comunica agli utenti dove trovarla
- Ogni utente copia sul suo PC ed esegue Matrici.exe
```

---

## Per gli utenti finali

### Installazione (fai una sola volta)

1. Copia cartella "Matrici" sul tuo PC (es: `C:\Programmi\Matrici`)
2. Verifica accesso cartella rete: `\\SERVER\Condivisa\Matrici\`
3. Esegui: `Matrici.exe`

### Uso Quotidiano

**Modifiche veloci (uso principale):**
1. Seleziona operatore dalla lista
2. Click "⚡ Modifiche Rapide"
3. Scegli tab:
   - **Postazione**: Sede/Smart Working/Trasferta
   - **Cambio Turno**: Modifica orari
   - **Straordinario**: Aggiungi straordinari (3 slot)
   - **Giustificativo**: Aggiungi assenze (5 slot)
4. Click "Salva"

**Inserimento nuovo operatore:**
1. Tab "Anagrafica"
2. Click "Nuovo Operatore"
3. Compila campi obbligatori (Nome, Cognome, ID SAP, Data)
4. Salva

**Vedere copertura:**
1. Tab "Capability"
2. Seleziona data
3. Scegli intervallo (15 o 30 minuti)
4. Leggi colori:
   - 🟢 = OK
   - 🟡 = Attenzione
   - 🔴 = Critico

**Report:**
1. Tab "Riepilogo"
2. Scegli vista (Servizio/Persona)
3. Filtra (Giorno/Settimana/Mese)
4. Click "📊 Esporta Excel"

---

## Manutenzione Settimanale

**Compattazione database (fai venerdì sera):**
```cmd
python scripts\optimize_access_multiuser.py
```

**Backup (automatizza con script IT):**
```cmd
copy "\\SERVER\Condivisa\Matrici\matrici.accdb" "\\BACKUP\matrici_%date%.accdb"
```

---

## Problemi Comuni

| Problema | Soluzione |
|----------|-----------|
| "Database non trovato" | Verifica percorso in database_config.ini |
| "Database bloccato" | Elimina file .laccdb, chiudi Access |
| "Modifiche non visibili" | Aspetta 45 sec o riavvia |
| "Lentezza" | Compatta database |

---

## Info Tecniche

- **Database**: Access .accdb su cartella di rete
- **Utenti simultanei**: 10-15 (limite Access)
- **Aggiornamento**: Automatico ogni 45 secondi
- **Backup**: Manuale o con script schedulato
- **Esportazioni**: Excel (.xlsx) via OpenPyXL

---

Per guida completa: leggi `GUIDA_INSTALLAZIONE.md`
