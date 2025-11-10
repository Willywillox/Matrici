"""
Script per import completo da template Excel unificato

Importa automaticamente (in ordine):
1. Skills
2. Turni
3. Giustificativi
4. Operatori

Da un unico file Excel con 4 sheet
"""

import sys
import os
import pandas as pd
from pathlib import Path

# Aggiungi path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from database.db_manager import DatabaseManager


class ImportCompleto:
    """Importatore unificato Skills + Turni + Operatori"""

    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.stats = {
            'skills': {'imported': 0, 'skipped': 0, 'errors': 0},
            'turni': {'imported': 0, 'skipped': 0, 'errors': 0},
            'giustificativi': {'imported': 0, 'updated': 0, 'errors': 0},
            'operatori': {'imported': 0, 'updated': 0, 'skipped': 0, 'errors': 0}
        }

    def import_from_excel(self, file_path):
        """
        Import completo da file Excel unificato

        Args:
            file_path: Percorso file Excel

        Returns:
            dict con statistiche import
        """
        print(f"\n{'='*70}")
        print(f"  IMPORT COMPLETO DA TEMPLATE UNIFICATO")
        print(f"{'='*70}\n")
        print(f"File: {file_path}\n")

        # Verifica file
        if not Path(file_path).exists():
            print(f"[ERROR] File non trovato: {file_path}")
            return None

        # Connetti database
        self.db_manager.connect()

        try:
            # === PASSO 1: IMPORT SKILLS ===
            print(f"\n{'-'*70}")
            print("[1/4] STEP 1/4: IMPORT SKILLS")
            print(f"{'-'*70}\n")

            self.import_skills(file_path)

            # === PASSO 2: IMPORT TURNI ===
            print(f"\n{'-'*70}")
            print("[2/4] STEP 2/4: IMPORT TURNI")
            print(f"{'-'*70}\n")

            self.import_turni(file_path)

            # === PASSO 3: IMPORT GIUSTIFICATIVI ===
            print(f"\n{'-'*70}")
            print("[3/4] STEP 3/4: IMPORT GIUSTIFICATIVI")
            print(f"{'-'*70}\n")

            self.import_giustificativi(file_path)

            # === PASSO 4: IMPORT OPERATORI ===
            print(f"\n{'-'*70}")
            print("[4/4] STEP 4/4: IMPORT OPERATORI")
            print(f"{'-'*70}\n")

            self.import_operatori(file_path)

            # Report finale
            self.print_summary()

            return self.stats

        finally:
            self.db_manager.close()

    def import_skills(self, file_path):
        """Import skills da sheet Skills"""
        try:
            df = pd.read_excel(file_path, sheet_name='Skills')
            print(f"[OK] Sheet 'Skills' letto: {len(df)} righe\n")

            if 'Codice_Skill' not in df.columns:
                print("[ERROR] Colonna 'Codice_Skill' mancante!")
                return

            for idx, row in df.iterrows():
                try:
                    codice = str(row['Codice_Skill']).strip()

                    if not codice or pd.isna(row['Codice_Skill']):
                        continue

                    descrizione = str(row.get('Descrizione', '')).strip() if pd.notna(row.get('Descrizione')) else None
                    produttivita = float(row.get('Produttivita_Default', 1.0)) if pd.notna(row.get('Produttivita_Default')) else 1.0

                    # Verifica se skill esiste
                    existing = self.db_manager.execute_query(
                        "SELECT ID FROM Skills WHERE Codice_Skill = ?",
                        (codice,)
                    )

                    if existing:
                        print(f"  [SKIP] Skill '{codice}' già esistente, skip")
                        self.stats['skills']['skipped'] += 1
                        continue

                    # Insert skill
                    query = """
                        INSERT INTO Skills (Codice_Skill, Descrizione, Produttivita_Default)
                        VALUES (?, ?, ?)
                    """
                    self.db_manager.execute_update(query, (codice, descrizione, produttivita))

                    print(f"  [OK] Skill '{codice}' importata")
                    self.stats['skills']['imported'] += 1

                except Exception as e:
                    print(f"  [ERROR] Riga {idx+2}: Errore - {e}")
                    self.stats['skills']['errors'] += 1

        except Exception as e:
            print(f"[ERROR] Errore lettura sheet Skills: {e}")

    def import_turni(self, file_path):
        """Import turni da sheet Turni"""
        try:
            df = pd.read_excel(file_path, sheet_name='Turni')
            print(f"[OK] Sheet 'Turni' letto: {len(df)} righe\n")

            required = ['ID_Turno', 'Ora_Inizio', 'Ora_Fine']
            missing = [col for col in required if col not in df.columns]

            if missing:
                print(f"[ERROR] Colonne mancanti: {', '.join(missing)}")
                return

            for idx, row in df.iterrows():
                try:
                    id_turno = str(row['ID_Turno']).strip()

                    if not id_turno or pd.isna(row['ID_Turno']):
                        continue

                    ora_inizio = str(row['Ora_Inizio']).strip()
                    ora_fine = str(row['Ora_Fine']).strip()
                    descrizione = str(row.get('Descrizione', '')).strip() if pd.notna(row.get('Descrizione')) else None
                    ore_turno = float(row.get('Ore_Turno', 0)) if pd.notna(row.get('Ore_Turno')) else None
                    ora_inizio_spezzato = str(row.get('Ora_Inizio_Spezzato', '')).strip() if pd.notna(row.get('Ora_Inizio_Spezzato')) else None
                    ora_fine_spezzato = str(row.get('Ora_Fine_Spezzato', '')).strip() if pd.notna(row.get('Ora_Fine_Spezzato')) else None
                    note = str(row.get('Note', '')).strip() if pd.notna(row.get('Note')) else None

                    # Calcola ore se non fornite
                    if not ore_turno:
                        ore_turno = self.calcola_ore_turno(ora_inizio, ora_fine)

                    # Verifica se turno esiste
                    existing = self.db_manager.execute_query(
                        "SELECT ID FROM Turni WHERE ID_Turno = ?",
                        (id_turno,)
                    )

                    if existing:
                        print(f"  ⏭️  Turno '{id_turno}' già esistente, skip")
                        self.stats['turni']['skipped'] += 1
                        continue

                    # Insert turno
                    query = """
                        INSERT INTO Turni (
                            ID_Turno, Descrizione, Ora_Inizio, Ora_Fine, Ore_Turno,
                            Ora_Inizio_Spezzato, Ora_Fine_Spezzato, Note
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """
                    self.db_manager.execute_update(query, (
                        id_turno, descrizione, ora_inizio, ora_fine, ore_turno,
                        ora_inizio_spezzato, ora_fine_spezzato, note
                    ))

                    print(f"  [OK] Turno '{id_turno}': {ora_inizio}-{ora_fine} ({ore_turno}h)")
                    self.stats['turni']['imported'] += 1

                except Exception as e:
                    print(f"  [ERROR] Riga {idx+2}: Errore - {e}")
                    self.stats['turni']['errors'] += 1

        except Exception as e:
            print(f"[ERROR] Errore lettura sheet Turni: {e}")

    def import_giustificativi(self, file_path):
        """Import giustificativi da sheet Giust"""
        try:
            # Verifica se sheet esiste
            xl_file = pd.ExcelFile(file_path)
            if 'Giust' not in xl_file.sheet_names:
                print("[SKIP] Sheet 'Giust' non trovato, saltato")
                return

            df = pd.read_excel(file_path, sheet_name='Giust')
            print(f"[OK] Sheet 'Giust' letto: {len(df)} righe\n")

            # Identifica colonna codice
            codice_col = None
            if 'Giustificativo' in df.columns:
                codice_col = 'Giustificativo'
            elif 'Codice_Giustificativo' in df.columns:
                codice_col = 'Codice_Giustificativo'

            if not codice_col:
                print("[ERROR] Colonna 'Giustificativo' o 'Codice_Giustificativo' mancante!")
                return

            if 'Tipologia' not in df.columns:
                print("[ERROR] Colonna 'Tipologia' mancante!")
                return

            for idx, row in df.iterrows():
                try:
                    codice = str(row[codice_col]).strip()

                    if not codice or pd.isna(row[codice_col]) or codice.lower() == 'nan':
                        continue

                    tipologia = str(row['Tipologia']).strip() if pd.notna(row['Tipologia']) else None
                    descrizione = str(row.get('Descrizione', '')).strip() if pd.notna(row.get('Descrizione')) else None
                    note = str(row.get('Note', '')).strip() if pd.notna(row.get('Note')) else None

                    # Verifica se esiste
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
                        print(f"  [UPD] '{codice}' - Tipologia: {tipologia}")
                        self.stats['giustificativi']['updated'] += 1
                    else:
                        # Insert
                        query = """
                            INSERT INTO Giustificativi (Codice_Giustificativo, Descrizione, Tipologia, Note)
                            VALUES (?, ?, ?, ?)
                        """
                        self.db_manager.execute_update(query, (codice, descrizione, tipologia, note))
                        print(f"  [OK] '{codice}' - Tipologia: {tipologia}")
                        self.stats['giustificativi']['imported'] += 1

                except Exception as e:
                    print(f"  [ERROR] Riga {idx+2}: {e}")
                    self.stats['giustificativi']['errors'] += 1

        except Exception as e:
            print(f"[ERROR] Errore lettura sheet Giust: {e}")

    def import_operatori(self, file_path):
        """Import operatori da sheet Operatori"""
        try:
            # Importa usando lo script esistente
            from import_excel_operatori import ExcelImporter

            importer = ExcelImporter(self.db_manager)
            result = importer.import_from_excel(file_path, sheet_name='Operatori')

            if result:
                self.stats['operatori'] = {
                    'imported': importer.imported,
                    'updated': importer.updated,
                    'skipped': importer.skipped,
                    'errors': len(importer.errors)
                }

        except Exception as e:
            print(f"[ERROR] Errore import operatori: {e}")
            import traceback
            traceback.print_exc()

    def calcola_ore_turno(self, ora_inizio, ora_fine):
        """Calcola ore turno da orari"""
        try:
            h_i, m_i = map(int, ora_inizio.split(':'))
            h_f, m_f = map(int, ora_fine.split(':'))

            start = h_i + m_i / 60
            end = h_f + m_f / 60

            if end < start:
                end += 24

            return end - start
        except:
            return None

    def print_summary(self):
        """Stampa riepilogo completo"""
        print(f"\n{'='*70}")
        print(f"  RIEPILOGO IMPORT COMPLETO")
        print(f"{'='*70}")

        print(f"\nSKILLS:")
        print(f"  [OK] Importate:     {self.stats['skills']['imported']}")
        print(f"  [SKIP] Saltate:     {self.stats['skills']['skipped']}")
        print(f"  [ERROR] Errori:     {self.stats['skills']['errors']}")

        print(f"\nTURNI:")
        print(f"  [OK] Importati:     {self.stats['turni']['imported']}")
        print(f"  [SKIP] Saltati:     {self.stats['turni']['skipped']}")
        print(f"  [ERROR] Errori:     {self.stats['turni']['errors']}")

        print(f"\nGIUSTIFICATIVI:")
        print(f"  [OK] Importati:     {self.stats['giustificativi']['imported']}")
        print(f"  [UPD] Aggiornati:   {self.stats['giustificativi']['updated']}")
        print(f"  [ERROR] Errori:     {self.stats['giustificativi']['errors']}")

        print(f"\nOPERATORI:")
        print(f"  [OK] Importati:     {self.stats['operatori']['imported']}")
        print(f"  [UPD] Aggiornati:   {self.stats['operatori']['updated']}")
        print(f"  [SKIP] Saltati:     {self.stats['operatori']['skipped']}")
        print(f"  [ERROR] Errori:     {self.stats['operatori']['errors']}")

        totale_ok = (
            self.stats['skills']['imported'] +
            self.stats['turni']['imported'] +
            self.stats['giustificativi']['imported'] +
            self.stats['giustificativi']['updated'] +
            self.stats['operatori']['imported'] +
            self.stats['operatori']['updated']
        )

        totale_errori = (
            self.stats['skills']['errors'] +
            self.stats['turni']['errors'] +
            self.stats['giustificativi']['errors'] +
            self.stats['operatori']['errors']
        )

        print(f"\n{'='*70}")
        print(f"  TOTALE: {totale_ok} record importati/aggiornati, {totale_errori} errori")
        print(f"{'='*70}\n")


def main():
    """Main function"""
    if len(sys.argv) < 2:
        print("Uso: python scripts/import_completo.py <file_excel>")
        print("\nEsempio:")
        print("  python scripts/import_completo.py template_import_completo.xlsx")
        print("\nIl file Excel deve contenere 4 sheet:")
        print("  - Skills: Elenco competenze")
        print("  - Turni: Elenco turni")
        print("  - Giust: Giustificativi (opzionale)")
        print("  - Operatori: Dati operatori")
        return 1

    file_path = sys.argv[1]

    if not Path(file_path).exists():
        print(f"[ERROR] File non trovato: {file_path}")
        return 1

    # Crea importer
    db_manager = DatabaseManager()
    importer = ImportCompleto(db_manager)

    # Esegui import
    result = importer.import_from_excel(file_path)

    if result is None:
        return 1

    # Exit code
    totale_errori = (
        result['skills']['errors'] +
        result['turni']['errors'] +
        result['operatori']['errors']
    )

    return 0 if totale_errori == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
