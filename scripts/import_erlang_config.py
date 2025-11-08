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
        print(f"[ERROR] File non trovato: {excel_file}")
        return False

    # Leggi Excel
    try:
        df = pd.read_excel(excel_file, sheet_name='Erlang_Config')
        print(f"[OK] File Excel letto: {len(df)} righe\n")
    except Exception as e:
        print(f"[ERROR] Errore lettura file Excel: {e}")
        print("Assicurarsi che esista sheet 'Erlang_Config'")
        return False

    # Verifica colonne obbligatorie
    required_cols = [
        'Skill', 'Tipo_Canale', 'AHT_Seconds', 'Concurrency', 'Shrinkage'
    ]
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
                tipo_canale = str(row.get('Tipo_Canale', 'Voice')).strip()
                aht_seconds = int(row['AHT_Seconds'])
                concurrency = int(row.get('Concurrency', 1)) if pd.notna(row.get('Concurrency')) else 1
                shrinkage = float(row['Shrinkage'])

                # Service Level (per Voice/Email)
                sl_target = float(row.get('Service_Level_Target', 0.80)) if pd.notna(row.get('Service_Level_Target')) else 0.80
                sl_seconds = int(row.get('Service_Level_Seconds', 20)) if pd.notna(row.get('Service_Level_Seconds')) else 20

                # ASA (per Chat)
                asa_seconds = int(row.get('ASA_Target_Seconds', 60)) if pd.notna(row.get('ASA_Target_Seconds')) else 60

                # Campi opzionali
                tempo_pausa = int(row.get('Tempo_Pausa_Minuti', 0)) if pd.notna(row.get('Tempo_Pausa_Minuti')) else 0
                occupancy = float(row.get('Occupancy_Target', 0.85)) if pd.notna(row.get('Occupancy_Target')) else 0.85
                interval = int(row.get('Interval_Minutes', 30)) if pd.notna(row.get('Interval_Minutes')) else 30
                note = str(row.get('Note', '')).strip() if pd.notna(row.get('Note')) else None

                # Validazioni
                if aht_seconds <= 0:
                    print(f"  [WARN] Riga {idx+2}: AHT deve essere > 0, skip")
                    skipped += 1
                    continue

                if not (0 <= shrinkage <= 1):
                    print(f"  [WARN] Riga {idx+2}: Shrinkage deve essere tra 0 e 1, skip")
                    skipped += 1
                    continue

                if not (0 <= sl_target <= 1):
                    print(f"  [WARN] Riga {idx+2}: Service Level Target deve essere tra 0 e 1, skip")
                    skipped += 1
                    continue

                if concurrency < 1:
                    print(f"  [WARN] Riga {idx+2}: Concurrency deve essere almeno 1, skip")
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
                        SET Tipo_Canale = ?, AHT_Seconds = ?, Concurrency = ?,
                            Tempo_Pausa_Minuti = ?, Shrinkage = ?,
                            Service_Level_Target = ?, Service_Level_Seconds = ?,
                            ASA_Target_Seconds = ?, Occupancy_Target = ?,
                            Interval_Minutes = ?, Note = ?
                        WHERE Skill = ?
                    """
                    db_manager.execute_update(query, (
                        tipo_canale, aht_seconds, concurrency,
                        tempo_pausa, shrinkage,
                        sl_target, sl_seconds, asa_seconds,
                        occupancy, interval, note, skill
                    ))

                    print(f"  [UPD] '{skill}': Configurazione aggiornata")
                    if tipo_canale == 'Chat':
                        print(f"      {tipo_canale}, AHT={aht_seconds}s, Concurr={concurrency}, Shrinkage={shrinkage*100}%, ASA={asa_seconds}s")
                    else:
                        print(f"      {tipo_canale}, AHT={aht_seconds}s, Shrinkage={shrinkage*100}%, SL={sl_target*100}%/{sl_seconds}s")
                    updated += 1

                else:
                    # Insert nuova configurazione
                    query = """
                        INSERT INTO Erlang_Config (
                            Skill, Tipo_Canale, AHT_Seconds, Concurrency,
                            Tempo_Pausa_Minuti, Shrinkage,
                            Service_Level_Target, Service_Level_Seconds,
                            ASA_Target_Seconds, Occupancy_Target,
                            Interval_Minutes, Note
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """
                    db_manager.execute_update(query, (
                        skill, tipo_canale, aht_seconds, concurrency,
                        tempo_pausa, shrinkage,
                        sl_target, sl_seconds, asa_seconds,
                        occupancy, interval, note
                    ))

                    print(f"  [OK] '{skill}': Nuova configurazione")
                    if tipo_canale == 'Chat':
                        print(f"      {tipo_canale}, AHT={aht_seconds}s, Concurr={concurrency}, Shrinkage={shrinkage*100}%, ASA={asa_seconds}s")
                    else:
                        print(f"      {tipo_canale}, AHT={aht_seconds}s, Shrinkage={shrinkage*100}%, SL={sl_target*100}%/{sl_seconds}s")
                    imported += 1

            except ValueError as e:
                print(f"  [ERROR] Riga {idx+2}: Valore numerico invalido - {e}")
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
        print(f"[OK] Importate (nuove):     {imported}")
        print(f"[UPD] Aggiornate:           {updated}")
        print(f"[SKIP] Saltate:             {skipped}")
        print(f"[ERROR] Errori:             {errors}")

        total_configs = config_esistenti - updated + imported
        print(f"[INFO] Totale configurazioni: {total_configs}")
        print(f"{'='*70}\n")

        db_manager.close()
        return errors == 0

    except Exception as e:
        print(f"[ERROR] Errore database: {e}")
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
            SELECT Skill, Tipo_Canale, AHT_Seconds, Concurrency,
                   Shrinkage, Service_Level_Target, Service_Level_Seconds,
                   ASA_Target_Seconds, Occupancy_Target, Interval_Minutes
            FROM Erlang_Config
            ORDER BY Tipo_Canale, Skill
        """)

        if not configs:
            print("Nessuna configurazione trovata\n")
            return

        print(f"{'Skill':<28} {'Canale':<8} {'AHT':>6} {'Conc':>5} {'Shr%':>5} {'SL%/ASA':>9} {'Occ%':>5} {'Int':>5}")
        print(f"{'-'*80}")

        for cfg in configs:
            skill, canale, aht, conc, shr, slt, sls, asa, occ, interval = cfg
            if canale == 'Chat':
                target_display = f"ASA:{asa}s"
            else:
                target_display = f"{slt*100:.0f}%/{sls}s"
            print(f"{skill:<28} {canale:<8} {aht:>5}s {conc:>5} {shr*100:>4.0f}% {target_display:>9} {occ*100:>4.0f}% {interval:>4}m")

        print(f"\nTotale: {len(configs)} configurazioni")
        print(f"{'='*70}\n")

        db_manager.close()

    except Exception as e:
        print(f"[ERROR] Errore: {e}")


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Uso: python import_erlang_config.py <file_excel> [--list]")
        print("\nEsempio:")
        print("  python import_erlang_config.py template_erlang_config.xlsx")
        print("\nPer visualizzare configurazioni attuali:")
        print("  python import_erlang_config.py --list")
        print("\nIl file Excel deve contenere sheet 'Erlang_Config' con colonne:")
        print("  - Skill (obbligatorio)")
        print("  - Tipo_Canale (obbligatorio: Voice/Chat/Email)")
        print("  - AHT_Seconds (obbligatorio)")
        print("  - Concurrency (obbligatorio, ≥1, tipicamente >1 per Chat)")
        print("  - Shrinkage (obbligatorio, 0-1)")
        print("  - Service_Level_Target (opzionale, 0-1, per Voice/Email)")
        print("  - Service_Level_Seconds (opzionale, per Voice/Email)")
        print("  - ASA_Target_Seconds (opzionale, per Chat)")
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
        print(f"[ERROR] File non trovato: {excel_file}")
        sys.exit(1)

    success = import_erlang_config(excel_file, db_path)

    # Mostra configurazioni finali
    if success:
        list_current_configs(db_path)

    sys.exit(0 if success else 1)
