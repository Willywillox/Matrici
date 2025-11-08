"""
Script di migrazione per aggiungere la tabella Giustificativi al database esistente
"""

import sys
import os

# Aggiungi path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from database.db_manager import DatabaseManager


def migrate_database():
    """Aggiunge la tabella Giustificativi al database esistente"""

    print("\n" + "="*70)
    print("  MIGRAZIONE DATABASE: Aggiunta tabella Giustificativi")
    print("="*70 + "\n")

    db_manager = DatabaseManager()

    try:
        db_manager.connect()
        print("[OK] Connesso al database\n")

        # Verifica se tabella esiste già
        if db_manager.is_sqlite:
            check_query = """
                SELECT name FROM sqlite_master
                WHERE type='table' AND name='Giustificativi'
            """
        else:
            check_query = """
                SELECT COUNT(*) FROM MSysObjects
                WHERE Name='Giustificativi' AND Type=1
            """

        result = db_manager.execute_query(check_query)

        if result and len(result) > 0:
            if db_manager.is_sqlite:
                if result[0][0] == 'Giustificativi':
                    print("[SKIP] Tabella 'Giustificativi' già esistente, nessuna migrazione necessaria")
                    return True
            else:
                if result[0][0] > 0:
                    print("[SKIP] Tabella 'Giustificativi' già esistente, nessuna migrazione necessaria")
                    return True

        print("[INFO] Creazione tabella Giustificativi...")

        if db_manager.is_sqlite:
            # SQLite
            create_query = """
                CREATE TABLE IF NOT EXISTS Giustificativi (
                    ID INTEGER PRIMARY KEY AUTOINCREMENT,
                    Codice_Giustificativo TEXT UNIQUE NOT NULL,
                    Descrizione TEXT,
                    Tipologia TEXT,
                    Note TEXT
                )
            """
        else:
            # MS Access
            create_query = """
                CREATE TABLE Giustificativi (
                    ID AUTOINCREMENT PRIMARY KEY,
                    Codice_Giustificativo TEXT(50) UNIQUE NOT NULL,
                    Descrizione TEXT(255),
                    Tipologia TEXT(100),
                    Note TEXT(255)
                )
            """

        db_manager.execute_update(create_query)
        print("[OK] Tabella 'Giustificativi' creata con successo!\n")

        # Verifica creazione
        if db_manager.is_sqlite:
            verify_query = "SELECT name FROM sqlite_master WHERE type='table' AND name='Giustificativi'"
        else:
            verify_query = "SELECT COUNT(*) FROM MSysObjects WHERE Name='Giustificativi' AND Type=1"

        verify_result = db_manager.execute_query(verify_query)

        if verify_result and len(verify_result) > 0:
            print("[OK] Verifica: Tabella creata correttamente\n")
            print("="*70)
            print("  MIGRAZIONE COMPLETATA CON SUCCESSO")
            print("="*70 + "\n")
            return True
        else:
            print("[ERROR] Verifica fallita: Tabella non trovata dopo creazione")
            return False

    except Exception as e:
        print(f"[ERROR] Errore durante la migrazione: {e}")
        import traceback
        traceback.print_exc()
        return False

    finally:
        db_manager.close()


if __name__ == '__main__':
    print("\nQuesta migrazione aggiungerà la tabella 'Giustificativi' al database.")
    print("La tabella conterrà l'anagrafica dei giustificativi con le relative tipologie.\n")

    risposta = input("Vuoi procedere con la migrazione? (s/n): ").strip().lower()

    if risposta != 's':
        print("\n[ANNULLATO] Migrazione annullata dall'utente")
        sys.exit(1)

    success = migrate_database()

    if success:
        print("\n✓ Migrazione completata! Puoi ora importare i giustificativi.")
        sys.exit(0)
    else:
        print("\n✗ Migrazione fallita. Controlla gli errori sopra.")
        sys.exit(1)
