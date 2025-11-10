"""
Script per import giustificativi da Excel

Importa l'anagrafica dei giustificativi (ferie, ROL, malattia, etc.)
con le relative tipologie (macro categorie)
"""

import sys
import os
import pandas as pd
from pathlib import Path

# Aggiungi path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from database.db_manager import DatabaseManager


class GiustificativiImporter:
    """Importatore giustificativi da Excel"""

    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.imported = 0
        self.updated = 0
        self.skipped = 0
        self.errors = []

    def import_from_excel(self, file_path, sheet_name='Giust'):
        """
        Import giustificativi da file Excel

        Args:
            file_path: Percorso file Excel
            sheet_name: Nome dello sheet (default: 'Giust')

        Returns:
            bool: True se import ok, False altrimenti
        """
        print(f"\n{'='*70}")
        print(f"  IMPORT GIUSTIFICATIVI")
        print(f"{'='*70}\n")
        print(f"File: {file_path}")
        print(f"Sheet: {sheet_name}\n")

        # Verifica file
        if not Path(file_path).exists():
            print(f"[ERROR] File non trovato: {file_path}")
            return False

        try:
            # Leggi Excel
            df = pd.read_excel(file_path, sheet_name=sheet_name)
            print(f"[OK] File letto: {len(df)} righe\n")

            # Verifica colonne richieste
            # Accetta sia "Giustificativo" che "Codice_Giustificativo"
            codice_col = None
            if 'Giustificativo' in df.columns:
                codice_col = 'Giustificativo'
            elif 'Codice_Giustificativo' in df.columns:
                codice_col = 'Codice_Giustificativo'

            if not codice_col:
                print("[ERROR] Colonne obbligatorie mancanti!")
                print("Serve almeno la colonna 'Giustificativo' o 'Codice_Giustificativo'")
                return False

            if 'Tipologia' not in df.columns:
                print("[ERROR] Colonna 'Tipologia' mancante!")
                return False

            # Connetti database
            self.db_manager.connect()

            # Processa ogni riga
            for idx, row in df.iterrows():
                row_num = idx + 2  # Excel row (header = 1)

                try:
                    codice = str(row[codice_col]).strip()

                    # Skip righe vuote
                    if not codice or pd.isna(row[codice_col]) or codice.lower() == 'nan':
                        continue

                    tipologia = str(row['Tipologia']).strip() if pd.notna(row['Tipologia']) else None
                    descrizione = str(row.get('Descrizione', '')).strip() if pd.notna(row.get('Descrizione')) else None
                    note = str(row.get('Note', '')).strip() if pd.notna(row.get('Note')) else None

                    # Verifica se giustificativo esiste
                    existing = self.db_manager.execute_query(
                        "SELECT ID FROM Giustificativi WHERE Codice_Giustificativo = ?",
                        (codice,)
                    )

                    if existing:
                        # Update
                        query = """
                            UPDATE Giustificativi
                            SET Descrizione = ?, Tipologia = ?, Note = ?
                            WHERE Codice_Giustificativo = ?
                        """
                        self.db_manager.execute_update(query, (descrizione, tipologia, note, codice))
                        print(f"  [UPD] Riga {row_num}: '{codice}' - Tipologia: {tipologia}")
                        self.updated += 1
                    else:
                        # Insert
                        query = """
                            INSERT INTO Giustificativi (Codice_Giustificativo, Descrizione, Tipologia, Note)
                            VALUES (?, ?, ?, ?)
                        """
                        self.db_manager.execute_update(query, (codice, descrizione, tipologia, note))
                        print(f"  [OK] Riga {row_num}: '{codice}' - Tipologia: {tipologia}")
                        self.imported += 1

                except Exception as e:
                    error_msg = f"Riga {row_num}: {e}"
                    self.errors.append(error_msg)
                    print(f"  [ERROR] {error_msg}")
                    continue

            # Report finale
            print(f"\n{'='*70}")
            print(f"  RIEPILOGO IMPORT GIUSTIFICATIVI")
            print(f"{'='*70}")
            print(f"  [OK] Importati:     {self.imported}")
            print(f"  [UPD] Aggiornati:   {self.updated}")
            print(f"  [ERROR] Errori:     {len(self.errors)}")
            print(f"{'='*70}\n")

            if self.errors:
                print("ERRORI:")
                for err in self.errors[:10]:  # Mostra max 10 errori
                    print(f"  - {err}")
                if len(self.errors) > 10:
                    print(f"  ... e altri {len(self.errors) - 10} errori")
                print()

            return True

        except Exception as e:
            print(f"[ERROR] Errore lettura file Excel: {e}")
            import traceback
            traceback.print_exc()
            return False

        finally:
            self.db_manager.close()


def main():
    """Main function"""
    import argparse

    parser = argparse.ArgumentParser(
        description='Import giustificativi da Excel'
    )
    parser.add_argument('--file', '-f', required=True,
                        help='File Excel da importare')
    parser.add_argument('--sheet', '-s', default='Giust',
                        help='Nome dello sheet (default: Giust)')

    args = parser.parse_args()

    if not Path(args.file).exists():
        print(f"[ERROR] File non trovato: {args.file}")
        return 1

    # Crea importer
    db_manager = DatabaseManager()
    importer = GiustificativiImporter(db_manager)

    # Esegui import
    success = importer.import_from_excel(args.file, sheet_name=args.sheet)

    if not success or len(importer.errors) > 0:
        return 1

    return 0


if __name__ == '__main__':
    sys.exit(main())
