"""
Script per popolare il database con dati di test
"""
import sys
import os
from datetime import datetime, time, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from database.db_creator import DatabaseCreator
from database.db_manager import DatabaseManager


def populate_test_data():
    """Popola il database con dati di esempio"""

    db_path = 'data/operator_overtime.db'

    # Crea database
    print("Creazione database...")
    creator = DatabaseCreator(db_path)
    creator.create_database()

    # Connetti
    db_manager = DatabaseManager(db_path)
    db_manager.connect()

    print("Inserimento skills...")
    # Inserisci skills
    skills = [
        {'Codice_Skill': 'CUSTOMER_CARE', 'Descrizione': 'Assistenza clienti', 'Produttivita_Default': 8.0},
        {'Codice_Skill': 'BACK_OFFICE', 'Descrizione': 'Back office', 'Produttivita_Default': 12.0},
        {'Codice_Skill': 'TECHNICAL_SUPPORT', 'Descrizione': 'Supporto tecnico', 'Produttivita_Default': 6.0},
    ]

    for skill in skills:
        try:
            db_manager.insert_skill(skill)
        except:
            pass  # Già esistente

    print("Inserimento operatori...")
    # Inserisci operatori di test
    data_oggi = datetime.now()

    operatori = [
        {
            'Nome': 'Mario',
            'Cognome': 'Rossi',
            'ID_SAP': 'EMP001',
            'Tipo_Contratto': 'Full Time',
            'FTE': 1.0,
            'Ore_Settimana': 40.0,
            'ID_Turno': 'T1',
            'Ora_Inizio_Turno': '09:00',
            'Ora_Fine_Turno': '18:00',
            'Ora_Inizio_Turno_Spezzato': None,
            'Ora_Fine_Turno_Spezzato': None,
            'Inizio_Strao_1': None,
            'Fine_Strao_1': None,
            'Inizio_Strao_2': None,
            'Fine_Strao_2': None,
            'Inizio_Strao_3': None,
            'Fine_Strao_3': None,
            'Inizio_Pausa_1': '13:00',
            'Fine_Pausa_1': '14:00',
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
            'Etichetta_Skill': 'CUSTOMER_CARE',
            'Data_Riferimento': data_oggi.strftime('%Y-%m-%d')
        },
        {
            'Nome': 'Laura',
            'Cognome': 'Bianchi',
            'ID_SAP': 'EMP002',
            'Tipo_Contratto': 'Full Time',
            'FTE': 1.0,
            'Ore_Settimana': 40.0,
            'ID_Turno': 'T1',
            'Ora_Inizio_Turno': '09:00',
            'Ora_Fine_Turno': '18:00',
            'Ora_Inizio_Turno_Spezzato': None,
            'Ora_Fine_Turno_Spezzato': None,
            'Inizio_Strao_1': '18:00',
            'Fine_Strao_1': '20:00',
            'Inizio_Strao_2': None,
            'Fine_Strao_2': None,
            'Inizio_Strao_3': None,
            'Fine_Strao_3': None,
            'Inizio_Pausa_1': '13:00',
            'Fine_Pausa_1': '14:00',
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
            'Etichetta_Skill': 'CUSTOMER_CARE',
            'Data_Riferimento': data_oggi.strftime('%Y-%m-%d')
        },
        {
            'Nome': 'Giuseppe',
            'Cognome': 'Verdi',
            'ID_SAP': 'EMP003',
            'Tipo_Contratto': 'Part Time',
            'FTE': 0.5,
            'Ore_Settimana': 20.0,
            'ID_Turno': 'T2',
            'Ora_Inizio_Turno': '14:00',
            'Ora_Fine_Turno': '18:00',
            'Ora_Inizio_Turno_Spezzato': None,
            'Ora_Fine_Turno_Spezzato': None,
            'Inizio_Strao_1': None,
            'Fine_Strao_1': None,
            'Inizio_Strao_2': None,
            'Fine_Strao_2': None,
            'Inizio_Strao_3': None,
            'Fine_Strao_3': None,
            'Inizio_Pausa_1': None,
            'Fine_Pausa_1': None,
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
            'Etichetta_Skill': 'BACK_OFFICE',
            'Data_Riferimento': data_oggi.strftime('%Y-%m-%d')
        },
        {
            'Nome': 'Anna',
            'Cognome': 'Neri',
            'ID_SAP': 'EMP004',
            'Tipo_Contratto': 'Full Time',
            'FTE': 1.0,
            'Ore_Settimana': 40.0,
            'ID_Turno': 'T3',
            'Ora_Inizio_Turno': '08:00',
            'Ora_Fine_Turno': '13:00',
            'Ora_Inizio_Turno_Spezzato': '14:00',
            'Ora_Fine_Turno_Spezzato': '17:00',
            'Inizio_Strao_1': None,
            'Fine_Strao_1': None,
            'Inizio_Strao_2': None,
            'Fine_Strao_2': None,
            'Inizio_Strao_3': None,
            'Fine_Strao_3': None,
            'Inizio_Pausa_1': '10:00',
            'Fine_Pausa_1': '10:15',
            'Inizio_Pausa_2': '15:00',
            'Fine_Pausa_2': '15:15',
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
            'Etichetta_Skill': 'TECHNICAL_SUPPORT',
            'Data_Riferimento': data_oggi.strftime('%Y-%m-%d')
        },
        {
            'Nome': 'Paolo',
            'Cognome': 'Gialli',
            'ID_SAP': 'EMP005',
            'Tipo_Contratto': 'Full Time',
            'FTE': 1.0,
            'Ore_Settimana': 40.0,
            'ID_Turno': 'T1',
            'Ora_Inizio_Turno': '09:00',
            'Ora_Fine_Turno': '18:00',
            'Ora_Inizio_Turno_Spezzato': None,
            'Ora_Fine_Turno_Spezzato': None,
            'Inizio_Strao_1': None,
            'Fine_Strao_1': None,
            'Inizio_Strao_2': None,
            'Fine_Strao_2': None,
            'Inizio_Strao_3': None,
            'Fine_Strao_3': None,
            'Inizio_Pausa_1': '12:30',
            'Fine_Pausa_1': '13:30',
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
            'Etichetta_Skill': 'CUSTOMER_CARE',
            'Data_Riferimento': data_oggi.strftime('%Y-%m-%d')
        }
    ]

    for op in operatori:
        db_manager.insert_operatore(op)

    print("Inserimento cambio skill...")
    # Inserisci un cambio skill di esempio
    cambio_skill = {
        'ID_SAP': 'EMP001',
        'Data_Riferimento': data_oggi.strftime('%Y-%m-%d'),
        'Ora_Inizio': '15:00',
        'Ora_Fine': '16:00',
        'Skill_Temporaneo': 'BACK_OFFICE',
        'Note': 'Supporto temporaneo al back office'
    }
    db_manager.insert_cambio_skill(cambio_skill)

    print("Inserimento forecast...")
    # Inserisci forecast di esempio
    forecast_data = []
    start_hour = 9
    end_hour = 18

    for hour in range(start_hour, end_hour + 1):
        for minute in [0, 15, 30, 45]:
            fascia = datetime.combine(data_oggi.date(), time(hour, minute))

            # Volumi più alti nelle ore centrali
            if 10 <= hour <= 16:
                volumi = 80
            else:
                volumi = 50

            for skill in ['CUSTOMER_CARE', 'BACK_OFFICE', 'TECHNICAL_SUPPORT']:
                if skill == 'CUSTOMER_CARE':
                    prod = 8.0
                elif skill == 'BACK_OFFICE':
                    prod = 12.0
                else:
                    prod = 6.0

                fte_richiesti = volumi / prod / 4  # Diviso 4 perché è ogni 15 min

                forecast_data.append({
                    'Data_Riferimento': data_oggi.strftime('%Y-%m-%d'),
                    'Fascia_Oraria': fascia.strftime('%Y-%m-%d %H:%M:%S'),
                    'Skill': skill,
                    'Volumi_Attesi': volumi,
                    'Produttivita_Target': prod,
                    'FTE_Richiesti': fte_richiesti
                })

    db_manager.bulk_insert_forecast(forecast_data)

    db_manager.close()

    print(f"\n✓ Database popolato con successo!")
    print(f"  - {len(skills)} skills")
    print(f"  - {len(operatori)} operatori")
    print(f"  - {len(forecast_data)} record forecast")
    print(f"\nDatabase: {db_path}")


if __name__ == '__main__':
    populate_test_data()
