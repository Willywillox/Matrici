"""
Script per importare forecast volumi da file Excel

Il file Excel deve avere le seguenti colonne:
- Data_Riferimento: Data in formato YYYY-MM-DD
- Fascia_Oraria: Ora in formato HH:MM
- Skill: Codice skill/coda
- Volumi_Attesi: Numero contatti/chiamate previsti
- Produttivita_Target: Produttività target (opzionale, default 1.0)
- Note: Annotazioni (opzionale)
"""

import pandas as pd
import sys
import os
from pathlib import Path
from datetime import datetime

# Aggiungi path per import moduli
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from database.db_manager import DatabaseManager


def import_forecast(excel_file, db_path='data/operator_overtime.db', replace_existing=False):
    """
    Importa forecast da Excel nel database

    Args:
        excel_file: Path al file Excel
        db_path: Path al database
        replace_existing: Se True, sostituisce forecast esistenti per la stessa data

    Returns:
        True se successo, False altrimenti
    """

    print(f"\n{'='*70}")
    print(f"  IMPORT FORECAST VOLUMI")
    print(f"{'='*70}\n")
    print(f"File Excel: {excel_file}")
    print(f"Database: {db_path}")
    print(f"Modalità: {'SOSTITUZIONE' if replace_existing else 'APPEND'}\n")

    # Verifica file
    if not Path(excel_file).exists():
        print(f"[ERROR] File non trovato: {excel_file}")
        return False

    # Leggi Excel
    try:
        df = pd.read_excel(excel_file, sheet_name='Forecast')
        print(f"[OK] File Excel letto: {len(df)} righe\n")
    except Exception as e:
        print(f"[ERROR] Errore lettura file Excel: {e}")
        print("Assicurarsi che esista sheet 'Forecast'")
        return False

    # Verifica colonne obbligatorie
    required_cols = ['Data_Riferimento', 'Fascia_Oraria', 'Skill', 'Volumi_Attesi']
    missing_cols = [col for col in required_cols if col not in df.columns]

    if missing_cols:
        print(f"[ERROR] Colonne mancanti: {', '.join(missing_cols)}")
        print(f"Colonne trovate: {', '.join(df.columns)}")
        return False

    print(f"Colonne trovate: {', '.join(df.columns)}\n")

    # Connetti database
    db_manager = DatabaseManager(db_path)

    try:
        db_manager.connect()

        # Se replace_existing, elimina forecast esistenti per le date nel file
        if replace_existing:
            date_uniche = df['Data_Riferimento'].unique()
            for data in date_uniche:
                if pd.notna(data):
                    data_str = pd.to_datetime(data).strftime('%Y-%m-%d')
                    db_manager.execute_update(
                        "DELETE FROM Forecast WHERE Data_Riferimento = ?",
                        (data_str,)
                    )
                    print(f"[DEL] Eliminati forecast esistenti per {data_str}")
            print()

        # Conta forecast esistenti
        cursor = db_manager.execute_query(
            "SELECT COUNT(*) as count FROM Forecast"
        )
        forecast_esistenti = cursor[0][0] if cursor else 0
        print(f"Forecast già presenti: {forecast_esistenti}\n")

        # Importa forecast
        imported = 0
        skipped = 0
        errors = 0

        for idx, row in df.iterrows():
            try:
                # Skip righe vuote
                if pd.isna(row.get('Skill')) or str(row['Skill']).strip() == '':
                    continue

                # Parsing dati
                data_rif = pd.to_datetime(row['Data_Riferimento'])
                fascia_oraria_str = str(row['Fascia_Oraria']).strip()

                # Gestisci formati diversi per fascia oraria
                if ':' in fascia_oraria_str:
                    # Formato HH:MM
                    fascia_oraria = datetime.strptime(
                        f"{data_rif.strftime('%Y-%m-%d')} {fascia_oraria_str}",
                        '%Y-%m-%d %H:%M'
                    )
                else:
                    # Assume sia già un datetime
                    fascia_oraria = pd.to_datetime(row['Fascia_Oraria'])

                skill = str(row['Skill']).strip()
                volumi_attesi = int(row['Volumi_Attesi'])

                # Campi opzionali
                produttivita = float(row.get('Produttivita_Target', 1.0)) if pd.notna(row.get('Produttivita_Target')) else 1.0
                note = str(row.get('Note', '')).strip() if pd.notna(row.get('Note')) else None

                # Validazioni
                if volumi_attesi < 0:
                    print(f"  [WARN] Riga {idx+2}: Volumi negativi, skip")
                    skipped += 1
                    continue

                # Verifica se forecast già esiste (stessa data + fascia + skill)
                existing = db_manager.execute_query("""
                    SELECT ID FROM Forecast
                    WHERE Data_Riferimento = ? AND Fascia_Oraria = ? AND Skill = ?
                """, (
                    data_rif.strftime('%Y-%m-%d'),
                    fascia_oraria.strftime('%Y-%m-%d %H:%M:%S'),
                    skill
                ))

                if existing and not replace_existing:
                    skipped += 1
                    continue

                # Insert forecast
                # FTE_Richiesti verrà calcolato da Erlang C, qui lo lasciamo a 0
                query = """
                    INSERT INTO Forecast (
                        Data_Riferimento, Fascia_Oraria, Skill,
                        Volumi_Attesi, Produttivita_Target, FTE_Richiesti
                    ) VALUES (?, ?, ?, ?, ?, ?)
                """

                db_manager.execute_update(query, (
                    data_rif.strftime('%Y-%m-%d'),
                    fascia_oraria.strftime('%Y-%m-%d %H:%M:%S'),
                    skill,
                    volumi_attesi,
                    produttivita,
                    0  # FTE_Richiesti calcolato da Erlang
                ))

                if idx % 50 == 0 and idx > 0:
                    print(f"  ... {idx} righe processate")

                imported += 1

            except ValueError as e:
                print(f"  [ERROR] Riga {idx+2}: Valore non valido - {e}")
                errors += 1
                continue
            except Exception as e:
                print(f"  [ERROR] Riga {idx+2}: Errore - {e}")
                errors += 1
                continue

        # Riepilogo
        print(f"\n{'='*70}")
        print(f"  RIEPILOGO IMPORT")
        print(f"{'='*70}")
        print(f"[OK] Importati:             {imported}")
        print(f"[SKIP] Saltati:             {skipped}")
        print(f"[ERROR] Errori:             {errors}")

        # Conta totale finale
        cursor = db_manager.execute_query(
            "SELECT COUNT(*) as count FROM Forecast"
        )
        totale_forecast = cursor[0][0] if cursor else 0
        print(f"[INFO] Totale forecast:     {totale_forecast}")

        # Mostra riepilogo per data e skill
        print(f"\n{'='*70}")
        print(f"  RIEPILOGO PER DATA E SKILL")
        print(f"{'='*70}\n")

        cursor = db_manager.execute_query("""
            SELECT Data_Riferimento, Skill,
                   COUNT(*) as num_fasce,
                   SUM(Volumi_Attesi) as totale_volumi
            FROM Forecast
            GROUP BY Data_Riferimento, Skill
            ORDER BY Data_Riferimento, Skill
        """)

        if cursor:
            print(f"{'Data':<12} {'Skill':<25} {'Fasce':>8} {'Tot.Volumi':>12}")
            print(f"{'-'*70}")
            for row in cursor:
                data, skill, fasce, volumi = row
                print(f"{data:<12} {skill:<25} {fasce:>8} {volumi:>12}")
        else:
            print("Nessun forecast nel database")

        print(f"\n{'='*70}\n")

        db_manager.close()
        return errors == 0

    except Exception as e:
        print(f"[ERROR] Errore database: {e}")
        import traceback
        traceback.print_exc()
        return False


def delete_forecast_by_date(data, db_path='data/operator_overtime.db'):
    """Elimina forecast per una specifica data"""

    print(f"\n{'='*70}")
    print(f"  ELIMINAZIONE FORECAST")
    print(f"{'='*70}\n")
    print(f"Data: {data}")
    print(f"Database: {db_path}\n")

    db_manager = DatabaseManager(db_path)

    try:
        db_manager.connect()

        # Conta quanti ne elimineremo
        cursor = db_manager.execute_query(
            "SELECT COUNT(*) FROM Forecast WHERE Data_Riferimento = ?",
            (data,)
        )
        count = cursor[0][0] if cursor else 0

        if count == 0:
            print(f"Nessun forecast trovato per {data}")
            db_manager.close()
            return True

        # Chiedi conferma
        print(f"[WARN] Verranno eliminati {count} record forecast per {data}")
        conferma = input("Confermare? (s/N): ")

        if conferma.lower() != 's':
            print("Operazione annullata")
            db_manager.close()
            return False

        # Elimina
        db_manager.execute_update(
            "DELETE FROM Forecast WHERE Data_Riferimento = ?",
            (data,)
        )

        print(f"[OK] Eliminati {count} record\n")

        db_manager.close()
        return True

    except Exception as e:
        print(f"[ERROR] Errore: {e}")
        return False


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Uso: python import_forecast.py <file_excel> [--replace] [--delete-date YYYY-MM-DD]")
        print("\nEsempi:")
        print("  python import_forecast.py template_forecast.xlsx")
        print("  python import_forecast.py template_forecast.xlsx --replace")
        print("  python import_forecast.py --delete-date 2025-11-08")
        print("\nOpzioni:")
        print("  --replace       Sostituisce forecast esistenti per le date nel file")
        print("  --delete-date   Elimina tutti i forecast per una data specifica")
        print("\nIl file Excel deve contenere sheet 'Forecast' con colonne:")
        print("  - Data_Riferimento (obbligatorio, YYYY-MM-DD)")
        print("  - Fascia_Oraria (obbligatorio, HH:MM)")
        print("  - Skill (obbligatorio)")
        print("  - Volumi_Attesi (obbligatorio)")
        print("  - Produttivita_Target (opzionale)")
        print("  - Note (opzionale)")
        sys.exit(1)

    # Database path
    db_path = 'data/operator_overtime.db'

    # Modalità delete
    if '--delete-date' in sys.argv:
        idx = sys.argv.index('--delete-date')
        if idx + 1 >= len(sys.argv):
            print("[ERROR] Specificare la data da eliminare")
            sys.exit(1)

        data = sys.argv[idx + 1]
        success = delete_forecast_by_date(data, db_path)
        sys.exit(0 if success else 1)

    # Import da file
    excel_file = sys.argv[1]

    if not os.path.exists(excel_file):
        print(f"[ERROR] File non trovato: {excel_file}")
        sys.exit(1)

    replace = '--replace' in sys.argv

    success = import_forecast(excel_file, db_path, replace)

    sys.exit(0 if success else 1)
