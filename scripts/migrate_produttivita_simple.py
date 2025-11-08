"""
Script di migrazione semplificato per aggiungere Produttivita a Erlang_Config
Usa sqlite3 direttamente senza dipendenze
"""

import sqlite3
import os

def migrate_database():
    """Aggiunge la colonna Produttivita alla tabella Erlang_Config"""

    # Prova prima il percorso di default
    db_path = 'data/operator_overtime.db'

    # Se non esiste, cerca altri database SQLite
    if not os.path.exists(db_path):
        if os.path.exists('data'):
            for file in os.listdir('data'):
                if file.endswith('.db'):
                    db_path = os.path.join('data', file)
                    break
        else:
            db_path = None

    if not db_path or not os.path.exists(db_path):
        print("[ERROR] Nessun database SQLite trovato")
        print(f"[INFO] Cercato in: data/operator_overtime.db")
        print("[INFO] Se usi MS Access, devi configurare i driver ODBC")
        return False

    print("\n" + "="*70)
    print(f"  MIGRAZIONE DATABASE: {db_path}")
    print("="*70 + "\n")

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Verifica se colonna esiste già
        cursor.execute("PRAGMA table_info(Erlang_Config)")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]

        if 'Produttivita' in column_names:
            print("[SKIP] Colonna 'Produttivita' già esistente, nessuna migrazione necessaria")
            conn.close()
            return True

        print("[INFO] Aggiunta colonna Produttivita...")
        cursor.execute("ALTER TABLE Erlang_Config ADD COLUMN Produttivita REAL DEFAULT 1.0")
        conn.commit()

        print("[OK] Colonna 'Produttivita' aggiunta con successo!\n")

        # Verifica
        cursor.execute("PRAGMA table_info(Erlang_Config)")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]

        if 'Produttivita' in column_names:
            print("[OK] Verifica: Colonna aggiunta correttamente\n")
            print("="*70)
            print("  MIGRAZIONE COMPLETATA CON SUCCESSO")
            print("="*70 + "\n")
            conn.close()
            return True
        else:
            print("[ERROR] Verifica fallita")
            conn.close()
            return False

    except Exception as e:
        print(f"[ERROR] Errore durante la migrazione: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    print("\nQuesta migrazione aggiungerà la colonna 'Produttivita' alla tabella Erlang_Config.")
    print("Questa colonna permette di definire la produttività target per ogni skill.\n")

    risposta = input("Vuoi procedere con la migrazione? (s/n): ").strip().lower()

    if risposta != 's':
        print("\n[ANNULLATO] Migrazione annullata dall'utente")
        exit(1)

    success = migrate_database()

    if success:
        print("\n✓ Migrazione completata! Puoi ora configurare la produttività per ogni skill.")
        exit(0)
    else:
        print("\n✗ Migrazione fallita. Controlla gli errori sopra.")
        exit(1)
