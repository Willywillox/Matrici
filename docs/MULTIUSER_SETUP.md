# Setup Multi-Utente Matrici

## Panoramica

Matrici supporta **3 modalità di lavoro multi-utente**:

1. **SQL Server** - Consigliato per 10+ utenti
2. **Access su Rete** - Per piccoli team (max 10 utenti)
3. **SQLite Locale** - Solo singolo utente (default)

---

## 🏆 Soluzione Consigliata: SQL Server Express

### Perché SQL Server?

✅ **Gratuito** (Express Edition)
✅ **Affidabile** - Gestisce centinaia di utenti
✅ **Sicuro** - Autenticazione integrata Windows
✅ **Veloce** - Ottime performance
✅ **Backup automatici**
✅ **Nessun rischio corruzione dati**

---

## 📋 Setup SQL Server Passo-Passo

### Fase 1: Installazione SQL Server Express

**Sul server (o PC centrale):**

1. **Scarica SQL Server Express:**
   - Vai su: https://www.microsoft.com/it-it/sql-server/sql-server-downloads
   - Scarica "Express" (gratuito)

2. **Installa SQL Server:**
   ```
   - Scegli "Basic" o "Custom"
   - Nome istanza: SQLEXPRESS (default)
   - Abilita "Mixed Mode" authentication (opzionale)
   - Annotare nome server: es. NOME-PC\SQLEXPRESS
   ```

3. **Installa SQL Server Management Studio (SSMS):**
   - Scarica da: https://docs.microsoft.com/it-it/sql/ssms/download-sql-server-management-studio-ssms
   - Utile per gestione database (opzionale ma consigliato)

### Fase 2: Configurazione SQL Server

**Abilita connessioni di rete:**

1. Apri **SQL Server Configuration Manager**

2. **Abilita TCP/IP:**
   ```
   SQL Server Network Configuration →
   Protocols for SQLEXPRESS →
   TCP/IP → Right Click → Enable
   ```

3. **Configura porta TCP/IP:**
   ```
   TCP/IP → Properties → IP Addresses →
   IPAll → TCP Port: 1433
   ```

4. **Riavvia servizio SQL Server:**
   ```
   SQL Server Services →
   SQL Server (SQLEXPRESS) → Right Click → Restart
   ```

5. **Configura Windows Firewall:**
   ```powershell
   # Esegui come amministratore
   netsh advfirewall firewall add rule name="SQL Server" dir=in action=allow protocol=TCP localport=1433
   ```

### Fase 3: Creazione Database Matrici

**Opzione A: Con SSMS (consigliato)**

1. Apri SQL Server Management Studio
2. Connetti a: `localhost\SQLEXPRESS`
3. File → Open → File → Seleziona `scripts/create_sqlserver_database.sql`
4. Clicca Execute (F5)
5. Verifica output: "Database Matrici creato con successo!"

**Opzione B: Con sqlcmd (command line)**

```cmd
cd C:\Matrici
sqlcmd -S localhost\SQLEXPRESS -i scripts\create_sqlserver_database.sql
```

**Opzione C: Con Python (automatico)**

```bash
python scripts/setup_sqlserver.py
```

### Fase 4: Configurazione Applicazione

**Su ogni PC client:**

1. **Copia file di configurazione:**
   ```
   Copia database_config.ini.example → database_config.ini
   ```

2. **Modifica `database_config.ini`:**
   ```ini
   [database]
   type = sqlserver
   server = NOME-SERVER\SQLEXPRESS
   database = Matrici
   trusted_connection = yes

   [multiuser]
   auto_refresh = yes
   refresh_interval = 30
   show_notifications = yes
   ```

3. **Sostituisci NOME-SERVER:**
   - Se server è stesso PC: `localhost\SQLEXPRESS`
   - Se server è altro PC: `NOME-PC\SQLEXPRESS` o `IP\SQLEXPRESS`
   - Esempio: `192.168.1.100\SQLEXPRESS`

4. **Installa driver ODBC (se necessario):**
   - Scarica: https://docs.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server
   - Installa "ODBC Driver 17 for SQL Server"

5. **Testa connessione:**
   - Avvia Matrici
   - Menu Database → Info Database
   - Verifica che mostri "SQL Server"

### Fase 5: Test Multi-Utente

1. **PC 1**: Apri Matrici, vai a Anagrafica
2. **PC 2**: Apri Matrici, vai a Anagrafica
3. **PC 1**: Inserisci nuovo operatore
4. **PC 2**: Clicca "🔄 Aggiorna" → Vedi operatore inserito da PC 1 ✅

---

## 🌐 Alternativa: Access su Rete Condivisa

**Per max 10 utenti in ufficio**

### Setup

1. **Crea share di rete:**
   ```
   Server: Crea cartella: C:\MatriciData
   Share come: \\server\MatriciData
   Permessi: Lettura/Scrittura per tutti gli utenti
   ```

2. **Copia database:**
   ```
   Copia: operator_overtime.accdb
   In: \\server\MatriciData\
   ```

3. **Configura `database_config.ini` su ogni PC:**
   ```ini
   [database]
   type = access
   path = \\server\MatriciData\operator_overtime.accdb

   [multiuser]
   auto_refresh = yes
   refresh_interval = 60
   ```

4. **Installa Access Database Engine su ogni PC:**
   - Scarica: https://www.microsoft.com/en-us/download/details.aspx?id=54920
   - Installa versione 64-bit

### Limitazioni Access

⚠️ **Max 10-15 utenti simultanei**
⚠️ **Performance limitate su rete lenta**
⚠️ **Rischio corruzione con troppi accessi**
⚠️ **Nessun vero lock management**

---

## 🔄 Funzionalità Multi-Utente

### Refresh Automatico

L'applicazione **aggiorna automaticamente i dati** ogni X secondi:

```ini
[multiuser]
refresh_interval = 30  # secondi
```

**Cosa viene aggiornato:**
- Lista operatori
- Dashboard capability
- Report riepilogo

**Quando:**
- Automaticamente ogni 30 secondi (configurabile)
- Manualmente cliccando "🔄 Aggiorna"

### Notifiche Modifiche

Quando un altro utente modifica dati, vedrai:

```
┌─────────────────────────────────────────────┐
│ ℹ️  Dati Aggiornati                         │
├─────────────────────────────────────────────┤
│ L'utente "Mario Rossi" ha modificato        │
│ l'anagrafica operatori.                     │
│                                             │
│ [Aggiorna Ora] [Ignora]                    │
└─────────────────────────────────────────────┘
```

### Gestione Conflitti

**Scenario: Due utenti modificano stesso operatore**

1. **User 1** apre operatore "Mario Rossi" per modifica
2. **User 2** apre stesso operatore "Mario Rossi" per modifica
3. **User 1** salva → ✅ Salvato con successo
4. **User 2** salva → ⚠️ Messaggio:

```
┌─────────────────────────────────────────────┐
│ ⚠️  Conflitto Rilevato                      │
├─────────────────────────────────────────────┤
│ Questo operatore è stato modificato da      │
│ un altro utente nel frattempo.              │
│                                             │
│ Vuoi:                                       │
│ • Sovrascrivere le modifiche dell'altro    │
│ • Ricaricare e perdere le tue modifiche    │
│ • Annullare                                 │
└─────────────────────────────────────────────┘
```

### Utenti Online

Nella status bar vedi chi è connesso:

```
┌─────────────────────────────────────────────┐
│ 👥 Utenti online: Mario, Laura, Giuseppe    │
└─────────────────────────────────────────────┘
```

---

## 🔒 Sicurezza

### Autenticazione Windows (SQL Server)

**Setup:**
```ini
[database]
trusted_connection = yes
```

**Vantaggi:**
- Usa credenziali Windows
- Nessuna password da memorizzare
- Gestione centralizzata utenti in Active Directory

### Autenticazione SQL Server

**Setup:**
```ini
[database]
trusted_connection = no
username = matrici_user
password = SecurePassword123!
```

**Creare utente SQL:**
```sql
USE Matrici;
CREATE LOGIN matrici_user WITH PASSWORD = 'SecurePassword123!';
CREATE USER matrici_user FOR LOGIN matrici_user;
ALTER ROLE db_datareader ADD MEMBER matrici_user;
ALTER ROLE db_datawriter ADD MEMBER matrici_user;
```

### Permessi Granulari

**Esempio: Utente READ-ONLY**

```sql
-- Crea utente che può solo leggere
CREATE LOGIN matrici_readonly WITH PASSWORD = 'ReadOnly123!';
CREATE USER matrici_readonly FOR LOGIN matrici_readonly;
ALTER ROLE db_datareader ADD MEMBER matrici_readonly;
```

---

## 🔧 Troubleshooting

### Errore: "Named Pipes Provider, error: 40"

**Causa:** SQL Server non accetta connessioni remote

**Soluzione:**
1. Verifica servizio SQL Server attivo
2. Abilita TCP/IP (vedi Fase 2)
3. Riavvia servizio SQL Server
4. Verifica firewall

### Errore: "Login failed for user"

**Causa:** Autenticazione fallita

**Soluzione:**
1. Verifica `trusted_connection = yes` in config
2. Utente Windows ha permessi su database?
3. Prova con utente SQL Server

### Errore: "Database locked"

**Causa:** File Access in uso

**Soluzione:**
1. Chiudi tutte le istanze Matrici
2. Verifica nessun processo blocca .accdb
3. Riavvia tutti i client
4. Considera migrazione a SQL Server

### Performance Lente

**Causa:** Troppi utenti su Access o rete lenta

**Soluzione:**
1. Migra a SQL Server
2. Aumenta `refresh_interval` in config
3. Disabilita `auto_refresh` temporaneamente
4. Usa filtri per ridurre dati caricati

### Dati Non Aggiornati

**Causa:** Refresh disabilitato o intervallo troppo lungo

**Soluzione:**
1. Clicca manualmente "🔄 Aggiorna"
2. Riduci `refresh_interval` (es: 15 secondi)
3. Verifica `auto_refresh = yes`

---

## 📊 Architettura Multi-Utente

### SQL Server

```
┌─────────────┐      ┌─────────────┐      ┌─────────────┐
│  Utente 1   │      │  Utente 2   │      │  Utente 10  │
│  PC Ufficio │      │  PC Ufficio │      │  PC Ufficio │
│             │      │             │      │             │
│  Matrici.exe│      │  Matrici.exe│      │  Matrici.exe│
└──────┬──────┘      └──────┬──────┘      └──────┬──────┘
       │                    │                    │
       │    Rete Locale (TCP/IP - Porta 1433)   │
       └────────────────────┼────────────────────┘
                            │
                            ▼
                   ┌─────────────────┐
                   │   SQL Server    │
                   │  \\server\       │
                   │   SQLEXPRESS     │
                   │                 │
                   │  Database:      │
                   │  - Matrici      │
                   │                 │
                   │  Gestisce:      │
                   │  • Transazioni  │
                   │  • Lock         │
                   │  • Concorrenza  │
                   │  • Backup       │
                   └─────────────────┘
```

### Access su Rete

```
┌─────────────┐      ┌─────────────┐
│  Utente 1   │      │  Utente 2   │
│  Matrici.exe│      │  Matrici.exe│
└──────┬──────┘      └──────┬──────┘
       │                    │
       │  Rete Condivisa    │
       └────────┬───────────┘
                │
                ▼
      ┌──────────────────────┐
      │  \\server\share      │
      │  operator_overtime   │
      │  .accdb              │
      │                      │
      │  (File condiviso)    │
      └──────────────────────┘
```

---

## 🎯 Raccomandazioni Finali

### Per 2-5 Utenti
→ **Access su Rete** va bene
- Setup veloce
- Nessun server dedicato necessario

### Per 6-15 Utenti
→ **SQL Server Express** consigliato
- Più affidabile
- Migliori performance
- Preparato per crescita

### Per 15+ Utenti
→ **SQL Server Standard** (a pagamento)
- Features enterprise
- Backup automatici
- High availability

### Per Uso Remoto (da casa)
→ **Considera architettura Web**
- Accesso via browser
- Nessuna installazione client
- VPN non necessaria

---

## 📚 Risorse

**SQL Server:**
- Download: https://www.microsoft.com/it-it/sql-server/sql-server-downloads
- Documentazione: https://docs.microsoft.com/it-it/sql/sql-server/

**ODBC Driver:**
- Download: https://docs.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server

**Access Database Engine:**
- Download: https://www.microsoft.com/en-us/download/details.aspx?id=54920

---

**Per supporto: aprire issue su GitHub o contattare il team IT aziendale**
