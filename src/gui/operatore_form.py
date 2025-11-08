"""
Form per inserimento/modifica anagrafica operatore
"""
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, time
from tkcalendar import DateEntry


class OperatoreForm(tk.Toplevel):
    """Form completo per gestione anagrafica operatore"""

    def __init__(self, parent, db_manager, operatore_id=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.operatore_id = operatore_id

        self.title("Anagrafica Operatore" if not operatore_id else "Modifica Operatore")
        self.geometry("900x700")
        self.resizable(False, False)

        # Variabili form
        self.vars = {}

        # Setup UI
        self.setup_ui()

        # Carica dati se modifica
        if operatore_id:
            self.load_operatore()

    def setup_ui(self):
        """Crea l'interfaccia del form"""
        # Main container con scrollbar
        main_frame = ttk.Frame(self)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)

        # Canvas per scroll
        canvas = tk.Canvas(main_frame)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # === SEZIONE DATI ANAGRAFICI ===
        self.create_section(scrollable_frame, "DATI ANAGRAFICI", 0)

        row = 1
        self.create_field(scrollable_frame, row, "Nome *:", "Nome", entry_width=30)
        self.create_field(scrollable_frame, row, "Cognome *:", "Cognome", entry_width=30, col_offset=3)

        row += 1
        self.create_field(scrollable_frame, row, "ID SAP *:", "ID_SAP", entry_width=15)
        self.create_field(scrollable_frame, row, "Tipo Contratto:", "Tipo_Contratto",
                         combo_values=['Full Time', 'Part Time', 'Tempo Determinato'], col_offset=3)

        row += 1
        self.create_field(scrollable_frame, row, "FTE:", "FTE", entry_width=10, default="1.0")
        self.create_field(scrollable_frame, row, "Ore Settimana:", "Ore_Settimana", entry_width=10, default="40", col_offset=3)

        row += 1
        self.create_field(scrollable_frame, row, "Data Riferimento *:", "Data_Riferimento",
                         is_date=True, default=datetime.now().strftime('%Y-%m-%d'))

        # === SEZIONE TURNO ===
        row += 1
        self.create_section(scrollable_frame, "TURNO ORDINARIO", row)

        row += 1
        self.create_field(scrollable_frame, row, "ID Turno:", "ID_Turno", entry_width=15)
        self.create_field(scrollable_frame, row, "Ora Inizio:", "Ora_Inizio_Turno",
                         is_time=True, default="09:00", col_offset=3)
        self.create_field(scrollable_frame, row, "Ora Fine:", "Ora_Fine_Turno",
                         is_time=True, default="18:00", col_offset=5)

        # Turno spezzato
        row += 1
        ttk.Label(scrollable_frame, text="Turno Spezzato (opzionale):",
                 font=('Arial', 9, 'italic')).grid(row=row, column=0, columnspan=2, sticky='w', pady=(10,5))

        row += 1
        self.create_field(scrollable_frame, row, "Ora Inizio:", "Ora_Inizio_Turno_Spezzato",
                         is_time=True, col_offset=0)
        self.create_field(scrollable_frame, row, "Ora Fine:", "Ora_Fine_Turno_Spezzato",
                         is_time=True, col_offset=3)

        # === SEZIONE STRAORDINARI ===
        row += 1
        self.create_section(scrollable_frame, "STRAORDINARI (Max 3 Slot)", row)

        for i in range(1, 4):
            row += 1
            ttk.Label(scrollable_frame, text=f"Slot {i}:", font=('Arial', 9, 'bold')).grid(
                row=row, column=0, sticky='w', padx=5)
            self.create_field(scrollable_frame, row, "Inizio:", f"Inizio_Strao_{i}",
                             is_time=True, col_offset=1, label_width=8)
            self.create_field(scrollable_frame, row, "Fine:", f"Fine_Strao_{i}",
                             is_time=True, col_offset=4, label_width=6)

        # === SEZIONE PAUSE ===
        row += 1
        self.create_section(scrollable_frame, "PAUSE (Max 5 Slot)", row)

        # Checkbox e bottone pause automatiche
        row += 1
        pause_auto_frame = ttk.Frame(scrollable_frame)
        pause_auto_frame.grid(row=row, column=0, columnspan=6, sticky='w', padx=5, pady=5)

        self.pause_auto_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            pause_auto_frame,
            text="🤖 Calcola pause automaticamente (distribuzione intelligente)",
            variable=self.pause_auto_var
        ).pack(side='left', padx=5)

        ttk.Button(
            pause_auto_frame,
            text="⚡ Calcola Ora",
            command=self.calcola_pause_automatiche,
            width=15
        ).pack(side='left', padx=5)

        # Label info distribuzione
        self.pause_info_label = ttk.Label(
            pause_auto_frame,
            text="",
            foreground='blue',
            font=('Arial', 8, 'italic')
        )
        self.pause_info_label.pack(side='left', padx=10)

        for i in range(1, 6):
            row += 1
            ttk.Label(scrollable_frame, text=f"Pausa {i}:", font=('Arial', 9, 'bold')).grid(
                row=row, column=0, sticky='w', padx=5)
            self.create_field(scrollable_frame, row, "Inizio:", f"Inizio_Pausa_{i}",
                             is_time=True, col_offset=1, label_width=8)
            self.create_field(scrollable_frame, row, "Fine:", f"Fine_Pausa_{i}",
                             is_time=True, col_offset=4, label_width=6)

        # === SEZIONE GIUSTIFICATIVI ===
        row += 1
        self.create_section(scrollable_frame, "GIUSTIFICATIVI (Max 5 Slot)", row)

        giust_types = ['', 'Assenza', 'Ferie', 'Malattia', 'Permesso', 'ROL', 'Congedo']

        for i in range(1, 6):
            row += 1
            ttk.Label(scrollable_frame, text=f"Giustificativo {i}:", font=('Arial', 9, 'bold')).grid(
                row=row, column=0, sticky='w', padx=5)
            self.create_field(scrollable_frame, row, "Tipo:", f"Tipo_Giust_{i}",
                             combo_values=giust_types, col_offset=1, label_width=8, entry_width=15)
            self.create_field(scrollable_frame, row, "Inizio:", f"Inizio_Giust_{i}",
                             is_time=True, col_offset=3, label_width=8)
            self.create_field(scrollable_frame, row, "Fine:", f"Fine_Giust_{i}",
                             is_time=True, col_offset=5, label_width=6)

        # === SEZIONE SKILL ===
        row += 1
        self.create_section(scrollable_frame, "SKILL / COMPETENZA", row)

        row += 1
        # Carica skills dal database
        skills_list = self.get_skills_list()
        self.create_field(scrollable_frame, row, "Etichetta Skill *:", "Etichetta_Skill",
                         combo_values=skills_list, entry_width=30)

        # === SEZIONE POSTAZIONE ===
        row += 1
        self.create_section(scrollable_frame, "POSTAZIONE (Sede/Smart Working)", row)

        row += 1
        postazioni = ['', 'Sede', 'Smart Working', 'Trasferta', 'Permesso', 'Assente']
        self.create_field(scrollable_frame, row, "Postazione:", "Postazione",
                         combo_values=postazioni, entry_width=20, default='Sede')

        # === BOTTONI ===
        row += 1
        btn_frame = ttk.Frame(scrollable_frame)
        btn_frame.grid(row=row, column=0, columnspan=7, pady=20)

        ttk.Button(btn_frame, text="Salva", command=self.salva,
                  width=20, style='Accent.TButton').pack(side='left', padx=10)
        ttk.Button(btn_frame, text="Annulla", command=self.destroy,
                  width=20).pack(side='left', padx=10)

        # Pack canvas
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Bind mousewheel
        canvas.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1*(e.delta/120)), "units"))

    def create_section(self, parent, title, row):
        """Crea una sezione header"""
        section_frame = ttk.Frame(parent, relief='ridge', borderwidth=2)
        section_frame.grid(row=row, column=0, columnspan=7, sticky='ew', pady=(15, 5), padx=5)

        ttk.Label(section_frame, text=title, font=('Arial', 11, 'bold'),
                 background='#e0e0e0').pack(fill='x', padx=5, pady=5)

    def create_field(self, parent, row, label, var_name, entry_width=20, combo_values=None,
                    is_time=False, is_date=False, default="", col_offset=0, label_width=None):
        """Crea un campo del form"""
        # Label
        lbl_width = label_width if label_width else 15
        ttk.Label(parent, text=label, width=lbl_width).grid(
            row=row, column=col_offset, sticky='e', padx=5, pady=5)

        # Campo
        if combo_values:
            self.vars[var_name] = tk.StringVar(value=default)
            widget = ttk.Combobox(parent, textvariable=self.vars[var_name],
                                 values=combo_values, width=entry_width, state='readonly')
        elif is_date:
            self.vars[var_name] = tk.StringVar(value=default)
            widget = DateEntry(parent, textvariable=self.vars[var_name],
                              width=entry_width, date_pattern='yyyy-mm-dd')
        elif is_time:
            self.vars[var_name] = tk.StringVar(value=default)
            widget = ttk.Entry(parent, textvariable=self.vars[var_name], width=10)
            # Placeholder per formato
            if not default:
                widget.insert(0, "HH:MM")
                widget.config(foreground='gray')
                widget.bind('<FocusIn>', lambda e: self.on_time_focus_in(e, var_name))
        else:
            self.vars[var_name] = tk.StringVar(value=default)
            widget = ttk.Entry(parent, textvariable=self.vars[var_name], width=entry_width)

        widget.grid(row=row, column=col_offset+1, sticky='w', padx=5, pady=5)

    def on_time_focus_in(self, event, var_name):
        """Gestisce focus su campo time"""
        widget = event.widget
        if widget.get() == "HH:MM":
            widget.delete(0, 'end')
            widget.config(foreground='black')

    def get_skills_list(self):
        """Recupera lista skills dal database"""
        try:
            self.db_manager.connect()
            skills = self.db_manager.get_skills()
            self.db_manager.close()
            return [''] + [skill[1] for skill in skills]  # skill[1] = Codice_Skill
        except:
            return ['CUSTOMER_CARE', 'BACK_OFFICE', 'TECHNICAL_SUPPORT']

    def load_operatore(self):
        """Carica dati operatore esistente"""
        try:
            self.db_manager.connect()

            # Ottieni i nomi delle colonne
            cursor = self.db_manager.execute_query(
                "SELECT * FROM Anagrafica_Operatori WHERE ID = ?",
                (self.operatore_id,)
            )

            if cursor and len(cursor) > 0:
                # Ottieni nomi colonne e dati
                columns = [
                    'ID', 'Nome', 'Cognome', 'ID_SAP', 'Tipo_Contratto', 'FTE', 'Ore_Settimana',
                    'ID_Turno', 'Ora_Inizio_Turno', 'Ora_Fine_Turno',
                    'Ora_Inizio_Turno_Spezzato', 'Ora_Fine_Turno_Spezzato',
                    'Inizio_Strao_1', 'Fine_Strao_1', 'Inizio_Strao_2', 'Fine_Strao_2',
                    'Inizio_Strao_3', 'Fine_Strao_3',
                    'Inizio_Pausa_1', 'Fine_Pausa_1', 'Inizio_Pausa_2', 'Fine_Pausa_2',
                    'Inizio_Pausa_3', 'Fine_Pausa_3', 'Inizio_Pausa_4', 'Fine_Pausa_4',
                    'Inizio_Pausa_5', 'Fine_Pausa_5',
                    'Tipo_Giust_1', 'Inizio_Giust_1', 'Fine_Giust_1',
                    'Tipo_Giust_2', 'Inizio_Giust_2', 'Fine_Giust_2',
                    'Tipo_Giust_3', 'Inizio_Giust_3', 'Fine_Giust_3',
                    'Tipo_Giust_4', 'Inizio_Giust_4', 'Fine_Giust_4',
                    'Tipo_Giust_5', 'Inizio_Giust_5', 'Fine_Giust_5',
                    'Etichetta_Skill', 'Data_Riferimento', 'Postazione'
                ]

                op_data = cursor[0]

                # Carica i valori nei campi del form
                for idx, col_name in enumerate(columns):
                    if col_name in self.vars and idx < len(op_data):
                        value = op_data[idx]
                        if value is not None:
                            # Converti datetime/time in stringa HH:MM per campi orario
                            if 'Ora_' in col_name or 'Inizio_' in col_name or 'Fine_' in col_name:
                                if col_name != 'Ore_Settimana':  # Escludi Ore_Settimana che è numerico
                                    # Estrai solo HH:MM se è datetime
                                    value_str = str(value)
                                    if ' ' in value_str:
                                        value_str = value_str.split(' ')[1]  # Prendi la parte time
                                    if len(value_str) >= 5:
                                        value_str = value_str[:5]  # HH:MM
                                    self.vars[col_name].set(value_str)
                                else:
                                    self.vars[col_name].set(str(value))
                            elif col_name == 'Data_Riferimento':
                                # Converti data in formato YYYY-MM-DD
                                value_str = str(value)
                                if ' ' in value_str:
                                    value_str = value_str.split(' ')[0]  # Solo la data
                                self.vars[col_name].set(value_str)
                            else:
                                self.vars[col_name].set(str(value))

            self.db_manager.close()
        except Exception as e:
            messagebox.showerror("Errore", f"Errore caricamento operatore: {e}")
            import traceback
            traceback.print_exc()

    def calcola_pause_automatiche(self):
        """Calcola e assegna pause automaticamente con distribuzione intelligente"""
        from utils.pause_scheduler import PauseScheduler

        # Validazione campi necessari
        ora_inizio = self.vars.get('Ora_Inizio_Turno', tk.StringVar()).get().strip()
        ora_fine = self.vars.get('Ora_Fine_Turno', tk.StringVar()).get().strip()
        skill = self.vars.get('Etichetta_Skill', tk.StringVar()).get().strip()
        data = self.vars.get('Data_Riferimento', tk.StringVar()).get().strip()

        if not ora_inizio:
            messagebox.showwarning("Attenzione", "Inserisci Ora Inizio Turno prima")
            return

        if not skill:
            messagebox.showwarning("Attenzione", "Seleziona Skill prima")
            return

        if not data:
            messagebox.showwarning("Attenzione", "Inserisci Data Riferimento prima")
            return

        try:
            # Crea scheduler
            scheduler = PauseScheduler(self.db_manager)

            # Determina ID_SAP corrente (se editing)
            id_sap_corrente = None
            if self.operatore_id:
                id_sap_corrente = self.vars.get('ID_SAP', tk.StringVar()).get().strip()

            # Calcola pause (1 pausa di 15 minuti)
            pause = scheduler.calcola_pause_automatiche(
                ora_inizio_turno=ora_inizio,
                ora_fine_turno=ora_fine or "18:00",
                skill=skill,
                data_riferimento=data,
                id_sap_corrente=id_sap_corrente,
                num_pause=1  # 1 pausa di 15 minuti
            )

            if not pause:
                messagebox.showinfo("Info", "Non è stato possibile calcolare pause automatiche.\nTurno troppo corto o dati non validi.")
                return

            # Assegna pause ai campi
            for idx, (inizio, fine) in enumerate(pause, 1):
                if idx <= 5:  # Max 5 slot pause
                    self.vars[f'Inizio_Pausa_{idx}'].set(inizio)
                    self.vars[f'Fine_Pausa_{idx}'].set(fine)

            # Mostra info distribuzione
            dist = scheduler.visualizza_distribuzione(skill, data)
            info_text = f"Slot 1h45: {dist['slot_1h45']} | Slot 2h: {dist['slot_2h']} | Slot 2h15: {dist['slot_2h15']} operatori"
            self.pause_info_label.config(text=info_text)

            messagebox.showinfo(
                "Pause Calcolate",
                f"✅ Pause assegnate automaticamente!\n\n"
                f"Distribuzione attuale:\n"
                f"• Slot 1h45 (dopo inizio turno): {dist['slot_1h45']} operatori\n"
                f"• Slot 2h (dopo inizio turno): {dist['slot_2h']} operatori\n"
                f"• Slot 2h15 (dopo inizio turno): {dist['slot_2h15']} operatori\n\n"
                f"Bilanciamento: {dist['bilanciamento']}"
            )

        except Exception as e:
            messagebox.showerror("Errore", f"Errore calcolo pause:\n{e}")
            import traceback
            traceback.print_exc()

    def salva(self):
        """Salva l'operatore"""
        # Validazione campi obbligatori
        if not self.vars['Nome'].get().strip():
            messagebox.showwarning("Attenzione", "Il campo Nome è obbligatorio")
            return
        if not self.vars['Cognome'].get().strip():
            messagebox.showwarning("Attenzione", "Il campo Cognome è obbligatorio")
            return
        if not self.vars['ID_SAP'].get().strip():
            messagebox.showwarning("Attenzione", "Il campo ID SAP è obbligatorio")
            return

        # Valida orari
        if not self.validate_times():
            return

        # Prepara dati
        operatore_data = {}
        for var_name, var in self.vars.items():
            value = var.get().strip()
            # Converti "HH:MM" placeholder in None
            if value == "HH:MM" or value == "":
                operatore_data[var_name] = None
            else:
                operatore_data[var_name] = value

        # Salva nel database
        try:
            self.db_manager.connect()

            if self.operatore_id:
                # Update
                self.db_manager.update_operatore(self.operatore_id, operatore_data)
                messagebox.showinfo("Successo", "Operatore aggiornato con successo")
            else:
                # Insert
                self.db_manager.insert_operatore(operatore_data)
                messagebox.showinfo("Successo", "Operatore inserito con successo")

            self.db_manager.close()
            self.destroy()

        except Exception as e:
            messagebox.showerror("Errore", f"Errore salvataggio operatore: {e}")
            import traceback
            traceback.print_exc()

    def validate_times(self):
        """Valida i campi orario"""
        time_fields = []

        # Raccogli tutti i campi time
        for var_name in self.vars:
            if 'Ora_' in var_name or 'Inizio_' in var_name or 'Fine_' in var_name:
                time_fields.append(var_name)

        # Valida formato HH:MM
        for field in time_fields:
            value = self.vars[field].get().strip()
            if value and value != "HH:MM":
                if not self.is_valid_time(value):
                    messagebox.showwarning("Attenzione",
                                          f"Formato orario non valido per {field}.\nUsa formato HH:MM (es: 09:30)")
                    return False

        return True

    def is_valid_time(self, time_str):
        """Verifica se stringa è un orario valido"""
        try:
            parts = time_str.split(':')
            if len(parts) != 2:
                return False
            hour = int(parts[0])
            minute = int(parts[1])
            return 0 <= hour <= 23 and 0 <= minute <= 59
        except:
            return False
