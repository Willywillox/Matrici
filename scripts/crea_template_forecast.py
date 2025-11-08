"""
Genera template Excel per forecast volumi

Il template contiene:
- Data di riferimento
- Fasce orarie (30 minuti)
- Skill/Coda
- Volumi attesi
"""

import pandas as pd
import sys
from datetime import datetime, timedelta, time


def crea_template_forecast(output_file='template_forecast.xlsx', data_riferimento=None):
    """
    Crea template Excel per import forecast volumi

    Args:
        output_file: Nome file output
        data_riferimento: Data di riferimento (default: oggi)
    """

    if data_riferimento is None:
        data_riferimento = datetime.now().date()
    elif isinstance(data_riferimento, str):
        data_riferimento = datetime.strptime(data_riferimento, '%Y-%m-%d').date()

    # Genera fasce orarie ogni 30 minuti (48 fasce in un giorno)
    fasce_orarie = []
    current = datetime.combine(data_riferimento, time(0, 0))
    for i in range(48):  # 24 ore * 2 (ogni 30 minuti)
        fasce_orarie.append(current)
        current += timedelta(minutes=30)

    # Skills di esempio
    skills = ['CUSTOMER_CARE', 'BACK_OFFICE', 'TECHNICAL_SUPPORT', 'SALES']

    # Crea dati di esempio con pattern realistico
    forecast_data = []

    for skill in skills:
        for fascia in fasce_orarie:
            ora = fascia.hour

            # Pattern volumetrico realistico (maggiore in orari di punta)
            if 9 <= ora <= 12:  # Mattina (punta)
                volume_base = 120
            elif 14 <= ora <= 18:  # Pomeriggio
                volume_base = 100
            elif 8 <= ora <= 9 or 12 <= ora <= 14:  # Inizio/pausa pranzo
                volume_base = 80
            elif 18 <= ora <= 20:  # Sera
                volume_base = 60
            else:  # Notte/chiusura
                volume_base = 0

            # Variazione per skill
            if skill == 'CUSTOMER_CARE':
                volume = volume_base
            elif skill == 'TECHNICAL_SUPPORT':
                volume = int(volume_base * 0.6)  # Meno volumi
            elif skill == 'BACK_OFFICE':
                volume = int(volume_base * 0.4)  # Ancora meno
            elif skill == 'SALES':
                volume = int(volume_base * 0.3)
            else:
                volume = volume_base

            forecast_data.append({
                'Data_Riferimento': data_riferimento.strftime('%Y-%m-%d'),
                'Fascia_Oraria': fascia.strftime('%H:%M'),
                'Skill': skill,
                'Volumi_Attesi': volume,
                'Produttivita_Target': 1.0,
                'Note': ''
            })

    df = pd.DataFrame(forecast_data)

    # Crea Excel con formattazione
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Forecast', index=False)

        # Ottieni workbook e worksheet
        workbook = writer.book
        worksheet = writer.sheets['Forecast']

        # Formattazione header
        from openpyxl.styles import Font, PatternFill, Alignment, Border, Side

        header_fill = PatternFill(start_color='1F4E78', end_color='1F4E78', fill_type='solid')
        header_font = Font(bold=True, color='FFFFFF', size=11)

        for cell in worksheet[1]:
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = Alignment(horizontal='center', vertical='center')

        # Larghezza colonne
        column_widths = {
            'A': 18,  # Data_Riferimento
            'B': 15,  # Fascia_Oraria
            'C': 25,  # Skill
            'D': 18,  # Volumi_Attesi
            'E': 20,  # Produttivita_Target
            'F': 40   # Note
        }

        for col, width in column_widths.items():
            worksheet.column_dimensions[col].width = width

        # Bordi per tutte le celle
        thin_border = Border(
            left=Side(style='thin'),
            right=Side(style='thin'),
            top=Side(style='thin'),
            bottom=Side(style='thin')
        )

        for row in worksheet.iter_rows(min_row=1, max_row=len(df)+1):
            for cell in row:
                cell.border = thin_border
                if cell.row > 1:
                    cell.alignment = Alignment(horizontal='center', vertical='center')

        # Colora fasce orarie alternate per leggibilità
        skill_colors = {
            'CUSTOMER_CARE': 'E8F4F8',
            'BACK_OFFICE': 'FFF4E6',
            'TECHNICAL_SUPPORT': 'F0F4F8',
            'SALES': 'F4F0FF'
        }

        for row_idx in range(2, len(df)+2):
            cell_skill = worksheet.cell(row_idx, 3)
            skill_value = cell_skill.value

            if skill_value in skill_colors:
                fill_color = skill_colors[skill_value]
                for col_idx in range(1, 7):
                    worksheet.cell(row_idx, col_idx).fill = PatternFill(
                        start_color=fill_color,
                        end_color=fill_color,
                        fill_type='solid'
                    )

        # Aggiungi sheet con istruzioni
        istruzioni = pd.DataFrame({
            'ISTRUZIONI PER IL FORECAST': [
                '',
                '=== STRUTTURA FILE ===',
                '',
                'Questo template permette di importare previsioni di volumi per skill/code.',
                '',
                'COLONNE:',
                '  • Data_Riferimento: Data in formato YYYY-MM-DD (es: 2025-11-08)',
                '  • Fascia_Oraria: Ora inizio fascia in formato HH:MM (es: 09:00)',
                '  • Skill: Codice skill/coda (deve corrispondere a Skills configurati)',
                '  • Volumi_Attesi: Numero contatti/chiamate previsti nella fascia',
                '  • Produttivita_Target: Produttività target (tipicamente 1.0)',
                '  • Note: Annotazioni (opzionale)',
                '',
                '=== FASCE ORARIE ===',
                '',
                'Le fasce sono intervalli di 30 minuti che coprono l\'intera giornata (00:00-23:30).',
                'Ogni skill deve avere 48 fasce (24 ore x 2).',
                '',
                'Esempio:',
                '  00:00, 00:30, 01:00, 01:30, ..., 23:00, 23:30',
                '',
                '=== VOLUMI ATTESI ===',
                '',
                'I volumi rappresentano il numero di contatti/chiamate previsti in ogni fascia.',
                '',
                'Consigli:',
                '  • Analizzare storico per pattern realistici',
                '  • Considerare giorni della settimana (lun-ven diverso da sab-dom)',
                '  • Considerare stagionalità e eventi speciali',
                '  • Tipicamente fasce di punta: 9-12 e 14-18',
                '',
                'Esempi volumi fasce di punta:',
                '  • Customer Care: 80-150 chiamate/30min',
                '  • Technical Support: 40-80 chiamate/30min',
                '  • Back Office: 20-40 pratiche/30min',
                '',
                '=== CALCOLO ERLANG C ===',
                '',
                'I volumi vengono usati per calcolare FTE richiesti tramite Erlang C.',
                'Assicurarsi che le configurazioni Erlang siano state importate per ogni skill.',
                '',
                'Parametri Erlang necessari (da configurare separatamente):',
                '  • AHT (Average Handle Time)',
                '  • Service Level Target (es: 80% in 20 secondi)',
                '  • Shrinkage (es: 30%)',
                '',
                '=== IMPORT ===',
                '',
                'Dopo aver completato il forecast:',
                '  python scripts/import_forecast.py template_forecast.xlsx',
                '',
                'Il sistema calcolerà automaticamente gli FTE richiesti in base a:',
                '  - Volumi previsti',
                '  - Configurazione Erlang per ogni skill',
                '',
                '=== SUGGERIMENTI ===',
                '',
                '1. Creare forecast separati per giorni tipo:',
                '   - Lunedì-Venerdì (giorni lavorativi)',
                '   - Sabato',
                '   - Domenica/Festivi',
                '',
                '2. Aggiornare periodicamente in base a:',
                '   - Trend storici',
                '   - Campagne marketing',
                '   - Eventi stagionali',
                '',
                '3. Validare i volumi confrontando con:',
                '   - Storico volumi reali',
                '   - Capacità massima gestibile',
                '',
                ''
            ]
        })

        istruzioni.to_excel(writer, sheet_name='Istruzioni', index=False, header=False)
        worksheet_istr = writer.sheets['Istruzioni']
        worksheet_istr.column_dimensions['A'].width = 90

        # Formattazione istruzioni
        for row in worksheet_istr.iter_rows():
            for cell in row:
                if cell.value and isinstance(cell.value, str):
                    if cell.value.startswith('==='):
                        cell.font = Font(bold=True, size=13, color='1F4E78')
                    elif cell.value.startswith('  •') or cell.value.startswith('  -'):
                        cell.font = Font(size=10)
                        cell.alignment = Alignment(indent=2)
                    elif cell.value and not cell.value.startswith(' '):
                        cell.font = Font(size=10)

        # Sheet esempio riepilogo
        riepilogo_data = []
        for skill in skills:
            df_skill = df[df['Skill'] == skill]
            totale_volumi = df_skill['Volumi_Attesi'].sum()
            fasce_attive = len(df_skill[df_skill['Volumi_Attesi'] > 0])

            riepilogo_data.append({
                'Skill': skill,
                'Totale_Volumi_Giorno': totale_volumi,
                'Fasce_Attive': fasce_attive,
                'Media_Per_Fascia': totale_volumi / fasce_attive if fasce_attive > 0 else 0
            })

        df_riepilogo = pd.DataFrame(riepilogo_data)
        df_riepilogo.to_excel(writer, sheet_name='Riepilogo', index=False)

        worksheet_riep = writer.sheets['Riepilogo']
        for col_idx, col in enumerate(['A', 'B', 'C', 'D'], 1):
            worksheet_riep.column_dimensions[col].width = 25

        for cell in worksheet_riep[1]:
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = Alignment(horizontal='center', vertical='center')

    print(f"\n✅ Template forecast creato: {output_file}")
    print(f"\nData riferimento: {data_riferimento.strftime('%Y-%m-%d')}")
    print(f"Fasce orarie: 48 (ogni 30 minuti)")
    print(f"Skills: {len(skills)} ({', '.join(skills)})")
    print(f"Record totali: {len(df)}")
    print("\nSheet create:")
    print("  • Forecast: Dati volumi per fascia e skill")
    print("  • Riepilogo: Sommario volumi per skill")
    print("  • Istruzioni: Guida completa all'uso")
    print(f"\nPer importare: python scripts/import_forecast.py {output_file}\n")


if __name__ == '__main__':
    data = None

    if len(sys.argv) > 1:
        if sys.argv[1] == '--help':
            print("Uso: python crea_template_forecast.py [data] [output_file]")
            print("\nEsempi:")
            print("  python crea_template_forecast.py")
            print("  python crea_template_forecast.py 2025-11-08")
            print("  python crea_template_forecast.py 2025-11-08 forecast_nov.xlsx")
            sys.exit(0)

        try:
            data = datetime.strptime(sys.argv[1], '%Y-%m-%d').date()
        except ValueError:
            print(f"❌ Formato data non valido: {sys.argv[1]}")
            print("Usare formato: YYYY-MM-DD (es: 2025-11-08)")
            sys.exit(1)

    output = sys.argv[2] if len(sys.argv) > 2 else 'template_forecast.xlsx'

    crea_template_forecast(output, data)
