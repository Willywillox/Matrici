# 📊 Guida Import Excel Operatori

## Come Caricare Massivamente gli Operatori da Excel

Invece di inserire operatori uno per uno, puoi caricarli tutti insieme da un file Excel.

---

## 🎯 Procedura Completa

### STEP 1: Crea il Template Excel

```cmd
python scripts/create_excel_template.py
```

Questo crea il file: `templates/template_import_operatori.xlsx`

**Il template contiene:**
- Header con tutte le colonne necessarie
- Colori per identificare le sezioni
- Riga di esempio da copiare/modificare
- Foglio "Istruzioni" con guida completa

---

### STEP 2: Compila il File Excel

Apri `template_import_operatori.xlsx` con Excel/LibreOffice e compila:

#### 📌 COLONNE OBBLIGATORIE (sfondo rosso)

| Colonna | Esempio | Note |
|---------|---------|------|
| **Nome** | Mario | Nome operatore |
| **Cognome** | Rossi | Cognome operatore |
| **ID_SAP** | 12345 | Codice univoco (testo!) |
| **Data_Riferimento** | 2025-01-15 | Formato YYYY-MM-DD |

#### 📋 COLONNE OPZIONALI

**ANAGRAFICA (sfondo azzurro):**
- `Tipo_Contratto`: Full Time, Part Time, Apprendista
- `FTE`: 1 (100%), 0.5 (50%), ecc.
- `Ore_Settimana`: 40, 36, 20, ecc.

**TURNO (sfondo verde):**
- `ID_Turno`: T1, MATTINA, POME
- `Ora_Inizio_Turno`: 09:00
- `Ora_Fine_Turno`: 18:00
- `Ora_Inizio_Turno_Spezzato`: (se turno spezzato)
- `Ora_Fine_Turno_Spezzato`: (se turno spezzato)

**STRAORDINARI (sfondo giallo) - 3 slot:**
- `Inizio_Strao_1`: 18:00
- `Fine_Strao_1`: 20:00
- `Inizio_Strao_2`: ...
- `Fine_Strao_2`: ...
- `Inizio_Strao_3`: ...
- `Fine_Strao_3`: ...

**PAUSE (sfondo viola) - 5 slot:**
- `Inizio_Pausa_1`: 12:00
- `Fine_Pausa_1`: 13:00
- `Inizio_Pausa_2`: ...
- `Fine_Pausa_2`: ...
- ... (fino a Pausa_5)

**GIUSTIFICATIVI (sfondo arancione) - 5 slot:**
- `Tipo_Giust_1`: Assenza, Ferie, Malattia, Permesso, ROL, Congedo
- `Inizio_Giust_1`: 09:00
- `Fine_Giust_1`: 18:00
- ... (fino a Giust_5)

**SKILL E POSTAZIONE (sfondo grigio):**
- `Etichetta_Skill`: Customer Care, Tech Support, Vendite
- `Postazione`: Sede, Smart Working, Trasferta, Permesso, Assente

---

### STEP 3: Importa in Matrici

Hai **2 opzioni**:

#### OPZIONE A: Da Interfaccia Grafica (Raccomandato)

1. Apri `Matrici.exe`
2. Vai su tab **Anagrafica**
3. Click su **📊 Importa Excel**
4. Seleziona il tuo file Excel compilato
5. Conferma import
6. Aspetta che finisca (vedi progresso in tempo reale)
7. Click "Chiudi" quando vedi "✓ IMPORT COMPLETATO"

#### OPZIONE B: Da Riga di Comando

```cmd
python scripts/import_excel_operatori.py --file percorso/mio_file.xlsx
```

Esempio:
```cmd
python scripts/import_excel_operatori.py --file C:\Dati\operatori_gennaio.xlsx
```

Se il file Excel ha più fogli, specifica quale:
```cmd
python scripts/import_excel_operatori.py --file C:\Dati\operatori.xlsx --sheet "Operatori"
```

---

## 📝 Formati Supportati

### Date
- `YYYY-MM-DD` (raccomandato): 2025-01-15
- `DD/MM/YYYY`: 15/01/2025
- `MM/DD/YYYY`: 01/15/2025

### Orari
- `HH:MM` (raccomandato): 09:00, 18:30
- `HH:MM:SS`: 09:00:00, 18:30:00
- Anche formati Excel nativi (come frazione di giorno)

### Numeri
- FTE: `1`, `0.5`, `0.8`
- Ore: `40`, `36.5`, `20`

---

## ⚠️ Comportamento Import

### Nuovo Record
Se **ID_SAP + Data** NON esistono nel database:
- ✅ Viene creato NUOVO record
- Messaggio: `✓ Riga X: Nome Cognome - IMPORTATO`

### Record Esistente
Se **ID_SAP + Data** esistono già nel database:
- 🔄 Il record viene AGGIORNATO con i nuovi valori
- Messaggio: `↻ Riga X: Nome Cognome - AGGIORNATO`

### Righe con Errori
- ❌ Saltate e segnalate alla fine
- Esempio: Campi obbligatori mancanti, date non valide

---

## 📊 Esempio Pratico

### Scenario: Import 50 operatori per 15 Gennaio

**File Excel:**
```
Nome    | Cognome | ID_SAP | Data_Riferimento | Tipo_Contratto | FTE | Ora_Inizio_Turno | Ora_Fine_Turno | Etichetta_Skill | Postazione
--------|---------|--------|------------------|----------------|-----|------------------|----------------|-----------------|------------
Mario   | Rossi   | 12345  | 2025-01-15       | Full Time      | 1   | 09:00            | 18:00          | Customer Care   | Sede
Laura   | Bianchi | 12346  | 2025-01-15       | Part Time      | 0.5 | 09:00            | 13:00          | Tech Support    | Smart Working
Paolo   | Verdi   | 12347  | 2025-01-15       | Full Time      | 1   | 14:00            | 22:00          | Customer Care   | Sede
...     | ...     | ...    | ...              | ...            | ... | ...              | ...            | ...             | ...
(altre 47 righe)
```

**Esegui import:**
```cmd
python scripts/import_excel_operatori.py --file operatori_15gen.xlsx
```

**Output:**
```
============================================================
  IMPORT EXCEL OPERATORI
============================================================

✓ File letto: operatori_15gen.xlsx
  Righe trovate: 50

Inizio import...

  ✓ Riga 2: Mario Rossi (ID_SAP: 12345) - IMPORTATO
  ✓ Riga 3: Laura Bianchi (ID_SAP: 12346) - IMPORTATO
  ✓ Riga 4: Paolo Verdi (ID_SAP: 12347) - IMPORTATO
  ...

============================================================
  RIEPILOGO IMPORT
============================================================
  ✓ Nuovi operatori importati:     50
  ↻ Operatori aggiornati:          0
  ✗ Righe saltate (errori):        0
============================================================
```

---

## 🔧 Consigli e Best Practices

### 1️⃣ Usa sempre il Template
- Crea sempre da `create_excel_template.py`
- NON modificare i nomi delle colonne
- Colori aiutano a identificare le sezioni

### 2️⃣ Valida i Dati Prima
- Controlla che ID_SAP siano univoci
- Verifica date nel formato corretto
- Assicurati orari siano logici (inizio < fine)

### 3️⃣ Fai Backup Prima di Import Massivi
```cmd
copy "\\SERVER\Condivisa\Matrici\matrici.accdb" "\\BACKUP\matrici_backup_%date%.accdb"
```

### 4️⃣ Importa in Blocchi
Se hai 1000+ operatori:
- Dividi in file da 100-200 righe
- Importa a blocchi
- Verifica risultati tra un import e l'altro

### 5️⃣ Testa Prima con Pochi Record
- Crea file di test con 5-10 operatori
- Importa e verifica che tutto sia corretto
- Poi procedi con file completo

### 6️⃣ Gestisci Duplicati
Se importi lo stesso file 2 volte:
- I record vengono AGGIORNATI (non duplicati)
- Usa questo per correzioni massive

---

## ❓ Problemi Comuni

### "Colonne obbligatorie mancanti"
❌ **Errore:** Il file Excel non ha le colonne corrette
✅ **Soluzione:** Usa il template creato con `create_excel_template.py`

### "Riga X: Campi obbligatori mancanti"
❌ **Errore:** Nome, Cognome, ID_SAP o Data sono vuoti
✅ **Soluzione:** Compila tutti i campi obbligatori (sfondo rosso nel template)

### "Errore lettura file Excel"
❌ **Errore:** File Excel corrotto o formato non supportato
✅ **Soluzione:**
- Salva come .xlsx (non .xls vecchio formato)
- Verifica che openpyxl sia installato: `pip install openpyxl`

### "ID_SAP duplicati"
❌ **Errore:** Stesso ID_SAP compare 2+ volte nello stesso file
✅ **Soluzione:**
- Se stessa data: L'ultimo sovrascrive il primo (OK se voluto)
- Se date diverse: Entrambi vengono importati (OK, normale)

### "Orari non validi"
❌ **Errore:** Orario scritto male (es. "9" invece di "09:00")
✅ **Soluzione:** Usa formato HH:MM (es. 09:00, 18:30)

---

## 🚀 Workflow Consigliato

### Setup Iniziale (Prima volta)
```cmd
# 1. Crea template
python scripts/create_excel_template.py

# 2. Apri template con Excel
start templates\template_import_operatori.xlsx

# 3. Compila dati operatori

# 4. Salva come "operatori_gennaio.xlsx"

# 5. Importa
python scripts\import_excel_operatori.py --file operatori_gennaio.xlsx
```

### Aggiornamenti Mensili
```cmd
# 1. Copia template del mese precedente
copy operatori_gennaio.xlsx operatori_febbraio.xlsx

# 2. Modifica date e dati in Excel

# 3. Importa nuovo mese
python scripts\import_excel_operatori.py --file operatori_febbraio.xlsx
```

### Correzioni Massive
```cmd
# 1. Esporta dati attuali (se necessario)
#    Tab Riepilogo → Esporta Excel

# 2. Modifica Excel esportato

# 3. Re-importa (aggiorna record esistenti)
python scripts\import_excel_operatori.py --file operatori_corretti.xlsx
```

---

## 📞 Supporto

Per problemi:
1. Verifica di usare il template corretto
2. Controlla formato date e orari
3. Leggi messaggi di errore (indicano riga e problema)
4. Consulta foglio "Istruzioni" nel template

---

**Ora sei pronto per importare centinaia di operatori in pochi secondi!** 🎉
