#!/usr/bin/env python3
"""
Script diagnostico per verificare il contenuto del database
e capire perché i report non trovano operatori
"""
import sys
import os
import sqlite3
from datetime import datetime

def diagnose():
    print("=" * 80)
    print("DIAGNOSI DATABASE - Verifica operatori e formati date")
    print("=" * 80)
    print()

    # Determina quale database usare
    db_paths = [
        'operator_overtime.db',
        'data/operator_overtime.db',
        'operator_overtime.accdb',
        'data/operator_overtime.accdb'
    ]

    db_path = None
    for path in db_paths:
        if os.path.exists(path):
            db_path = path
            print(f"✓ Database trovato: {path}")
            break

    if not db_path:
        print("✗ ERRORE: Nessun database trovato!")
        print(f"  Cercato in: {db_paths}")
        return

    # Solo SQLite supportato per diagnostica
    if not db_path.endswith('.db'):
        print("⚠️  Database Access rilevato (.accdb)")
        print("   Questo script diagnostico funziona solo con SQLite (.db)")
        print("   Se usi Access, controlla manualmente il database.")
        return

    print()

    # Connetti al database SQLite
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        print("✓ Connessione al database riuscita")
        print()
    except Exception as e:
        print(f"✗ ERRORE: Impossibile connettersi al database!")
        print(f"  {e}")
        return

    # 1. Conta totale operatori
    print("-" * 80)
    print("1. TOTALE RECORD NEL DATABASE")
    print("-" * 80)

    try:
        cursor.execute("SELECT COUNT(*) as total FROM Anagrafica_Operatori")
        result = cursor.fetchone()
        total = result[0] if result else 0
        print(f"   Totale record in Anagrafica_Operatori: {total}")

        if total == 0:
            print()
            print("   ⚠️  IL DATABASE È VUOTO!")
            print("   Devi prima importare i dati degli operatori.")
            conn.close()
            return
    except Exception as e:
        print(f"   ✗ Errore: {e}")
        conn.close()
        return

    print()

    # 2. Mostra tutte le date disponibili
    print("-" * 80)
    print("2. DATE DISPONIBILI NEL DATABASE")
    print("-" * 80)

    try:
        cursor.execute("SELECT DISTINCT Data_Riferimento FROM Anagrafica_Operatori ORDER BY Data_Riferimento")
        results = cursor.fetchall()

        if results:
            print(f"   Trovate {len(results)} date univoche:")
            print()

            # Mostra tutte le date (limitate a prime 20)
            for i, row in enumerate(results[:20]):
                data_ref = row['Data_Riferimento']
                print(f"   {i+1:3d}. {data_ref} (tipo: {type(data_ref).__name__})")

            if len(results) > 20:
                print(f"   ... e altre {len(results) - 20} date")

            print()
            print("   📅 Formato date rilevato:")
            data_esempio = results[0]['Data_Riferimento']
            print(f"      Esempio: {data_esempio}")
            print(f"      Tipo: {type(data_esempio)}")

            # Analizza il formato
            if isinstance(data_esempio, str):
                if '/' in data_esempio:
                    print(f"      Formato probabile: DD/MM/YYYY o MM/DD/YYYY")
                elif '-' in data_esempio:
                    print(f"      Formato probabile: YYYY-MM-DD")
                else:
                    print(f"      Formato sconosciuto")
        else:
            print("   ✗ Nessuna data trovata!")
    except Exception as e:
        print(f"   ✗ Errore: {e}")

    print()

    # 3. Mostra esempio di record
    print("-" * 80)
    print("3. ESEMPIO DI RECORD NEL DATABASE")
    print("-" * 80)

    try:
        cursor.execute("SELECT * FROM Anagrafica_Operatori LIMIT 1")
        row = cursor.fetchone()

        if row:
            print("   Campi del primo record:")
            print()

            # Mostra i campi principali
            campi_chiave = ['ID_SAP', 'Nome', 'Cognome', 'Data_Riferimento',
                           'Etichetta_Skill', 'Ora_Inizio_Turno', 'Ora_Fine_Turno']

            for field_name in campi_chiave:
                try:
                    field_value = row[field_name]
                    print(f"   {field_name:25s}: {field_value}")
                except:
                    pass
    except Exception as e:
        print(f"   ✗ Errore: {e}")

    print()

    # 4. Test ricerca per periodo 10-16 novembre
    print("-" * 80)
    print("4. TEST RICERCA PER PERIODO 10-16 NOVEMBRE 2024")
    print("-" * 80)
    print()

    date_to_test = [
        '2024-11-10',
        '10/11/2024',
        '11/10/2024',
        '2024-11-10 00:00:00',
        '10/11/2024 00:00:00'
    ]

    trovato = False
    for data_test in date_to_test:
        print(f"   Provo formato: {data_test}")

        try:
            cursor.execute("SELECT * FROM Anagrafica_Operatori WHERE Data_Riferimento = ?", (data_test,))
            operatori = cursor.fetchall()

            if operatori:
                print(f"   ✓ TROVATI {len(operatori)} operatori!")
                print(f"   ")
                # Mostra i primi 3
                for i, op in enumerate(operatori[:3]):
                    try:
                        nome = op['Nome']
                        cognome = op['Cognome']
                        id_sap = op['ID_SAP']
                        print(f"      - {cognome} {nome} (ID: {id_sap})")
                    except:
                        print(f"      - Record {i+1}")

                if len(operatori) > 3:
                    print(f"      ... e altri {len(operatori) - 3} operatori")

                print()
                print(f"   🎯 SOLUZIONE TROVATA!")
                print(f"   Il formato corretto per le date nel tuo database è: {data_test}")
                print()
                trovato = True
                break
            else:
                print(f"   ✗ Nessun operatore trovato")
        except Exception as e:
            print(f"   ✗ Errore: {e}")

    if not trovato:
        print()
        print(f"   ⚠️  NESSUN FORMATO HA FUNZIONATO!")
        print()
        print(f"   Possibili cause:")
        print(f"   1. Le date nel database non corrispondono a novembre 2024")
        print(f"   2. Il formato delle date è diverso da quelli testati")
        print(f"   3. Gli operatori sono registrati con altre date")
        print()
        print(f"   Controlla le date disponibili nella sezione 2 sopra.")

    print()

    # 5. Conta operatori per skill
    print("-" * 80)
    print("5. RIEPILOGO OPERATORI PER SKILL")
    print("-" * 80)

    try:
        cursor.execute("""
            SELECT Etichetta_Skill, COUNT(*) as count
            FROM Anagrafica_Operatori
            GROUP BY Etichetta_Skill
            ORDER BY count DESC
        """)
        results = cursor.fetchall()

        if results:
            print(f"   Skill trovate:")
            print()
            for row in results:
                skill = row['Etichetta_Skill']
                count = row['count']
                print(f"   {skill:30s}: {count:4d} record")
    except Exception as e:
        print(f"   ✗ Errore: {e}")

    print()
    print("=" * 80)
    print("DIAGNOSI COMPLETATA")
    print("=" * 80)

    conn.close()

if __name__ == '__main__':
    diagnose()
