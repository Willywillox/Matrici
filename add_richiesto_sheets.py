#!/usr/bin/env python3
"""
Script per aggiungere fogli "Richiesto" per skill nel template Excel.
Ogni skill avrà un foglio dedicato con la stessa struttura del forecast:
- Righe: Date
- Colonne: Fasce orarie di 15 minuti
"""

import openpyxl
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
from openpyxl.utils import get_column_letter
from datetime import time
import sys

def create_time_slots():
    """Crea le fasce orarie di 15 minuti per 24 ore (96 intervalli)"""
    time_slots = []
    for hour in range(24):
        for minute in [0, 15, 30, 45]:
            start_time = time(hour, minute)
            # Calcola l'ora di fine (15 minuti dopo)
            end_minute = minute + 15
            if end_minute == 60:
                end_hour = (hour + 1) % 24
                end_minute = 0
            else:
                end_hour = hour
            end_time = time(end_hour, end_minute)

            time_slot = f"{start_time.strftime('%H:%M')}-{end_time.strftime('%H:%M')}"
            time_slots.append(time_slot)

    return time_slots

def read_skills(worksheet):
    """Legge gli skill dal foglio Skills"""
    skills = []
    for row in worksheet.iter_rows(min_row=2, max_row=worksheet.max_row):
        codice = row[0].value
        descrizione = row[1].value if len(row) > 1 else None
        if codice:
            skills.append({
                'codice': codice,
                'descrizione': descrizione
            })
    return skills

def create_richiesto_sheet(workbook, skill_code, skill_description):
    """Crea un foglio richiesto per uno skill specifico"""

    # Crea il nuovo foglio
    ws = workbook.create_sheet(title=f"RQ_{skill_code[:25]}")  # Limita a 31 caratteri totali

    # Stili (verde per richiesto)
    header_fill = PatternFill(start_color="70AD47", end_color="70AD47", fill_type="solid")
    header_font = Font(bold=True, color="FFFFFF", size=11)
    center_alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    border = Border(
        left=Side(style='thin'),
        right=Side(style='thin'),
        top=Side(style='thin'),
        bottom=Side(style='thin')
    )

    # Header principale (riga 1)
    ws.merge_cells('A1:A2')
    cell_a1 = ws['A1']
    cell_a1.value = "Data"
    cell_a1.fill = header_fill
    cell_a1.font = header_font
    cell_a1.alignment = center_alignment
    cell_a1.border = border

    # Titolo skill (sopra le colonne)
    ws.merge_cells('B1:CU1')
    cell_b1 = ws['B1']
    cell_b1.value = f"RICHIESTO - {skill_code}: {skill_description if skill_description else ''}"
    cell_b1.fill = header_fill
    cell_b1.font = header_font
    cell_b1.alignment = center_alignment
    cell_b1.border = border

    # Genera le fasce orarie
    time_slots = create_time_slots()

    # Scrivi le fasce orarie nella riga 2
    for idx, time_slot in enumerate(time_slots, start=2):
        col_letter = get_column_letter(idx)
        cell = ws[f'{col_letter}2']
        cell.value = time_slot
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = center_alignment
        cell.border = border

        # Imposta larghezza colonna
        ws.column_dimensions[col_letter].width = 12

    # Imposta larghezza colonna Data
    ws.column_dimensions['A'].width = 12

    # Aggiungi alcune righe di esempio per le date
    example_row_start = 3
    num_example_rows = 30  # 30 giorni di esempio

    for row_idx in range(example_row_start, example_row_start + num_example_rows):
        # Formatta cella data
        cell_date = ws[f'A{row_idx}']
        cell_date.number_format = 'DD/MM/YYYY'
        cell_date.alignment = Alignment(horizontal="center", vertical="center")
        cell_date.border = border

        # Formatta celle richiesto (numeri decimali - risultato Erlang)
        for col_idx in range(2, len(time_slots) + 2):
            col_letter = get_column_letter(col_idx)
            cell = ws[f'{col_letter}{row_idx}']
            cell.number_format = '0.00'  # Numero decimale (per Erlang)
            cell.alignment = Alignment(horizontal="right", vertical="center")
            cell.border = border

    # Freeze panes (blocca intestazioni)
    ws.freeze_panes = 'B3'

    return ws

def main():
    # Percorso del template
    template_path = '/home/user/Matrici/template_import_completo.xlsx'

    try:
        # Carica il workbook
        print(f"Caricamento template: {template_path}")
        wb = openpyxl.load_workbook(template_path)

        # Leggi gli skill
        if 'Skills' not in wb.sheetnames:
            print("ERRORE: Foglio 'Skills' non trovato nel template")
            return 1

        ws_skills = wb['Skills']
        skills = read_skills(ws_skills)

        print(f"\nTrovati {len(skills)} skill:")
        for skill in skills:
            print(f"  - {skill['codice']}: {skill['descrizione']}")

        # Rimuovi eventuali fogli richiesto esistenti (che iniziano con RQ_)
        sheets_to_remove = [sheet for sheet in wb.sheetnames if sheet.startswith('RQ_')]
        for sheet_name in sheets_to_remove:
            print(f"\nRimozione foglio esistente: {sheet_name}")
            wb.remove(wb[sheet_name])

        # Crea un foglio richiesto per ogni skill
        print("\n" + "="*60)
        print("Creazione fogli RICHIESTO per skill...")
        print("="*60)

        for skill in skills:
            print(f"\nCreazione foglio richiesto per skill: {skill['codice']}")
            create_richiesto_sheet(wb, skill['codice'], skill['descrizione'])
            print(f"  ✓ Foglio 'RQ_{skill['codice']}' creato con successo")

        # Salva il workbook
        print(f"\nSalvataggio template modificato...")
        wb.save(template_path)
        print(f"✓ Template salvato con successo: {template_path}")

        print("\n" + "="*60)
        print("COMPLETATO!")
        print("="*60)
        print(f"\nFogli RICHIESTO creati:")
        for skill in skills:
            print(f"  - RQ_{skill['codice']}: Richiesto (Erlang) per {skill['descrizione']}")

        return 0

    except Exception as e:
        print(f"\nERRORE: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1

if __name__ == '__main__':
    sys.exit(main())
