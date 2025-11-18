"""
Dialog per modificare le pause degli operatori
"""
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from tkcalendar import DateEntry


class PauseEditorDialog(tk.Toplevel):
    """Dialog per modificare le pause con filtri"""

    def __init__(self, parent, db_manager):
        super().__init__(parent)
        self.db_manager = db_manager
        self.modified = False
        self.operators_data = []
        self.pause_entries = {}  # Dizionario per tenere traccia degli Entry per le pause

        self.title("Modifica Pause Operatori")
        self.geometry("1200x700")
        self.transient(parent)
        self.grab_set()

        self.setup_ui()
        self.load_filters()

    def setup_ui(self):
        """Crea l'interfaccia del dialog"""
        # === PANNELLO FILTRI ===
        filter_frame = ttk.LabelFrame(self, text="Filtri", padding=10)
        filter_frame.pack(fill='x', padx=10, pady=10)

        # Row 1: Data e Skill
        row1 = ttk.Frame(filter_frame)
        row1.pack(fill='x', pady=5)

        ttk.Label(row1, text="Data:", font=('Arial', 10, 'bold')).pack(side='left', padx=5)
        self.date_var = tk.StringVar(value=datetime.now().strftime('%d/%m/%Y'))
        self.date_entry = DateEntry(row1, textvariable=self.date_var, width=12,
                                     date_pattern='dd/mm/yyyy')
        self.date_entry.pack(side='left', padx=5)

        ttk.Label(row1, text="Skill:", font=('Arial', 10, 'bold')).pack(side='left', padx=(20, 5))
        self.skill_var = tk.StringVar(value='Tutti')
        self.skill_combo = ttk.Combobox(row1, textvariable=self.skill_var,
                                        values=['Tutti'], width=25, state='readonly')
        self.skill_combo.pack(side='left', padx=5)
        self.skill_combo.bind('<<ComboboxSelected>>', self.on_skill_change)

        ttk.Label(row1, text="Microskill:", font=('Arial', 10, 'bold')).pack(side='left', padx=(20, 5))
        self.microskill_var = tk.StringVar(value='Tutti')
        self.microskill_combo = ttk.Combobox(row1, textvariable=self.microskill_var,
                                             values=['Tutti'], width=25, state='readonly')
        self.microskill_combo.pack(side='left', padx=5)

        # Row 2: Filtro orario
        row2 = ttk.Frame(filter_frame)
        row2.pack(fill='x', pady=5)

        ttk.Label(row2, text="Orario Da:", font=('Arial', 10, 'bold')).pack(side='left', padx=5)
        self.time_start_var = tk.StringVar(value='')
        time_start_entry = ttk.Entry(row2, textvariable=self.time_start_var, width=8)
        time_start_entry.pack(side='left', padx=5)
        ttk.Label(row2, text="(HH:MM)", font=('Arial', 8)).pack(side='left', padx=(0, 10))

        ttk.Label(row2, text="A:", font=('Arial', 10, 'bold')).pack(side='left', padx=5)
        self.time_end_var = tk.StringVar(value='')
        time_end_entry = ttk.Entry(row2, textvariable=self.time_end_var, width=8)
        time_end_entry.pack(side='left', padx=5)
        ttk.Label(row2, text="(HH:MM)", font=('Arial', 8)).pack(side='left', padx=(0, 10))

        ttk.Button(row2, text="🔍 Cerca", command=self.search_operators,
                  width=15).pack(side='left', padx=(20, 5))

        # === TABELLA OPERATORI ===
        table_frame = ttk.LabelFrame(self, text="Operatori", padding=10)
        table_frame.pack(fill='both', expand=True, padx=10, pady=10)

        # Scrollbar
        scroll_y = ttk.Scrollbar(table_frame, orient='vertical')
        scroll_y.pack(side='right', fill='y')

        scroll_x = ttk.Scrollbar(table_frame, orient='horizontal')
        scroll_x.pack(side='bottom', fill='x')

        # Treeview
        columns = ('ID_SAP', 'Nome', 'Cognome', 'Skill', 'Microskill',
                   'Ora_Inizio', 'Ora_Fine', 'Pausa_Attuale', 'Nuova_Pausa')
        self.tree = ttk.Treeview(table_frame, columns=columns, show='headings',
                                yscrollcommand=scroll_y.set,
                                xscrollcommand=scroll_x.set,
                                height=20)

        scroll_y.config(command=self.tree.yview)
        scroll_x.config(command=self.tree.xview)

        # Headers
        self.tree.heading('ID_SAP', text='ID SAP')
        self.tree.heading('Nome', text='Nome')
        self.tree.heading('Cognome', text='Cognome')
        self.tree.heading('Skill', text='Skill')
        self.tree.heading('Microskill', text='Microskill')
        self.tree.heading('Ora_Inizio', text='Ora Inizio')
        self.tree.heading('Ora_Fine', text='Ora Fine')
        self.tree.heading('Pausa_Attuale', text='Pausa Attuale')
        self.tree.heading('Nuova_Pausa', text='Nuova Pausa')

        # Column widths
        self.tree.column('ID_SAP', width=80, anchor='center')
        self.tree.column('Nome', width=120)
        self.tree.column('Cognome', width=120)
        self.tree.column('Skill', width=100)
        self.tree.column('Microskill', width=100)
        self.tree.column('Ora_Inizio', width=80, anchor='center')
        self.tree.column('Ora_Fine', width=80, anchor='center')
        self.tree.column('Pausa_Attuale', width=100, anchor='center')
        self.tree.column('Nuova_Pausa', width=120, anchor='center')

        self.tree.pack(fill='both', expand=True)

        # Bind doppio click per modificare pausa
        self.tree.bind('<Double-1>', self.on_double_click)

        # === PULSANTI ===
        button_frame = ttk.Frame(self)
        button_frame.pack(fill='x', padx=10, pady=10)

        ttk.Button(button_frame, text="💾 Salva Modifiche", command=self.save_changes,
                  width=20).pack(side='left', padx=5)
        ttk.Button(button_frame, text="❌ Annulla", command=self.destroy,
                  width=20).pack(side='right', padx=5)

    def load_filters(self):
        """Carica opzioni per i filtri"""
        try:
            self.db_manager.connect()

            # Carica skill
            skills_result = self.db_manager.execute_query("""
                SELECT DISTINCT Codice_Skill
                FROM Skills
                WHERE Codice_Skill IS NOT NULL
                ORDER BY Codice_Skill
            """)
            skills = ['Tutti'] + [row[0] for row in skills_result] if skills_result else ['Tutti']
            self.skill_combo['values'] = skills

            # Carica tutti i microskill inizialmente
            microskills_result = self.db_manager.execute_query("""
                SELECT DISTINCT Microskill
                FROM Skills
                WHERE Microskill IS NOT NULL AND Microskill != ''
                ORDER BY Microskill
            """)
            microskills = ['Tutti'] + [row[0] for row in microskills_result] if microskills_result else ['Tutti']
            self.microskill_combo['values'] = microskills

        except Exception as e:
            messagebox.showerror("Errore", f"Errore caricamento filtri:\n{e}")

    def on_skill_change(self, event=None):
        """Aggiorna microskill in base allo skill selezionato"""
        selected_skill = self.skill_var.get()

        try:
            self.db_manager.connect()

            if selected_skill == 'Tutti':
                # Mostra tutti i microskill
                microskills_result = self.db_manager.execute_query("""
                    SELECT DISTINCT Microskill
                    FROM Skills
                    WHERE Microskill IS NOT NULL AND Microskill != ''
                    ORDER BY Microskill
                """)
            else:
                # Filtra microskill per skill selezionato
                microskills_result = self.db_manager.execute_query("""
                    SELECT DISTINCT Microskill
                    FROM Skills
                    WHERE Codice_Skill = ?
                      AND Microskill IS NOT NULL
                      AND Microskill != ''
                    ORDER BY Microskill
                """, (selected_skill,))

            microskills = ['Tutti'] + [row[0] for row in microskills_result] if microskills_result else ['Tutti']
            self.microskill_combo['values'] = microskills
            self.microskill_var.set('Tutti')

        except Exception as e:
            print(f"Errore aggiornamento microskill: {e}")

    def search_operators(self):
        """Cerca operatori in base ai filtri"""
        # Pulisci tabella
        for item in self.tree.get_children():
            self.tree.delete(item)

        self.operators_data = []
        self.pause_entries = {}

        # Costruisci query
        date_str = self.date_entry.get_date().strftime('%Y-%m-%d')
        skill = self.skill_var.get()
        microskill = self.microskill_var.get()
        time_start = self.time_start_var.get().strip()
        time_end = self.time_end_var.get().strip()

        try:
            self.db_manager.connect()

            # Query base
            query = """
                SELECT
                    a.ID_SAP,
                    a.Nome,
                    a.Cognome,
                    a.Etichetta_Skill,
                    a.Microskill,
                    a.Ora_Inizio_Turno,
                    a.Ora_Fine_Turno,
                    a.Inizio_Pausa_1,
                    a.Fine_Pausa_1
                FROM Anagrafica_Operatori a
                WHERE a.Data_Riferimento = ?
            """
            params = [date_str]

            # Aggiungi filtri
            if skill != 'Tutti':
                query += " AND a.Etichetta_Skill = ?"
                params.append(skill)

            if microskill != 'Tutti':
                query += " AND a.Microskill = ?"
                params.append(microskill)

            if time_start:
                query += " AND a.Ora_Inizio_Turno >= ?"
                params.append(time_start)

            if time_end:
                query += " AND a.Ora_Fine_Turno <= ?"
                params.append(time_end)

            query += " ORDER BY a.Ora_Inizio_Turno, a.ID_SAP"

            result = self.db_manager.execute_query(query, params)

            if result:
                for row in result:
                    id_sap, nome, cognome, skill_op, microskill_op, ora_inizio, ora_fine, pausa_inizio, pausa_fine = row

                    # Formatta pausa attuale
                    if pausa_inizio and pausa_fine:
                        pausa_str = f"{self._format_time(pausa_inizio)}-{self._format_time(pausa_fine)}"
                    else:
                        pausa_str = ""

                    # Inserisci nella tabella
                    item_id = self.tree.insert('', 'end', values=(
                        id_sap, nome, cognome, skill_op or '', microskill_op or '',
                        ora_inizio or '', ora_fine or '', pausa_str, ''
                    ))

                    # Salva dati operatore
                    self.operators_data.append({
                        'item_id': item_id,
                        'id_sap': id_sap,
                        'data': date_str,
                        'pausa_attuale': pausa_str,
                        'nuova_pausa': None
                    })

                messagebox.showinfo("Ricerca", f"Trovati {len(result)} operatori")
            else:
                messagebox.showinfo("Ricerca", "Nessun operatore trovato con i filtri selezionati")

        except Exception as e:
            messagebox.showerror("Errore", f"Errore durante la ricerca:\n{e}")
            import traceback
            traceback.print_exc()

    def on_double_click(self, event):
        """Gestisce doppio click su riga per modificare pausa"""
        item = self.tree.selection()
        if not item:
            return

        item_id = item[0]
        column = self.tree.identify_column(event.x)

        # Solo colonna Nuova_Pausa è editabile (colonna #9)
        if column != '#9':
            messagebox.showinfo("Info", "Doppio click sulla colonna 'Nuova Pausa' per modificare")
            return

        # Trova dati operatore
        op_data = None
        for op in self.operators_data:
            if op['item_id'] == item_id:
                op_data = op
                break

        if not op_data:
            return

        # Ottieni bbox della cella
        bbox = self.tree.bbox(item_id, column)
        if not bbox:
            return

        # Crea Entry per modificare
        x, y, width, height = bbox

        entry_var = tk.StringVar(value=op_data.get('nuova_pausa') or op_data.get('pausa_attuale') or '')
        entry = ttk.Entry(self.tree, textvariable=entry_var, width=15)
        entry.place(x=x, y=y, width=width, height=height)
        entry.focus()
        entry.select_range(0, 'end')

        def save_edit(event=None):
            new_value = entry_var.get().strip()
            op_data['nuova_pausa'] = new_value

            # Aggiorna visualizzazione
            values = list(self.tree.item(item_id, 'values'))
            values[8] = new_value
            self.tree.item(item_id, values=values)

            entry.destroy()

        def cancel_edit(event=None):
            entry.destroy()

        entry.bind('<Return>', save_edit)
        entry.bind('<Escape>', cancel_edit)
        entry.bind('<FocusOut>', save_edit)

    def save_changes(self):
        """Salva le modifiche delle pause nel database"""
        # Controlla se ci sono modifiche
        modifications = [op for op in self.operators_data if op.get('nuova_pausa')]

        if not modifications:
            messagebox.showinfo("Info", "Nessuna modifica da salvare")
            return

        try:
            self.db_manager.connect()
            count = 0

            for op in modifications:
                # Parse nuova pausa (formato HH:MM-HH:MM)
                nuova_pausa = op['nuova_pausa']
                if nuova_pausa and '-' in nuova_pausa:
                    parts = nuova_pausa.split('-')
                    pausa_inizio = parts[0].strip()
                    pausa_fine = parts[1].strip() if len(parts) > 1 else None
                else:
                    pausa_inizio = None
                    pausa_fine = None

                # Aggiorna pausa nel database
                self.db_manager.execute_update("""
                    UPDATE Anagrafica_Operatori
                    SET Inizio_Pausa_1 = ?, Fine_Pausa_1 = ?
                    WHERE ID_SAP = ? AND Data_Riferimento = ?
                """, (pausa_inizio, pausa_fine, op['id_sap'], op['data']))
                count += 1

            self.modified = True

            messagebox.showinfo("Successo", f"Aggiornate {count} pause con successo")
            self.destroy()

        except Exception as e:
            messagebox.showerror("Errore", f"Errore salvataggio modifiche:\n{e}")
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
