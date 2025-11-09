#!/usr/bin/env python3
"""
Test calcolo ore per Bianchi Laura (test data)
"""
import sys
import sqlite3
from datetime import datetime, timedelta, time

sys.path.insert(0, 'src')

from models.operatore import Operatore
from utils.capability_calculator import CapabilityCalculator

db_path = 'data/operator_overtime.db'

conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

print("=" * 80)
print("TEST CALCOLO ORE PER BIANCHI LAURA")
print("=" * 80)
print()

# Trova Bianchi
cursor.execute("""
    SELECT ID_SAP FROM Anagrafica_Operatori
    WHERE Cognome = 'Bianchi'
    LIMIT 1
""")

row = cursor.fetchone()
if not row:
    print("Operatrice Bianchi non trovata!")
    conn.close()
    exit(1)

id_sap = row['ID_SAP']

print(f"ID SAP: {id_sap}")
print()

def _row_to_dict(row):
    if hasattr(row, 'keys'):
        return {key: row[key] for key in row.keys()}
    return {}

# Carica tutti i giorni
cursor.execute("""
    SELECT * FROM Anagrafica_Operatori
    WHERE ID_SAP = ?
    ORDER BY Data_Riferimento
""", (id_sap,))

giorni = cursor.fetchall()

print(f"Giorni trovati: {len(giorni)}")
print()

all_operatori = []

for giorno in giorni:
    data = giorno['Data_Riferimento']

    # Crea operatore
    op_dict = _row_to_dict(giorno)
    op = Operatore(**op_dict)
    all_operatori.append(op)

    # Info base
    print(f"Data: {data}")
    print(f"  Turno: {op.ora_inizio_turno} - {op.ora_fine_turno}")
    print(f"  Giustificativi: {len(op.giustificativi)}")

    if op.giustificativi:
        for g in op.giustificativi:
            print(f"    - {g['tipo']}: {g['inizio']} - {g['fine']}")

    # Calcola ore manualmente slot per slot
    ore_prod = 0
    ore_pausa = 0
    ore_giust = 0
    ore_assenza = 0

    for h in range(24):
        for m in [0, 15, 30, 45]:
            t = time(h, m)

            # Prima controlla giustificativo
            giust = op.get_giustificativo_at_time(t)

            if giust:
                # Ha un giustificativo a quest'ora
                if giust.lower() in ['ferie', 'malattia', 'permesso', 'rol', 'assenza']:
                    ore_assenza += 0.25
                else:
                    ore_giust += 0.25
            elif op.is_presente(t):
                # Presente al lavoro
                if op.is_in_pausa(t):
                    ore_pausa += 0.25
                else:
                    ore_prod += 0.25

    print(f"  Ore calcolate manualmente:")
    print(f"    Produzione: {ore_prod:.2f}h")
    print(f"    Pausa: {ore_pausa:.2f}h")
    print(f"    Assenze (Ferie/Malattia/ecc): {ore_assenza:.2f}h")
    print(f"    Altri giustificativi: {ore_giust:.2f}h")

    # Verifica coerenza
    turno_inizio_str = str(op.ora_inizio_turno) if op.ora_inizio_turno else None
    turno_fine_str = str(op.ora_fine_turno) if op.ora_fine_turno else None

    if turno_inizio_str == '00:00:00' and turno_fine_str == '00:00:00':
        tipo_giorno = "RIPOSO" if not giust else f"ASSENZA ({giust})"
        if ore_prod > 0 or ore_pausa > 0:
            print(f"  ❌ ERRORE: Riposo conta {ore_prod:.2f}h produzione + {ore_pausa:.2f}h pausa!")
        else:
            print(f"  ✓ OK: Riposo non conta ore di lavoro")
    else:
        tipo_giorno = "LAVORO"

    print(f"  Tipo giorno: {tipo_giorno}")
    print()

print("=" * 80)
print("TEST CALCOLO CON CapabilityCalculator")
print("=" * 80)
print()

# Test con CapabilityCalculator
data_inizio = datetime.strptime(giorni[0]['Data_Riferimento'], '%Y-%m-%d')
data_fine = datetime.strptime(giorni[-1]['Data_Riferimento'], '%Y-%m-%d')

# Carica giustificativi dalla tabella
cursor.execute("SELECT Codice_Giustificativo, Tipologia FROM Giustificativi")
giust_rows = cursor.fetchall()

giustificativi_map = {}
tipologie_giustificativi = set()

for row in giust_rows:
    codice = row['Codice_Giustificativo']
    tipologia = row['Tipologia']
    giustificativi_map[codice] = tipologia
    tipologie_giustificativi.add(tipologia)

tipologie_giustificativi = sorted(list(tipologie_giustificativi))

print(f"Giustificativi caricati: {len(giustificativi_map)}")
print(f"Tipologie: {tipologie_giustificativi}")
print()

calculator = CapabilityCalculator(all_operatori)
# Imposta manualmente i giustificativi
calculator.giustificativi_map = giustificativi_map
calculator.tipologie_giustificativi = tipologie_giustificativi

print("Calcolo report PER PERSONA...")
df = calculator.calcola_rendiconto_per_persona(data_inizio, data_fine)

if df is not None and not df.empty:
    # Filtra solo Bianchi
    df_bianchi = df[df['ID_SAP'] == id_sap]

    print(f"Righe per Bianchi: {len(df_bianchi)}")
    print()

    if not df_bianchi.empty:
        print("Dettaglio giornaliero:")
        print()

        colonne_da_mostrare = ['Data', 'Ore_Produzione', 'Ore_Pausa', 'Ore_Straordinario']

        # Aggiungi colonne giustificativi se esistono
        for col in df_bianchi.columns:
            if col.startswith('Ore_') and col not in colonne_da_mostrare:
                colonne_da_mostrare.append(col)

        colonne_esistenti = [col for col in colonne_da_mostrare if col in df_bianchi.columns]

        print(df_bianchi[colonne_esistenti].to_string(index=False))

        print()
        print("TOTALE SETTIMANA:")
        for col in colonne_esistenti:
            if col != 'Data':
                totale = df_bianchi[col].sum()
                print(f"  {col}: {totale:.2f}h")
    else:
        print("Nessun record trovato per Bianchi nel report!")
else:
    print("Report vuoto o None!")

conn.close()
