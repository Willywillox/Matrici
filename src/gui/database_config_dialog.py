"""
Dialog per la configurazione e migrazione del database
"""
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.db_config import DatabaseConfig


class DatabaseConfigDialog(tk.Toplevel):
    """Dialog per configurare il database"""

    def __init__(self, parent, db_manager=None):
        super().__init__(parent)
        self.title("Configurazione Database")
        self.geometry("600x450")
        self.resizable(False, False)

        self.db_manager = db_manager
        self.config = DatabaseConfig()
        self.result = None

        # Centra la finestra
        self.transient(parent)
        self.grab_set()

        self.setup_ui()
        self.load_current_config()

    def setup_ui(self):
        """Crea l'interfaccia"""
        # Frame principale
        main_frame = ttk.Frame(self, padding=20)
        main_frame.pack(fill='both', expand=True)

        # === TIPO DATABASE ===
        type_frame = ttk.LabelFrame(main_frame, text="Tipo Database", padding=10)
        type_frame.pack(fill='x', pady=(0, 10))

        self.db_type_var = tk.StringVar(value='sqlite')

        ttk.Radiobutton(type_frame, text="SQLite (locale)",
                       variable=self.db_type_var, value='sqlite',
                       command=self.on_type_change).pack(anchor='w')
        ttk.Radiobutton(type_frame, text="Microsoft Access (rete)",
                       variable=self.db_type_var, value='access',
                       command=self.on_type_change).pack(anchor='w')
        ttk.Radiobutton(type_frame, text="SQL Server",
                       variable=self.db_type_var, value='sqlserver',
                       command=self.on_type_change).pack(anchor='w')

        # === PATH DATABASE ===
        path_frame = ttk.LabelFrame(main_frame, text="Percorso Database", padding=10)
        path_frame.pack(fill='x', pady=(0, 10))

        path_row = ttk.Frame(path_frame)
        path_row.pack(fill='x')

        self.path_var = tk.StringVar()
        self.path_entry = ttk.Entry(path_row, textvariable=self.path_var, width=50)
        self.path_entry.pack(side='left', fill='x', expand=True, padx=(0, 5))

        ttk.Button(path_row, text="Sfoglia...", command=self.browse_path).pack(side='left')

        # === SQL SERVER OPTIONS ===
        self.sqlserver_frame = ttk.LabelFrame(main_frame, text="Opzioni SQL Server", padding=10)
        self.sqlserver_frame.pack(fill='x', pady=(0, 10))

        # Server
        server_row = ttk.Frame(self.sqlserver_frame)
        server_row.pack(fill='x', pady=2)
        ttk.Label(server_row, text="Server:", width=15).pack(side='left')
        self.server_var = tk.StringVar(value='localhost')
        ttk.Entry(server_row, textvariable=self.server_var, width=30).pack(side='left')

        # Database name
        dbname_row = ttk.Frame(self.sqlserver_frame)
        dbname_row.pack(fill='x', pady=2)
        ttk.Label(dbname_row, text="Database:", width=15).pack(side='left')
        self.dbname_var = tk.StringVar(value='Matrici')
        ttk.Entry(dbname_row, textvariable=self.dbname_var, width=30).pack(side='left')

        # Trusted connection
        self.trusted_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(self.sqlserver_frame, text="Usa autenticazione Windows",
                       variable=self.trusted_var).pack(anchor='w', pady=2)

        # Nascondi inizialmente
        self.sqlserver_frame.pack_forget()

        # === INFO DATABASE CORRENTE ===
        info_frame = ttk.LabelFrame(main_frame, text="Database Corrente", padding=10)
        info_frame.pack(fill='x', pady=(0, 10))

        self.info_label = ttk.Label(info_frame, text="", wraplength=550)
        self.info_label.pack(anchor='w')

        # === MIGRAZIONE ===
        migrate_frame = ttk.LabelFrame(main_frame, text="Migrazione Dati", padding=10)
        migrate_frame.pack(fill='x', pady=(0, 10))

        ttk.Label(migrate_frame,
                 text="Copia tutti i dati dal database corrente al nuovo database").pack(anchor='w')

        migrate_btn_row = ttk.Frame(migrate_frame)
        migrate_btn_row.pack(fill='x', pady=(5, 0))

        ttk.Button(migrate_btn_row, text="SQLite -> Access",
                  command=self.migrate_sqlite_to_access).pack(side='left', padx=(0, 5))
        ttk.Button(migrate_btn_row, text="Access -> SQLite",
                  command=self.migrate_access_to_sqlite).pack(side='left')

        # === PULSANTI ===
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill='x', pady=(10, 0))

        ttk.Button(btn_frame, text="Salva", command=self.save_config,
                  width=15).pack(side='right', padx=(5, 0))
        ttk.Button(btn_frame, text="Annulla", command=self.cancel,
                  width=15).pack(side='right')
        ttk.Button(btn_frame, text="Test Connessione", command=self.test_connection,
                  width=15).pack(side='left')

    def load_current_config(self):
        """Carica la configurazione corrente"""
        self.db_type_var.set(self.config.db_type)
        self.path_var.set(self.config.db_path)

        # Carica opzioni SQL Server se presenti
        if self.config.config.has_section('sqlserver'):
            self.server_var.set(self.config.config.get('sqlserver', 'server', fallback='localhost'))
            self.dbname_var.set(self.config.config.get('sqlserver', 'database', fallback='Matrici'))
            trusted = self.config.config.get('sqlserver', 'trusted_connection', fallback='yes')
            self.trusted_var.set(trusted.lower() == 'yes')

        self.on_type_change()
        self.update_info()

    def on_type_change(self):
        """Gestisce cambio tipo database"""
        db_type = self.db_type_var.get()

        if db_type == 'sqlserver':
            self.sqlserver_frame.pack(fill='x', pady=(0, 10), after=self.path_entry.master.master)
        else:
            self.sqlserver_frame.pack_forget()

    def browse_path(self):
        """Apre dialogo per selezionare file database"""
        db_type = self.db_type_var.get()

        if db_type == 'sqlite':
            filetypes = [("SQLite Database", "*.db"), ("Tutti i file", "*.*")]
            default_ext = '.db'
        else:
            filetypes = [("Access Database", "*.accdb;*.mdb"), ("Tutti i file", "*.*")]
            default_ext = '.accdb'

        path = filedialog.askopenfilename(
            title="Seleziona Database",
            filetypes=filetypes,
            defaultextension=default_ext
        )

        if path:
            self.path_var.set(path)

    def update_info(self):
        """Aggiorna informazioni database corrente"""
        if self.db_manager:
            info = self.db_manager.get_db_info()
            text = f"Tipo: {info['type']}\nPath: {info['path']}\nConnesso: {'Si' if info['connected'] else 'No'}"
        else:
            text = f"Tipo: {self.config.db_type}\nPath: {self.config.db_path}"

        self.info_label.config(text=text)

    def test_connection(self):
        """Testa la connessione al database configurato"""
        db_type = self.db_type_var.get()
        path = self.path_var.get()

        try:
            if db_type == 'sqlite':
                import sqlite3
                conn = sqlite3.connect(path)
                conn.execute("SELECT 1")
                conn.close()
                messagebox.showinfo("Test Connessione", "Connessione SQLite riuscita!")

            elif db_type == 'access':
                import pyodbc
                conn_str = f"DRIVER={{Microsoft Access Driver (*.mdb, *.accdb)}};DBQ={os.path.abspath(path)};"
                conn = pyodbc.connect(conn_str)
                conn.execute("SELECT 1")
                conn.close()
                messagebox.showinfo("Test Connessione", "Connessione Access riuscita!")

            elif db_type == 'sqlserver':
                import pyodbc
                server = self.server_var.get()
                database = self.dbname_var.get()
                conn_str = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};"
                if self.trusted_var.get():
                    conn_str += "Trusted_Connection=yes;"
                conn = pyodbc.connect(conn_str)
                conn.execute("SELECT 1")
                conn.close()
                messagebox.showinfo("Test Connessione", "Connessione SQL Server riuscita!")

        except Exception as e:
            messagebox.showerror("Errore Connessione", f"Impossibile connettersi:\n{e}")

    def migrate_sqlite_to_access(self):
        """Avvia migrazione da SQLite ad Access"""
        # Chiedi il file Access di destinazione
        access_path = filedialog.asksaveasfilename(
            title="Seleziona Database Access di destinazione",
            filetypes=[("Access Database", "*.accdb")],
            defaultextension='.accdb'
        )

        if not access_path:
            return

        # Conferma
        if not messagebox.askyesno("Conferma Migrazione",
                                   f"Migrare tutti i dati da:\n{self.config.db_path}\n\na:\n{access_path}\n\nContinuare?"):
            return

        try:
            from scripts.migrate_database import DatabaseMigrator
            migrator = DatabaseMigrator()

            # Esegui migrazione
            success = migrator.migrate_sqlite_to_access(self.config.db_path, access_path)

            if success:
                messagebox.showinfo("Migrazione Completata",
                                   f"Dati migrati con successo!\n\nTabelle: {migrator.stats['tables_migrated']}\nRighe: {migrator.stats['rows_migrated']}")

                # Chiedi se vuole usare il nuovo database
                if messagebox.askyesno("Cambia Database",
                                      "Vuoi usare il nuovo database Access come database principale?"):
                    self.db_type_var.set('access')
                    self.path_var.set(access_path)
            else:
                messagebox.showerror("Errore Migrazione", "La migrazione ha riscontrato errori.")

        except Exception as e:
            messagebox.showerror("Errore", f"Errore durante la migrazione:\n{e}")

    def migrate_access_to_sqlite(self):
        """Avvia migrazione da Access a SQLite"""
        # Chiedi il file Access sorgente
        access_path = filedialog.askopenfilename(
            title="Seleziona Database Access sorgente",
            filetypes=[("Access Database", "*.accdb;*.mdb")]
        )

        if not access_path:
            return

        # Chiedi il file SQLite di destinazione
        sqlite_path = filedialog.asksaveasfilename(
            title="Seleziona Database SQLite di destinazione",
            filetypes=[("SQLite Database", "*.db")],
            defaultextension='.db'
        )

        if not sqlite_path:
            return

        # Conferma
        if not messagebox.askyesno("Conferma Migrazione",
                                   f"Migrare tutti i dati da:\n{access_path}\n\na:\n{sqlite_path}\n\nContinuare?"):
            return

        try:
            from scripts.migrate_database import DatabaseMigrator
            migrator = DatabaseMigrator()

            # Esegui migrazione
            success = migrator.migrate_access_to_sqlite(access_path, sqlite_path)

            if success:
                messagebox.showinfo("Migrazione Completata",
                                   f"Dati migrati con successo!\n\nTabelle: {migrator.stats['tables_migrated']}\nRighe: {migrator.stats['rows_migrated']}")

                # Chiedi se vuole usare il nuovo database
                if messagebox.askyesno("Cambia Database",
                                      "Vuoi usare il nuovo database SQLite come database principale?"):
                    self.db_type_var.set('sqlite')
                    self.path_var.set(sqlite_path)
            else:
                messagebox.showerror("Errore Migrazione", "La migrazione ha riscontrato errori.")

        except Exception as e:
            messagebox.showerror("Errore", f"Errore durante la migrazione:\n{e}")

    def save_config(self):
        """Salva la configurazione"""
        db_type = self.db_type_var.get()
        path = self.path_var.get()

        if not path:
            messagebox.showerror("Errore", "Specificare il percorso del database")
            return

        try:
            if db_type == 'sqlite':
                self.config.set_sqlite(path)
            elif db_type == 'access':
                self.config.set_access(path)
            elif db_type == 'sqlserver':
                self.config.set_sqlserver(
                    self.server_var.get(),
                    self.dbname_var.get(),
                    self.trusted_var.get()
                )

            self.result = {
                'type': db_type,
                'path': path
            }

            messagebox.showinfo("Salvato",
                              "Configurazione salvata!\n\nRiavviare l'applicazione per applicare le modifiche.")
            self.destroy()

        except Exception as e:
            messagebox.showerror("Errore", f"Errore salvataggio configurazione:\n{e}")

    def cancel(self):
        """Annulla e chiude"""
        self.result = None
        self.destroy()


if __name__ == '__main__':
    # Test dialog
    root = tk.Tk()
    root.withdraw()

    dialog = DatabaseConfigDialog(root)
    root.wait_window(dialog)

    if dialog.result:
        print(f"Configurazione salvata: {dialog.result}")
    else:
        print("Annullato")

    root.destroy()
