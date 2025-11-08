"""
Script per creare template Excel per import turni

Genera un file Excel con:
- Tutte le colonne necessarie
- Esempi precompilati
- Istruzioni d'uso
"""

import pandas as pd
import sys
import os

def crea_template_turni(output_file='template_turni.xlsx'):
    """Crea template Excel per import turni"""

    print("\n=== CREAZIONE TEMPLATE EXCEL TURNI ===\n")

    # Dati di esempio
    data = {
        'ID_Turno': [
            'T1',
            'T2',
            'T3',
            'T4',
            'T5',
            ''  # Riga vuota per l'utente
        ],
        'Descrizione': [
            'Turno Mattina Standard',
            'Turno Pomeriggio',
            'Turno Spezzato',
            'Turno Notte',
            'Turno Weekend',
            ''
        ],
        'Ora_Inizio': [
            '09:00',
            '14:00',
            '09:00',
            '22:00',
            '08:00',
            ''
        ],
        'Ora_Fine': [
            '18:00',
            '22:00',
            '13:00',
            '06:00',
            '16:00',
            ''
        ],
        'Ore_Turno': [
            9.0,
            8.0,
            8.0,  # 4h + 4h spezzato
            8.0,
            8.0,
            None
        ],
        'Ora_Inizio_Spezzato': [
            '',
            '',
            '17:00',  # Turno spezzato
            '',
            '',
            ''
        ],
        'Ora_Fine_Spezzato': [
            '',
            '',
            '21:00',  # Turno spezzato
            '',
            '',
            ''
        ],
        'Note': [
            'Turno standard ufficio',
            'Turno pomeridiano',
            'Pausa pranzo 13:00-17:00',
            'Attraversa mezzanotte',
            'Turno ridotto weekend',
            ''
        ]
    }

    # Crea DataFrame
    df = pd.DataFrame(data)

    # Crea Excel con formattazione
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        # Scrivi dati
        df.to_excel(writer, sheet_name='Turni', index=False)

        # Ottieni worksheet
        worksheet = writer.sheets['Turni']

        # Imposta larghezze colonne
        column_widths = {
            'A': 12,  # ID_Turno
            'B': 30,  # Descrizione
            'C': 12,  # Ora_Inizio
            'D': 12,  # Ora_Fine
            'E': 12,  # Ore_Turno
            'F': 18,  # Ora_Inizio_Spezzato
            'G': 18,  # Ora_Fine_Spezzato
            'H': 35   # Note
        }

        for col, width in column_widths.items():
            worksheet.column_dimensions[col].width = width

        # Formatta header (grassetto, sfondo grigio)
        from openpyxl.styles import Font, PatternFill, Alignment

        header_fill = PatternFill(start_color="D3D3D3", end_color="D3D3D3", fill_type="solid")
        header_font = Font(bold=True, size=11)

        for cell in worksheet[1]:
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = Alignment(horizontal='center', vertical='center')

        # Allineamento centrato per orari
        for row in range(2, worksheet.max_row + 1):
            for col in ['A', 'C', 'D', 'E', 'F', 'G']:
                worksheet[f'{col}{row}'].alignment = Alignment(horizontal='center')

        # Aggiungi sheet istruzioni
        istruzioni = pd.DataFrame({
            'ISTRUZIONI PER L\'USO': [
                '',
                '=== COME USARE QUESTO TEMPLATE ===',
                '',
                '1. COMPILA LE RIGHE:',
                '   - ID_Turno: Codice identificativo turno (es: T1, T2, TURNO_A)',
                '   - Descrizione: Nome descrittivo del turno (opzionale)',
                '   - Ora_Inizio: Ora inizio turno nel formato HH:MM (es: 09:00)',
                '   - Ora_Fine: Ora fine turno nel formato HH:MM (es: 18:00)',
                '   - Ore_Turno: Ore totali (opzionale, calcolato automaticamente se vuoto)',
                '   - Ora_Inizio_Spezzato: Ora inizio parte spezzata (opzionale, formato HH:MM)',
                '   - Ora_Fine_Spezzato: Ora fine parte spezzata (opzionale, formato HH:MM)',
                '   - Note: Annotazioni libere (opzionale)',
                '',
                '2. ESEMPI FORNITI:',
                '   - T1: Turno standard 09:00-18:00 (9 ore)',
                '   - T2: Turno pomeridiano 14:00-22:00 (8 ore)',
                '   - T3: Turno spezzato 09:00-13:00 + 17:00-21:00 (8 ore totali)',
                '   - T4: Turno notte 22:00-06:00 (attraversa mezzanotte)',
                '   - T5: Turno weekend ridotto 08:00-16:00',
                '',
                '3. AGGIUNGI I TUOI TURNI:',
                '   - Usa la riga vuota in fondo o aggiungi nuove righe',
                '   - Puoi eliminare gli esempi se non ti servono',
                '',
                '4. IMPORTA NEL DATABASE:',
                '   - Salva il file Excel',
                '   - Apri il prompt dei comandi (CMD)',
                '   - Vai nella cartella Matrici: cd C:\\Matrici',
                '   - Esegui: python scripts/import_excel_turni.py template_turni.xlsx',
                '',
                '5. NOTE IMPORTANTI:',
                '   - ID_Turno DEVE essere univoco (non duplicare)',
                '   - Formato orario: sempre HH:MM (es: 09:00, non 9:00 o 9)',
                '   - Per turni notturni: Ora_Fine può essere < Ora_Inizio (attraversa mezzanotte)',
                '   - Turni spezzati: compila sia parte normale che parte spezzata',
                '   - Ore_Turno: se vuoto viene calcolato automaticamente',
                '',
                '=== ESEMPI DI TURNI COMUNI ===',
                '',
                'Turno ufficio:         09:00-18:00 (1h pausa non contata)',
                'Turno continuo:        08:00-16:00 (nessuna pausa)',
                'Turno notte:           22:00-06:00 (attraversa mezzanotte)',
                'Turno spezzato:        09:00-13:00 + 17:00-21:00',
                'Turno part-time:       14:00-18:00',
                'Turno weekend:         10:00-18:00',
                '',
                '=== DOMANDE FREQUENTI ===',
                '',
                'Q: Posso importare più volte lo stesso file?',
                'A: Sì, i turni già esistenti vengono saltati automaticamente.',
                '',
                'Q: Cosa succede se sbaglio un formato orario?',
                'A: Lo script mostra un errore per quella riga e continua con le altre.',
                '',
                'Q: Posso modificare un turno già importato?',
                'A: Devi eliminarlo dal database e reimportarlo, oppure modificarlo manualmente.',
                '',
                'Q: Come elimino tutti i turni?',
                'A: Usa il menu "Database → Inizializza Database" in Matrici (cancella tutto!).',
                '',
            ]
        })

        istruzioni.to_excel(writer, sheet_name='Istruzioni', index=False, header=False)

        # Formatta foglio istruzioni
        ws_istr = writer.sheets['Istruzioni']
        ws_istr.column_dimensions['A'].width = 80

        # Grassetto per i titoli
        for row in [2, 4, 13, 21, 27, 33, 41]:
            ws_istr[f'A{row}'].font = Font(bold=True, size=12)

    print(f"✅ Template creato: {output_file}")
    print(f"\nIl file contiene:")
    print(f"  - Sheet 'Turni': Template con 5 esempi + riga vuota")
    print(f"  - Sheet 'Istruzioni': Guida completa all'uso")
    print(f"\nProssimi passi:")
    print(f"  1. Apri {output_file} con Excel")
    print(f"  2. Compila i tuoi turni (o modifica gli esempi)")
    print(f"  3. Salva il file")
    print(f"  4. Importa: python scripts/import_excel_turni.py {output_file}")
    print()


if __name__ == '__main__':
    # Verifica se è stato specificato un nome file
    if len(sys.argv) > 1:
        output_file = sys.argv[1]
    else:
        output_file = 'template_turni.xlsx'

    # Crea template
    try:
        crea_template_turni(output_file)
        print("✅ Template creato con successo!\n")
    except Exception as e:
        print(f"❌ Errore durante la creazione del template: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
