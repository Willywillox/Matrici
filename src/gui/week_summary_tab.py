"""
Tab Riepilogo Settimanale - Vista dettagliata operatori per settimana
"""
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
from tkcalendar import DateEntry


class WeekSummaryTab(ttk.Frame):
    """Tab per riepilogo settimanale operatori"""

    def __init__(self, parent, db_manager):
        super().__init__(parent)
        self.db_manager = db_manager
        self.current_data = []
        self.setup_ui()

    def setup_ui(self):
        """Crea l'interfaccia del tab"""
        # === PANNELLO CONTROLLI ===
        control_frame = ttk.LabelFrame(self, text="Filtri Settimana", padding=10)
        control_frame.pack(fill='x', padx=10, pady=10)

        # Row 1: Selezione settimana
        row1 = ttk.Frame(control_frame)
        row1.pack(fill='x', pady=5)

        ttk.Label(row1, text="Settimana del:", font=('Arial', 10, 'bold')).pack(side='left', padx=5)

        # Data iniziale settimana (lunedì)
        today = datetime.now().date()
        monday = today - timedelta(days=today.weekday())

        self.week_start_var = tk.StringVar(value=monday.strftime('%d/%m/%Y'))
        self.week_start_entry = DateEntry(row1, textvariable=self.week_start_var, width=12,
                                           date_pattern='dd/mm/yyyy')
        self.week_start_entry.pack(side='left', padx=5)

        # Pulsanti navigazione settimana
        ttk.Button(row1, text="◀ Sett. Prec.", command=self.prev_week,
                  width=12).pack(side='left', padx=5)
        ttk.Button(row1, text="Sett. Succ. ▶", command=self.next_week,
                  width=12).pack(side='left', padx=5)

        # Filtro skill
        ttk.Label(row1, text="Skill:", font=('Arial', 10, 'bold')).pack(side='left', padx=(20, 5))
        self.skill_var = tk.StringVar(value='Tutti')
        self.skill_combo = ttk.Combobox(row1, textvariable=self.skill_var,
                                        values=['Tutti'], width=20, state='readonly')
        self.skill_combo.pack(side='left', padx=5)

        # Filtro microskill
        ttk.Label(row1, text="Microskill:", font=('Arial', 10, 'bold')).pack(side='left', padx=(10, 5))
        self.microskill_var = tk.StringVar(value='Tutti')
        self.microskill_combo = ttk.Combobox(row1, textvariable=self.microskill_var,
                                             values=['Tutti'], width=20, state='readonly')
        self.microskill_combo.pack(side='left', padx=5)

        # Pulsante aggiorna
        ttk.Button(row1, text="🔄 Aggiorna", command=self.refresh_data,
                  width=15).pack(side='left', padx=(20, 5))

        # === TABELLA RIEPILOGO ===
        table_frame = ttk.Frame(self)
        table_frame.pack(fill='both', expand=True, padx=10, pady=10)

        # Scrollbar
        scroll_y = ttk.Scrollbar(table_frame, orient='vertical')
        scroll_y.pack(side='right', fill='y')

        scroll_x = ttk.Scrollbar(table_frame, orient='horizontal')
        scroll_x.pack(side='bottom', fill='x')

        # Definizione colonne
        # Colonne fisse a sinistra + 5 giorni x 4 campi (Turno, Strao, Giust, Pausa)
        base_columns = ['ID_SAP', 'Nome', 'Cognome', 'Skill', 'Microskill']

        day_columns = []
        giorni = ['Lun', 'Mar', 'Mer', 'Gio', 'Ven']
        for giorno in giorni:
            day_columns.extend([
                f'{giorno}_Turno',
                f'{giorno}_Strao',
                f'{giorno}_Giust',
                f'{giorno}_Pausa'
            ])

        all_columns = base_columns + day_columns

        self.tree = ttk.Treeview(table_frame, columns=all_columns, show='headings',
                                yscrollcommand=scroll_y.set,
                                xscrollcommand=scroll_x.set,
                                height=25)

        scroll_y.config(command=self.tree.yview)
        scroll_x.config(command=self.tree.xview)

        # Headers e larghezze colonne base
        self.tree.heading('ID_SAP', text='ID SAP')
        self.tree.heading('Nome', text='Nome')
        self.tree.heading('Cognome', text='Cognome')
        self.tree.heading('Skill', text='Skill')
        self.tree.heading('Microskill', text='Microskill')

        self.tree.column('ID_SAP', width=70, anchor='center')
        self.tree.column('Nome', width=100)
        self.tree.column('Cognome', width=100)
        self.tree.column('Skill', width=80)
        self.tree.column('Microskill', width=80)

        # Headers e larghezze colonne giorni
        for giorno in giorni:
            self.tree.heading(f'{giorno}_Turno', text=f'{giorno}\nTurno')
            self.tree.heading(f'{giorno}_Strao', text=f'{giorno}\nStrao')
            self.tree.heading(f'{giorno}_Giust', text=f'{giorno}\nGiust.')
            self.tree.heading(f'{giorno}_Pausa', text=f'{giorno}\nPausa')

            self.tree.column(f'{giorno}_Turno', width=90, anchor='center')
            self.tree.column(f'{giorno}_Strao', width=50, anchor='center')
            self.tree.column(f'{giorno}_Giust', width=60, anchor='center')
            self.tree.column(f'{giorno}_Pausa', width=70, anchor='center')

        self.tree.pack(fill='both', expand=True)

        # Carica filtri iniziali
        self.load_filters()

    def load_filters(self):
        """Carica opzioni per i filtri"""
        try:
            self.db_manager.connect()

            # Carica skill
            skills_result = self.db_manager.execute_query("""
                SELECT DISTINCT Etichetta_Skill
                FROM Anagrafica_Operatori
                WHERE Etichetta_Skill IS NOT NULL
                ORDER BY Etichetta_Skill
            """)
            skills = ['Tutti'] + [row[0] for row in skills_result] if skills_result else ['Tutti']
            self.skill_combo['values'] = skills

            # Carica microskill
            microskills_result = self.db_manager.execute_query("""
                SELECT DISTINCT Microskill
                FROM Anagrafica_Operatori
                WHERE Microskill IS NOT NULL AND Microskill != ''
                ORDER BY Microskill
            """)
            microskills = ['Tutti'] + [row[0] for row in microskills_result] if microskills_result else ['Tutti']
            self.microskill_combo['values'] = microskills

        except Exception as e:
            print(f"Errore caricamento filtri: {e}")

    def prev_week(self):
        """Va alla settimana precedente"""
        current_date = self.week_start_entry.get_date()
        new_date = current_date - timedelta(days=7)
        self.week_start_entry.set_date(new_date)
        self.refresh_data()

    def next_week(self):
        """Va alla settimana successiva"""
        current_date = self.week_start_entry.get_date()
        new_date = current_date + timedelta(days=7)
        self.week_start_entry.set_date(new_date)
        self.refresh_data()

    def refresh_data(self):
        """Carica e mostra dati della settimana"""
        # Pulisci tabella
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Calcola date della settimana
        week_start = self.week_start_entry.get_date()
        # Assicurati che sia lunedì
        week_start = week_start - timedelta(days=week_start.weekday())

        dates = [(week_start + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(5)]

        try:
            self.db_manager.connect()

            # Query per ottenere tutti gli operatori unici della settimana
            query_operatori = """
                SELECT DISTINCT ID_SAP, Nome, Cognome, Etichetta_Skill, Microskill
                FROM Anagrafica_Operatori
                WHERE Data_Riferimento BETWEEN ? AND ?
            """
            params = [dates[0], dates[4]]

            # Aggiungi filtri
            skill = self.skill_var.get()
            microskill = self.microskill_var.get()

            if skill != 'Tutti':
                query_operatori += " AND Etichetta_Skill = ?"
                params.append(skill)

            if microskill != 'Tutti':
                query_operatori += " AND Microskill = ?"
                params.append(microskill)

            query_operatori += " ORDER BY Cognome, Nome"

            operatori = self.db_manager.execute_query(query_operatori, params)

            if not operatori:
                messagebox.showinfo("Info", "Nessun operatore trovato per la settimana selezionata")
                return

            # Per ogni operatore, ottieni i dati di ogni giorno
            for op in operatori:
                id_sap, nome, cognome, skill_op, microskill_op = op

                row_data = [id_sap, nome, cognome, skill_op or '', microskill_op or '']

                # Per ogni giorno della settimana
                for date_str in dates:
                    # Ottieni dati turno
                    turno_result = self.db_manager.execute_query("""
                        SELECT Ora_Inizio_Turno, Ora_Fine_Turno,
                               Inizio_Strao_1, Fine_Strao_1,
                               Inizio_Pausa_1, Fine_Pausa_1
                        FROM Anagrafica_Operatori
                        WHERE ID_SAP = ? AND Data_Riferimento = ?
                    """, (id_sap, date_str))

                    if turno_result and turno_result[0]:
                        ora_inizio, ora_fine, strao_inizio, strao_fine, pausa_inizio, pausa_fine = turno_result[0]

                        # Turno
                        if ora_inizio and ora_fine:
                            turno_str = f"{self._format_time(ora_inizio)}-{self._format_time(ora_fine)}"
                        else:
                            turno_str = ""

                        # Straordinario
                        if strao_inizio and strao_fine:
                            strao_str = f"{self._format_time(strao_inizio)}-{self._format_time(strao_fine)}"
                        elif strao_inizio or strao_fine:
                            strao_str = "Sì"
                        else:
                            strao_str = ""

                        # Pausa
                        if pausa_inizio and pausa_fine:
                            pausa_str = f"{self._format_time(pausa_inizio)}-{self._format_time(pausa_fine)}"
                        else:
                            pausa_str = ""
                    else:
                        turno_str = ""
                        strao_str = ""
                        pausa_str = ""

                    # Giustificativi per questo giorno
                    giust_result = self.db_manager.execute_query("""
                        SELECT Tipologia
                        FROM Giustificativi
                        WHERE ID_SAP = ? AND Data = ?
                    """, (id_sap, date_str))

                    if giust_result:
                        giust_str = ", ".join([g[0] for g in giust_result if g[0]])
                    else:
                        giust_str = ""

                    row_data.extend([turno_str, strao_str, giust_str, pausa_str])

                # Inserisci riga
                self.tree.insert('', 'end', values=row_data)

            # Aggiorna header con date
            giorni = ['Lun', 'Mar', 'Mer', 'Gio', 'Ven']
            for i, giorno in enumerate(giorni):
                date_obj = week_start + timedelta(days=i)
                date_label = date_obj.strftime('%d/%m')

                self.tree.heading(f'{giorno}_Turno', text=f'{giorno} {date_label}\nTurno')
                self.tree.heading(f'{giorno}_Strao', text=f'{giorno}\nStrao')
                self.tree.heading(f'{giorno}_Giust', text=f'{giorno}\nGiust.')
                self.tree.heading(f'{giorno}_Pausa', text=f'{giorno}\nPausa')

            messagebox.showinfo("Aggiornamento", f"Caricati {len(operatori)} operatori")

        except Exception as e:
            messagebox.showerror("Errore", f"Errore caricamento dati:\n{e}")
            import traceback
            traceback.print_exc()

    def _format_time(self, time_value):
        """Formatta valore orario"""
        if not time_value:
            return ""

        # Se è già stringa HH:MM
        if isinstance(time_value, str):
            if len(time_value) >= 5:
                return time_value[:5]
            return time_value

        # Se è datetime
        if hasattr(time_value, 'strftime'):
            return time_value.strftime('%H:%M')

        return str(time_value)
