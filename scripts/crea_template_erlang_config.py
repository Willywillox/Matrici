"""
Genera template Excel per configurazione parametri Erlang C

Il file Excel conterrà configurazioni per calcoli workforce planning:
- AHT (Average Handle Time)
- Shrinkage (pause, formazione, ecc.)
- Service Level targets
- Occupancy target
"""

import pandas as pd
import sys
from pathlib import Path


def crea_template_erlang(output_file='template_erlang_config.xlsx'):
    """
    Crea template Excel per import configurazione Erlang C

    Args:
        output_file: Nome file output
    """

    # Dati di esempio
    config_data = {
        'Skill': [
            'CUSTOMER_CARE',
            'BACK_OFFICE',
            'TECHNICAL_SUPPORT',
            'SALES',
            ''
        ],
        'AHT_Seconds': [
            180,   # 3 minuti
            240,   # 4 minuti
            300,   # 5 minuti
            150,   # 2.5 minuti
            180
        ],
        'Tempo_Pausa_Minuti': [
            0,     # Pause gestite separatamente
            0,
            0,
            0,
            0
        ],
        'Shrinkage': [
            0.30,  # 30% (pause, formazione, riunioni, ecc.)
            0.25,  # 25%
            0.30,  # 30%
            0.28,  # 28%
            0.30
        ],
        'Service_Level_Target': [
            0.80,  # 80% delle chiamate
            0.75,  # 75%
            0.80,  # 80%
            0.85,  # 85%
            0.80
        ],
        'Service_Level_Seconds': [
            20,    # Entro 20 secondi
            30,    # Entro 30 secondi
            20,    # Entro 20 secondi
            15,    # Entro 15 secondi
            20
        ],
        'Occupancy_Target': [
            0.85,  # 85% occupancy
            0.80,  # 80%
            0.85,  # 85%
            0.87,  # 87%
            0.85
        ],
        'Interval_Minutes': [
            30,    # Calcoli ogni 30 minuti
            30,
            30,
            30,
            30
        ],
        'Note': [
            'Assistenza clienti standard',
            'Attività back office (email, pratiche)',
            'Supporto tecnico avanzato',
            'Vendite outbound e inbound',
            ''
        ]
    }

    df = pd.DataFrame(config_data)

    # Crea Excel con formattazione
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Erlang_Config', index=False)

        # Ottieni workbook e worksheet
        workbook = writer.book
        worksheet = writer.sheets['Erlang_Config']

        # Formattazione header
        from openpyxl.styles import Font, PatternFill, Alignment

        header_fill = PatternFill(start_color='366092', end_color='366092', fill_type='solid')
        header_font = Font(bold=True, color='FFFFFF')

        for cell in worksheet[1]:
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = Alignment(horizontal='center', vertical='center')

        # Larghezza colonne
        column_widths = {
            'A': 25,  # Skill
            'B': 18,  # AHT_Seconds
            'C': 22,  # Tempo_Pausa_Minuti
            'D': 15,  # Shrinkage
            'E': 22,  # Service_Level_Target
            'F': 25,  # Service_Level_Seconds
            'G': 20,  # Occupancy_Target
            'H': 20,  # Interval_Minutes
            'I': 40   # Note
        }

        for col, width in column_widths.items():
            worksheet.column_dimensions[col].width = width

        # Aggiungi sheet con istruzioni
        istruzioni = pd.DataFrame({
            'ISTRUZIONI PER LA CONFIGURAZIONE ERLANG C': [
                '',
                '=== PARAMETRI ===',
                '',
                'Skill: Codice skill/coda (deve corrispondere a Skills configurati)',
                '',
                'AHT_Seconds: Average Handle Time in secondi',
                '  - Tempo medio gestione chiamata/contatto',
                '  - Include tempo conversazione + after call work',
                '  - Esempio: 180 = 3 minuti',
                '',
                'Tempo_Pausa_Minuti: Minuti pausa per ora (normalmente 0)',
                '  - Pause gestite separatamente nello shrinkage',
                '  - Lasciare a 0 se pause già incluse in Shrinkage',
                '',
                'Shrinkage: Percentuale tempo non produttivo (0-1)',
                '  - Include: pause, formazione, riunioni, assenze',
                '  - Esempio: 0.30 = 30% del tempo non produttivo',
                '  - Tipicamente tra 25% e 35%',
                '',
                'Service_Level_Target: Target Service Level (0-1)',
                '  - Percentuale chiamate da rispondere entro target',
                '  - Esempio: 0.80 = 80% delle chiamate',
                '  - Standard: 0.80 (80/20)',
                '',
                'Service_Level_Seconds: Secondi target risposta',
                '  - Tempo massimo attesa per Service Level',
                '  - Esempio: 20 = entro 20 secondi',
                '  - Standard: 20 secondi (80/20 rule)',
                '',
                'Occupancy_Target: Target occupancy agenti (0-1)',
                '  - Percentuale tempo in chiamata/lavoro',
                '  - Esempio: 0.85 = 85% occupati',
                '  - Tipicamente tra 80% e 90%',
                '',
                'Interval_Minutes: Intervallo calcolo in minuti',
                '  - Tipicamente 30 minuti',
                '  - Deve corrispondere a intervalli forecast',
                '',
                'Note: Descrizione/annotazioni',
                '',
                '=== ESEMPI VALORI TIPICI ===',
                '',
                'Customer Care:',
                '  - AHT: 180-240 secondi (3-4 minuti)',
                '  - Shrinkage: 30%',
                '  - Service Level: 80% in 20 secondi',
                '',
                'Back Office:',
                '  - AHT: 240-360 secondi (4-6 minuti)',
                '  - Shrinkage: 25%',
                '  - Service Level: 75% in 30 secondi',
                '',
                'Technical Support:',
                '  - AHT: 300-600 secondi (5-10 minuti)',
                '  - Shrinkage: 30%',
                '  - Service Level: 80% in 20 secondi',
                '',
                '=== IMPORT ===',
                '',
                'Dopo aver completato la configurazione:',
                '  python scripts/import_erlang_config.py template_erlang_config.xlsx',
                ''
            ]
        })

        istruzioni.to_excel(writer, sheet_name='Istruzioni', index=False, header=False)
        worksheet_istr = writer.sheets['Istruzioni']
        worksheet_istr.column_dimensions['A'].width = 80

        # Formattazione istruzioni
        for row in worksheet_istr.iter_rows():
            for cell in row:
                if cell.value and isinstance(cell.value, str):
                    if cell.value.startswith('==='):
                        cell.font = Font(bold=True, size=12, color='1F4E78')
                    elif cell.value.startswith('  '):
                        cell.font = Font(italic=True, size=10)

    print(f"\n✅ Template creato: {output_file}")
    print("\nColonne create:")
    print("  - Skill: Codice skill/coda")
    print("  - AHT_Seconds: Average Handle Time")
    print("  - Tempo_Pausa_Minuti: Minuti pausa/ora")
    print("  - Shrinkage: % tempo non produttivo")
    print("  - Service_Level_Target: Target % SL")
    print("  - Service_Level_Seconds: Secondi target risposta")
    print("  - Occupancy_Target: Target occupancy")
    print("  - Interval_Minutes: Intervallo calcolo")
    print("  - Note: Annotazioni")
    print("\n4 configurazioni di esempio incluse")
    print("Sheet 'Istruzioni' con guida completa")
    print(f"\nPer importare: python scripts/import_erlang_config.py {output_file}\n")


if __name__ == '__main__':
    output = sys.argv[1] if len(sys.argv) > 1 else 'template_erlang_config.xlsx'
    crea_template_erlang(output)
