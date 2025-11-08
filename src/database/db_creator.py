"""
Modulo per la creazione e gestione del database Access
"""
import pyodbc
import os
from datetime import datetime


class DatabaseCreator:
    """Gestisce la creazione del database Access"""

    def __init__(self, db_path='data/operator_overtime.accdb'):
        self.db_path = db_path

    def create_database(self):
        """Crea il database Access con tutte le tabelle necessarie"""

        # Verifica se esiste già
        if os.path.exists(self.db_path):
            print(f"Database già esistente: {self.db_path}")
            return

        # Crea il database Access (richiede Microsoft Access Database Engine)
        conn_str = (
            r'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};'
            f'DBQ={os.path.abspath(self.db_path)};'
        )

        try:
            # Nota: su Windows con Access installato, questo crea il database
            conn = pyodbc.connect(conn_str)
            cursor = conn.cursor()

            # Tabella Anagrafica Operatori
            cursor.execute("""
                CREATE TABLE Anagrafica_Operatori (
                    ID AUTOINCREMENT PRIMARY KEY,
                    Nome TEXT(50) NOT NULL,
                    Cognome TEXT(50) NOT NULL,
                    ID_SAP TEXT(20) UNIQUE NOT NULL,
                    Tipo_Contratto TEXT(50),
                    FTE DOUBLE,
                    Ore_Settimana DOUBLE,
                    ID_Turno TEXT(20),
                    Ora_Inizio_Turno DATETIME,
                    Ora_Fine_Turno DATETIME,
                    Ora_Inizio_Turno_Spezzato DATETIME,
                    Ora_Fine_Turno_Spezzato DATETIME,
                    Inizio_Strao_1 DATETIME,
                    Fine_Strao_1 DATETIME,
                    Inizio_Strao_2 DATETIME,
                    Fine_Strao_2 DATETIME,
                    Inizio_Strao_3 DATETIME,
                    Fine_Strao_3 DATETIME,
                    Inizio_Pausa_1 DATETIME,
                    Fine_Pausa_1 DATETIME,
                    Inizio_Pausa_2 DATETIME,
                    Fine_Pausa_2 DATETIME,
                    Inizio_Pausa_3 DATETIME,
                    Fine_Pausa_3 DATETIME,
                    Inizio_Pausa_4 DATETIME,
                    Fine_Pausa_4 DATETIME,
                    Inizio_Pausa_5 DATETIME,
                    Fine_Pausa_5 DATETIME,
                    Tipo_Giust_1 TEXT(50),
                    Inizio_Giust_1 DATETIME,
                    Fine_Giust_1 DATETIME,
                    Tipo_Giust_2 TEXT(50),
                    Inizio_Giust_2 DATETIME,
                    Fine_Giust_2 DATETIME,
                    Tipo_Giust_3 TEXT(50),
                    Inizio_Giust_3 DATETIME,
                    Fine_Giust_3 DATETIME,
                    Tipo_Giust_4 TEXT(50),
                    Inizio_Giust_4 DATETIME,
                    Fine_Giust_4 DATETIME,
                    Tipo_Giust_5 TEXT(50),
                    Inizio_Giust_5 DATETIME,
                    Fine_Giust_5 DATETIME,
                    Etichetta_Skill TEXT(100),
                    Data_Riferimento DATETIME NOT NULL,
                    Postazione TEXT(20)
                )
            """)

            # Tabella Cambio Skill Intraday
            cursor.execute("""
                CREATE TABLE Cambio_Skill (
                    ID AUTOINCREMENT PRIMARY KEY,
                    ID_SAP TEXT(20) NOT NULL,
                    Data_Riferimento DATETIME NOT NULL,
                    Ora_Inizio DATETIME NOT NULL,
                    Ora_Fine DATETIME NOT NULL,
                    Skill_Temporaneo TEXT(100) NOT NULL,
                    Note TEXT(255)
                )
            """)

            # Tabella Forecast
            cursor.execute("""
                CREATE TABLE Forecast (
                    ID AUTOINCREMENT PRIMARY KEY,
                    Data_Riferimento DATETIME NOT NULL,
                    Fascia_Oraria DATETIME NOT NULL,
                    Skill TEXT(100) NOT NULL,
                    Volumi_Attesi INTEGER,
                    Produttivita_Target DOUBLE,
                    FTE_Richiesti DOUBLE
                )
            """)

            # Tabella Skills (anagrafica skills)
            cursor.execute("""
                CREATE TABLE Skills (
                    ID AUTOINCREMENT PRIMARY KEY,
                    Codice_Skill TEXT(50) UNIQUE NOT NULL,
                    Descrizione TEXT(255),
                    Produttivita_Default DOUBLE
                )
            """)

            # Tabella Turni (anagrafica turni standard)
            cursor.execute("""
                CREATE TABLE Turni (
                    ID AUTOINCREMENT PRIMARY KEY,
                    ID_Turno TEXT(20) UNIQUE NOT NULL,
                    Descrizione TEXT(255),
                    Ora_Inizio DATETIME NOT NULL,
                    Ora_Fine DATETIME NOT NULL,
                    Ore_Turno DOUBLE,
                    Ora_Inizio_Spezzato DATETIME,
                    Ora_Fine_Spezzato DATETIME,
                    Note TEXT(255)
                )
            """)

            # Tabella Erlang_Config (configurazione parametri Erlang C per skill)
            cursor.execute("""
                CREATE TABLE Erlang_Config (
                    ID AUTOINCREMENT PRIMARY KEY,
                    Skill TEXT(100) UNIQUE NOT NULL,
                    AHT_Seconds INTEGER DEFAULT 180,
                    Tempo_Pausa_Minuti INTEGER DEFAULT 0,
                    Shrinkage DOUBLE DEFAULT 0.30,
                    Service_Level_Target DOUBLE DEFAULT 0.80,
                    Service_Level_Seconds INTEGER DEFAULT 20,
                    Occupancy_Target DOUBLE DEFAULT 0.85,
                    Interval_Minutes INTEGER DEFAULT 30,
                    Note TEXT(255),
                    Data_Aggiornamento DATETIME DEFAULT Now()
                )
            """)

            # Tabella Storico Turni (per mantenere storico)
            cursor.execute("""
                CREATE TABLE Storico_Turni (
                    ID AUTOINCREMENT PRIMARY KEY,
                    ID_SAP TEXT(20) NOT NULL,
                    Data_Riferimento DATETIME NOT NULL,
                    Tipo_Turno TEXT(20),
                    Ora_Inizio DATETIME,
                    Ora_Fine DATETIME,
                    Skill TEXT(100),
                    Note TEXT(255),
                    Data_Inserimento DATETIME DEFAULT Now()
                )
            """)

            conn.commit()
            print(f"Database creato con successo: {self.db_path}")

        except pyodbc.Error as e:
            print(f"Errore nella creazione del database: {e}")
            print("\nNOTA: Su Linux/Mac, Access non è supportato.")
            print("Verrà creato un database SQLite alternativo...")
            self._create_sqlite_alternative()

        finally:
            if 'conn' in locals():
                conn.close()

    def _create_sqlite_alternative(self):
        """Crea un database SQLite come alternativa per sviluppo/test"""
        import sqlite3

        sqlite_path = self.db_path.replace('.accdb', '.db')
        conn = sqlite3.connect(sqlite_path)
        cursor = conn.cursor()

        # Stesse tabelle ma per SQLite
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Anagrafica_Operatori (
                ID INTEGER PRIMARY KEY AUTOINCREMENT,
                Nome TEXT NOT NULL,
                Cognome TEXT NOT NULL,
                ID_SAP TEXT UNIQUE NOT NULL,
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
                Postazione TEXT
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Cambio_Skill (
                ID INTEGER PRIMARY KEY AUTOINCREMENT,
                ID_SAP TEXT NOT NULL,
                Data_Riferimento TEXT NOT NULL,
                Ora_Inizio TEXT NOT NULL,
                Ora_Fine TEXT NOT NULL,
                Skill_Temporaneo TEXT NOT NULL,
                Note TEXT
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Forecast (
                ID INTEGER PRIMARY KEY AUTOINCREMENT,
                Data_Riferimento TEXT NOT NULL,
                Fascia_Oraria TEXT NOT NULL,
                Skill TEXT NOT NULL,
                Volumi_Attesi INTEGER,
                Produttivita_Target REAL,
                FTE_Richiesti REAL
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Skills (
                ID INTEGER PRIMARY KEY AUTOINCREMENT,
                Codice_Skill TEXT UNIQUE NOT NULL,
                Descrizione TEXT,
                Produttivita_Default REAL
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Turni (
                ID INTEGER PRIMARY KEY AUTOINCREMENT,
                ID_Turno TEXT UNIQUE NOT NULL,
                Descrizione TEXT,
                Ora_Inizio TEXT NOT NULL,
                Ora_Fine TEXT NOT NULL,
                Ore_Turno REAL,
                Ora_Inizio_Spezzato TEXT,
                Ora_Fine_Spezzato TEXT,
                Note TEXT
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Erlang_Config (
                ID INTEGER PRIMARY KEY AUTOINCREMENT,
                Skill TEXT UNIQUE NOT NULL,
                AHT_Seconds INTEGER DEFAULT 180,
                Tempo_Pausa_Minuti INTEGER DEFAULT 0,
                Shrinkage REAL DEFAULT 0.30,
                Service_Level_Target REAL DEFAULT 0.80,
                Service_Level_Seconds INTEGER DEFAULT 20,
                Occupancy_Target REAL DEFAULT 0.85,
                Interval_Minutes INTEGER DEFAULT 30,
                Note TEXT,
                Data_Aggiornamento TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Storico_Turni (
                ID INTEGER PRIMARY KEY AUTOINCREMENT,
                ID_SAP TEXT NOT NULL,
                Data_Riferimento TEXT NOT NULL,
                Tipo_Turno TEXT,
                Ora_Inizio TEXT,
                Ora_Fine TEXT,
                Skill TEXT,
                Note TEXT,
                Data_Inserimento TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        conn.commit()
        conn.close()
        print(f"Database SQLite creato con successo: {sqlite_path}")


if __name__ == '__main__':
    creator = DatabaseCreator()
    creator.create_database()
