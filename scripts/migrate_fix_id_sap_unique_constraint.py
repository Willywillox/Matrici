#!/usr/bin/env python3
"""
Script di migrazione per correggere il vincolo UNIQUE su ID_SAP

PROBLEMA:
- Il database ha ID_SAP con vincolo UNIQUE
- Ma gli operatori possono avere lo stesso ID_SAP in date diverse
- Causa errore "UNIQUE constraint failed" durante l'import

SOLUZIONE:
- Rimuove UNIQUE da ID_SAP
- Aggiunge UNIQUE sulla combinazione (ID_SAP, Data_Riferimento)
- Permette stesso operatore in giorni diversi

USO:
    python scripts/migrate_fix_id_sap_unique_constraint.py
"""

import sys
import os
from pathlib import Path

# Aggiungi path per import
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from database.db_manager import DatabaseManager


def migrate_sqlite(db_path='data/operator_overtime.db'):
    """
    Migra database SQLite per correggere vincolo UNIQUE su ID_SAP

    In SQLite non possiamo modificare vincoli esistenti,
    quindi dobbiamo ricreare la tabella:
    1. Crea nuova tabella con schema corretto
    2. Copia dati dalla vecchia alla nuova
    3. Elimina vecchia tabella
    4. Rinomina nuova tabella
    """

    print(f"\n{'='*70}")
    print(f"  MIGRAZIONE DATABASE SQLITE")
    print(f"{'='*70}\n")
    print(f"Database: {db_path}\n")

    if not Path(db_path).exists():
        print(f"[ERROR] Database non trovato: {db_path}")
        return False

    db_manager = DatabaseManager(db_path)

    try:
        db_manager.connect()

        # Verifica se migrazione è necessaria
        # Controlla se esiste già il nuovo constraint
        result = db_manager.execute_query("""
            SELECT sql FROM sqlite_master
            WHERE type='table' AND name='Anagrafica_Operatori'
        """)

        if result and len(result) > 0:
            table_sql = result[0][0]
            print(f"Schema attuale della tabella:\n{table_sql}\n")

            # Verifica se ha già il constraint corretto
            if 'UNIQUE (ID_SAP, Data_Riferimento)' in table_sql or 'UNIQUE(ID_SAP, Data_Riferimento)' in table_sql:
                print("[OK] Il database ha già il constraint corretto!")
                print("Nessuna migrazione necessaria.\n")
                db_manager.close()
                return True

            # Verifica se ha ancora il vecchio UNIQUE su ID_SAP
            if 'ID_SAP TEXT UNIQUE' in table_sql or 'ID_SAP" UNIQUE' in table_sql:
                print("[INFO] Rilevato vecchio constraint UNIQUE su ID_SAP")
                print("[INFO] Inizio migrazione...\n")
            else:
                print("[INFO] Schema non standard, applico migrazione comunque...\n")

        # PASSO 1: Crea nuova tabella con schema corretto
        print("[1/5] Creazione nuova tabella 'Anagrafica_Operatori_New'...")

        db_manager.execute_update("""
            CREATE TABLE Anagrafica_Operatori_New (
                ID INTEGER PRIMARY KEY AUTOINCREMENT,
                Nome TEXT NOT NULL,
                Cognome TEXT NOT NULL,
                ID_SAP TEXT NOT NULL,
                Tipo_Contratto TEXT,
                FTE REAL,
                Ore_Settimana REAL,
                ID_Turno TEXT,
                Ora_Inizio_Turno TEXT,
                Ora_Fine_Turno TEXT,
                Ora_Inizio_Turno_Spezzato TEXT,
                Ora_Fine_Turno_Spezzato TEXT,
                Inizio_Strao_1 TEXT,
                Fine_Strao_1 TEXT,
                Inizio_Strao_2 TEXT,
                Fine_Strao_2 TEXT,
                Inizio_Strao_3 TEXT,
                Fine_Strao_3 TEXT,
                Inizio_Pausa_1 TEXT,
                Fine_Pausa_1 TEXT,
                Inizio_Pausa_2 TEXT,
                Fine_Pausa_2 TEXT,
                Inizio_Pausa_3 TEXT,
                Fine_Pausa_3 TEXT,
                Inizio_Pausa_4 TEXT,
                Fine_Pausa_4 TEXT,
                Inizio_Pausa_5 TEXT,
                Fine_Pausa_5 TEXT,
                Tipo_Giust_1 TEXT,
                Inizio_Giust_1 TEXT,
                Fine_Giust_1 TEXT,
                Tipo_Giust_2 TEXT,
                Inizio_Giust_2 TEXT,
                Fine_Giust_2 TEXT,
                Tipo_Giust_3 TEXT,
                Inizio_Giust_3 TEXT,
                Fine_Giust_3 TEXT,
                Tipo_Giust_4 TEXT,
                Inizio_Giust_4 TEXT,
                Fine_Giust_4 TEXT,
                Tipo_Giust_5 TEXT,
                Inizio_Giust_5 TEXT,
                Fine_Giust_5 TEXT,
                Etichetta_Skill TEXT,
                Data_Riferimento TEXT NOT NULL,
                Postazione TEXT,
                UNIQUE (ID_SAP, Data_Riferimento)
            )
        """)
        print("    [OK] Nuova tabella creata\n")

        # PASSO 2: Conta record nella tabella vecchia
        print("[2/5] Conta record da migrare...")
        result = db_manager.execute_query("SELECT COUNT(*) FROM Anagrafica_Operatori")
        record_count = result[0][0] if result else 0
        print(f"    [OK] Trovati {record_count} record\n")

        # PASSO 3: Copia dati dalla vecchia alla nuova
        print("[3/5] Copia dati nella nuova tabella...")

        db_manager.execute_update("""
            INSERT INTO Anagrafica_Operatori_New (
                ID, Nome, Cognome, ID_SAP, Tipo_Contratto, FTE, Ore_Settimana,
                ID_Turno, Ora_Inizio_Turno, Ora_Fine_Turno,
                Ora_Inizio_Turno_Spezzato, Ora_Fine_Turno_Spezzato,
                Inizio_Strao_1, Fine_Strao_1, Inizio_Strao_2, Fine_Strao_2,
                Inizio_Strao_3, Fine_Strao_3,
                Inizio_Pausa_1, Fine_Pausa_1, Inizio_Pausa_2, Fine_Pausa_2,
                Inizio_Pausa_3, Fine_Pausa_3, Inizio_Pausa_4, Fine_Pausa_4,
                Inizio_Pausa_5, Fine_Pausa_5,
                Tipo_Giust_1, Inizio_Giust_1, Fine_Giust_1,
                Tipo_Giust_2, Inizio_Giust_2, Fine_Giust_2,
                Tipo_Giust_3, Inizio_Giust_3, Fine_Giust_3,
                Tipo_Giust_4, Inizio_Giust_4, Fine_Giust_4,
                Tipo_Giust_5, Inizio_Giust_5, Fine_Giust_5,
                Etichetta_Skill, Data_Riferimento, Postazione
            )
            SELECT
                ID, Nome, Cognome, ID_SAP, Tipo_Contratto, FTE, Ore_Settimana,
                ID_Turno, Ora_Inizio_Turno, Ora_Fine_Turno,
                Ora_Inizio_Turno_Spezzato, Ora_Fine_Turno_Spezzato,
                Inizio_Strao_1, Fine_Strao_1, Inizio_Strao_2, Fine_Strao_2,
                Inizio_Strao_3, Fine_Strao_3,
                Inizio_Pausa_1, Fine_Pausa_1, Inizio_Pausa_2, Fine_Pausa_2,
                Inizio_Pausa_3, Fine_Pausa_3, Inizio_Pausa_4, Fine_Pausa_4,
                Inizio_Pausa_5, Fine_Pausa_5,
                Tipo_Giust_1, Inizio_Giust_1, Fine_Giust_1,
                Tipo_Giust_2, Inizio_Giust_2, Fine_Giust_2,
                Tipo_Giust_3, Inizio_Giust_3, Fine_Giust_3,
                Tipo_Giust_4, Inizio_Giust_4, Fine_Giust_4,
                Tipo_Giust_5, Inizio_Giust_5, Fine_Giust_5,
                Etichetta_Skill, Data_Riferimento, Postazione
            FROM Anagrafica_Operatori
        """)

        # Verifica che tutti i record siano stati copiati
        result = db_manager.execute_query("SELECT COUNT(*) FROM Anagrafica_Operatori_New")
        new_count = result[0][0] if result else 0
        print(f"    [OK] Copiati {new_count} record\n")

        if new_count != record_count:
            print(f"    [WARN] Conteggio diverso! Vecchia: {record_count}, Nuova: {new_count}")
            print(f"    Questo può succedere se c'erano duplicati ID_SAP + Data")

        # PASSO 4: Elimina vecchia tabella
        print("[4/5] Eliminazione vecchia tabella...")
        db_manager.execute_update("DROP TABLE Anagrafica_Operatori")
        print("    [OK] Vecchia tabella eliminata\n")

        # PASSO 5: Rinomina nuova tabella
        print("[5/5] Rinomina nuova tabella...")
        db_manager.execute_update("""
            ALTER TABLE Anagrafica_Operatori_New
            RENAME TO Anagrafica_Operatori
        """)
        print("    [OK] Tabella rinominata\n")

        # Verifica finale
        result = db_manager.execute_query("""
            SELECT sql FROM sqlite_master
            WHERE type='table' AND name='Anagrafica_Operatori'
        """)

        if result:
            new_schema = result[0][0]
            print(f"{'='*70}")
            print(f"  SCHEMA FINALE")
            print(f"{'='*70}\n")
            print(new_schema)
            print(f"\n{'='*70}")

            if 'UNIQUE (ID_SAP, Data_Riferimento)' in new_schema or 'UNIQUE(ID_SAP, Data_Riferimento)' in new_schema:
                print("[OK] Migrazione completata con successo!")
                print(f"[OK] Record migrati: {new_count}")
                print(f"[OK] Nuovo vincolo: UNIQUE (ID_SAP, Data_Riferimento)")
            else:
                print("[ERROR] Qualcosa è andato storto, constraint non trovato")
                return False

        db_manager.close()
        print(f"{'='*70}\n")
        return True

    except Exception as e:
        print(f"[ERROR] Errore durante la migrazione: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main function"""

    # Path database
    db_path = 'data/operator_overtime.db'

    if not os.path.exists(db_path):
        print(f"[ERROR] Database non trovato: {db_path}")
        print("\nAssicurati di eseguire lo script dalla directory principale del progetto")
        print("e che il database esista in data/operator_overtime.db")
        return 1

    # Esegui migrazione
    success = migrate_sqlite(db_path)

    if success:
        print("\n[INFO] Ora puoi importare i tuoi operatori con lo stesso ID_SAP in date diverse!")
        print("[INFO] Riprova l'import Excel dalla GUI")
        return 0
    else:
        print("\n[ERROR] Migrazione fallita. Controlla gli errori sopra.")
        return 1


if __name__ == '__main__':
    sys.exit(main())
