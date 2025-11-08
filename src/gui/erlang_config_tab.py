"""
Tab per configurazione parametri Erlang C per skill

Permette di configurare per ogni skill:
- Tipo canale (Voice, Chat, Email)
- AHT (Average Handle Time)
- Concurrency (per chat)
- Shrinkage
- Service Level targets
- ASA (Average Speed to Answer) per chat
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime


class ErlangConfigTab(ttk.Frame):
    """Tab per gestione configurazioni Erlang C"""

    def __init__(self, parent, db_manager):
        super().__init__(parent)
        self.db_manager = db_manager
        self.setup_ui()
        self.refresh_table()

    def setup_ui(self):
        """Crea l'interfaccia del tab"""

        # === PANNELLO PULSANTI ===
        button_frame = ttk.Frame(self)
        button_frame.pack(fill='x', padx=10, pady=10)

        ttk.Button(button_frame, text="➕ Nuova Configurazione",
                  command=self.add_config, width=25).pack(side='left', padx=5)
        ttk.Button(button_frame, text="✏️ Modifica",
                  command=self.edit_config, width=20).pack(side='left', padx=5)
        ttk.Button(button_frame, text="🗑️ Elimina",
                  command=self.delete_config, width=20).pack(side='left', padx=5)
        ttk.Button(button_frame, text="🔄 Aggiorna",
                  command=self.refresh_table, width=20).pack(side='left', padx=5)

        # === TABELLA CONFIGURAZIONI ===
        table_frame = ttk.LabelFrame(self, text="Configurazioni Erlang C per Skill", padding=10)
        table_frame.pack(fill='both', expand=True, padx=10, pady=5)

        # Scrollbars
        scroll_y = ttk.Scrollbar(table_frame, orient='vertical')
        scroll_y.pack(side='right', fill='y')

        scroll_x = ttk.Scrollbar(table_frame, orient='horizontal')
        scroll_x.pack(side='bottom', fill='x')

        # Colonne
        columns = (
            'ID', 'Skill', 'Canale', 'AHT(s)', 'Concurr.', 'Shrink%', 'Prod%',
            'SL%', 'SL(s)', 'ASA(s)', 'Occ%', 'Interval', 'Note'
        )

        self.tree = ttk.Treeview(table_frame, columns=columns, show='headings',
                                 yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set,
                                 height=20)

        scroll_y.config(command=self.tree.yview)
        scroll_x.config(command=self.tree.xview)

        # Larghezze colonne
        column_widths = {
            'ID': 50,
            'Skill': 180,
            'Canale': 80,
            'AHT(s)': 70,
            'Concurr.': 80,
            'Shrink%': 70,
            'Prod%': 70,
            'SL%': 60,
            'SL(s)': 60,
            'ASA(s)': 70,
            'Occ%': 60,
            'Interval': 70,
            'Note': 200
        }

        for col in columns:
            self.tree.heading(col, text=col)
            width = column_widths.get(col, 100)
            self.tree.column(col, width=width, anchor='center' if col != 'Note' else 'w')

        self.tree.pack(fill='both', expand=True)

        # Double-click per modificare
        self.tree.bind('<Double-1>', lambda e: self.edit_config())

        # === INFO PANEL ===
        info_frame = ttk.Frame(self)
        info_frame.pack(fill='x', padx=10, pady=5)

        info_text = ("💡 Configurazione Erlang C: definisci AHT, Service Level, Shrinkage e altri parametri per ogni skill. "
                    "Per CHAT, imposta Concurrency > 1 (quante chat simultanee per agente) e ASA target.")
        ttk.Label(info_frame, text=info_text, wraplength=1000,
                 font=('Arial', 9), foreground='#555').pack()

    def refresh_table(self):
        """Aggiorna la tabella con i dati dal database"""
        # Pulisci tabella
        for item in self.tree.get_children():
            self.tree.delete(item)

        try:
            self.db_manager.connect()

            configs = self.db_manager.execute_query("""
                SELECT ID, Skill, Tipo_Canale, AHT_Seconds, Concurrency,
                       Shrinkage, Produttivita, Service_Level_Target, Service_Level_Seconds,
                       ASA_Target_Seconds, Occupancy_Target, Interval_Minutes, Note
                FROM Erlang_Config
                ORDER BY Skill
            """)

            if configs:
                for cfg in configs:
                    config_id, skill, tipo_canale, aht, concurrency, shrinkage, produttivita, \
                    sl_target, sl_seconds, asa_seconds, occ_target, interval, note = cfg

                    # Formatta valori
                    shrink_pct = f"{shrinkage*100:.0f}%" if shrinkage else "0%"
                    prod_pct = f"{produttivita*100:.0f}%" if produttivita else "100%"
                    sl_pct = f"{sl_target*100:.0f}%" if sl_target else "0%"
                    occ_pct = f"{occ_target*100:.0f}%" if occ_target else "0%"

                    values = (
                        config_id,
                        skill,
                        tipo_canale or 'Voice',
                        aht or 180,
                        concurrency or 1,
                        shrink_pct,
                        prod_pct,
                        sl_pct,
                        sl_seconds or 20,
                        asa_seconds or 60,
                        occ_pct,
                        f"{interval}m" if interval else "30m",
                        note or ''
                    )

                    # Tag colore per tipo canale
                    tag = 'voice' if tipo_canale == 'Voice' else 'chat' if tipo_canale == 'Chat' else 'email'
                    self.tree.insert('', 'end', values=values, tags=(tag,))

            self.db_manager.close()

            # Tag colors
            self.tree.tag_configure('voice', background='#E8F4F8')
            self.tree.tag_configure('chat', background='#FFF4E6')
            self.tree.tag_configure('email', background='#F0F4F8')

        except Exception as e:
            messagebox.showerror("Errore", f"Errore caricamento configurazioni:\n{e}")

    def add_config(self):
        """Apre dialog per aggiungere nuova configurazione"""
        dialog = ErlangConfigDialog(self, self.db_manager, mode='add')
        self.wait_window(dialog)
        self.refresh_table()

    def edit_config(self):
        """Modifica configurazione selezionata"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Attenzione", "Selezionare una configurazione da modificare")
            return

        item = self.tree.item(selection[0])
        config_id = item['values'][0]

        dialog = ErlangConfigDialog(self, self.db_manager, mode='edit', config_id=config_id)
        self.wait_window(dialog)
        self.refresh_table()

    def delete_config(self):
        """Elimina configurazione selezionata"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Attenzione", "Selezionare una configurazione da eliminare")
            return

        item = self.tree.item(selection[0])
        config_id = item['values'][0]
        skill = item['values'][1]

        risposta = messagebox.askyesno(
            "Conferma Eliminazione",
            f"Eliminare la configurazione Erlang per skill '{skill}'?\n\n"
            "I calcoli FTE richiesti non funzioneranno più per questa skill."
        )

        if not risposta:
            return

        try:
            self.db_manager.connect()
            self.db_manager.execute_update(
                "DELETE FROM Erlang_Config WHERE ID = ?",
                (config_id,)
            )
            self.db_manager.close()

            messagebox.showinfo("Successo", f"Configurazione '{skill}' eliminata")
            self.refresh_table()

        except Exception as e:
            messagebox.showerror("Errore", f"Errore eliminazione:\n{e}")


class ErlangConfigDialog(tk.Toplevel):
    """Dialog per aggiungere/modificare configurazione Erlang"""

    def __init__(self, parent, db_manager, mode='add', config_id=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.mode = mode
        self.config_id = config_id

        self.title("Nuova Configurazione Erlang" if mode == 'add' else "Modifica Configurazione Erlang")
        self.geometry("700x750")
        self.resizable(False, False)

        # Centra finestra
        self.update_idletasks()
        x = (self.winfo_screenwidth() - 700) // 2
        y = (self.winfo_screenheight() - 750) // 2
        self.geometry(f"700x750+{x}+{y}")

        self.vars = {}
        self.available_skills = []
        self._load_skills()
        self.setup_ui()

        if mode == 'edit' and config_id:
            self.load_config()

    def setup_ui(self):
        """Crea form configurazione"""

        # Canvas con scrollbar
        canvas = tk.Canvas(self, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)

        scrollable_frame = ttk.Frame(canvas)
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # === FORM ===
        form = ttk.Frame(scrollable_frame, padding=20)
        form.pack(fill='both', expand=True)

        row = 0

        # Titolo
        ttk.Label(form, text="Configurazione Parametri Erlang C",
                 font=('Arial', 14, 'bold')).grid(row=row, column=0, columnspan=2, pady=(0, 20))
        row += 1

        # === SEZIONE BASE ===
        ttk.Label(form, text="📊 Informazioni Base",
                 font=('Arial', 11, 'bold')).grid(row=row, column=0, columnspan=2, sticky='w', pady=(10, 5))
        row += 1

        # Skill
        ttk.Label(form, text="Skill/Coda:*").grid(row=row, column=0, sticky='w', pady=5)
        skill_frame = ttk.Frame(form)
        skill_frame.grid(row=row, column=1, sticky='w', pady=5)

        self.vars['skill'] = tk.StringVar()

        # Debug: stampa cosa viene passato al Combobox
        print(f"[DEBUG] Creazione Combobox con {len(self.available_skills)} skills: {self.available_skills}")

        skill_combo = ttk.Combobox(skill_frame, textvariable=self.vars['skill'],
                                    values=self.available_skills, width=37, state='normal')
        skill_combo.pack(side='left')

        if self.mode == 'edit':
            skill_combo.config(state='readonly')  # Skill non modificabile in edit
        elif self.available_skills:
            skill_combo.current(0)  # Seleziona primo skill di default

        # Etichetta informativa
        if not self.available_skills and self.mode == 'add':
            ttk.Label(skill_frame, text="  ⚠️ Digita manualmente (Skills vuoto)",
                     foreground='#FF9800', font=('Arial', 8)).pack(side='left', padx=5)

        row += 1

        # Tipo Canale
        ttk.Label(form, text="Tipo Canale:*").grid(row=row, column=0, sticky='w', pady=5)
        self.vars['tipo_canale'] = tk.StringVar(value='Voice')
        canale_frame = ttk.Frame(form)
        canale_frame.grid(row=row, column=1, sticky='w', pady=5)

        ttk.Radiobutton(canale_frame, text="📞 Voice", variable=self.vars['tipo_canale'],
                       value='Voice', command=self.on_canale_change).pack(side='left', padx=5)
        ttk.Radiobutton(canale_frame, text="💬 Chat", variable=self.vars['tipo_canale'],
                       value='Chat', command=self.on_canale_change).pack(side='left', padx=5)
        ttk.Radiobutton(canale_frame, text="📧 Email", variable=self.vars['tipo_canale'],
                       value='Email', command=self.on_canale_change).pack(side='left', padx=5)
        row += 1

        # === SEZIONE PARAMETRI OPERATIVI ===
        ttk.Label(form, text="⚙️ Parametri Operativi",
                 font=('Arial', 11, 'bold')).grid(row=row, column=0, columnspan=2, sticky='w', pady=(15, 5))
        row += 1

        # AHT
        ttk.Label(form, text="AHT (secondi):*").grid(row=row, column=0, sticky='w', pady=5)
        aht_frame = ttk.Frame(form)
        aht_frame.grid(row=row, column=1, sticky='w', pady=5)
        self.vars['aht_seconds'] = tk.IntVar(value=180)
        ttk.Entry(aht_frame, textvariable=self.vars['aht_seconds'], width=15).pack(side='left')
        ttk.Label(aht_frame, text="  (Average Handle Time - es: 180 = 3 minuti)",
                 foreground='#666', font=('Arial', 9)).pack(side='left', padx=5)
        row += 1

        # Concurrency (solo per Chat)
        ttk.Label(form, text="Concurrency:").grid(row=row, column=0, sticky='w', pady=5)
        concurr_frame = ttk.Frame(form)
        concurr_frame.grid(row=row, column=1, sticky='w', pady=5)
        self.vars['concurrency'] = tk.IntVar(value=1)
        self.concurrency_entry = ttk.Entry(concurr_frame, textvariable=self.vars['concurrency'], width=15)
        self.concurrency_entry.pack(side='left')
        self.concurrency_label = ttk.Label(concurr_frame,
                                           text="  (Chat simultanee per agente - es: 3)",
                                           foreground='#666', font=('Arial', 9))
        self.concurrency_label.pack(side='left', padx=5)
        row += 1

        # Shrinkage
        ttk.Label(form, text="Shrinkage (%):*").grid(row=row, column=0, sticky='w', pady=5)
        shr_frame = ttk.Frame(form)
        shr_frame.grid(row=row, column=1, sticky='w', pady=5)
        self.vars['shrinkage'] = tk.DoubleVar(value=30.0)
        ttk.Entry(shr_frame, textvariable=self.vars['shrinkage'], width=15).pack(side='left')
        ttk.Label(shr_frame, text="  (Tempo non produttivo - es: 30%)",
                 foreground='#666', font=('Arial', 9)).pack(side='left', padx=5)
        row += 1

        # Produttivita
        ttk.Label(form, text="Produttività (%):*").grid(row=row, column=0, sticky='w', pady=5)
        prod_frame = ttk.Frame(form)
        prod_frame.grid(row=row, column=1, sticky='w', pady=5)
        self.vars['produttivita'] = tk.DoubleVar(value=100.0)
        ttk.Entry(prod_frame, textvariable=self.vars['produttivita'], width=15).pack(side='left')
        ttk.Label(prod_frame, text="  (Produttività target per skill - es: 100%)",
                 foreground='#666', font=('Arial', 9)).pack(side='left', padx=5)
        row += 1

        # Occupancy
        ttk.Label(form, text="Occupancy Target (%):").grid(row=row, column=0, sticky='w', pady=5)
        occ_frame = ttk.Frame(form)
        occ_frame.grid(row=row, column=1, sticky='w', pady=5)
        self.vars['occupancy_target'] = tk.DoubleVar(value=85.0)
        ttk.Entry(occ_frame, textvariable=self.vars['occupancy_target'], width=15).pack(side='left')
        ttk.Label(occ_frame, text="  (Target occupancy agenti - es: 85%)",
                 foreground='#666', font=('Arial', 9)).pack(side='left', padx=5)
        row += 1

        # === SEZIONE SERVICE LEVEL (Voice/Email) ===
        ttk.Label(form, text="📈 Service Level (per Voice/Email)",
                 font=('Arial', 11, 'bold')).grid(row=row, column=0, columnspan=2, sticky='w', pady=(15, 5))
        row += 1

        # SL Target
        ttk.Label(form, text="Service Level Target (%):").grid(row=row, column=0, sticky='w', pady=5)
        sl_frame = ttk.Frame(form)
        sl_frame.grid(row=row, column=1, sticky='w', pady=5)
        self.vars['service_level_target'] = tk.DoubleVar(value=80.0)
        self.sl_target_entry = ttk.Entry(sl_frame, textvariable=self.vars['service_level_target'], width=15)
        self.sl_target_entry.pack(side='left')
        self.sl_target_label = ttk.Label(sl_frame, text="  (% chiamate entro target - es: 80%)",
                                        foreground='#666', font=('Arial', 9))
        self.sl_target_label.pack(side='left', padx=5)
        row += 1

        # SL Seconds
        ttk.Label(form, text="Service Level Seconds:").grid(row=row, column=0, sticky='w', pady=5)
        sls_frame = ttk.Frame(form)
        sls_frame.grid(row=row, column=1, sticky='w', pady=5)
        self.vars['service_level_seconds'] = tk.IntVar(value=20)
        self.sl_seconds_entry = ttk.Entry(sls_frame, textvariable=self.vars['service_level_seconds'], width=15)
        self.sl_seconds_entry.pack(side='left')
        self.sl_seconds_label = ttk.Label(sls_frame, text="  (Secondi target risposta - es: 20)",
                                         foreground='#666', font=('Arial', 9))
        self.sl_seconds_label.pack(side='left', padx=5)
        row += 1

        # === SEZIONE ASA (Chat) ===
        ttk.Label(form, text="💬 ASA - Average Speed to Answer (per Chat)",
                 font=('Arial', 11, 'bold')).grid(row=row, column=0, columnspan=2, sticky='w', pady=(15, 5))
        row += 1

        # ASA Target
        ttk.Label(form, text="ASA Target (secondi):").grid(row=row, column=0, sticky='w', pady=5)
        asa_frame = ttk.Frame(form)
        asa_frame.grid(row=row, column=1, sticky='w', pady=5)
        self.vars['asa_target_seconds'] = tk.IntVar(value=60)
        self.asa_entry = ttk.Entry(asa_frame, textvariable=self.vars['asa_target_seconds'], width=15)
        self.asa_entry.pack(side='left')
        self.asa_label = ttk.Label(asa_frame,
                                   text="  (Tempo medio prima risposta - es: 60s)",
                                   foreground='#666', font=('Arial', 9))
        self.asa_label.pack(side='left', padx=5)
        row += 1

        # === ALTRE IMPOSTAZIONI ===
        ttk.Label(form, text="🔧 Altre Impostazioni",
                 font=('Arial', 11, 'bold')).grid(row=row, column=0, columnspan=2, sticky='w', pady=(15, 5))
        row += 1

        # Interval
        ttk.Label(form, text="Intervallo calcolo (min):").grid(row=row, column=0, sticky='w', pady=5)
        int_frame = ttk.Frame(form)
        int_frame.grid(row=row, column=1, sticky='w', pady=5)
        self.vars['interval_minutes'] = tk.IntVar(value=30)
        ttk.Entry(int_frame, textvariable=self.vars['interval_minutes'], width=15).pack(side='left')
        ttk.Label(int_frame, text="  (Tipicamente 30 minuti)",
                 foreground='#666', font=('Arial', 9)).pack(side='left', padx=5)
        row += 1

        # Note
        ttk.Label(form, text="Note:").grid(row=row, column=0, sticky='nw', pady=5)
        self.vars['note'] = tk.StringVar()
        note_entry = ttk.Entry(form, textvariable=self.vars['note'], width=40)
        note_entry.grid(row=row, column=1, sticky='w', pady=5)
        row += 1

        # === INFO BOX ===
        info_frame = ttk.LabelFrame(form, text="ℹ️ Guida Rapida", padding=10)
        info_frame.grid(row=row, column=0, columnspan=2, sticky='ew', pady=20)

        info_text = (
            "VOICE: AHT tipico 180-300s, SL 80% in 20s, Concurrency = 1\n"
            "CHAT: AHT tipico 120-240s, ASA target 60s, Concurrency 2-4 (chat simultanee)\n"
            "EMAIL: AHT tipico 300-600s, SL 75% in 4h, Concurrency = 1\n\n"
            "Shrinkage tipico: 25-35% (include pause, formazione, riunioni)\n"
            "Occupancy tipico: 80-90% (tempo effettivo in attività produttiva)"
        )
        ttk.Label(info_frame, text=info_text, justify='left',
                 font=('Arial', 9), foreground='#555').pack()
        row += 1

        # === PULSANTI ===
        button_frame = ttk.Frame(form)
        button_frame.grid(row=row, column=0, columnspan=2, pady=20)

        ttk.Button(button_frame, text="💾 Salva", command=self.save,
                  width=20).pack(side='left', padx=10)
        ttk.Button(button_frame, text="❌ Annulla", command=self.destroy,
                  width=20).pack(side='left', padx=10)

        # Configura stato iniziale campi
        self.on_canale_change()

    def on_canale_change(self):
        """Gestisce cambio tipo canale"""
        canale = self.vars['tipo_canale'].get()

        if canale == 'Voice':
            # Voice: concurrency = 1, usa SL, nascondi ASA
            self.vars['concurrency'].set(1)
            self.concurrency_entry.config(state='disabled')
            self.concurrency_label.config(foreground='#CCC')

            self.sl_target_entry.config(state='normal')
            self.sl_seconds_entry.config(state='normal')
            self.sl_target_label.config(foreground='#666')
            self.sl_seconds_label.config(foreground='#666')

            self.asa_entry.config(state='disabled')
            self.asa_label.config(foreground='#CCC')

        elif canale == 'Chat':
            # Chat: concurrency > 1, usa ASA, nascondi SL tradizionale
            if self.vars['concurrency'].get() == 1:
                self.vars['concurrency'].set(3)  # Default per chat
            self.concurrency_entry.config(state='normal')
            self.concurrency_label.config(foreground='#666')

            self.sl_target_entry.config(state='disabled')
            self.sl_seconds_entry.config(state='disabled')
            self.sl_target_label.config(foreground='#CCC')
            self.sl_seconds_label.config(foreground='#CCC')

            self.asa_entry.config(state='normal')
            self.asa_label.config(foreground='#666')

        else:  # Email
            # Email: concurrency = 1, usa SL con tempi lunghi
            self.vars['concurrency'].set(1)
            self.concurrency_entry.config(state='disabled')
            self.concurrency_label.config(foreground='#CCC')

            self.sl_target_entry.config(state='normal')
            self.sl_seconds_entry.config(state='normal')
            self.sl_target_label.config(foreground='#666')
            self.sl_seconds_label.config(foreground='#666')

            self.asa_entry.config(state='disabled')
            self.asa_label.config(foreground='#CCC')

    def _load_skills(self):
        """Carica elenco skills dal database (sia da Skills che da Erlang_Config)"""
        skills_set = set()

        try:
            self.db_manager.connect()

            # Prova a caricare dalla tabella Skills
            try:
                result = self.db_manager.execute_query("""
                    SELECT DISTINCT Codice_Skill
                    FROM Skills
                    ORDER BY Codice_Skill
                """)

                if result:
                    skills_from_table = [row[0] for row in result if row[0]]
                    skills_set.update(skills_from_table)
                    print(f"[DEBUG] Caricati {len(skills_from_table)} skills dalla tabella Skills")
                else:
                    print("[DEBUG] Tabella Skills vuota")
            except Exception as e:
                print(f"[DEBUG] Tabella Skills non disponibile: {e}")

            # Carica anche gli skills già configurati in Erlang_Config
            try:
                result = self.db_manager.execute_query("""
                    SELECT DISTINCT Skill
                    FROM Erlang_Config
                    ORDER BY Skill
                """)

                if result:
                    skills_from_erlang = [row[0] for row in result if row[0]]
                    skills_set.update(skills_from_erlang)
                    print(f"[DEBUG] Caricati {len(skills_from_erlang)} skills da Erlang_Config")
            except Exception as e:
                print(f"[DEBUG] Nessuno skill in Erlang_Config: {e}")

            self.db_manager.close()

            # Converti set in lista ordinata
            self.available_skills = sorted(list(skills_set))
            print(f"[DEBUG] Totale skills disponibili: {len(self.available_skills)} - {self.available_skills}")

        except Exception as e:
            self.available_skills = []
            print(f"[ERRORE] Impossibile caricare skills: {e}")
            import traceback
            traceback.print_exc()

    def load_config(self):
        """Carica configurazione esistente"""
        try:
            self.db_manager.connect()

            result = self.db_manager.execute_query("""
                SELECT Skill, Tipo_Canale, AHT_Seconds, Concurrency, Tempo_Pausa_Minuti,
                       Shrinkage, Produttivita, Service_Level_Target, Service_Level_Seconds,
                       ASA_Target_Seconds, Occupancy_Target, Interval_Minutes, Note
                FROM Erlang_Config
                WHERE ID = ?
            """, (self.config_id,))

            if result and len(result) > 0:
                cfg = result[0]
                self.vars['skill'].set(cfg[0] or '')
                self.vars['tipo_canale'].set(cfg[1] or 'Voice')
                self.vars['aht_seconds'].set(cfg[2] or 180)
                self.vars['concurrency'].set(cfg[3] or 1)
                self.vars['shrinkage'].set((cfg[5] * 100) if cfg[5] else 30.0)
                self.vars['produttivita'].set((cfg[6] * 100) if cfg[6] else 100.0)
                self.vars['service_level_target'].set((cfg[7] * 100) if cfg[7] else 80.0)
                self.vars['service_level_seconds'].set(cfg[8] or 20)
                self.vars['asa_target_seconds'].set(cfg[9] or 60)
                self.vars['occupancy_target'].set((cfg[10] * 100) if cfg[10] else 85.0)
                self.vars['interval_minutes'].set(cfg[11] or 30)
                self.vars['note'].set(cfg[12] or '')

                self.on_canale_change()

            self.db_manager.close()

        except Exception as e:
            messagebox.showerror("Errore", f"Errore caricamento configurazione:\n{e}")

    def save(self):
        """Salva configurazione nel database"""
        # Validazioni
        skill = self.vars['skill'].get().strip()
        if not skill:
            messagebox.showerror("Errore", "Skill è obbligatorio")
            return

        try:
            aht = self.vars['aht_seconds'].get()
            if aht <= 0:
                messagebox.showerror("Errore", "AHT deve essere maggiore di 0")
                return

            concurrency = self.vars['concurrency'].get()
            if concurrency < 1:
                messagebox.showerror("Errore", "Concurrency deve essere almeno 1")
                return

            shrinkage = self.vars['shrinkage'].get() / 100.0
            if not (0 <= shrinkage < 1):
                messagebox.showerror("Errore", "Shrinkage deve essere tra 0 e 99%")
                return

            produttivita = self.vars['produttivita'].get() / 100.0
            if produttivita <= 0:
                messagebox.showerror("Errore", "Produttività deve essere maggiore di 0")
                return

            sl_target = self.vars['service_level_target'].get() / 100.0
            occ_target = self.vars['occupancy_target'].get() / 100.0

        except tk.TclError:
            messagebox.showerror("Errore", "Valori numerici non validi")
            return

        # Salva nel database
        try:
            self.db_manager.connect()

            if self.mode == 'add':
                # Verifica se skill già esiste
                existing = self.db_manager.execute_query(
                    "SELECT ID FROM Erlang_Config WHERE Skill = ?",
                    (skill,)
                )
                if existing:
                    messagebox.showerror("Errore", f"Configurazione per skill '{skill}' già esistente")
                    self.db_manager.close()
                    return

                # Insert
                query = """
                    INSERT INTO Erlang_Config (
                        Skill, Tipo_Canale, AHT_Seconds, Concurrency, Tempo_Pausa_Minuti,
                        Shrinkage, Produttivita, Service_Level_Target, Service_Level_Seconds,
                        ASA_Target_Seconds, Occupancy_Target, Interval_Minutes, Note
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """
                params = (
                    skill,
                    self.vars['tipo_canale'].get(),
                    self.vars['aht_seconds'].get(),
                    self.vars['concurrency'].get(),
                    0,  # Tempo_Pausa_Minuti
                    shrinkage,
                    produttivita,
                    sl_target,
                    self.vars['service_level_seconds'].get(),
                    self.vars['asa_target_seconds'].get(),
                    occ_target,
                    self.vars['interval_minutes'].get(),
                    self.vars['note'].get() or None
                )
                self.db_manager.execute_update(query, params)
                messagebox.showinfo("Successo", f"Configurazione '{skill}' creata")

            else:  # mode == 'edit'
                # Update
                query = """
                    UPDATE Erlang_Config
                    SET Tipo_Canale = ?, AHT_Seconds = ?, Concurrency = ?,
                        Shrinkage = ?, Produttivita = ?, Service_Level_Target = ?, Service_Level_Seconds = ?,
                        ASA_Target_Seconds = ?, Occupancy_Target = ?, Interval_Minutes = ?, Note = ?
                    WHERE ID = ?
                """
                params = (
                    self.vars['tipo_canale'].get(),
                    self.vars['aht_seconds'].get(),
                    self.vars['concurrency'].get(),
                    shrinkage,
                    produttivita,
                    sl_target,
                    self.vars['service_level_seconds'].get(),
                    self.vars['asa_target_seconds'].get(),
                    occ_target,
                    self.vars['interval_minutes'].get(),
                    self.vars['note'].get() or None,
                    self.config_id
                )
                self.db_manager.execute_update(query, params)
                messagebox.showinfo("Successo", f"Configurazione '{skill}' aggiornata")

            self.db_manager.close()
            self.destroy()

        except Exception as e:
            messagebox.showerror("Errore", f"Errore salvataggio:\n{e}")
            import traceback
            traceback.print_exc()
