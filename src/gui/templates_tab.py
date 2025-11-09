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

        # Container con scrollbar
        canvas_container = ttk.Frame(self)
        canvas_container.pack(fill='both', expand=True, padx=5, pady=5)

        # Canvas e scrollbar
        canvas = tk.Canvas(canvas_container, highlightthickness=0)
        scrollbar = ttk.Scrollbar(canvas_container, orient="vertical", command=canvas.yview)

        # Frame scrollabile
        main_container = ttk.Frame(canvas)

        # Configura scrolling
        main_container.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=main_container, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Pack canvas e scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Bind mousewheel per scrolling
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)

        # === SEZIONE IMPORT COMPLETO ===
        complete_frame = ttk.LabelFrame(main_container, text="📦 Template Completo", padding=15)
        complete_frame.pack(fill='x', pady=(0, 15), padx=15)

        ttk.Label(complete_frame, text="Template con tutti gli sheet (Skills, Turni, Giustificativi, Operatori)",
                 font=('Arial', 9), foreground='#666').pack(anchor='w', pady=(0, 10))

        btn_frame = ttk.Frame(complete_frame)
        btn_frame.pack(fill='x')

        ttk.Button(btn_frame, text="📄 Genera Template Completo",
                  command=self.genera_template_completo,
                  width=30).pack(side='left', padx=5)

        ttk.Label(btn_frame, text="Include: Skills, Turni, Giustificativi, Operatori",
                 font=('Arial', 8), foreground='#888').pack(side='left', padx=10)

        # === SEZIONE IMPORT DATI ===
        import_frame = ttk.LabelFrame(main_container, text="📤 Import Dati", padding=15)
        import_frame.pack(fill='x', pady=(0, 15), padx=15)

        ttk.Label(import_frame, text="Carica i dati compilati nei template Excel direttamente nel database",
                 font=('Arial', 9), foreground='#666').pack(anchor='w', pady=(0, 10))

        # Griglia bottoni import (2x2)
        import_grid = ttk.Frame(import_frame)
        import_grid.pack(fill='x')

        # RIGA 1 - Skills e Turni
        # Bottone Importa Skills
        skills_card = ttk.Frame(import_grid, relief='solid', borderwidth=1)
        skills_card.grid(row=0, column=0, padx=5, pady=5, sticky='nsew')

        ttk.Label(skills_card, text="🎯 Skills",
                 font=('Arial', 10, 'bold')).pack(anchor='w', padx=10, pady=(10, 5))
        ttk.Label(skills_card, text="Importa configurazione skill/code del contact center",
                 font=('Arial', 8), foreground='#666', wraplength=200).pack(anchor='w', padx=10, pady=(0, 10))

        # Buttons frame
        skills_btn_frame = ttk.Frame(skills_card)
        skills_btn_frame.pack(padx=10, pady=(0, 10))
        ttk.Button(skills_btn_frame, text="📤 Importa",
                  command=self.importa_skills,
                  width=12).pack(side='left', padx=(0, 5))
        ttk.Button(skills_btn_frame, text="🗑️ Elimina",
                  command=self.elimina_skills,
                  width=12).pack(side='left')

        # Bottone Importa Turni
        turni_card = ttk.Frame(import_grid, relief='solid', borderwidth=1)
        turni_card.grid(row=0, column=1, padx=5, pady=5, sticky='nsew')

        ttk.Label(turni_card, text="🕐 Turni",
                 font=('Arial', 10, 'bold')).pack(anchor='w', padx=10, pady=(10, 5))
        ttk.Label(turni_card, text="Importa turni e orari di lavoro",
                 font=('Arial', 8), foreground='#666', wraplength=200).pack(anchor='w', padx=10, pady=(0, 10))

        # Buttons frame
        turni_btn_frame = ttk.Frame(turni_card)
        turni_btn_frame.pack(padx=10, pady=(0, 10))
        ttk.Button(turni_btn_frame, text="📤 Importa",
                  command=self.importa_turni,
                  width=12).pack(side='left', padx=(0, 5))
        ttk.Button(turni_btn_frame, text="🗑️ Elimina",
                  command=self.elimina_turni,
                  width=12).pack(side='left')

        # RIGA 2 - Giustificativi e Anagrafica
        # Bottone Importa Giustificativi
        giust_card = ttk.Frame(import_grid, relief='solid', borderwidth=1)
        giust_card.grid(row=1, column=0, padx=5, pady=5, sticky='nsew')

        ttk.Label(giust_card, text="📋 Giustificativi",
                 font=('Arial', 10, 'bold')).pack(anchor='w', padx=10, pady=(10, 5))
        ttk.Label(giust_card, text="Importa codici assenze (Ferie, Malattia, ROL, etc.)",
                 font=('Arial', 8), foreground='#666', wraplength=200).pack(anchor='w', padx=10, pady=(0, 10))

        # Buttons frame
        giust_btn_frame = ttk.Frame(giust_card)
        giust_btn_frame.pack(padx=10, pady=(0, 10))
        ttk.Button(giust_btn_frame, text="📤 Importa",
                  command=self.importa_giustificativi,
                  width=12).pack(side='left', padx=(0, 5))
        ttk.Button(giust_btn_frame, text="🗑️ Elimina",
                  command=self.elimina_giustificativi,
                  width=12).pack(side='left')

        # Bottone Importa Anagrafica Operatori
        op_card = ttk.Frame(import_grid, relief='solid', borderwidth=1)
        op_card.grid(row=1, column=1, padx=5, pady=5, sticky='nsew')

        ttk.Label(op_card, text="👥 Anagrafica Operatori",
                 font=('Arial', 10, 'bold')).pack(anchor='w', padx=10, pady=(10, 5))
        ttk.Label(op_card, text="Importa operatori con turni, pause, straordinari",
                 font=('Arial', 8), foreground='#666', wraplength=200).pack(anchor='w', padx=10, pady=(0, 10))

        # Buttons frame
        op_btn_frame = ttk.Frame(op_card)
        op_btn_frame.pack(padx=10, pady=(0, 10))
        ttk.Button(op_btn_frame, text="📤 Importa",
                  command=self.importa_anagrafica_operatori,
                  width=12).pack(side='left', padx=(0, 5))
        ttk.Button(op_btn_frame, text="🗑️ Elimina",
                  command=self.elimina_anagrafica_operatori,
                  width=12).pack(side='left')

        # Configura grid weights per import
        import_grid.columnconfigure(0, weight=1)
        import_grid.columnconfigure(1, weight=1)

        # === SEZIONE TEMPLATES SINGOLI ===
        singles_frame = ttk.LabelFrame(main_container, text="📑 Templates Singoli", padding=15)
        singles_frame.pack(fill='both', expand=True, padx=15, pady=(0, 15))

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
        info_frame.pack(fill='x', pady=(0, 15), padx=15)

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

    def importa_giustificativi(self):
        """Importa giustificativi da file Excel"""
        import subprocess
        import sys
        import threading

        # Seleziona file Excel
        file_path = filedialog.askopenfilename(
            title="Seleziona file Excel con Giustificativi",
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
            "Conferma Import Giustificativi",
            f"Importare giustificativi da:\n{file_path}\n\n"
            "ATTENZIONE:\n"
            "• Se un codice esiste già, verrà AGGIORNATO\n"
            "• Nuovi codici verranno AGGIUNTI\n\n"
            "Il file deve avere un foglio 'Giust' o 'Giustificativi'.\n\n"
            "Continuare?"
        ):
            return

        # Crea finestra progresso
        progress_window = tk.Toplevel(self)
        progress_window.title("Import Giustificativi...")
        progress_window.geometry("600x400")
        progress_window.transient(self)
        progress_window.grab_set()

        ttk.Label(progress_window, text="Import Giustificativi in corso...",
                 font=('Arial', 12, 'bold')).pack(pady=10)

        # Text widget per output
        output_text = tk.Text(progress_window, height=20, width=70)
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
                                          'scripts', 'import_giustificativi.py')

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
                    output_text.insert('end', "\n✅ IMPORT COMPLETATO CON SUCCESSO!\n", 'success')
                    output_text.tag_config('success', foreground='green', font=('Arial', 10, 'bold'))
                else:
                    output_text.insert('end', "\n⚠️ Import completato con errori. Verifica sopra.\n", 'error')
                    output_text.tag_config('error', foreground='red', font=('Arial', 10, 'bold'))

                output_text.see('end')

                # Abilita bottone chiudi
                close_btn.config(state='normal')

            except Exception as e:
                output_text.insert('end', f"\n❌ ERRORE: {str(e)}\n", 'error')
                output_text.tag_config('error', foreground='red', font=('Arial', 10, 'bold'))
                close_btn.config(state='normal')

        # Avvia import in thread
        thread = threading.Thread(target=run_import, daemon=True)
        thread.start()

    def importa_anagrafica_operatori(self):
        """Importa anagrafica operatori da file Excel"""
        import subprocess
        import sys
        import threading

        # Seleziona file Excel
        file_path = filedialog.askopenfilename(
            title="Seleziona file Excel con Anagrafica Operatori",
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
            "Conferma Import Anagrafica",
            f"Importare anagrafica operatori da:\n{file_path}\n\n"
            "ATTENZIONE:\n"
            "• Se ID_SAP + Data esistono già, i dati verranno AGGIORNATI\n"
            "• Nuovi operatori/turni verranno AGGIUNTI\n"
            "• L'operazione potrebbe richiedere alcuni minuti\n\n"
            "Il file deve avere un foglio 'Operatori' con le colonne:\n"
            "ID_SAP, Nome, Cognome, Data_Riferimento, Ora_Inizio_Turno,\n"
            "Ora_Fine_Turno, Skill, etc.\n\n"
            "Continuare?"
        ):
            return

        # Crea finestra progresso
        progress_window = tk.Toplevel(self)
        progress_window.title("Import Anagrafica...")
        progress_window.geometry("600x400")
        progress_window.transient(self)
        progress_window.grab_set()

        ttk.Label(progress_window, text="Import Anagrafica Operatori in corso...",
                 font=('Arial', 12, 'bold')).pack(pady=10)

        # Text widget per output
        output_text = tk.Text(progress_window, height=20, width=70)
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
                    output_text.insert('end', "\n✅ IMPORT COMPLETATO CON SUCCESSO!\n", 'success')
                    output_text.tag_config('success', foreground='green', font=('Arial', 10, 'bold'))
                else:
                    output_text.insert('end', "\n⚠️ Import completato con errori. Verifica sopra.\n", 'error')
                    output_text.tag_config('error', foreground='red', font=('Arial', 10, 'bold'))

                output_text.see('end')

                # Abilita bottone chiudi
                close_btn.config(state='normal')

            except Exception as e:
                output_text.insert('end', f"\n❌ ERRORE: {str(e)}\n", 'error')
                output_text.tag_config('error', foreground='red', font=('Arial', 10, 'bold'))
                close_btn.config(state='normal')

        # Avvia import in thread
        thread = threading.Thread(target=run_import, daemon=True)
        thread.start()

    def importa_skills(self):
        """Importa skills da file Excel"""
        import subprocess
        import sys
        import threading

        # Seleziona file Excel
        file_path = filedialog.askopenfilename(
            title="Seleziona file Excel con Skills",
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
            "Conferma Import Skills",
            f"Importare skills da:\n{file_path}\n\n"
            "ATTENZIONE:\n"
            "• Se un codice skill esiste già, verrà AGGIORNATO\n"
            "• Nuovi codici verranno AGGIUNTI\n\n"
            "Il file deve avere un foglio 'Skills' con colonne:\n"
            "Codice_Skill, Descrizione, Produttivita_Default\n\n"
            "Continuare?"
        ):
            return

        # Crea finestra progresso
        progress_window = tk.Toplevel(self)
        progress_window.title("Import Skills...")
        progress_window.geometry("600x400")
        progress_window.transient(self)
        progress_window.grab_set()

        ttk.Label(progress_window, text="Import Skills in corso...",
                 font=('Arial', 12, 'bold')).pack(pady=10)

        # Text widget per output
        output_text = tk.Text(progress_window, height=20, width=70)
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
                                          'scripts', 'import_skills.py')

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
                    output_text.insert('end', "\n✅ IMPORT COMPLETATO CON SUCCESSO!\n", 'success')
                    output_text.tag_config('success', foreground='green', font=('Arial', 10, 'bold'))
                else:
                    output_text.insert('end', "\n⚠️ Import completato con errori. Verifica sopra.\n", 'error')
                    output_text.tag_config('error', foreground='red', font=('Arial', 10, 'bold'))

                output_text.see('end')

                # Abilita bottone chiudi
                close_btn.config(state='normal')

            except Exception as e:
                output_text.insert('end', f"\n❌ ERRORE: {str(e)}\n", 'error')
                output_text.tag_config('error', foreground='red', font=('Arial', 10, 'bold'))
                close_btn.config(state='normal')

        # Avvia import in thread
        thread = threading.Thread(target=run_import, daemon=True)
        thread.start()

    def importa_turni(self):
        """Importa turni da file Excel"""
        import subprocess
        import sys
        import threading

        # Seleziona file Excel
        file_path = filedialog.askopenfilename(
            title="Seleziona file Excel con Turni",
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
            "Conferma Import Turni",
            f"Importare turni da:\n{file_path}\n\n"
            "ATTENZIONE:\n"
            "• Se un ID_Turno esiste già, verrà AGGIORNATO\n"
            "• Nuovi turni verranno AGGIUNTI\n\n"
            "Il file deve avere un foglio 'Turni' con colonne:\n"
            "ID_Turno, Ora_Inizio, Ora_Fine, Descrizione (opzionale)\n\n"
            "Continuare?"
        ):
            return

        # Crea finestra progresso
        progress_window = tk.Toplevel(self)
        progress_window.title("Import Turni...")
        progress_window.geometry("600x400")
        progress_window.transient(self)
        progress_window.grab_set()

        ttk.Label(progress_window, text="Import Turni in corso...",
                 font=('Arial', 12, 'bold')).pack(pady=10)

        # Text widget per output
        output_text = tk.Text(progress_window, height=20, width=70)
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
                                          'scripts', 'import_excel_turni.py')

                process = subprocess.Popen(
                    [sys.executable, script_path, file_path],
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
                    output_text.insert('end', "\n✅ IMPORT COMPLETATO CON SUCCESSO!\n", 'success')
                    output_text.tag_config('success', foreground='green', font=('Arial', 10, 'bold'))
                else:
                    output_text.insert('end', "\n⚠️ Import completato con errori. Verifica sopra.\n", 'error')
                    output_text.tag_config('error', foreground='red', font=('Arial', 10, 'bold'))

                output_text.see('end')

                # Abilita bottone chiudi
                close_btn.config(state='normal')

            except Exception as e:
                output_text.insert('end', f"\n❌ ERRORE: {str(e)}\n", 'error')
                output_text.tag_config('error', foreground='red', font=('Arial', 10, 'bold'))
                close_btn.config(state='normal')

        # Avvia import in thread
        thread = threading.Thread(target=run_import, daemon=True)
        thread.start()

    def elimina_skills(self):
        """Elimina tutti i record dalla tabella Skills"""
        try:
            # Connetti al database e conta i record
            self.db_manager.connect()
            result = self.db_manager.execute_query("SELECT COUNT(*) as count FROM Skills")
            count = result[0]['count'] if result else 0
            self.db_manager.close()

            if count == 0:
                messagebox.showinfo("Info", "Nessuna skill presente nel database.")
                return

            # Conferma eliminazione
            if not messagebox.askyesno(
                "Conferma Eliminazione Skills",
                f"ATTENZIONE!\n\n"
                f"Stai per eliminare TUTTI i {count} record dalla tabella Skills.\n\n"
                f"Questa operazione NON può essere annullata!\n\n"
                f"Continuare?"
            ):
                return

            # Elimina
            self.db_manager.connect()
            self.db_manager.execute_update("DELETE FROM Skills")
            self.db_manager.close()

            messagebox.showinfo(
                "Successo",
                f"✅ Eliminati {count} record dalla tabella Skills.\n\n"
                f"Il database è stato pulito con successo."
            )

        except Exception as e:
            messagebox.showerror("Errore", f"Errore durante l'eliminazione:\n{e}")
            import traceback
            traceback.print_exc()
        finally:
            try:
                self.db_manager.close()
            except:
                pass

    def elimina_turni(self):
        """Elimina tutti i record dalla tabella Turni"""
        try:
            # Connetti al database e conta i record
            self.db_manager.connect()
            result = self.db_manager.execute_query("SELECT COUNT(*) as count FROM Turni")
            count = result[0]['count'] if result else 0
            self.db_manager.close()

            if count == 0:
                messagebox.showinfo("Info", "Nessun turno presente nel database.")
                return

            # Conferma eliminazione
            if not messagebox.askyesno(
                "Conferma Eliminazione Turni",
                f"ATTENZIONE!\n\n"
                f"Stai per eliminare TUTTI i {count} record dalla tabella Turni.\n\n"
                f"Questa operazione NON può essere annullata!\n\n"
                f"Continuare?"
            ):
                return

            # Elimina
            self.db_manager.connect()
            self.db_manager.execute_update("DELETE FROM Turni")
            self.db_manager.close()

            messagebox.showinfo(
                "Successo",
                f"✅ Eliminati {count} record dalla tabella Turni.\n\n"
                f"Il database è stato pulito con successo."
            )

        except Exception as e:
            messagebox.showerror("Errore", f"Errore durante l'eliminazione:\n{e}")
            import traceback
            traceback.print_exc()
        finally:
            try:
                self.db_manager.close()
            except:
                pass

    def elimina_giustificativi(self):
        """Elimina tutti i record dalla tabella Giustificativi"""
        try:
            # Connetti al database e conta i record
            self.db_manager.connect()
            result = self.db_manager.execute_query("SELECT COUNT(*) as count FROM Giustificativi")
            count = result[0]['count'] if result else 0
            self.db_manager.close()

            if count == 0:
                messagebox.showinfo("Info", "Nessun giustificativo presente nel database.")
                return

            # Conferma eliminazione
            if not messagebox.askyesno(
                "Conferma Eliminazione Giustificativi",
                f"ATTENZIONE!\n\n"
                f"Stai per eliminare TUTTI i {count} record dalla tabella Giustificativi.\n\n"
                f"Questa operazione NON può essere annullata!\n\n"
                f"NOTA: Se elimini i giustificativi, gli operatori con questi codici\n"
                f"potrebbero avere problemi nei calcoli!\n\n"
                f"Continuare?"
            ):
                return

            # Elimina
            self.db_manager.connect()
            self.db_manager.execute_update("DELETE FROM Giustificativi")
            self.db_manager.close()

            messagebox.showinfo(
                "Successo",
                f"✅ Eliminati {count} record dalla tabella Giustificativi.\n\n"
                f"Il database è stato pulito con successo."
            )

        except Exception as e:
            messagebox.showerror("Errore", f"Errore durante l'eliminazione:\n{e}")
            import traceback
            traceback.print_exc()
        finally:
            try:
                self.db_manager.close()
            except:
                pass

    def elimina_anagrafica_operatori(self):
        """Elimina tutti i record dalla tabella Anagrafica_Operatori"""
        try:
            # Connetti al database e conta i record
            self.db_manager.connect()
            result = self.db_manager.execute_query("SELECT COUNT(*) as count FROM Anagrafica_Operatori")
            count = result[0]['count'] if result else 0
            self.db_manager.close()

            if count == 0:
                messagebox.showinfo("Info", "Nessun operatore presente nel database.")
                return

            # Conferma eliminazione
            if not messagebox.askyesno(
                "Conferma Eliminazione Anagrafica Operatori",
                f"ATTENZIONE!\n\n"
                f"Stai per eliminare TUTTI i {count} record dalla tabella Anagrafica_Operatori.\n\n"
                f"Questa operazione NON può essere annullata!\n\n"
                f"NOTA: Questo eliminerà TUTTI i dati degli operatori inclusi turni,\n"
                f"pause, straordinari e giustificativi associati!\n\n"
                f"Continuare?"
            ):
                return

            # Elimina
            self.db_manager.connect()
            self.db_manager.execute_update("DELETE FROM Anagrafica_Operatori")
            self.db_manager.close()

            messagebox.showinfo(
                "Successo",
                f"✅ Eliminati {count} record dalla tabella Anagrafica_Operatori.\n\n"
                f"Il database è stato pulito con successo."
            )

        except Exception as e:
            messagebox.showerror("Errore", f"Errore durante l'eliminazione:\n{e}")
            import traceback
            traceback.print_exc()
        finally:
            try:
                self.db_manager.close()
            except:
                pass


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
