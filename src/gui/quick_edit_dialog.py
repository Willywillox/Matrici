"""
GUI per modifiche rapide giornaliere (turni, straordinari, giustificativi, postazione)
"""
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, time
from tkcalendar import DateEntry


class QuickEditDialog(tk.Toplevel):
    """Dialog per modifiche rapide giornaliere"""

    def __init__(self, parent, db_manager, operatore_id=None, data=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.operatore_id = operatore_id
        self.data = data or datetime.now()

        self.title("Modifiche Rapide Giornaliere")
        self.geometry("700x650")
        self.resizable(False, False)

        self.operatore_data = None
        self.setup_ui()

        if operatore_id:
            self.load_operatore()

    def setup_ui(self):
        """Crea interfaccia"""
        # === HEADER ===
        header_frame = ttk.Frame(self, relief='raised', borderwidth=2)
        header_frame.pack(fill='x', padx=5, pady=5)

        ttk.Label(header_frame, text="MODIFICHE RAPIDE",
                 font=('Arial', 12, 'bold')).pack(pady=5)

        # === SELEZIONE OPERATORE E DATA ===
        select_frame = ttk.LabelFrame(self, text="Selezione", padding=10)
        select_frame.pack(fill='x', padx=10, pady=10)

        # Operatore
        ttk.Label(select_frame, text="Operatore:", font=('Arial', 9, 'bold')).grid(
            row=0, column=0, sticky='e', padx=5, pady=5)

        self.operatore_var = tk.StringVar()
        self.operatore_combo = ttk.Combobox(select_frame, textvariable=self.operatore_var,
                                            width=30, state='readonly')
        self.operatore_combo.grid(row=0, column=1, sticky='w', padx=5, pady=5)
        self.operatore_combo.bind('<<ComboboxSelected>>', self.on_operatore_change)

        # Data
        ttk.Label(select_frame, text="Data:", font=('Arial', 9, 'bold')).grid(
            row=0, column=2, sticky='e', padx=(20, 5), pady=5)

        self.date_var = tk.StringVar(value=self.data.strftime('%Y-%m-%d'))
        self.date_entry = DateEntry(select_frame, textvariable=self.date_var,
                                    width=12, date_pattern='yyyy-mm-dd')
        self.date_entry.grid(row=0, column=3, sticky='w', padx=5, pady=5)
        self.date_entry.bind('<<DateEntrySelected>>', self.on_date_change)

        ttk.Button(select_frame, text="Carica", command=self.load_operatore,
                  width=10).grid(row=0, column=4, padx=10)

        # === DATI ATTUALI ===
        current_frame = ttk.LabelFrame(self, text="Dati Attuali", padding=10)
        current_frame.pack(fill='x', padx=10, pady=5)

        self.current_label = ttk.Label(current_frame, text="Seleziona operatore e data",
                                       font=('Arial', 9), foreground='gray')
        self.current_label.pack(pady=5)

        # === NOTEBOOK MODIFICHE ===
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)

        # Tab 1: Postazione
        self.tab_postazione = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_postazione, text='📍 Postazione')
        self.setup_postazione_tab()

        # Tab 2: Turno
        self.tab_turno = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_turno, text='🕐 Cambio Turno')
        self.setup_turno_tab()

        # Tab 3: Straordinario
        self.tab_strao = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_strao, text='⏰ Straordinario')
        self.setup_strao_tab()

        # Tab 4: Giustificativo
        self.tab_giust = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_giust, text='📋 Giustificativo')
        self.setup_giust_tab()

        # === BOTTONI ===
        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill='x', padx=10, pady=10)

        ttk.Button(btn_frame, text="💾 Salva Tutte le Modifiche",
                  command=self.salva_modifiche, style='Accent.TButton',
                  width=30).pack(side='left', padx=5)

        ttk.Button(btn_frame, text="Annulla", command=self.destroy,
                  width=15).pack(side='right', padx=5)

        # Carica lista operatori
        self.load_operatori_list()

    def setup_postazione_tab(self):
        """Tab per cambio postazione"""
        frame = ttk.Frame(self.tab_postazione, padding=20)
        frame.pack(fill='both', expand=True)

        ttk.Label(frame, text="Seleziona Postazione per questa giornata:",
                 font=('Arial', 10, 'bold')).pack(pady=10)

        self.postazione_var = tk.StringVar()

        options = [
            ('🏢 Sede', 'Sede'),
            ('🏠 Smart Working', 'Smart Working'),
            ('🚗 Trasferta', 'Trasferta'),
            ('📵 Permesso', 'Permesso'),
            ('🏥 Assente', 'Assente')
        ]

        for label, value in options:
            ttk.Radiobutton(frame, text=label, variable=self.postazione_var,
                           value=value).pack(anchor='w', padx=20, pady=5)

        # Info
        info_frame = ttk.Frame(frame, relief='solid', borderwidth=1)
        info_frame.pack(fill='x', pady=20, padx=10)

        ttk.Label(info_frame, text="ℹ️ Informazione",
                 font=('Arial', 9, 'bold')).pack(anchor='w', padx=10, pady=5)

        ttk.Label(info_frame,
                 text="La postazione indica dove lavora l'operatore per questa giornata.\n"
                      "Utile per tracking presenze fisiche e gestione smart working.",
                 font=('Arial', 8), foreground='gray').pack(anchor='w', padx=10, pady=5)

    def setup_turno_tab(self):
        """Tab per cambio turno"""
        frame = ttk.Frame(self.tab_turno, padding=20)
        frame.pack(fill='both', expand=True)

        ttk.Label(frame, text="Modifica Turno Giornaliero:",
                 font=('Arial', 10, 'bold')).pack(pady=10)

        # Turno principale
        turno_frame = ttk.LabelFrame(frame, text="Turno Principale", padding=10)
        turno_frame.pack(fill='x', pady=10)

        ttk.Label(turno_frame, text="Ora Inizio:").grid(row=0, column=0, sticky='e', padx=5, pady=5)
        self.turno_inizio_var = tk.StringVar()
        ttk.Entry(turno_frame, textvariable=self.turno_inizio_var, width=10).grid(
            row=0, column=1, sticky='w', padx=5, pady=5)

        ttk.Label(turno_frame, text="Ora Fine:").grid(row=0, column=2, sticky='e', padx=(20,5), pady=5)
        self.turno_fine_var = tk.StringVar()
        ttk.Entry(turno_frame, textvariable=self.turno_fine_var, width=10).grid(
            row=0, column=3, sticky='w', padx=5, pady=5)

        # Turno spezzato
        spezzato_frame = ttk.LabelFrame(frame, text="Turno Spezzato (opzionale)", padding=10)
        spezzato_frame.pack(fill='x', pady=10)

        ttk.Label(spezzato_frame, text="Ora Inizio:").grid(row=0, column=0, sticky='e', padx=5, pady=5)
        self.spezzato_inizio_var = tk.StringVar()
        ttk.Entry(spezzato_frame, textvariable=self.spezzato_inizio_var, width=10).grid(
            row=0, column=1, sticky='w', padx=5, pady=5)

        ttk.Label(spezzato_frame, text="Ora Fine:").grid(row=0, column=2, sticky='e', padx=(20,5), pady=5)
        self.spezzato_fine_var = tk.StringVar()
        ttk.Entry(spezzato_frame, textvariable=self.spezzato_fine_var, width=10).grid(
            row=0, column=3, sticky='w', padx=5, pady=5)

        # Bottoni rapidi
        quick_frame = ttk.Frame(frame)
        quick_frame.pack(pady=10)

        ttk.Label(quick_frame, text="Turni Predefiniti:", font=('Arial', 9, 'bold')).pack()

        btn_row = ttk.Frame(quick_frame)
        btn_row.pack(pady=5)

        turni = [
            ('6-14', '06:00', '14:00'),
            ('9-18', '09:00', '18:00'),
            ('14-22', '14:00', '22:00'),
            ('22-6', '22:00', '06:00')
        ]

        for label, inizio, fine in turni:
            ttk.Button(btn_row, text=label,
                      command=lambda i=inizio, f=fine: self.set_turno_rapido(i, f),
                      width=8).pack(side='left', padx=2)

    def setup_strao_tab(self):
        """Tab per straordinario"""
        frame = ttk.Frame(self.tab_strao, padding=20)
        frame.pack(fill='both', expand=True)

        ttk.Label(frame, text="Inserisci/Modifica Straordinario:",
                 font=('Arial', 10, 'bold')).pack(pady=10)

        # Slot straordinari
        for i in range(1, 4):
            slot_frame = ttk.LabelFrame(frame, text=f"Slot Straordinario {i}", padding=10)
            slot_frame.pack(fill='x', pady=5)

            ttk.Label(slot_frame, text="Ora Inizio:").grid(row=0, column=0, sticky='e', padx=5, pady=5)

            var_inizio = tk.StringVar()
            setattr(self, f'strao{i}_inizio_var', var_inizio)
            ttk.Entry(slot_frame, textvariable=var_inizio, width=10).grid(
                row=0, column=1, sticky='w', padx=5, pady=5)

            ttk.Label(slot_frame, text="Ora Fine:").grid(row=0, column=2, sticky='e', padx=(20,5), pady=5)

            var_fine = tk.StringVar()
            setattr(self, f'strao{i}_fine_var', var_fine)
            ttk.Entry(slot_frame, textvariable=var_fine, width=10).grid(
                row=0, column=3, sticky='w', padx=5, pady=5)

            # Bottone clear
            ttk.Button(slot_frame, text="Cancella",
                      command=lambda idx=i: self.clear_strao(idx),
                      width=10).grid(row=0, column=4, padx=10)

    def setup_giust_tab(self):
        """Tab per giustificativi"""
        frame = ttk.Frame(self.tab_giust, padding=20)
        frame.pack(fill='both', expand=True)

        ttk.Label(frame, text="Inserisci/Modifica Giustificativo:",
                 font=('Arial', 10, 'bold')).pack(pady=10)

        # Canvas per scroll
        canvas = tk.Canvas(frame, height=400)
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Slot giustificativi
        giust_types = ['', 'Assenza', 'Ferie', 'Malattia', 'Permesso', 'ROL', 'Congedo']

        for i in range(1, 6):
            slot_frame = ttk.LabelFrame(scrollable_frame, text=f"Giustificativo {i}", padding=10)
            slot_frame.pack(fill='x', pady=5, padx=5)

            # Tipo
            ttk.Label(slot_frame, text="Tipo:").grid(row=0, column=0, sticky='e', padx=5, pady=5)

            var_tipo = tk.StringVar()
            setattr(self, f'giust{i}_tipo_var', var_tipo)
            combo = ttk.Combobox(slot_frame, textvariable=var_tipo,
                                values=giust_types, width=15, state='readonly')
            combo.grid(row=0, column=1, sticky='w', padx=5, pady=5)

            # Orari
            ttk.Label(slot_frame, text="Inizio:").grid(row=0, column=2, sticky='e', padx=(20,5), pady=5)

            var_inizio = tk.StringVar()
            setattr(self, f'giust{i}_inizio_var', var_inizio)
            ttk.Entry(slot_frame, textvariable=var_inizio, width=10).grid(
                row=0, column=3, sticky='w', padx=5, pady=5)

            ttk.Label(slot_frame, text="Fine:").grid(row=0, column=4, sticky='e', padx=(20,5), pady=5)

            var_fine = tk.StringVar()
            setattr(self, f'giust{i}_fine_var', var_fine)
            ttk.Entry(slot_frame, textvariable=var_fine, width=10).grid(
                row=0, column=5, sticky='w', padx=5, pady=5)

            # Bottone clear
            ttk.Button(slot_frame, text="Cancella",
                      command=lambda idx=i: self.clear_giust(idx),
                      width=10).grid(row=0, column=6, padx=10)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def load_operatori_list(self):
        """Carica lista operatori"""
        try:
            self.db_manager.connect()
            # Carica operatori unici
            query = "SELECT DISTINCT ID_SAP, Nome, Cognome FROM Anagrafica_Operatori ORDER BY Cognome, Nome"
            result = self.db_manager.execute_query(query)

            operatori = []
            self.operatori_map = {}  # Map display -> ID_SAP

            for row in result:
                id_sap = row[0]
                nome = row[1]
                cognome = row[2]
                display = f"{cognome} {nome} ({id_sap})"
                operatori.append(display)
                self.operatori_map[display] = id_sap

            self.operatore_combo['values'] = operatori

            if operatori:
                self.operatore_combo.current(0)

            self.db_manager.close()

        except Exception as e:
            messagebox.showerror("Errore", f"Errore caricamento operatori: {e}")

    def on_operatore_change(self, event=None):
        """Gestisce cambio operatore"""
        self.load_operatore()

    def on_date_change(self, event=None):
        """Gestisce cambio data"""
        self.load_operatore()

    def load_operatore(self):
        """Carica dati operatore per data selezionata"""
        try:
            operatore_display = self.operatore_var.get()
            if not operatore_display:
                return

            id_sap = self.operatori_map.get(operatore_display)
            if not id_sap:
                return

            data = self.date_var.get()

            self.db_manager.connect()
            query = """
                SELECT * FROM Anagrafica_Operatori
                WHERE ID_SAP = ? AND Data_Riferimento = ?
            """
            result = self.db_manager.execute_query(query, (id_sap, data))

            if result:
                # Dati trovati
                row = result[0]
                self.operatore_data = self._row_to_dict(row)
                self.populate_fields()
                self.update_current_label()
            else:
                # Nessun dato per questa data
                messagebox.showinfo("Info",
                                   f"Nessun dato trovato per {operatore_display} in data {data}.\n\n"
                                   "Puoi inserire nuovi dati e salvarli.")
                self.operatore_data = None
                self.clear_all_fields()
                self.update_current_label()

            self.db_manager.close()

        except Exception as e:
            messagebox.showerror("Errore", f"Errore caricamento dati: {e}")
            import traceback
            traceback.print_exc()

    def populate_fields(self):
        """Popola i campi con dati operatore"""
        if not self.operatore_data:
            return

        # Postazione
        self.postazione_var.set(self.operatore_data.get('Postazione', 'Sede'))

        # Turno
        self.turno_inizio_var.set(self._time_to_str(self.operatore_data.get('Ora_Inizio_Turno')))
        self.turno_fine_var.set(self._time_to_str(self.operatore_data.get('Ora_Fine_Turno')))
        self.spezzato_inizio_var.set(self._time_to_str(self.operatore_data.get('Ora_Inizio_Turno_Spezzato')))
        self.spezzato_fine_var.set(self._time_to_str(self.operatore_data.get('Ora_Fine_Turno_Spezzato')))

        # Straordinari
        for i in range(1, 4):
            inizio_var = getattr(self, f'strao{i}_inizio_var')
            fine_var = getattr(self, f'strao{i}_fine_var')
            inizio_var.set(self._time_to_str(self.operatore_data.get(f'Inizio_Strao_{i}')))
            fine_var.set(self._time_to_str(self.operatore_data.get(f'Fine_Strao_{i}')))

        # Giustificativi
        for i in range(1, 6):
            tipo_var = getattr(self, f'giust{i}_tipo_var')
            inizio_var = getattr(self, f'giust{i}_inizio_var')
            fine_var = getattr(self, f'giust{i}_fine_var')
            tipo_var.set(self.operatore_data.get(f'Tipo_Giust_{i}', ''))
            inizio_var.set(self._time_to_str(self.operatore_data.get(f'Inizio_Giust_{i}')))
            fine_var.set(self._time_to_str(self.operatore_data.get(f'Fine_Giust_{i}')))

    def clear_all_fields(self):
        """Pulisci tutti i campi"""
        self.postazione_var.set('Sede')
        self.turno_inizio_var.set('')
        self.turno_fine_var.set('')
        self.spezzato_inizio_var.set('')
        self.spezzato_fine_var.set('')

        for i in range(1, 4):
            self.clear_strao(i)

        for i in range(1, 6):
            self.clear_giust(i)

    def update_current_label(self):
        """Aggiorna label dati attuali"""
        if not self.operatore_data:
            self.current_label.config(text="Nessun dato per questa data", foreground='gray')
            return

        turno = f"{self._time_to_str(self.operatore_data.get('Ora_Inizio_Turno'))} - {self._time_to_str(self.operatore_data.get('Ora_Fine_Turno'))}"
        postazione = self.operatore_data.get('Postazione', 'Non specificata')

        text = f"Turno: {turno} | Postazione: {postazione}"
        self.current_label.config(text=text, foreground='black')

    def set_turno_rapido(self, inizio, fine):
        """Imposta turno con bottoni rapidi"""
        self.turno_inizio_var.set(inizio)
        self.turno_fine_var.set(fine)

    def clear_strao(self, idx):
        """Cancella slot straordinario"""
        getattr(self, f'strao{idx}_inizio_var').set('')
        getattr(self, f'strao{idx}_fine_var').set('')

    def clear_giust(self, idx):
        """Cancella slot giustificativo"""
        getattr(self, f'giust{idx}_tipo_var').set('')
        getattr(self, f'giust{idx}_inizio_var').set('')
        getattr(self, f'giust{idx}_fine_var').set('')

    def salva_modifiche(self):
        """Salva tutte le modifiche"""
        try:
            operatore_display = self.operatore_var.get()
            if not operatore_display:
                messagebox.showwarning("Attenzione", "Seleziona un operatore")
                return

            id_sap = self.operatori_map.get(operatore_display)
            data = self.date_var.get()

            # Raccogli dati
            dati = {
                'ID_SAP': id_sap,
                'Data_Riferimento': data,
                'Postazione': self.postazione_var.get(),
                'Ora_Inizio_Turno': self.turno_inizio_var.get() or None,
                'Ora_Fine_Turno': self.turno_fine_var.get() or None,
                'Ora_Inizio_Turno_Spezzato': self.spezzato_inizio_var.get() or None,
                'Ora_Fine_Turno_Spezzato': self.spezzato_fine_var.get() or None,
            }

            # Straordinari
            for i in range(1, 4):
                dati[f'Inizio_Strao_{i}'] = getattr(self, f'strao{i}_inizio_var').get() or None
                dati[f'Fine_Strao_{i}'] = getattr(self, f'strao{i}_fine_var').get() or None

            # Giustificativi
            for i in range(1, 6):
                dati[f'Tipo_Giust_{i}'] = getattr(self, f'giust{i}_tipo_var').get() or None
                dati[f'Inizio_Giust_{i}'] = getattr(self, f'giust{i}_inizio_var').get() or None
                dati[f'Fine_Giust_{i}'] = getattr(self, f'giust{i}_fine_var').get() or None

            # Salva nel database
            self.db_manager.connect()

            if self.operatore_data:
                # Update
                op_id = self.operatore_data.get('ID')
                query = "UPDATE Anagrafica_Operatori SET "
                updates = []
                values = []

                for key, value in dati.items():
                    if key not in ['ID_SAP', 'Data_Riferimento']:
                        updates.append(f"{key} = ?")
                        values.append(value)

                query += ', '.join(updates)
                query += " WHERE ID = ?"
                values.append(op_id)

                self.db_manager.execute_update(query, tuple(values))

            else:
                # Insert nuovo record
                # Carica dati base operatore
                query_base = """
                    SELECT Nome, Cognome, Tipo_Contratto, FTE, Ore_Settimana, Etichetta_Skill
                    FROM Anagrafica_Operatori
                    WHERE ID_SAP = ?
                    LIMIT 1
                """
                result = self.db_manager.execute_query(query_base, (id_sap,))

                if result:
                    row = result[0]
                    dati['Nome'] = row[0]
                    dati['Cognome'] = row[1]
                    dati['Tipo_Contratto'] = row[2]
                    dati['FTE'] = row[3]
                    dati['Ore_Settimana'] = row[4]
                    dati['Etichetta_Skill'] = row[5]

                self.db_manager.insert_operatore(dati)

            self.db_manager.close()

            messagebox.showinfo("Successo", "Modifiche salvate con successo!")
            self.destroy()

        except Exception as e:
            messagebox.showerror("Errore", f"Errore salvataggio: {e}")
            import traceback
            traceback.print_exc()

    def _row_to_dict(self, row):
        """Converte row in dict"""
        if hasattr(row, 'cursor_description'):
            return {desc[0]: getattr(row, desc[0]) for desc in row.cursor_description}
        return {}

    def _time_to_str(self, value):
        """Converte time in stringa"""
        if value is None or value == '':
            return ''

        if isinstance(value, str):
            return value

        if isinstance(value, time):
            return value.strftime('%H:%M')

        return str(value)
