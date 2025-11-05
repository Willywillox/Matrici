# Matrici - Gestione Turni e Capability Operatori

Tool desktop per la gestione e il monitoraggio della copertura operatori con analisi dettagliata di turni straordinari, pause, giustificativi e confronto con i forecast.

## Caratteristiche Principali

### 📊 Dashboard Intraday
- **Vista a fasce orarie configurabili**: 15 o 30 minuti
- **Tracking dettagliato**: Operatori presenti, in pausa, in produzione, in straordinario
- **Analisi per skill**: Capability disponibile per ogni competenza
- **Confronto con forecast**: Delta FTE effettivi vs richiesti con indicatori colorati
- **Dettaglio operatori**: Click su fascia oraria per vedere chi è presente

### 👥 Gestione Anagrafica Operatori
Dati completi per ogni operatore:
- Dati base: Nome, Cognome, ID SAP, Tipo Contratto, FTE, Ore Settimana
- Turno principale: Orario inizio/fine + turno spezzato
- 3 slot straordinari: Inizio e fine per ogni slot
- 5 slot pause: Orari pausa dettagliati
- 5 slot giustificativi: Tipo, inizio, fine (assenze, permessi, etc.)
- Skill principale: Etichetta competenza
- Cambio skill intraday: Tracking quando operatore cambia skill durante la giornata

### 📈 Report Completi
- **Rendiconto ore per servizio/skill**: Ore totali, produzione, pausa, straordinario
- **Rendiconto ore per persona**: Dettaglio individuale operatori
- **Periodi configurabili**: Giornaliero, settimanale, mensile
- **Export Excel**: Esportazione facile per ulteriori analisi

### 🎯 Forecast e Capability
- Import forecast volumi attesi
- Calcolo automatico FTE richiesti (Volumi ÷ Produttività)
- Confronto capability effettiva vs forecast
- Indicatori visivi: Verde (OK) | Giallo (Sottocopertura lieve) | Rosso (Critica)

## Installazione e Utilizzo

### Requisiti
- Windows 10/11 (o Linux/Mac per sviluppo)
- Python 3.8+ (solo per sviluppo, non necessario per exe)
- Microsoft Access Database Engine (opzionale, usa SQLite altrimenti)

### Installazione per Sviluppo

```bash
# Clone repository
git clone <repository-url>
cd Matrici

# Installa dipendenze
pip install -r requirements.txt

# Inizializza database e popola dati di test
python scripts/populate_test_data.py

# Avvia applicazione
python main.py
```

### Creazione Eseguibile Windows

```bash
# Su Windows
build_exe.bat

# L'eseguibile sarà in: dist/Matrici.exe
```

Distribuisci solo il file `Matrici.exe` - non richiede installazione di Python!

## 🌐 Uso Multi-Utente (10+ Persone)

Matrici supporta **lavoro collaborativo con database condiviso**!

### Setup Consigliato: SQL Server Express

**Per 10+ utenti che lavorano contemporaneamente:**

1. **Server (una volta):**
   ```bash
   # Installa SQL Server Express (gratuito)
   # Esegui setup automatico:
   python scripts/setup_sqlserver.py
   ```

2. **Ogni PC Client:**
   ```bash
   # Copia database_config.ini dal server
   # Modifica "server" con nome/IP del server
   # Avvia Matrici → Tutti vedono stessi dati!
   ```

**Funzionalità Multi-Utente:**
- ✅ **Refresh Automatico**: Vedi modifiche degli altri utenti ogni 30 sec
- ✅ **Notifiche**: Avvisi quando qualcuno modifica dati
- ✅ **Gestione Conflitti**: Protezione da modifiche concorrenti
- ✅ **Utenti Online**: Vedi chi è connesso
- ✅ **100+ utenti supportati**

**Alternativa Semplice: Access su Rete**

Per piccoli team (max 10 utenti):
```ini
# database_config.ini
[database]
type = access
path = \\server\share\operator_overtime.accdb
```

📚 **Guida Completa**: Vedi [`docs/MULTIUSER_SETUP.md`](docs/MULTIUSER_SETUP.md)

---

## Guida Rapida

### 1. Primo Avvio
- Vai su **Database → Crea/Inizializza Database**
- (Opzionale) Esegui `scripts/populate_test_data.py` per dati di esempio

### 2. Inserimento Operatori
- Tab **Gestione Operatori**
- Click **Nuovo Operatore**
- Compila tutti i campi richiesti:
  - Anagrafica base
  - Orari turno (anche spezzato se necessario)
  - Straordinari pianificati
  - Pause
  - Giustificativi (assenze, permessi)
  - Skill principale

### 3. Cambio Skill Intraday
Se un operatore cambia skill durante la giornata:
- Inserisci record in tabella `Cambio_Skill`
- Specifica: ID_SAP, Data, Ora Inizio/Fine, Skill Temporaneo

### 4. Import Forecast
- Tab **Forecast**
- Prepara Excel con colonne: Data, Fascia_Oraria, Skill, Volumi_Attesi, Produttivita_Target
- Click **Importa Forecast da Excel**

### 5. Visualizza Dashboard
- Tab **Dashboard**
- Seleziona data e intervallo (15 o 30 min)
- Click **Aggiorna**
- Analizza:
  - Operatori presenti per fascia
  - Capability per skill
  - Delta vs forecast
  - Copertura %

### 6. Genera Report
- Tab **Report**
- Seleziona periodo (inizio/fine)
- Click **Genera Report Servizio** per rendiconto ore per skill
- Click **Genera Report Persona** per rendiconto individuale

## Struttura Database

### Tabella: Anagrafica_Operatori
Contiene tutti i dati dell'operatore per una data specifica:
- Anagrafica: Nome, Cognome, ID_SAP, Tipo_Contratto, FTE, Ore_Settimana
- Turno: ID_Turno, Ora_Inizio_Turno, Ora_Fine_Turno, Ora_Inizio_Turno_Spezzato, Ora_Fine_Turno_Spezzato
- Straordinari (3 slot): Inizio_Strao_1-3, Fine_Strao_1-3
- Pause (5 slot): Inizio_Pausa_1-5, Fine_Pausa_1-5
- Giustificativi (5 slot): Tipo_Giust_1-5, Inizio_Giust_1-5, Fine_Giust_1-5
- Skill: Etichetta_Skill
- Data_Riferimento

### Tabella: Cambio_Skill
Tracking cambi skill durante la giornata:
- ID_SAP, Data_Riferimento, Ora_Inizio, Ora_Fine, Skill_Temporaneo, Note

### Tabella: Forecast
Volumi e FTE richiesti per fascia oraria:
- Data_Riferimento, Fascia_Oraria, Skill, Volumi_Attesi, Produttivita_Target, FTE_Richiesti

### Tabella: Skills
Anagrafica competenze:
- Codice_Skill, Descrizione, Produttivita_Default

## Logica di Calcolo Capability

Per ogni fascia oraria (es. 09:00-09:15):

1. **Operatori presenti**: Verifica chi è in turno (ordinario o spezzato o straordinario) e non ha giustificativi di assenza
2. **Operatori in pausa**: Chi è presente ma in uno slot di pausa
3. **Operatori in produzione**: Presenti - In pausa
4. **Operatori in straordinario**: Chi è in uno slot straordinario
5. **FTE Effettivi**: = Operatori in produzione
6. **Skill**: Etichetta_Skill principale, o Skill_Temporaneo se c'è cambio skill attivo
7. **Delta FTE**: FTE Effettivi - FTE Richiesti
8. **Copertura %**: (FTE Effettivi ÷ FTE Richiesti) × 100

### Indicatori Colorati
- Verde: Copertura >= 95%
- Giallo: Copertura 80-94%
- Rosso: Copertura < 80%

## Architettura Progetto

```
Matrici/
├── main.py                     # Entry point applicazione
├── requirements.txt            # Dipendenze Python
├── build_exe.spec             # Config PyInstaller
├── build_exe.bat              # Script build Windows
├── data/                      # Database SQLite/Access
│   └── operator_overtime.db
├── scripts/
│   └── populate_test_data.py  # Script dati di test
├── src/
│   ├── database/
│   │   ├── db_creator.py      # Creazione database
│   │   └── db_manager.py      # Gestione connessione e query
│   ├── models/
│   │   └── operatore.py       # Modello dati Operatore
│   ├── utils/
│   │   └── capability_calculator.py  # Calcolo capability
│   ├── gui/
│   │   └── main_window.py     # Interfaccia grafica principale
│   └── reports/               # Moduli report (future estensioni)
└── docs/                      # Documentazione
```

## Sviluppi Futuri

- [ ] Form completo inserimento/modifica operatori
- [ ] Import/export massivo da/verso Excel
- [ ] Visualizzazione grafica timeline operatori
- [ ] Report PDF automatici
- [ ] Notifiche sottocopertura
- [ ] Analisi predittiva copertura
- [ ] API REST per integrazioni
- [ ] Multi-lingua (IT/EN)

## Supporto

Per bug, richieste feature o domande, aprire una issue su GitHub.

## Licenza

[Da definire]

---

**Matrici** - Ottimizza la gestione dei tuoi operatori con visibilità completa su turni, capability e copertura.