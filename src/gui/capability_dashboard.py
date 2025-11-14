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
        self.tipologie_giustificativi = self._load_tipologie_giustificativi()
        self.setup_ui()
        self.load_skills()  # Carica skill all'inizializzazione
        self.load_microskills()  # Carica microskill all'inizializzazione

    def _load_tipologie_giustificativi(self):
        """Carica tipologie uniche di giustificativi dal database"""
        tipologie = []
        try:
            self.db_manager.connect()
            result = self.db_manager.execute_query("""
                SELECT DISTINCT Tipologia
                FROM Giustificativi
                WHERE Tipologia IS NOT NULL
                ORDER BY Tipologia
            """)

            if result:
                tipologie = [row[0] for row in result]

        except Exception as e:
            print(f"Avviso: Impossibile caricare tipologie giustificativi: {e}")

        return tipologie

    def setup_ui(self):
        """Crea l'interfaccia della dashboard"""
        # === PANNELLO CONTROLLI ===
        control_frame = ttk.LabelFrame(self, text="Filtri e Opzioni", padding=10)
        control_frame.pack(fill='x', padx=10, pady=10)

        # Row 1: Intervallo date
        row1 = ttk.Frame(control_frame)
        row1.pack(fill='x', pady=5)

        ttk.Label(row1, text="Da:", font=('Arial', 10, 'bold')).pack(side='left', padx=5)
        self.date_start_var = tk.StringVar(value=datetime.now().strftime('%d/%m/%Y'))
        self.date_start_entry = DateEntry(row1, textvariable=self.date_start_var, width=12,
                                           date_pattern='dd/mm/yyyy')
        self.date_start_entry.pack(side='left', padx=5)

        ttk.Label(row1, text="A:", font=('Arial', 10, 'bold')).pack(side='left', padx=(10, 5))
        self.date_end_var = tk.StringVar(value=datetime.now().strftime('%d/%m/%Y'))
        self.date_end_entry = DateEntry(row1, textvariable=self.date_end_var, width=12,
                                         date_pattern='dd/mm/yyyy')
        self.date_end_entry.pack(side='left', padx=5)

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

        # Bind per aggiornare filtro quando cambia skill
        self.skill_combo.bind('<<ComboboxSelected>>', lambda e: self.apply_filter())

        # Microskill con selezione multipla
        ttk.Label(row2, text="Microskill:", font=('Arial', 10, 'bold')).pack(side='left', padx=(15, 5))

        # Frame per contenere Listbox e Scrollbar
        microskill_frame = ttk.Frame(row2)
        microskill_frame.pack(side='left', padx=5)

        # Listbox con scrollbar per selezione multipla
        microskill_scrollbar = ttk.Scrollbar(microskill_frame, orient='vertical')
        self.microskill_listbox = tk.Listbox(microskill_frame,
                                             height=3,
                                             width=20,
                                             selectmode='multiple',
                                             exportselection=False,
                                             yscrollcommand=microskill_scrollbar.set)
        microskill_scrollbar.config(command=self.microskill_listbox.yview)
        self.microskill_listbox.pack(side='left', fill='both')
        microskill_scrollbar.pack(side='left', fill='y')

        # Inserisci valore iniziale
        self.microskill_listbox.insert(0, 'Tutti')
        self.microskill_listbox.selection_set(0)

        # Bind per aggiornare filtro quando cambia selezione
        self.microskill_listbox.bind('<<ListboxSelect>>', self.on_microskill_select)

        ttk.Button(row2, text="🔄 Aggiorna", command=self.refresh_data,
                  width=15).pack(side='left', padx=(20, 5))
        ttk.Button(row2, text="📊 Esporta Excel", command=self.export_excel,
                  width=15).pack(side='left', padx=5)

        # Row 3: Vista riepilogo
        row3 = ttk.Frame(control_frame)
        row3.pack(fill='x', pady=5)

        ttk.Label(row3, text="Vista Riepilogo:", font=('Arial', 10, 'bold')).pack(side='left', padx=5)
        self.vista_var = tk.StringVar(value='Totale')
        self.vista_combo = ttk.Combobox(row3, textvariable=self.vista_var,
                                        values=['Totale', 'Settimana', 'Mese'],
                                        width=15, state='readonly')
        self.vista_combo.pack(side='left', padx=5)
        self.vista_combo.bind('<<ComboboxSelected>>', self.on_vista_change)

        # Selettori periodo (inizialmente nascosti)
        self.week_label = ttk.Label(row3, text="Settimana:")
        self.week_var = tk.StringVar()
        self.week_combo = ttk.Combobox(row3, textvariable=self.week_var, width=30, state='readonly')
        self.week_combo.bind('<<ComboboxSelected>>', lambda e: self.update_summary_by_period())

        self.month_label = ttk.Label(row3, text="Mese:")
        self.month_var = tk.StringVar()
        self.month_combo = ttk.Combobox(row3, textvariable=self.month_var, width=20, state='readonly')
        self.month_combo.bind('<<ComboboxSelected>>', lambda e: self.update_summary_by_period())

        # === PANNELLO SUMMARY ===
        self.summary_frame = ttk.LabelFrame(self, text="Riepilogo", padding=10)
        self.summary_frame.pack(fill='x', padx=10, pady=5)

        self.summary_labels = {}
        self.summary_grid = None  # Sarà creato dinamicamente

        # Crea vista iniziale (Totale)
        self.create_summary_totale()

        # Sezione FTE
        fte_section = ttk.LabelFrame(summary_grid, text="FTE", padding=5)
        fte_section.grid(row=0, column=0, padx=5, pady=5, sticky='ew')
        summary_grid.columnconfigure(0, weight=1)

        fte_indicators = [
            ('required_fte', 'Richiesti', '#2196F3'),
            ('total_fte', 'Disponibili', '#4CAF50'),
            ('delta_fte', 'Delta', '#FF9800')
        ]

        for i, (key, label, color) in enumerate(fte_indicators):
            card = ttk.Frame(fte_section)
            card.grid(row=0, column=i, padx=5, pady=2, sticky='ew')
            fte_section.columnconfigure(i, weight=1)

            ttk.Label(card, text=label, font=('Arial', 8)).pack()
            value_label = ttk.Label(card, text="--", font=('Arial', 14, 'bold'),
                                   foreground=color)
            value_label.pack()
            self.summary_labels[key] = value_label

        # Sezione Forecast
        forecast_section = ttk.LabelFrame(summary_grid, text="Forecast", padding=5)
        forecast_section.grid(row=0, column=1, padx=5, pady=5, sticky='ew')
        summary_grid.columnconfigure(1, weight=1)

        forecast_indicators = [
            ('volumi_attesi', 'Volumi Attesi', '#9C27B0'),
            ('gestibile', 'Gestibile', '#4CAF50'),
            ('delta_forecast', 'Delta', '#FF9800')
        ]

        for i, (key, label, color) in enumerate(forecast_indicators):
            card = ttk.Frame(forecast_section)
            card.grid(row=0, column=i, padx=5, pady=2, sticky='ew')
            forecast_section.columnconfigure(i, weight=1)

            ttk.Label(card, text=label, font=('Arial', 8)).pack()
            value_label = ttk.Label(card, text="--", font=('Arial', 14, 'bold'),
                                   foreground=color)
            value_label.pack()
            self.summary_labels[key] = value_label

        # Sezione Ore
        ore_section = ttk.LabelFrame(summary_grid, text="Ore", padding=5)
        ore_section.grid(row=0, column=2, padx=5, pady=5, sticky='ew')
        summary_grid.columnconfigure(2, weight=1)

        ore_indicators = [
            ('ore_richieste', 'Richieste', '#2196F3'),
            ('ore_produzione', 'Produzione', '#4CAF50'),
            ('delta_ore', 'Delta', '#FF9800')
        ]

        for i, (key, label, color) in enumerate(ore_indicators):
            card = ttk.Frame(ore_section)
            card.grid(row=0, column=i, padx=5, pady=2, sticky='ew')
            ore_section.columnconfigure(i, weight=1)

            ttk.Label(card, text=label, font=('Arial', 8)).pack()
            value_label = ttk.Label(card, text="--", font=('Arial', 14, 'bold'),
                                   foreground=color)
            value_label.pack()
            self.summary_labels[key] = value_label

        # Sezione Capability
        capability_section = ttk.LabelFrame(summary_grid, text="Capability", padding=5)
        capability_section.grid(row=0, column=3, padx=5, pady=5, sticky='ew')
        summary_grid.columnconfigure(3, weight=1)

        capability_indicators = [
            ('capability_forecast', 'Prevista', '#9C27B0'),
            ('capability_gestibile', 'Gestibile', '#4CAF50'),
            ('delta_capability', 'Delta', '#FF9800')
        ]

        for i, (key, label, color) in enumerate(capability_indicators):
            card = ttk.Frame(capability_section)
            card.grid(row=0, column=i, padx=5, pady=2, sticky='ew')
            capability_section.columnconfigure(i, weight=1)

            ttk.Label(card, text=label, font=('Arial', 8)).pack()
            value_label = ttk.Label(card, text="--", font=('Arial', 14, 'bold'),
                                   foreground=color)
            value_label.pack()
            self.summary_labels[key] = value_label

        # Sezione Copertura
        coverage_section = ttk.LabelFrame(summary_grid, text="Performance", padding=5)
        coverage_section.grid(row=0, column=4, padx=5, pady=5, sticky='ew')
        summary_grid.columnconfigure(4, weight=1)

        coverage_card = ttk.Frame(coverage_section)
        coverage_card.pack(padx=5, pady=2)

        ttk.Label(coverage_card, text="Copertura Media", font=('Arial', 8)).pack()
        value_label = ttk.Label(coverage_card, text="--", font=('Arial', 14, 'bold'),
                               foreground='#9C27B0')
        value_label.pack()
        self.summary_labels['coverage'] = value_label

        # === TABELLA CAPABILITY ===
        table_frame = ttk.LabelFrame(self, text="Dettaglio Capability per Fascia Oraria", padding=10)
        table_frame.pack(fill='both', expand=True, padx=10, pady=10)

        # Scrollbars
        scroll_y = ttk.Scrollbar(table_frame, orient='vertical')
        scroll_y.pack(side='right', fill='y')

        scroll_x = ttk.Scrollbar(table_frame, orient='horizontal')
        scroll_x.pack(side='bottom', fill='x')

        # Treeview - colonne dinamiche con giustificativi
        # Rimossa colonna Microskill - i dati vengono aggregati per fascia
        base_columns_before = ['Data', 'Fascia', 'Skill', 'Presenti', 'In Pausa', 'In Produzione', 'In Strao']
        # Riorganizzate per raggruppamento logico:
        # FTE: Effettivi, Richiesti, Delta
        # Forecast: Volumi, Gestibile, Delta
        # Agenti: Richiesti, Produzione, Delta
        # Ore: Necessarie, Produzione, Delta
        # Produttività: Prod/h
        # Performance: Capability %, Copertura %, Stato
        base_columns_after = [
            'FTE Eff.', 'FTE Rich.', 'Delta FTE',
            'Volumi FC', 'Gest. Chiam.', 'Delta FC',
            'Agenti', 'Ag.Produzione', 'Delta Ag',
            'Prod/h',
            'Ore Necessarie', 'Ore Produz.', 'Delta Ore',
            'Capability %', 'Copertura %', 'Stato'
        ]

        # Inserisci colonne giustificativi tra In Strao e FTE Eff.
        columns = tuple(base_columns_before + self.tipologie_giustificativi + base_columns_after)

        self.tree = ttk.Treeview(table_frame, columns=columns, show='headings',
                                 yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set,
                                 height=20)

        scroll_y.config(command=self.tree.yview)
        scroll_x.config(command=self.tree.xview)

        # Colonne con larghezze
        column_widths = {
            'Data': 90,
            'Fascia': 80,
            'Skill': 150,
            'Presenti': 70,
            'In Pausa': 70,
            'In Produzione': 100,
            'In Strao': 70,
            'FTE Eff.': 70,
            'FTE Rich.': 80,
            'Delta FTE': 70,
            'Volumi FC': 90,
            'Gest. Chiam.': 90,
            'Delta FC': 70,
            'Agenti': 70,
            'Ag.Produzione': 100,
            'Delta Ag': 70,
            'Prod/h': 70,
            'Ore Necessarie': 100,
            'Ore Produz.': 90,
            'Delta Ore': 80,
            'Capability %': 90,
            'Copertura %': 90,
            'Stato': 100
        }

        # Aggiungi larghezza per colonne giustificativi (abbreviate se troppo lunghe)
        for tipologia in self.tipologie_giustificativi:
            column_widths[tipologia] = 80

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
            # Checkbox selezionata: disabilita i DateEntry
            self.date_start_entry.config(state='disabled')
            self.date_end_entry.config(state='disabled')
        else:
            # Checkbox deselezionata: abilita i DateEntry
            self.date_start_entry.config(state='normal')
            self.date_end_entry.config(state='normal')

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

    def load_microskills(self):
        """Carica lista microskill dal database"""
        try:
            self.db_manager.connect()

            # Carica microskill unici dalla tabella Skills
            microskills_skills = self.db_manager.execute_query("""
                SELECT DISTINCT Microskill FROM Skills
                WHERE Microskill IS NOT NULL AND TRIM(Microskill) != ''
                ORDER BY Microskill
            """)

            # Carica microskill unici dalla tabella Anagrafica_Operatori
            microskills_ops = self.db_manager.execute_query("""
                SELECT DISTINCT Microskill FROM Anagrafica_Operatori
                WHERE Microskill IS NOT NULL AND TRIM(Microskill) != ''
                ORDER BY Microskill
            """)

            # Combina e deduplica
            microskills_set = set()
            if microskills_skills:
                microskills_set.update([row[0] for row in microskills_skills])
            if microskills_ops:
                microskills_set.update([row[0] for row in microskills_ops])

            # Aggiorna la listbox
            self.microskill_listbox.delete(0, tk.END)  # Pulisci contenuto esistente
            self.microskill_listbox.insert(0, 'Tutti')

            if microskills_set:
                for microskill in sorted(list(microskills_set)):
                    self.microskill_listbox.insert(tk.END, microskill)
                print(f"[INFO] Caricati {len(microskills_set)} microskill dal database")
            else:
                print("[INFO] Nessun microskill trovato nel database")

            # Seleziona 'Tutti' di default
            self.microskill_listbox.selection_set(0)

            self.db_manager.close()
        except Exception as e:
            # In caso di errore, lascia solo "Tutti"
            self.microskill_listbox.delete(0, tk.END)
            self.microskill_listbox.insert(0, 'Tutti')
            self.microskill_listbox.selection_set(0)
            print(f"[ERROR] Errore caricamento microskill: {e}")

    def get_selected_microskills(self):
        """Ottiene la lista dei microskill selezionati nella listbox"""
        selected_indices = self.microskill_listbox.curselection()
        if not selected_indices:
            return []

        selected_microskills = []
        for idx in selected_indices:
            value = self.microskill_listbox.get(idx)
            selected_microskills.append(value)

        return selected_microskills

    def on_microskill_select(self, event=None):
        """Callback quando cambia la selezione dei microskill"""
        selected = self.get_selected_microskills()

        # Se è selezionato 'Tutti', deseleziona gli altri
        if 'Tutti' in selected and len(selected) > 1:
            # Se 'Tutti' è stato appena cliccato, deseleziona gli altri
            if selected[-1] == 'Tutti':
                self.microskill_listbox.selection_clear(0, tk.END)
                self.microskill_listbox.selection_set(0)  # Solo 'Tutti'
            else:
                # Se è stato selezionato altro, deseleziona 'Tutti'
                tutti_idx = self.microskill_listbox.get(0, tk.END).index('Tutti')
                self.microskill_listbox.selection_clear(tutti_idx)

        # Aggiorna filtro e riepilogo
        self.apply_filter()

    def apply_filter(self):
        """Applica il filtro ai dati correnti e aggiorna il riepilogo"""
        if self.current_data is None or self.current_data.empty:
            return

        # Filtra i dati in base a skill e microskill selezionati
        df_filtered = self.current_data.copy()

        # Filtro skill
        skill_filter = self.skill_var.get()
        if skill_filter != 'Tutti':
            df_filtered = df_filtered[df_filtered['Skill'] == skill_filter]

        # Filtro microskill (selezione multipla)
        selected_microskills = self.get_selected_microskills()
        if selected_microskills and 'Tutti' not in selected_microskills:
            # Filtra per includere solo i microskill selezionati
            # Gestisci anche valori null/NaN come stringhe vuote
            df_filtered = df_filtered[
                df_filtered['Microskill'].fillna('').isin(selected_microskills)
            ]

        # Ripopola tabella con dati filtrati
        self.populate_table(df_filtered)

        # Aggiorna summary con dati filtrati
        self.update_summary(df_filtered)

    def refresh_data(self):
        """Aggiorna i dati della dashboard"""
        try:
            from models.operatore import Operatore
            from utils.capability_calculator import CapabilityCalculator

            # Parse parametri (da formato italiano dd/mm/yyyy)
            data_inizio = datetime.strptime(self.date_start_var.get(), '%d/%m/%Y')
            data_fine = datetime.strptime(self.date_end_var.get(), '%d/%m/%Y')
            intervallo = int(self.interval_var.get())

            # Verifica intervallo valido
            if data_fine < data_inizio:
                messagebox.showwarning("Attenzione", "La data fine deve essere >= data inizio")
                return

            # Carica operatori
            self.db_manager.connect()

            # Logica di caricamento dati
            if self.all_dates_var.get():
                # Tutte le date: carica tutti gli operatori
                operatori_data = self.db_manager.get_operatori(None)
            else:
                # Intervallo specifico: carica solo operatori nell'intervallo
                # Carica tutti e poi filtra (db_manager.get_operatori non supporta range)
                operatori_data = self.db_manager.get_operatori(None)

            if not operatori_data:
                messagebox.showinfo("Info", "Nessun operatore trovato nel database.\n\n"
                                           "Inserire operatori nella sezione Anagrafica.")
                self.db_manager.close()
                return

            # Estrai date uniche dagli operatori
            date_uniche = set()
            for row in operatori_data:
                op_dict = self._row_to_dict(row)
                data_rif = op_dict.get('Data_Riferimento')

                # Gestione sicura del parsing della data
                try:
                    if isinstance(data_rif, str):
                        # Verifica che sia una data valida e non un altro valore come "Smart"
                        if len(data_rif) >= 8 and '-' in data_rif:  # Formato YYYY-MM-DD minimo
                            data_rif = datetime.strptime(data_rif, '%Y-%m-%d')
                        else:
                            continue  # Salta questa riga se non è una data valida
                    if data_rif:
                        data_obj = data_rif.date() if isinstance(data_rif, datetime) else data_rif

                        # Filtra per intervallo se non "Tutte le date"
                        if not self.all_dates_var.get():
                            if data_inizio.date() <= data_obj <= data_fine.date():
                                date_uniche.add(data_obj)
                        else:
                            date_uniche.add(data_obj)
                except (ValueError, AttributeError) as e:
                    # Ignora righe con dati non validi
                    print(f"[WARNING] Data non valida ignorata: {data_rif}")
                    continue

            if not date_uniche:
                if self.all_dates_var.get():
                    msg = "Nessun operatore trovato nel database."
                else:
                    msg = f"Nessun operatore trovato nell'intervallo {self.date_start_var.get()} - {self.date_end_var.get()}."
                messagebox.showinfo("Info", msg)
                self.db_manager.close()
                return

            # Calcola capability per ogni data
            all_dataframes = []

            for data_corrente in sorted(date_uniche):
                # Converti a datetime
                if not isinstance(data_corrente, datetime):
                    data_corrente = datetime.combine(data_corrente, datetime.min.time())

                # Filtra operatori per questa data
                operatori = []
                for row in operatori_data:
                    op_dict = self._row_to_dict(row)
                    data_op = op_dict.get('Data_Riferimento')

                    # Gestione sicura del parsing della data
                    try:
                        if isinstance(data_op, str):
                            # Verifica che sia una data valida
                            if len(data_op) >= 8 and '-' in data_op:
                                data_op = datetime.strptime(data_op, '%Y-%m-%d')
                            else:
                                continue  # Salta operatore con data non valida
                    except ValueError:
                        continue  # Salta operatore con data non valida

                    if data_op and data_op.date() == data_corrente.date():
                        op = Operatore(**op_dict)

                        # Carica cambi skill
                        cambi = self.db_manager.get_cambi_skill(op.id_sap, data_corrente.strftime('%Y-%m-%d'))
                        for cambio in cambi:
                            cambio_dict = self._row_to_dict(cambio)
                            op.cambi_skill.append({
                                'ora_inizio': self._parse_time(cambio_dict.get('Ora_Inizio')),
                                'ora_fine': self._parse_time(cambio_dict.get('Ora_Fine')),
                                'skill': cambio_dict.get('Skill_Temporaneo')
                            })

                        operatori.append(op)

                if operatori:
                    # Carica forecast per questa data
                    forecast_data = self.db_manager.get_forecast(data_corrente.strftime('%Y-%m-%d'))
                    forecast = [self._row_to_dict(row) for row in forecast_data]

                    # Calcola capability
                    calculator = CapabilityCalculator(operatori, forecast, db_manager=self.db_manager)
                    df_day = calculator.calcola_capability_per_fascia(data_corrente, intervallo)
                    all_dataframes.append(df_day)

            self.db_manager.close()

            # Concatena tutti i dataframe
            if all_dataframes:
                df_capability = pd.concat(all_dataframes, ignore_index=True)
            else:
                df_capability = pd.DataFrame()

            # Salva per export
            self.current_data = df_capability

            # Popola tabella
            self.populate_table(df_capability)

            # Aggiorna summary
            self.update_summary(df_capability)

            # Aggiorna lista skill
            skills = ['Tutti'] + sorted(df_capability['Skill'].unique().tolist())
            self.skill_combo['values'] = skills

            # Aggiorna lista microskill nella listbox
            microskills_unique = df_capability['Microskill'].dropna().unique().tolist()
            # Rimuovi stringhe vuote
            microskills_unique = [m for m in microskills_unique if m and str(m).strip() != '']

            # Salva selezione corrente
            current_selection = self.get_selected_microskills()

            # Aggiorna listbox
            self.microskill_listbox.delete(0, tk.END)
            self.microskill_listbox.insert(0, 'Tutti')

            if microskills_unique:
                for microskill in sorted(microskills_unique):
                    self.microskill_listbox.insert(tk.END, microskill)

            # Ripristina selezione se possibile
            all_items = list(self.microskill_listbox.get(0, tk.END))
            for item in current_selection:
                if item in all_items:
                    idx = all_items.index(item)
                    self.microskill_listbox.selection_set(idx)

            # Se nessuna selezione, seleziona 'Tutti'
            if not self.microskill_listbox.curselection():
                self.microskill_listbox.selection_set(0)

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

        # Determina ore per fascia per calcoli delle ore
        if not df.empty and 'Fascia_Oraria' in df.columns:
            sorted_fasce = sorted(df['Fascia_Oraria'].unique())
            if len(sorted_fasce) >= 2:
                delta_minutes = (sorted_fasce[1] - sorted_fasce[0]).total_seconds() / 60
                ore_per_fascia = delta_minutes / 60.0
            else:
                ore_per_fascia = 0.25  # Default 15 minuti
        else:
            ore_per_fascia = 0.25  # Default 15 minuti

        # Aggrega dati per (Fascia_Oraria, Skill) - somma tutti i valori numerici
        # I microskill selezionati sono già stati filtrati in apply_filter()
        numeric_cols = ['Presenti', 'In_Pausa', 'In_Produzione', 'In_Straordinario',
                       'FTE_Effettivi', 'FTE_Richiesti', 'Volumi_Attesi', 'Gestibile_Chiamate',
                       'Agenti_Richiesti', 'Produttivita_Oraria']

        # Aggiungi colonne giustificativi dinamiche
        for tipologia in self.tipologie_giustificativi:
            if tipologia in df.columns:
                numeric_cols.append(tipologia)

        # Raggruppa e aggrega
        df_aggregato = df.groupby(['Fascia_Oraria', 'Skill'], as_index=False)[numeric_cols].sum()

        # Ricalcola metriche percentuali dopo aggregazione
        df_aggregato['Capability_%'] = (df_aggregato['Gestibile_Chiamate'] / df_aggregato['Volumi_Attesi'] * 100).fillna(0)
        df_aggregato['Copertura_%'] = (df_aggregato['In_Produzione'] / df_aggregato['Agenti_Richiesti'] * 100).fillna(100).clip(upper=100)
        df_aggregato['Delta_FTE'] = df_aggregato['FTE_Effettivi'] - df_aggregato['FTE_Richiesti']

        for _, row in df_aggregato.iterrows():
            # Estrai dati con gestione errori
            try:
                # Data e fascia oraria
                data = row['Fascia_Oraria'].strftime('%d/%m/%Y')
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

                # Volumi forecast
                volumi_fc = row.get('Volumi_Attesi', 0)
                if volumi_fc is None or pd.isna(volumi_fc):
                    volumi_fc = 0
                volumi_fc = int(volumi_fc)

                fte_rich = row.get('FTE_Richiesti', 0)
                if fte_rich is None or pd.isna(fte_rich):
                    fte_rich = 0

                # Produttività oraria
                prod_oraria = row.get('Produttivita_Oraria', 0)
                if prod_oraria is None or pd.isna(prod_oraria):
                    prod_oraria = 0

                # Agenti richiesti (numero teste)
                agenti_richiesti = row.get('Agenti_Richiesti', 0)
                if agenti_richiesti is None or pd.isna(agenti_richiesti):
                    agenti_richiesti = 0
                agenti_richiesti = int(agenti_richiesti)

                # Gestibile chiamate
                gestibile_chiamate = row.get('Gestibile_Chiamate', 0)
                if gestibile_chiamate is None or pd.isna(gestibile_chiamate):
                    gestibile_chiamate = 0
                gestibile_chiamate = int(gestibile_chiamate)

                # Capability %
                capability_pct = row.get('Capability_%', 0)
                if capability_pct is None or pd.isna(capability_pct):
                    capability_pct = 0

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

                # Costruisci valori dinamicamente includendo giustificativi
                # Ordine: Data, Fascia, Skill, Presenti, In Pausa, In Produzione, In Strao,
                #         [Giustificativi...], FTE Eff., FTE Rich., Richiesto, Gest. Chiam., Delta, Copertura %, Stato
                values_list = [
                    data, fascia, skill, presenti, in_pausa, in_prod, in_strao
                ]

                # Aggiungi valori giustificativi dinamicamente
                for tipologia in self.tipologie_giustificativi:
                    valore_giust = row.get(tipologia, 0)
                    if valore_giust is None or pd.isna(valore_giust):
                        valore_giust = 0
                    values_list.append(int(valore_giust))

                # Aggiungi valori finali
                # Nuovo ordine: FTE Eff., FTE Rich., Delta FTE, Volumi FC, Gest. Chiam., Delta FC,
                #               Agenti, Ag.Produzione, Delta Ag, Prod/h,
                #               Ore Necessarie, Ore Produz., Delta Ore,
                #               Capability %, Copertura %, Stato

                # Calcola Delta FTE
                delta_fte = fte_eff - fte_rich

                # Calcola Delta FC (forecast)
                delta_fc = gestibile_chiamate - volumi_fc if volumi_fc > 0 else 0

                # Ag.Produzione = operatori in produzione
                ag_produzione = in_prod

                # Delta Ag = Ag.Produzione - Agenti Richiesti
                delta_ag = ag_produzione - agenti_richiesti

                # Ore Necessarie = Agenti Richiesti * ore per fascia
                ore_necessarie = agenti_richiesti * ore_per_fascia

                # Ore Produzione = Operatori in Produzione * ore per fascia
                ore_produzione = ag_produzione * ore_per_fascia

                # Delta Ore = Ore Produzione - Ore Necessarie
                delta_ore = ore_produzione - ore_necessarie

                values_list.extend([
                    f"{fte_eff:.1f}", f"{fte_rich:.1f}", f"{delta_fte:+.1f}",
                    volumi_fc, gestibile_chiamate, f"{delta_fc:+.0f}",
                    agenti_richiesti, ag_produzione, f"{delta_ag:+.0f}",
                    f"{prod_oraria:.1f}",
                    f"{ore_necessarie:.1f}h", f"{ore_produzione:.1f}h", f"{delta_ore:+.1f}h",
                    f"{capability_pct:.0f}%", f"{copertura:.0f}%", stato
                ])

                self.tree.insert('', 'end', values=tuple(values_list), tags=(tag,))

            except Exception as e:
                print(f"Errore popolamento riga: {e}")
                continue

    def update_summary(self, df):
        """Aggiorna il pannello summary"""
        if df is None or df.empty:
            # Mostra valori di default se non ci sono dati
            for key in ['total_fte', 'required_fte', 'delta_fte', 'volumi_attesi',
                       'gestibile', 'delta_forecast', 'ore_richieste', 'ore_produzione',
                       'delta_ore', 'capability_forecast', 'capability_gestibile',
                       'delta_capability', 'coverage']:
                if key in self.summary_labels:
                    self.summary_labels[key].config(text="--")
            return

        try:
            # === SEZIONE FTE ===
            # Determina intervallo in minuti per calcolare ore per fascia
            if not df.empty and 'Fascia_Oraria' in df.columns:
                sorted_fasce = sorted(df['Fascia_Oraria'].unique())
                if len(sorted_fasce) >= 2:
                    delta_minutes = (sorted_fasce[1] - sorted_fasce[0]).total_seconds() / 60
                    ore_per_fascia = delta_minutes / 60.0
                else:
                    ore_per_fascia = 0.25  # Default 15 minuti
            else:
                ore_per_fascia = 0.25  # Default 15 minuti

            # Calcola giorni lavorativi unici nel dataframe (escludendo weekend)
            if 'Fascia_Oraria' in df.columns and not df.empty:
                # Ottieni tutte le date univoche
                date_uniche = df['Fascia_Oraria'].dt.date.unique()
                # Filtra solo giorni lavorativi (lunedì=0 a venerdì=4)
                giorni_lavorativi = sum(1 for d in date_uniche
                                       if pd.Timestamp(d).dayofweek < 5)
                if giorni_lavorativi == 0:
                    giorni_lavorativi = 1  # Fallback
            else:
                giorni_lavorativi = 1

            # Calcola FTE Disponibili usando formula: Ore totali disponibili / Giorni lavorativi / 8
            if 'In_Produzione' in df.columns:
                ore_totali_disponibili = df['In_Produzione'].sum() * ore_per_fascia
                total_fte = ore_totali_disponibili / giorni_lavorativi / 8
            else:
                total_fte = 0

            # Calcola FTE richiesti usando formula: Ore totali / Giorni lavorativi / 8
            if 'Agenti_Richiesti' in df.columns:
                ore_totali_richieste = df['Agenti_Richiesti'].sum() * ore_per_fascia
                required_fte = ore_totali_richieste / giorni_lavorativi / 8
            else:
                required_fte = 0

            # Delta FTE
            delta_fte = total_fte - required_fte

            # === SEZIONE FORECAST ===
            # Volumi Attesi
            if 'Volumi_Attesi' in df.columns:
                volumi_attesi = df['Volumi_Attesi'].sum()
            else:
                volumi_attesi = 0

            # Gestibile
            if 'Gestibile_Chiamate' in df.columns:
                gestibile = df['Gestibile_Chiamate'].sum()
            else:
                gestibile = 0

            # Delta Forecast (Gestibile - Volumi Attesi)
            delta_forecast = gestibile - volumi_attesi

            # === SEZIONE ORE ===
            # Determina intervallo in minuti
            if not df.empty and 'Fascia_Oraria' in df.columns:
                # Prova a determinare l'intervallo dai dati
                sorted_fasce = sorted(df['Fascia_Oraria'].unique())
                if len(sorted_fasce) >= 2:
                    delta_minutes = (sorted_fasce[1] - sorted_fasce[0]).total_seconds() / 60
                    ore_per_fascia = delta_minutes / 60.0
                else:
                    ore_per_fascia = 0.25  # Default 15 minuti
            else:
                ore_per_fascia = 0.25  # Default 15 minuti

            # Ore Produzione (somma operatori in produzione * ore_fascia)
            if 'In_Produzione' in df.columns:
                ore_produzione = df['In_Produzione'].sum() * ore_per_fascia
            else:
                ore_produzione = 0

            # Ore Richieste (FTE_Richiesti * 8 ore/giorno / numero fasce per giornata * numero fasce)
            # Alternativa: Agenti_Richiesti * ore_fascia
            if 'Agenti_Richiesti' in df.columns:
                ore_richieste = df['Agenti_Richiesti'].sum() * ore_per_fascia
            else:
                ore_richieste = 0

            # Delta Ore
            delta_ore = ore_produzione - ore_richieste

            # === CAPABILITY ===
            # Capability in valori assoluti (chiamate)
            # Capability Forecast = Volumi Attesi
            capability_forecast_val = volumi_attesi

            # Capability Gestibile = Gestibile
            capability_gestibile_val = gestibile

            # Delta Capability = Gestibile - Volumi Attesi
            delta_capability_val = gestibile - volumi_attesi

            # === COPERTURA ===
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

            # === AGGIORNA LABELS ===
            # FTE Section
            self.summary_labels['required_fte'].config(text=f"{required_fte:.1f}")
            self.summary_labels['total_fte'].config(text=f"{total_fte:.1f}")

            delta_fte_text = f"{delta_fte:+.1f}"
            delta_fte_color = '#4CAF50' if delta_fte >= 0 else '#F44336'
            self.summary_labels['delta_fte'].config(text=delta_fte_text, foreground=delta_fte_color)

            # Forecast Section
            self.summary_labels['volumi_attesi'].config(text=f"{int(volumi_attesi)}")
            self.summary_labels['gestibile'].config(text=f"{int(gestibile)}")

            delta_forecast_text = f"{delta_forecast:+.0f}"
            delta_forecast_color = '#4CAF50' if delta_forecast >= 0 else '#F44336'
            self.summary_labels['delta_forecast'].config(text=delta_forecast_text, foreground=delta_forecast_color)

            # Ore Section
            self.summary_labels['ore_richieste'].config(text=f"{ore_richieste:.1f}h")
            self.summary_labels['ore_produzione'].config(text=f"{ore_produzione:.1f}h")

            delta_ore_text = f"{delta_ore:+.1f}h"
            delta_ore_color = '#4CAF50' if delta_ore >= 0 else '#F44336'
            self.summary_labels['delta_ore'].config(text=delta_ore_text, foreground=delta_ore_color)

            # Capability Section
            self.summary_labels['capability_forecast'].config(text=f"{int(capability_forecast_val)}")
            self.summary_labels['capability_gestibile'].config(text=f"{int(capability_gestibile_val)}")

            delta_capability_text = f"{delta_capability_val:+.0f}"
            delta_capability_color = '#4CAF50' if delta_capability_val >= 0 else '#F44336'
            self.summary_labels['delta_capability'].config(text=delta_capability_text, foreground=delta_capability_color)

            # Coverage
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
            import traceback
            traceback.print_exc()
            # Valori di fallback
            for key in ['total_fte', 'required_fte', 'delta_fte', 'volumi_attesi',
                       'gestibile', 'delta_forecast', 'ore_richieste', 'ore_produzione',
                       'delta_ore', 'capability_forecast', 'capability_gestibile',
                       'delta_capability', 'coverage']:
                if key in self.summary_labels:
                    self.summary_labels[key].config(text="--")

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

    def create_summary_totale(self):
        """Crea vista riepilogo totale (quella attuale)"""
        # Pulisci contenuto precedente
        if self.summary_grid:
            self.summary_grid.destroy()

        self.summary_grid = ttk.Frame(self.summary_frame)
        self.summary_grid.pack(fill='x')

        # Le sezioni sono già create sotto nel codice esistente
        # Questo metodo serve solo per compatibilità

    def on_vista_change(self, event=None):
        """Gestisce cambio vista riepilogo"""
        vista = self.vista_var.get()

        # Nascondi tutti i selettori periodo
        self.week_label.pack_forget()
        self.week_combo.pack_forget()
        self.month_label.pack_forget()
        self.month_combo.pack_forget()

        if vista == 'Totale':
            # Vista totale - nessun selettore
            self.create_summary_totale()
            if self.current_data is not None:
                self.update_summary(self.current_data)

        elif vista == 'Settimana':
            # Mostra selettore settimana
            self.week_label.pack(side='left', padx=(20, 5))
            self.week_combo.pack(side='left', padx=5)
            self.populate_weeks()
            self.create_summary_by_day()

        elif vista == 'Mese':
            # Mostra selettore mese
            self.month_label.pack(side='left', padx=(20, 5))
            self.month_combo.pack(side='left', padx=5)
            self.populate_months()
            self.create_summary_by_day()

    def populate_weeks(self):
        """Popola lista settimane disponibili in base ai dati"""
        if self.current_data is None or self.current_data.empty:
            return

        # Ottieni date univoche
        dates = pd.to_datetime(self.current_data['Fascia_Oraria']).dt.date.unique()
        weeks = {}

        for date in sorted(dates):
            # Calcola inizio settimana (lunedì)
            week_start = date - timedelta(days=date.weekday())
            week_end = week_start + timedelta(days=4)  # Venerdì

            week_key = week_start.strftime('%Y-%m-%d')
            week_label = f"{week_start.strftime('%d/%m/%Y')} - {week_end.strftime('%d/%m/%Y')}"
            weeks[week_key] = week_label

        if weeks:
            self.week_combo['values'] = list(weeks.values())
            self.week_combo.set(list(weeks.values())[0])  # Seleziona prima settimana
            # Salva mapping per uso futuro
            self.week_mapping = {v: k for k, v in weeks.items()}

    def populate_months(self):
        """Popola lista mesi disponibili in base ai dati"""
        if self.current_data is None or self.current_data.empty:
            return

        # Ottieni mesi univoci
        dates = pd.to_datetime(self.current_data['Fascia_Oraria'])
        months = dates.dt.to_period('M').unique()

        month_labels = []
        self.month_mapping = {}

        for month in sorted(months):
            month_start = month.to_timestamp()
            month_label = month_start.strftime('%B %Y')  # es. "Novembre 2024"
            month_key = month_start.strftime('%Y-%m')
            month_labels.append(month_label)
            self.month_mapping[month_label] = month_key

        if month_labels:
            self.month_combo['values'] = month_labels
            self.month_combo.set(month_labels[0])  # Seleziona primo mese

    def create_summary_by_day(self):
        """Crea vista riepilogo per giorno (settimana/mese)"""
        # Pulisci contenuto precedente
        if self.summary_grid:
            self.summary_grid.destroy()

        # Crea frame con scrollbar per giorni
        canvas_frame = ttk.Frame(self.summary_frame)
        canvas_frame.pack(fill='both', expand=True)

        canvas = tk.Canvas(canvas_frame, height=200)
        scrollbar = ttk.Scrollbar(canvas_frame, orient='horizontal', command=canvas.xview)
        self.summary_grid = ttk.Frame(canvas)

        canvas.create_window((0, 0), window=self.summary_grid, anchor='nw')
        canvas.configure(xscrollcommand=scrollbar.set)

        canvas.pack(side='top', fill='both', expand=True)
        scrollbar.pack(side='bottom', fill='x')

        # Aggiorna canvas quando cambia dimensione
        self.summary_grid.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox('all')))

        # Popola con dati
        self.update_summary_by_period()

    def update_summary_by_period(self):
        """Aggiorna riepilogo in base a periodo selezionato"""
        if self.current_data is None or self.current_data.empty:
            return

        vista = self.vista_var.get()

        # Pulisci grid
        for widget in self.summary_grid.winfo_children():
            widget.destroy()

        if vista == 'Settimana':
            selected_week = self.week_var.get()
            if not selected_week or not hasattr(self, 'week_mapping'):
                return

            week_start_str = self.week_mapping.get(selected_week)
            if not week_start_str:
                return

            week_start = datetime.strptime(week_start_str, '%Y-%m-%d').date()
            self._render_week_summary(week_start)

        elif vista == 'Mese':
            selected_month = self.month_var.get()
            if not selected_month or not hasattr(self, 'month_mapping'):
                return

            month_key = self.month_mapping.get(selected_month)
            if not month_key:
                return

            self._render_month_summary(month_key)

    def _render_week_summary(self, week_start):
        """Renderizza riepilogo settimana con dettaglio per giorno"""
        giorni_settimana = ['Lun', 'Mar', 'Mer', 'Gio', 'Ven']

        # Header con giorni
        for col, giorno in enumerate(giorni_settimana):
            date = week_start + timedelta(days=col)
            header = ttk.Label(self.summary_grid,
                             text=f"{giorno}\n{date.strftime('%d/%m')}",
                             font=('Arial', 9, 'bold'))
            header.grid(row=0, column=col, padx=5, pady=5, sticky='ew')

        # Colonna TOTALE
        ttk.Label(self.summary_grid, text="TOTALE\nSettimana",
                 font=('Arial', 10, 'bold'), foreground='#2196F3').grid(
            row=0, column=len(giorni_settimana), padx=10, pady=5, sticky='ew')

        # Indicatori principali
        indicators = ['FTE', 'Volumi', 'Gestibile', 'Ore Prod.', 'Copertura %']

        totali = {ind: 0 for ind in indicators}

        for row_idx, indicator in enumerate(indicators, start=1):
            # Label indicatore
            ttk.Label(self.summary_grid, text=indicator,
                     font=('Arial', 8, 'bold')).grid(
                row=row_idx, column=-1, padx=5, pady=2, sticky='w')

            # Valori per ogni giorno
            for col, giorno in enumerate(giorni_settimana):
                date = week_start + timedelta(days=col)
                date_str = date.strftime('%Y-%m-%d')

                # Filtra dati per questo giorno
                df_day = self.current_data[
                    pd.to_datetime(self.current_data['Fascia_Oraria']).dt.date == date
                ]

                # Calcola valore indicatore
                value = self._calc_indicator_value(df_day, indicator)
                totali[indicator] += value

                # Mostra valore
                ttk.Label(self.summary_grid, text=f"{value:.1f}").grid(
                    row=row_idx, column=col, padx=5, pady=2)

            # Mostra totale
            ttk.Label(self.summary_grid, text=f"{totali[indicator]:.1f}",
                     font=('Arial', 9, 'bold'), foreground='#2196F3').grid(
                row=row_idx, column=len(giorni_settimana), padx=10, pady=2)

    def _render_month_summary(self, month_key):
        """Renderizza riepilogo mese con dettaglio per giorno"""
        year, month = map(int, month_key.split('-'))
        month_start = datetime(year, month, 1).date()

        # Calcola numero giorni nel mese
        import calendar
        num_days = calendar.monthrange(year, month)[1]

        # Header con giorni (mostra solo primi 10 caratteri per risparmiare spazio)
        for day in range(1, num_days + 1):
            date = datetime(year, month, day).date()
            day_name = ['Lun', 'Mar', 'Mer', 'Gio', 'Ven', 'Sab', 'Dom'][date.weekday()]

            header = ttk.Label(self.summary_grid,
                             text=f"{day_name}\n{day:02d}",
                             font=('Arial', 8))
            header.grid(row=0, column=day-1, padx=2, pady=5, sticky='ew')

        # Colonna TOTALE
        ttk.Label(self.summary_grid, text="TOT\nMese",
                 font=('Arial', 9, 'bold'), foreground='#2196F3').grid(
            row=0, column=num_days, padx=5, pady=5, sticky='ew')

        # Indicatori
        indicators = ['FTE', 'Vol.', 'Gest.', 'Ore', 'Cop.%']
        totali = {ind: 0 for ind in indicators}

        for row_idx, indicator in enumerate(indicators, start=1):
            # Label
            ttk.Label(self.summary_grid, text=indicator,
                     font=('Arial', 8, 'bold')).grid(
                row=row_idx, column=-1, padx=5, pady=2, sticky='w')

            # Valori per ogni giorno
            for day in range(1, num_days + 1):
                date = datetime(year, month, day).date()

                # Filtra dati
                df_day = self.current_data[
                    pd.to_datetime(self.current_data['Fascia_Oraria']).dt.date == date
                ]

                value = self._calc_indicator_value(df_day, indicator)
                totali[indicator] += value

                if value > 0:
                    ttk.Label(self.summary_grid, text=f"{value:.0f}",
                             font=('Arial', 7)).grid(
                        row=row_idx, column=day-1, padx=2, pady=1)

            # Totale
            ttk.Label(self.summary_grid, text=f"{totali[indicator]:.0f}",
                     font=('Arial', 8, 'bold'), foreground='#2196F3').grid(
                row=row_idx, column=num_days, padx=5, pady=2)

    def _calc_indicator_value(self, df, indicator):
        """Calcola valore indicatore per un dataframe"""
        if df.empty:
            return 0

        if indicator in ['FTE']:
            return df['FTE_Effettivi'].sum() if 'FTE_Effettivi' in df.columns else 0
        elif indicator in ['Volumi', 'Vol.']:
            return df['Volumi_Attesi'].sum() if 'Volumi_Attesi' in df.columns else 0
        elif indicator in ['Gestibile', 'Gest.']:
            return df['Gestibile_Chiamate'].sum() if 'Gestibile_Chiamate' in df.columns else 0
        elif indicator in ['Ore Prod.', 'Ore']:
            ore_per_fascia = 0.25  # Default
            return df['In_Produzione'].sum() * ore_per_fascia if 'In_Produzione' in df.columns else 0
        elif indicator in ['Copertura %', 'Cop.%']:
            if 'In_Produzione' in df.columns and 'Agenti_Richiesti' in df.columns:
                prod = df['In_Produzione'].sum()
                rich = df['Agenti_Richiesti'].sum()
                return (prod / rich * 100) if rich > 0 else 100
            return 0

        return 0

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
        # pyodbc.Row (Access)
        if hasattr(row, 'cursor_description'):
            return {desc[0]: getattr(row, desc[0]) for desc in row.cursor_description}
        # sqlite3.Row
        elif hasattr(row, 'keys'):
            return {key: row[key] for key in row.keys()}
        # Fallback per tuple/liste (non dovrebbe succedere con row_factory)
        else:
            print("[WARN] Row senza metadati, ritorno dict vuoto")
            return {}

    def _parse_time(self, value):
        """Parse time value"""
        from models.operatore import Operatore
        op = Operatore()
        return op._parse_time(value)
