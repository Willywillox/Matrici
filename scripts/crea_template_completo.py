"""
Script per creare template Excel UNIFICATO per import completo

Genera un unico file Excel con 3 sheet:
1. Skills - Elenco competenze/skill
2. Turni - Elenco turni standard
3. Operatori - Dati completi operatori

Import in ordine: Skills → Turni → Operatori
"""

import pandas as pd
import sys
import os
from datetime import datetime

def crea_template_unificato(output_file='template_import_completo.xlsx'):
    """Crea template Excel unificato per import completo"""

    print("\n=== CREAZIONE TEMPLATE EXCEL UNIFICATO ===\n")

    # ======= SHEET 1: SKILLS =======
    skills_data = {
        'Codice_Skill': [
            'CUSTOMER_CARE',
            'BACK_OFFICE',
            'TECHNICAL_SUPPORT',
            'SALES',
            'AMMINISTRAZIONE',
            ''
        ],
        'Descrizione': [
            'Assistenza clienti telefonica e chat',
            'Gestione back office e pratiche amministrative',
            'Supporto tecnico avanzato',
            'Vendita e consulenza commerciale',
            'Amministrazione e contabilità',
            ''
        ],
        'Produttivita_Default': [
            1.0,
            1.0,
            0.8,
            1.0,
            1.0,
            None
        ]
    }

    df_skills = pd.DataFrame(skills_data)

    # ======= SHEET 2: TURNI =======
    turni_data = {
        'ID_Turno': ['T1', 'T2', 'T3', 'T4', 'T5', ''],
        'Descrizione': [
            'Turno Mattina Standard',
            'Turno Pomeriggio',
            'Turno Spezzato',
            'Turno Notte',
            'Turno Weekend',
            ''
        ],
        'Ora_Inizio': ['09:00', '14:00', '09:00', '22:00', '08:00', ''],
        'Ora_Fine': ['18:00', '22:00', '13:00', '06:00', '16:00', ''],
        'Ore_Turno': [9.0, 8.0, 8.0, 8.0, 8.0, None],
        'Ora_Inizio_Spezzato': ['', '', '17:00', '', '', ''],
        'Ora_Fine_Spezzato': ['', '', '21:00', '', '', ''],
        'Note': [
            'Turno standard ufficio',
            'Turno pomeridiano',
            'Pausa pranzo 13:00-17:00',
            'Attraversa mezzanotte',
            'Turno ridotto weekend',
            ''
        ]
    }

    df_turni = pd.DataFrame(turni_data)

    # ======= SHEET 3: OPERATORI =======
    operatori_data = {
        # OBBLIGATORI
        'Nome': ['Mario', 'Lucia', 'Giovanni', ''],
        'Cognome': ['Rossi', 'Bianchi', 'Verdi', ''],
        'ID_SAP': ['SAP001', 'SAP002', 'SAP003', ''],
        'Data_Riferimento': ['2025-11-08', '2025-11-08', '2025-11-08', ''],

        # CONTRATTUALI
        'Tipo_Contratto': ['Full Time', 'Part Time', 'Full Time', ''],
        'FTE': [1.0, 0.5, 1.0, ''],
        'Ore_Settimana': [40, 20, 40, ''],

        # TURNO
        'ID_Turno': ['T1', 'T2', 'T1', ''],
        'Ora_Inizio_Turno': ['09:00', '14:00', '09:00', ''],
        'Ora_Fine_Turno': ['18:00', '22:00', '18:00', ''],
        'Ora_Inizio_Turno_Spezzato': ['', '', '', ''],
        'Ora_Fine_Turno_Spezzato': ['', '', '', ''],

        # STRAORDINARI
        'Inizio_Strao_1': ['18:00', '', '', ''],
        'Fine_Strao_1': ['20:00', '', '', ''],
        'Inizio_Strao_2': ['', '', '', ''],
        'Fine_Strao_2': ['', '', '', ''],
        'Inizio_Strao_3': ['', '', '', ''],
        'Fine_Strao_3': ['', '', '', ''],

        # PAUSE
        'Inizio_Pausa_1': ['10:45', '16:30', '10:45', ''],
        'Fine_Pausa_1': ['11:00', '16:45', '11:00', ''],
        'Inizio_Pausa_2': ['13:00', '', '13:00', ''],
        'Fine_Pausa_2': ['14:00', '', '14:00', ''],
        'Inizio_Pausa_3': ['', '', '', ''],
        'Fine_Pausa_3': ['', '', '', ''],
        'Inizio_Pausa_4': ['', '', '', ''],
        'Fine_Pausa_4': ['', '', '', ''],
        'Inizio_Pausa_5': ['', '', '', ''],
        'Fine_Pausa_5': ['', '', '', ''],

        # GIUSTIFICATIVI
        'Tipo_Giust_1': ['', 'Permesso', '', ''],
        'Inizio_Giust_1': ['', '20:00', '', ''],
        'Fine_Giust_1': ['', '22:00', '', ''],
        'Tipo_Giust_2': ['', '', '', ''],
        'Inizio_Giust_2': ['', '', '', ''],
        'Fine_Giust_2': ['', '', '', ''],
        'Tipo_Giust_3': ['', '', '', ''],
        'Inizio_Giust_3': ['', '', '', ''],
        'Fine_Giust_3': ['', '', '', ''],
        'Tipo_Giust_4': ['', '', '', ''],
        'Inizio_Giust_4': ['', '', '', ''],
        'Fine_Giust_4': ['', '', '', ''],
        'Tipo_Giust_5': ['', '', '', ''],
        'Inizio_Giust_5': ['', '', '', ''],
        'Fine_Giust_5': ['', '', '', ''],

        # SKILL E POSTAZIONE
        'Etichetta_Skill': ['CUSTOMER_CARE', 'BACK_OFFICE', 'TECHNICAL_SUPPORT', ''],
        'Postazione': ['Sede', 'Smart Working', 'Sede', ''],
    }

    df_operatori = pd.DataFrame(operatori_data)

    # ======= CREA EXCEL CON FORMATTAZIONE =======
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:

        # === SHEET 1: SKILLS ===
        df_skills.to_excel(writer, sheet_name='Skills', index=False)
        ws_skills = writer.sheets['Skills']

        ws_skills.column_dimensions['A'].width = 25  # Codice_Skill
        ws_skills.column_dimensions['B'].width = 50  # Descrizione
        ws_skills.column_dimensions['C'].width = 20  # Produttivita_Default

        from openpyxl.styles import Font, PatternFill, Alignment

        # Header skills
        header_fill_skills = PatternFill(start_color="9C27B0", end_color="9C27B0", fill_type="solid")
        header_font = Font(bold=True, size=11, color="FFFFFF")

        for cell in ws_skills[1]:
            cell.fill = header_fill_skills
            cell.font = header_font
            cell.alignment = Alignment(horizontal='center', vertical='center')

        # === SHEET 2: TURNI ===
        df_turni.to_excel(writer, sheet_name='Turni', index=False)
        ws_turni = writer.sheets['Turni']

        ws_turni.column_dimensions['A'].width = 12
        ws_turni.column_dimensions['B'].width = 30
        ws_turni.column_dimensions['C'].width = 12
        ws_turni.column_dimensions['D'].width = 12
        ws_turni.column_dimensions['E'].width = 12
        ws_turni.column_dimensions['F'].width = 18
        ws_turni.column_dimensions['G'].width = 18
        ws_turni.column_dimensions['H'].width = 35

        # Header turni
        header_fill_turni = PatternFill(start_color="FF9800", end_color="FF9800", fill_type="solid")

        for cell in ws_turni[1]:
            cell.fill = header_fill_turni
            cell.font = header_font
            cell.alignment = Alignment(horizontal='center', vertical='center')

        # === SHEET 3: OPERATORI ===
        df_operatori.to_excel(writer, sheet_name='Operatori', index=False)
        ws_operatori = writer.sheets['Operatori']

        # Larghezze colonne operatori
        ws_operatori.column_dimensions['A'].width = 12  # Nome
        ws_operatori.column_dimensions['B'].width = 12  # Cognome
        ws_operatori.column_dimensions['C'].width = 12  # ID_SAP
        ws_operatori.column_dimensions['D'].width = 15  # Data

        # Header operatori
        header_fill_operatori = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")

        for cell in ws_operatori[1]:
            cell.fill = header_fill_operatori
            cell.font = header_font
            cell.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)

        # === SHEET 4: ISTRUZIONI ===
        istruzioni = pd.DataFrame({
            'GUIDA IMPORT COMPLETO': [
                '',
                '=== TEMPLATE EXCEL UNIFICATO ===',
                '',
                'Questo file contiene TUTTO il necessario per configurare Matrici:',
                '',
                '📋 Sheet 1: SKILLS',
                '   Elenco delle competenze/skill disponibili',
                '   Es: CUSTOMER_CARE, BACK_OFFICE, TECHNICAL_SUPPORT',
                '',
                '🕐 Sheet 2: TURNI',
                '   Elenco dei turni standard (orari fissi)',
                '   Es: T1 (09:00-18:00), T2 (14:00-22:00)',
                '',
                '👥 Sheet 3: OPERATORI',
                '   Dati completi degli operatori',
                '   Include: anagrafica, turni, straordinari, pause, giustificativi, skill',
                '',
                '=== ORDINE DI IMPORT ===',
                '',
                'IMPORTANTE: Lo script importa automaticamente nell\'ordine corretto:',
                '',
                '1️⃣ SKILLS (prima)',
                '   Devono esistere prima di assegnarle agli operatori',
                '',
                '2️⃣ TURNI (secondo)',
                '   Devono esistere prima di assegnarli agli operatori',
                '',
                '3️⃣ OPERATORI (ultimo)',
                '   Possono usare Skills e Turni già importati',
                '',
                '=== COME COMPILARE ===',
                '',
                '📋 SHEET SKILLS:',
                '• Codice_Skill: Codice univoco (es: CUSTOMER_CARE)',
                '• Descrizione: Descrizione della skill (opzionale)',
                '• Produttivita_Default: Valore 0-1 (1.0 = 100%, opzionale)',
                '',
                'Esempi forniti:',
                '- CUSTOMER_CARE: Assistenza clienti',
                '- BACK_OFFICE: Gestione pratiche',
                '- TECHNICAL_SUPPORT: Supporto tecnico',
                '',
                '🕐 SHEET TURNI:',
                '• ID_Turno: Codice univoco (es: T1, T2)',
                '• Descrizione: Nome turno (opzionale)',
                '• Ora_Inizio, Ora_Fine: Formato HH:MM',
                '• Ore_Turno: Totale ore (opzionale, calcolato auto)',
                '• Turno spezzato: Opzionale (es: 09:00-13:00 + 17:00-21:00)',
                '',
                'Esempi forniti:',
                '- T1: Turno mattina 09:00-18:00',
                '- T2: Turno pomeriggio 14:00-22:00',
                '- T3: Turno spezzato con pausa lunga',
                '',
                '👥 SHEET OPERATORI:',
                '• Campi OBBLIGATORI (4):',
                '  - Nome, Cognome, ID_SAP, Data_Riferimento',
                '',
                '• Campi OPZIONALI:',
                '  - Tipo_Contratto, FTE, Ore_Settimana',
                '  - ID_Turno (deve esistere in sheet Turni!)',
                '  - Orari turno (se non usi ID_Turno)',
                '  - Straordinari (3 slot)',
                '  - Pause (5 slot)',
                '  - Giustificativi (5 slot)',
                '  - Etichetta_Skill (deve esistere in sheet Skills!)',
                '  - Postazione (Sede, Smart Working, ecc.)',
                '',
                '=== ESECUZIONE IMPORT ===',
                '',
                'PASSO 1: Compila i 3 sheet',
                '  - Skills: Aggiungi le tue competenze',
                '  - Turni: Aggiungi i tuoi orari standard',
                '  - Operatori: Aggiungi i tuoi operatori',
                '',
                'PASSO 2: Salva il file Excel',
                '',
                'PASSO 3: Esegui lo script di import',
                '',
                '  cd C:\\Matrici',
                '  python scripts/import_completo.py template_import_completo.xlsx',
                '',
                'PASSO 4: Controlla il report',
                '  Lo script mostra:',
                '  ✓ Quante skills importate',
                '  ✓ Quanti turni importati',
                '  ✓ Quanti operatori importati',
                '  ✗ Eventuali errori',
                '',
                '=== VANTAGGI TEMPLATE UNIFICATO ===',
                '',
                '✅ Un solo file da gestire',
                '✅ Import automatico in ordine corretto',
                '✅ Validazione automatica (Skills e Turni esistono)',
                '✅ Report completo di tutto l\'import',
                '✅ Esempi precompilati per ogni sheet',
                '',
                '=== RIFERIMENTI INCROCIATI ===',
                '',
                'IMPORTANTE: Gli operatori fanno riferimento a Skills e Turni:',
                '',
                'Esempio Operatore:',
                '  Nome: Mario',
                '  ID_Turno: T1  ← deve esistere in sheet Turni',
                '  Etichetta_Skill: CUSTOMER_CARE  ← deve esistere in sheet Skills',
                '',
                'Lo script controlla automaticamente questi riferimenti!',
                '',
                '=== REIMPORT E AGGIORNAMENTI ===',
                '',
                '✓ Skills: Se codice già esiste → SKIP (non duplica)',
                '✓ Turni: Se ID già esiste → SKIP (non duplica)',
                '✓ Operatori: Se ID_SAP+Data esistono → AGGIORNA dati',
                '',
                'Puoi reimportare lo stesso file più volte senza problemi!',
                '',
                '=== ERRORI COMUNI ===',
                '',
                'Q: "Skill non trovata"',
                'A: Assicurati che la skill sia nello sheet Skills prima',
                '',
                'Q: "Turno non trovato"',
                'A: Assicurati che l\'ID_Turno sia nello sheet Turni',
                '',
                'Q: "Formato data errato"',
                'A: Usa formato YYYY-MM-DD (es: 2025-11-08)',
                '',
                'Q: "Formato orario errato"',
                'A: Usa formato HH:MM (es: 09:00)',
                '',
                '=== ESEMPIO COMPLETO ===',
                '',
                'Sheet Skills:',
                '  CUSTOMER_CARE | Assistenza clienti | 1.0',
                '',
                'Sheet Turni:',
                '  T1 | Turno Mattina | 09:00 | 18:00 | 9.0',
                '',
                'Sheet Operatori:',
                '  Mario | Rossi | SAP001 | 2025-11-08',
                '  Turno: T1',
                '  Skill: CUSTOMER_CARE',
                '',
                'Import:',
                '  1. Importa skill CUSTOMER_CARE',
                '  2. Importa turno T1',
                '  3. Importa operatore Mario con turno T1 e skill CUSTOMER_CARE',
                '',
                '✅ Tutto corretto!',
                '',
            ]
        })

        istruzioni.to_excel(writer, sheet_name='Istruzioni', index=False, header=False)
        ws_istr = writer.sheets['Istruzioni']
        ws_istr.column_dimensions['A'].width = 85

        # Grassetto per titoli
        bold_font = Font(bold=True, size=12)
        for row_idx in [2, 16, 28, 58, 74, 91, 108, 118, 130]:
            ws_istr[f'A{row_idx}'].font = bold_font

    print(f"✅ Template unificato creato: {output_file}")
    print(f"\nIl file contiene:")
    print(f"  📋 Sheet 'Skills': 5 esempi + riga vuota")
    print(f"  🕐 Sheet 'Turni': 5 esempi + riga vuota")
    print(f"  👥 Sheet 'Operatori': 3 esempi + riga vuota")
    print(f"  📖 Sheet 'Istruzioni': Guida completa")
    print(f"\nProssimi passi:")
    print(f"  1. Apri {output_file} con Excel")
    print(f"  2. Compila i 3 sheet (Skills, Turni, Operatori)")
    print(f"  3. Salva il file")
    print(f"  4. Import: python scripts/import_completo.py {output_file}")
    print(f"\nIMPORTANTE: Lo script importa automaticamente nell'ordine:")
    print(f"  1️⃣ Skills → 2️⃣ Turni → 3️⃣ Operatori")
    print()


if __name__ == '__main__':
    if len(sys.argv) > 1:
        output_file = sys.argv[1]
    else:
        output_file = 'template_import_completo.xlsx'

    try:
        crea_template_unificato(output_file)
        print("✅ Template creato con successo!\n")
    except Exception as e:
        print(f"❌ Errore durante la creazione del template: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
