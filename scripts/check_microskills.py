#!/usr/bin/env python3
"""
Script diagnostico per verificare i microskill nel database
"""
import sqlite3
import os
import sys

# Assicurati di essere nella directory corretta
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
os.chdir(project_root)

db_path = 'data/operator_overtime.db'

print(f"Connessione al database: {db_path}")
print(f"Directory corrente: {os.getcwd()}")
print("=" * 80)

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Controlla tabella Skills
    print("\n1. TABELLA Skills - Records con 'cmb' (case-insensitive):")
    print("-" * 80)
    cursor.execute("""
        SELECT ID, Etichetta, Microskill, Descrizione
        FROM Skills
        WHERE LOWER(Etichetta) LIKE '%cmb%'
           OR LOWER(Microskill) LIKE '%cmb%'
        ORDER BY Etichetta, Microskill
    """)
    skills_rows = cursor.fetchall()
    if skills_rows:
        print(f"{'ID':<10} {'Etichetta':<20} {'Microskill':<20} {'Descrizione':<30}")
        for row in skills_rows:
            print(f"{str(row[0]):<10} {str(row[1]):<20} {str(row[2]):<20} {str(row[3]):<30}")
    else:
        print("Nessun record trovato nella tabella Skills")

    # Controlla tabella Anagrafica_Operatori
    print("\n2. TABELLA Anagrafica_Operatori - Records con skill 'cmb' (case-insensitive):")
    print("-" * 80)
    cursor.execute("""
        SELECT ID, Nome, Cognome, ID_SAP, Etichetta_Skill, Microskill, Data_Riferimento, Postazione
        FROM Anagrafica_Operatori
        WHERE LOWER(Etichetta_Skill) LIKE '%cmb%'
           OR LOWER(Microskill) LIKE '%cmb%'
        ORDER BY Etichetta_Skill, Microskill, Data_Riferimento
    """)
    anagrafica_rows = cursor.fetchall()
    if anagrafica_rows:
        print(f"{'ID':<5} {'Nome':<15} {'Cognome':<15} {'ID_SAP':<10} {'Skill':<10} {'Microskill':<15} {'Data':<12} {'Postazione':<20}")
        for row in anagrafica_rows:
            print(f"{str(row[0]):<5} {str(row[1]):<15} {str(row[2]):<15} {str(row[3]):<10} {str(row[4]):<10} {str(row[5]):<15} {str(row[6]):<12} {str(row[7]):<20}")
    else:
        print("Nessun record trovato nella tabella Anagrafica_Operatori")

    # Conta microskill univoci nella tabella Anagrafica
    print("\n3. MICROSKILL UNIVOCI in Anagrafica_Operatori:")
    print("-" * 80)
    cursor.execute("""
        SELECT Etichetta_Skill, Microskill, COUNT(*) as count
        FROM Anagrafica_Operatori
        WHERE Microskill IS NOT NULL AND Microskill != ''
        GROUP BY Etichetta_Skill, Microskill
        ORDER BY Etichetta_Skill, Microskill
    """)
    unique_microskills = cursor.fetchall()
    if unique_microskills:
        print(f"{'Skill':<20} {'Microskill':<20} {'Conteggio':<10}")
        for row in unique_microskills:
            print(f"{str(row[0]):<20} {str(row[1]):<20} {str(row[2]):<10}")
    else:
        print("Nessun microskill trovato")

    # Controlla tutti i microskill disponibili
    print("\n4. TUTTI I MICROSKILL UNIVOCI (da entrambe le tabelle):")
    print("-" * 80)
    cursor.execute("""
        SELECT DISTINCT Microskill
        FROM (
            SELECT Microskill FROM Skills WHERE Microskill IS NOT NULL AND Microskill != ''
            UNION
            SELECT Microskill FROM Anagrafica_Operatori WHERE Microskill IS NOT NULL AND Microskill != ''
        )
        ORDER BY Microskill
    """)
    all_microskills = cursor.fetchall()
    if all_microskills:
        for row in all_microskills:
            print(f"  - {row[0]}")
    else:
        print("Nessun microskill trovato nel database")

    conn.close()
    print("\n" + "=" * 80)
    print("Controllo completato!")

except sqlite3.Error as e:
    print(f"ERRORE SQLite: {e}")
    sys.exit(1)
except Exception as e:
    print(f"ERRORE: {e}")
    sys.exit(1)
