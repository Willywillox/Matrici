# Template Import Completo - Forecast per Skill

Template Excel per la gestione di forecast e richiesto per skill con intervalli di 15 minuti.

## 📋 Struttura Template

Il template è composto da **10 fogli** organizzati in 3 categorie:

### 1. Fogli Base (4 fogli)

- **Skills**: Definizione delle competenze/skill disponibili
- **Turni**: Pattern di turni standard
- **Operatori**: Dati degli operatori con assegnazione turni e skill
- **Istruzioni**: Documentazione completa del template

### 2. Fogli Forecast (3 fogli) - Prefisso `FC_`

Un foglio per ogni skill definito, contenente:
- **Righe**: Date (formato DD/MM/YYYY)
- **Colonne**: 96 fasce orarie di 15 minuti (00:00-00:15, 00:15-00:30, ..., 23:45-00:00)
- **Valori**: Numeri interi (volume previsto per fascia oraria)

Fogli creati automaticamente:
- `FC_FL_PS_PA` - Forecast Assistenza clienti telefonica e chat
- `FC_BO_PS_PA` - Forecast Gestione back office e pratiche amministrative
- `FC_CMB` - Forecast Supporto tecnico avanzato

### 3. Fogli Richiesto (3 fogli) - Prefisso `RQ_`

Un foglio per ogni skill definito, con struttura identica ai Forecast:
- **Righe**: Date (formato DD/MM/YYYY)
- **Colonne**: 96 fasce orarie di 15 minuti
- **Valori**: Numeri decimali (risorse richieste calcolate con Erlang C)

Fogli creati automaticamente:
- `RQ_FL_PS_PA` - Richiesto Assistenza clienti telefonica e chat
- `RQ_BO_PS_PA` - Richiesto Gestione back office e pratiche amministrative
- `RQ_CMB` - Richiesto Supporto tecnico avanzato

## 🔧 Script di Generazione

### `generate_forecast_sheets.py`

Genera i fogli forecast per ogni skill definito nel foglio Skills.

**Funzionalità:**
- Legge gli skill dal foglio Skills
- Crea un foglio forecast (FC_) per ogni skill
- Struttura: Date × Fasce orarie 15 min (96 colonne)
- Aggiunge validazione dati (combo box) per skill nel foglio Operatori

**Esecuzione:**
```bash
python3 generate_forecast_sheets.py
```

### `add_richiesto_sheets.py`

Genera i fogli richiesto per il calcolo Erlang C.

**Funzionalità:**
- Legge gli skill dal foglio Skills
- Crea un foglio richiesto (RQ_) per ogni skill
- Struttura identica ai fogli forecast (Date × Fasce orarie 15 min)
- Formattazione decimale per risultati Erlang

**Esecuzione:**
```bash
python3 add_richiesto_sheets.py
```

### `update_instructions.py`

Aggiorna il foglio Istruzioni con documentazione completa.

**Funzionalità:**
- Genera istruzioni dettagliate per l'uso del template
- Spiega struttura fogli Forecast e Richiesto
- Fornisce workflow consigliato

**Esecuzione:**
```bash
python3 update_instructions.py
```

## 📊 Utilizzo in Dashboard

### Workflow Forecast → Richiesto

1. **Compila Skills** - Definisci tutti gli skill disponibili nel foglio Skills
2. **Compila Forecast** - Inserisci volumi previsti nei fogli FC_ per ogni skill
3. **Calcola Richiesto** - Usa Erlang C per calcolare risorse necessarie (fogli RQ_)
4. **Filtra per Data** - In dashboard, filtra per data per confrontare forecast vs richiesto
5. **Analizza Gap** - Identifica discrepanze e pianifica azioni correttive

### Fasce Orarie

Ogni foglio contiene **96 colonne** con intervalli di 15 minuti:
- `00:00-00:15`, `00:15-00:30`, `00:30-00:45`, `00:45-01:00`
- ...
- `23:00-23:15`, `23:15-23:30`, `23:30-23:45`, `23:45-00:00`

Questo permette analisi granulari e calcoli Erlang precisi per ogni quarto d'ora.

## 🔄 Aggiunta Nuovi Skill

Quando aggiungi un nuovo skill al foglio Skills:

1. Inserisci nuovo skill nel foglio Skills (Codice_Skill, Descrizione, Produttivita_Default)
2. Esegui script per rigenerare fogli:
   ```bash
   python3 generate_forecast_sheets.py
   python3 add_richiesto_sheets.py
   ```
3. I nuovi fogli FC_ e RQ_ saranno creati automaticamente
4. La combo box nel foglio Operatori si aggiornerà automaticamente

## 📦 Requisiti

```bash
pip install openpyxl pandas
```

## 📝 Note Importanti

- Le date nei fogli Forecast e Richiesto devono coincidere per confronto corretto
- I codici skill devono essere univoci e coerenti in tutti i fogli
- Le fasce orarie di 15 minuti coprono l'intera giornata (96 intervalli)
- I fogli si aggiornano automaticamente quando aggiungi/rimuovi skill

## 📄 License

Questo template è stato creato per la gestione di workforce management e forecast per contact center.
