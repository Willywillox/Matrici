#!/usr/bin/env python3
"""
Migrazione: Rimuove vincolo UNIQUE da Codice_Skill e aggiunge UNIQUE su (Codice_Skill, Microskill)

Questo permette di avere più microskill per la stessa skill.
"""
import sqlite3
import os
import sys

# Assicurati di essere nella directory corretta
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
os.chdir(project_root)

db_path = 'data/operator_overtime.db'

print(f"{'='*80}")
print("MIGRAZIONE: Skills - Supporto microskill multipli per skill")
print(f"{'='*80}\n")

if not os.path.exists(db_path):
    print(f"[ERROR] Database non trovato: {db_path}")
    print("Questo script funziona solo con SQLite")
    sys.exit(1)

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    print("[INFO] Inizio migrazione...")

    # 1. Crea nuova tabella Skills con la struttura corretta
    print("[1/6] Creazione nuova tabella Skills_New...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Skills_New (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            Codice_Skill TEXT(50) NOT NULL,
            Descrizione TEXT(255),
            Produttivita_Default REAL DEFAULT 1.0,
            Microskill TEXT(100),
            UNIQUE(Codice_Skill, Microskill)
        )
    """)

    # 2. Verifica se la colonna Microskill esiste nella tabella vecchia
    print("[2/6] Verifica struttura tabella Skills esistente...")
    cursor.execute("PRAGMA table_info(Skills)")
    columns = [col[1] for col in cursor.fetchall()]
    has_microskill = 'Microskill' in columns

    print(f"       Colonne esistenti: {', '.join(columns)}")
    print(f"       Ha colonna Microskill: {has_microskill}")

    # 3. Copia dati dalla tabella vecchia
    print("[3/6] Copia dati dalla tabella Skills...")
    if has_microskill:
        cursor.execute("""
            INSERT INTO Skills_New (ID, Codice_Skill, Descrizione, Produttivita_Default, Microskill)
            SELECT ID, Codice_Skill, Descrizione, Produttivita_Default, Microskill
            FROM Skills
        """)
    else:
        cursor.execute("""
            INSERT INTO Skills_New (ID, Codice_Skill, Descrizione, Produttivita_Default)
            SELECT ID, Codice_Skill, Descrizione, Produttivita_Default
            FROM Skills
        """)

    rows_copied = cursor.rowcount
    print(f"       Copiate {rows_copied} righe")

    # 4. Elimina tabella vecchia
    print("[4/6] Eliminazione tabella Skills...")
    cursor.execute("DROP TABLE Skills")

    # 5. Rinomina nuova tabella
    print("[5/6] Rinomina Skills_New -> Skills...")
    cursor.execute("ALTER TABLE Skills_New RENAME TO Skills")

    # 6. Commit
    print("[6/6] Commit delle modifiche...")
    conn.commit()

    print("\n" + "="*80)
    print("[SUCCESS] Migrazione completata con successo!")
    print("="*80)
    print("\nOra puoi:")
    print("1. Importare skills con microskill multipli usando lo stesso Codice_Skill")
    print("2. Esempio nel template:")
    print("   Riga 1: CMB, cmb_pa")
    print("   Riga 2: CMB, cmb_ba")
    print("   Entrambe saranno importate correttamente!")
    print()

except sqlite3.Error as e:
    print(f"\n[ERROR] Errore SQLite: {e}")
    conn.rollback()
    sys.exit(1)
except Exception as e:
    print(f"\n[ERROR] Errore: {e}")
    import traceback
    traceback.print_exc()
    conn.rollback()
    sys.exit(1)
finally:
    conn.close()
