"""
Tab per generazione templates Excel
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
import os


class TemplatesTab(ttk.Frame):
    """Tab per scaricare templates Excel"""

    def __init__(self, parent, db_manager):
        super().__init__(parent)
        self.db_manager = db_manager
        self.setup_ui()

    def setup_ui(self):
        """Crea l'interfaccia del tab"""

        # Titolo
        title_frame = ttk.Frame(self)
        title_frame.pack(fill='x', padx=20, pady=20)

        ttk.Label(title_frame, text="📥 Generazione Templates Excel",
                 font=('Arial', 16, 'bold')).pack(anchor='w')
        ttk.Label(title_frame, text="Scarica i template Excel per importare dati nel sistema",
                 font=('Arial', 10), foreground='#666').pack(anchor='w', pady=(5, 0))

        # Container principale con scroll
        main_container = ttk.Frame(self)
        main_container.pack(fill='both', expand=True, padx=20, pady=10)

        # === SEZIONE IMPORT COMPLETO ===
        complete_frame = ttk.LabelFrame(main_container, text="📦 Template Completo", padding=15)
        complete_frame.pack(fill='x', pady=(0, 15))

        ttk.Label(complete_frame, text="Template con tutti gli sheet (Skills, Turni, Giustificativi, Operatori)",
                 font=('Arial', 9), foreground='#666').pack(anchor='w', pady=(0, 10))

        btn_frame = ttk.Frame(complete_frame)
        btn_frame.pack(fill='x')

        ttk.Button(btn_frame, text="📄 Genera Template Completo",
                  command=self.genera_template_completo,
                  width=30).pack(side='left', padx=5)

        ttk.Label(btn_frame, text="Include: Skills, Turni, Giustificativi, Operatori",
                 font=('Arial', 8), foreground='#888').pack(side='left', padx=10)

        # === SEZIONE TEMPLATES SINGOLI ===
        singles_frame = ttk.LabelFrame(main_container, text="📑 Templates Singoli", padding=15)
        singles_frame.pack(fill='both', expand=True)

        # Grid per templates singoli
        templates = [
            {
                'name': 'Skills',
                'icon': '🎯',
                'description': 'Configurazione skill/code del contact center',
                'command': self.genera_template_skills,
                'columns': 'Codice_Skill, Descrizione, Canale, Priorita'
            },
            {
                'name': 'Turni',
                'icon': '🕐',
                'description': 'Turni e orari di lavoro degli operatori',
                'command': self.genera_template_turni,
                'columns': 'Data, ID_SAP, Ora_Inizio, Ora_Fine, Skill, Pausa_Inizio, Pausa_Fine'
            },
            {
                'name': 'Giustificativi',
                'icon': '📋',
                'description': 'Codici assenze e giustificativi',
                'command': self.genera_template_giustificativi,
                'columns': 'Codice_Giustificativo, Descrizione, Tipologia, Note'
            },
            {
                'name': 'Operatori',
                'icon': '👥',
                'description': 'Anagrafica operatori del contact center',
                'command': self.genera_template_operatori,
                'columns': 'ID_SAP, Nome, Cognome, Skill_Primario, Data_Assunzione'
            },
            {
                'name': 'Forecast',
                'icon': '📊',
                'description': 'Previsioni volumi per fasce orarie',
                'command': self.genera_template_forecast,
                'columns': 'Data_Riferimento, Fascia_Oraria, Skill, Volumi_Attesi'
            },
            {
                'name': 'Erlang Config',
                'icon': '⚙️',
                'description': 'Configurazione parametri Erlang C per skill',
                'command': self.genera_template_erlang,
                'columns': 'Skill, AHT_Seconds, Shrinkage, Service_Level_Target, Occupancy'
            }
        ]

        for i, template in enumerate(templates):
            row = i // 2
            col = i % 2

            card = ttk.Frame(singles_frame, relief='solid', borderwidth=1)
            card.grid(row=row, column=col, padx=10, pady=10, sticky='nsew')

            # Header della card
            header = ttk.Frame(card)
            header.pack(fill='x', padx=15, pady=(15, 5))

            ttk.Label(header, text=f"{template['icon']} {template['name']}",
                     font=('Arial', 11, 'bold')).pack(anchor='w')

            # Descrizione
            ttk.Label(card, text=template['description'],
                     font=('Arial', 9), foreground='#666',
                     wraplength=300).pack(anchor='w', padx=15, pady=(0, 5))

            # Colonne
            ttk.Label(card, text=f"Colonne: {template['columns']}",
                     font=('Arial', 8), foreground='#888',
                     wraplength=300).pack(anchor='w', padx=15, pady=(0, 10))

            # Pulsante
            ttk.Button(card, text="📥 Scarica Template",
                      command=template['command'],
                      width=25).pack(padx=15, pady=(0, 15))

        # Configura grid weights
        singles_frame.columnconfigure(0, weight=1)
        singles_frame.columnconfigure(1, weight=1)

        # === INFO PANEL ===
        info_frame = ttk.LabelFrame(main_container, text="ℹ️ Informazioni", padding=10)
        info_frame.pack(fill='x', pady=(15, 0))

        info_text = (
            "I templates sono file Excel precompilati con:\n"
            "  • Colonne corrette già formattate\n"
            "  • Dati di esempio per guidare la compilazione\n"
            "  • Istruzioni dettagliate per ogni campo\n\n"
            "Dopo aver scaricato e compilato i template, usa il tab 'Import Excel' per caricare i dati."
        )

        ttk.Label(info_frame, text=info_text, font=('Arial', 9),
                 foreground='#555', justify='left').pack(anchor='w')

    def _choose_save_location(self, default_filename):
        """
        Apre dialog per scegliere dove salvare il file

        Args:
            default_filename: Nome file di default

        Returns:
            Path completo scelto dall'utente o None se annullato
        """
        filepath = filedialog.asksaveasfilename(
            defaultextension='.xlsx',
            filetypes=[('Excel files', '*.xlsx'), ('All files', '*.*')],
            initialfile=default_filename,
            title='Salva Template Excel'
        )

        return filepath if filepath else None

    def genera_template_completo(self):
        """Genera template completo con tutti gli sheet"""
        filepath = self._choose_save_location('template_completo.xlsx')
        if not filepath:
            return

        try:
            from scripts.crea_template_completo import crea_template_completo
            crea_template_completo(filepath)

            messagebox.showinfo(
                "Successo",
                f"✅ Template completo generato con successo!\n\n"
                f"Percorso: {filepath}\n\n"
                f"Il template include tutti gli sheet necessari:\n"
                f"  • Skills\n"
                f"  • Turni\n"
                f"  • Giustificativi (Giust)\n"
                f"  • Operatori\n\n"
                f"Compila i dati e usa 'Import Excel > Import Completo' per caricarli."
            )

        except Exception as e:
            messagebox.showerror("Errore", f"Errore generazione template:\n{e}")
            import traceback
            traceback.print_exc()

    def genera_template_skills(self):
        """Genera template per skills"""
        filepath = self._choose_save_location('template_skills.xlsx')
        if not filepath:
            return

        try:
            import pandas as pd

            # Dati di esempio
            data = [
                {'Codice_Skill': 'CUSTOMER_CARE', 'Descrizione': 'Customer Care Generale',
                 'Canale': 'Voice', 'Priorita': 1, 'Note': ''},
                {'Codice_Skill': 'TECHNICAL_SUPPORT', 'Descrizione': 'Supporto Tecnico',
                 'Canale': 'Voice', 'Priorita': 2, 'Note': ''},
                {'Codice_Skill': 'BACK_OFFICE', 'Descrizione': 'Back Office',
                 'Canale': 'Email', 'Priorita': 3, 'Note': ''},
                {'Codice_Skill': 'SALES', 'Descrizione': 'Vendite',
                 'Canale': 'Voice', 'Priorita': 4, 'Note': ''},
            ]

            df = pd.DataFrame(data)
            df.to_excel(filepath, sheet_name='Skills', index=False)

            messagebox.showinfo("Successo", f"✅ Template Skills generato:\n{filepath}")

        except Exception as e:
            messagebox.showerror("Errore", f"Errore generazione template:\n{e}")

    def genera_template_turni(self):
        """Genera template per turni"""
        filepath = self._choose_save_location('template_turni.xlsx')
        if not filepath:
            return

        try:
            from scripts.crea_template_turni import crea_template_turni
            crea_template_turni(filepath)

            messagebox.showinfo(
                "Successo",
                f"✅ Template Turni generato:\n{filepath}\n\n"
                f"Include dati di esempio per 5 operatori."
            )

        except Exception as e:
            messagebox.showerror("Errore", f"Errore generazione template:\n{e}")

    def genera_template_giustificativi(self):
        """Genera template per giustificativi"""
        filepath = self._choose_save_location('template_giustificativi.xlsx')
        if not filepath:
            return

        try:
            import pandas as pd

            # Dati di esempio
            data = [
                {'Codice_Giustificativo': 'FER', 'Descrizione': 'Ferie',
                 'Tipologia': 'FerieROL', 'Note': 'Ferie ordinarie'},
                {'Codice_Giustificativo': 'ROL', 'Descrizione': 'Riduzione Orario Lavoro',
                 'Tipologia': 'FerieROL', 'Note': 'ROL'},
                {'Codice_Giustificativo': 'MAL', 'Descrizione': 'Malattia',
                 'Tipologia': 'Malattia', 'Note': 'Malattia certificata'},
                {'Codice_Giustificativo': 'PER', 'Descrizione': 'Permesso',
                 'Tipologia': 'Assenze generiche', 'Note': 'Permesso retribuito'},
                {'Codice_Giustificativo': 'ASS', 'Descrizione': 'Assenza ingiustificata',
                 'Tipologia': 'Assenze generiche', 'Note': 'Assenza non autorizzata'},
            ]

            df = pd.DataFrame(data)
            df.to_excel(filepath, sheet_name='Giust', index=False)

            messagebox.showinfo("Successo", f"✅ Template Giustificativi generato:\n{filepath}")

        except Exception as e:
            messagebox.showerror("Errore", f"Errore generazione template:\n{e}")

    def genera_template_operatori(self):
        """Genera template per operatori"""
        filepath = self._choose_save_location('template_operatori.xlsx')
        if not filepath:
            return

        try:
            from scripts.crea_template_operatori import crea_template_operatori
            crea_template_operatori(filepath)

            messagebox.showinfo(
                "Successo",
                f"✅ Template Operatori generato:\n{filepath}\n\n"
                f"Include dati di esempio per 10 operatori."
            )

        except Exception as e:
            messagebox.showerror("Errore", f"Errore generazione template:\n{e}")

    def genera_template_forecast(self):
        """Genera template per forecast"""
        filepath = self._choose_save_location('template_forecast.xlsx')
        if not filepath:
            return

        # Dialog per chiedere la data
        dialog = DateSelectionDialog(self, "Seleziona data per Forecast")
        self.wait_window(dialog)

        if not dialog.selected_date:
            return  # Utente ha annullato

        try:
            from scripts.crea_template_forecast import crea_template_forecast
            crea_template_forecast(filepath, dialog.selected_date)

            messagebox.showinfo(
                "Successo",
                f"✅ Template Forecast generato:\n{filepath}\n\n"
                f"Data: {dialog.selected_date.strftime('%Y-%m-%d')}\n"
                f"Fasce: 48 (ogni 30 minuti)\n"
                f"Skills: 4 di esempio\n\n"
                f"Controlla gli sheet 'Forecast', 'Riepilogo' e 'Istruzioni'."
            )

        except Exception as e:
            messagebox.showerror("Errore", f"Errore generazione template:\n{e}")

    def genera_template_erlang(self):
        """Genera template per configurazione Erlang"""
        filepath = self._choose_save_location('template_erlang_config.xlsx')
        if not filepath:
            return

        try:
            from scripts.crea_template_erlang_config import crea_template_erlang_config
            crea_template_erlang_config(filepath)

            messagebox.showinfo(
                "Successo",
                f"✅ Template Erlang Config generato:\n{filepath}\n\n"
                f"Include configurazioni di esempio per:\n"
                f"  • Voice\n"
                f"  • Chat\n"
                f"  • Email"
            )

        except Exception as e:
            messagebox.showerror("Errore", f"Errore generazione template:\n{e}")


class DateSelectionDialog(tk.Toplevel):
    """Dialog per selezione data"""

    def __init__(self, parent, title="Seleziona Data"):
        super().__init__(parent)
        self.title(title)
        self.geometry("350x200")
        self.resizable(False, False)

        # Centra la finestra
        self.update_idletasks()
        x = (self.winfo_screenwidth() - 350) // 2
        y = (self.winfo_screenheight() - 200) // 2
        self.geometry(f"350x200+{x}+{y}")

        self.selected_date = None

        self.setup_ui()

    def setup_ui(self):
        """Crea interfaccia dialog"""
        frame = ttk.Frame(self, padding=20)
        frame.pack(fill='both', expand=True)

        ttk.Label(frame, text="Seleziona la data di riferimento per il forecast:",
                 font=('Arial', 10)).pack(pady=(0, 20))

        # Data
        date_frame = ttk.Frame(frame)
        date_frame.pack(pady=10)

        ttk.Label(date_frame, text="Data:").pack(side='left', padx=5)

        self.date_var = tk.StringVar(value=datetime.now().strftime('%Y-%m-%d'))
        ttk.Entry(date_frame, textvariable=self.date_var, width=15).pack(side='left', padx=5)

        ttk.Label(date_frame, text="(YYYY-MM-DD)",
                 font=('Arial', 8), foreground='#888').pack(side='left', padx=5)

        # Pulsanti
        button_frame = ttk.Frame(frame)
        button_frame.pack(pady=20)

        ttk.Button(button_frame, text="OK", command=self.confirm,
                  width=12).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Annulla", command=self.cancel,
                  width=12).pack(side='left', padx=5)

    def confirm(self):
        """Conferma selezione"""
        try:
            self.selected_date = datetime.strptime(self.date_var.get(), '%Y-%m-%d').date()
            self.destroy()
        except ValueError:
            messagebox.showerror("Errore", "Formato data non valido.\nUsare: YYYY-MM-DD")

    def cancel(self):
        """Annulla selezione"""
        self.selected_date = None
        self.destroy()
