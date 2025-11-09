#!/usr/bin/env python3
"""
Script per aggiornare il foglio Istruzioni con informazioni sui fogli Forecast e Richiesto
"""

import openpyxl
from openpyxl.styles import Font, Alignment, PatternFill
import sys

def update_instructions(workbook):
    """Aggiorna il foglio Istruzioni con informazioni sui fogli Forecast e Richiesto"""

    if 'Istruzioni' not in workbook.sheetnames:
        print("Foglio 'Istruzioni' non trovato, creazione nuovo foglio...")
        ws = workbook.create_sheet('Istruzioni')
    else:
        ws = workbook['Istruzioni']
        # Pulisci il contenuto esistente
        ws.delete_rows(1, ws.max_row)

    # Stili
    title_font = Font(bold=True, size=16, color="1F4E78")
    header_font = Font(bold=True, size=12, color="FFFFFF")
    header_fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
    section_font = Font(bold=True, size=11, color="203864")
    normal_font = Font(size=10)

    row = 1

    # Titolo
    ws[f'A{row}'] = "ISTRUZIONI - Template Import Completo"
    ws[f'A{row}'].font = title_font
    row += 2

    # Sezione 1: Panoramica
    ws[f'A{row}'] = "1. PANORAMICA"
    ws[f'A{row}'].font = section_font
    row += 1

    ws[f'A{row}'] = "Questo template Excel contiene 10 fogli organizzati in 3 categorie:"
    ws[f'A{row}'].font = normal_font
    row += 1

    ws[f'A{row}'] = "  • FOGLI BASE: Skills, Turni, Operatori, Istruzioni"
    row += 1
    ws[f'A{row}'] = "  • FOGLI FORECAST: FC_[SKILL] - Previsione volumi per skill (intervalli 15 min)"
    row += 1
    ws[f'A{row}'] = "  • FOGLI RICHIESTO: RQ_[SKILL] - Risorse richieste calcolate con Erlang (intervalli 15 min)"
    row += 2

    # Sezione 2: Fogli Base
    ws[f'A{row}'] = "2. FOGLI BASE"
    ws[f'A{row}'].font = section_font
    row += 1

    ws[f'A{row}'] = "2.1 SKILLS"
    ws[f'A{row}'].font = Font(bold=True, size=10)
    row += 1
    ws[f'A{row}'] = "  Define le competenze/skill disponibili nel sistema."
    row += 1
    ws[f'A{row}'] = "  Colonne obbligatorie:"
    row += 1
    ws[f'A{row}'] = "    - Codice_Skill: Codice univoco dello skill (es: FL_PS_PA, BO_PS_PA, CMB)"
    row += 1
    ws[f'A{row}'] = "    - Descrizione: Descrizione dello skill (opzionale)"
    row += 1
    ws[f'A{row}'] = "    - Produttivita_Default: Valore da 0 a 1 (1.0 = 100%) (opzionale)"
    row += 2

    ws[f'A{row}'] = "2.2 TURNI"
    ws[f'A{row}'].font = Font(bold=True, size=10)
    row += 1
    ws[f'A{row}'] = "  Define i pattern di turni standard."
    row += 1
    ws[f'A{row}'] = "  Colonne principali: ID_Turno, Descrizione, Ora_Inizio, Ora_Fine, Ore_Turno"
    row += 2

    ws[f'A{row}'] = "2.3 OPERATORI"
    ws[f'A{row}'].font = Font(bold=True, size=10)
    row += 1
    ws[f'A{row}'] = "  Contiene i dati degli operatori con assegnazione turni e skill."
    row += 1
    ws[f'A{row}'] = "  Colonne obbligatorie: Nome, Cognome, ID_SAP, Data_Riferimento"
    row += 1
    ws[f'A{row}'] = "  Colonna Etichetta_Skill: Seleziona skill dalla lista a tendina (validazione automatica)"
    row += 2

    # Sezione 3: Fogli Forecast
    ws[f'A{row}'] = "3. FOGLI FORECAST (FC_)"
    ws[f'A{row}'].font = section_font
    row += 1

    ws[f'A{row}'] = "Ogni skill ha un foglio forecast dedicato con prefisso FC_ (es: FC_FL_PS_PA)"
    row += 1
    ws[f'A{row}'] = "Struttura:"
    row += 1
    ws[f'A{row}'] = "  • Colonna A: Data (formato DD/MM/YYYY)"
    row += 1
    ws[f'A{row}'] = "  • Colonne B-CU (96 colonne): Fasce orarie di 15 minuti"
    row += 1
    ws[f'A{row}'] = "    - 00:00-00:15, 00:15-00:30, ..., 23:45-00:00"
    row += 1
    ws[f'A{row}'] = "    - Valori: Numero intero (volume previsto per quella fascia oraria)"
    row += 2

    ws[f'A{row}'] = "Utilizzo in Dashboard:"
    row += 1
    ws[f'A{row}'] = "  1. Inserisci le date nella colonna A"
    row += 1
    ws[f'A{row}'] = "  2. Inserisci i volumi previsti per ogni fascia oraria"
    row += 1
    ws[f'A{row}'] = "  3. Filtra per data in dashboard per visualizzare forecast e confrontarlo con richiesto"
    row += 2

    # Sezione 4: Fogli Richiesto
    ws[f'A{row}'] = "4. FOGLI RICHIESTO (RQ_)"
    ws[f'A{row}'].font = section_font
    row += 1

    ws[f'A{row}'] = "Ogni skill ha un foglio richiesto con prefisso RQ_ (es: RQ_FL_PS_PA)"
    row += 1
    ws[f'A{row}'] = "Struttura identica ai fogli Forecast:"
    row += 1
    ws[f'A{row}'] = "  • Colonna A: Data (formato DD/MM/YYYY)"
    row += 1
    ws[f'A{row}'] = "  • Colonne B-CU (96 colonne): Fasce orarie di 15 minuti"
    row += 1
    ws[f'A{row}'] = "    - Valori: Numero decimale (risorse richieste calcolate con Erlang)"
    row += 2

    ws[f'A{row}'] = "Utilizzo:"
    row += 1
    ws[f'A{row}'] = "  1. I valori vengono calcolati automaticamente tramite formula Erlang C"
    row += 1
    ws[f'A{row}'] = "  2. Input: Dati forecast (FC_) + parametri SLA (tempo medio, livello servizio)"
    row += 1
    ws[f'A{row}'] = "  3. Output: Numero di risorse necessarie per ogni fascia oraria"
    row += 1
    ws[f'A{row}'] = "  4. Confronta con capacità disponibile per pianificare assunzioni/turni"
    row += 2

    # Sezione 5: Workflow
    ws[f'A{row}'] = "5. WORKFLOW CONSIGLIATO"
    ws[f'A{row}'].font = section_font
    row += 1

    ws[f'A{row}'] = "Ordine di compilazione:"
    row += 1
    ws[f'A{row}'] = "  1. Compila foglio SKILLS con tutti gli skill disponibili"
    row += 1
    ws[f'A{row}'] = "  2. Compila foglio TURNI con i pattern di turno"
    row += 1
    ws[f'A{row}'] = "  3. Compila foglio OPERATORI (usa combo box per selezionare skill)"
    row += 1
    ws[f'A{row}'] = "  4. Compila fogli FORECAST (FC_) con volumi previsti per ogni skill"
    row += 1
    ws[f'A{row}'] = "  5. Calcola fogli RICHIESTO (RQ_) con Erlang C (tramite dashboard/tool)"
    row += 1
    ws[f'A{row}'] = "  6. Analizza gap tra richiesto e disponibile in dashboard"
    row += 2

    # Sezione 6: Note
    ws[f'A{row}'] = "6. NOTE IMPORTANTI"
    ws[f'A{row}'].font = section_font
    row += 1

    ws[f'A{row}'] = "  • Le date nei fogli Forecast e Richiesto devono coincidere per confronto corretto"
    row += 1
    ws[f'A{row}'] = "  • I codici skill devono essere univoci e coerenti in tutti i fogli"
    row += 1
    ws[f'A{row}'] = "  • Le fasce orarie di 15 minuti coprono l'intera giornata (96 intervalli)"
    row += 1
    ws[f'A{row}'] = "  • I fogli Forecast e Richiesto si aggiornano automaticamente quando aggiungi/rimuovi skill"
    row += 1

    # Imposta larghezza colonna
    ws.column_dimensions['A'].width = 100

    # Wrap text per tutte le celle
    for row_cells in ws.iter_rows():
        for cell in row_cells:
            cell.alignment = Alignment(wrap_text=True, vertical='top')

    print("✓ Foglio Istruzioni aggiornato con successo")

def main():
    template_path = '/home/user/Matrici/template_import_completo.xlsx'

    try:
        print(f"Caricamento template: {template_path}")
        wb = openpyxl.load_workbook(template_path)

        print("\nAggiornamento foglio Istruzioni...")
        update_instructions(wb)

        print(f"\nSalvataggio template...")
        wb.save(template_path)
        print(f"✓ Template salvato: {template_path}")

        return 0

    except Exception as e:
        print(f"\nERRORE: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1

if __name__ == '__main__':
    sys.exit(main())
