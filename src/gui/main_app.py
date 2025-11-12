"""
Applicazione principale Matrici - GUI rifatta
"""
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sys
import os
from datetime import datetime, timedelta

# Aggiungi path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from database.db_manager import DatabaseManager
from database.db_creator import DatabaseCreator
from gui.operatore_form import OperatoreForm
from gui.quick_edit_dialog import QuickEditDialog
from gui.cambio_turno_dialog import CambioTurnoDialog
from gui.capability_dashboard import CapabilityDashboard
from gui.riepilogo_screen import RiepilogoScreen
from gui.erlang_config_tab import ErlangConfigTab
from gui.templates_tab import TemplatesTab


class MatriciApp:
    """Applicazione principale Matrici"""

    def __init__(self, root):
        self.root = root
        self.root.title("Matrici - Gestione Turni e Capability Operatori")
        self.root.geometry("1400x850")

        # Database Access
        self.db_path = 'data/operator_overtime.accdb'
        # Fallback a SQLite se Access non disponibile
        if not os.path.exists(self.db_path):
            self.db_path = 'data/operator_overtime.db'

        self.db_manager = DatabaseManager(self.db_path)

        # Verifica database
        self.check_database()

        # Setup stili
        self.setup_styles()

        # Setup GUI
        self.setup_gui()

    def check_database(self):
        """Verifica esistenza database"""
        db_dir = os.path.dirname(self.db_path)
        if not os.path.exists(db_dir):
            os.makedirs(db_dir)

        if not os.path.exists(self.db_path):
            response = messagebox.askyesno(
                "Database non trovato",
                "Il database non esiste. Vuoi crearlo ora?"
            )
            if response:
                self.init_database()
            else:
                messagebox.showwarning("Attenzione",
                                      "L'applicazione potrebbe non funzionare correttamente "
                                      "senza database.\n\nUsa Menu Database → Inizializza Database")

    def init_database(self):
        """Inizializza il database"""
        try:
            creator = DatabaseCreator(self.db_path)
            creator.create_database()
            messagebox.showinfo("Successo",
                               f"Database creato con successo:\n{self.db_path}\n\n"
                               "Ora puoi inserire operatori e forecast.")
        except Exception as e:
            messagebox.showerror("Errore", f"Errore nella creazione database:\n{e}")

    def setup_styles(self):
        """Configura stili ttk"""
        style = ttk.Style()

        # Tema
        try:
            style.theme_use('clam')  # Tema moderno
        except:
            pass

        # Stile bottoni
        style.configure('Accent.TButton', font=('Arial', 10, 'bold'))

        # Stile labels
        style.configure('Title.TLabel', font=('Arial', 14, 'bold'))
        style.configure('Subtitle.TLabel', font=('Arial', 11, 'bold'))

    def setup_gui(self):
        """Crea l'interfaccia principale"""
        # === MENU BAR ===
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # Menu File
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Esporta Report Completo", command=self.export_full_report)
        file_menu.add_separator()
        file_menu.add_command(label="Esci", command=self.root.quit)

        # Menu Database
        db_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Database", menu=db_menu)
        db_menu.add_command(label="Inizializza Database", command=self.init_database)
        db_menu.add_command(label="Importa Dati Test", command=self.import_test_data)
        db_menu.add_command(label="Info Database", command=self.show_db_info)

        # Menu Aiuto
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Aiuto", menu=help_menu)
        help_menu.add_command(label="Guida Rapida", command=self.show_help)
        help_menu.add_command(label="Info Applicazione", command=self.show_about)

        # === HEADER ===
        header_frame = ttk.Frame(self.root, relief='raised', borderwidth=2)
        header_frame.pack(fill='x', padx=5, pady=5)

        title_label = ttk.Label(header_frame,
                               text="MATRICI - Gestione Turni e Capability Operatori",
                               style='Title.TLabel', foreground='#1976D2')
        title_label.pack(side='left', padx=20, pady=10)

        # Clock
        self.clock_label = ttk.Label(header_frame, text="", font=('Arial', 10))
        self.clock_label.pack(side='right', padx=20)
        self.update_clock()

        # Database status
        db_status = "Access" if self.db_path.endswith('.accdb') else "SQLite"
        db_label = ttk.Label(header_frame, text=f"Database: {db_status}",
                            font=('Arial', 9, 'italic'))
        db_label.pack(side='right', padx=20)

        # === STATUS BAR (create BEFORE tabs so refresh_operatori can use it) ===
        status_frame = ttk.Frame(self.root, relief='sunken', borderwidth=1)
        status_frame.pack(fill='x', side='bottom')

        self.status_label = ttk.Label(status_frame, text="Pronto", anchor='w')
        self.status_label.pack(side='left', fill='x', expand=True, padx=5)

        # === NOTEBOOK (TABS) ===
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=5, pady=5)

        # Tab 1: ANAGRAFICA OPERATORI
        self.tab_anagrafica = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_anagrafica, text='📋 Anagrafica Operatori')
        self.setup_anagrafica_tab()

        # Tab 2: CAPABILITY DASHBOARD
        self.tab_capability = CapabilityDashboard(self.notebook, self.db_manager)
        self.notebook.add(self.tab_capability, text='📊 Dashboard Capability')

        # Tab 3: RIEPILOGO
        self.tab_riepilogo = RiepilogoScreen(self.notebook, self.db_manager)
        self.notebook.add(self.tab_riepilogo, text='📈 Riepilogo')

        # Tab 4: FORECAST (semplificato per ora)
        self.tab_forecast = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_forecast, text='🎯 Forecast')
        self.setup_forecast_tab()

        # Tab 5: ERLANG CONFIG
        self.tab_erlang = ErlangConfigTab(self.notebook, self.db_manager)
        self.notebook.add(self.tab_erlang, text='⚙️ Erlang Config')

        # Tab 6: TEMPLATES
        self.tab_templates = TemplatesTab(self.notebook, self.db_manager)
        self.notebook.add(self.tab_templates, text='📥 Templates')

    def setup_anagrafica_tab(self):
        """Setup tab anagrafica operatori"""
        # Toolbar
        toolbar = ttk.Frame(self.tab_anagrafica)
        toolbar.pack(fill='x', padx=10, pady=10)

        ttk.Button(toolbar, text="➕ Nuovo Operatore", command=self.nuovo_operatore,
                  width=20, style='Accent.TButton').pack(side='left', padx=5)
        ttk.Button(toolbar, text="⚡ Modifiche Rapide", command=self.modifiche_rapide,
                  width=20, style='Accent.TButton').pack(side='left', padx=5)
        ttk.Button(toolbar, text="🔄 Cambio Turno", command=self.cambio_turno,
                  width=18, style='Accent.TButton').pack(side='left', padx=5)
        ttk.Button(toolbar, text="📊 Importa Excel", command=self.importa_excel,
                  width=18, style='Accent.TButton').pack(side='left', padx=5)
        ttk.Button(toolbar, text="✏️ Modifica", command=self.modifica_operatore,
                  width=15).pack(side='left', padx=5)
        ttk.Button(toolbar, text="🗑️ Elimina", command=self.elimina_operatore,
                  width=15).pack(side='left', padx=5)
        ttk.Button(toolbar, text="🔄 Aggiorna Lista", command=self.refresh_operatori,
                  width=15).pack(side='left', padx=5)
        ttk.Button(toolbar, text="⏱️ Calcola Pause Automatiche", command=self.calcola_pause_massivo,
                  width=25, style='Accent.TButton').pack(side='left', padx=5)

        # Filtri
        filter_frame = ttk.LabelFrame(self.tab_anagrafica, text="Filtri", padding=10)
        filter_frame.pack(fill='x', padx=10, pady=5)

        ttk.Label(filter_frame, text="Data:").pack(side='left', padx=5)
        self.filter_date_var = tk.StringVar(value=datetime.now().strftime('%d/%m/%Y'))
        from tkcalendar import DateEntry
        self.filter_date_entry = DateEntry(filter_frame, textvariable=self.filter_date_var,
                                           width=12, date_pattern='dd/mm/yyyy')
        self.filter_date_entry.pack(side='left', padx=5)

        # Checkbox "Tutte le date" - DEFAULT TRUE per mostrare tutti i record
        self.filter_all_dates_var = tk.BooleanVar(value=True)
        all_dates_check = ttk.Checkbutton(filter_frame, text="Tutte le date",
                                          variable=self.filter_all_dates_var,
                                          command=self.toggle_date_filter)
        all_dates_check.pack(side='left', padx=5)

        # Disabilita DateEntry di default (perché "Tutte le date" è True)
        self.filter_date_entry.config(state='disabled')

        ttk.Label(filter_frame, text="Skill:").pack(side='left', padx=(20, 5))
        self.filter_skill_var = tk.StringVar(value='Tutte')
        self.filter_skill_combo = ttk.Combobox(filter_frame, textvariable=self.filter_skill_var,
                    values=['Tutte'], width=20, state='readonly')
        self.filter_skill_combo.pack(side='left', padx=5)

        # Filtro ricerca globale
        ttk.Label(filter_frame, text="🔍 Cerca:").pack(side='left', padx=(20, 5))
        self.filter_search_var = tk.StringVar()
        self.filter_search_var.trace('w', lambda *args: self.refresh_operatori())
        search_entry = ttk.Entry(filter_frame, textvariable=self.filter_search_var, width=25)
        search_entry.pack(side='left', padx=5)

        ttk.Button(filter_frame, text="🗑️ Pulisci",
                  command=lambda: self.filter_search_var.set('')).pack(side='left', padx=5)

        ttk.Button(filter_frame, text="Applica Filtri", command=self.refresh_operatori).pack(side='left', padx=10)

        # Tabella operatori
        table_frame = ttk.LabelFrame(self.tab_anagrafica, text="Elenco Operatori", padding=10)
        table_frame.pack(fill='both', expand=True, padx=10, pady=10)

        # Scrollbars
        scroll_y = ttk.Scrollbar(table_frame, orient='vertical')
        scroll_y.pack(side='right', fill='y')

        scroll_x = ttk.Scrollbar(table_frame, orient='horizontal')
        scroll_x.pack(side='bottom', fill='x')

        # Treeview - TUTTE le colonne dettagliate
        columns = ('ID', 'ID_SAP', 'Nome', 'Cognome', 'Contratto', 'FTE',
                   'Turno', 'Turno_Spezzato',
                   'Strao_1', 'Strao_2', 'Strao_3',
                   'Pausa_1', 'Pausa_2', 'Pausa_3', 'Pausa_4', 'Pausa_5',
                   'Giust_1_Tipo', 'Giust_1_Orario',
                   'Giust_2_Tipo', 'Giust_2_Orario',
                   'Giust_3_Tipo', 'Giust_3_Orario',
                   'Giust_4_Tipo', 'Giust_4_Orario',
                   'Giust_5_Tipo', 'Giust_5_Orario',
                   'Skill', 'Microskill', 'Postazione', 'Data')

        self.tree_operatori = ttk.Treeview(table_frame, columns=columns, show='headings',
                                           yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)

        scroll_y.config(command=self.tree_operatori.yview)
        scroll_x.config(command=self.tree_operatori.xview)

        # Intestazioni con larghezze
        widths = {
            'ID': 50, 'ID_SAP': 80, 'Nome': 100, 'Cognome': 100,
            'Contratto': 100, 'FTE': 50,
            'Turno': 100, 'Turno_Spezzato': 110,
            'Strao_1': 100, 'Strao_2': 100, 'Strao_3': 100,
            'Pausa_1': 80, 'Pausa_2': 80, 'Pausa_3': 80, 'Pausa_4': 80, 'Pausa_5': 80,
            'Giust_1_Tipo': 80, 'Giust_1_Orario': 100,
            'Giust_2_Tipo': 80, 'Giust_2_Orario': 100,
            'Giust_3_Tipo': 80, 'Giust_3_Orario': 100,
            'Giust_4_Tipo': 80, 'Giust_4_Orario': 100,
            'Giust_5_Tipo': 80, 'Giust_5_Orario': 100,
            'Skill': 120, 'Microskill': 100, 'Postazione': 110, 'Data': 90
        }

        for col in columns:
            self.tree_operatori.heading(col, text=col, command=lambda c=col: self.sort_operatori(c))
            self.tree_operatori.column(col, width=widths.get(col, 100), anchor='center')

        self.tree_operatori.pack(fill='both', expand=True)

        # Bind double-click
        self.tree_operatori.bind('<Double-1>', lambda e: self.modifica_operatore())

        # Carica skill e dati
        self.load_skills_anagrafica()
        self.refresh_operatori()

    def load_skills_anagrafica(self):
        """Carica lista skill nel filtro dell'anagrafica operatori"""
        try:
            self.db_manager.connect()

            # Carica skill dalla tabella Skills
            skills_data = self.db_manager.execute_query("SELECT Codice_Skill FROM Skills ORDER BY Codice_Skill")

            if skills_data and len(skills_data) > 0:
                skills = ['Tutte'] + [row[0] for row in skills_data]
                self.filter_skill_combo['values'] = skills
            else:
                # Fallback: Se Skills è vuota, carica dagli operatori
                operatori_skills = self.db_manager.execute_query("""
                    SELECT DISTINCT Etichetta_Skill
                    FROM Anagrafica_Operatori
                    WHERE Etichetta_Skill IS NOT NULL
                    AND TRIM(Etichetta_Skill) != ''
                    ORDER BY Etichetta_Skill
                """)

                if operatori_skills and len(operatori_skills) > 0:
                    skills = ['Tutte'] + [row[0].strip() for row in operatori_skills]
                    self.filter_skill_combo['values'] = skills
                else:
                    # Nessuno skill trovato
                    self.filter_skill_combo['values'] = ['Tutte']

            self.db_manager.close()
        except Exception as e:
            # In caso di errore, lascia solo "Tutte"
            self.filter_skill_combo['values'] = ['Tutte']
            print(f"[ERROR] Errore caricamento skill: {e}")

    def setup_forecast_tab(self):
        """Setup tab forecast"""
        frame = ttk.Frame(self.tab_forecast)
        frame.pack(fill='both', expand=True, padx=20, pady=20)

        ttk.Label(frame, text="Gestione Forecast",
                 style='Title.TLabel').pack(pady=20)

        ttk.Label(frame, text="Importa forecast da file Excel con volumi attesi e FTE richiesti",
                 font=('Arial', 10)).pack(pady=10)

        ttk.Button(frame, text="📂 Importa Forecast da Excel",
                  command=self.import_forecast, width=30).pack(pady=10)

        ttk.Button(frame, text="📝 Inserimento Manuale Forecast",
                  command=self.manual_forecast, width=30).pack(pady=5)

        ttk.Label(frame, text="\nFormato file Excel richiesto:\nVedi documentazione (docs/TEMPLATE_FORECAST.md)",
                 font=('Arial', 9, 'italic'), foreground='gray').pack(pady=20)

    # === METODI ANAGRAFICA ===

    def nuovo_operatore(self):
        """Apre form per nuovo operatore"""
        form = OperatoreForm(self.root, self.db_manager)
        form.transient(self.root)
        form.grab_set()
        self.root.wait_window(form)
        self.refresh_operatori()

    def modifica_operatore(self):
        """Modifica operatore selezionato"""
        selection = self.tree_operatori.selection()
        if not selection:
            messagebox.showwarning("Attenzione", "Seleziona un operatore da modificare")
            return

        item = self.tree_operatori.item(selection[0])
        operatore_id = item['values'][0]

        form = OperatoreForm(self.root, self.db_manager, operatore_id=operatore_id)
        form.transient(self.root)
        form.grab_set()
        self.root.wait_window(form)
        self.refresh_operatori()

    def modifiche_rapide(self):
        """Apre dialog modifiche rapide giornaliere"""
        # Prendi operatore selezionato se esiste
        operatore_id = None
        selection = self.tree_operatori.selection()
        if selection:
            item = self.tree_operatori.item(selection[0])
            operatore_id = item['values'][0]

        # Prendi data dai filtri
        data_str = self.filter_date_var.get()
        try:
            data = datetime.strptime(data_str, '%d/%m/%Y')
        except:
            data = datetime.now()

        dialog = QuickEditDialog(self.root, self.db_manager, operatore_id=operatore_id, data=data)
        dialog.transient(self.root)
        dialog.grab_set()
        self.root.wait_window(dialog)
        self.refresh_operatori()

    def cambio_turno(self):
        """Apre dialog per cambio turno tra operatori"""
        dialog = CambioTurnoDialog(self.root, self.db_manager)
        dialog.transient(self.root)
        dialog.grab_set()
        self.root.wait_window(dialog)
        self.refresh_operatori()

    def calcola_pause_massivo(self):
        """Calcola pause automatiche per tutti gli operatori in un intervallo di date"""
        # Crea dialog per selezione intervallo
        dialog = tk.Toplevel(self.root)
        dialog.title("Calcolo Pause Automatico Massivo")
        dialog.geometry("500x250")
        dialog.transient(self.root)
        dialog.grab_set()

        # Centra dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() - 500) // 2
        y = (dialog.winfo_screenheight() - 250) // 2
        dialog.geometry(f"500x250+{x}+{y}")

        # Frame principale
        main_frame = ttk.Frame(dialog, padding=20)
        main_frame.pack(fill='both', expand=True)

        ttk.Label(main_frame, text="Calcolo Pause Automatiche per Intervallo Date",
                 font=('Arial', 12, 'bold')).pack(pady=(0, 20))

        ttk.Label(main_frame, text="Questo calcolerà automaticamente le pause ottimizzate per tutti gli operatori\n"
                 "nell'intervallo di date selezionato.", justify='center').pack(pady=(0, 20))

        # Selezione date
        date_frame = ttk.Frame(main_frame)
        date_frame.pack(pady=10)

        ttk.Label(date_frame, text="Data Inizio:").grid(row=0, column=0, padx=5, pady=5, sticky='e')
        from tkcalendar import DateEntry
        date_start_var = tk.StringVar(value=datetime.now().strftime('%d/%m/%Y'))
        date_start_entry = DateEntry(date_frame, textvariable=date_start_var,
                                     width=12, date_pattern='dd/mm/yyyy')
        date_start_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(date_frame, text="Data Fine:").grid(row=1, column=0, padx=5, pady=5, sticky='e')
        date_end_var = tk.StringVar(value=datetime.now().strftime('%d/%m/%Y'))
        date_end_entry = DateEntry(date_frame, textvariable=date_end_var,
                                   width=12, date_pattern='dd/mm/yyyy')
        date_end_entry.grid(row=1, column=1, padx=5, pady=5)

        # Bottoni
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=20)

        def esegui_calcolo():
            try:
                # Parse date
                data_inizio = datetime.strptime(date_start_var.get(), '%d/%m/%Y')
                data_fine = datetime.strptime(date_end_var.get(), '%d/%m/%Y')

                if data_fine < data_inizio:
                    messagebox.showwarning("Attenzione", "La data fine deve essere >= data inizio")
                    return

                # Chiudi dialog
                dialog.destroy()

                # Mostra progress
                progress_window = tk.Toplevel(self.root)
                progress_window.title("Calcolo in corso...")
                progress_window.geometry("400x150")
                progress_window.transient(self.root)
                progress_window.grab_set()

                ttk.Label(progress_window, text="Calcolo pause automatiche in corso...",
                         font=('Arial', 12, 'bold')).pack(pady=20)
                progress_label = ttk.Label(progress_window, text="Inizializzazione...")
                progress_label.pack(pady=10)

                # Calcola pause
                from utils.pause_scheduler import PauseScheduler
                self.db_manager.connect()

                # Genera lista di tutte le date nell'intervallo
                date_list = []
                current_date = data_inizio
                while current_date <= data_fine:
                    date_list.append(current_date.strftime('%Y-%m-%d'))
                    current_date += timedelta(days=1)

                total_operatori = 0
                total_pause = 0

                # Per ogni data, carica operatori e calcola pause
                for data_str in date_list:
                    progress_label.config(text=f"Elaborazione {data_str}...")
                    progress_window.update()

                    # Carica operatori per questa data
                    operatori = self.db_manager.get_operatori(data_str)

                    if not operatori:
                        continue

                    scheduler = PauseScheduler(self.db_manager)

                    # Per ogni operatore, calcola e aggiorna pause
                    for row in operatori:
                        values = list(row)
                        op_id = values[0]
                        id_sap = values[3] if len(values) > 3 else None
                        skill = values[43] if len(values) > 43 else None
                        ora_inizio = values[8] if len(values) > 8 else None
                        ora_fine = values[9] if len(values) > 9 else None
                        ora_inizio_spezzato = values[10] if len(values) > 10 else None
                        ora_fine_spezzato = values[11] if len(values) > 11 else None

                        if not ora_inizio or not skill:
                            continue  # Salta se mancano dati essenziali

                        # Formatta orari
                        def format_time(value):
                            if not value:
                                return None
                            val_str = str(value)
                            if ' ' in val_str:
                                val_str = val_str.split(' ')[1]
                            return val_str[:5] if len(val_str) >= 5 else val_str

                        def calc_duration_hours(inizio_str, fine_str):
                            """Calcola durata in ore tra due orari HH:MM"""
                            try:
                                from datetime import datetime
                                inizio = datetime.strptime(inizio_str, '%H:%M')
                                fine = datetime.strptime(fine_str, '%H:%M')
                                durata = (fine - inizio).total_seconds() / 3600
                                return max(0, durata)
                            except:
                                return 0

                        ora_inizio_str = format_time(ora_inizio)
                        ora_fine_str = format_time(ora_fine) if ora_fine else "18:00"

                        # Calcola durata turno principale e numero pause necessarie
                        durata_turno = calc_duration_hours(ora_inizio_str, ora_fine_str)
                        num_pause_turno = max(1, round(durata_turno / 2)) if durata_turno > 0 else 0

                        # Calcola pause per turno principale
                        pause_totali = []
                        if num_pause_turno > 0:
                            pause = scheduler.calcola_pause_automatiche(
                                ora_inizio_turno=ora_inizio_str,
                                ora_fine_turno=ora_fine_str,
                                skill=skill,
                                data_riferimento=data_str,
                                id_sap_corrente=id_sap,
                                num_pause=num_pause_turno
                            )
                            if pause:
                                pause_totali.extend(pause)

                        # Gestisci turno spezzato (se presente)
                        if ora_inizio_spezzato and ora_fine_spezzato:
                            ora_inizio_spez_str = format_time(ora_inizio_spezzato)
                            ora_fine_spez_str = format_time(ora_fine_spezzato)

                            if ora_inizio_spez_str and ora_fine_spez_str:
                                durata_spezzato = calc_duration_hours(ora_inizio_spez_str, ora_fine_spez_str)
                                num_pause_spezzato = max(1, round(durata_spezzato / 2)) if durata_spezzato > 0 else 0

                                if num_pause_spezzato > 0:
                                    pause_spezzato = scheduler.calcola_pause_automatiche(
                                        ora_inizio_turno=ora_inizio_spez_str,
                                        ora_fine_turno=ora_fine_spez_str,
                                        skill=skill,
                                        data_riferimento=data_str,
                                        id_sap_corrente=id_sap,
                                        num_pause=num_pause_spezzato
                                    )
                                    if pause_spezzato:
                                        pause_totali.extend(pause_spezzato)

                        if pause_totali and len(pause_totali) > 0:
                            # Riconnetti perché PauseScheduler chiude la connessione dopo ogni chiamata
                            self.db_manager.connect()

                            # Aggiorna record con le pause calcolate (massimo 5 slot)
                            update_data = {}
                            for idx, (inizio, fine) in enumerate(pause_totali[:5], 1):
                                update_data[f'Inizio_Pausa_{idx}'] = inizio
                                update_data[f'Fine_Pausa_{idx}'] = fine

                            self.db_manager.update_operatore(op_id, update_data)
                            total_pause += len(pause_totali[:5])

                        total_operatori += 1


                self.db_manager.close()
                progress_window.destroy()

                # Mostra risultato
                messagebox.showinfo("Completato",
                                   f"Calcolo completato!\n\n"
                                   f"Operatori elaborati: {total_operatori}\n"
                                   f"Pause calcolate: {total_pause}\n"
                                   f"Date elaborate: {len(date_list)}")

                # Aggiorna lista
                self.refresh_operatori()

            except Exception as e:
                messagebox.showerror("Errore", f"Errore durante il calcolo:\n{e}")
                import traceback
                traceback.print_exc()

        ttk.Button(button_frame, text="✓ Calcola", command=esegui_calcolo,
                  style='Accent.TButton', width=15).pack(side='left', padx=5)
        ttk.Button(button_frame, text="✗ Annulla", command=dialog.destroy,
                  width=15).pack(side='left', padx=5)

    def importa_excel(self):
        """Importa operatori da file Excel"""
        from tkinter import filedialog
        import subprocess
        import threading

        # Seleziona file Excel
        file_path = filedialog.askopenfilename(
            title="Seleziona file Excel da importare",
            filetypes=[
                ("File Excel", "*.xlsx *.xls"),
                ("Tutti i file", "*.*")
            ],
            initialdir="."
        )

        if not file_path:
            return

        # Conferma import
        if not messagebox.askyesno(
            "Conferma Import",
            f"Importare operatori da:\n{file_path}\n\n"
            "ATTENZIONE:\n"
            "• Se ID_SAP + Data esistono già, i dati verranno AGGIORNATI\n"
            "• L'operazione potrebbe richiedere alcuni minuti\n\n"
            "Continuare?"
        ):
            return

        # Crea finestra progresso
        progress_window = tk.Toplevel(self.root)
        progress_window.title("Import in corso...")
        progress_window.geometry("500x300")
        progress_window.transient(self.root)
        progress_window.grab_set()

        ttk.Label(progress_window, text="Import Excel in corso...",
                 style='Title.TLabel').pack(pady=10)

        # Text widget per output
        output_text = tk.Text(progress_window, height=15, width=60)
        output_text.pack(padx=10, pady=10, fill='both', expand=True)

        scroll = ttk.Scrollbar(output_text)
        scroll.pack(side='right', fill='y')
        output_text.config(yscrollcommand=scroll.set)
        scroll.config(command=output_text.yview)

        # Bottone chiudi (disabilitato durante import)
        close_btn = ttk.Button(progress_window, text="Chiudi", state='disabled',
                              command=progress_window.destroy)
        close_btn.pack(pady=10)

        def run_import():
            """Esegue import in thread separato"""
            try:
                # Esegui script import
                script_path = os.path.join(os.path.dirname(__file__), '..', '..',
                                          'scripts', 'import_excel_operatori.py')

                # Specifica il foglio "Operatori" per supportare template_import_completo.xlsx
                process = subprocess.Popen(
                    [sys.executable, script_path, '--file', file_path, '--sheet', 'Operatori'],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    bufsize=1
                )

                # Leggi output in tempo reale
                for line in process.stdout:
                    output_text.insert('end', line)
                    output_text.see('end')
                    output_text.update()

                process.wait()

                # Risultato finale
                if process.returncode == 0:
                    output_text.insert('end', "\n[OK] IMPORT COMPLETATO CON SUCCESSO!\n", 'success')
                    output_text.tag_config('success', foreground='green', font=('Arial', 10, 'bold'))
                else:
                    output_text.insert('end', "\n[ERROR] Import completato con errori. Verifica sopra.\n", 'error')
                    output_text.tag_config('error', foreground='red', font=('Arial', 10, 'bold'))

                output_text.see('end')

                # Abilita bottone chiudi
                close_btn.config(state='normal')

                # Refresh lista
                self.refresh_operatori()

            except Exception as e:
                output_text.insert('end', f"\n[ERROR] ERRORE: {str(e)}\n", 'error')
                output_text.tag_config('error', foreground='red', font=('Arial', 10, 'bold'))
                close_btn.config(state='normal')

        # Avvia import in thread
        thread = threading.Thread(target=run_import, daemon=True)
        thread.start()

    def elimina_operatore(self):
        """Elimina operatore selezionato"""
        selection = self.tree_operatori.selection()
        if not selection:
            messagebox.showwarning("Attenzione", "Seleziona un operatore da eliminare")
            return

        item = self.tree_operatori.item(selection[0])
        nome = f"{item['values'][3]} {item['values'][2]}"  # Cognome Nome

        if not messagebox.askyesno("Conferma Eliminazione",
                                   f"Eliminare l'operatore {nome}?\n\nQuesta operazione non può essere annullata."):
            return

        try:
            operatore_id = item['values'][0]
            self.db_manager.connect()
            self.db_manager.delete_operatore(operatore_id)
            self.db_manager.close()

            messagebox.showinfo("Successo", "Operatore eliminato con successo")
            self.refresh_operatori()

        except Exception as e:
            messagebox.showerror("Errore", f"Errore nell'eliminazione:\n{e}")

    def toggle_date_filter(self):
        """Abilita/disabilita il filtro data quando la checkbox 'Tutte le date' viene selezionata"""
        if self.filter_all_dates_var.get():
            # Checkbox selezionata: disabilita il DateEntry
            self.filter_date_entry.config(state='disabled')
        else:
            # Checkbox deselezionata: abilita il DateEntry
            self.filter_date_entry.config(state='normal')
        # Aggiorna la lista
        self.refresh_operatori()

    def refresh_operatori(self):
        """Ricarica lista operatori"""
        try:
            self.db_manager.connect()

            # Filtri
            data_filtro = None

            # Se "Tutte le date" NON è selezionata, applica il filtro data
            if not (hasattr(self, 'filter_all_dates_var') and self.filter_all_dates_var.get()):
                data_filtro_str = self.filter_date_var.get() if hasattr(self, 'filter_date_var') else None
                # Converti data da formato italiano (dd/mm/yyyy) a ISO (yyyy-mm-dd) per database
                if data_filtro_str:
                    try:
                        data_obj = datetime.strptime(data_filtro_str, '%d/%m/%Y')
                        data_filtro = data_obj.strftime('%Y-%m-%d')
                    except:
                        data_filtro = None
            operatori = self.db_manager.get_operatori(data_filtro)

            # Filtro di ricerca globale
            search_text = self.filter_search_var.get().lower().strip() if hasattr(self, 'filter_search_var') else ''

            # Clear
            for item in self.tree_operatori.get_children():
                self.tree_operatori.delete(item)

            # Populate
            count = 0
            for row in operatori:
                if hasattr(row, 'cursor_description'):
                    # Access/pyodbc
                    values = [getattr(row, desc[0]) for desc in row.cursor_description]
                else:
                    # SQLite
                    values = list(row)

                # Helper per formattare orari
                def format_time(value):
                    if not value:
                        return ''
                    val_str = str(value)
                    if ' ' in val_str:
                        val_str = val_str.split(' ')[1]  # Prendi parte time
                    return val_str[:5] if len(val_str) >= 5 else val_str  # HH:MM

                def format_time_range(inizio, fine):
                    if inizio and fine:
                        return f"{format_time(inizio)}-{format_time(fine)}"
                    elif inizio:
                        return format_time(inizio)
                    return ''

                # Estrai TUTTE le colonne dettagliate
                try:
                    # Dati base
                    op_id = values[0]
                    id_sap = values[3] if len(values) > 3 else ''
                    nome = values[1] if len(values) > 1 else ''
                    cognome = values[2] if len(values) > 2 else ''
                    contratto = values[4] if len(values) > 4 and values[4] else ''
                    fte = values[5] if len(values) > 5 and values[5] else ''

                    # Turno ordinario
                    turno = format_time_range(
                        values[8] if len(values) > 8 else None,
                        values[9] if len(values) > 9 else None
                    )

                    # Turno spezzato
                    turno_spezzato = format_time_range(
                        values[10] if len(values) > 10 else None,
                        values[11] if len(values) > 11 else None
                    )

                    # Straordinari (3 slot)
                    strao_1 = format_time_range(
                        values[12] if len(values) > 12 else None,
                        values[13] if len(values) > 13 else None
                    )
                    strao_2 = format_time_range(
                        values[14] if len(values) > 14 else None,
                        values[15] if len(values) > 15 else None
                    )
                    strao_3 = format_time_range(
                        values[16] if len(values) > 16 else None,
                        values[17] if len(values) > 17 else None
                    )

                    # Pause (5 slot)
                    pausa_1 = format_time_range(
                        values[18] if len(values) > 18 else None,
                        values[19] if len(values) > 19 else None
                    )
                    pausa_2 = format_time_range(
                        values[20] if len(values) > 20 else None,
                        values[21] if len(values) > 21 else None
                    )
                    pausa_3 = format_time_range(
                        values[22] if len(values) > 22 else None,
                        values[23] if len(values) > 23 else None
                    )
                    pausa_4 = format_time_range(
                        values[24] if len(values) > 24 else None,
                        values[25] if len(values) > 25 else None
                    )
                    pausa_5 = format_time_range(
                        values[26] if len(values) > 26 else None,
                        values[27] if len(values) > 27 else None
                    )

                    # Giustificativi (5 slot) - Tipo e Orario separati
                    giust_1_tipo = values[28] if len(values) > 28 and values[28] else ''
                    giust_1_orario = format_time_range(
                        values[29] if len(values) > 29 else None,
                        values[30] if len(values) > 30 else None
                    )

                    giust_2_tipo = values[31] if len(values) > 31 and values[31] else ''
                    giust_2_orario = format_time_range(
                        values[32] if len(values) > 32 else None,
                        values[33] if len(values) > 33 else None
                    )

                    giust_3_tipo = values[34] if len(values) > 34 and values[34] else ''
                    giust_3_orario = format_time_range(
                        values[35] if len(values) > 35 else None,
                        values[36] if len(values) > 36 else None
                    )

                    giust_4_tipo = values[37] if len(values) > 37 and values[37] else ''
                    giust_4_orario = format_time_range(
                        values[38] if len(values) > 38 else None,
                        values[39] if len(values) > 39 else None
                    )

                    giust_5_tipo = values[40] if len(values) > 40 and values[40] else ''
                    giust_5_orario = format_time_range(
                        values[41] if len(values) > 41 else None,
                        values[42] if len(values) > 42 else None
                    )

                    # Ordine colonne nel DB: Skill(43), Data(44), Postazione(45), Microskill(46)
                    # Microskill è stato aggiunto alla fine dalla migrazione
                    skill = values[43] if len(values) > 43 and values[43] else ''
                    data = values[44] if len(values) > 44 and values[44] else ''
                    postazione = values[45] if len(values) > 45 and values[45] else 'Non specificata'
                    microskill = values[46] if len(values) > 46 and values[46] else ''

                    # Costruisci riga completa (ordine treeview: Skill, Microskill, Postazione, Data)
                    row_data = (
                        op_id, id_sap, nome, cognome, contratto, fte,
                        turno, turno_spezzato,
                        strao_1, strao_2, strao_3,
                        pausa_1, pausa_2, pausa_3, pausa_4, pausa_5,
                        giust_1_tipo, giust_1_orario,
                        giust_2_tipo, giust_2_orario,
                        giust_3_tipo, giust_3_orario,
                        giust_4_tipo, giust_4_orario,
                        giust_5_tipo, giust_5_orario,
                        skill, microskill, postazione, data
                    )
                except (IndexError, Exception) as e:
                    # Fallback se indici non corrispondono
                    print(f"Errore parsing riga: {e}")
                    continue

                # Applica filtro di ricerca globale su tutte le colonne
                if search_text:
                    # Converti tutti i valori in stringa e cerca in ciascuna colonna
                    row_text = ' '.join(str(v).lower() for v in row_data if v is not None)
                    if search_text not in row_text:
                        continue  # Salta questa riga se non matcha

                self.tree_operatori.insert('', 'end', values=row_data)
                count += 1

            self.db_manager.close()

            # Mostra contatore con info sul filtro
            if search_text:
                self.status_label.config(text=f"Operatori visualizzati: {count} (filtrati da {len(operatori)})")
            else:
                self.status_label.config(text=f"Operatori caricati: {len(operatori)}")

        except Exception as e:
            messagebox.showerror("Errore", f"Errore nel caricamento operatori:\n{e}")
            import traceback
            traceback.print_exc()

    def sort_operatori(self, col):
        """Ordina tabella operatori"""
        # TODO: Implementare
        pass

    # === METODI FORECAST ===

    def import_forecast(self):
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

            # Mostra dialog di attesa
            progress_window = tk.Toplevel(self.root)
            progress_window.title("Import in corso...")
            progress_window.geometry("400x150")
            progress_window.transient(self.root)
            progress_window.grab_set()

            ttk.Label(progress_window, text="Import forecast in corso...",
                     font=('Arial', 12, 'bold')).pack(pady=20)
            ttk.Label(progress_window, text="Attendere prego...").pack(pady=10)
            progress_bar = ttk.Progressbar(progress_window, mode='indeterminate')
            progress_bar.pack(pady=10, padx=40, fill='x')
            progress_bar.start(10)

            progress_window.update()

            # Esegui import
            success = do_import(
                excel_file=file_path,
                db_path=self.db_manager.db_path,
                replace_existing=replace
            )

            # Chiudi dialog attesa
            progress_window.destroy()

            if success:
                messagebox.showinfo(
                    "Successo",
                    "Forecast importati con successo!\n\n"
                    "Aggiorna la dashboard Capability per visualizzarli."
                )
                # Ricarica dashboard se esiste
                if hasattr(self, 'tab_capability') and self.tab_capability:
                    try:
                        self.tab_capability.load_skills()
                    except:
                        pass
            else:
                messagebox.showerror(
                    "Errore",
                    "Errore durante l'import del forecast.\n\n"
                    "Controlla la console per dettagli."
                )

        except Exception as e:
            if 'progress_window' in locals():
                progress_window.destroy()
            messagebox.showerror("Errore", f"Errore import forecast:\n{str(e)}")

    def manual_forecast(self):
        """Inserimento manuale forecast"""
        messagebox.showinfo("In sviluppo", "Funzione inserimento manuale in sviluppo.")

    # === METODI MENU ===

    def export_full_report(self):
        """Esporta report completo"""
        messagebox.showinfo("In sviluppo", "Export report completo in sviluppo")

    def import_test_data(self):
        """Importa dati di test"""
        if messagebox.askyesno("Conferma",
                              "Importare dati di test?\n\n"
                              "Questo creerà 5 operatori di esempio e forecast per oggi."):
            try:
                # Esegui script populate_test_data
                import subprocess
                import sys

                script_path = os.path.join(os.path.dirname(__file__), '..', '..',
                                          'scripts', 'populate_test_data.py')

                result = subprocess.run([sys.executable, script_path],
                                       capture_output=True, text=True)

                if result.returncode == 0:
                    messagebox.showinfo("Successo",
                                       "Dati di test importati con successo!\n\n"
                                       "Ricarica le schermate per visualizzarli.")
                    self.refresh_operatori()
                else:
                    messagebox.showerror("Errore",
                                        f"Errore nell'import:\n{result.stderr}")

            except Exception as e:
                messagebox.showerror("Errore", f"Errore:\n{e}")

    def show_db_info(self):
        """Mostra info database"""
        try:
            self.db_manager.connect()

            # Conta record
            op_count = len(self.db_manager.get_operatori())
            skills_count = len(self.db_manager.get_skills())

            self.db_manager.close()

            info = f"""
Database: {self.db_path}
Tipo: {"Microsoft Access" if self.db_path.endswith('.accdb') else "SQLite"}

Record:
- Operatori: {op_count}
- Skills: {skills_count}
            """

            messagebox.showinfo("Info Database", info.strip())

        except Exception as e:
            messagebox.showerror("Errore", f"Errore lettura database:\n{e}")

    def show_help(self):
        """Mostra aiuto"""
        help_text = """
MATRICI - Guida Rapida

1. ANAGRAFICA OPERATORI
   - Inserisci operatori con turni, straordinari, pause, giustificativi
   - Doppio click per modificare

2. DASHBOARD CAPABILITY
   - Visualizza copertura per fasce 15/30 min
   - Confronto con forecast
   - Indicatori colorati

3. RIEPILOGO
   - Report aggregati giorno/settimana/mese
   - Vista per servizio o persona
   - Export Excel

Per documentazione completa:
Vedi docs/QUICK_START.md
        """

        messagebox.showinfo("Guida Rapida", help_text.strip())

    def show_about(self):
        """Info applicazione"""
        about_text = """
MATRICI
Gestione Turni e Capability Operatori

Versione 1.0

Tool per monitoraggio copertura operatori
con analisi dettagliata turni, straordinari,
pause e confronto con forecast.

© 2024
        """

        messagebox.showinfo("Info Applicazione", about_text.strip())

    def update_clock(self):
        """Aggiorna orologio"""
        now = datetime.now()
        time_str = now.strftime('%d/%m/%Y %H:%M:%S')
        self.clock_label.config(text=time_str)
        self.root.after(1000, self.update_clock)


def main():
    """Entry point"""
    root = tk.Tk()

    # Icona (se disponibile)
    # root.iconbitmap('icon.ico')

    app = MatriciApp(root)
    root.mainloop()


if __name__ == '__main__':
    main()
