#!/usr/bin/env python3
"""
Verifica dettagliata calcolo ore per Inserra
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
print("VERIFICA CALCOLO ORE PER INSERRA MARIA RITA")
print("=" * 80)
print()

# Trova Inserra
cursor.execute("""
    SELECT ID_SAP FROM Anagrafica_Operatori
    WHERE Cognome LIKE '%Inserra%'
    LIMIT 1
""")

row = cursor.fetchone()
if not row:
    print("Operatrice Inserra non trovata!")
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
                # Se è un'assenza (ferie, malattia, ecc), conta come ore_giustificativo
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

    print(f"  Ore calcolate:")
    print(f"    Produzione: {ore_prod:.2f}h")
    print(f"    Pausa: {ore_pausa:.2f}h")
    print(f"    Assenze (Ferie/Malattia/ecc): {ore_assenza:.2f}h")
    print(f"    Altri giustificativi: {ore_giust:.2f}h")

    # Verifica coerenza
    turno_inizio_str = str(op.ora_inizio_turno) if op.ora_inizio_turno else None
    turno_fine_str = str(op.ora_fine_turno) if op.ora_fine_turno else None

    if turno_inizio_str == '00:00:00' and turno_fine_str == '00:00:00':
        tipo_giorno = "RIPOSO"
        if ore_prod > 0 or ore_pausa > 0:
            print(f"  ❌ ERRORE: Riposo conta ore di produzione/pausa!")
    else:
        tipo_giorno = "LAVORO"
        if ore_assenza > 0:
            print(f"  ✓ Giornata con assenza correttamente rilevata")

    print(f"  Tipo giorno: {tipo_giorno}")
    print()

print("=" * 80)
print("TEST CALCOLO CON CapabilityCalculator")
print("=" * 80)
print()

# Test con CapabilityCalculator
data_inizio = datetime.strptime(giorni[0]['Data_Riferimento'], '%Y-%m-%d')
data_fine = datetime.strptime(giorni[-1]['Data_Riferimento'], '%Y-%m-%d')

calculator = CapabilityCalculator(all_operatori)

print("Calcolo report PER PERSONA...")
df = calculator.calcola_rendiconto_per_persona(data_inizio, data_fine)

if df is not None and not df.empty:
    # Filtra solo Inserra
    df_inserra = df[df['ID_SAP'] == id_sap]

    print(f"Righe per Inserra: {len(df_inserra)}")
    print()

    if not df_inserra.empty:
        print("Dettaglio giornaliero:")
        print()

        colonne_da_mostrare = ['Data', 'Ore_Produzione', 'Ore_Pausa', 'Ore_Straordinario']

        # Aggiungi colonne giustificativi se esistono
        for col in df_inserra.columns:
            if col.startswith('Ore_') and col not in colonne_da_mostrare:
                colonne_da_mostrare.append(col)

        colonne_esistenti = [col for col in colonne_da_mostrare if col in df_inserra.columns]

        print(df_inserra[colonne_esistenti].to_string(index=False))

        print()
        print("TOTALE SETTIMANA:")
        for col in colonne_esistenti:
            if col != 'Data':
                totale = df_inserra[col].sum()
                print(f"  {col}: {totale:.2f}h")
    else:
        print("Nessun record trovato per Inserra nel report!")
else:
    print("Report vuoto o None!")

conn.close()
