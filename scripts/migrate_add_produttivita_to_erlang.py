"""
Script di migrazione per aggiungere la colonna Produttivita alla tabella Erlang_Config
"""

import sys
import os

# Aggiungi path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from database.db_manager import DatabaseManager


def migrate_database():
    """Aggiunge la colonna Produttivita alla tabella Erlang_Config"""

    print("\n" + "="*70)
    print("  MIGRAZIONE DATABASE: Aggiunta colonna Produttivita a Erlang_Config")
    print("="*70 + "\n")

    db_manager = DatabaseManager()

    try:
        db_manager.connect()
        print("[OK] Connesso al database\n")

        # Verifica se colonna esiste già
        if db_manager.is_sqlite:
            check_query = "PRAGMA table_info(Erlang_Config)"
            columns = db_manager.execute_query(check_query)
            column_names = [col[1] for col in columns] if columns else []

            if 'Produttivita' in column_names:
                print("[SKIP] Colonna 'Produttivita' già esistente, nessuna migrazione necessaria")
                return True

            print("[INFO] Aggiunta colonna Produttivita...")
            alter_query = "ALTER TABLE Erlang_Config ADD COLUMN Produttivita REAL DEFAULT 1.0"

        else:
            # MS Access
            # Verifica se colonna esiste
            try:
                test_query = "SELECT TOP 1 Produttivita FROM Erlang_Config"
                db_manager.execute_query(test_query)
                print("[SKIP] Colonna 'Produttivita' già esistente, nessuna migrazione necessaria")
                return True
            except:
                # Colonna non esiste, procedi
                print("[INFO] Aggiunta colonna Produttivita...")
                alter_query = "ALTER TABLE Erlang_Config ADD COLUMN Produttivita DOUBLE DEFAULT 1.0"

        db_manager.execute_update(alter_query)
        print("[OK] Colonna 'Produttivita' aggiunta con successo!\n")

        # Verifica aggiunta
        if db_manager.is_sqlite:
            verify = db_manager.execute_query("PRAGMA table_info(Erlang_Config)")
            column_names = [col[1] for col in verify] if verify else []
            if 'Produttivita' in column_names:
                print("[OK] Verifica: Colonna aggiunta correttamente\n")
                print("="*70)
                print("  MIGRAZIONE COMPLETATA CON SUCCESSO")
                print("="*70 + "\n")
                return True
        else:
            # Per Access, prova query
            try:
                db_manager.execute_query("SELECT TOP 1 Produttivita FROM Erlang_Config")
                print("[OK] Verifica: Colonna aggiunta correttamente\n")
                print("="*70)
                print("  MIGRAZIONE COMPLETATA CON SUCCESSO")
                print("="*70 + "\n")
                return True
            except:
                print("[ERROR] Verifica fallita")
                return False

    except Exception as e:
        print(f"[ERROR] Errore durante la migrazione: {e}")
        import traceback
        traceback.print_exc()
        return False

    finally:
        db_manager.close()


if __name__ == '__main__':
    print("\nQuesta migrazione aggiungerà la colonna 'Produttivita' alla tabella Erlang_Config.")
    print("Questa colonna permette di definire la produttività target per ogni skill.\n")

    risposta = input("Vuoi procedere con la migrazione? (s/n): ").strip().lower()

    if risposta != 's':
        print("\n[ANNULLATO] Migrazione annullata dall'utente")
        sys.exit(1)

    success = migrate_database()

    if success:
        print("\n✓ Migrazione completata! Puoi ora configurare la produttività per ogni skill.")
        sys.exit(0)
    else:
        print("\n✗ Migrazione fallita. Controlla gli errori sopra.")
        sys.exit(1)
