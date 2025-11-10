# Guida all'Interfaccia Matrici

## Panoramica Interfaccia

L'applicazione Matrici presenta un'interfaccia user-friendly organizzata in **4 sezioni principali** (tab):

### 1. 📋 Anagrafica Operatori

**Funzione**: Gestione completa dell'anagrafica operatori con tutti i dettagli di turno.

#### Funzionalità:
- **➕ Nuovo Operatore**: Apre form dettagliato per inserimento completo
- **✏️ Modifica**: Modifica operatore selezionato (doppio click sulla riga)
- **🗑️ Elimina**: Elimina operatore con conferma
- **🔄 Aggiorna Lista**: Ricarica elenco operatori

#### Filtri Disponibili:
- **Data**: Visualizza operatori per data specifica
- **Skill**: Filtra per competenza

#### Form Inserimento Operatore:

Il form è organizzato in sezioni chiare e scorrevoli:

**DATI ANAGRAFICI**
- Nome * (obbligatorio)
- Cognome * (obbligatorio)
- ID SAP * (obbligatorio)
- Tipo Contratto (Full Time, Part Time, Tempo Determinato)
- FTE (es: 1.0 per full time, 0.5 per part time)
- Ore Settimana (es: 40 per full time)
- Data Riferimento * (data per cui valgono questi dati)

**TURNO ORDINARIO**
- ID Turno (codice turno aziendale)
- Ora Inizio - Ora Fine (es: 09:00 - 18:00)
- Turno Spezzato (opzionale): Ora Inizio - Ora Fine seconda parte

**STRAORDINARI (Max 3 Slot)**
- Slot 1: Inizio - Fine (es: 18:00 - 20:00)
- Slot 2: Inizio - Fine
- Slot 3: Inizio - Fine

**PAUSE (Max 5 Slot)**
- Pausa 1: Inizio - Fine (es: 13:00 - 14:00)
- Pausa 2-5: Inizio - Fine

**GIUSTIFICATIVI (Max 5 Slot)**
- Giustificativo 1: Tipo - Inizio - Fine
  - Tipi: Assenza, Ferie, Malattia, Permesso, ROL, Congedo
- Giustificativo 2-5: Tipo - Inizio - Fine

**SKILL / COMPETENZA**
- Etichetta Skill * (seleziona da lista predefinita)

#### Consigli Uso:
- I campi contrassegnati con * sono obbligatori
- Gli orari vanno inseriti in formato HH:MM (es: 09:30)
- Lasciare vuoti i campi non utilizzati
- Per turno spezzato: inserire entrambi gli orari di entrambe le parti

---

### 2. 📊 Dashboard Capability

**Funzione**: Visualizzazione in tempo reale della copertura per fasce orarie.

#### Controlli:
- **Data**: Seleziona giorno da analizzare
- **Intervallo**: Scegli tra fasce da 15 o 30 minuti
- **Filtra Skill**: Visualizza solo una competenza specifica o tutte
- **🔄 Aggiorna**: Ricalcola capability con parametri attuali
- **📊 Esporta Excel**: Salva snapshot corrente in Excel

#### Riepilogo Giornata (Cards Colorate):
Nella parte superiore trovi 4 indicatori principali:

- **FTE Totali Disponibili** (Verde): Operatori in produzione totali
- **FTE Richiesti** (Blu): Fabbisogno da forecast
- **Delta FTE** (Arancio): Differenza (positivo = surplus, negativo = deficit)
  - Verde se positivo
  - Rosso se negativo
- **Copertura Media %** (Viola): Percentuale media di copertura
  - Verde ≥ 95%
  - Arancio 80-94%
  - Rosso < 80%

#### Tabella Dettaglio Fasce:

Colonne:
- **Fascia**: Orario (es: 09:00, 09:15, 09:30...)
- **Skill**: Competenza
- **Presenti**: Operatori presenti (turno ordinario + straordinario)
- **In Pausa**: Operatori in pausa in quel momento
- **In Produzione**: Operatori effettivamente produttivi (Presenti - Pausa)
- **In Strao**: Operatori in straordinario
- **FTE Eff.**: Full Time Equivalent effettivi (= In Produzione)
- **FTE Rich.**: FTE richiesti da forecast
- **Delta**: Differenza (FTE Eff - FTE Rich)
- **Copertura %**: Percentuale copertura
- **Stato**: Indicatore visivo

#### Indicatori Colorati:
Ogni riga è colorata in base alla copertura:
- 🟢 **Verde (OK)**: Copertura ≥ 95% - Tutto regolare
- 🟡 **Giallo (Attenzione)**: Copertura 80-94% - Monitorare
- 🔴 **Rosso (Critico)**: Copertura < 80% - Azione richiesta!

#### Azioni:
- **Doppio Click su riga**: Mostra dettaglio operatori presenti in quella fascia
- **Export Excel**: Salva tutti i dati visualizzati

#### Interpretazione:
- **Presenti > In Produzione**: Ci sono operatori in pausa
- **In Strao > 0**: Ci sono operatori in straordinario
- **Delta Negativo**: Sottocopertura - considerare:
  - Richiamare operatori in pausa
  - Attivare straordinari
  - Riassegnare skill

---

### 3. 📈 Riepilogo

**Funzione**: Report aggregati con analisi per periodi estesi.

#### Parametri Report:

**Tipo Riepilogo:**
- **Giornaliero**: Analisi singola giornata
- **Settimanale**: Analisi settimana (Lun-Dom)
- **Mensile**: Analisi mese intero

**Periodo:**
- Data Inizio - Data Fine
- Nota: Tipo riepilogo suggerisce automaticamente le date

**Vista:**
- **Per Servizio/Skill**: Aggrega per competenza
- **Per Persona**: Aggrega per operatore

#### Tab Disponibili:

**Tab 1: Riepilogo Generale**

Cards Metriche Principali:
- **Ore Totali Lavorate** (Verde): Somma ore presenza
- **Ore Produzione** (Blu): Ore effettivamente produttive
- **Ore Pausa** (Arancio): Totale pause
- **Ore Straordinario** (Viola): Totale straordinari

Tabella Riepilogo:
- Vista aggregata per Skill o Persona secondo selezione

**Tab 2: Dettaglio per Periodo**
- Vista giornaliera dettagliata nel periodo
- Consente analisi granulare

**Tab 3: Grafici**
- (In sviluppo)
- Visualizzazioni grafiche trend

#### Funzionalità:
- **📊 Genera Report**: Calcola report con parametri attuali
- **📁 Esporta Excel**: Salva report in file Excel multi-sheet

#### Casi d'Uso:

**Rendiconto Settimanale**:
1. Seleziona "Settimanale"
2. Scegli settimana (es: Lun 01/01 - Dom 07/01)
3. Scegli "Per Persona"
4. Genera Report
→ Ottieni ore lavorate per ogni operatore nella settimana

**Analisi Servizio Mensile**:
1. Seleziona "Mensile"
2. Scegli mese
3. Scegli "Per Servizio/Skill"
4. Genera Report
→ Ottieni distribuzione ore per ogni competenza nel mese

---

### 4. 🎯 Forecast

**Funzione**: Gestione volumi previsti e FTE richiesti.

#### Funzionalità:
- **📂 Importa Forecast da Excel**: Carica file Excel con forecast
- **📝 Inserimento Manuale**: Form inserimento forecast (in sviluppo)

#### Formato Excel Richiesto:

Colonne obbligatorie:
- **Data_Riferimento**: Data (formato YYYY-MM-DD)
- **Fascia_Oraria**: Ora (formato HH:MM, es: 09:00, 09:15)
- **Skill**: Codice competenza
- **Volumi_Attesi**: Numero pratiche/chiamate attese
- **Produttivita_Target**: Pratiche/ora per operatore
- **FTE_Richiesti**: Calcolato come Volumi ÷ Produttività

Per dettagli completi vedi: `docs/TEMPLATE_FORECAST.md`

---

## Menu Applicazione

### Menu File
- **Esporta Report Completo**: Export completo tutti i dati
- **Esci**: Chiude applicazione

### Menu Database
- **Inizializza Database**: Crea struttura database se non esiste
- **Importa Dati Test**: Popola database con 5 operatori e forecast esempio
- **Info Database**: Mostra info su database corrente (Access o SQLite)

### Menu Aiuto
- **Guida Rapida**: Help contestuale
- **Info Applicazione**: Versione e credits

---

## Header Informazioni

Nella barra superiore trovi:
- **Titolo applicazione**
- **Database attivo**: Indica se Access o SQLite
- **Orologio**: Data e ora correnti (aggiornato automaticamente)

## Status Bar

Nella barra inferiore trovi lo stato corrente:
- "Pronto" - Applicazione pronta
- "Operatori caricati: X" - Dopo caricamento anagrafica
- Altri messaggi di stato

---

## Workflow Tipico Completo

### Setup Iniziale (Prima volta)

1. **Avvia applicazione**
2. **Menu Database → Inizializza Database**
3. **Menu Database → Importa Dati Test** (opzionale, per provare)
4. **Tab Anagrafica → ➕ Nuovo Operatore**: Inserisci operatori reali

### Uso Giornaliero

**Mattina - Pianificazione Giornata:**
1. **Tab Anagrafica**: Verifica/aggiorna operatori per oggi
   - Inserisci straordinari pianificati
   - Segna assenze/permessi
2. **Tab Forecast**: Verifica forecast del giorno caricato
3. **Tab Dashboard**: Prima analisi capability prevista

**Durante la Giornata - Monitoraggio:**
1. **Tab Dashboard**: Seleziona oggi + intervallo 15 min
2. **🔄 Aggiorna**: Vedi situazione corrente
3. **Analizza** fasce rosse/gialle:
   - Identifica sottocoperture
   - Prendi azioni correttive
4. **📊 Esporta Excel**: Snapshot per tracking

**Sera - Chiusura Giornata:**
1. **Tab Riepilogo**: Giornaliero, oggi
2. **Genera Report Persona**: Verifica ore lavorate
3. **Genera Report Servizio**: Distribuzione ore per skill
4. **📁 Esporta Excel**: Archivia report

**Fine Settimana/Mese:**
1. **Tab Riepilogo**: Settimanale o Mensile
2. **Genera Report**: Vista complessiva periodo
3. **Analizza trend** e pianifica settimana/mese successivo

---

## Shortcuts e Tips

### Shortcuts:
- **Doppio Click**: Modifica operatore (tab Anagrafica)
- **Doppio Click**: Dettaglio fascia (tab Dashboard)
- **F5**: Aggiorna dati (da implementare)

### Tips Navigazione:
- Usa i **filtri** per ridurre dati visualizzati
- **Export Excel** frequente per storicizzare dati
- Controlla **indicatori colorati** per azioni rapide
- Usa **Date Entry** con calendario pop-up per selezione date facile

### Performance:
- Filtra per **skill specifica** se hai molti operatori
- **Export** dati vecchi e rimuovi da database per velocità
- Database Access gestisce migliaia di record senza problemi

---

## Risoluzione Problemi Interfaccia

**Form non si apre:**
- Verifica database inizializzato
- Controlla permessi file database

**Dati non si vedono:**
- Verifica filtri applicati
- Clicca "🔄 Aggiorna"
- Verifica data selezionata corretta

**Export Excel fallisce:**
- Chiudi file Excel se già aperto
- Verifica permessi cartella destinazione

**Indicatori sempre "--":**
- Genera report prima (click "📊 Genera Report")
- Verifica presenza dati per periodo selezionato

---

**Per supporto completo**: Vedi `docs/QUICK_START.md` e `README.md`
