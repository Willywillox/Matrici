"""
Applicazione principale Matrici - GUI rifatta
"""
import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os
from datetime import datetime

# Aggiungi path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from database.db_manager import DatabaseManager
from database.db_creator import DatabaseCreator
from gui.operatore_form import OperatoreForm
from gui.quick_edit_dialog import QuickEditDialog
from gui.capability_dashboard import CapabilityDashboard
from gui.riepilogo_screen import RiepilogoScreen


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

    def setup_anagrafica_tab(self):
        """Setup tab anagrafica operatori"""
        # Toolbar
        toolbar = ttk.Frame(self.tab_anagrafica)
        toolbar.pack(fill='x', padx=10, pady=10)

        ttk.Button(toolbar, text="➕ Nuovo Operatore", command=self.nuovo_operatore,
                  width=20, style='Accent.TButton').pack(side='left', padx=5)
        ttk.Button(toolbar, text="⚡ Modifiche Rapide", command=self.modifiche_rapide,
                  width=20, style='Accent.TButton').pack(side='left', padx=5)
        ttk.Button(toolbar, text="📊 Importa Excel", command=self.importa_excel,
                  width=18, style='Accent.TButton').pack(side='left', padx=5)
        ttk.Button(toolbar, text="✏️ Modifica", command=self.modifica_operatore,
                  width=15).pack(side='left', padx=5)
        ttk.Button(toolbar, text="🗑️ Elimina", command=self.elimina_operatore,
                  width=15).pack(side='left', padx=5)
        ttk.Button(toolbar, text="🔄 Aggiorna Lista", command=self.refresh_operatori,
                  width=15).pack(side='left', padx=5)

        # Filtri
        filter_frame = ttk.LabelFrame(self.tab_anagrafica, text="Filtri", padding=10)
        filter_frame.pack(fill='x', padx=10, pady=5)

        ttk.Label(filter_frame, text="Data:").pack(side='left', padx=5)
        self.filter_date_var = tk.StringVar(value=datetime.now().strftime('%Y-%m-%d'))
        from tkcalendar import DateEntry
        self.filter_date_entry = DateEntry(filter_frame, textvariable=self.filter_date_var,
                                           width=12, date_pattern='yyyy-mm-dd')
        self.filter_date_entry.pack(side='left', padx=5)

        ttk.Label(filter_frame, text="Skill:").pack(side='left', padx=(20, 5))
        self.filter_skill_var = tk.StringVar(value='Tutte')
        ttk.Combobox(filter_frame, textvariable=self.filter_skill_var,
                    values=['Tutte'], width=20, state='readonly').pack(side='left', padx=5)

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

        # Treeview
        columns = ('ID', 'ID_SAP', 'Nome', 'Cognome', 'Contratto', 'FTE',
                   'Turno', 'Skill', 'Postazione', 'Data', 'Straordinari', 'Pause', 'Giustificativi')

        self.tree_operatori = ttk.Treeview(table_frame, columns=columns, show='headings',
                                           yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)

        scroll_y.config(command=self.tree_operatori.yview)
        scroll_x.config(command=self.tree_operatori.xview)

        # Intestazioni
        widths = {'ID': 50, 'ID_SAP': 80, 'Nome': 100, 'Cognome': 100, 'Contratto': 100,
                 'FTE': 50, 'Turno': 100, 'Skill': 120, 'Postazione': 110, 'Data': 90,
                 'Straordinari': 80, 'Pause': 60, 'Giustificativi': 100}

        for col in columns:
            self.tree_operatori.heading(col, text=col, command=lambda c=col: self.sort_operatori(c))
            self.tree_operatori.column(col, width=widths.get(col, 100), anchor='center')

        self.tree_operatori.pack(fill='both', expand=True)

        # Bind double-click
        self.tree_operatori.bind('<Double-1>', lambda e: self.modifica_operatore())

        # Carica dati
        self.refresh_operatori()

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
            data = datetime.strptime(data_str, '%Y-%m-%d')
        except:
            data = datetime.now()

        dialog = QuickEditDialog(self.root, self.db_manager, operatore_id=operatore_id, data=data)
        dialog.transient(self.root)
        dialog.grab_set()
        self.root.wait_window(dialog)
        self.refresh_operatori()

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

                process = subprocess.Popen(
                    [sys.executable, script_path, '--file', file_path],
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
                    output_text.insert('end', "\n✓ IMPORT COMPLETATO CON SUCCESSO!\n", 'success')
                    output_text.tag_config('success', foreground='green', font=('Arial', 10, 'bold'))
                else:
                    output_text.insert('end', "\n✗ Import completato con errori. Verifica sopra.\n", 'error')
                    output_text.tag_config('error', foreground='red', font=('Arial', 10, 'bold'))

                output_text.see('end')

                # Abilita bottone chiudi
                close_btn.config(state='normal')

                # Refresh lista
                self.refresh_operatori()

            except Exception as e:
                output_text.insert('end', f"\n✗ ERRORE: {str(e)}\n", 'error')
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

    def refresh_operatori(self):
        """Ricarica lista operatori"""
        try:
            self.db_manager.connect()

            # Filtri
            data_filtro = self.filter_date_var.get() if hasattr(self, 'filter_date_var') else None
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

                # Conta straordinari, pause, giustificativi
                strao_count = sum(1 for i in range(1, 4) if values[11 + (i-1)*2])  # Inizio_Strao_1-3
                pause_count = sum(1 for i in range(1, 6) if values[17 + (i-1)*2])  # Inizio_Pausa_1-5
                giust_count = sum(1 for i in range(1, 6) if values[27 + (i-1)*3])  # Tipo_Giust_1-5

                # Estrai campi principali (indici dipendono dalla struttura tabella)
                try:
                    postazione = values[44] if len(values) > 44 and values[44] else 'Non specificata'

                    row_data = (
                        values[0],  # ID
                        values[3],  # ID_SAP
                        values[1],  # Nome
                        values[2],  # Cognome
                        values[4] if values[4] else '',  # Tipo_Contratto
                        values[5] if values[5] else '',  # FTE
                        values[7] if values[7] else '',  # ID_Turno
                        values[42] if values[42] else '',  # Etichetta_Skill
                        postazione,  # Postazione
                        values[43] if values[43] else '',  # Data_Riferimento
                        strao_count,
                        pause_count,
                        giust_count
                    )
                except IndexError:
                    # Fallback se indici non corrispondono
                    row_data = values[:12] if len(values) >= 12 else values

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
        messagebox.showinfo("In sviluppo", "Funzione import forecast da Excel in sviluppo.\n\n"
                                          "Per ora usa lo script di test per popolare forecast.")

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
