"""
Dashboard Capability con dettaglio fasce orarie
"""
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime, timedelta
import pandas as pd
from tkcalendar import DateEntry


class CapabilityDashboard(ttk.Frame):
    """Dashboard per visualizzazione capability intraday"""

    def __init__(self, parent, db_manager):
        super().__init__(parent)
        self.db_manager = db_manager
        self.current_data = None
        self.setup_ui()
        self.load_skills()  # Carica skill all'inizializzazione

    def setup_ui(self):
        """Crea l'interfaccia della dashboard"""
        # === PANNELLO CONTROLLI ===
        control_frame = ttk.LabelFrame(self, text="Filtri e Opzioni", padding=10)
        control_frame.pack(fill='x', padx=10, pady=10)

        # Row 1: Data e intervallo
        row1 = ttk.Frame(control_frame)
        row1.pack(fill='x', pady=5)

        ttk.Label(row1, text="Data:", font=('Arial', 10, 'bold')).pack(side='left', padx=5)
        self.date_var = tk.StringVar(value=datetime.now().strftime('%d/%m/%Y'))
        self.date_entry = DateEntry(row1, textvariable=self.date_var, width=12,
                                     date_pattern='dd/mm/yyyy')
        self.date_entry.pack(side='left', padx=5)

        # Checkbox "Tutte le date"
        self.all_dates_var = tk.BooleanVar(value=False)
        all_dates_check = ttk.Checkbutton(row1, text="Tutte le date",
                                          variable=self.all_dates_var,
                                          command=self.toggle_date_filter)
        all_dates_check.pack(side='left', padx=5)

        ttk.Label(row1, text="Intervallo:", font=('Arial', 10, 'bold')).pack(side='left', padx=(20, 5))
        self.interval_var = tk.StringVar(value='15')
        ttk.Radiobutton(row1, text="15 minuti", variable=self.interval_var,
                       value='15').pack(side='left', padx=5)
        ttk.Radiobutton(row1, text="30 minuti", variable=self.interval_var,
                       value='30').pack(side='left', padx=5)

        # Row 2: Skill filter e bottoni
        row2 = ttk.Frame(control_frame)
        row2.pack(fill='x', pady=5)

        ttk.Label(row2, text="Filtra Skill:", font=('Arial', 10, 'bold')).pack(side='left', padx=5)
        self.skill_var = tk.StringVar(value='Tutti')
        self.skill_combo = ttk.Combobox(row2, textvariable=self.skill_var,
                                        values=['Tutti'], width=25, state='readonly')
        self.skill_combo.pack(side='left', padx=5)

        ttk.Button(row2, text="🔄 Aggiorna", command=self.refresh_data,
                  width=15).pack(side='left', padx=(20, 5))
        ttk.Button(row2, text="📊 Esporta Excel", command=self.export_excel,
                  width=15).pack(side='left', padx=5)

        # === PANNELLO SUMMARY ===
        summary_frame = ttk.LabelFrame(self, text="Riepilogo Giornata", padding=10)
        summary_frame.pack(fill='x', padx=10, pady=5)

        self.summary_labels = {}

        summary_grid = ttk.Frame(summary_frame)
        summary_grid.pack(fill='x')

        # Indicatori colorati
        indicators = [
            ('total_fte', 'FTE Totali Disponibili', '#4CAF50'),
            ('required_fte', 'FTE Richiesti', '#2196F3'),
            ('delta_fte', 'Delta FTE', '#FF9800'),
            ('coverage', 'Copertura Media %', '#9C27B0')
        ]

        for i, (key, label, color) in enumerate(indicators):
            card = ttk.Frame(summary_grid, relief='raised', borderwidth=2)
            card.grid(row=0, column=i, padx=10, pady=5, sticky='ew')
            summary_grid.columnconfigure(i, weight=1)

            ttk.Label(card, text=label, font=('Arial', 9)).pack(pady=(5, 0))
            value_label = ttk.Label(card, text="--", font=('Arial', 16, 'bold'),
                                   foreground=color)
            value_label.pack(pady=(0, 5))
            self.summary_labels[key] = value_label

        # === TABELLA CAPABILITY ===
        table_frame = ttk.LabelFrame(self, text="Dettaglio Capability per Fascia Oraria", padding=10)
        table_frame.pack(fill='both', expand=True, padx=10, pady=10)

        # Scrollbars
        scroll_y = ttk.Scrollbar(table_frame, orient='vertical')
        scroll_y.pack(side='right', fill='y')

        scroll_x = ttk.Scrollbar(table_frame, orient='horizontal')
        scroll_x.pack(side='bottom', fill='x')

        # Treeview
        columns = (
            'Fascia', 'Skill', 'Presenti', 'In Pausa', 'In Produzione',
            'In Strao', 'FTE Eff.', 'FTE Rich.', 'Delta', 'Copertura %', 'Stato'
        )

        self.tree = ttk.Treeview(table_frame, columns=columns, show='headings',
                                 yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set,
                                 height=20)

        scroll_y.config(command=self.tree.yview)
        scroll_x.config(command=self.tree.xview)

        # Colonne con larghezze
        column_widths = {
            'Fascia': 80,
            'Skill': 150,
            'Presenti': 70,
            'In Pausa': 70,
            'In Produzione': 100,
            'In Strao': 70,
            'FTE Eff.': 70,
            'FTE Rich.': 80,
            'Delta': 70,
            'Copertura %': 90,
            'Stato': 100
        }

        for col in columns:
            self.tree.heading(col, text=col, command=lambda c=col: self.sort_column(c))
            width = column_widths.get(col, 100)
            self.tree.column(col, width=width, anchor='center')

        self.tree.pack(fill='both', expand=True)

        # Bind double-click per dettaglio
        self.tree.bind('<Double-1>', self.show_detail)

        # Tag colors
        self.tree.tag_configure('ok', background='#C8E6C9')  # Verde chiaro
        self.tree.tag_configure('warning', background='#FFF9C4')  # Giallo chiaro
        self.tree.tag_configure('critical', background='#FFCDD2')  # Rosso chiaro
        self.tree.tag_configure('selected', background='#BBDEFB')  # Blu chiaro

        # === LEGENDA ===
        legend_frame = ttk.Frame(self)
        legend_frame.pack(fill='x', padx=10, pady=5)

        ttk.Label(legend_frame, text="Legenda:", font=('Arial', 9, 'bold')).pack(side='left', padx=5)

        legend_items = [
            ('🟢 OK (≥95%)', '#C8E6C9'),
            ('🟡 Attenzione (80-94%)', '#FFF9C4'),
            ('🔴 Critico (<80%)', '#FFCDD2')
        ]

        for text, color in legend_items:
            frame = ttk.Frame(legend_frame, relief='solid', borderwidth=1)
            frame.pack(side='left', padx=5)
            lbl = ttk.Label(frame, text=text, background=color, padding=5)
            lbl.pack()

    def toggle_date_filter(self):
        """Abilita/disabilita il filtro data quando la checkbox 'Tutte le date' viene selezionata"""
        if self.all_dates_var.get():
            # Checkbox selezionata: disabilita il DateEntry
            self.date_entry.config(state='disabled')
        else:
            # Checkbox deselezionata: abilita il DateEntry
            self.date_entry.config(state='normal')

    def load_skills(self):
        """Carica lista skill dal database"""
        try:
            self.db_manager.connect()

            # Carica skill dalla tabella Skills
            skills_data = self.db_manager.execute_query("SELECT Codice_Skill FROM Skills ORDER BY Codice_Skill")

            if skills_data and len(skills_data) > 0:
                skills = ['Tutti'] + [row[0] for row in skills_data]
                self.skill_combo['values'] = skills
            else:
                # Fallback: Se Skills è vuota, carica dagli operatori
                print("[INFO] Tabella Skills vuota, carico skill dagli operatori...")
                operatori_skills = self.db_manager.execute_query("""
                    SELECT DISTINCT Etichetta_Skill
                    FROM Anagrafica_Operatori
                    WHERE Etichetta_Skill IS NOT NULL
                    AND TRIM(Etichetta_Skill) != ''
                    ORDER BY Etichetta_Skill
                """)

                if operatori_skills and len(operatori_skills) > 0:
                    skills = ['Tutti'] + [row[0].strip() for row in operatori_skills]
                    self.skill_combo['values'] = skills
                    print(f"[INFO] Caricati {len(operatori_skills)} skill dagli operatori")
                else:
                    # Nessuno skill trovato
                    self.skill_combo['values'] = ['Tutti']
                    print("[WARN] Nessuno skill trovato nel database")

            self.db_manager.close()
        except Exception as e:
            # In caso di errore, lascia solo "Tutti"
            self.skill_combo['values'] = ['Tutti']
            print(f"[ERROR] Errore caricamento skill: {e}")

    def refresh_data(self):
        """Aggiorna i dati della dashboard"""
        try:
            from models.operatore import Operatore
            from utils.capability_calculator import CapabilityCalculator

            # Parse parametri (da formato italiano dd/mm/yyyy)
            data = datetime.strptime(self.date_var.get(), '%d/%m/%Y')
            intervallo = int(self.interval_var.get())

            # Carica operatori
            self.db_manager.connect()

            # Se "Tutte le date" è selezionata, carica tutti gli operatori
            if self.all_dates_var.get():
                operatori_data = self.db_manager.get_operatori(None)  # Tutti gli operatori
            else:
                operatori_data = self.db_manager.get_operatori(data.strftime('%Y-%m-%d'))

            if not operatori_data:
                if self.all_dates_var.get():
                    messagebox.showinfo("Info", "Nessun operatore trovato nel database.\n\n"
                                               "Inserire operatori nella sezione Anagrafica.")
                else:
                    messagebox.showinfo("Info", f"Nessun operatore trovato per la data {self.date_var.get()}.\n\n"
                                               "Prova a selezionare 'Tutte le date' o inserire operatori per questa data.")
                self.db_manager.close()
                return

            # Crea oggetti Operatore
            operatori = []
            for row in operatori_data:
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

            self.db_manager.close()

            # Calcola capability (passa db_manager per Erlang C)
            calculator = CapabilityCalculator(operatori, forecast, db_manager=self.db_manager)
            df_capability = calculator.calcola_capability_per_fascia(data, intervallo)

            # Salva per export
            self.current_data = df_capability

            # Popola tabella
            self.populate_table(df_capability)

            # Aggiorna summary
            self.update_summary(df_capability)

            # Aggiorna lista skill
            skills = ['Tutti'] + sorted(df_capability['Skill'].unique().tolist())
            self.skill_combo['values'] = skills

        except Exception as e:
            messagebox.showerror("Errore", f"Errore nell'aggiornamento dashboard:\n{e}")
            import traceback
            traceback.print_exc()

    def populate_table(self, df):
        """Popola la tabella con i dati"""
        # Pulisci tabella
        for item in self.tree.get_children():
            self.tree.delete(item)

        if df is None or df.empty:
            return

        skill_filter = self.skill_var.get()

        for _, row in df.iterrows():
            # Filtro skill
            if skill_filter != 'Tutti' and row['Skill'] != skill_filter:
                continue

            # Estrai dati con gestione errori
            try:
                fascia = row['Fascia_Oraria'].strftime('%H:%M')
                skill = row['Skill']
                presenti = int(row['Presenti'])
                in_pausa = int(row['In_Pausa'])
                in_prod = int(row['In_Produzione'])
                in_strao = int(row['In_Straordinario'])

                # Gestione FTE_Effettivi con fallback
                fte_eff = row.get('FTE_Effettivi', 0)
                if fte_eff is None or pd.isna(fte_eff):
                    fte_eff = 0

                fte_rich = row.get('FTE_Richiesti', 0)
                if fte_rich is None or pd.isna(fte_rich):
                    fte_rich = 0

                delta = row.get('Delta_FTE', 0)
                if delta is None or pd.isna(delta):
                    delta = 0

                copertura = row.get('Copertura_%', 100)
                if copertura is None or pd.isna(copertura):
                    copertura = 100

                # Determina stato
                if copertura >= 95:
                    stato = "🟢 OK"
                    tag = 'ok'
                elif copertura >= 80:
                    stato = "🟡 Attenzione"
                    tag = 'warning'
                else:
                    stato = "🔴 Critico"
                    tag = 'critical'

                # Inserisci riga
                values = (
                    fascia, skill, presenti, in_pausa, in_prod, in_strao,
                    f"{fte_eff:.1f}", f"{fte_rich:.1f}", f"{delta:+.1f}",
                    f"{copertura:.0f}%", stato
                )

                self.tree.insert('', 'end', values=values, tags=(tag,))

            except Exception as e:
                print(f"Errore popolamento riga: {e}")
                continue

    def update_summary(self, df):
        """Aggiorna il pannello summary"""
        if df is None or df.empty:
            # Mostra valori di default se non ci sono dati
            self.summary_labels['total_fte'].config(text="0.0")
            self.summary_labels['required_fte'].config(text="0.0")
            self.summary_labels['delta_fte'].config(text="0.0", foreground='#4CAF50')
            self.summary_labels['coverage'].config(text="--", foreground='#9C27B0')
            return

        try:
            # Somma FTE effettivi
            if 'FTE_Effettivi' in df.columns:
                total_fte = df['FTE_Effettivi'].sum()
            else:
                total_fte = 0

            # Somma FTE richiesti
            if 'FTE_Richiesti' in df.columns:
                required_fte = df['FTE_Richiesti'].sum()
            else:
                required_fte = 0

            # Calcola delta
            delta_fte = total_fte - required_fte

            # Calcola copertura media
            if 'Copertura_%' in df.columns:
                # Filtra valori validi (non NaN)
                coperture_valide = df['Copertura_%'].dropna()
                if len(coperture_valide) > 0:
                    avg_coverage = coperture_valide.mean()
                else:
                    avg_coverage = 100
            else:
                avg_coverage = 100

            # Aggiorna labels
            self.summary_labels['total_fte'].config(text=f"{total_fte:.1f}")
            self.summary_labels['required_fte'].config(text=f"{required_fte:.1f}")

            # Delta con colore
            delta_text = f"{delta_fte:+.1f}"
            delta_color = '#4CAF50' if delta_fte >= 0 else '#F44336'
            self.summary_labels['delta_fte'].config(text=delta_text, foreground=delta_color)

            # Coverage con colore
            coverage_text = f"{avg_coverage:.1f}%"
            if avg_coverage >= 95:
                coverage_color = '#4CAF50'
            elif avg_coverage >= 80:
                coverage_color = '#FF9800'
            else:
                coverage_color = '#F44336'
            self.summary_labels['coverage'].config(text=coverage_text, foreground=coverage_color)

        except Exception as e:
            print(f"Errore aggiornamento summary: {e}")
            # Valori di fallback
            self.summary_labels['total_fte'].config(text="--")
            self.summary_labels['required_fte'].config(text="--")
            self.summary_labels['delta_fte'].config(text="--", foreground='#9C27B0')
            self.summary_labels['coverage'].config(text="--", foreground='#9C27B0')

    def show_detail(self, event):
        """Mostra dettaglio operatori per fascia selezionata"""
        selection = self.tree.selection()
        if not selection:
            return

        item = self.tree.item(selection[0])
        values = item['values']

        fascia = values[0]
        skill = values[1]
        presenti = values[2]
        in_pausa = values[3]
        in_prod = values[4]

        detail_msg = f"""
DETTAGLIO FASCIA ORARIA

Fascia: {fascia}
Skill: {skill}

Operatori Presenti: {presenti}
Operatori in Pausa: {in_pausa}
Operatori in Produzione: {in_prod}

(Click destro per vedere nomi operatori - in sviluppo)
        """

        messagebox.showinfo("Dettaglio Fascia", detail_msg.strip())

    def export_excel(self):
        """Esporta i dati in Excel"""
        if self.current_data is None or self.current_data.empty:
            messagebox.showwarning("Attenzione", "Nessun dato da esportare.\nAggiorna prima la dashboard.")
            return

        try:
            filename = filedialog.asksaveasfilename(
                defaultextension='.xlsx',
                filetypes=[('Excel files', '*.xlsx'), ('All files', '*.*')],
                initialfile=f"Capability_{self.date_var.get()}.xlsx"
            )

            if not filename:
                return

            # Export
            self.current_data.to_excel(filename, index=False, sheet_name='Capability')

            messagebox.showinfo("Successo", f"Dati esportati in:\n{filename}")

        except Exception as e:
            messagebox.showerror("Errore", f"Errore nell'esportazione:\n{e}")

    def sort_column(self, col):
        """Ordina tabella per colonna"""
        # TODO: Implementare ordinamento
        pass

    def _row_to_dict(self, row):
        """Converte row database in dict"""
        if hasattr(row, 'cursor_description'):
            return {desc[0]: getattr(row, desc[0]) for desc in row.cursor_description}
        return {}

    def _parse_time(self, value):
        """Parse time value"""
        from models.operatore import Operatore
        op = Operatore()
        return op._parse_time(value)
