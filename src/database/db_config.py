"""
Sistema di configurazione database multi-piattaforma
Supporta SQLite, Access e SQL Server
"""
import os
import configparser
from pathlib import Path


class DatabaseConfig:
    """Gestisce la configurazione del database"""

    DEFAULT_CONFIG = {
        'database': {
            'type': 'sqlite',
            'path': 'data/operator_overtime.db'
        },
        'access': {
            'path': '',
            'driver': 'Microsoft Access Driver (*.mdb, *.accdb)'
        },
        'sqlserver': {
            'server': 'localhost',
            'database': 'Matrici',
            'trusted_connection': 'yes',
            'driver': 'ODBC Driver 17 for SQL Server'
        }
    }

    def __init__(self, config_path='database_config.ini'):
        self.config_path = config_path
        self.config = configparser.ConfigParser()
        self._load_config()

    def _load_config(self):
        """Carica la configurazione dal file o crea default"""
        if os.path.exists(self.config_path):
            self.config.read(self.config_path)
        else:
            # Crea configurazione default
            for section, values in self.DEFAULT_CONFIG.items():
                self.config[section] = values
            self._save_config()

    def _save_config(self):
        """Salva la configurazione su file"""
        with open(self.config_path, 'w') as f:
            self.config.write(f)

    @property
    def db_type(self):
        """Ritorna il tipo di database configurato"""
        return self.config.get('database', 'type', fallback='sqlite')

    @db_type.setter
    def db_type(self, value):
        """Imposta il tipo di database"""
        if value not in ['sqlite', 'access', 'sqlserver']:
            raise ValueError(f"Tipo database non supportato: {value}")
        self.config.set('database', 'type', value)
        self._save_config()

    @property
    def db_path(self):
        """Ritorna il path del database"""
        return self.config.get('database', 'path', fallback='data/operator_overtime.db')

    @db_path.setter
    def db_path(self, value):
        """Imposta il path del database"""
        self.config.set('database', 'path', value)
        self._save_config()

    def get_connection_string(self):
        """Genera la stringa di connessione in base al tipo di database"""
        db_type = self.db_type

        if db_type == 'sqlite':
            return self.db_path

        elif db_type == 'access':
            access_path = self.config.get('access', 'path', fallback=self.db_path)
            driver = self.config.get('access', 'driver')
            return f"DRIVER={{{driver}}};DBQ={os.path.abspath(access_path)};"

        elif db_type == 'sqlserver':
            server = self.config.get('sqlserver', 'server')
            database = self.config.get('sqlserver', 'database')
            driver = self.config.get('sqlserver', 'driver')
            trusted = self.config.get('sqlserver', 'trusted_connection')

            conn_str = f"DRIVER={{{driver}}};SERVER={server};DATABASE={database};"
            if trusted.lower() == 'yes':
                conn_str += "Trusted_Connection=yes;"
            return conn_str

        raise ValueError(f"Tipo database non supportato: {db_type}")

    def set_sqlite(self, path):
        """Configura per usare SQLite"""
        self.config.set('database', 'type', 'sqlite')
        self.config.set('database', 'path', path)
        self._save_config()

    def set_access(self, path):
        """Configura per usare Access"""
        self.config.set('database', 'type', 'access')
        self.config.set('database', 'path', path)
        self.config.set('access', 'path', path)
        self._save_config()

    def set_sqlserver(self, server, database, trusted=True):
        """Configura per usare SQL Server"""
        self.config.set('database', 'type', 'sqlserver')
        self.config.set('sqlserver', 'server', server)
        self.config.set('sqlserver', 'database', database)
        self.config.set('sqlserver', 'trusted_connection', 'yes' if trusted else 'no')
        self._save_config()

    def get_config_summary(self):
        """Ritorna un riepilogo della configurazione attuale"""
        return {
            'type': self.db_type,
            'path': self.db_path,
            'connection_string': self.get_connection_string()
        }


if __name__ == '__main__':
    # Test configurazione
    config = DatabaseConfig()
    print("Configurazione attuale:")
    print(config.get_config_summary())
