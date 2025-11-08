"""
Script per importare configurazioni Erlang C da file Excel

Il file Excel deve avere le seguenti colonne:
- Skill: Codice skill/coda (UNIQUE)
- AHT_Seconds: Average Handle Time in secondi
- Tempo_Pausa_Minuti: Minuti pausa per ora (opzionale)
- Shrinkage: Percentuale shrinkage (0-1)
- Service_Level_Target: Target Service Level (0-1)
- Service_Level_Seconds: Secondi target risposta
- Occupancy_Target: Target occupancy (0-1)
- Interval_Minutes: Intervallo calcolo (default 30)
- Note: Note/descrizione (opzionale)
"""

import pandas as pd
import sys
import os
from pathlib import Path

# Aggiungi path per import moduli
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from database.db_manager import DatabaseManager


def import_erlang_config(excel_file, db_path='data/operator_overtime.db'):
    """
    Importa configurazioni Erlang C da Excel nel database

    Args:
        excel_file: Path al file Excel
        db_path: Path al database

    Returns:
        True se successo, False altrimenti
    """

    print(f"\n{'='*70}")
    print(f"  IMPORT CONFIGURAZIONE ERLANG C")
    print(f"{'='*70}\n")
    print(f"File Excel: {excel_file}")
    print(f"Database: {db_path}\n")

    # Verifica file
    if not Path(excel_file).exists():
        print(f"❌ File non trovato: {excel_file}")
        return False

    # Leggi Excel
    try:
        df = pd.read_excel(excel_file, sheet_name='Erlang_Config')
        print(f"✓ File Excel letto: {len(df)} righe\n")
    except Exception as e:
        print(f"❌ Errore lettura file Excel: {e}")
        print("Assicurarsi che esista sheet 'Erlang_Config'")
        return False

    # Verifica colonne obbligatorie
    required_cols = [
        'Skill', 'AHT_Seconds', 'Shrinkage',
        'Service_Level_Target', 'Service_Level_Seconds'
    ]
    missing_cols = [col for col in required_cols if col not in df.columns]

    if missing_cols:
        print(f"❌ Colonne mancanti: {', '.join(missing_cols)}")
        print(f"Colonne trovate: {', '.join(df.columns)}")
        return False

    print(f"Colonne trovate: {', '.join(df.columns)}\n")

    # Connetti database
    db_manager = DatabaseManager(db_path)

    try:
        db_manager.connect()

        # Conta configurazioni esistenti
        cursor = db_manager.execute_query(
            "SELECT COUNT(*) as count FROM Erlang_Config"
        )
        config_esistenti = cursor[0][0] if cursor else 0
        print(f"Configurazioni già presenti: {config_esistenti}\n")

        # Importa configurazioni
        imported = 0
        updated = 0
        skipped = 0
        errors = 0

        for idx, row in df.iterrows():
            try:
                # Skip righe vuote
                if pd.isna(row.get('Skill')) or str(row['Skill']).strip() == '':
                    continue

                skill = str(row['Skill']).strip()
                aht_seconds = int(row['AHT_Seconds'])
                shrinkage = float(row['Shrinkage'])
                sl_target = float(row['Service_Level_Target'])
                sl_seconds = int(row['Service_Level_Seconds'])

                # Campi opzionali
                tempo_pausa = int(row.get('Tempo_Pausa_Minuti', 0)) if pd.notna(row.get('Tempo_Pausa_Minuti')) else 0
                occupancy = float(row.get('Occupancy_Target', 0.85)) if pd.notna(row.get('Occupancy_Target')) else 0.85
                interval = int(row.get('Interval_Minutes', 30)) if pd.notna(row.get('Interval_Minutes')) else 30
                note = str(row.get('Note', '')).strip() if pd.notna(row.get('Note')) else None

                # Validazioni
                if aht_seconds <= 0:
                    print(f"  ⚠️  Riga {idx+2}: AHT deve essere > 0, skip")
                    skipped += 1
                    continue

                if not (0 <= shrinkage <= 1):
                    print(f"  ⚠️  Riga {idx+2}: Shrinkage deve essere tra 0 e 1, skip")
                    skipped += 1
                    continue

                if not (0 <= sl_target <= 1):
                    print(f"  ⚠️  Riga {idx+2}: Service Level Target deve essere tra 0 e 1, skip")
                    skipped += 1
                    continue

                # Verifica se configurazione esiste
                existing = db_manager.execute_query(
                    "SELECT ID FROM Erlang_Config WHERE Skill = ?",
                    (skill,)
                )

                if existing:
                    # Update configurazione esistente
                    query = """
                        UPDATE Erlang_Config
                        SET AHT_Seconds = ?,
                            Tempo_Pausa_Minuti = ?,
                            Shrinkage = ?,
                            Service_Level_Target = ?,
                            Service_Level_Seconds = ?,
                            Occupancy_Target = ?,
                            Interval_Minutes = ?,
                            Note = ?
                        WHERE Skill = ?
                    """
                    db_manager.execute_update(query, (
                        aht_seconds, tempo_pausa, shrinkage,
                        sl_target, sl_seconds, occupancy,
                        interval, note, skill
                    ))

                    print(f"  ↻ '{skill}': Configurazione aggiornata")
                    print(f"      AHT={aht_seconds}s, Shrinkage={shrinkage*100}%, SL={sl_target*100}%/{sl_seconds}s")
                    updated += 1

                else:
                    # Insert nuova configurazione
                    query = """
                        INSERT INTO Erlang_Config (
                            Skill, AHT_Seconds, Tempo_Pausa_Minuti,
                            Shrinkage, Service_Level_Target, Service_Level_Seconds,
                            Occupancy_Target, Interval_Minutes, Note
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """
                    db_manager.execute_update(query, (
                        skill, aht_seconds, tempo_pausa,
                        shrinkage, sl_target, sl_seconds,
                        occupancy, interval, note
                    ))

                    print(f"  ✓ '{skill}': Nuova configurazione")
                    print(f"      AHT={aht_seconds}s, Shrinkage={shrinkage*100}%, SL={sl_target*100}%/{sl_seconds}s")
                    imported += 1

            except ValueError as e:
                print(f"  ❌ Riga {idx+2}: Valore numerico invalido - {e}")
                errors += 1
                continue
            except Exception as e:
                print(f"  ❌ Riga {idx+2}: Errore - {e}")
                errors += 1
                continue

        # Riepilogo
        print(f"\n{'='*70}")
        print(f"  RIEPILOGO IMPORT")
        print(f"{'='*70}")
        print(f"✓ Importate (nuove):     {imported}")
        print(f"↻ Aggiornate:            {updated}")
        print(f"⏭️  Saltate:              {skipped}")
        print(f"❌ Errori:                {errors}")

        total_configs = config_esistenti - updated + imported
        print(f"📊 Totale configurazioni: {total_configs}")
        print(f"{'='*70}\n")

        db_manager.close()
        return errors == 0

    except Exception as e:
        print(f"❌ Errore database: {e}")
        import traceback
        traceback.print_exc()
        return False


def list_current_configs(db_path='data/operator_overtime.db'):
    """Visualizza configurazioni Erlang C attuali"""

    print(f"\n{'='*70}")
    print(f"  CONFIGURAZIONI ERLANG C ATTUALI")
    print(f"{'='*70}\n")

    db_manager = DatabaseManager(db_path)

    try:
        db_manager.connect()

        configs = db_manager.execute_query("""
            SELECT Skill, AHT_Seconds, Shrinkage,
                   Service_Level_Target, Service_Level_Seconds,
                   Occupancy_Target, Interval_Minutes
            FROM Erlang_Config
            ORDER BY Skill
        """)

        if not configs:
            print("Nessuna configurazione trovata\n")
            return

        print(f"{'Skill':<25} {'AHT':>8} {'Shr%':>6} {'SL%':>6} {'SLs':>5} {'Occ%':>6} {'Int':>5}")
        print(f"{'-'*70}")

        for cfg in configs:
            skill, aht, shr, slt, sls, occ, interval = cfg
            print(f"{skill:<25} {aht:>6}s {shr*100:>5.0f}% {slt*100:>5.0f}% {sls:>4}s {occ*100:>5.0f}% {interval:>4}m")

        print(f"\nTotale: {len(configs)} configurazioni")
        print(f"{'='*70}\n")

        db_manager.close()

    except Exception as e:
        print(f"❌ Errore: {e}")


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Uso: python import_erlang_config.py <file_excel> [--list]")
        print("\nEsempio:")
        print("  python import_erlang_config.py template_erlang_config.xlsx")
        print("\nPer visualizzare configurazioni attuali:")
        print("  python import_erlang_config.py --list")
        print("\nIl file Excel deve contenere sheet 'Erlang_Config' con colonne:")
        print("  - Skill (obbligatorio)")
        print("  - AHT_Seconds (obbligatorio)")
        print("  - Shrinkage (obbligatorio, 0-1)")
        print("  - Service_Level_Target (obbligatorio, 0-1)")
        print("  - Service_Level_Seconds (obbligatorio)")
        print("  - Tempo_Pausa_Minuti (opzionale)")
        print("  - Occupancy_Target (opzionale)")
        print("  - Interval_Minutes (opzionale)")
        print("  - Note (opzionale)")
        sys.exit(1)

    # Database path
    db_path = 'data/operator_overtime.db'

    # Modalità list
    if sys.argv[1] == '--list':
        list_current_configs(db_path)
        sys.exit(0)

    # Import da file
    excel_file = sys.argv[1]

    if not os.path.exists(excel_file):
        print(f"❌ File non trovato: {excel_file}")
        sys.exit(1)

    success = import_erlang_config(excel_file, db_path)

    # Mostra configurazioni finali
    if success:
        list_current_configs(db_path)

    sys.exit(0 if success else 1)
