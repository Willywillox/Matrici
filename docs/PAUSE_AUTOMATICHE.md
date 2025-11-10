# 🤖 Sistema Pause Automatiche - Distribuzione Intelligente

## Come Funziona

Matrici include un **motore intelligente** che distribuisce automaticamente le pause tra gli operatori, evitando sovrapposizioni e garantendo copertura ottimale.

---

## 🎯 Logica di Funzionamento

### Slot Disponibili

Il sistema ha **3 slot di pause** disponibili:

| Slot | Offset dall'inizio turno | Esempio (turno 9:00-18:00) |
|------|--------------------------|----------------------------|
| **Slot 1** | **1h 45min** | Pausa: 10:45 - 11:00 |
| **Slot 2** | **2h 00min** | Pausa: 11:00 - 11:15 |
| **Slot 3** | **2h 15min** | Pausa: 11:15 - 11:30 |

**Durata pausa:** 15 minuti per ogni slot

---

### Distribuzione Intelligente

Quando calcoli pause per un operatore, il sistema:

1. **Analizza operatori esistenti**
   - Carica tutti gli operatori con **stesso skill** e **stessa data**
   - Conta quanti operatori sono già in ogni slot

2. **Identifica slot meno affollato**
   - Slot 1: 3 operatori
   - Slot 2: 5 operatori ← più affollato
   - Slot 3: 2 operatori ← meno affollato ✅

3. **Assegna slot ottimale**
   - Nuovo operatore → Slot 3 (meno affollato)
   - Risultato: **distribuzione bilanciata**!

---

## 📋 Come Usare

### **OPZIONE A - Da Form Operatore (Nuovo/Modifica)**

**1. Apri form operatore:**
- Tab Anagrafica → "➕ Nuovo Operatore"
- Oppure doppio click su operatore esistente

**2. Compila campi necessari:**
```
Ora Inizio Turno: 09:00
Ora Fine Turno:   18:00
Skill:            Customer Care
Data Riferimento: 2025-01-15
```

**3. Vai alla sezione PAUSE**

**4. Click su: "⚡ Calcola Ora"**

**5. Risultato:**
```
╔════════════════════════════════════════════════╗
║ ✅ Pause assegnate automaticamente!           ║
║                                                ║
║ Distribuzione attuale:                         ║
║ • Slot 1h45:  3 operatori                      ║
║ • Slot 2h:    5 operatori                      ║
║ • Slot 2h15:  2 operatori ← TU SEI QUI        ║
║                                                ║
║ Bilanciamento: OK                              ║
╚════════════════════════════════════════════════╝
```

**6. Pause compilate automaticamente:**
```
Pausa 1:
  Inizio: 11:15:00  (2h15 dopo inizio turno)
  Fine:   11:30:00  (durata 15 minuti)
```

**7. Salva operatore!**

---

### **OPZIONE B - Calcolo Manuale (Batch)**

Usa script Python per calcolare pause per più operatori:

```python
from src.utils.pause_scheduler import PauseScheduler
from src.database.db_manager import DatabaseManager

db = DatabaseManager()
scheduler = PauseScheduler(db)

# Calcola pause per operatore
pause = scheduler.calcola_pause_automatiche(
    ora_inizio_turno="09:00",
    ora_fine_turno="18:00",
    skill="Customer Care",
    data_riferimento="2025-01-15",
    id_sap_corrente=None,  # None se nuovo operatore
    num_pause=1            # 1 pausa di 15 minuti
)

print(pause)
# Output: [('11:15:00', '11:30:00')]
```

---

## 📊 Visualizzare Distribuzione

**Dopo calcolo, vedi:**

```
Slot 1h45: 3 | Slot 2h: 5 | Slot 2h15: 2 operatori
```

**Significato:**
- **3 operatori** hanno pausa dopo 1h45 dall'inizio turno
- **5 operatori** hanno pausa dopo 2h
- **2 operatori** hanno pausa dopo 2h15

**Bilanciamento:**
- ✅ **OK**: Differenza max 1-2 operatori tra slot
- ⚠️ **Sbilanciato**: Differenza > 2 operatori tra slot

---

## 🎨 Esempio Pratico

### Scenario: Team Customer Care con 9 operatori

**Tutti turno 9:00-18:00, skill "Customer Care", data 2025-01-15**

#### **Operatore 1 (primo inserito):**
```
Slot disponibili: 1h45=0, 2h=0, 2h15=0
→ Assegnato: Slot 1 (1h45) → Pausa 10:45-11:00
```

#### **Operatore 2:**
```
Slot disponibili: 1h45=1, 2h=0, 2h15=0
→ Assegnato: Slot 2 (2h) → Pausa 11:00-11:15
```

#### **Operatore 3:**
```
Slot disponibili: 1h45=1, 2h=1, 2h15=0
→ Assegnato: Slot 3 (2h15) → Pausa 11:15-11:30
```

#### **Operatore 4:**
```
Slot disponibili: 1h45=1, 2h=1, 2h15=1
→ Assegnato: Slot 1 (1h45) → Pausa 10:45-11:00
```

#### **...e così via...**

#### **Risultato Finale (9 operatori):**

| Orario | Slot | Operatori in pausa |
|--------|------|--------------------|
| 10:45-11:00 | 1h45 | Op1, Op4, Op7 (3 operatori) |
| 11:00-11:15 | 2h   | Op2, Op5, Op8 (3 operatori) |
| 11:15-11:30 | 2h15 | Op3, Op6, Op9 (3 operatori) |

**Bilanciamento: PERFETTO!** ✅
- 3 operatori per slot
- Copertura garantita: massimo 3 operatori in pausa contemporaneamente
- 6 operatori sempre operativi

---

## ⚙️ Configurazione Avanzata

### Modificare Slot e Durate

Se vuoi cambiare slot disponibili, modifica `src/utils/pause_scheduler.py`:

```python
class PauseScheduler:
    # Slot pause disponibili (offset dall'inizio turno)
    SLOT_OFFSETS = [
        timedelta(hours=1, minutes=45),  # Slot 1: dopo 1h45
        timedelta(hours=2, minutes=0),   # Slot 2: dopo 2h
        timedelta(hours=2, minutes=15),  # Slot 3: dopo 2h15
    ]

    PAUSA_DURATA = timedelta(minutes=15)  # Durata pausa: 15 minuti
```

**Esempio: 4 slot da 10 minuti:**
```python
SLOT_OFFSETS = [
    timedelta(hours=1, minutes=30),  # dopo 1h30
    timedelta(hours=1, minutes=50),  # dopo 1h50
    timedelta(hours=2, minutes=10),  # dopo 2h10
    timedelta(hours=2, minutes=30),  # dopo 2h30
]

PAUSA_DURATA = timedelta(minutes=10)
```

---

## 🔍 Algoritmo Dettagliato

### Step 1: Query Database
```sql
SELECT ID_SAP, Ora_Inizio_Turno, Inizio_Pausa_1, ...
FROM Anagrafica_Operatori
WHERE Etichetta_Skill = 'Customer Care'
  AND Data_Riferimento = '2025-01-15'
  AND ID_SAP != 'operatore_corrente'
```

### Step 2: Analisi Occupazione
Per ogni operatore esistente:
- Parse orario inizio pausa
- Calcola offset dall'inizio turno
- Se offset ≈ 1h45 (±5 min) → contatore slot 1++
- Se offset ≈ 2h (±5 min) → contatore slot 2++
- Se offset ≈ 2h15 (±5 min) → contatore slot 3++

### Step 3: Selezione Slot
- Ordina slot per occupazione (crescente)
- Seleziona primo slot (meno affollato)
- Calcola orario: inizio_turno + offset_slot
- Durata: 15 minuti

### Step 4: Assegnazione
- Compila campo `Inizio_Pausa_1`
- Compila campo `Fine_Pausa_1`
- Salva nel database

---

## 💡 Best Practices

### ✅ DO

- ✅ **Usa sempre calcolo automatico** per nuovi operatori
- ✅ **Ricalcola** se cambi turno o skill
- ✅ **Verifica distribuzione** dopo calcolo
- ✅ **Bilancia manualmente** se necessario (muovi operatori tra slot)

### ❌ DON'T

- ❌ **Non assegnare pause manualmente** se hai tanti operatori
- ❌ **Non ignorare avvisi** di sbilanciamento
- ❌ **Non usare stessi orari** per tutti gli operatori

---

## 📈 Monitoraggio

### Dashboard Distribuzione

Crea report distribuzione pause:

```python
from src.utils.pause_scheduler import PauseScheduler
from src.database.db_manager import DatabaseManager

db = DatabaseManager()
scheduler = PauseScheduler(db)

# Analizza distribuzione per skill e data
dist = scheduler.visualizza_distribuzione(
    skill="Customer Care",
    data_riferimento="2025-01-15"
)

print(f"Totale operatori: {dist['totale_operatori']}")
print(f"Slot 1h45: {dist['slot_1h45']} operatori")
print(f"Slot 2h: {dist['slot_2h']} operatori")
print(f"Slot 2h15: {dist['slot_2h15']} operatori")
print(f"Bilanciamento: {dist['bilanciamento']}")
```

**Output:**
```
Totale operatori: 9
Slot 1h45: 3 operatori
Slot 2h: 3 operatori
Slot 2h15: 3 operatori
Bilanciamento: OK
```

---

## ❓ FAQ

### Q: Posso avere più di 1 pausa automatica?
✅ **SÌ!** Usa parametro `num_pause`:
```python
pause = scheduler.calcola_pause_automatiche(
    ...
    num_pause=2  # 2 pause da 15 minuti
)
```
Risultato: 2 pause negli slot meno affollati

---

### Q: Cosa succede se cambio turno dopo aver calcolato pause?
⚠️ Le pause restano quelle vecchie. **Devi ricalcolare!**
1. Click "⚡ Calcola Ora"
2. Conferma sovrascrittura
3. Salva

---

### Q: Posso modificare manualmente pause dopo calcolo automatico?
✅ **SÌ!** Puoi modificare orari manualmente nei campi.
Il calcolo automatico è solo un suggerimento iniziale.

---

### Q: Il calcolo considera turno spezzato?
⚠️ **Parzialmente**. Al momento considera solo turno principale.
Per turno spezzato, calcola pause sul primo blocco.

---

### Q: Funziona con turni notturni (attraversano mezzanotte)?
✅ **SÌ!** Il sistema gestisce turni tipo 22:00-06:00.
```
Turno: 22:00 - 06:00 (8 ore)
Slot 1h45: 23:45 - 00:00
Slot 2h:   00:00 - 00:15
Slot 2h15: 00:15 - 00:30
```

---

## 🎯 Vantaggi

### Prima (Manuale):
- ❌ Rischio sovrapposizioni (tutti in pausa insieme)
- ❌ Copertura non garantita
- ❌ Difficile bilanciare con tanti operatori
- ❌ Tempo: 5 minuti per operatore

### Ora (Automatico):
- ✅ Distribuzione ottimale automatica
- ✅ Copertura sempre garantita
- ✅ Bilanciamento intelligente
- ✅ Tempo: 1 click (2 secondi)

---

## 📞 Supporto

Per problemi o domande:
- Leggi questa guida completa
- Verifica configurazione slot in `pause_scheduler.py`
- Controlla log errori in caso di problemi

---

**Sistema Pause Automatiche - Versione 1.0**
Parte di Matrici - Gestione Turni e Capability Operatori
