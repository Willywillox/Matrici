#!/usr/bin/env python3
"""
Verifica se ci sono record duplicati per lo stesso operatore nella stessa data
"""
import sqlite3

db_path = 'data/operator_overtime.db'

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("=" * 80)
print("CONTROLLO RECORD DUPLICATI")
print("=" * 80)
print()

# Cerca duplicati per ID_SAP + Data_Riferimento
cursor.execute("""
    SELECT ID_SAP, Data_Riferimento, COUNT(*) as count
    FROM Anagrafica_Operatori
    WHERE Data_Riferimento BETWEEN '2024-11-10' AND '2024-11-16'
    GROUP BY ID_SAP, Data_Riferimento
    HAVING COUNT(*) > 1
    ORDER BY count DESC, ID_SAP, Data_Riferimento
""")

duplicati = cursor.fetchall()

if duplicati:
    print(f"⚠️  TROVATI {len(duplicati)} RECORD DUPLICATI!")
    print()
    print("ID_SAP     Data            Copie")
    print("-" * 40)

    total_extra = 0
    for id_sap, data, count in duplicati:
        print(f"{id_sap:10s} {data:15s} {count:3d}")
        total_extra += (count - 1)

    print()
    print(f"Record extra totali: {total_extra}")
    print()
    print("PROBLEMA: Ogni record duplicato viene contato più volte nel calcolo ore!")
    print(f"Se ogni giorno è duplicato, le ore vengono moltiplicate per {duplicati[0][2]} volte.")
    print()
    print("SOLUZIONE:")
    print("1. Cancella i duplicati dal database")
    print("2. Oppure modifica il codice per fare DISTINCT su ID_SAP + Data_Riferimento")

else:
    print("✓ Nessun record duplicato trovato")
    print()
    print("I duplicati NON sono il problema.")
    print("Controlla:")
    print("  1. La durata effettiva dei turni giornalieri")
    print("  2. Se ci sono straordinari non previsti")
    print("  3. Esegui: python diagnose_ore_calcolo.py")

print()

# Mostra statistiche generali
print("-" * 80)
print("STATISTICHE GENERALI:")
print()

cursor.execute("""
    SELECT ID_SAP, COUNT(*) as giorni,
           COUNT(DISTINCT Data_Riferimento) as giorni_unici
    FROM Anagrafica_Operatori
    WHERE Data_Riferimento BETWEEN '2024-11-10' AND '2024-11-16'
    GROUP BY ID_SAP
    ORDER BY ID_SAP
""")

stats = cursor.fetchall()

print("ID_SAP     Record  Giorni Unici  Note")
print("-" * 60)

for id_sap, record_count, giorni_unici in stats:
    note = ""
    if record_count != giorni_unici:
        note = f"⚠️  DUPLICATI! ({record_count - giorni_unici} extra)"

    print(f"{id_sap:10s} {record_count:6d}  {giorni_unici:12d}  {note}")

conn.close()
