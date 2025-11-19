"""
Script di migrazione database
Copia struttura e dati tra SQLite e Access
"""
import os
import sys
import shutil
import sqlite3
from datetime import datetime

# Aggiungi path per import
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class DatabaseMigrator:
    """Gestisce la migrazione tra diversi tipi di database"""

    # Mapping tipi SQLite -> Access
    TYPE_MAPPING_SQLITE_TO_ACCESS = {
        'INTEGER': 'LONG',
        'TEXT': 'TEXT(255)',
        'REAL': 'DOUBLE',
        'BLOB': 'LONGBINARY',
        'NUMERIC': 'DOUBLE',
    }

    # Tabelle da migrare nell'ordine corretto (per foreign keys)
    TABLES_ORDER = [
        'Skills',
        'Turni',
        'Giustificativi',
        'Erlang_Config',
        'Anagrafica_Operatori',
        'Cambio_Skill',
        'Forecast',
        'Storico_Turni',
    ]

    def __init__(self):
        self.source_conn = None
        self.target_conn = None
        self.stats = {
            'tables_migrated': 0,
            'rows_migrated': 0,
            'errors': []
        }

    def migrate_sqlite_to_access(self, sqlite_path, access_path):
        """Migra da SQLite ad Access"""
        print(f"\n{'='*60}")
        print("MIGRAZIONE DATABASE: SQLite -> Access")
        print(f"{'='*60}")
        print(f"Origine: {sqlite_path}")
        print(f"Destinazione: {access_path}")
        print(f"{'='*60}\n")

        # Verifica file sorgente
        if not os.path.exists(sqlite_path):
            raise FileNotFoundError(f"Database SQLite non trovato: {sqlite_path}")

        # Backup del database Access se esiste
        if os.path.exists(access_path):
            backup_path = self._create_backup(access_path)
            print(f"Backup creato: {backup_path}\n")

        try:
            # Connetti a SQLite
            self.source_conn = sqlite3.connect(sqlite_path)
            self.source_conn.row_factory = sqlite3.Row

            # Connetti/Crea Access
            self._connect_access(access_path)

            # Ottieni lista tabelle da SQLite
            tables = self._get_sqlite_tables()
            print(f"Tabelle da migrare: {len(tables)}\n")

            # Migra ogni tabella
            for table_name in self.TABLES_ORDER:
                if table_name in tables:
                    self._migrate_table(table_name)

            # Migra tabelle aggiuntive non in TABLES_ORDER
            for table_name in tables:
                if table_name not in self.TABLES_ORDER:
                    self._migrate_table(table_name)

            print(f"\n{'='*60}")
            print("MIGRAZIONE COMPLETATA")
            print(f"{'='*60}")
            print(f"Tabelle migrate: {self.stats['tables_migrated']}")
            print(f"Righe totali migrate: {self.stats['rows_migrated']}")

            if self.stats['errors']:
                print(f"\nErrori riscontrati: {len(self.stats['errors'])}")
                for err in self.stats['errors']:
                    print(f"  - {err}")

            return True

        except Exception as e:
            print(f"\nERRORE CRITICO: {e}")
            import traceback
            traceback.print_exc()
            return False

        finally:
            if self.source_conn:
                self.source_conn.close()
            if self.target_conn:
                self.target_conn.close()

    def migrate_access_to_sqlite(self, access_path, sqlite_path):
        """Migra da Access a SQLite"""
        print(f"\n{'='*60}")
        print("MIGRAZIONE DATABASE: Access -> SQLite")
        print(f"{'='*60}")
        print(f"Origine: {access_path}")
        print(f"Destinazione: {sqlite_path}")
        print(f"{'='*60}\n")

        # Verifica file sorgente
        if not os.path.exists(access_path):
            raise FileNotFoundError(f"Database Access non trovato: {access_path}")

        # Backup del database SQLite se esiste
        if os.path.exists(sqlite_path):
            backup_path = self._create_backup(sqlite_path)
            print(f"Backup creato: {backup_path}\n")

        try:
            # Connetti ad Access
            import pyodbc
            conn_str = f"DRIVER={{Microsoft Access Driver (*.mdb, *.accdb)}};DBQ={os.path.abspath(access_path)};"
            self.source_conn = pyodbc.connect(conn_str)

            # Crea/Connetti a SQLite
            # Crea directory se necessario
            db_dir = os.path.dirname(sqlite_path)
            if db_dir and not os.path.exists(db_dir):
                os.makedirs(db_dir)

            self.target_conn = sqlite3.connect(sqlite_path)

            # Ottieni lista tabelle da Access
            cursor = self.source_conn.cursor()
            tables = [table.table_name for table in cursor.tables(tableType='TABLE')
                     if not table.table_name.startswith('MSys')]

            print(f"Tabelle da migrare: {len(tables)}\n")

            # Migra ogni tabella
            for table_name in tables:
                self._migrate_table_access_to_sqlite(table_name)

            self.target_conn.commit()

            print(f"\n{'='*60}")
            print("MIGRAZIONE COMPLETATA")
            print(f"{'='*60}")
            print(f"Tabelle migrate: {self.stats['tables_migrated']}")
            print(f"Righe totali migrate: {self.stats['rows_migrated']}")

            return True

        except Exception as e:
            print(f"\nERRORE CRITICO: {e}")
            import traceback
            traceback.print_exc()
            return False

        finally:
            if self.source_conn:
                self.source_conn.close()
            if self.target_conn:
                self.target_conn.close()

    def _create_backup(self, db_path):
        """Crea un backup del database"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_dir = os.path.join(os.path.dirname(db_path), 'backups')

        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)

        filename = os.path.basename(db_path)
        name, ext = os.path.splitext(filename)
        backup_path = os.path.join(backup_dir, f"{name}_{timestamp}{ext}")

        shutil.copy2(db_path, backup_path)
        return backup_path

    def _connect_access(self, access_path):
        """Connette o crea database Access"""
        try:
            import pyodbc
        except ImportError:
            raise ImportError("pyodbc non installato. Installare con: pip install pyodbc")

        # Crea directory se necessario
        db_dir = os.path.dirname(access_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir)

        # Se il file non esiste, deve essere creato manualmente o con un template
        if not os.path.exists(access_path):
            print("NOTA: Il file Access deve essere creato manualmente prima della migrazione.")
            print("      Puoi copiare un file .accdb vuoto come template.")
            raise FileNotFoundError(f"File Access non trovato: {access_path}")

        conn_str = f"DRIVER={{Microsoft Access Driver (*.mdb, *.accdb)}};DBQ={os.path.abspath(access_path)};"
        self.target_conn = pyodbc.connect(conn_str)

        # Verifica se le tabelle esistono, altrimenti creale
        cursor = self.target_conn.cursor()
        existing_tables = [table.table_name for table in cursor.tables(tableType='TABLE')
                         if not table.table_name.startswith('MSys')]

        if 'Anagrafica_Operatori' not in existing_tables:
            print("Tabelle non trovate nel database Access. Creazione tabelle...")
            from src.database.db_creator import DatabaseCreator
            # Chiudi connessione temporaneamente
            self.target_conn.close()
            # Crea tabelle
            creator = DatabaseCreator(access_path)
            creator.create_database()
            # Riconnetti
            self.target_conn = pyodbc.connect(conn_str)
            print("Tabelle create con successo!")

    def _get_sqlite_tables(self):
        """Ottieni lista tabelle SQLite"""
        cursor = self.source_conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
        return [row[0] for row in cursor.fetchall()]

    def _get_sqlite_table_schema(self, table_name):
        """Ottieni schema tabella SQLite"""
        cursor = self.source_conn.cursor()
        cursor.execute(f"PRAGMA table_info({table_name})")
        return cursor.fetchall()

    def _migrate_table(self, table_name):
        """Migra una singola tabella da SQLite ad Access"""
        print(f"Migrando tabella: {table_name}...", end=" ")

        try:
            # Ottieni dati da SQLite
            src_cursor = self.source_conn.cursor()
            src_cursor.execute(f"SELECT * FROM {table_name}")
            rows = src_cursor.fetchall()

            if not rows:
                print("(vuota)")
                self.stats['tables_migrated'] += 1
                return

            # Ottieni nomi colonne
            columns = [description[0] for description in src_cursor.description]

            # Verifica se la tabella esiste in Access, altrimenti creala
            self._ensure_access_table(table_name, columns)

            # Inserisci dati in Access
            tgt_cursor = self.target_conn.cursor()

            # Svuota tabella esistente
            try:
                tgt_cursor.execute(f"DELETE FROM {table_name}")
            except:
                pass

            # Prepara INSERT
            placeholders = ', '.join(['?' for _ in columns])
            # Escludi colonna ID (autoincrement)
            insert_columns = [c for c in columns if c.upper() != 'ID']
            insert_placeholders = ', '.join(['?' for _ in insert_columns])

            insert_sql = f"INSERT INTO {table_name} ({', '.join(insert_columns)}) VALUES ({insert_placeholders})"

            # Inserisci righe
            for row in rows:
                # Crea dict dalla riga
                row_dict = dict(zip(columns, row))
                # Estrai valori escludendo ID
                values = [row_dict[col] for col in insert_columns]
                try:
                    tgt_cursor.execute(insert_sql, values)
                except Exception as e:
                    self.stats['errors'].append(f"{table_name}: {e}")

            self.target_conn.commit()

            print(f"{len(rows)} righe")
            self.stats['tables_migrated'] += 1
            self.stats['rows_migrated'] += len(rows)

        except Exception as e:
            print(f"ERRORE: {e}")
            self.stats['errors'].append(f"{table_name}: {e}")

    def _ensure_access_table(self, table_name, columns):
        """Verifica che la tabella esista in Access"""
        # In Access le tabelle devono già esistere con lo schema corretto
        # perché la creazione dinamica è complessa
        pass

    def _migrate_table_access_to_sqlite(self, table_name):
        """Migra una singola tabella da Access a SQLite"""
        print(f"Migrando tabella: {table_name}...", end=" ")

        try:
            # Ottieni dati da Access
            src_cursor = self.source_conn.cursor()
            src_cursor.execute(f"SELECT * FROM [{table_name}]")
            rows = src_cursor.fetchall()

            if not rows:
                print("(vuota)")
                self.stats['tables_migrated'] += 1
                return

            # Ottieni nomi colonne
            columns = [description[0] for description in src_cursor.description]

            # Crea tabella in SQLite se non esiste
            self._create_sqlite_table_from_access(table_name, columns, src_cursor)

            # Inserisci dati
            tgt_cursor = self.target_conn.cursor()

            # Svuota tabella esistente
            tgt_cursor.execute(f"DELETE FROM {table_name}")

            # Prepara INSERT
            placeholders = ', '.join(['?' for _ in columns])
            insert_sql = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({placeholders})"

            # Inserisci righe
            for row in rows:
                try:
                    tgt_cursor.execute(insert_sql, tuple(row))
                except Exception as e:
                    self.stats['errors'].append(f"{table_name}: {e}")

            print(f"{len(rows)} righe")
            self.stats['tables_migrated'] += 1
            self.stats['rows_migrated'] += len(rows)

        except Exception as e:
            print(f"ERRORE: {e}")
            self.stats['errors'].append(f"{table_name}: {e}")

    def _create_sqlite_table_from_access(self, table_name, columns, cursor):
        """Crea tabella SQLite basata su schema Access"""
        # Per semplicità, crea tutte le colonne come TEXT
        # In produzione si dovrebbe mappare i tipi correttamente
        col_defs = ', '.join([f'"{col}" TEXT' for col in columns])
        create_sql = f"CREATE TABLE IF NOT EXISTS {table_name} ({col_defs})"

        tgt_cursor = self.target_conn.cursor()
        tgt_cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
        tgt_cursor.execute(create_sql)


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description='Migrazione database Matrici')
    parser.add_argument('direction', choices=['sqlite-to-access', 'access-to-sqlite'],
                       help='Direzione della migrazione')
    parser.add_argument('--source', required=True, help='Path database sorgente')
    parser.add_argument('--target', required=True, help='Path database destinazione')

    args = parser.parse_args()

    migrator = DatabaseMigrator()

    if args.direction == 'sqlite-to-access':
        success = migrator.migrate_sqlite_to_access(args.source, args.target)
    else:
        success = migrator.migrate_access_to_sqlite(args.source, args.target)

    sys.exit(0 if success else 1)


if __name__ == '__main__':
    # Se eseguito senza argomenti, mostra uso interattivo
    if len(sys.argv) == 1:
        print("\nMigrazione Database Matrici")
        print("="*40)
        print("\nUso da linea di comando:")
        print("  python migrate_database.py sqlite-to-access --source data/db.db --target data/db.accdb")
        print("  python migrate_database.py access-to-sqlite --source data/db.accdb --target data/db.db")
        print("\nOppure importa e usa la classe DatabaseMigrator:")
        print("  from scripts.migrate_database import DatabaseMigrator")
        print("  migrator = DatabaseMigrator()")
        print("  migrator.migrate_sqlite_to_access('source.db', 'target.accdb')")
    else:
        main()
