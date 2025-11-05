"""
Script per ottimizzare database Access per uso multi-utente
"""
import pyodbc
import os
import sys


def optimize_access_for_multiuser(db_path):
    """
    Ottimizza impostazioni Access per uso multi-utente su rete

    NOTA: Questo script richiede che Access sia installato su questa macchina
    """

    print(f"Ottimizzazione database Access: {db_path}")
    print("="*60)

    if not os.path.exists(db_path):
        print(f"✗ Database non trovato: {db_path}")
        return False

    try:
        # Connessione
        conn_str = (
            r'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};'
            f'DBQ={os.path.abspath(db_path)};'
        )

        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()

        print("✓ Connessione al database riuscita")

        # Verifica tabelle esistenti
        tables = cursor.tables(tableType='TABLE').fetchall()
        table_names = [table.table_name for table in tables if not table.table_name.startswith('MSys')]

        print(f"✓ Tabelle trovate: {len(table_names)}")
        for table_name in table_names:
            print(f"  - {table_name}")

        # Crea indici per performance multi-utente
        print("\n Creazione indici per performance...")

        indices = [
            ("IX_Anagrafica_Data_SAP", "Anagrafica_Operatori", ["Data_Riferimento", "ID_SAP"]),
            ("IX_Anagrafica_Skill", "Anagrafica_Operatori", ["Etichetta_Skill"]),
            ("IX_CambioSkill_Date", "Cambio_Skill", ["Data_Riferimento", "ID_SAP"]),
            ("IX_Forecast_DateTime", "Forecast", ["Data_Riferimento", "Fascia_Oraria"]),
        ]

        for index_name, table_name, columns in indices:
            try:
                # Verifica se tabella esiste
                if table_name not in table_names:
                    print(f"  ⊘ Tabella {table_name} non trovata, skip indice {index_name}")
                    continue

                # Prova a creare indice
                columns_str = ', '.join(columns)
                sql = f"CREATE INDEX {index_name} ON {table_name} ({columns_str})"
                cursor.execute(sql)
                print(f"  ✓ Indice {index_name} creato")
            except pyodbc.Error as e:
                if 'already exists' in str(e).lower():
                    print(f"  • Indice {index_name} già esistente")
                else:
                    print(f"  ⚠ Warning indice {index_name}: {e}")

        # Aggiungi campo timestamp per tracking modifiche (se non esiste)
        print("\n Aggiunta campi timestamp...")

        for table_name in ['Anagrafica_Operatori', 'Cambio_Skill', 'Forecast']:
            if table_name in table_names:
                try:
                    # Verifica se campo esiste
                    cursor.execute(f"SELECT LastModified FROM {table_name}")
                    print(f"  • Campo LastModified già presente in {table_name}")
                except:
                    # Aggiungi campo
                    try:
                        cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN LastModified DATETIME")
                        cursor.execute(f"UPDATE {table_name} SET LastModified = Now()")
                        print(f"  ✓ Campo LastModified aggiunto a {table_name}")
                    except pyodbc.Error as e:
                        print(f"  ⚠ Warning {table_name}: {e}")

        conn.commit()
        conn.close()

        print("\n" + "="*60)
        print("✓ OTTIMIZZAZIONE COMPLETATA CON SUCCESSO!")
        print("="*60)
        print("\nIl database è ora ottimizzato per uso multi-utente.")
        print("Raccomandazioni:")
        print("- Usa percorso UNC (\\\\server\\share\\file.accdb)")
        print("- Compatta database settimanalmente")
        print("- Backup giornaliero automatico")
        print("- Max 10 utenti simultanei consigliati")

        return True

    except pyodbc.Error as e:
        print(f"\n✗ ERRORE durante ottimizzazione: {e}")
        print("\nPossibili cause:")
        print("- Access Database Engine non installato")
        print("- Database aperto da altro processo")
        print("- Permessi insufficienti sul file")
        return False


def compact_and_repair(db_path):
    """
    Compatta e ripara database Access

    NOTA: Richiede Access installato
    """
    print(f"\nCompattazione database: {db_path}")
    print("-"*60)

    try:
        import win32com.client

        # Crea backup prima
        backup_path = db_path.replace('.accdb', '_backup.accdb')
        if os.path.exists(db_path):
            import shutil
            shutil.copy2(db_path, backup_path)
            print(f"✓ Backup creato: {backup_path}")

        # Compatta usando Access automation
        access = win32com.client.Dispatch("Access.Application")

        temp_path = db_path.replace('.accdb', '_temp.accdb')

        # Compact
        access.CompactRepair(
            SourceFile=os.path.abspath(db_path),
            DestinationFile=os.path.abspath(temp_path),
            LogFile=False
        )

        access.Quit()

        # Sostituisci originale con compattato
        if os.path.exists(temp_path):
            os.remove(db_path)
            os.rename(temp_path, db_path)
            print("✓ Database compattato con successo")

            # Statistiche
            original_size = os.path.getsize(backup_path) / 1024 / 1024
            new_size = os.path.getsize(db_path) / 1024 / 1024
            saved = original_size - new_size

            print(f"\nStatistiche:")
            print(f"  Dimensione originale: {original_size:.2f} MB")
            print(f"  Dimensione compattata: {new_size:.2f} MB")
            print(f"  Spazio risparmiato: {saved:.2f} MB ({saved/original_size*100:.1f}%)")

            return True
        else:
            print("✗ Compattazione fallita: file temp non creato")
            return False

    except ImportError:
        print("✗ Libreria win32com non trovata")
        print("Installa con: pip install pywin32")
        return False
    except Exception as e:
        print(f"✗ Errore durante compattazione: {e}")
        return False


def main():
    """Main"""
    print("="*60)
    print("MATRICI - Ottimizzazione Database Access Multi-Utente")
    print("="*60)
    print()

    # Trova database
    db_path = 'data/operator_overtime.accdb'

    if len(sys.argv) > 1:
        db_path = sys.argv[1]

    if not os.path.exists(db_path):
        # Prova percorso alternativo
        db_path = os.path.join(os.path.dirname(__file__), '..', db_path)

    if not os.path.exists(db_path):
        print(f"✗ Database non trovato: {db_path}")
        print("\nUso: python optimize_access_multiuser.py [path/to/database.accdb]")
        return

    print(f"Database: {os.path.abspath(db_path)}")
    print()

    # Menu
    print("Operazioni disponibili:")
    print("1. Ottimizza per multi-utente (indici, timestamp)")
    print("2. Compatta e ripara database")
    print("3. Entrambe")
    print()

    choice = input("Scegli operazione (1-3): ").strip()

    if choice == '1':
        optimize_access_for_multiuser(db_path)
    elif choice == '2':
        compact_and_repair(db_path)
    elif choice == '3':
        if optimize_access_for_multiuser(db_path):
            print("\n" + "="*60)
            compact_and_repair(db_path)
    else:
        print("Scelta non valida")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nOperazione interrotta dall'utente")
    except Exception as e:
        print(f"\n\n✗ Errore imprevisto: {e}")
        import traceback
        traceback.print_exc()
