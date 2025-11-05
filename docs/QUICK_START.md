# Guida Rapida Matrici

## Primi Passi

### 1. Installazione

**Utente finale (Windows):**
- Scarica `Matrici.exe`
- Doppio click per avviare
- Nessuna installazione richiesta!

**Sviluppatore:**
```bash
pip install -r requirements.txt
python main.py
```

### 2. Inizializzazione Database

Al primo avvio:
1. Menu **Database** → **Crea/Inizializza Database**
2. Verrà creato `data/operator_overtime.db`

**Per test rapido:**
```bash
python scripts/populate_test_data.py
```
Questo crea 5 operatori di esempio con turni, pause, straordinari e forecast.

### 3. Workflow Tipico

#### A. Inserimento Dati Giornalieri

**Mattina - Pianificazione:**
1. Tab **Gestione Operatori**
2. Per ogni operatore, inserire/aggiornare:
   - Turno del giorno
   - Straordinari pianificati
   - Pause previste
   - Assenze/Permessi (giustificativi)
   - Skill principale

**Se operatore cambia skill durante il giorno:**
- Aggiungere record in `Cambio_Skill`
- Es: "Mario dalle 15:00 alle 16:00 supporta Back Office"

#### B. Monitoraggio Intraday

**Dashboard in tempo reale:**
1. Tab **Dashboard**
2. Seleziona data odierna
3. Scegli intervallo: 15 o 30 minuti
4. Click **Aggiorna**

**Interpretare i dati:**
- **Presenti**: Operatori in turno (ordinario + straordinario)
- **In Pausa**: Operatori in pausa pranzo/caffè
- **In Produzione**: Operatori effettivamente disponibili (Presenti - In Pausa)
- **In Straordinario**: Operatori in straordinario
- **FTE Effettivi**: Capability disponibile
- **FTE Richiesti**: Fabbisogno dal forecast
- **Delta**: Differenza (positivo = surplus, negativo = deficit)
- **Copertura %**: Percentuale di copertura

**Colori:**
- 🟢 Verde (>=95%): Copertura OK
- 🟡 Giallo (80-94%): Sottocopertura lieve
- 🔴 Rosso (<80%): Sottocopertura critica

**Azioni su sottocopertura:**
- Verificare operatori in pausa
- Considerare richiamo straordinario
- Valutare riassegnazione skill

#### C. Import Forecast

**Preparare file Excel:**
Colonne richieste:
- `Data_Riferimento`: es. 2024-01-15
- `Fascia_Oraria`: es. 09:00
- `Skill`: es. CUSTOMER_CARE
- `Volumi_Attesi`: es. 100
- `Produttivita_Target`: es. 8.0
- `FTE_Richiesti`: calcolato come Volumi/Produttivita (es. 100/8 = 12.5)

**Importare:**
1. Tab **Forecast**
2. Click **Importa Forecast da Excel**
3. Seleziona file

#### D. Report Fine Giornata/Settimana

**Report per Servizio/Skill:**
1. Tab **Report**
2. Seleziona periodo (es. Lunedì-Venerdì)
3. Click **Genera Report Servizio**
4. Visualizza ore totali, produzione, pause, straordinario per ogni skill

**Report per Persona:**
1. Tab **Report**
2. Seleziona periodo
3. Click **Genera Report Persona**
4. Visualizza ore individuali per ogni operatore

**Export Excel:**
- Dashboard: Click **Esporta Excel** per salvare snapshot
- Report: Click destro → Export (in sviluppo)

## Casi d'Uso Comuni

### Scenario 1: Turno Ordinario con Pausa Pranzo
```
Mario Rossi - CUSTOMER_CARE
Turno: 09:00-18:00
Pausa: 13:00-14:00

Risultato:
- 09:00-13:00: In produzione (4h)
- 13:00-14:00: In pausa (1h)
- 14:00-18:00: In produzione (4h)
Totale produzione: 8h
```

### Scenario 2: Turno Spezzato
```
Anna Neri - TECHNICAL_SUPPORT
Turno parte 1: 08:00-13:00
Turno parte 2: 14:00-17:00
Pause: 10:00-10:15, 15:00-15:15

Risultato:
- Mattina: 5h (con 15min pausa)
- Pomeriggio: 3h (con 15min pausa)
Totale produzione: 7.5h
```

### Scenario 3: Straordinario Serale
```
Laura Bianchi - CUSTOMER_CARE
Turno ordinario: 09:00-18:00
Straordinario: 18:00-20:00
Pausa: 13:00-14:00

Risultato:
- Ore ordinarie: 8h
- Ore straordinario: 2h
- Totale: 10h (8h ordinarie + 2h strao)
```

### Scenario 4: Cambio Skill Intraday
```
Mario Rossi - CUSTOMER_CARE
Cambio skill: 15:00-16:00 → BACK_OFFICE

Calcolo capability:
- 09:00-15:00: CUSTOMER_CARE
- 15:00-16:00: BACK_OFFICE
- 16:00-18:00: CUSTOMER_CARE

Rendiconto ore per servizio:
- CUSTOMER_CARE: 7h
- BACK_OFFICE: 1h
```

### Scenario 5: Assenza Parziale
```
Giuseppe Verdi - BACK_OFFICE
Turno: 14:00-18:00
Giustificativo: Permesso 16:00-18:00

Risultato:
- 14:00-16:00: In produzione (2h)
- 16:00-18:00: Assente
Totale: 2h lavorate
```

## Tips & Tricks

### Ottimizzazione Input Dati
- **Template Excel**: Prepara template per import massivo operatori
- **Copia turni**: Usa stesso turno per più giorni (future feature)
- **Skill predefinite**: Crea anagrafica skills una volta, poi riusa

### Analisi Dashboard
- **Filtro per skill**: Usa dropdown skill per analisi mirata
- **Export frequente**: Esporta snapshot ogni ora per tracking
- **Double-click**: Doppio click su fascia per dettaglio operatori (in dev)

### Report
- **Confronto settimanale**: Genera report settimana corrente vs precedente
- **Alert rossi**: Identifica fasce critiche per azioni correttive future
- **Analisi trend**: Esporta più giorni e analizza pattern in Excel

### Performance
- **Database leggero**: SQLite gestisce migliaia di record senza problemi
- **Backup giornaliero**: Menu Database → Backup (in sviluppo)
- **Pulizia dati vecchi**: Elimina dati oltre 3 mesi se non servono

## Troubleshooting

**Problema: Database non si crea**
- Soluzione: Verifica permessi cartella `data/`
- Alternativa: Crea manualmente cartella `data/`

**Problema: Import Excel fallisce**
- Soluzione: Verifica formato colonne (vedi sezione Import Forecast)
- Tip: Usa file di esempio come template

**Problema: Dashboard vuota**
- Causa: Nessun operatore per la data selezionata
- Soluzione: Verifica `Data_Riferimento` in anagrafica operatori

**Problema: Calcoli capability errati**
- Causa: Overlap orari turno/pause/strao
- Soluzione: Verifica non ci siano sovrapposizioni negli orari

**Problema: Exe non si avvia**
- Soluzione: Antivirus potrebbe bloccarlo
- Alternativa: Esegui da Python: `python main.py`

## Contatti e Supporto

Per assistenza:
1. Consulta README.md per documentazione completa
2. Verifica esempi in `scripts/populate_test_data.py`
3. Apri issue su GitHub per bug/feature request

---

**Buon lavoro con Matrici!** 🚀
