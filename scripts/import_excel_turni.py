"""
Script per importare anagrafica turni da file Excel

Il file Excel deve avere le seguenti colonne:
- ID_Turno: Codice turno (es: T1, T2, T3, ...)
- Descrizione: Descrizione turno (opzionale)
- Ora_Inizio: Ora inizio turno (formato HH:MM es: 09:00)
- Ora_Fine: Ora fine turno (formato HH:MM es: 18:00)
- Ore_Turno: Ore totali turno (opzionale, calcolato automaticamente se manca)
- Ora_Inizio_Spezzato: Ora inizio turno spezzato (opzionale, formato HH:MM)
- Ora_Fine_Spezzato: Ora fine turno spezzato (opzionale, formato HH:MM)
- Note: Note aggiuntive (opzionale)
"""

import pandas as pd
import sys
import os
from datetime import datetime, timedelta

# Aggiungi path per import moduli
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from database.db_manager import DatabaseManager


def calcola_ore_turno(ora_inizio, ora_fine):
    """Calcola ore turno da orari"""
    try:
        # Parse orari
        if isinstance(ora_inizio, str):
            h_i, m_i = map(int, ora_inizio.split(':'))
        else:
            h_i = ora_inizio.hour
            m_i = ora_inizio.minute

        if isinstance(ora_fine, str):
            h_f, m_f = map(int, ora_fine.split(':'))
        else:
            h_f = ora_fine.hour
            m_f = ora_fine.minute

        # Calcola differenza in ore
        start = h_i + m_i / 60
        end = h_f + m_f / 60

        # Se fine < inizio, attraversa mezzanotte
        if end < start:
            end += 24

        return end - start
    except:
        return None


def import_turni_da_excel(excel_file, db_path='data/operator_overtime.db'):
    """Importa turni da Excel nel database"""

    print(f"\n=== IMPORT TURNI DA EXCEL ===\n")
    print(f"File Excel: {excel_file}")
    print(f"Database: {db_path}\n")

    # Leggi Excel
    try:
        df = pd.read_excel(excel_file)
        print(f"✅ File Excel letto: {len(df)} righe trovate\n")
    except Exception as e:
        print(f"❌ Errore lettura file Excel: {e}")
        return False

    # Verifica colonne obbligatorie
    required_cols = ['ID_Turno', 'Ora_Inizio', 'Ora_Fine']
    missing_cols = [col for col in required_cols if col not in df.columns]

    if missing_cols:
        print(f"❌ Colonne mancanti nel file Excel: {', '.join(missing_cols)}")
        print(f"Colonne trovate: {', '.join(df.columns)}")
        return False

    print(f"Colonne trovate: {', '.join(df.columns)}\n")

    # Connetti database
    db_manager = DatabaseManager(db_path)

    try:
        db_manager.connect()

        # Conta turni esistenti
        cursor = db_manager.execute_query("SELECT COUNT(*) as count FROM Turni")
        turni_esistenti = cursor[0][0] if cursor else 0
        print(f"Turni già presenti nel database: {turni_esistenti}\n")

        # Importa turni
        imported = 0
        skipped = 0
        errors = 0

        for idx, row in df.iterrows():
            try:
                id_turno = str(row['ID_Turno']).strip()
                ora_inizio = str(row['Ora_Inizio']).strip()
                ora_fine = str(row['Ora_Fine']).strip()

                # Campi opzionali
                descrizione = str(row.get('Descrizione', '')).strip() if 'Descrizione' in row and pd.notna(row.get('Descrizione')) else None
                note = str(row.get('Note', '')).strip() if 'Note' in row and pd.notna(row.get('Note')) else None

                # Turno spezzato
                ora_inizio_spezzato = None
                ora_fine_spezzato = None

                if 'Ora_Inizio_Spezzato' in row and pd.notna(row.get('Ora_Inizio_Spezzato')):
                    ora_inizio_spezzato = str(row['Ora_Inizio_Spezzato']).strip()

                if 'Ora_Fine_Spezzato' in row and pd.notna(row.get('Ora_Fine_Spezzato')):
                    ora_fine_spezzato = str(row['Ora_Fine_Spezzato']).strip()

                # Calcola ore turno se non fornite
                ore_turno = None
                if 'Ore_Turno' in row and pd.notna(row.get('Ore_Turno')):
                    ore_turno = float(row['Ore_Turno'])
                else:
                    ore_turno = calcola_ore_turno(ora_inizio, ora_fine)

                # Verifica se turno già esiste
                existing = db_manager.execute_query(
                    "SELECT ID FROM Turni WHERE ID_Turno = ?",
                    (id_turno,)
                )

                if existing:
                    print(f"⏭️  Turno {id_turno} già esistente, skip")
                    skipped += 1
                    continue

                # Insert turno
                query = """
                    INSERT INTO Turni (
                        ID_Turno, Descrizione, Ora_Inizio, Ora_Fine, Ore_Turno,
                        Ora_Inizio_Spezzato, Ora_Fine_Spezzato, Note
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """

                db_manager.execute_update(query, (
                    id_turno,
                    descrizione,
                    ora_inizio,
                    ora_fine,
                    ore_turno,
                    ora_inizio_spezzato,
                    ora_fine_spezzato,
                    note
                ))

                print(f"✅ Turno {id_turno}: {ora_inizio}-{ora_fine} ({ore_turno}h)")
                imported += 1

            except Exception as e:
                print(f"❌ Errore riga {idx + 2}: {e}")
                errors += 1
                continue

        # Riepilogo
        print(f"\n=== RIEPILOGO IMPORT ===")
        print(f"✅ Importati: {imported}")
        print(f"⏭️  Saltati (già esistenti): {skipped}")
        print(f"❌ Errori: {errors}")
        print(f"📊 Totale turni nel database: {turni_esistenti + imported}\n")

        db_manager.close()
        return True

    except Exception as e:
        print(f"❌ Errore database: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Uso: python import_excel_turni.py <file_excel>")
        print("\nEsempio:")
        print("  python import_excel_turni.py turni.xlsx")
        print("\nIl file Excel deve contenere le colonne:")
        print("  - ID_Turno (obbligatorio)")
        print("  - Ora_Inizio (obbligatorio, formato HH:MM)")
        print("  - Ora_Fine (obbligatorio, formato HH:MM)")
        print("  - Descrizione (opzionale)")
        print("  - Ore_Turno (opzionale, calcolato automaticamente)")
        print("  - Ora_Inizio_Spezzato (opzionale, formato HH:MM)")
        print("  - Ora_Fine_Spezzato (opzionale, formato HH:MM)")
        print("  - Note (opzionale)")
        sys.exit(1)

    excel_file = sys.argv[1]

    if not os.path.exists(excel_file):
        print(f"❌ File non trovato: {excel_file}")
        sys.exit(1)

    # Database path (usa config se disponibile)
    db_path = 'data/operator_overtime.db'

    success = import_turni_da_excel(excel_file, db_path)

    sys.exit(0 if success else 1)
