"""
Script di migrazione per aggiungere tabella Erlang_Config ai database esistenti

Aggiunge la tabella Erlang_Config se non esiste già.
"""

import sys
import os
from pathlib import Path

# Aggiungi path per import moduli
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.database.db_manager import DatabaseManager


def migrate_database(db_path='data/operator_overtime.db'):
    """
    Aggiunge tabella Erlang_Config al database esistente

    Args:
        db_path: Path al database
    """

    print(f"\n{'='*70}")
    print(f"  MIGRAZIONE DATABASE: AGGIUNTA TABELLA ERLANG_CONFIG")
    print(f"{'='*70}\n")
    print(f"Database: {db_path}\n")

    if not Path(db_path).exists():
        print(f"❌ Database non trovato: {db_path}")
        print("Creare prima il database usando l'applicazione o db_creator.py")
        return False

    db_manager = DatabaseManager(db_path)

    try:
        db_manager.connect()

        # Verifica se tabella esiste già
        if db_path.endswith('.db'):  # SQLite
            cursor = db_manager.execute_query("""
                SELECT name FROM sqlite_master
                WHERE type='table' AND name='Erlang_Config'
            """)
            table_exists = cursor and len(cursor) > 0
        else:  # Access
            try:
                cursor = db_manager.execute_query("SELECT TOP 1 * FROM Erlang_Config")
                table_exists = True
            except:
                table_exists = False

        if table_exists:
            print("✓ Tabella Erlang_Config già esistente")
            print("Nessuna migrazione necessaria\n")

            # Mostra count
            cursor = db_manager.execute_query("SELECT COUNT(*) FROM Erlang_Config")
            count = cursor[0][0] if cursor else 0
            print(f"Configurazioni presenti: {count}\n")

            db_manager.close()
            return True

        print("📋 Creazione tabella Erlang_Config...")

        # Crea tabella
        if db_path.endswith('.db'):  # SQLite
            db_manager.execute_update("""
                CREATE TABLE IF NOT EXISTS Erlang_Config (
                    ID INTEGER PRIMARY KEY AUTOINCREMENT,
                    Skill TEXT UNIQUE NOT NULL,
                    Tipo_Canale TEXT DEFAULT 'Voice',
                    AHT_Seconds INTEGER DEFAULT 180,
                    Concurrency INTEGER DEFAULT 1,
                    Tempo_Pausa_Minuti INTEGER DEFAULT 0,
                    Shrinkage REAL DEFAULT 0.30,
                    Service_Level_Target REAL DEFAULT 0.80,
                    Service_Level_Seconds INTEGER DEFAULT 20,
                    ASA_Target_Seconds INTEGER DEFAULT 60,
                    Occupancy_Target REAL DEFAULT 0.85,
                    Interval_Minutes INTEGER DEFAULT 30,
                    Note TEXT,
                    Data_Aggiornamento TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
        else:  # Access
            db_manager.execute_update("""
                CREATE TABLE Erlang_Config (
                    ID AUTOINCREMENT PRIMARY KEY,
                    Skill TEXT(100) UNIQUE NOT NULL,
                    Tipo_Canale TEXT(20) DEFAULT 'Voice',
                    AHT_Seconds INTEGER DEFAULT 180,
                    Concurrency INTEGER DEFAULT 1,
                    Tempo_Pausa_Minuti INTEGER DEFAULT 0,
                    Shrinkage DOUBLE DEFAULT 0.30,
                    Service_Level_Target DOUBLE DEFAULT 0.80,
                    Service_Level_Seconds INTEGER DEFAULT 20,
                    ASA_Target_Seconds INTEGER DEFAULT 60,
                    Occupancy_Target DOUBLE DEFAULT 0.85,
                    Interval_Minutes INTEGER DEFAULT 30,
                    Note TEXT(255),
                    Data_Aggiornamento DATETIME DEFAULT Now()
                )
            """)

        print("✅ Tabella Erlang_Config creata con successo!")

        # Inserisci configurazione di esempio
        print("\n📝 Inserimento configurazione di esempio...")

        db_manager.execute_update("""
            INSERT INTO Erlang_Config (
                Skill, Tipo_Canale, AHT_Seconds, Concurrency,
                Shrinkage, Service_Level_Target, Service_Level_Seconds,
                ASA_Target_Seconds, Occupancy_Target, Interval_Minutes, Note
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            'CUSTOMER_CARE_VOICE',
            'Voice',
            180,  # 3 minuti
            1,    # Voice: sempre 1
            0.30, # 30% shrinkage
            0.80, # 80% SL
            20,   # in 20 secondi
            0,    # ASA non usato per voice
            0.85, # 85% occupancy
            30,   # intervalli 30 min
            'Configurazione esempio per assistenza clienti voice'
        ))

        print("✅ Configurazione di esempio inserita\n")

        print(f"{'='*70}")
        print(f"  MIGRAZIONE COMPLETATA CON SUCCESSO")
        print(f"{'='*70}\n")
        print("Ora puoi:")
        print("  1. Aprire l'applicazione e andare al tab 'Erlang Config'")
        print("  2. Aggiungere altre configurazioni tramite GUI")
        print("  3. Oppure importare da Excel:")
        print("     python scripts/crea_template_erlang_config.py config.xlsx")
        print("     python scripts/import_erlang_config.py config.xlsx")
        print()

        db_manager.close()
        return True

    except Exception as e:
        print(f"❌ Errore durante la migrazione: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    # Determina path database
    db_path = 'data/operator_overtime.db'

    if len(sys.argv) > 1:
        if sys.argv[1] == '--help':
            print("Uso: python migrate_add_erlang_config.py [db_path]")
            print("\nEsempi:")
            print("  python migrate_add_erlang_config.py")
            print("  python migrate_add_erlang_config.py data/operator_overtime.db")
            print("  python migrate_add_erlang_config.py data/operator_overtime.accdb")
            sys.exit(0)
        db_path = sys.argv[1]

    # Cerca database se non specificato
    if not os.path.exists(db_path):
        # Prova Access
        db_path_access = 'data/operator_overtime.accdb'
        if os.path.exists(db_path_access):
            db_path = db_path_access
        else:
            print(f"❌ Database non trovato né in {db_path} né in {db_path_access}")
            print("Creare prima il database dall'applicazione")
            sys.exit(1)

    success = migrate_database(db_path)
    sys.exit(0 if success else 1)
