"""
Database manager con supporto multi-utente e SQL Server
"""
import pyodbc
import sqlite3
import os
from datetime import datetime, timedelta
import pandas as pd


class MultiUserDatabaseManager:
    """Gestisce connessioni a database condivisi multi-utente"""

    def __init__(self, config_file='database_config.ini'):
        """
        Inizializza il manager leggendo la configurazione

        Config file formato:
        [database]
        type = sqlserver|access|sqlite
        server = localhost\SQLEXPRESS
        database = Matrici
        trusted_connection = yes
        # oppure
        # username = user
        # password = pass
        """
        self.config = self.load_config(config_file)
        self.conn = None
        self.db_type = self.config.get('type', 'sqlite')
        self.auto_refresh = True  # Auto-refresh dati

    def load_config(self, config_file):
        """Carica configurazione da file INI"""
        import configparser

        config = {}

        if os.path.exists(config_file):
            parser = configparser.ConfigParser()
            parser.read(config_file)

            if 'database' in parser:
                config = dict(parser['database'])
        else:
            # Default: SQLite locale
            config = {
                'type': 'sqlite',
                'path': 'data/operator_overtime.db'
            }

        return config

    def connect(self):
        """Stabilisce connessione al database"""
        try:
            if self.db_type == 'sqlserver':
                # SQL Server
                conn_str_parts = []

                if 'server' in self.config:
                    conn_str_parts.append(f"DRIVER={{ODBC Driver 17 for SQL Server}}")
                    conn_str_parts.append(f"SERVER={self.config['server']}")
                    conn_str_parts.append(f"DATABASE={self.config['database']}")

                    if self.config.get('trusted_connection', 'yes').lower() == 'yes':
                        conn_str_parts.append("Trusted_Connection=yes")
                    else:
                        conn_str_parts.append(f"UID={self.config['username']}")
                        conn_str_parts.append(f"PWD={self.config['password']}")

                    # Opzioni per multi-utente
                    conn_str_parts.append("MARS_Connection=yes")  # Multiple Active Result Sets

                    conn_str = ';'.join(conn_str_parts)
                    self.conn = pyodbc.connect(conn_str, autocommit=False)

            elif self.db_type == 'access':
                # Access su rete
                db_path = self.config.get('path', 'data/operator_overtime.accdb')

                # Supporto percorsi UNC
                conn_str = (
                    r'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};'
                    f'DBQ={db_path};'
                )

                self.conn = pyodbc.connect(conn_str)

            else:
                # SQLite
                db_path = self.config.get('path', 'data/operator_overtime.db')
                self.conn = sqlite3.connect(db_path, timeout=30.0)  # Timeout per lock

            return True

        except Exception as e:
            print(f"Errore connessione database: {e}")
            return False

    def close(self):
        """Chiude la connessione"""
        if self.conn:
            self.conn.close()

    def execute_query(self, query, params=None):
        """Esegue query con gestione lock e retry"""
        max_retries = 3
        retry_delay = 0.5

        for attempt in range(max_retries):
            try:
                if not self.conn:
                    self.connect()

                cursor = self.conn.cursor()

                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)

                return cursor.fetchall()

            except Exception as e:
                if 'locked' in str(e).lower() and attempt < max_retries - 1:
                    # Database locked, retry
                    import time
                    time.sleep(retry_delay)
                    retry_delay *= 2
                else:
                    raise

    def execute_update(self, query, params=None):
        """Esegue update con transaction"""
        max_retries = 3
        retry_delay = 0.5

        for attempt in range(max_retries):
            try:
                if not self.conn:
                    self.connect()

                cursor = self.conn.cursor()

                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)

                self.conn.commit()
                return cursor.rowcount

            except Exception as e:
                self.conn.rollback()

                if 'locked' in str(e).lower() and attempt < max_retries - 1:
                    import time
                    time.sleep(retry_delay)
                    retry_delay *= 2
                else:
                    raise

    def get_last_update_time(self, table_name):
        """Ritorna timestamp ultima modifica della tabella"""
        # Per SQL Server, usa change tracking
        # Per Access/SQLite, mantieni tabella metadati

        if self.db_type == 'sqlserver':
            query = f"""
                SELECT MAX(LastModified)
                FROM {table_name}_Metadata
            """
        else:
            query = f"""
                SELECT MAX(LastModified)
                FROM Metadata
                WHERE TableName = ?
            """

        try:
            result = self.execute_query(query, (table_name,) if self.db_type != 'sqlserver' else None)
            if result and result[0][0]:
                return result[0][0]
        except:
            pass

        return None

    def update_metadata(self, table_name, user_id):
        """Aggiorna metadata dopo modifica"""
        query = """
            INSERT INTO Metadata (TableName, LastModified, ModifiedBy)
            VALUES (?, ?, ?)
        """

        self.execute_update(query, (table_name, datetime.now(), user_id))

    # === METODI CON LOCKING ===

    def insert_operatore_safe(self, operatore_data, user_id):
        """Inserisce operatore con lock ottimistico"""
        try:
            # Begin transaction
            columns = ', '.join(operatore_data.keys())
            placeholders = ', '.join(['?' for _ in operatore_data])
            query = f"INSERT INTO Anagrafica_Operatori ({columns}) VALUES ({placeholders})"

            self.execute_update(query, tuple(operatore_data.values()))

            # Update metadata
            self.update_metadata('Anagrafica_Operatori', user_id)

            return True

        except Exception as e:
            print(f"Errore inserimento: {e}")
            return False

    def update_operatore_safe(self, id_operatore, operatore_data, user_id):
        """Aggiorna operatore con controllo versione"""
        try:
            # Verifica se record non è stato modificato da altri nel frattempo
            # (Optimistic locking)

            set_clause = ', '.join([f"{k} = ?" for k in operatore_data.keys()])
            query = f"UPDATE Anagrafica_Operatori SET {set_clause} WHERE ID = ?"

            params = list(operatore_data.values()) + [id_operatore]
            rows_affected = self.execute_update(query, params)

            if rows_affected > 0:
                self.update_metadata('Anagrafica_Operatori', user_id)
                return True
            else:
                # Record non trovato o modificato da altri
                return False

        except Exception as e:
            print(f"Errore update: {e}")
            return False

    def check_for_updates(self, table_name, last_check):
        """Verifica se ci sono stati aggiornamenti da altri utenti"""
        last_update = self.get_last_update_time(table_name)

        if last_update and last_check:
            if isinstance(last_update, str):
                last_update = datetime.fromisoformat(last_update)
            if isinstance(last_check, str):
                last_check = datetime.fromisoformat(last_check)

            return last_update > last_check

        return False

    def __enter__(self):
        """Context manager"""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()
