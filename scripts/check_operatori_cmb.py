#!/usr/bin/env python3
"""
Script per verificare operatori con skill CMB
"""
import sqlite3
import os
import sys

# Directory corretta
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
os.chdir(project_root)

db_path = 'data/operator_overtime.db'

print(f"Connessione al database: {db_path}")
print(f"Directory corrente: {os.getcwd()}")
print("=" * 100)

if not os.path.exists(db_path):
    print(f"[ERROR] Database non trovato: {db_path}")
    sys.exit(1)

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Controlla operatori con skill CMB
    print("\nOPERATORI CON SKILL CMB (o microskill cmb_*):")
    print("-" * 100)
    cursor.execute("""
        SELECT ID, Nome, Cognome, ID_SAP, Etichetta_Skill, Microskill, Data_Riferimento, Postazione
        FROM Anagrafica_Operatori
        WHERE LOWER(Etichetta_Skill) LIKE '%cmb%'
           OR LOWER(Microskill) LIKE '%cmb%'
        ORDER BY ID_SAP, Data_Riferimento
    """)

    rows = cursor.fetchall()
    if rows:
        print(f"{'ID':<5} {'Nome':<12} {'Cognome':<12} {'ID_SAP':<10} {'Skill':<10} {'Microskill':<15} {'Data':<12} {'Postazione':<15}")
        print("-" * 100)
        for row in rows:
            print(f"{str(row[0]):<5} {str(row[1]):<12} {str(row[2]):<12} {str(row[3]):<10} {str(row[4] or ''):<10} {str(row[5] or ''):<15} {str(row[6]):<12} {str(row[7] or ''):<15}")
    else:
        print("Nessun operatore trovato con skill CMB")

    # Controlla combinazioni duplicate (ID_SAP, Data_Riferimento)
    print("\n\nCONTROLLO DUPLICATI (stesso ID_SAP + Data):")
    print("-" * 100)
    cursor.execute("""
        SELECT ID_SAP, Data_Riferimento, COUNT(*) as count
        FROM Anagrafica_Operatori
        GROUP BY ID_SAP, Data_Riferimento
        HAVING COUNT(*) > 1
    """)

    duplicati = cursor.fetchall()
    if duplicati:
        print(f"{'ID_SAP':<15} {'Data':<15} {'Conteggio':<10}")
        print("-" * 100)
        for dup in duplicati:
            print(f"{str(dup[0]):<15} {str(dup[1]):<15} {str(dup[2]):<10}")

            # Mostra i record duplicati
            cursor.execute("""
                SELECT ID, Nome, Cognome, Etichetta_Skill, Microskill
                FROM Anagrafica_Operatori
                WHERE ID_SAP = ? AND Data_Riferimento = ?
            """, (dup[0], dup[1]))

            detail_rows = cursor.fetchall()
            for detail in detail_rows:
                print(f"  -> ID={detail[0]}: {detail[1]} {detail[2]} | Skill={detail[3]} | Microskill={detail[4]}")
            print()
    else:
        print("Nessun duplicato trovato (OK)")

    # Mostra tutte le combinazioni ID_SAP + Data
    print("\n\nTUTTE LE COMBINAZIONI ID_SAP + DATA nel database:")
    print("-" * 100)
    cursor.execute("""
        SELECT ID_SAP, Data_Riferimento, COUNT(*) as records
        FROM Anagrafica_Operatori
        GROUP BY ID_SAP, Data_Riferimento
        ORDER BY ID_SAP, Data_Riferimento
        LIMIT 20
    """)

    combinations = cursor.fetchall()
    if combinations:
        print(f"{'ID_SAP':<15} {'Data':<15} {'Record':<10}")
        print("-" * 100)
        for comb in combinations:
            print(f"{str(comb[0]):<15} {str(comb[1]):<15} {str(comb[2]):<10}")
        if len(combinations) == 20:
            print("\n(Mostrate prime 20 combinazioni)")
    else:
        print("Nessun dato nel database")

    conn.close()
    print("\n" + "=" * 100)
    print("Controllo completato!")

except sqlite3.Error as e:
    print(f"ERRORE SQLite: {e}")
    sys.exit(1)
except Exception as e:
    print(f"ERRORE: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
