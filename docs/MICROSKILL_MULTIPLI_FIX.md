# Fix: Supporto Microskill Multipli per la Stessa Skill

## Problema Identificato

Quando si caricano skills con più microskill usando il template (es. CMB con cmb_pa e cmb_ba), solo l'ultimo microskill viene salvato nel database.

### Causa
1. La tabella `Skills` ha un vincolo `UNIQUE` sulla colonna `Codice_Skill`
2. Gli script di import controllano solo se esiste `Codice_Skill` e sovrascrivono il record esistente
3. Questo impedisce di avere più microskill per la stessa skill

## Soluzione

### Passo 1: Migrazione Database

Esegui lo script di migrazione per modificare la struttura della tabella Skills:

```bash
python scripts/migrate_skills_microskill_unique.py
```

Questo script:
- Rimuove il vincolo `UNIQUE` da `Codice_Skill`
- Aggiunge un vincolo `UNIQUE` sulla coppia `(Codice_Skill, Microskill)`
- Permette di avere più record con lo stesso `Codice_Skill` ma `Microskill` diversi

### Passo 2: Ricarica il Template

Dopo la migrazione, ricarica il template nella sezione Templates dell'applicazione.

Il template può ora contenere:
```
Codice_Skill | Descrizione        | Produttivita_Default | Microskill
-------------|-------------------|----------------------|------------
CMB          | Customer Manager   | 1.0                  | cmb_pa
CMB          | Customer Manager   | 1.0                  | cmb_ba
```

Entrambe le righe saranno importate correttamente come record separati.

## Modifiche Apportate

### 1. Script di Migrazione
- **File**: `scripts/migrate_skills_microskill_unique.py`
- Crea nuova tabella con vincolo UNIQUE su (Codice_Skill, Microskill)
- Migra i dati esistenti
- Sostituisce la tabella vecchia

### 2. Script Import Skills
- **File**: `scripts/import_skills.py`
- Controlla la combinazione (Codice_Skill, Microskill) invece di solo Codice_Skill
- Aggiorna solo il record specifico se esiste
- Inserisce nuovo record se la combinazione non esiste

### 3. Script Import Completo
- **File**: `scripts/import_completo.py`
- Aggiunto supporto per colonna Microskill
- Gestisce correttamente microskill multipli per stessa skill

## Verifica

Dopo aver eseguito la migrazione e ricaricato il template:

1. Apri il form Anagrafica
2. Clicca sul dropdown Microskill
3. Dovresti vedere entrambi `cmb_pa` e `cmb_ba`

Esegui lo script diagnostico per verificare:
```bash
python scripts/check_microskills.py
```

## Note
- Il vincolo UNIQUE sulla coppia (Codice_Skill, Microskill) impedisce duplicati
- Ogni combinazione Skill+Microskill è unica nel database
- Le skill senza microskill continuano a funzionare normalmente
