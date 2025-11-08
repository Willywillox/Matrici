#!/usr/bin/env python3
"""
Script per importare operatori massivamente da file Excel

Uso:
    python scripts/import_excel_operatori.py --file dati_operatori.xlsx
    python scripts/import_excel_operatori.py --file dati_operatori.xlsx --sheet "Operatori"
"""

import sys
import os
import argparse
from pathlib import Path
from datetime import datetime
import pandas as pd

# Aggiungi path per import
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from database.db_manager import DatabaseManager


class ExcelImporter:
    """Importatore Excel → Database"""

    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.errors = []
        self.warnings = []
        self.imported = 0
        self.updated = 0
        self.skipped = 0

    def parse_time(self, value):
        """Converte valore Excel in orario HH:MM:SS"""
        if pd.isna(value) or value == '' or value is None:
            return None

        # Se è già un datetime
        if isinstance(value, datetime):
            return value.strftime('%H:%M:%S')

        # Se è una stringa
        if isinstance(value, str):
            value = value.strip()
            if not value:
                return None

            # Prova vari formati
            for fmt in ['%H:%M:%S', '%H:%M', '%I:%M %p', '%I:%M:%S %p']:
                try:
                    dt = datetime.strptime(value, fmt)
                    return dt.strftime('%H:%M:%S')
                except ValueError:
                    continue

        # Se è un float (Excel time come frazione di giorno)
        try:
            if isinstance(value, (int, float)):
                # Excel memorizza tempi come frazione di 24h
                total_seconds = value * 24 * 3600
                hours = int(total_seconds // 3600)
                minutes = int((total_seconds % 3600) // 60)
                seconds = int(total_seconds % 60)
                return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        except:
            pass

        return None

    def parse_date(self, value):
        """Converte valore Excel in data YYYY-MM-DD"""
        if pd.isna(value) or value == '' or value is None:
            return None

        # Se è già un datetime
        if isinstance(value, datetime):
            return value.strftime('%Y-%m-%d')

        # Se è una stringa
        if isinstance(value, str):
            value = value.strip()
            if not value:
                return None

            # Prova vari formati
            for fmt in ['%Y-%m-%d', '%d/%m/%Y', '%m/%d/%Y', '%d-%m-%Y']:
                try:
                    dt = datetime.strptime(value, fmt)
                    return dt.strftime('%Y-%m-%d')
                except ValueError:
                    continue

        # Se è un Timestamp pandas
        try:
            return pd.to_datetime(value).strftime('%Y-%m-%d')
        except:
            pass

        return None

    def import_from_excel(self, file_path, sheet_name=None):
        """
        Importa operatori da file Excel

        Args:
            file_path: Percorso file Excel
            sheet_name: Nome foglio (None = primo foglio)

        Returns:
            dict con statistiche import
        """
        print(f"\n{'='*60}")
        print(f"  IMPORT EXCEL OPERATORI")
        print(f"{'='*60}\n")

        # Leggi Excel
        try:
            if sheet_name:
                df = pd.read_excel(file_path, sheet_name=sheet_name)
                print(f"[OK] File letto: {file_path} (foglio: {sheet_name})")
            else:
                df = pd.read_excel(file_path)
                print(f"[OK] File letto: {file_path}")

            print(f"  Righe trovate: {len(df)}\n")
        except Exception as e:
            print(f"[ERROR] Errore lettura file Excel: {e}")
            return None

        # Colonne richieste
        required_cols = ['Nome', 'Cognome', 'ID_SAP', 'Data_Riferimento']
        missing = [col for col in required_cols if col not in df.columns]

        if missing:
            print(f"[ERROR] Colonne obbligatorie mancanti: {', '.join(missing)}")
            print(f"\nColonne trovate: {', '.join(df.columns)}")
            print(f"\nUsa il template: templates/template_import_operatori.xlsx")
            return None

        # Connetti database
        self.db_manager.connect()

        # Processa ogni riga
        print(f"Inizio import...\n")

        for idx, row in df.iterrows():
            row_num = idx + 2  # +2 perché Excel parte da 1 e c'è l'header

            try:
                # Valida campi obbligatori
                nome = str(row['Nome']).strip() if pd.notna(row['Nome']) else None
                cognome = str(row['Cognome']).strip() if pd.notna(row['Cognome']) else None
                id_sap = str(row['ID_SAP']).strip() if pd.notna(row['ID_SAP']) else None
                data_rif = self.parse_date(row['Data_Riferimento'])

                if not all([nome, cognome, id_sap, data_rif]):
                    self.errors.append(f"Riga {row_num}: Campi obbligatori mancanti (Nome, Cognome, ID_SAP, Data)")
                    self.skipped += 1
                    continue

                # Prepara dati operatore
                dati = {
                    'Nome': nome,
                    'Cognome': cognome,
                    'ID_SAP': id_sap,
                    'Data_Riferimento': data_rif,
                    'Tipo_Contratto': str(row.get('Tipo_Contratto', '')).strip() if pd.notna(row.get('Tipo_Contratto')) else None,
                    'FTE': float(row.get('FTE', 0)) if pd.notna(row.get('FTE')) else None,
                    'Ore_Settimana': float(row.get('Ore_Settimana', 0)) if pd.notna(row.get('Ore_Settimana')) else None,
                    'ID_Turno': str(row.get('ID_Turno', '')).strip() if pd.notna(row.get('ID_Turno')) else None,
                    'Ora_Inizio_Turno': self.parse_time(row.get('Ora_Inizio_Turno')),
                    'Ora_Fine_Turno': self.parse_time(row.get('Ora_Fine_Turno')),
                    'Ora_Inizio_Turno_Spezzato': self.parse_time(row.get('Ora_Inizio_Turno_Spezzato')),
                    'Ora_Fine_Turno_Spezzato': self.parse_time(row.get('Ora_Fine_Turno_Spezzato')),
                    'Etichetta_Skill': str(row.get('Etichetta_Skill', '')).strip() if pd.notna(row.get('Etichetta_Skill')) else None,
                    'Postazione': str(row.get('Postazione', '')).strip() if pd.notna(row.get('Postazione')) else None,
                }

                # Straordinari (3 slot)
                for i in range(1, 4):
                    dati[f'Inizio_Strao_{i}'] = self.parse_time(row.get(f'Inizio_Strao_{i}'))
                    dati[f'Fine_Strao_{i}'] = self.parse_time(row.get(f'Fine_Strao_{i}'))

                # Pause (5 slot)
                for i in range(1, 6):
                    dati[f'Inizio_Pausa_{i}'] = self.parse_time(row.get(f'Inizio_Pausa_{i}'))
                    dati[f'Fine_Pausa_{i}'] = self.parse_time(row.get(f'Fine_Pausa_{i}'))

                # Giustificativi (5 slot)
                for i in range(1, 6):
                    dati[f'Tipo_Giust_{i}'] = str(row.get(f'Tipo_Giust_{i}', '')).strip() if pd.notna(row.get(f'Tipo_Giust_{i}')) else None
                    dati[f'Inizio_Giust_{i}'] = self.parse_time(row.get(f'Inizio_Giust_{i}'))
                    dati[f'Fine_Giust_{i}'] = self.parse_time(row.get(f'Fine_Giust_{i}'))

                # Verifica se operatore esiste già (stessa data e ID_SAP)
                query = """
                    SELECT ID FROM Anagrafica_Operatori
                    WHERE ID_SAP = ? AND Data_Riferimento = ?
                """
                existing = self.db_manager.execute_query(query, (id_sap, data_rif))

                if existing:
                    # Update
                    op_id = existing[0][0]
                    updates = []
                    values = []

                    for key, value in dati.items():
                        if key not in ['ID_SAP', 'Data_Riferimento']:
                            updates.append(f"{key} = ?")
                            values.append(value)

                    query = f"UPDATE Anagrafica_Operatori SET {', '.join(updates)} WHERE ID = ?"
                    values.append(op_id)

                    self.db_manager.execute_update(query, tuple(values))
                    self.updated += 1
                    print(f"  [UPD] Riga {row_num}: {nome} {cognome} (ID_SAP: {id_sap}) - AGGIORNATO")

                else:
                    # Insert
                    self.db_manager.insert_operatore(dati)
                    self.imported += 1
                    print(f"  [OK] Riga {row_num}: {nome} {cognome} (ID_SAP: {id_sap}) - IMPORTATO")

            except Exception as e:
                error_msg = f"Riga {row_num}: Errore import - {str(e)}"
                self.errors.append(error_msg)
                print(f"  [ERROR] {error_msg}")
                self.skipped += 1

        self.db_manager.close()

        # Report finale
        self.print_summary()

        return {
            'imported': self.imported,
            'updated': self.updated,
            'skipped': self.skipped,
            'errors': self.errors,
            'warnings': self.warnings
        }

    def print_summary(self):
        """Stampa riepilogo import"""
        print(f"\n{'='*60}")
        print(f"  RIEPILOGO IMPORT")
        print(f"{'='*60}")
        print(f"  [OK] Nuovi operatori importati:     {self.imported}")
        print(f"  [UPD] Operatori aggiornati:         {self.updated}")
        print(f"  [ERROR] Righe saltate (errori):     {self.skipped}")
        print(f"{'='*60}\n")

        if self.errors:
            print(f"ERRORI ({len(self.errors)}):")
            for err in self.errors:
                print(f"  • {err}")
            print()

        if self.warnings:
            print(f"AVVISI ({len(self.warnings)}):")
            for warn in self.warnings:
                print(f"  • {warn}")
            print()


def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Import operatori da Excel')
    parser.add_argument('--file', '-f', required=True, help='Percorso file Excel')
    parser.add_argument('--sheet', '-s', help='Nome foglio Excel (opzionale)')

    args = parser.parse_args()

    # Verifica file esista
    if not Path(args.file).exists():
        print(f"[ERROR] File non trovato: {args.file}")
        return 1

    # Crea importer
    db_manager = DatabaseManager()
    importer = ExcelImporter(db_manager)

    # Esegui import
    result = importer.import_from_excel(args.file, args.sheet)

    if result is None:
        return 1

    # Exit code
    if result['errors']:
        return 1
    else:
        return 0


if __name__ == '__main__':
    sys.exit(main())
