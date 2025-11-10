#!/usr/bin/env python3
"""
Script di migrazione database: aggiunge colonna Microskill alle tabelle Skills e Anagrafica_Operatori
"""

import sqlite3
import sys
import os


def check_column_exists(cursor, table_name, column_name):
    """Verifica se una colonna esiste in una tabella"""
    try:
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = [row[1] for row in cursor.fetchall()]
        return column_name in columns
    except Exception as e:
        print(f"Errore verifica colonna {column_name} in {table_name}: {e}")
        return False


def main():
    print("=" * 60)
    print("MIGRAZIONE DATABASE: Aggiunta colonna Microskill")
    print("=" * 60)
    print()

    # Determina il path del database
    db_path = 'operator_overtime.db'
    if not os.path.exists(db_path):
        db_path = 'data/operator_overtime.db'
        if not os.path.exists(db_path):
            print(f"❌ Database non trovato!")
            print(f"   Cercato in: operator_overtime.db e data/operator_overtime.db")
            sys.exit(1)

    print(f"Database: {db_path}")

    try:
        # Connetti al database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        print("✓ Connessione al database riuscita")
        print()

        # === MIGRAZIONE TABELLA SKILLS ===
        print("1. Verifica tabella Skills...")
        if check_column_exists(cursor, 'Skills', 'Microskill'):
            print("   ⚠️  Colonna 'Microskill' già presente in Skills")
        else:
            print("   → Aggiunta colonna 'Microskill' a Skills...")
            cursor.execute("ALTER TABLE Skills ADD COLUMN Microskill TEXT DEFAULT ''")
            conn.commit()
            print("   ✓ Colonna 'Microskill' aggiunta a Skills")
        print()

        # === MIGRAZIONE TABELLA ANAGRAFICA_OPERATORI ===
        print("2. Verifica tabella Anagrafica_Operatori...")
        if check_column_exists(cursor, 'Anagrafica_Operatori', 'Microskill'):
            print("   ⚠️  Colonna 'Microskill' già presente in Anagrafica_Operatori")
        else:
            print("   → Aggiunta colonna 'Microskill' a Anagrafica_Operatori...")
            cursor.execute("ALTER TABLE Anagrafica_Operatori ADD COLUMN Microskill TEXT DEFAULT ''")
            conn.commit()
            print("   ✓ Colonna 'Microskill' aggiunta a Anagrafica_Operatori")
        print()

        conn.close()

        print("=" * 60)
        print("✅ MIGRAZIONE COMPLETATA CON SUCCESSO!")
        print("=" * 60)
        print()
        print("Le tabelle ora supportano i microskill:")
        print("  • Skills.Microskill - Microskill associato allo skill")
        print("  • Anagrafica_Operatori.Microskill - Microskill dell'operatore")
        print()
        print("Puoi ora importare dati con la colonna Microskill nei template Excel.")
        print()

    except Exception as e:
        print()
        print("=" * 60)
        print("❌ ERRORE DURANTE LA MIGRAZIONE")
        print("=" * 60)
        print(f"Errore: {e}")
        print()
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
