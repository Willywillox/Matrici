#!/usr/bin/env python3
"""
Script di verifica setup Matrici
Controlla che tutti i componenti siano configurati correttamente
"""

import sys
import os
from pathlib import Path

def print_header(text):
    """Stampa intestazione sezione"""
    print(f"\n{'='*60}")
    print(f"  {text}")
    print('='*60)

def print_check(name, status, message=""):
    """Stampa risultato check"""
    icon = "✅" if status else "❌"
    print(f"{icon} {name}")
    if message:
        print(f"   → {message}")

def check_python_version():
    """Verifica versione Python"""
    print_header("1. VERSIONE PYTHON")
    major, minor = sys.version_info[:2]
    version_ok = major >= 3 and minor >= 8
    print_check(
        "Python 3.8+",
        version_ok,
        f"Versione attuale: {major}.{minor}"
    )
    return version_ok

def check_dependencies():
    """Verifica dipendenze installate"""
    print_header("2. DIPENDENZE PYTHON")

    required = {
        'pyodbc': 'Connessione database Access',
        'pandas': 'Elaborazione dati',
        'openpyxl': 'Export Excel',
        'tkinter': 'Interfaccia grafica',
        'dateutil': 'Gestione date',
        'PIL': 'Gestione immagini',
        'tkcalendar': 'Widget calendario'
    }

    all_ok = True
    for module, description in required.items():
        try:
            if module == 'tkinter':
                import tkinter
            elif module == 'dateutil':
                import dateutil
            elif module == 'PIL':
                from PIL import Image
            else:
                __import__(module)
            print_check(f"{module}", True, description)
        except ImportError:
            print_check(f"{module}", False, f"NON INSTALLATO - {description}")
            all_ok = False

    return all_ok

def check_database_config():
    """Verifica configurazione database"""
    print_header("3. CONFIGURAZIONE DATABASE")

    config_file = Path("database_config.ini")

    if not config_file.exists():
        print_check(
            "database_config.ini",
            False,
            "File non trovato. Copia database_config.ini.example → database_config.ini"
        )
        return False

    print_check("database_config.ini", True, "File trovato")

    # Leggi configurazione
    with open(config_file, 'r', encoding='utf-8') as f:
        content = f.read()

    db_type_configured = 'type =' in content and '# type =' not in content
    print_check(
        "Tipo database configurato",
        db_type_configured,
        "Verifica che 'type = access' (o sqlite/sqlserver) sia impostato"
    )

    return db_type_configured

def check_project_structure():
    """Verifica struttura progetto"""
    print_header("4. STRUTTURA PROGETTO")

    required_paths = {
        'src/': 'Codice sorgente',
        'src/database/': 'Moduli database',
        'src/gui/': 'Interfacce grafiche',
        'src/models/': 'Modelli dati',
        'src/utils/': 'Utility',
        'scripts/': 'Script configurazione',
        'docs/': 'Documentazione',
        'requirements.txt': 'Dipendenze Python',
        'build_exe.spec': 'Configurazione build exe'
    }

    all_ok = True
    for path, description in required_paths.items():
        exists = Path(path).exists()
        print_check(path, exists, description)
        if not exists:
            all_ok = False

    return all_ok

def check_pyinstaller():
    """Verifica PyInstaller"""
    print_header("5. PYINSTALLER (per creare exe)")

    try:
        import PyInstaller
        version = PyInstaller.__version__
        print_check("PyInstaller", True, f"Versione {version}")
        return True
    except ImportError:
        print_check(
            "PyInstaller",
            False,
            "NON INSTALLATO - Esegui: pip install pyinstaller"
        )
        return False

def check_database_access():
    """Verifica accesso al database"""
    print_header("6. CONNESSIONE DATABASE")

    try:
        # Prova a importare il db_manager
        sys.path.insert(0, 'src')
        from database.db_manager import DatabaseManager

        db = DatabaseManager()
        print_check(
            "Connessione database",
            True,
            f"Connesso a: {db.config.db_type}"
        )

        # Verifica tabelle
        if db.config.db_type == 'access':
            # Per Access, verifica che il file esista
            db_path = Path(db.config.db_path)
            if db_path.exists():
                print_check(
                    "File database Access",
                    True,
                    f"Trovato: {db.config.db_path}"
                )
                return True
            else:
                print_check(
                    "File database Access",
                    False,
                    f"Non trovato: {db.config.db_path}\n   Esegui: scripts\\create_access_network.bat"
                )
                return False
        else:
            print_check("Tipo database", True, db.config.db_type)
            return True

    except Exception as e:
        print_check(
            "Connessione database",
            False,
            f"Errore: {str(e)}"
        )
        return False

def check_access_drivers():
    """Verifica driver Access"""
    print_header("7. DRIVER ACCESS (ODBC)")

    try:
        import pyodbc
        drivers = [d for d in pyodbc.drivers() if 'Access' in d or 'EXCEL' in d]

        if drivers:
            print_check("Driver Access", True, f"Trovati: {', '.join(drivers)}")
            return True
        else:
            print_check(
                "Driver Access",
                False,
                "Nessun driver trovato. Installa Microsoft Access Database Engine"
            )
            return False
    except Exception as e:
        print_check("Driver Access", False, f"Errore: {str(e)}")
        return False

def main():
    """Main function"""
    print("\n" + "="*60)
    print("  MATRICI - VERIFICA SETUP")
    print("  Controllo configurazione e dipendenze")
    print("="*60)

    results = []

    # Esegui tutti i check
    results.append(("Python Version", check_python_version()))
    results.append(("Dipendenze", check_dependencies()))
    results.append(("Configurazione DB", check_database_config()))
    results.append(("Struttura Progetto", check_project_structure()))
    results.append(("PyInstaller", check_pyinstaller()))
    results.append(("Driver Access", check_access_drivers()))
    results.append(("Database", check_database_access()))

    # Riepilogo finale
    print_header("RIEPILOGO")

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        icon = "✅" if result else "❌"
        print(f"{icon} {name}")

    print(f"\n{'='*60}")
    print(f"  RISULTATO: {passed}/{total} check superati")
    print('='*60)

    if passed == total:
        print("\n🎉 TUTTO OK! Sei pronto per costruire l'exe con:")
        print("   pyinstaller build_exe.spec")
        return 0
    else:
        print("\n⚠️  Alcuni check hanno fallito. Risolvi i problemi sopra.")
        print("   Consulta GUIDA_INSTALLAZIONE.md per aiuto.")
        return 1

if __name__ == '__main__':
    sys.exit(main())
