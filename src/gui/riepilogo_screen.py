"""
Schermata Riepilogo con aggregazioni giorno/settimana/mese
"""
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime, timedelta
import pandas as pd
from tkcalendar import DateEntry


class RiepilogoScreen(ttk.Frame):
    """Schermata riepilogo con report aggregati"""

    def __init__(self, parent, db_manager):
        super().__init__(parent)
        self.db_manager = db_manager
        self.current_report_data = None
        self.setup_ui()

    def setup_ui(self):
        """Crea l'interfaccia"""
        # === PANNELLO CONTROLLI ===
        control_frame = ttk.LabelFrame(self, text="Parametri Report", padding=10)
        control_frame.pack(fill='x', padx=10, pady=10)

        # Row 1: Tipo report
        row1 = ttk.Frame(control_frame)
        row1.pack(fill='x', pady=5)

        ttk.Label(row1, text="Tipo Riepilogo:", font=('Arial', 10, 'bold')).pack(side='left', padx=5)

        self.report_type_var = tk.StringVar(value='giornaliero')
        ttk.Radiobutton(row1, text="Giornaliero", variable=self.report_type_var,
                       value='giornaliero', command=self.on_report_type_change).pack(side='left', padx=5)
        ttk.Radiobutton(row1, text="Settimanale", variable=self.report_type_var,
                       value='settimanale', command=self.on_report_type_change).pack(side='left', padx=5)
        ttk.Radiobutton(row1, text="Mensile", variable=self.report_type_var,
                       value='mensile', command=self.on_report_type_change).pack(side='left', padx=5)

        # Row 2: Periodo
        row2 = ttk.Frame(control_frame)
        row2.pack(fill='x', pady=5)

        ttk.Label(row2, text="Data Inizio:", font=('Arial', 10, 'bold')).pack(side='left', padx=5)
        self.date_start_var = tk.StringVar(value=datetime.now().strftime('%d/%m/%Y'))
        self.date_start_entry = DateEntry(row2, textvariable=self.date_start_var,
                                          width=12, date_pattern='dd/mm/yyyy')
        self.date_start_entry.pack(side='left', padx=5)

        ttk.Label(row2, text="Data Fine:", font=('Arial', 10, 'bold')).pack(side='left', padx=(20, 5))
        self.date_end_var = tk.StringVar(value=datetime.now().strftime('%d/%m/%Y'))
        self.date_end_entry = DateEntry(row2, textvariable=self.date_end_var,
                                        width=12, date_pattern='dd/mm/yyyy')
        self.date_end_entry.pack(side='left', padx=5)

        # Row 3: Vista
        row3 = ttk.Frame(control_frame)
        row3.pack(fill='x', pady=5)

        ttk.Label(row3, text="Vista:", font=('Arial', 10, 'bold')).pack(side='left', padx=5)

        self.view_type_var = tk.StringVar(value='servizio')
        ttk.Radiobutton(row3, text="Per Servizio/Skill", variable=self.view_type_var,
                       value='servizio').pack(side='left', padx=5)
        ttk.Radiobutton(row3, text="Per Persona", variable=self.view_type_var,
                       value='persona').pack(side='left', padx=5)

        # Row 4: Bottoni
        row4 = ttk.Frame(control_frame)
        row4.pack(fill='x', pady=10)

        ttk.Button(row4, text="📊 Genera Report", command=self.generate_report,
                  width=20).pack(side='left', padx=5)
        ttk.Button(row4, text="📁 Esporta Excel", command=self.export_excel,
                  width=20).pack(side='left', padx=5)

        # === NOTEBOOK PER TABS ===
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)

        # Tab 1: Riepilogo
        self.tab_summary = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_summary, text='Riepilogo Generale')
        self.setup_summary_tab()

        # Tab 2: Dettaglio
        self.tab_detail = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_detail, text='Dettaglio per Periodo')
        self.setup_detail_tab()

        # Tab 3: Grafici
        self.tab_charts = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_charts, text='Grafici (In sviluppo)')
        ttk.Label(self.tab_charts, text="Grafici e visualizzazioni - In sviluppo",
                 font=('Arial', 14)).pack(expand=True)

    def setup_summary_tab(self):
        """Setup tab riepilogo generale"""
        # Frame per cards
        cards_frame = ttk.Frame(self.tab_summary)
        cards_frame.pack(fill='x', padx=10, pady=10)

        self.summary_cards = {}

        # Row 1: Ore
        row1_metrics = [
            ('ore_produzione', 'Ore Produzione', '#2196F3'),
            ('ore_ordinarie', 'Ore Ordinarie', '#4CAF50'),
            ('ore_strao', 'Ore Straordinario', '#9C27B0'),
            ('estensione_strao', 'Estensione Strao %', '#FF5722'),
        ]

        for i, (key, label, color) in enumerate(row1_metrics):
            card = ttk.Frame(cards_frame, relief='raised', borderwidth=2)
            card.grid(row=0, column=i, padx=10, pady=5, sticky='ew')
            cards_frame.columnconfigure(i, weight=1)

            ttk.Label(card, text=label, font=('Arial', 9)).pack(pady=(5, 0))
            value_label = ttk.Label(card, text="--", font=('Arial', 16, 'bold'),
                                   foreground=color)
            value_label.pack(pady=(0, 5))
            self.summary_cards[key] = value_label

        # Row 2: Assenze e Metriche
        row2_metrics = [
            ('ore_assenze', 'Ore Assenze Totali', '#FF9800'),
            ('ore_pianificate', 'Ore Pianificate', '#009688'),
            ('assenteismo', 'Assenteismo %', '#F44336'),
            ('ore_pausa', 'Ore Pausa', '#795548'),
        ]

        for i, (key, label, color) in enumerate(row2_metrics):
            card = ttk.Frame(cards_frame, relief='raised', borderwidth=2)
            card.grid(row=1, column=i, padx=10, pady=5, sticky='ew')

            ttk.Label(card, text=label, font=('Arial', 9)).pack(pady=(5, 0))
            value_label = ttk.Label(card, text="--", font=('Arial', 16, 'bold'),
                                   foreground=color)
            value_label.pack(pady=(0, 5))
            self.summary_cards[key] = value_label

        # Tabella summary
        table_frame = ttk.LabelFrame(self.tab_summary, text="Riepilogo per Skill/Persona",
                                     padding=10)
        table_frame.pack(fill='both', expand=True, padx=10, pady=10)

        scroll_y = ttk.Scrollbar(table_frame, orient='vertical')
        scroll_y.pack(side='right', fill='y')

        self.tree_summary = ttk.Treeview(table_frame, show='headings',
                                         yscrollcommand=scroll_y.set, height=15)
        scroll_y.config(command=self.tree_summary.yview)
        self.tree_summary.pack(fill='both', expand=True)

    def setup_detail_tab(self):
        """Setup tab dettaglio per periodo"""
        # Tabella dettaglio
        table_frame = ttk.Frame(self.tab_detail)
        table_frame.pack(fill='both', expand=True, padx=10, pady=10)

        # Scrollbars
        scroll_y = ttk.Scrollbar(table_frame, orient='vertical')
        scroll_y.pack(side='right', fill='y')

        scroll_x = ttk.Scrollbar(table_frame, orient='horizontal')
        scroll_x.pack(side='bottom', fill='x')

        self.tree_detail = ttk.Treeview(table_frame, show='headings',
                                        yscrollcommand=scroll_y.set,
                                        xscrollcommand=scroll_x.set, height=20)

        scroll_y.config(command=self.tree_detail.yview)
        scroll_x.config(command=self.tree_detail.xview)
        self.tree_detail.pack(fill='both', expand=True)

    def on_report_type_change(self):
        """Gestisce cambio tipo report"""
        report_type = self.report_type_var.get()

        # Imposta date suggerite
        today = datetime.now()

        if report_type == 'giornaliero':
            self.date_start_var.set(today.strftime('%d/%m/%Y'))
            self.date_end_var.set(today.strftime('%d/%m/%Y'))

        elif report_type == 'settimanale':
            # Lunedì di questa settimana
            monday = today - timedelta(days=today.weekday())
            sunday = monday + timedelta(days=6)
            self.date_start_var.set(monday.strftime('%d/%m/%Y'))
            self.date_end_var.set(sunday.strftime('%d/%m/%Y'))

        elif report_type == 'mensile':
            # Primo e ultimo giorno del mese
            first_day = today.replace(day=1)
            if today.month == 12:
                last_day = today.replace(day=31)
            else:
                last_day = (today.replace(month=today.month + 1, day=1) - timedelta(days=1))
            self.date_start_var.set(first_day.strftime('%d/%m/%Y'))
            self.date_end_var.set(last_day.strftime('%d/%m/%Y'))

    def generate_report(self):
        """Genera il report"""
        try:
            from models.operatore import Operatore
            from utils.capability_calculator import CapabilityCalculator

            # Parse date (da formato italiano dd/mm/yyyy)
            data_inizio = datetime.strptime(self.date_start_var.get(), '%d/%m/%Y')
            data_fine = datetime.strptime(self.date_end_var.get(), '%d/%m/%Y')

            if data_fine < data_inizio:
                messagebox.showwarning("Attenzione", "La data fine deve essere >= data inizio")
                return

            view_type = self.view_type_var.get()

            # Carica dati per il periodo
            self.db_manager.connect()

            # Raccogliamo dati per ogni giorno del periodo
            all_operatori = []
            current_date = data_inizio

            while current_date <= data_fine:
                operatori_data = self.db_manager.get_operatori(current_date.strftime('%Y-%m-%d'))

                for row in operatori_data:
                    op_dict = self._row_to_dict(row)
                    op = Operatore(**op_dict)
                    all_operatori.append(op)

                current_date += timedelta(days=1)

            if not all_operatori:
                messagebox.showinfo("Info", "Nessun operatore trovato per il periodo selezionato.")
                self.db_manager.close()
                return

            # Calcola rendiconto
            calculator = CapabilityCalculator(all_operatori)

            if view_type == 'servizio':
                df_report = calculator.calcola_rendiconto_per_servizio(data_inizio, data_fine)
                self.populate_service_report(df_report)
            else:
                df_report = calculator.calcola_rendiconto_per_persona(data_inizio, data_fine)
                self.populate_person_report(df_report)

            # Salva per export
            self.current_report_data = df_report

            # Aggiorna summary cards
            self.update_summary_cards(df_report, view_type)

            self.db_manager.close()

            messagebox.showinfo("Successo", f"Report generato per periodo:\n"
                                           f"{data_inizio.strftime('%d/%m/%Y')} - {data_fine.strftime('%d/%m/%Y')}")

        except Exception as e:
            messagebox.showerror("Errore", f"Errore nella generazione report:\n{e}")
            import traceback
            traceback.print_exc()

    def populate_service_report(self, df):
        """Popola report per servizio"""
        # Summary tab
        self.tree_summary['columns'] = list(df.columns)
        self.tree_summary['show'] = 'headings'

        for col in df.columns:
            self.tree_summary.heading(col, text=col.replace('_', ' '))
            self.tree_summary.column(col, width=150, anchor='center')

        # Clear
        for item in self.tree_summary.get_children():
            self.tree_summary.delete(item)

        # Populate
        for _, row in df.iterrows():
            self.tree_summary.insert('', 'end', values=tuple(row))

        # Detail tab - stessa cosa per ora
        self.tree_detail['columns'] = list(df.columns)
        self.tree_detail['show'] = 'headings'

        for col in df.columns:
            self.tree_detail.heading(col, text=col.replace('_', ' '))
            self.tree_detail.column(col, width=150, anchor='center')

        for item in self.tree_detail.get_children():
            self.tree_detail.delete(item)

        for _, row in df.iterrows():
            self.tree_detail.insert('', 'end', values=tuple(row))

    def populate_person_report(self, df):
        """Popola report per persona"""
        self.populate_service_report(df)  # Stessa logica

    def update_summary_cards(self, df, view_type):
        """Aggiorna le cards summary"""
        # Entrambe le viste ora hanno le stesse colonne
        ore_produzione = df['Ore_Produzione'].sum()
        ore_ordinarie = df['Ore_Ordinarie_Turno'].sum()
        ore_pausa = df['Ore_Pausa'].sum()
        ore_strao = df['Ore_Straordinario'].sum()
        ore_assenze = df['Ore_Assenze_Totali'].sum()
        ore_pianificate = df['Ore_Pianificate'].sum()

        # Calcola medie ponderate per le percentuali
        if ore_ordinarie > 0:
            estensione_strao = (ore_strao / ore_ordinarie) * 100
        else:
            estensione_strao = 0

        if ore_pianificate > 0:
            assenteismo = (ore_assenze / ore_pianificate) * 100
        else:
            assenteismo = 0

        self.summary_cards['ore_produzione'].config(text=f"{ore_produzione:.1f} h")
        self.summary_cards['ore_ordinarie'].config(text=f"{ore_ordinarie:.1f} h")
        self.summary_cards['ore_pausa'].config(text=f"{ore_pausa:.1f} h")
        self.summary_cards['ore_strao'].config(text=f"{ore_strao:.1f} h")
        self.summary_cards['ore_assenze'].config(text=f"{ore_assenze:.1f} h")
        self.summary_cards['ore_pianificate'].config(text=f"{ore_pianificate:.1f} h")
        self.summary_cards['estensione_strao'].config(text=f"{estensione_strao:.1f}%")
        self.summary_cards['assenteismo'].config(text=f"{assenteismo:.1f}%")

    def export_excel(self):
        """Esporta report in Excel"""
        if self.current_report_data is None or self.current_report_data.empty:
            messagebox.showwarning("Attenzione", "Nessun report da esportare.\nGenera prima il report.")
            return

        try:
            filename = filedialog.asksaveasfilename(
                defaultextension='.xlsx',
                filetypes=[('Excel files', '*.xlsx'), ('All files', '*.*')],
                initialfile=f"Report_{self.date_start_var.get()}_{self.date_end_var.get()}.xlsx"
            )

            if not filename:
                return

            # Export
            with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                self.current_report_data.to_excel(writer, index=False, sheet_name='Riepilogo')

                # Aggiungi sheet con info
                info_data = {
                    'Parametro': ['Data Inizio', 'Data Fine', 'Tipo Report', 'Vista'],
                    'Valore': [
                        self.date_start_var.get(),
                        self.date_end_var.get(),
                        self.report_type_var.get(),
                        self.view_type_var.get()
                    ]
                }
                pd.DataFrame(info_data).to_excel(writer, index=False, sheet_name='Info')

            messagebox.showinfo("Successo", f"Report esportato in:\n{filename}")

        except Exception as e:
            messagebox.showerror("Errore", f"Errore nell'esportazione:\n{e}")

    def _row_to_dict(self, row):
        """Converte row database in dict"""
        if hasattr(row, 'cursor_description'):
            return {desc[0]: getattr(row, desc[0]) for desc in row.cursor_description}
        return {}
