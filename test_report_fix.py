#!/usr/bin/env python3
"""
Test veloce per verificare che il fix _row_to_dict funzioni
"""
import sys
import os
import sqlite3
from datetime import datetime, timedelta

sys.path.insert(0, 'src')

from models.operatore import Operatore

def test_row_to_dict():
    """Testa la conversione Row -> Dict -> Operatore"""

    print("=" * 80)
    print("TEST: Verifica fix _row_to_dict per SQLite")
    print("=" * 80)
    print()

    # Connetti al database
    db_path = 'data/operator_overtime.db'
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Carica operatori per una data
    data_str = '2024-11-11'  # Lunedì
    print(f"1. Caricamento operatori per data: {data_str}")
    print()

    cursor.execute("SELECT * FROM Anagrafica_Operatori WHERE Data_Riferimento = ?", (data_str,))
    operatori_data = cursor.fetchall()
    print(f"   Righe trovate: {len(operatori_data)}")

    if not operatori_data:
        print("   ✗ Nessun operatore trovato!")
        conn.close()
        return

    print()
    print("2. Test conversione Row -> Dict -> Operatore")
    print()

    # Usa la stessa logica di riepilogo_screen.py
    def _row_to_dict(row):
        """Metodo fixato"""
        # SQLite Row objects (hanno keys())
        if hasattr(row, 'keys'):
            return {key: row[key] for key in row.keys()}

        # PyODBC Row objects (hanno cursor_description)
        if hasattr(row, 'cursor_description'):
            return {desc[0]: getattr(row, desc[0]) for desc in row.cursor_description}

        return {}

    all_operatori = []

    for i, row in enumerate(operatori_data):
        # Converti row in dict
        op_dict = _row_to_dict(row)

        if i == 0:
            print(f"   Esempio conversione prima riga:")
            print(f"   - Type row: {type(row)}")
            print(f"   - hasattr keys: {hasattr(row, 'keys')}")
            print(f"   - Campi estratti: {len(op_dict)}")
            print(f"   - Campi chiave:")
            for key in ['Nome', 'Cognome', 'ID_SAP', 'Ora_Inizio_Turno', 'Ora_Fine_Turno', 'Inizio_Pausa_1']:
                print(f"     {key}: {op_dict.get(key, 'MISSING')}")
            print()

        # Crea operatore
        op = Operatore(**op_dict)
        all_operatori.append(op)

        # Verifica che l'operatore abbia i dati
        if i == 0:
            print(f"   Verifica Operatore creato:")
            print(f"   - Nome: {op.nome}")
            print(f"   - Cognome: {op.cognome}")
            print(f"   - ID_SAP: {op.id_sap}")
            print(f"   - Skill: {op.etichetta_skill}")
            print(f"   - Turno: {op.ora_inizio_turno} - {op.ora_fine_turno}")
            print(f"   - Pause: {len(op.pause)} pause definite")
            print(f"   - Straordinari: {len(op.straordinari)} straordinari")
            print(f"   - Giustificativi: {len(op.giustificativi)} giustificativi")
            print()

    print(f"✓ Convertiti {len(all_operatori)} operatori con successo!")
    print()

    # Verifica statistiche
    print("3. Statistiche operatori caricati:")
    print()

    operatori_con_turno = sum(1 for op in all_operatori if op.ora_inizio_turno and op.ora_fine_turno)
    operatori_con_pause = sum(1 for op in all_operatori if len(op.pause) > 0)
    operatori_con_strao = sum(1 for op in all_operatori if len(op.straordinari) > 0)

    print(f"   - Operatori con turno definito: {operatori_con_turno}/{len(all_operatori)}")
    print(f"   - Operatori con pause: {operatori_con_pause}/{len(all_operatori)}")
    print(f"   - Operatori con straordinari: {operatori_con_strao}/{len(all_operatori)}")
    print()

    if operatori_con_turno > 0:
        print("   ✓ FIX FUNZIONA! Gli operatori hanno i dati dei turni!")
    else:
        print("   ✗ PROBLEMA! Gli operatori NON hanno i dati dei turni!")
        print("   Il bug _row_to_dict non è stato risolto.")

    print()

    # Test skill uniche
    print("4. Test aggregazione per skill:")
    print()

    skills = {}
    for op in all_operatori:
        skill = op.etichetta_skill or "Nessuna skill"
        if skill not in skills:
            skills[skill] = 0
        skills[skill] += 1

    for skill, count in skills.items():
        print(f"   - {skill}: {count} operatori")

    print()
    print("=" * 80)
    print("TEST COMPLETATO")
    print("=" * 80)
    print()
    print("CONCLUSIONE:")
    if operatori_con_turno == len(all_operatori) and operatori_con_turno > 0:
        print("✓ Il fix _row_to_dict funziona PERFETTAMENTE!")
        print("✓ Tutti gli operatori hanno i dati completi")
        print("✓ I report PER SERVIZIO e PER PERSONA dovrebbero funzionare!")
    elif operatori_con_turno > 0:
        print("⚠️  Il fix funziona PARZIALMENTE")
        print(f"⚠️  Solo {operatori_con_turno}/{len(all_operatori)} operatori hanno dati")
    else:
        print("✗ Il fix NON funziona")
        print("✗ Gli operatori non hanno dati dei turni")

    conn.close()

if __name__ == '__main__':
    test_row_to_dict()
