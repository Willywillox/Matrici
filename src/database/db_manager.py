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
        if not data_riferimento:
            return self.execute_query("SELECT * FROM Anagrafica_Operatori")

        # Prova prima con match esatto
        query = "SELECT * FROM Anagrafica_Operatori WHERE Data_Riferimento = ?"
        results = self.execute_query(query, (data_riferimento,))

        if results:
            return results

        # Se non trova risultati, prova con formati alternativi
        # Converte YYYY-MM-DD in altri formati comuni
        try:
            from datetime import datetime
            if isinstance(data_riferimento, str) and '-' in data_riferimento:
                # Parsing della data nel formato YYYY-MM-DD
                dt = datetime.strptime(data_riferimento, '%Y-%m-%d')

                # Formati alternativi da provare
                formati_alt = [
                    dt.strftime('%d/%m/%Y'),  # DD/MM/YYYY
                    dt.strftime('%Y-%m-%d %H:%M:%S'),  # Con timestamp
                    dt.strftime('%d/%m/%Y %H:%M:%S'),  # DD/MM/YYYY con timestamp
                    dt.strftime('%m/%d/%Y'),  # MM/DD/YYYY (formato US)
                ]

                for formato in formati_alt:
                    results = self.execute_query(query, (formato,))
                    if results:
                        print(f"[DEBUG DB] Trovati operatori con formato data: {formato}")
                        return results

                # Se ancora nessun risultato, prova con LIKE per match parziale
                # Questo cattura date con timestamp
                like_query = "SELECT * FROM Anagrafica_Operatori WHERE Data_Riferimento LIKE ?"
                for pattern in [f"{data_riferimento}%", f"%{dt.strftime('%d/%m/%Y')}%"]:
                    results = self.execute_query(like_query, (pattern,))
                    if results:
                        print(f"[DEBUG DB] Trovati operatori con pattern: {pattern}")
                        return results
        except Exception as e:
            print(f"[DEBUG DB] Errore parsing data: {e}")

        print(f"[DEBUG DB] Nessun operatore trovato per data: {data_riferimento}")
        return []

    def get_date_riferimento_list(self):
        """Recupera tutte le date riferimento univoche presenti nel database"""
        query = "SELECT DISTINCT Data_Riferimento FROM Anagrafica_Operatori ORDER BY Data_Riferimento"
        try:
            results = self.execute_query(query)
            return [row[0] if hasattr(row, '__getitem__') else row.Data_Riferimento for row in results]
        except Exception as e:
            print(f"[DEBUG DB] Errore recupero date: {e}")
            return []

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
        # Rimuovi il campo ID da operatore_data se presente (non deve essere aggiornato)
        if 'ID' in operatore_data:
            operatore_data = {k: v for k, v in operatore_data.items() if k != 'ID'}

        # Verifica se stiamo modificando ID_SAP o Data_Riferimento
        if 'ID_SAP' in operatore_data or 'Data_Riferimento' in operatore_data:
            id_sap = operatore_data.get('ID_SAP')
            data_rif = operatore_data.get('Data_Riferimento')

            # Se entrambi sono presenti, verifica che non confliggano con un altro operatore
            if id_sap and data_rif:
                existing = self.execute_query(
                    "SELECT ID FROM Anagrafica_Operatori WHERE ID_SAP = ? AND Data_Riferimento = ? AND ID != ?",
                    (id_sap, data_rif, id_operatore)
                )

                if existing and len(existing) > 0:
                    print(f"[ERROR] Conflitto trovato: ID_SAP={id_sap}, Data={data_rif} già esiste per operatore ID={existing[0][0]}")
                    raise ValueError(
                        f"Esiste già un operatore con ID_SAP='{id_sap}' nella data {data_rif}.\n"
                        f"Non puoi avere due operatori con lo stesso ID_SAP nella stessa data."
                    )

        set_clause = ', '.join([f"{k} = ?" for k in operatore_data.keys()])
        query = f"UPDATE Anagrafica_Operatori SET {set_clause} WHERE ID = ?"

        params = list(operatore_data.values()) + [id_operatore]

        # Debug logging
        print(f"[DEBUG DB] UPDATE query: {query}")
        print(f"[DEBUG DB] Params: {params}")
        print(f"[DEBUG DB] ID_operatore: {id_operatore}")

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
