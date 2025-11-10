"""
Script per importare Skills da file Excel

Importa l'anagrafica delle skills/code del contact center

Uso:
    python scripts/import_skills.py --file <file_excel.xlsx> [--sheet Skills]
"""

import sys
import os
from pathlib import Path
import pandas as pd

# Aggiungi path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from database.db_manager import DatabaseManager


class SkillsImporter:
    """Importatore skills da Excel"""

    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.imported = 0
        self.updated = 0
        self.skipped = 0
        self.errors = []

    def import_from_excel(self, file_path, sheet_name='Skills'):
        """
        Import skills da file Excel

        Args:
            file_path: Percorso file Excel
            sheet_name: Nome dello sheet (default: 'Skills')

        Returns:
            bool: True se import ok, False altrimenti
        """
        print(f"\n{'='*70}")
        print(f"  IMPORT SKILLS")
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
            if 'Codice_Skill' not in df.columns:
                print("[ERROR] Colonna obbligatoria 'Codice_Skill' mancante!")
                print(f"Colonne presenti: {df.columns.tolist()}")
                return False

            # Connetti database
            self.db_manager.connect()

            # Processa ogni riga
            for idx, row in df.iterrows():
                row_num = idx + 2  # Excel row (header = 1)

                try:
                    codice = str(row['Codice_Skill']).strip()

                    # Skip righe vuote
                    if not codice or pd.isna(row['Codice_Skill']) or codice.lower() == 'nan':
                        continue

                    descrizione = str(row.get('Descrizione', '')).strip() if pd.notna(row.get('Descrizione')) else None
                    produttivita = float(row.get('Produttivita_Default', 1.0)) if pd.notna(row.get('Produttivita_Default')) else 1.0
                    microskill = str(row.get('Microskill', '')).strip() if pd.notna(row.get('Microskill')) else ''

                    # Verifica se skill esiste
                    existing = self.db_manager.execute_query(
                        "SELECT ID FROM Skills WHERE Codice_Skill = ?",
                        (codice,)
                    )

                    if existing:
                        # Update
                        query = """
                            UPDATE Skills
                            SET Descrizione = ?, Produttivita_Default = ?, Microskill = ?
                            WHERE Codice_Skill = ?
                        """
                        self.db_manager.execute_update(query, (descrizione, produttivita, microskill, codice))
                        microskill_info = f" - Microskill: {microskill}" if microskill else ""
                        print(f"  [UPD] Riga {row_num}: '{codice}'{microskill_info} - Aggiornata")
                        self.updated += 1
                    else:
                        # Insert
                        query = """
                            INSERT INTO Skills (Codice_Skill, Descrizione, Produttivita_Default, Microskill)
                            VALUES (?, ?, ?, ?)
                        """
                        self.db_manager.execute_update(query, (codice, descrizione, produttivita, microskill))
                        microskill_info = f" - Microskill: {microskill}" if microskill else ""
                        print(f"  [OK] Riga {row_num}: '{codice}'{microskill_info} - Importata")
                        self.imported += 1

                except Exception as e:
                    error_msg = f"Riga {row_num}: {e}"
                    self.errors.append(error_msg)
                    print(f"  [ERROR] {error_msg}")
                    continue

            # Report finale
            print(f"\n{'='*70}")
            print(f"  RIEPILOGO IMPORT SKILLS")
            print(f"{'='*70}")
            print(f"  [OK] Importate:     {self.imported}")
            print(f"  [UPD] Aggiornate:   {self.updated}")
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
        description='Import skills da Excel'
    )
    parser.add_argument('--file', '-f', required=True,
                        help='File Excel da importare')
    parser.add_argument('--sheet', '-s', default='Skills',
                        help='Nome dello sheet (default: Skills)')

    args = parser.parse_args()

    if not Path(args.file).exists():
        print(f"[ERROR] File non trovato: {args.file}")
        return 1

    # Crea importer
    db_manager = DatabaseManager()
    importer = SkillsImporter(db_manager)

    # Esegui import
    success = importer.import_from_excel(args.file, sheet_name=args.sheet)

    if not success or len(importer.errors) > 0:
        return 1

    return 0


if __name__ == '__main__':
    sys.exit(main())
