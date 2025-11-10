#!/usr/bin/env python3
"""
Crea un database SQLite vuoto con tutte le tabelle necessarie
"""
import sqlite3
import os

def create_database():
    db_path = 'operator_overtime.db'

    # Rimuovi database esistente se vuoto
    if os.path.exists(db_path):
        size = os.path.getsize(db_path)
        if size == 0:
            os.remove(db_path)
            print(f"Rimosso database vuoto esistente")

    print(f"Creazione database: {db_path}")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Stesse tabelle ma per SQLite
    print("Creazione tabella Anagrafica_Operatori...")
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

    print("Creazione tabella Cambio_Skill...")
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

    print("Creazione tabella Forecast...")
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

    print("Creazione tabella Skills...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Skills (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            Codice_Skill TEXT UNIQUE NOT NULL,
            Descrizione TEXT,
            Produttivita_Default REAL
        )
    """)

    print("Creazione tabella Turni...")
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

    print("Creazione tabella Giustificativi...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Giustificativi (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            Codice_Giustificativo TEXT UNIQUE NOT NULL,
            Descrizione TEXT,
            Tipologia TEXT,
            Note TEXT
        )
    """)

    print("Creazione tabella Erlang_Config...")
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

    print("Creazione tabella Storico_Turni...")
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

    print()
    print(f"✓ Database creato con successo!")
    print(f"  Path: {os.path.abspath(db_path)}")
    print(f"  Dimensione: {os.path.getsize(db_path)} byte")
    print()
    print("PROSSIMI PASSI:")
    print("1. Importa i dati degli operatori usando uno degli script di import:")
    print("   - scripts/import_excel_turni.py")
    print("   - scripts/import_completo.py")
    print("2. Configura i giustificativi: scripts/import_giustificativi.py")
    print("3. Importa il forecast: scripts/import_forecast.py")

if __name__ == '__main__':
    create_database()
