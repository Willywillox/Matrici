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

        # Crea il database Access (richiede Microsoft Access Database Engine)
        conn_str = (
            r'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};'
            f'DBQ={os.path.abspath(self.db_path)};'
        )

        try:
            # Nota: su Windows con Access installato, questo crea il database
            conn = pyodbc.connect(conn_str)

            # Verifica se le tabelle esistono già
            cursor = conn.cursor()
            existing_tables = [table.table_name for table in cursor.tables(tableType='TABLE')
                              if not table.table_name.startswith('MSys')]

            if 'Anagrafica_Operatori' in existing_tables:
                print(f"Database già configurato con tabelle: {self.db_path}")
                conn.close()
                return

            print(f"Creazione tabelle in: {self.db_path}")
            cursor = conn.cursor()

            # Tabella Anagrafica Operatori
            print("Creazione tabella: Anagrafica_Operatori")
            cursor.execute("""
                CREATE TABLE Anagrafica_Operatori (
                    ID COUNTER PRIMARY KEY,
                    Nome TEXT(50),
                    Cognome TEXT(50),
                    ID_SAP TEXT(20),
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
                    Data_Riferimento DATETIME,
                    Postazione TEXT(20),
                    Microskill TEXT(100)
                )
            """)

            # Tabella Cambio Skill Intraday
            print("Creazione tabella: Cambio_Skill")
            cursor.execute("""
                CREATE TABLE Cambio_Skill (
                    ID COUNTER PRIMARY KEY,
                    ID_SAP TEXT(20),
                    Data_Riferimento DATETIME,
                    Ora_Inizio DATETIME,
                    Ora_Fine DATETIME,
                    Skill_Temporaneo TEXT(100),
                    Note TEXT(255)
                )
            """)

            # Tabella Forecast
            print("Creazione tabella: Forecast")
            cursor.execute("""
                CREATE TABLE Forecast (
                    ID COUNTER PRIMARY KEY,
                    Data_Riferimento DATETIME,
                    Fascia_Oraria DATETIME,
                    Skill TEXT(100),
                    Volumi_Attesi INTEGER,
                    Produttivita_Target DOUBLE,
                    FTE_Richiesti DOUBLE
                )
            """)

            # Tabella Skills (anagrafica skills)
            print("Creazione tabella: Skills")
            cursor.execute("""
                CREATE TABLE Skills (
                    ID COUNTER PRIMARY KEY,
                    Codice_Skill TEXT(50),
                    Descrizione TEXT(255),
                    Produttivita_Default DOUBLE
                )
            """)

            # Tabella Turni (anagrafica turni standard)
            print("Creazione tabella: Turni")
            cursor.execute("""
                CREATE TABLE Turni (
                    ID COUNTER PRIMARY KEY,
                    ID_Turno TEXT(20),
                    Descrizione TEXT(255),
                    Ora_Inizio DATETIME,
                    Ora_Fine DATETIME,
                    Ore_Turno DOUBLE,
                    Ora_Inizio_Spezzato DATETIME,
                    Ora_Fine_Spezzato DATETIME,
                    Note TEXT(255)
                )
            """)

            # Tabella Giustificativi (anagrafica giustificativi)
            print("Creazione tabella: Giustificativi")
            cursor.execute("""
                CREATE TABLE Giustificativi (
                    ID COUNTER PRIMARY KEY,
                    Codice_Giustificativo TEXT(50),
                    Descrizione TEXT(255),
                    Tipologia TEXT(100),
                    Note TEXT(255)
                )
            """)

            # Tabella Erlang_Config (configurazione parametri Erlang C per skill)
            print("Creazione tabella: Erlang_Config")
            cursor.execute("""
                CREATE TABLE Erlang_Config (
                    ID COUNTER PRIMARY KEY,
                    Skill TEXT(100),
                    Tipo_Canale TEXT(20),
                    AHT_Seconds INTEGER,
                    Concurrency INTEGER,
                    Tempo_Pausa_Minuti INTEGER,
                    Shrinkage DOUBLE,
                    Produttivita DOUBLE,
                    Service_Level_Target DOUBLE,
                    Service_Level_Seconds INTEGER,
                    ASA_Target_Seconds INTEGER,
                    Occupancy_Target DOUBLE,
                    Interval_Minutes INTEGER,
                    Note TEXT(255),
                    Data_Aggiornamento DATETIME
                )
            """)

            # Tabella Storico Turni (per mantenere storico)
            print("Creazione tabella: Storico_Turni")
            cursor.execute("""
                CREATE TABLE Storico_Turni (
                    ID COUNTER PRIMARY KEY,
                    ID_SAP TEXT(20),
                    Data_Riferimento DATETIME,
                    Tipo_Turno TEXT(20),
                    Ora_Inizio DATETIME,
                    Ora_Fine DATETIME,
                    Skill TEXT(100),
                    Note TEXT(255),
                    Data_Inserimento DATETIME
                )
            """)

            conn.commit()
            print(f"Database creato con successo: {self.db_path}")

        except pyodbc.Error as e:
            print(f"Errore nella creazione del database Access: {e}")
            import traceback
            traceback.print_exc()
            # Rilancia l'errore invece di creare silenziosamente SQLite
            raise

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
            CREATE TABLE IF NOT EXISTS Giustificativi (
                ID INTEGER PRIMARY KEY AUTOINCREMENT,
                Codice_Giustificativo TEXT UNIQUE NOT NULL,
                Descrizione TEXT,
                Tipologia TEXT,
                Note TEXT
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Erlang_Config (
                ID INTEGER PRIMARY KEY AUTOINCREMENT,
                Skill TEXT UNIQUE NOT NULL,
                Tipo_Canale TEXT DEFAULT 'Voice',
                AHT_Seconds INTEGER DEFAULT 180,
                Concurrency INTEGER DEFAULT 1,
                Tempo_Pausa_Minuti INTEGER DEFAULT 0,
                Shrinkage REAL DEFAULT 0.30,
                Produttivita REAL DEFAULT 1.0,
                Service_Level_Target REAL DEFAULT 0.80,
                Service_Level_Seconds INTEGER DEFAULT 20,
                ASA_Target_Seconds INTEGER DEFAULT 60,
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
