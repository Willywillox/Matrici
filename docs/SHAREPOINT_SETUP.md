# 📁 Configurazione Database Access su SharePoint/OneDrive

## Per Chi Usa Microsoft Teams e SharePoint

Se la tua azienda usa **Microsoft Teams** e **SharePoint/OneDrive**, questa è la guida per te!

---

## 🎯 Scenario Tipico

```
Azienda con Microsoft 365
↓
Team: "Gestione Operatori" (o simile)
↓
Canale con Files
↓
Cartella condivisa per Matrici
↓
matrici.accdb
```

---

## 📋 SETUP PASSO-PASSO

### **STEP 1: Crea Cartella in Teams**

1. Apri **Microsoft Teams**
2. Vai al tuo Team (es. "Gestione Operatori")
3. Vai su tab **Files**
4. Crea cartella: `Matrici` (o nome a tua scelta)
5. Entra nella cartella

---

### **STEP 2: Ottieni Percorso SharePoint**

Ci sono **2 modi** per ottenere il percorso corretto:

#### **OPZIONE A - Da Teams (Raccomandato)**

1. In Teams, vai su **Files** → cartella `Matrici`
2. Click destro sulla cartella → **Open in SharePoint**
3. Si apre SharePoint nel browser
4. Nella barra indirizzo vedi URL tipo:
   ```
   https://tuaazienda.sharepoint.com/sites/GestioneOperatori/Shared%20Documents/Matrici
   ```
5. **Converti in percorso UNC:**
   ```
   \\tuaazienda.sharepoint.com@SSL\sites\GestioneOperatori\Shared Documents\Matrici
   ```

#### **OPZIONE B - Da Esplora File (Se sincronizzato)**

1. Apri **Esplora File**
2. Cerca cartella sincronizzata OneDrive/SharePoint
3. Esempio percorso locale:
   ```
   C:\Users\TuoNome\OneDrive - Azienda\Matrici
   ```
4. ⚠️ **NON usare questo percorso locale!**
5. Click destro sulla cartella → **View online**
6. Segui OPZIONE A sopra per ottenere percorso UNC

---

### **STEP 3: Formato Percorso Corretto**

SharePoint ha percorsi diversi dai file server tradizionali:

#### ❌ **NON Funzionano:**
```
C:\Users\Nome\OneDrive - Azienda\Matrici\matrici.accdb
Z:\Matrici\matrici.accdb
```

#### ✅ **Formato CORRETTO SharePoint:**
```
\\tuaazienda.sharepoint.com@SSL\sites\NomeTeam\Shared Documents\Matrici\matrici.accdb
```

#### 📝 **Template Generico:**
```
\\[tenant].sharepoint.com@SSL\sites\[site-name]\Shared Documents\[percorso-cartella]\matrici.accdb
```

Dove:
- `[tenant]` = Nome azienda (es. `contoso`, `acme`)
- `[site-name]` = Nome Team/Site (es. `GestioneOperatori`)
- `[percorso-cartella]` = Percorso cartella (es. `Matrici` o `General\Matrici`)

---

### **STEP 4: Crea Database su SharePoint**

#### **OPZIONE A - Crea Localmente, poi Carica**

```cmd
# 1. Crea database in locale
python src/database/db_creator.py --db-type access --path data/matrici.accdb

# 2. Carica su SharePoint
# Apri Teams → Files → Matrici → Upload → Seleziona data/matrici.accdb
```

#### **OPZIONE B - Crea Direttamente su SharePoint (se hai accesso)**

```cmd
python src/database/db_creator.py --db-type access --path "\\tuaazienda.sharepoint.com@SSL\sites\GestioneOperatori\Shared Documents\Matrici\matrici.accdb"
```

⚠️ **Nota:** Potrebbe richiedere autenticazione Microsoft la prima volta.

---

### **STEP 5: Configura database_config.ini**

Apri `database_config.ini` e modifica:

```ini
[database]
type = access

[access]
# Percorso SharePoint (formato UNC con @SSL)
path = \\tuaazienda.sharepoint.com@SSL\sites\GestioneOperatori\Shared Documents\Matrici\matrici.accdb

# Compattazione automatica
auto_compact_size_mb = 100
```

⚠️ **IMPORTANTE:**
- Usa **barre inverse** `\` (non slash `/`)
- Includi `@SSL` dopo `.sharepoint.com`
- Usa `Shared Documents` (NON tradurre in italiano)

---

### **STEP 6: Testa Connessione**

```cmd
# Verifica che il percorso sia accessibile
python verifica_setup.py
```

Se vedi:
```
✓ Connessione database: SUCCESSO
✓ File database Access: Trovato
```

→ Tutto OK! ✅

---

## 🔒 Permessi e Accesso

### **Chi Può Accedere?**

Tutti i membri del Team Teams possono accedere al database, **MA:**

1. **Permessi Teams:**
   - Devono essere membri del Team
   - Devono avere accesso al canale con i Files

2. **Permessi File:**
   - Click destro su `matrici.accdb` in Teams
   - **Manage Access** → Verifica utenti

3. **Autenticazione:**
   - Prima volta: Matrici chiede credenziali Microsoft
   - Poi ricorda (credenziali salvate in Windows)

---

## ⚠️ ATTENZIONI IMPORTANTI

### 🚫 **NON Usare Sincronizzazione OneDrive**

**PROBLEMA:**
```
Se cartella SharePoint è sincronizzata localmente via OneDrive:
→ Percorso locale: C:\Users\...\OneDrive\Matrici\matrici.accdb
→ Database Access si corrompe con sync simultanea
```

**SOLUZIONE:**
```
✓ Usa SEMPRE percorso UNC SharePoint (\\...@SSL\...)
✓ NON sincronizzare cartella Matrici con OneDrive Desktop
✓ Accedi solo via percorso SharePoint
```

**Come Disattivare Sync:**
1. Click destro icona OneDrive (system tray)
2. Settings → Account → Choose folders
3. Deseleziona cartella `Matrici`

---

### 🐌 **Performance: SharePoint vs File Server**

| Aspetto | File Server | SharePoint |
|---------|-------------|------------|
| Velocità | Veloce | Medio-Lento |
| Utenti Simultanei | 10-15 | 5-10 raccomandati |
| Latenza | Bassa | Variabile (dipende da internet) |
| Affidabilità | Alta | Buona |

**Raccomandazioni:**
- ✅ OK per 5-10 utenti con uso normale
- ⚠️ Se più di 10 utenti o uso intensivo → Considera SQL Server
- ✅ Compatta database settimanalmente
- ✅ Backup automatico (SharePoint ha versioning integrato)

---

## 🔧 Configurazione Avanzata SharePoint

### **Abilitare Versioning (Raccomandato)**

SharePoint può salvare versioni precedenti del database:

1. SharePoint → Files → `matrici.accdb`
2. Click `...` → **Version history**
3. Settings → **Library settings** → **Versioning settings**
4. Abilita: "Create major versions"
5. Mantieni: 10-20 versioni

**Vantaggio:** Se database si corrompe, puoi ripristinare versione precedente.

---

### **Backup Automatico con Power Automate**

Crea flow Power Automate per backup automatico:

```
Trigger: Recurrence (ogni domenica, 23:00)
↓
Action: Copy file
From: \\...sharepoint...\Matrici\matrici.accdb
To: \\...sharepoint...\Backup\matrici_backup.accdb
↓
Action: Rename con timestamp
New name: matrici_backup_YYYYMMDD.accdb
```

---

## 🐛 Risoluzione Problemi

### **"Impossibile aprire database"**

**Causa:** Percorso errato o autenticazione mancante

**Soluzione:**
1. Verifica percorso UNC con `@SSL`
2. Apri `matrici.accdb` manualmente da Esplora File (inserisci credenziali)
3. Riprova con Matrici

---

### **"Database bloccato"**

**Causa:** Utente ha database aperto in esclusiva

**Soluzione:**
1. SharePoint → Files → `matrici.accdb`
2. Check **Open** → Vedi chi ha file aperto
3. Chiedi di chiudere
4. Elimina file `.laccdb` se presente

---

### **"Operazioni lente"**

**Causa:** Latenza rete SharePoint

**Soluzione:**
1. Verifica connessione internet stabile
2. Compatta database: `python scripts/optimize_access_multiuser.py`
3. Se persiste, considera migrazione a SQL Server

---

### **"Sync conflict" (se OneDrive sync attivo)**

**Causa:** OneDrive cerca di sincronizzare database mentre è in uso

**Soluzione:**
1. **DISATTIVA SYNC** per cartella Matrici
2. Elimina copie conflitto
3. Usa solo percorso UNC SharePoint

---

## 📱 Accesso da Matrici

### **Distribuzione agli Utenti**

Ogni utente deve:

1. **Essere membro del Team Teams**
2. **Avere Matrici.exe sul proprio PC**
3. **Avere stesso database_config.ini** con percorso SharePoint
4. **Autenticarsi** la prima volta (credenziali Microsoft)

**Distribuzione:**
```
\\tuaazienda.sharepoint.com@SSL\sites\GestioneOperatori\Shared Documents\Matrici\Installazione\
├── Matrici.exe
├── database_config.ini  (con percorso SharePoint configurato)
└── (tutte le dll e file necessari)
```

Invia messaggio Teams:
```
Ciao a tutti,

Matrici è disponibile su SharePoint:
\\tuaazienda.sharepoint.com@SSL\sites\GestioneOperatori\Shared Documents\Matrici\Installazione

Installazione:
1. Copia cartella Matrici sul tuo PC (es. C:\Programmi\Matrici)
2. Esegui Matrici.exe
3. Inserisci credenziali Microsoft quando richiesto

Buon lavoro!
```

---

## ✅ Checklist Configurazione SharePoint

- [ ] Team Teams creato
- [ ] Cartella Files creata (es. `Matrici`)
- [ ] Percorso UNC SharePoint ottenuto
- [ ] Database creato e caricato su SharePoint
- [ ] `database_config.ini` configurato con percorso UNC
- [ ] Sync OneDrive disabilitato per cartella Matrici
- [ ] Permessi verificati (tutti i 10 utenti hanno accesso)
- [ ] Test connessione eseguito (`verifica_setup.py`)
- [ ] Versioning SharePoint abilitato
- [ ] Istruzioni inviate agli utenti

---

## 🎯 Esempio Configurazione Completa

### Scenario Reale

**Azienda:** Acme Corp
**Tenant SharePoint:** `acmecorp.sharepoint.com`
**Team:** "Customer Care"
**Cartella:** Files → Matrici

### Percorso SharePoint
```
\\acmecorp.sharepoint.com@SSL\sites\CustomerCare\Shared Documents\Matrici\matrici.accdb
```

### database_config.ini
```ini
[database]
type = access

[access]
path = \\acmecorp.sharepoint.com@SSL\sites\CustomerCare\Shared Documents\Matrici\matrici.accdb
auto_compact_size_mb = 100
```

### Verifica Accessibilità
```cmd
# Test 1: Apri in Esplora File
Win+R → \\acmecorp.sharepoint.com@SSL\sites\CustomerCare\Shared Documents\Matrici

# Test 2: Verifica setup
python verifica_setup.py

# Test 3: Apri Matrici
Matrici.exe
```

---

## 🔗 Link Utili Microsoft

- [SharePoint file paths](https://support.microsoft.com/en-us/office/open-a-sharepoint-library-in-file-explorer-aaee7bfb-e2a1-42ee-8fc0-bcc0754f04d2)
- [Teams file storage](https://support.microsoft.com/en-us/office/where-are-my-files-stored-in-microsoft-teams-7cbe4937-6382-4f35-9d09-1f3a853e1a9a)
- [Access database on SharePoint](https://support.microsoft.com/en-us/office/import-data-from-or-link-to-data-on-a-sharepoint-list-c9cb3f11-9ac0-4b27-8fc7-dcbbc6deb1d2)

---

## 📞 Supporto

**Problemi comuni SharePoint:**
1. Percorso UNC errato → Verifica formato con `@SSL`
2. Autenticazione fallita → Apri manualmente database per autenticarti
3. Performance lente → Verifica connessione internet, compatta database
4. Database bloccato → Verifica chi ha file aperto in SharePoint

**Per supporto IT aziendale:**
- Fornisci percorso UNC completo
- Verifica permessi SharePoint
- Chiedi di abilitare versioning

---

✅ **Configurazione SharePoint completata!** Ora hai Matrici su Teams/SharePoint accessibile a tutto il team! 🎉
