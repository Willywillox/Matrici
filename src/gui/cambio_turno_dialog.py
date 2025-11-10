"""
Dialog per cambio turno tra operatori

Permette di:
- Selezionare 2 operatori e una data
- Visualizzare tutte le info complete dei due operatori
- Scambiare i turni tra loro
- Modificare tutte le info (straordinari, pause, giustificativi, postazione)
- Salvare le modifiche
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from tkcalendar import DateEntry


class CambioTurnoDialog(tk.Toplevel):
    """Dialog per gestione cambio turno tra operatori"""

    def __init__(self, parent, db_manager):
        super().__init__(parent)
        self.db_manager = db_manager

        self.title("Cambio Turno tra Operatori")
        self.geometry("1200x800")

        # Dati operatori
        self.operatori_list = []
        self.op_a_data = {}
        self.op_b_data = {}

        # Variabili form
        self.vars_a = {}
        self.vars_b = {}

        # Carica giustificativi dal database
        self.giust_types = ['']  # Stringa vuota per "nessun giustificativo"
        self.load_giustificativi()

        # Setup UI
        self.setup_ui()
        self.load_operatori()

    def setup_ui(self):
        """Crea interfaccia dialog"""

        # === HEADER - Selezione operatori e data ===
        header_frame = ttk.LabelFrame(self, text="Selezione Operatori e Data", padding=10)
        header_frame.pack(fill='x', padx=10, pady=10)

        # Operatore A
        ttk.Label(header_frame, text="Operatore A:", font=('Arial', 10, 'bold')).grid(
            row=0, column=0, sticky='e', padx=5, pady=5)
        self.combo_op_a = ttk.Combobox(header_frame, width=30, state='readonly')
        self.combo_op_a.grid(row=0, column=1, padx=5, pady=5)
        self.combo_op_a.bind('<<ComboboxSelected>>', self.on_operatore_a_selected)

        # Operatore B
        ttk.Label(header_frame, text="Operatore B:", font=('Arial', 10, 'bold')).grid(
            row=0, column=2, sticky='e', padx=5, pady=5)
        self.combo_op_b = ttk.Combobox(header_frame, width=30, state='readonly')
        self.combo_op_b.grid(row=0, column=3, padx=5, pady=5)
        self.combo_op_b.bind('<<ComboboxSelected>>', self.on_operatore_b_selected)

        # Data
        ttk.Label(header_frame, text="Data:", font=('Arial', 10, 'bold')).grid(
            row=0, column=4, sticky='e', padx=5, pady=5)
        self.date_var = tk.StringVar(value=datetime.now().strftime('%d/%m/%Y'))
        self.date_entry = DateEntry(header_frame, textvariable=self.date_var,
                                    width=15, date_pattern='dd/mm/yyyy')
        self.date_entry.grid(row=0, column=5, padx=5, pady=5)
        self.date_entry.bind('<<DateEntrySelected>>', self.on_data_changed)

        # Bottone carica
        ttk.Button(header_frame, text="🔄 Carica Dati",
                  command=self.load_dati_operatori, style='Accent.TButton').grid(
            row=0, column=6, padx=10, pady=5)

        # === MAIN AREA - Due colonne per i due operatori ===
        main_frame = ttk.Frame(self)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)

        # Colonna Operatore A
        self.frame_a = ttk.LabelFrame(main_frame, text="📋 Operatore A - Info Completa", padding=10)
        self.frame_a.pack(side='left', fill='both', expand=True, padx=5)

        # Colonna Operatore B
        self.frame_b = ttk.LabelFrame(main_frame, text="📋 Operatore B - Info Completa", padding=10)
        self.frame_b.pack(side='right', fill='both', expand=True, padx=5)

        # Crea campi per operatore A
        self.create_operatore_fields(self.frame_a, self.vars_a)

        # Crea campi per operatore B
        self.create_operatore_fields(self.frame_b, self.vars_b)

        # === BOTTONI AZIONI ===
        actions_frame = ttk.Frame(self)
        actions_frame.pack(fill='x', padx=10, pady=10)

        ttk.Button(actions_frame, text="🔄 Scambia Turni",
                  command=self.scambia_turni, width=20,
                  style='Accent.TButton').pack(side='left', padx=10)

        ttk.Button(actions_frame, text="💾 Salva Modifiche",
                  command=self.salva_modifiche, width=20,
                  style='Accent.TButton').pack(side='left', padx=10)

        ttk.Button(actions_frame, text="Annulla",
                  command=self.destroy, width=20).pack(side='right', padx=10)

    def create_operatore_fields(self, parent, vars_dict):
        """Crea i campi per visualizzare/modificare dati operatore"""

        # Scrollable frame
        canvas = tk.Canvas(parent, highlightthickness=0)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        row = 0

        # === DATI ANAGRAFICI (read-only) ===
        ttk.Label(scrollable_frame, text="DATI ANAGRAFICA",
                 font=('Arial', 10, 'bold'), background='#e0e0e0').grid(
            row=row, column=0, columnspan=2, sticky='ew', pady=5)
        row += 1

        vars_dict['nome_cognome'] = tk.StringVar()
        ttk.Label(scrollable_frame, text="Nome:").grid(row=row, column=0, sticky='e', padx=5, pady=2)
        ttk.Label(scrollable_frame, textvariable=vars_dict['nome_cognome'],
                 font=('Arial', 9, 'bold')).grid(row=row, column=1, sticky='w', padx=5, pady=2)
        row += 1

        vars_dict['id_sap'] = tk.StringVar()
        ttk.Label(scrollable_frame, text="ID SAP:").grid(row=row, column=0, sticky='e', padx=5, pady=2)
        ttk.Label(scrollable_frame, textvariable=vars_dict['id_sap']).grid(
            row=row, column=1, sticky='w', padx=5, pady=2)
        row += 1

        # === TURNO ORDINARIO ===
        ttk.Label(scrollable_frame, text="TURNO ORDINARIO",
                 font=('Arial', 10, 'bold'), background='#e0e0e0').grid(
            row=row, column=0, columnspan=2, sticky='ew', pady=(10, 5))
        row += 1

        vars_dict['Ora_Inizio_Turno'] = self.create_editable_field(
            scrollable_frame, row, "Ora Inizio:", "09:00")
        row += 1
        vars_dict['Ora_Fine_Turno'] = self.create_editable_field(
            scrollable_frame, row, "Ora Fine:", "18:00")
        row += 1

        # === TURNO SPEZZATO ===
        ttk.Label(scrollable_frame, text="TURNO SPEZZATO (opzionale)",
                 font=('Arial', 9, 'italic')).grid(row=row, column=0, columnspan=2, sticky='w', pady=(10, 2))
        row += 1

        vars_dict['Ora_Inizio_Turno_Spezzato'] = self.create_editable_field(
            scrollable_frame, row, "Ora Inizio:")
        row += 1
        vars_dict['Ora_Fine_Turno_Spezzato'] = self.create_editable_field(
            scrollable_frame, row, "Ora Fine:")
        row += 1

        # === STRAORDINARI ===
        ttk.Label(scrollable_frame, text="STRAORDINARI",
                 font=('Arial', 10, 'bold'), background='#e0e0e0').grid(
            row=row, column=0, columnspan=2, sticky='ew', pady=(10, 5))
        row += 1

        for i in range(1, 4):
            ttk.Label(scrollable_frame, text=f"Slot {i}:", font=('Arial', 9, 'bold')).grid(
                row=row, column=0, columnspan=2, sticky='w', pady=2)
            row += 1
            vars_dict[f'Inizio_Strao_{i}'] = self.create_editable_field(
                scrollable_frame, row, "  Inizio:")
            row += 1
            vars_dict[f'Fine_Strao_{i}'] = self.create_editable_field(
                scrollable_frame, row, "  Fine:")
            row += 1

        # === PAUSE ===
        ttk.Label(scrollable_frame, text="PAUSE",
                 font=('Arial', 10, 'bold'), background='#e0e0e0').grid(
            row=row, column=0, columnspan=2, sticky='ew', pady=(10, 5))
        row += 1

        for i in range(1, 6):
            ttk.Label(scrollable_frame, text=f"Pausa {i}:", font=('Arial', 9, 'bold')).grid(
                row=row, column=0, columnspan=2, sticky='w', pady=2)
            row += 1
            vars_dict[f'Inizio_Pausa_{i}'] = self.create_editable_field(
                scrollable_frame, row, "  Inizio:")
            row += 1
            vars_dict[f'Fine_Pausa_{i}'] = self.create_editable_field(
                scrollable_frame, row, "  Fine:")
            row += 1

        # === GIUSTIFICATIVI ===
        ttk.Label(scrollable_frame, text="GIUSTIFICATIVI",
                 font=('Arial', 10, 'bold'), background='#e0e0e0').grid(
            row=row, column=0, columnspan=2, sticky='ew', pady=(10, 5))
        row += 1

        for i in range(1, 6):
            ttk.Label(scrollable_frame, text=f"Giust. {i}:", font=('Arial', 9, 'bold')).grid(
                row=row, column=0, columnspan=2, sticky='w', pady=2)
            row += 1
            vars_dict[f'Tipo_Giust_{i}'] = self.create_combo_field(
                scrollable_frame, row, "  Tipo:", self.giust_types)
            row += 1
            vars_dict[f'Inizio_Giust_{i}'] = self.create_editable_field(
                scrollable_frame, row, "  Inizio:")
            row += 1
            vars_dict[f'Fine_Giust_{i}'] = self.create_editable_field(
                scrollable_frame, row, "  Fine:")
            row += 1

        # === POSTAZIONE ===
        ttk.Label(scrollable_frame, text="POSTAZIONE",
                 font=('Arial', 10, 'bold'), background='#e0e0e0').grid(
            row=row, column=0, columnspan=2, sticky='ew', pady=(10, 5))
        row += 1

        postazioni = ['Sede', 'Smart Working', 'Trasferta', 'Permesso', 'Assente']
        vars_dict['Postazione'] = self.create_combo_field(
            scrollable_frame, row, "Postazione:", postazioni)
        row += 1

        # === SKILL ===
        ttk.Label(scrollable_frame, text="SKILL",
                 font=('Arial', 10, 'bold'), background='#e0e0e0').grid(
            row=row, column=0, columnspan=2, sticky='ew', pady=(10, 5))
        row += 1

        vars_dict['Etichetta_Skill'] = tk.StringVar()
        ttk.Label(scrollable_frame, text="Skill:").grid(row=row, column=0, sticky='e', padx=5, pady=2)
        ttk.Label(scrollable_frame, textvariable=vars_dict['Etichetta_Skill']).grid(
            row=row, column=1, sticky='w', padx=5, pady=2)
        row += 1

        # Pack canvas
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def create_editable_field(self, parent, row, label, default=""):
        """Crea campo editabile"""
        ttk.Label(parent, text=label).grid(row=row, column=0, sticky='e', padx=5, pady=2)
        var = tk.StringVar(value=default)
        entry = ttk.Entry(parent, textvariable=var, width=15)
        entry.grid(row=row, column=1, sticky='w', padx=5, pady=2)
        return var

    def create_combo_field(self, parent, row, label, values):
        """Crea campo combobox"""
        ttk.Label(parent, text=label).grid(row=row, column=0, sticky='e', padx=5, pady=2)
        var = tk.StringVar()
        combo = ttk.Combobox(parent, textvariable=var, values=values, width=13, state='readonly')
        combo.grid(row=row, column=1, sticky='w', padx=5, pady=2)
        return var

    def load_operatori(self):
        """Carica lista operatori nel combobox"""
        try:
            self.db_manager.connect()
            # Carica operatori distinti (un operatore per ID_SAP)
            operatori = self.db_manager.execute_query(
                """SELECT DISTINCT ID_SAP, Nome, Cognome
                   FROM Anagrafica_Operatori
                   ORDER BY Cognome, Nome"""
            )
            self.db_manager.close()

            if operatori:
                self.operatori_list = [
                    (row[0], f"{row[2]} {row[1]} ({row[0]})")  # (ID_SAP, "Cognome Nome (ID)")
                    for row in operatori
                ]
                display_list = [op[1] for op in self.operatori_list]
                self.combo_op_a['values'] = display_list
                self.combo_op_b['values'] = display_list

        except Exception as e:
            messagebox.showerror("Errore", f"Errore caricamento operatori:\n{e}")

    def load_giustificativi(self):
        """Carica lista giustificativi dal database"""
        try:
            self.db_manager.connect()
            giustificativi = self.db_manager.execute_query(
                "SELECT DISTINCT Codice_Giustificativo FROM Giustificativi ORDER BY Codice_Giustificativo"
            )
            self.db_manager.close()

            if giustificativi:
                # Aggiungi i codici alla lista (la stringa vuota è già presente)
                self.giust_types.extend([row[0] for row in giustificativi])
            else:
                # Se il database è vuoto, usa valori di default
                self.giust_types.extend(['Assenza', 'Ferie', 'Malattia', 'Permesso', 'ROL', 'Congedo'])

        except Exception as e:
            # In caso di errore, usa valori di default
            print(f"[WARNING] Errore caricamento giustificativi: {e}")
            self.giust_types.extend(['Assenza', 'Ferie', 'Malattia', 'Permesso', 'ROL', 'Congedo'])

    def on_operatore_a_selected(self, event=None):
        """Quando viene selezionato operatore A"""
        pass  # I dati vengono caricati quando si preme "Carica Dati"

    def on_operatore_b_selected(self, event=None):
        """Quando viene selezionato operatore B"""
        pass  # I dati vengono caricati quando si preme "Carica Dati"

    def on_data_changed(self, event=None):
        """Quando viene cambiata la data"""
        pass  # I dati vengono ricaricati quando si preme "Carica Dati"

    def load_dati_operatori(self):
        """Carica i dati completi dei due operatori per la data selezionata"""
        # Verifica selezioni
        if not self.combo_op_a.get():
            messagebox.showwarning("Attenzione", "Seleziona Operatore A")
            return

        if not self.combo_op_b.get():
            messagebox.showwarning("Attenzione", "Seleziona Operatore B")
            return

        # Ottieni ID_SAP
        idx_a = self.combo_op_a.current()
        idx_b = self.combo_op_b.current()

        if idx_a == idx_b:
            messagebox.showwarning("Attenzione", "Seleziona due operatori diversi")
            return

        id_sap_a = self.operatori_list[idx_a][0]
        id_sap_b = self.operatori_list[idx_b][0]
        data_str = self.date_var.get()

        # Converti data da formato italiano (dd/mm/yyyy) a ISO (yyyy-mm-dd) per database
        try:
            data_obj = datetime.strptime(data_str, '%d/%m/%Y')
            data = data_obj.strftime('%Y-%m-%d')
        except:
            messagebox.showerror("Errore", "Formato data non valido")
            return

        # Carica dati
        self.op_a_data = self.load_operatore_data(id_sap_a, data)
        self.op_b_data = self.load_operatore_data(id_sap_b, data)

        # Popola campi
        if self.op_a_data:
            self.populate_fields(self.vars_a, self.op_a_data)
        else:
            messagebox.showwarning("Attenzione",
                                  f"Nessun dato trovato per Operatore A nella data {data}")

        if self.op_b_data:
            self.populate_fields(self.vars_b, self.op_b_data)
        else:
            messagebox.showwarning("Attenzione",
                                  f"Nessun dato trovato per Operatore B nella data {data}")

    def load_operatore_data(self, id_sap, data):
        """Carica dati completi operatore per una data specifica"""
        try:
            self.db_manager.connect()
            result = self.db_manager.execute_query(
                """SELECT * FROM Anagrafica_Operatori
                   WHERE ID_SAP = ? AND Data_Riferimento = ?""",
                (id_sap, data)
            )
            self.db_manager.close()

            if result and len(result) > 0:
                # Mappa risultato a dizionario
                row = result[0]
                return {
                    'ID': row[0],
                    'Nome': row[1],
                    'Cognome': row[2],
                    'ID_SAP': row[3],
                    'Ora_Inizio_Turno': row[8],
                    'Ora_Fine_Turno': row[9],
                    'Ora_Inizio_Turno_Spezzato': row[10],
                    'Ora_Fine_Turno_Spezzato': row[11],
                    'Inizio_Strao_1': row[12], 'Fine_Strao_1': row[13],
                    'Inizio_Strao_2': row[14], 'Fine_Strao_2': row[15],
                    'Inizio_Strao_3': row[16], 'Fine_Strao_3': row[17],
                    'Inizio_Pausa_1': row[18], 'Fine_Pausa_1': row[19],
                    'Inizio_Pausa_2': row[20], 'Fine_Pausa_2': row[21],
                    'Inizio_Pausa_3': row[22], 'Fine_Pausa_3': row[23],
                    'Inizio_Pausa_4': row[24], 'Fine_Pausa_4': row[25],
                    'Inizio_Pausa_5': row[26], 'Fine_Pausa_5': row[27],
                    'Tipo_Giust_1': row[28], 'Inizio_Giust_1': row[29], 'Fine_Giust_1': row[30],
                    'Tipo_Giust_2': row[31], 'Inizio_Giust_2': row[32], 'Fine_Giust_2': row[33],
                    'Tipo_Giust_3': row[34], 'Inizio_Giust_3': row[35], 'Fine_Giust_3': row[36],
                    'Tipo_Giust_4': row[37], 'Inizio_Giust_4': row[38], 'Fine_Giust_4': row[39],
                    'Tipo_Giust_5': row[40], 'Inizio_Giust_5': row[41], 'Fine_Giust_5': row[42],
                    'Etichetta_Skill': row[43],
                    'Data_Riferimento': row[44],
                    'Postazione': row[45] if len(row) > 45 else 'Sede'
                }
            return None

        except Exception as e:
            print(f"Errore caricamento dati operatore: {e}")
            import traceback
            traceback.print_exc()
            return None

    def populate_fields(self, vars_dict, data):
        """Popola i campi con i dati operatore"""
        # Helper per formattare time
        def format_time(value):
            if not value:
                return ''
            val_str = str(value)
            if ' ' in val_str:
                val_str = val_str.split(' ')[1]
            return val_str[:5] if len(val_str) >= 5 else val_str

        # Anagrafica
        vars_dict['nome_cognome'].set(f"{data['Cognome']} {data['Nome']}")
        vars_dict['id_sap'].set(data['ID_SAP'])
        vars_dict['Etichetta_Skill'].set(data.get('Etichetta_Skill', ''))

        # Turno
        vars_dict['Ora_Inizio_Turno'].set(format_time(data.get('Ora_Inizio_Turno')))
        vars_dict['Ora_Fine_Turno'].set(format_time(data.get('Ora_Fine_Turno')))
        vars_dict['Ora_Inizio_Turno_Spezzato'].set(format_time(data.get('Ora_Inizio_Turno_Spezzato')))
        vars_dict['Ora_Fine_Turno_Spezzato'].set(format_time(data.get('Ora_Fine_Turno_Spezzato')))

        # Straordinari
        for i in range(1, 4):
            vars_dict[f'Inizio_Strao_{i}'].set(format_time(data.get(f'Inizio_Strao_{i}')))
            vars_dict[f'Fine_Strao_{i}'].set(format_time(data.get(f'Fine_Strao_{i}')))

        # Pause
        for i in range(1, 6):
            vars_dict[f'Inizio_Pausa_{i}'].set(format_time(data.get(f'Inizio_Pausa_{i}')))
            vars_dict[f'Fine_Pausa_{i}'].set(format_time(data.get(f'Fine_Pausa_{i}')))

        # Giustificativi
        for i in range(1, 6):
            vars_dict[f'Tipo_Giust_{i}'].set(data.get(f'Tipo_Giust_{i}') or '')
            vars_dict[f'Inizio_Giust_{i}'].set(format_time(data.get(f'Inizio_Giust_{i}')))
            vars_dict[f'Fine_Giust_{i}'].set(format_time(data.get(f'Fine_Giust_{i}')))

        # Postazione
        vars_dict['Postazione'].set(data.get('Postazione', 'Sede'))

    def scambia_turni(self):
        """Scambia i turni tra Operatore A e Operatore B"""
        if not self.op_a_data or not self.op_b_data:
            messagebox.showwarning("Attenzione", "Carica prima i dati degli operatori")
            return

        # Scambia tutti i dati del turno
        fields_to_swap = [
            'Ora_Inizio_Turno', 'Ora_Fine_Turno',
            'Ora_Inizio_Turno_Spezzato', 'Ora_Fine_Turno_Spezzato',
            'Inizio_Strao_1', 'Fine_Strao_1',
            'Inizio_Strao_2', 'Fine_Strao_2',
            'Inizio_Strao_3', 'Fine_Strao_3',
            'Inizio_Pausa_1', 'Fine_Pausa_1',
            'Inizio_Pausa_2', 'Fine_Pausa_2',
            'Inizio_Pausa_3', 'Fine_Pausa_3',
            'Inizio_Pausa_4', 'Fine_Pausa_4',
            'Inizio_Pausa_5', 'Fine_Pausa_5',
        ]

        for field in fields_to_swap:
            temp = self.vars_a[field].get()
            self.vars_a[field].set(self.vars_b[field].get())
            self.vars_b[field].set(temp)

        messagebox.showinfo("Successo", "✅ Turni scambiati!\n\nOra premi 'Salva Modifiche' per confermare.")

    def salva_modifiche(self):
        """Salva le modifiche nel database"""
        if not self.op_a_data or not self.op_b_data:
            messagebox.showwarning("Attenzione", "Carica prima i dati degli operatori")
            return

        try:
            self.db_manager.connect()

            # Salva operatore A
            self.salva_operatore(self.op_a_data['ID'], self.vars_a)

            # Salva operatore B
            self.salva_operatore(self.op_b_data['ID'], self.vars_b)

            self.db_manager.close()

            messagebox.showinfo("Successo",
                               "✅ Modifiche salvate con successo!\n\n"
                               "Le modifiche sono state applicate ai turni degli operatori.")
            self.destroy()

        except Exception as e:
            messagebox.showerror("Errore", f"Errore salvataggio:\n{e}")
            import traceback
            traceback.print_exc()

    def salva_operatore(self, operatore_id, vars_dict):
        """Salva i dati di un singolo operatore"""
        # Prepara dati per update
        update_data = {}

        # Campi da salvare
        fields = [
            'Ora_Inizio_Turno', 'Ora_Fine_Turno',
            'Ora_Inizio_Turno_Spezzato', 'Ora_Fine_Turno_Spezzato',
        ]

        # Straordinari, pause, giustificativi
        for i in range(1, 4):
            fields.extend([f'Inizio_Strao_{i}', f'Fine_Strao_{i}'])

        for i in range(1, 6):
            fields.extend([f'Inizio_Pausa_{i}', f'Fine_Pausa_{i}'])
            fields.extend([f'Tipo_Giust_{i}', f'Inizio_Giust_{i}', f'Fine_Giust_{i}'])

        fields.append('Postazione')

        # Raccogli valori
        for field in fields:
            value = vars_dict[field].get().strip()
            update_data[field] = value if value else None

        # Update database
        self.db_manager.update_operatore(operatore_id, update_data)
