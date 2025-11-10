#!/usr/bin/env python3
"""
Script diagnostico per verificare perché le ore calcolate non corrispondono
"""
import sys
import os
import sqlite3
from datetime import datetime

sys.path.insert(0, 'src')

from models.operatore import Operatore

def diagnose_ore_calcolo():
    """Diagnostica il calcolo delle ore per un operatore specifico"""

    db_path = 'data/operator_overtime.db'

    print("=" * 80)
    print("DIAGNOSTICA CALCOLO ORE OPERATORE")
    print("=" * 80)
    print()

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Chiedi quale operatore verificare
    print("Operatori disponibili:")
    cursor.execute("""
        SELECT DISTINCT ID_SAP, Nome, Cognome
        FROM Anagrafica_Operatori
        WHERE Data_Riferimento BETWEEN '2024-11-10' AND '2024-11-16'
        ORDER BY Cognome, Nome
    """)

    operatori = cursor.fetchall()
    for i, op in enumerate(operatori):
        print(f"  {i+1}. {op['Cognome']} {op['Nome']} (ID: {op['ID_SAP']})")

    print()

    # Prendi il primo operatore per diagnostica
    id_sap = operatori[0]['ID_SAP'] if operatori else None

    if not id_sap:
        print("Nessun operatore trovato!")
        conn.close()
        return

    print(f"Analisi per: {operatori[0]['Cognome']} {operatori[0]['Nome']} (ID: {id_sap})")
    print()

    # Carica dati settimana per settimana
    cursor.execute("""
        SELECT Data_Riferimento,
               Ora_Inizio_Turno, Ora_Fine_Turno,
               Inizio_Pausa_1, Fine_Pausa_1,
               Inizio_Strao_1, Fine_Strao_1,
               Tipo_Giust_1, Inizio_Giust_1, Fine_Giust_1
        FROM Anagrafica_Operatori
        WHERE ID_SAP = ?
        AND Data_Riferimento BETWEEN '2024-11-10' AND '2024-11-16'
        ORDER BY Data_Riferimento
    """, (id_sap,))

    giorni = cursor.fetchall()

    print("Dettaglio giornaliero:")
    print()

    total_ore_teoriche = 0
    total_ore_pausa = 0
    total_ore_strao = 0
    total_ore_produzione_calcolate = 0

    def _row_to_dict(row):
        """Converte SQLite row in dict"""
        if hasattr(row, 'keys'):
            return {key: row[key] for key in row.keys()}
        return {}

    for giorno in giorni:
        data = giorno['Data_Riferimento']

        # Carica operatore per quel giorno
        cursor.execute("SELECT * FROM Anagrafica_Operatori WHERE ID_SAP = ? AND Data_Riferimento = ?",
                      (id_sap, data))
        row = cursor.fetchone()
        op_dict = _row_to_dict(row)
        op = Operatore(**op_dict)

        # Calcola ore turno teoriche
        if op.ora_inizio_turno and op.ora_fine_turno:
            if op.ora_inizio_turno.hour == 0 and op.ora_fine_turno.hour == 0:
                ore_turno = 0  # Riposo
            else:
                ore_turno = (op.ora_fine_turno.hour * 60 + op.ora_fine_turno.minute -
                            op.ora_inizio_turno.hour * 60 - op.ora_inizio_turno.minute) / 60.0
        else:
            ore_turno = 0

        # Calcola ore pausa
        ore_pausa = 0
        for inizio, fine in op.pause:
            ore_pausa += (fine.hour * 60 + fine.minute - inizio.hour * 60 - inizio.minute) / 60.0

        # Calcola ore straordinario
        ore_strao = 0
        for inizio, fine in op.straordinari:
            ore_strao += (fine.hour * 60 + fine.minute - inizio.hour * 60 - inizio.minute) / 60.0

        # Calcola ore di produzione effettive contando i 15-min slots
        ore_produzione_slot = 0
        ore_pausa_slot = 0
        ore_strao_slot = 0

        # Simula il calcolo con slot da 15 minuti
        for ora in range(24):
            for minuto in [0, 15, 30, 45]:
                from datetime import time
                orario = time(ora, minuto)

                if op.is_presente(orario):
                    if op.is_in_pausa(orario):
                        ore_pausa_slot += 0.25
                    else:
                        ore_produzione_slot += 0.25

                    if op.is_in_straordinario(orario):
                        ore_strao_slot += 0.25

        print(f"  {data}:")
        print(f"    Turno teorico: {op.ora_inizio_turno or '--'} - {op.ora_fine_turno or '--'} = {ore_turno:.2f}h")
        print(f"    Pause teoriche: {ore_pausa:.2f}h ({len(op.pause)} pause)")
        print(f"    Strao teorico: {ore_strao:.2f}h ({len(op.straordinari)} periodi)")
        print(f"    ---")
        print(f"    CALCOLO CON SLOT 15-MIN:")
        print(f"    Ore produzione (slot): {ore_produzione_slot:.2f}h")
        print(f"    Ore pausa (slot): {ore_pausa_slot:.2f}h")
        print(f"    Ore strao (slot): {ore_strao_slot:.2f}h")

        if abs(ore_turno - ore_pausa - ore_produzione_slot) > 0.5:
            print(f"    ⚠️  DISCREPANZA: Teorico={(ore_turno - ore_pausa):.2f}h vs Calcolato={ore_produzione_slot:.2f}h")

        print()

        total_ore_teoriche += ore_turno
        total_ore_pausa += ore_pausa
        total_ore_strao += ore_strao
        total_ore_produzione_calcolate += ore_produzione_slot

    print("-" * 80)
    print("TOTALE SETTIMANA:")
    print(f"  Ore turno teoriche: {total_ore_teoriche:.2f}h")
    print(f"  Ore pausa: {total_ore_pausa:.2f}h")
    print(f"  Ore nette teoriche (turno - pausa): {total_ore_teoriche - total_ore_pausa:.2f}h")
    print(f"  Ore straordinario: {total_ore_strao:.2f}h")
    print()
    print(f"  ORE PRODUZIONE CALCOLATE (con slot 15-min): {total_ore_produzione_calcolate:.2f}h")
    print(f"  Ore ordinarie (produzione - strao): {total_ore_produzione_calcolate - total_ore_strao:.2f}h")
    print()

    if abs(total_ore_produzione_calcolate - 20) > 1 and total_ore_teoriche > 0:
        print("POSSIBILI PROBLEMI:")
        diff = total_ore_produzione_calcolate - 20
        if diff > 0:
            print(f"  - Le ore sono {diff:.2f}h in PIÙ rispetto alle 20h attese")
            print(f"  - Verifica se:")
            print(f"    • Le pause sono definite correttamente")
            print(f"    • Non ci sono record duplicati per la stessa data")
            print(f"    • I turni effettivi corrispondono a quanto dichiarato")

    conn.close()

if __name__ == '__main__':
    diagnose_ore_calcolo()
