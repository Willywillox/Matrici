"""
Finestra principale dell'applicazione
"""
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime, timedelta
import sys
import os

# Aggiungi path per import
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from database.db_manager import DatabaseManager
from models.operatore import Operatore
from utils.capability_calculator import CapabilityCalculator


class MainWindow:
    """Finestra principale dell'applicazione"""

    def __init__(self, root):
        self.root = root
        self.root.title("Matrici - Gestione Turni e Capability Operatori")
        self.root.geometry("1400x800")

        # Database
        self.db_path = 'data/operator_overtime.db'  # Usa SQLite per sviluppo
        self.db_manager = DatabaseManager(self.db_path)

        # Data corrente
        self.data_corrente = datetime.now()

        # Setup GUI
        self.setup_menu()
        self.setup_main_layout()

    def setup_menu(self):
        """Crea la barra menu"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # Menu File
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Importa Dati Excel", command=self.importa_dati)
        file_menu.add_command(label="Esporta Report", command=self.esporta_report)
        file_menu.add_separator()
        file_menu.add_command(label="Esci", command=self.root.quit)

        # Menu Database
        db_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Database", menu=db_menu)
        db_menu.add_command(label="Crea/Inizializza Database", command=self.init_database)
        db_menu.add_command(label="Backup Database", command=self.backup_database)

        # Menu Aiuto
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Aiuto", menu=help_menu)
        help_menu.add_command(label="Manuale", command=self.show_help)
        help_menu.add_command(label="Info", command=self.show_about)

    def setup_main_layout(self):
        """Crea il layout principale con tab"""
        # Notebook per tab
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=5, pady=5)

        # Tab Dashboard
        self.tab_dashboard = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_dashboard, text='Dashboard')
        self.setup_dashboard_tab()

        # Tab Gestione Operatori
        self.tab_operatori = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_operatori, text='Gestione Operatori')
        self.setup_operatori_tab()

        # Tab Report
        self.tab_report = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_report, text='Report')
        self.setup_report_tab()

        # Tab Forecast
        self.tab_forecast = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_forecast, text='Forecast')
        self.setup_forecast_tab()

    def setup_dashboard_tab(self):
        """Setup tab Dashboard con capability intraday"""
        # Frame controlli
        control_frame = ttk.Frame(self.tab_dashboard)
        control_frame.pack(fill='x', padx=5, pady=5)

        # Selezione data
        ttk.Label(control_frame, text="Data:").pack(side='left', padx=5)
        self.date_var = tk.StringVar(value=self.data_corrente.strftime('%Y-%m-%d'))
        self.date_entry = ttk.Entry(control_frame, textvariable=self.date_var, width=12)
        self.date_entry.pack(side='left', padx=5)

        # Selezione intervallo
        ttk.Label(control_frame, text="Intervallo:").pack(side='left', padx=5)
        self.interval_var = tk.StringVar(value='15')
        interval_combo = ttk.Combobox(control_frame, textvariable=self.interval_var,
                                       values=['15', '30'], width=5, state='readonly')
        interval_combo.pack(side='left', padx=5)

        # Selezione skill (filtro)
        ttk.Label(control_frame, text="Skill:").pack(side='left', padx=5)
        self.skill_var = tk.StringVar(value='Tutti')
        self.skill_combo = ttk.Combobox(control_frame, textvariable=self.skill_var,
                                         values=['Tutti'], width=20, state='readonly')
        self.skill_combo.pack(side='left', padx=5)

        # Bottone aggiorna
        ttk.Button(control_frame, text="Aggiorna", command=self.aggiorna_dashboard).pack(side='left', padx=10)

        # Bottone esporta
        ttk.Button(control_frame, text="Esporta Excel", command=self.esporta_dashboard).pack(side='left', padx=5)

        # Frame per tabella
        table_frame = ttk.Frame(self.tab_dashboard)
        table_frame.pack(fill='both', expand=True, padx=5, pady=5)

        # Scrollbar
        scrollbar_y = ttk.Scrollbar(table_frame, orient='vertical')
        scrollbar_y.pack(side='right', fill='y')

        scrollbar_x = ttk.Scrollbar(table_frame, orient='horizontal')
        scrollbar_x.pack(side='bottom', fill='x')

        # Treeview per dati
        columns = ('Fascia', 'Skill', 'Presenti', 'In_Pausa', 'In_Produzione',
                   'In_Strao', 'FTE_Eff', 'FTE_Rich', 'Delta', 'Copertura%')

        self.tree_dashboard = ttk.Treeview(table_frame, columns=columns, show='headings',
                                            yscrollcommand=scrollbar_y.set,
                                            xscrollcommand=scrollbar_x.set)

        scrollbar_y.config(command=self.tree_dashboard.yview)
        scrollbar_x.config(command=self.tree_dashboard.xview)

        # Colonne
        for col in columns:
            self.tree_dashboard.heading(col, text=col)
            width = 100 if col == 'Fascia' else 80
            self.tree_dashboard.column(col, width=width, anchor='center')

        self.tree_dashboard.pack(fill='both', expand=True)

        # Bind double-click per dettagli
        self.tree_dashboard.bind('<Double-1>', self.show_fascia_detail)

        # Frame summary
        summary_frame = ttk.Frame(self.tab_dashboard)
        summary_frame.pack(fill='x', padx=5, pady=5)

        self.summary_label = ttk.Label(summary_frame, text="", font=('Arial', 10, 'bold'))
        self.summary_label.pack(pady=5)

    def setup_operatori_tab(self):
        """Setup tab Gestione Operatori"""
        # Frame controlli
        control_frame = ttk.Frame(self.tab_operatori)
        control_frame.pack(fill='x', padx=5, pady=5)

        ttk.Button(control_frame, text="Nuovo Operatore", command=self.nuovo_operatore).pack(side='left', padx=5)
        ttk.Button(control_frame, text="Modifica", command=self.modifica_operatore).pack(side='left', padx=5)
        ttk.Button(control_frame, text="Elimina", command=self.elimina_operatore).pack(side='left', padx=5)
        ttk.Button(control_frame, text="Aggiorna Lista", command=self.aggiorna_lista_operatori).pack(side='left', padx=5)

        # Frame per lista operatori
        list_frame = ttk.Frame(self.tab_operatori)
        list_frame.pack(fill='both', expand=True, padx=5, pady=5)

        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient='vertical')
        scrollbar.pack(side='right', fill='y')

        # Treeview operatori
        columns = ('ID_SAP', 'Nome', 'Cognome', 'Contratto', 'FTE', 'Ore_Sett',
                   'Turno', 'Skill', 'Data_Rif')

        self.tree_operatori = ttk.Treeview(list_frame, columns=columns, show='headings',
                                            yscrollcommand=scrollbar.set)

        scrollbar.config(command=self.tree_operatori.yview)

        for col in columns:
            self.tree_operatori.heading(col, text=col.replace('_', ' '))
            self.tree_operatori.column(col, width=100, anchor='center')

        self.tree_operatori.pack(fill='both', expand=True)

        # Carica operatori
        self.aggiorna_lista_operatori()

    def setup_report_tab(self):
        """Setup tab Report"""
        # Frame controlli periodo
        control_frame = ttk.Frame(self.tab_report)
        control_frame.pack(fill='x', padx=5, pady=5)

        ttk.Label(control_frame, text="Report:").pack(side='left', padx=5)

        self.report_type_var = tk.StringVar(value='Giornaliero')
        report_combo = ttk.Combobox(control_frame, textvariable=self.report_type_var,
                                     values=['Giornaliero', 'Settimanale', 'Mensile'],
                                     width=15, state='readonly')
        report_combo.pack(side='left', padx=5)

        ttk.Label(control_frame, text="Data Inizio:").pack(side='left', padx=5)
        self.report_date_start = tk.StringVar(value=self.data_corrente.strftime('%Y-%m-%d'))
        ttk.Entry(control_frame, textvariable=self.report_date_start, width=12).pack(side='left', padx=5)

        ttk.Label(control_frame, text="Data Fine:").pack(side='left', padx=5)
        self.report_date_end = tk.StringVar(value=self.data_corrente.strftime('%Y-%m-%d'))
        ttk.Entry(control_frame, textvariable=self.report_date_end, width=12).pack(side='left', padx=5)

        ttk.Button(control_frame, text="Genera Report Servizio",
                   command=self.genera_report_servizio).pack(side='left', padx=10)

        ttk.Button(control_frame, text="Genera Report Persona",
                   command=self.genera_report_persona).pack(side='left', padx=5)

        # Frame risultati
        result_frame = ttk.Frame(self.tab_report)
        result_frame.pack(fill='both', expand=True, padx=5, pady=5)

        # Scrollbar
        scrollbar = ttk.Scrollbar(result_frame, orient='vertical')
        scrollbar.pack(side='right', fill='y')

        # Treeview per report
        self.tree_report = ttk.Treeview(result_frame, show='headings',
                                         yscrollcommand=scrollbar.set)

        scrollbar.config(command=self.tree_report.yview)
        self.tree_report.pack(fill='both', expand=True)

    def setup_forecast_tab(self):
        """Setup tab Forecast"""
        # Frame controlli
        control_frame = ttk.Frame(self.tab_forecast)
        control_frame.pack(fill='x', padx=5, pady=5)

        ttk.Label(control_frame, text="Gestione Forecast").pack(side='left', padx=5)
        ttk.Button(control_frame, text="Importa Forecast da Excel",
                   command=self.importa_forecast).pack(side='left', padx=10)

        # Istruzioni
        info_text = """
        Il forecast deve contenere per ogni fascia oraria:
        - Data e Ora
        - Skill
        - Volumi Attesi
        - Produttività Target
        - FTE Richiesti (calcolati come Volumi / Produttività)
        """

        info_label = ttk.Label(self.tab_forecast, text=info_text, justify='left')
        info_label.pack(padx=10, pady=10)

    # === METODI DASHBOARD ===

    def aggiorna_dashboard(self):
        """Aggiorna la dashboard con i dati correnti"""
        try:
            # Parse data
            data = datetime.strptime(self.date_var.get(), '%Y-%m-%d')
            intervallo = int(self.interval_var.get())

            # Carica operatori
            self.db_manager.connect()
            operatori_data = self.db_manager.get_operatori(data.strftime('%Y-%m-%d'))

            if not operatori_data:
                messagebox.showinfo("Info", "Nessun operatore trovato per questa data")
                return

            # Crea oggetti Operatore
            operatori = []
            for row in operatori_data:
                # Converti row in dict
                op_dict = self._row_to_dict(row)
                op = Operatore(**op_dict)

                # Carica cambi skill
                cambi = self.db_manager.get_cambi_skill(op.id_sap, data.strftime('%Y-%m-%d'))
                for cambio in cambi:
                    cambio_dict = self._row_to_dict(cambio)
                    op.cambi_skill.append({
                        'ora_inizio': self._parse_time(cambio_dict.get('Ora_Inizio')),
                        'ora_fine': self._parse_time(cambio_dict.get('Ora_Fine')),
                        'skill': cambio_dict.get('Skill_Temporaneo')
                    })

                operatori.append(op)

            # Carica forecast
            forecast_data = self.db_manager.get_forecast(data.strftime('%Y-%m-%d'))
            forecast = [self._row_to_dict(row) for row in forecast_data]

            # Calcola capability
            calculator = CapabilityCalculator(operatori, forecast)
            df_capability = calculator.calcola_capability_per_fascia(data, intervallo)

            # Popola albero
            self.tree_dashboard.delete(*self.tree_dashboard.get_children())

            skill_filter = self.skill_var.get()

            for _, row in df_capability.iterrows():
                if skill_filter != 'Tutti' and row['Skill'] != skill_filter:
                    continue

                fascia = row['Fascia_Oraria'].strftime('%H:%M')
                skill = row['Skill']
                presenti = row['Presenti']
                in_pausa = row['In_Pausa']
                in_prod = row['In_Produzione']
                in_strao = row['In_Straordinario']
                fte_eff = row['FTE_Effettivi']

                fte_rich = row.get('FTE_Richiesti', 0)
                delta = row.get('Delta_FTE', 0)
                copertura = row.get('Copertura_%', 100)

                # Colori in base alla copertura
                tag = ''
                if copertura < 80:
                    tag = 'red'
                elif copertura < 95:
                    tag = 'yellow'
                else:
                    tag = 'green'

                self.tree_dashboard.insert('', 'end',
                                            values=(fascia, skill, presenti, in_pausa,
                                                    in_prod, in_strao, fte_eff,
                                                    f'{fte_rich:.1f}', f'{delta:+.1f}',
                                                    f'{copertura:.0f}%'),
                                            tags=(tag,))

            # Tag colors
            self.tree_dashboard.tag_configure('red', background='#ffcccc')
            self.tree_dashboard.tag_configure('yellow', background='#ffffcc')
            self.tree_dashboard.tag_configure('green', background='#ccffcc')

            # Summary
            total_fte = df_capability['FTE_Effettivi'].sum()
            total_richiesti = df_capability.get('FTE_Richiesti', pd.Series([0])).sum()
            delta_total = total_fte - total_richiesti

            self.summary_label.config(
                text=f"FTE Effettivi Totali: {total_fte:.1f} | FTE Richiesti: {total_richiesti:.1f} | Delta: {delta_total:+.1f}"
            )

            # Aggiorna lista skill per filtro
            skills = ['Tutti'] + sorted(df_capability['Skill'].unique().tolist())
            self.skill_combo['values'] = skills

        except Exception as e:
            messagebox.showerror("Errore", f"Errore nell'aggiornamento dashboard: {e}")
            import traceback
            traceback.print_exc()

        finally:
            self.db_manager.close()

    def show_fascia_detail(self, event):
        """Mostra dettaglio operatori per una fascia selezionata"""
        selection = self.tree_dashboard.selection()
        if not selection:
            return

        item = self.tree_dashboard.item(selection[0])
        values = item['values']

        fascia_str = values[0]
        skill = values[1]

        # TODO: Mostrare popup con dettaglio operatori
        messagebox.showinfo("Dettaglio Fascia",
                             f"Fascia: {fascia_str}\nSkill: {skill}\n\nDettaglio operatori in sviluppo...")

    def esporta_dashboard(self):
        """Esporta i dati dashboard in Excel"""
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension='.xlsx',
                filetypes=[('Excel files', '*.xlsx'), ('All files', '*.*')]
            )

            if not filename:
                return

            # Carica dati
            data = datetime.strptime(self.date_var.get(), '%Y-%m-%d')
            intervallo = int(self.interval_var.get())

            self.db_manager.connect()
            operatori_data = self.db_manager.get_operatori(data.strftime('%Y-%m-%d'))
            operatori = [Operatore(**self._row_to_dict(row)) for row in operatori_data]

            forecast_data = self.db_manager.get_forecast(data.strftime('%Y-%m-%d'))
            forecast = [self._row_to_dict(row) for row in forecast_data]

            calculator = CapabilityCalculator(operatori, forecast)
            df = calculator.calcola_capability_per_fascia(data, intervallo)

            # Esporta
            df.to_excel(filename, index=False, sheet_name='Capability')

            messagebox.showinfo("Successo", f"Dati esportati in {filename}")

        except Exception as e:
            messagebox.showerror("Errore", f"Errore nell'esportazione: {e}")

        finally:
            self.db_manager.close()

    # === METODI OPERATORI ===

    def aggiorna_lista_operatori(self):
        """Aggiorna la lista degli operatori"""
        try:
            self.db_manager.connect()
            operatori = self.db_manager.get_operatori()

            self.tree_operatori.delete(*self.tree_operatori.get_children())

            for row in operatori:
                op = self._row_to_dict(row)
                self.tree_operatori.insert('', 'end',
                                            values=(op.get('ID_SAP', ''),
                                                    op.get('Nome', ''),
                                                    op.get('Cognome', ''),
                                                    op.get('Tipo_Contratto', ''),
                                                    op.get('FTE', ''),
                                                    op.get('Ore_Settimana', ''),
                                                    op.get('ID_Turno', ''),
                                                    op.get('Etichetta_Skill', ''),
                                                    op.get('Data_Riferimento', '')))

        except Exception as e:
            messagebox.showerror("Errore", f"Errore nel caricamento operatori: {e}")

        finally:
            self.db_manager.close()

    def nuovo_operatore(self):
        """Apre dialog per nuovo operatore"""
        messagebox.showinfo("In sviluppo", "Form inserimento operatore in sviluppo")
        # TODO: Creare form dedicato

    def modifica_operatore(self):
        """Modifica operatore selezionato"""
        selection = self.tree_operatori.selection()
        if not selection:
            messagebox.showwarning("Attenzione", "Seleziona un operatore")
            return

        messagebox.showinfo("In sviluppo", "Form modifica operatore in sviluppo")

    def elimina_operatore(self):
        """Elimina operatore selezionato"""
        selection = self.tree_operatori.selection()
        if not selection:
            messagebox.showwarning("Attenzione", "Seleziona un operatore")
            return

        if messagebox.askyesno("Conferma", "Eliminare l'operatore selezionato?"):
            messagebox.showinfo("In sviluppo", "Funzione eliminazione in sviluppo")

    # === METODI REPORT ===

    def genera_report_servizio(self):
        """Genera report ore per servizio"""
        try:
            data_inizio = datetime.strptime(self.report_date_start.get(), '%Y-%m-%d')
            data_fine = datetime.strptime(self.report_date_end.get(), '%Y-%m-%d')

            self.db_manager.connect()

            # Carica operatori per il periodo
            # (semplificazione: carica solo primo giorno)
            operatori_data = self.db_manager.get_operatori(data_inizio.strftime('%Y-%m-%d'))
            operatori = [Operatore(**self._row_to_dict(row)) for row in operatori_data]

            calculator = CapabilityCalculator(operatori)
            df_report = calculator.calcola_rendiconto_per_servizio(data_inizio, data_fine, 15)

            # Popola treeview
            self.tree_report.delete(*self.tree_report.get_children())
            self.tree_report['columns'] = list(df_report.columns)
            self.tree_report['show'] = 'headings'

            for col in df_report.columns:
                self.tree_report.heading(col, text=col.replace('_', ' '))
                self.tree_report.column(col, width=120, anchor='center')

            for _, row in df_report.iterrows():
                self.tree_report.insert('', 'end', values=tuple(row))

            messagebox.showinfo("Successo", "Report generato")

        except Exception as e:
            messagebox.showerror("Errore", f"Errore nella generazione report: {e}")
            import traceback
            traceback.print_exc()

        finally:
            self.db_manager.close()

    def genera_report_persona(self):
        """Genera report ore per persona"""
        try:
            data_inizio = datetime.strptime(self.report_date_start.get(), '%Y-%m-%d')
            data_fine = datetime.strptime(self.report_date_end.get(), '%Y-%m-%d')

            self.db_manager.connect()

            operatori_data = self.db_manager.get_operatori(data_inizio.strftime('%Y-%m-%d'))
            operatori = [Operatore(**self._row_to_dict(row)) for row in operatori_data]

            calculator = CapabilityCalculator(operatori)
            df_report = calculator.calcola_rendiconto_per_persona(data_inizio, data_fine)

            # Popola treeview
            self.tree_report.delete(*self.tree_report.get_children())
            self.tree_report['columns'] = list(df_report.columns)
            self.tree_report['show'] = 'headings'

            for col in df_report.columns:
                self.tree_report.heading(col, text=col.replace('_', ' '))
                self.tree_report.column(col, width=120, anchor='center')

            for _, row in df_report.iterrows():
                self.tree_report.insert('', 'end', values=tuple(row))

            messagebox.showinfo("Successo", "Report generato")

        except Exception as e:
            messagebox.showerror("Errore", f"Errore nella generazione report: {e}")

        finally:
            self.db_manager.close()

    # === METODI UTILITY ===

    def init_database(self):
        """Inizializza il database"""
        from database.db_creator import DatabaseCreator
        creator = DatabaseCreator(self.db_path)
        creator.create_database()
        messagebox.showinfo("Successo", "Database inizializzato")

    def importa_dati(self):
        """Importa dati da Excel"""
        messagebox.showinfo("In sviluppo", "Funzione importazione in sviluppo")

    def importa_forecast(self):
        """Importa forecast da Excel"""
        # Seleziona file Excel
        file_path = filedialog.askopenfilename(
            title="Seleziona file Excel forecast",
            filetypes=[
                ("File Excel", "*.xlsx *.xls"),
                ("Tutti i file", "*.*")
            ]
        )

        if not file_path:
            return  # Utente ha annullato

        # Chiedi se sostituire o aggiungere
        replace = messagebox.askyesnocancel(
            "Modalità Import",
            "Vuoi SOSTITUIRE i forecast esistenti per le date nel file?\n\n"
            "• SÌ = Sostituisci forecast esistenti\n"
            "• NO = Aggiungi ai forecast esistenti\n"
            "• ANNULLA = Annulla operazione"
        )

        if replace is None:
            return  # Utente ha annullato

        try:
            # Importa la funzione di import
            sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'scripts'))
            from import_forecast import import_forecast as do_import

            # Esegui import con feedback
            success = do_import(
                excel_file=file_path,
                db_path=self.db_manager.db_path if hasattr(self, 'db_manager') else 'data/operator_overtime.db',
                replace_existing=replace
            )

            if success:
                messagebox.showinfo(
                    "Successo",
                    "Forecast importati con successo!\n\n"
                    "Aggiorna la dashboard Capability per visualizzarli."
                )
            else:
                messagebox.showerror(
                    "Errore",
                    "Errore durante l'import del forecast.\n\n"
                    "Controlla la console per dettagli."
                )

        except Exception as e:
            messagebox.showerror("Errore", f"Errore import forecast:\n{str(e)}")

    def esporta_report(self):
        """Esporta report"""
        messagebox.showinfo("In sviluppo", "Funzione esportazione in sviluppo")

    def backup_database(self):
        """Backup del database"""
        messagebox.showinfo("In sviluppo", "Funzione backup in sviluppo")

    def show_help(self):
        """Mostra aiuto"""
        help_text = """
        MATRICI - Gestione Turni e Capability Operatori

        1. Dashboard: Visualizza capability per fasce orarie (15/30 min)
        2. Gestione Operatori: Inserisci/modifica anagrafica operatori
        3. Report: Genera rendiconti per servizio e persona
        4. Forecast: Importa e gestisci i volumi previsti

        Per supporto: vedere documentazione
        """
        messagebox.showinfo("Aiuto", help_text)

    def show_about(self):
        """Info applicazione"""
        messagebox.showinfo("Info", "Matrici v1.0\nGestione Turni e Capability Operatori")

    def _row_to_dict(self, row):
        """Converte una row del database in dict"""
        if hasattr(row, 'keys'):
            # pyodbc Row object
            return {key: getattr(row, key) for key in row.cursor_description}
        elif isinstance(row, dict):
            return row
        else:
            # Assume tuple/list
            # Questo richiede conoscenza delle colonne...
            return {}

    def _parse_time(self, value):
        """Parse time value"""
        from models.operatore import Operatore
        op = Operatore()
        return op._parse_time(value)


def main():
    """Entry point"""
    root = tk.Tk()
    app = MainWindow(root)
    root.mainloop()


if __name__ == '__main__':
    main()
