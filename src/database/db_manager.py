"""
Modulo per la gestione della connessione e operazioni sul database
"""
import pyodbc
import sqlite3
import os
from datetime import datetime, timedelta
import pandas as pd


class DatabaseManager:
    """Gestisce le operazioni sul database"""

    def __init__(self, db_path='data/operator_overtime.accdb'):
        self.db_path = db_path
        self.conn = None
        self.is_sqlite = db_path.endswith('.db')

    def connect(self):
        """Stabilisce la connessione al database"""
        try:
            if self.is_sqlite:
                self.conn = sqlite3.connect(self.db_path)
                # Configura row_factory per accedere alle colonne per nome
                self.conn.row_factory = sqlite3.Row
            else:
                conn_str = (
                    r'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};'
                    f'DBQ={os.path.abspath(self.db_path)};'
                )
                self.conn = pyodbc.connect(conn_str)
            return True
        except Exception as e:
            print(f"Errore connessione database: {e}")
            # Fallback a SQLite
            if not self.is_sqlite:
                self.db_path = self.db_path.replace('.accdb', '.db')
                self.is_sqlite = True
                return self.connect()
            return False

    def close(self):
        """Chiude la connessione al database"""
        if self.conn:
            self.conn.close()

    def execute_query(self, query, params=None):
        """Esegue una query e ritorna i risultati"""
        if not self.conn:
            self.connect()

        cursor = self.conn.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)

        return cursor.fetchall()

    def execute_update(self, query, params=None):
        """Esegue una query di update/insert/delete"""
        if not self.conn:
            self.connect()

        cursor = self.conn.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)

        self.conn.commit()
        return cursor.rowcount

    # === OPERATORI ===

    def get_operatori(self, data_riferimento=None):
        """Recupera tutti gli operatori per una data specifica"""
        query = "SELECT * FROM Anagrafica_Operatori"
        if data_riferimento:
            query += " WHERE Data_Riferimento = ?"
            return self.execute_query(query, (data_riferimento,))
        return self.execute_query(query)

    def get_operatore_by_sap(self, id_sap, data_riferimento):
        """Recupera un operatore specifico per ID SAP e data"""
        query = """
            SELECT * FROM Anagrafica_Operatori
            WHERE ID_SAP = ? AND Data_Riferimento = ?
        """
        return self.execute_query(query, (id_sap, data_riferimento))

    def insert_operatore(self, operatore_data):
        """Inserisce un nuovo operatore"""
        columns = ', '.join(operatore_data.keys())
        placeholders = ', '.join(['?' for _ in operatore_data])
        query = f"INSERT INTO Anagrafica_Operatori ({columns}) VALUES ({placeholders})"

        return self.execute_update(query, tuple(operatore_data.values()))

    def update_operatore(self, id_operatore, operatore_data):
        """Aggiorna un operatore esistente"""
        set_clause = ', '.join([f"{k} = ?" for k in operatore_data.keys()])
        query = f"UPDATE Anagrafica_Operatori SET {set_clause} WHERE ID = ?"

        params = list(operatore_data.values()) + [id_operatore]
        return self.execute_update(query, params)

    def delete_operatore(self, id_operatore):
        """Elimina un operatore"""
        query = "DELETE FROM Anagrafica_Operatori WHERE ID = ?"
        return self.execute_update(query, (id_operatore,))

    # === CAMBIO SKILL ===

    def get_cambi_skill(self, id_sap=None, data_riferimento=None):
        """Recupera i cambi skill"""
        query = "SELECT * FROM Cambio_Skill WHERE 1=1"
        params = []

        if id_sap:
            query += " AND ID_SAP = ?"
            params.append(id_sap)

        if data_riferimento:
            query += " AND Data_Riferimento = ?"
            params.append(data_riferimento)

        if params:
            return self.execute_query(query, tuple(params))
        return self.execute_query(query)

    def insert_cambio_skill(self, cambio_data):
        """Inserisce un cambio skill"""
        columns = ', '.join(cambio_data.keys())
        placeholders = ', '.join(['?' for _ in cambio_data])
        query = f"INSERT INTO Cambio_Skill ({columns}) VALUES ({placeholders})"

        return self.execute_update(query, tuple(cambio_data.values()))

    # === FORECAST ===

    def get_forecast(self, data_riferimento=None, skill=None):
        """Recupera i forecast"""
        query = "SELECT * FROM Forecast WHERE 1=1"
        params = []

        if data_riferimento:
            query += " AND Data_Riferimento = ?"
            params.append(data_riferimento)

        if skill:
            query += " AND Skill = ?"
            params.append(skill)

        query += " ORDER BY Fascia_Oraria"

        if params:
            return self.execute_query(query, tuple(params))
        return self.execute_query(query)

    def insert_forecast(self, forecast_data):
        """Inserisce un record di forecast"""
        columns = ', '.join(forecast_data.keys())
        placeholders = ', '.join(['?' for _ in forecast_data])
        query = f"INSERT INTO Forecast ({columns}) VALUES ({placeholders})"

        return self.execute_update(query, tuple(forecast_data.values()))

    def bulk_insert_forecast(self, forecast_list):
        """Inserisce multipli record di forecast"""
        for forecast in forecast_list:
            self.insert_forecast(forecast)

    # === SKILLS ===

    def get_skills(self):
        """Recupera tutte le skill"""
        query = "SELECT * FROM Skills ORDER BY Codice_Skill"
        return self.execute_query(query)

    def insert_skill(self, skill_data):
        """Inserisce una nuova skill"""
        columns = ', '.join(skill_data.keys())
        placeholders = ', '.join(['?' for _ in skill_data])
        query = f"INSERT INTO Skills ({columns}) VALUES ({placeholders})"

        return self.execute_update(query, tuple(skill_data.values()))

    # === UTILITY ===

    def get_dataframe(self, table_name, filters=None):
        """Ritorna una tabella come pandas DataFrame"""
        query = f"SELECT * FROM {table_name}"
        params = None

        if filters:
            where_clause = ' AND '.join([f"{k} = ?" for k in filters.keys()])
            query += f" WHERE {where_clause}"
            params = tuple(filters.values())

        if not self.conn:
            self.connect()

        return pd.read_sql_query(query, self.conn, params=params)

    def __enter__(self):
        """Context manager entry"""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()
