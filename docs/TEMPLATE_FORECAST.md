# Template Forecast Excel

## Formato File

Il file Excel per l'import del forecast deve contenere le seguenti colonne:

| Data_Riferimento | Fascia_Oraria | Skill | Volumi_Attesi | Produttivita_Target | FTE_Richiesti |
|------------------|---------------|-------|---------------|---------------------|---------------|
| 2024-01-15 | 09:00 | CUSTOMER_CARE | 100 | 8.0 | 12.50 |
| 2024-01-15 | 09:15 | CUSTOMER_CARE | 100 | 8.0 | 12.50 |
| 2024-01-15 | 09:30 | CUSTOMER_CARE | 120 | 8.0 | 15.00 |
| 2024-01-15 | 09:00 | BACK_OFFICE | 60 | 12.0 | 5.00 |
| 2024-01-15 | 09:15 | BACK_OFFICE | 60 | 12.0 | 5.00 |

## Descrizione Colonne

### Data_Riferimento
- **Formato**: YYYY-MM-DD (es. 2024-01-15)
- **Descrizione**: Data di riferimento del forecast

### Fascia_Oraria
- **Formato**: HH:MM (es. 09:00, 09:15, 09:30)
- **Descrizione**: Orario di inizio della fascia
- **Note**: Deve essere allineato all'intervallo scelto (15 o 30 minuti)

### Skill
- **Formato**: Testo (es. CUSTOMER_CARE, BACK_OFFICE, TECHNICAL_SUPPORT)
- **Descrizione**: Codice skill/servizio
- **Note**: Deve corrispondere alle skill in anagrafica

### Volumi_Attesi
- **Formato**: Numero intero (es. 100, 150, 200)
- **Descrizione**: Numero di pratiche/chiamate/ticket attese nella fascia
- **Note**: Può essere lasciato a 0 se non si hanno volumi

### Produttivita_Target
- **Formato**: Numero decimale (es. 8.0, 12.5)
- **Descrizione**: Numero di pratiche gestite per operatore all'ora
- **Note**: Usare punto come separatore decimale (non virgola)

### FTE_Richiesti
- **Formato**: Numero decimale (es. 12.50, 5.00)
- **Descrizione**: Full Time Equivalent richiesti
- **Calcolo**: Volumi_Attesi ÷ Produttivita_Target ÷ (60 ÷ Minuti_Fascia)
  - Per fascia 15 min: Volumi ÷ Produttivita ÷ 4
  - Per fascia 30 min: Volumi ÷ Produttivita ÷ 2

## Esempio Completo

### Scenario: Contact Center - Fascia 15 minuti

**Dati:**
- Skill: CUSTOMER_CARE
- Produttività: 8 pratiche/ora
- Volumi attesi 09:00-10:00: 400 pratiche totali (100 per ogni fascia da 15 min)

**Calcolo:**
- Volumi per fascia 15 min: 100
- FTE richiesti: 100 ÷ 8 ÷ 4 = 3.125

**File Excel:**

```
Data_Riferimento,Fascia_Oraria,Skill,Volumi_Attesi,Produttivita_Target,FTE_Richiesti
2024-01-15,09:00,CUSTOMER_CARE,100,8.0,3.125
2024-01-15,09:15,CUSTOMER_CARE,100,8.0,3.125
2024-01-15,09:30,CUSTOMER_CARE,100,8.0,3.125
2024-01-15,09:45,CUSTOMER_CARE,100,8.0,3.125
```

### Scenario: Multi-Skill - Fascia 30 minuti

**File Excel:**

```
Data_Riferimento,Fascia_Oraria,Skill,Volumi_Attesi,Produttivita_Target,FTE_Richiesti
2024-01-15,09:00,CUSTOMER_CARE,200,8.0,12.50
2024-01-15,09:30,CUSTOMER_CARE,200,8.0,12.50
2024-01-15,09:00,BACK_OFFICE,120,12.0,5.00
2024-01-15,09:30,BACK_OFFICE,120,12.0,5.00
2024-01-15,09:00,TECHNICAL_SUPPORT,60,6.0,5.00
2024-01-15,09:30,TECHNICAL_SUPPORT,60,6.0,5.00
```

## Script Python per Generare Forecast

Se hai un forecast giornaliero e vuoi espanderlo su fasce 15/30 min:

```python
import pandas as pd
from datetime import datetime, time, timedelta

def genera_forecast_intraday(data, skill, volumi_totali, produttivita,
                              ora_inizio, ora_fine, intervallo_min=15):
    """
    Genera forecast intraday da volumi totali giornalieri

    Args:
        data: Data (YYYY-MM-DD)
        skill: Codice skill
        volumi_totali: Volumi totali nel periodo
        produttivita: Pratiche/ora
        ora_inizio: Ora inizio (es. "09:00")
        ora_fine: Ora fine (es. "18:00")
        intervallo_min: 15 o 30
    """

    # Calcola numero fasce
    t_inizio = datetime.strptime(f"{data} {ora_inizio}", "%Y-%m-%d %H:%M")
    t_fine = datetime.strptime(f"{data} {ora_fine}", "%Y-%m-%d %H:%M")
    minuti_totali = (t_fine - t_inizio).total_seconds() / 60
    num_fasce = int(minuti_totali / intervallo_min)

    # Distribuisci volumi uniformemente
    volumi_per_fascia = volumi_totali / num_fasce

    # Calcola FTE
    fasce_per_ora = 60 / intervallo_min
    fte_per_fascia = volumi_per_fascia / produttivita / fasce_per_ora

    # Genera righe
    forecast = []
    current = t_inizio

    for _ in range(num_fasce):
        forecast.append({
            'Data_Riferimento': data,
            'Fascia_Oraria': current.strftime('%H:%M'),
            'Skill': skill,
            'Volumi_Attesi': int(volumi_per_fascia),
            'Produttivita_Target': produttivita,
            'FTE_Richiesti': round(fte_per_fascia, 2)
        })
        current += timedelta(minutes=intervallo_min)

    return pd.DataFrame(forecast)

# Esempio uso
df = genera_forecast_intraday(
    data='2024-01-15',
    skill='CUSTOMER_CARE',
    volumi_totali=3600,  # 3600 pratiche dalle 9 alle 18
    produttivita=8.0,
    ora_inizio='09:00',
    ora_fine='18:00',
    intervallo_min=15
)

# Salva
df.to_excel('forecast_2024-01-15.xlsx', index=False)
print(f"Forecast generato: {len(df)} fasce")
```

## Note Importanti

1. **Encoding**: Salva il file Excel in formato UTF-8
2. **Separatori**: Usa punto (.) per decimali, non virgola (,)
3. **Date**: Formato ISO (YYYY-MM-DD)
4. **Orari**: Formato 24h (HH:MM)
5. **Skill**: Case-sensitive, deve corrispondere esattamente all'anagrafica
6. **Completezza**: Inserisci forecast per tutte le fasce e tutte le skill
7. **Coerenza**: Intervallo fasce deve essere 15 o 30 min

## Troubleshooting Import

**Errore: "Data formato errato"**
- Verifica formato YYYY-MM-DD (non DD/MM/YYYY)

**Errore: "Skill non trovata"**
- Verifica skill esista in anagrafica Skills
- Controlla maiuscole/minuscole

**Errore: "Fascia oraria non valida"**
- Verifica formato HH:MM (non HH:MM:SS)
- Verifica allineamento a 15 o 30 min

**Import parziale**
- Verifica non ci siano righe duplicate
- Controlla non ci siano celle vuote

---

**Tip**: Tieni un template Excel master e duplicalo per nuove date!
