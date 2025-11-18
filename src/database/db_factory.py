"""
Database Factory - Crea connessioni per diversi tipi di database
Fornisce un'interfaccia unificata per SQLite, Access e SQL Server
"""
import os
import sqlite3
from .db_config import DatabaseConfig


class DatabaseFactory:
    """Factory per creare connessioni database"""

    def __init__(self, config_path='database_config.ini'):
        self.config = DatabaseConfig(config_path)
        self.conn = None
        self._db_type = None

    @property
    def db_type(self):
        return self._db_type or self.config.db_type

    def connect(self):
        """Crea una connessione al database configurato"""
        db_type = self.config.db_type
        self._db_type = db_type

        if db_type == 'sqlite':
            return self._connect_sqlite()
        elif db_type == 'access':
            return self._connect_access()
        elif db_type == 'sqlserver':
            return self._connect_sqlserver()
        else:
            raise ValueError(f"Tipo database non supportato: {db_type}")

    def _connect_sqlite(self):
        """Connessione SQLite"""
        db_path = self.config.db_path

        # Crea directory se non esiste
        db_dir = os.path.dirname(db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir)

        self.conn = sqlite3.connect(db_path)
        return self.conn

    def _connect_access(self):
        """Connessione Access via ODBC"""
        try:
            import pyodbc
        except ImportError:
            raise ImportError("pyodbc non installato. Installare con: pip install pyodbc")

        conn_str = self.config.get_connection_string()
        self.conn = pyodbc.connect(conn_str)
        return self.conn

    def _connect_sqlserver(self):
        """Connessione SQL Server via ODBC"""
        try:
            import pyodbc
        except ImportError:
            raise ImportError("pyodbc non installato. Installare con: pip install pyodbc")

        conn_str = self.config.get_connection_string()
        self.conn = pyodbc.connect(conn_str)
        return self.conn

    def close(self):
        """Chiude la connessione"""
        if self.conn:
            self.conn.close()
            self.conn = None

    def execute_query(self, query, params=None):
        """Esegue una query SELECT"""
        if not self.conn:
            self.connect()

        cursor = self.conn.cursor()

        # Adatta i placeholder per il tipo di database
        query = self._adapt_query(query)

        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)

        return cursor.fetchall()

    def execute_update(self, query, params=None):
        """Esegue una query UPDATE/INSERT/DELETE"""
        if not self.conn:
            self.connect()

        cursor = self.conn.cursor()

        # Adatta i placeholder per il tipo di database
        query = self._adapt_query(query)

        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)

        self.conn.commit()
        return cursor.rowcount

    def execute_many(self, query, params_list):
        """Esegue una query multiple volte con diversi parametri"""
        if not self.conn:
            self.connect()

        cursor = self.conn.cursor()
        query = self._adapt_query(query)

        cursor.executemany(query, params_list)
        self.conn.commit()
        return cursor.rowcount

    def _adapt_query(self, query):
        """Adatta la query per il tipo di database"""
        db_type = self.db_type

        if db_type == 'sqlite':
            # SQLite usa ? come placeholder (già standard)
            return query
        elif db_type in ['access', 'sqlserver']:
            # Access e SQL Server usano ? come placeholder (già compatibile)
            return query

        return query

    def get_tables(self):
        """Ritorna la lista delle tabelle nel database"""
        db_type = self.db_type

        if db_type == 'sqlite':
            result = self.execute_query(
                "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
            )
        elif db_type == 'access':
            cursor = self.conn.cursor()
            tables = [table.table_name for table in cursor.tables(tableType='TABLE')]
            return tables
        elif db_type == 'sqlserver':
            result = self.execute_query(
                "SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE='BASE TABLE'"
            )
        else:
            return []

        return [row[0] for row in result]

    def get_table_columns(self, table_name):
        """Ritorna le colonne di una tabella"""
        db_type = self.db_type

        if db_type == 'sqlite':
            result = self.execute_query(f"PRAGMA table_info({table_name})")
            return [(row[1], row[2]) for row in result]  # (nome, tipo)
        elif db_type == 'access':
            cursor = self.conn.cursor()
            columns = [(col.column_name, col.type_name)
                      for col in cursor.columns(table=table_name)]
            return columns
        elif db_type == 'sqlserver':
            result = self.execute_query(f"""
                SELECT COLUMN_NAME, DATA_TYPE
                FROM INFORMATION_SCHEMA.COLUMNS
                WHERE TABLE_NAME = ?
            """, (table_name,))
            return [(row[0], row[1]) for row in result]

        return []

    def get_row_count(self, table_name):
        """Ritorna il numero di righe in una tabella"""
        result = self.execute_query(f"SELECT COUNT(*) FROM {table_name}")
        return result[0][0] if result else 0


def create_database_manager(config_path='database_config.ini'):
    """Funzione helper per creare un DatabaseFactory configurato"""
    return DatabaseFactory(config_path)


if __name__ == '__main__':
    # Test factory
    factory = DatabaseFactory()
    try:
        factory.connect()
        tables = factory.get_tables()
        print(f"Database tipo: {factory.db_type}")
        print(f"Tabelle trovate: {tables}")

        for table in tables:
            count = factory.get_row_count(table)
            print(f"  - {table}: {count} righe")
    finally:
        factory.close()
