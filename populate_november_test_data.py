#!/usr/bin/env python3
"""
Popola il database con dati di test per novembre 10-16, 2024
"""
import sys
import os
import sqlite3
from datetime import datetime, timedelta

def populate_november_data():
    """Popola con operatori per novembre 10-16"""

    db_path = 'data/operator_overtime.db'

    print(f"Popolamento database: {db_path}")
    print(f"Periodo: 10-16 novembre 2024")
    print()

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Date novembre 10-16, 2024
    data_inizio = datetime(2024, 11, 10)
    data_fine = datetime(2024, 11, 16)

    # Operatori di esempio
    operatori_template = [
        {
            'Nome': 'Mario',
            'Cognome': 'Rossi',
            'ID_SAP': 'EMP001',
            'Tipo_Contratto': 'Full Time',
            'FTE': 1.0,
            'Ore_Settimana': 40.0,
            'ID_Turno': 'T1',
            'Etichetta_Skill': 'Customer Care',
            'Ora_Inizio_Turno': '09:00',
            'Ora_Fine_Turno': '18:00',
            'Inizio_Pausa_1': '13:00',
            'Fine_Pausa_1': '14:00',
            'Inizio_Strao_1': '18:00',
            'Fine_Strao_1': '19:00',
        },
        {
            'Nome': 'Laura',
            'Cognome': 'Bianchi',
            'ID_SAP': 'EMP002',
            'Tipo_Contratto': 'Full Time',
            'FTE': 1.0,
            'Ore_Settimana': 40.0,
            'ID_Turno': 'T2',
            'Etichetta_Skill': 'Customer Care',
            'Ora_Inizio_Turno': '10:00',
            'Ora_Fine_Turno': '19:00',
            'Inizio_Pausa_1': '14:00',
            'Fine_Pausa_1': '15:00',
        },
        {
            'Nome': 'Giuseppe',
            'Cognome': 'Verdi',
            'ID_SAP': 'EMP003',
            'Tipo_Contratto': 'Full Time',
            'FTE': 1.0,
            'Ore_Settimana': 40.0,
            'ID_Turno': 'T3',
            'Etichetta_Skill': 'Back Office',
            'Ora_Inizio_Turno': '08:00',
            'Ora_Fine_Turno': '17:00',
            'Inizio_Pausa_1': '12:00',
            'Fine_Pausa_1': '13:00',
            'Inizio_Strao_1': '17:00',
            'Fine_Strao_1': '18:30',
        },
        {
            'Nome': 'Anna',
            'Cognome': 'Neri',
            'ID_SAP': 'EMP004',
            'Tipo_Contratto': 'Part Time',
            'FTE': 0.5,
            'Ore_Settimana': 20.0,
            'ID_Turno': 'T4',
            'Etichetta_Skill': 'Technical Support',
            'Ora_Inizio_Turno': '09:00',
            'Ora_Fine_Turno': '13:00',
            'Inizio_Pausa_1': '11:00',
            'Fine_Pausa_1': '11:30',
        },
        {
            'Nome': 'Francesco',
            'Cognome': 'Gialli',
            'ID_SAP': 'EMP005',
            'Tipo_Contratto': 'Full Time',
            'FTE': 1.0,
            'Ore_Settimana': 40.0,
            'ID_Turno': 'T5',
            'Etichetta_Skill': 'Customer Care',
            'Ora_Inizio_Turno': '14:00',
            'Ora_Fine_Turno': '22:00',
            'Inizio_Pausa_1': '18:00',
            'Fine_Pausa_1': '19:00',
        }
    ]

    # Per ogni giorno
    current_date = data_inizio
    total_inserted = 0

    while current_date <= data_fine:
        data_str = current_date.strftime('%Y-%m-%d')
        giorno_settimana = current_date.weekday()  # 0=lunedì, 6=domenica

        print(f"Inserimento operatori per {data_str} ({current_date.strftime('%A')})")

        for op_template in operatori_template:
            # Crea record operatore per questa data
            operatore_data = {
                'Nome': op_template['Nome'],
                'Cognome': op_template['Cognome'],
                'ID_SAP': op_template['ID_SAP'],
                'Tipo_Contratto': op_template['Tipo_Contratto'],
                'FTE': op_template['FTE'],
                'Ore_Settimana': op_template['Ore_Settimana'],
                'ID_Turno': op_template['ID_Turno'],
                'Etichetta_Skill': op_template['Etichetta_Skill'],
                'Data_Riferimento': data_str,
                'Postazione': None,
                'Ora_Inizio_Turno_Spezzato': None,
                'Ora_Fine_Turno_Spezzato': None,
                'Inizio_Strao_2': None,
                'Fine_Strao_2': None,
                'Inizio_Strao_3': None,
                'Fine_Strao_3': None,
                'Inizio_Pausa_2': None,
                'Fine_Pausa_2': None,
                'Inizio_Pausa_3': None,
                'Fine_Pausa_3': None,
                'Inizio_Pausa_4': None,
                'Fine_Pausa_4': None,
                'Inizio_Pausa_5': None,
                'Fine_Pausa_5': None,
                'Tipo_Giust_1': None,
                'Inizio_Giust_1': None,
                'Fine_Giust_1': None,
                'Tipo_Giust_2': None,
                'Inizio_Giust_2': None,
                'Fine_Giust_2': None,
                'Tipo_Giust_3': None,
                'Inizio_Giust_3': None,
                'Fine_Giust_3': None,
                'Tipo_Giust_4': None,
                'Inizio_Giust_4': None,
                'Fine_Giust_4': None,
                'Tipo_Giust_5': None,
                'Inizio_Giust_5': None,
                'Fine_Giust_5': None,
            }

            # Riposo domenicale (domenica = giorno 6)
            if giorno_settimana == 6:
                operatore_data['Ora_Inizio_Turno'] = '00:00'
                operatore_data['Ora_Fine_Turno'] = '00:00'
                operatore_data['Inizio_Pausa_1'] = None
                operatore_data['Fine_Pausa_1'] = None
                operatore_data['Inizio_Strao_1'] = None
                operatore_data['Fine_Strao_1'] = None
            else:
                # Turno normale
                operatore_data['Ora_Inizio_Turno'] = op_template.get('Ora_Inizio_Turno')
                operatore_data['Ora_Fine_Turno'] = op_template.get('Ora_Fine_Turno')
                operatore_data['Inizio_Pausa_1'] = op_template.get('Inizio_Pausa_1')
                operatore_data['Fine_Pausa_1'] = op_template.get('Fine_Pausa_1')
                operatore_data['Inizio_Strao_1'] = op_template.get('Inizio_Strao_1')
                operatore_data['Fine_Strao_1'] = op_template.get('Fine_Strao_1')

                # Aggiungi qualche giustificativo casuale
                if op_template['ID_SAP'] == 'EMP002' and giorno_settimana == 1:  # Martedì
                    operatore_data['Tipo_Giust_1'] = 'Ferie'
                    operatore_data['Inizio_Giust_1'] = '09:00'
                    operatore_data['Fine_Giust_1'] = '18:00'
                    operatore_data['Ora_Inizio_Turno'] = '00:00'
                    operatore_data['Ora_Fine_Turno'] = '00:00'

                if op_template['ID_SAP'] == 'EMP004' and giorno_settimana == 3:  # Giovedì
                    operatore_data['Tipo_Giust_1'] = 'Permesso'
                    operatore_data['Inizio_Giust_1'] = '09:00'
                    operatore_data['Fine_Giust_1'] = '13:00'
                    operatore_data['Ora_Inizio_Turno'] = '00:00'
                    operatore_data['Ora_Fine_Turno'] = '00:00'

            try:
                # Insert usando SQLite direttamente
                columns = ', '.join(operatore_data.keys())
                placeholders = ', '.join(['?' for _ in operatore_data])
                query = f"INSERT INTO Anagrafica_Operatori ({columns}) VALUES ({placeholders})"

                cursor.execute(query, tuple(operatore_data.values()))
                total_inserted += 1
            except Exception as e:
                print(f"  ⚠️  Errore inserimento {op_template['Cognome']}: {e}")

        current_date += timedelta(days=1)

    conn.commit()
    conn.close()

    print()
    print(f"✓ Completato! Inseriti {total_inserted} record")
    print()
    print("Puoi ora:")
    print("1. Eseguire: python diagnose_database.py")
    print("2. Avviare l'app Matrici e generare il report per 10-16 novembre")

if __name__ == '__main__':
    populate_november_data()
