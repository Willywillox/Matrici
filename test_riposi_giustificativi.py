#!/usr/bin/env python3
"""
Verifica il comportamento di riposi e giustificativi
"""
import sys
import sqlite3
from datetime import datetime, timedelta, time

sys.path.insert(0, 'src')

from models.operatore import Operatore
from utils.capability_calculator import CapabilityCalculator

db_path = 'data/operator_overtime.db'

conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

print("=" * 80)
print("VERIFICA RIPOSI E GIUSTIFICATIVI")
print("=" * 80)
print()

# Cerca operatrice Inserra
cursor.execute("""
    SELECT ID_SAP, Nome, Cognome
    FROM Anagrafica_Operatori
    WHERE Cognome LIKE '%Inserra%' OR Cognome LIKE '%inserra%'
    LIMIT 1
""")

inserra = cursor.fetchone()

if inserra:
    id_sap = inserra['ID_SAP']
    nome = inserra['Nome']
    cognome = inserra['Cognome']

    print(f"Trovata operatrice: {cognome} {nome} (ID: {id_sap})")
    print()

    # Carica tutti i giorni per questa operatrice
    cursor.execute("""
        SELECT Data_Riferimento,
               Ora_Inizio_Turno, Ora_Fine_Turno,
               Tipo_Giust_1, Inizio_Giust_1, Fine_Giust_1
        FROM Anagrafica_Operatori
        WHERE ID_SAP = ?
        ORDER BY Data_Riferimento
        LIMIT 10
    """, (id_sap,))

    giorni = cursor.fetchall()

    print(f"Giorni trovati: {len(giorni)}")
    print()
    print("Dettaglio:")
    print("-" * 80)

    def _row_to_dict(row):
        if hasattr(row, 'keys'):
            return {key: row[key] for key in row.keys()}
        return {}

    for giorno in giorni:
        data = giorno['Data_Riferimento']
        turno_inizio = giorno['Ora_Inizio_Turno']
        turno_fine = giorno['Ora_Fine_Turno']
        tipo_giust = giorno['Tipo_Giust_1']

        # Carica operatore completo
        cursor.execute("SELECT * FROM Anagrafica_Operatori WHERE ID_SAP = ? AND Data_Riferimento = ?",
                      (id_sap, data))
        row = cursor.fetchone()
        op_dict = _row_to_dict(row)
        op = Operatore(**op_dict)

        # Testa presenza a vari orari
        ore_produzione = 0
        ore_pausa = 0
        ore_giust = 0

        for h in range(24):
            for m in [0, 15, 30, 45]:
                t = time(h, m)

                # Controlla se è in giustificativo
                giust = op.get_giustificativo_at_time(t)
                if giust:
                    ore_giust += 0.25
                elif op.is_presente(t):
                    if op.is_in_pausa(t):
                        ore_pausa += 0.25
                    else:
                        ore_produzione += 0.25

        # Tipo giorno
        if turno_inizio == '00:00' and turno_fine == '00:00':
            tipo_giorno = "RIPOSO" if not tipo_giust else f"ASSENZA ({tipo_giust})"
        else:
            tipo_giorno = "LAVORO"

        print(f"{data}: {tipo_giorno}")
        print(f"  Turno: {turno_inizio} - {turno_fine}")
        if tipo_giust:
            print(f"  Giustificativo: {tipo_giust}")
        print(f"  Ore calcolate: Prod={ore_produzione:.2f}h, Pausa={ore_pausa:.2f}h, Giust={ore_giust:.2f}h")

        if tipo_giorno == "RIPOSO" and ore_produzione > 0:
            print(f"  ❌ ERRORE: Riposo conta {ore_produzione}h di produzione!")

        if tipo_giust and ore_giust == 0:
            print(f"  ❌ ERRORE: Giustificativo '{tipo_giust}' non viene conteggiato!")

        print()

else:
    print("Operatrice 'Inserra' non trovata nel database")
    print()
    print("Operatori disponibili:")
    cursor.execute("SELECT DISTINCT Cognome, Nome FROM Anagrafica_Operatori ORDER BY Cognome")
    for row in cursor.fetchall():
        print(f"  - {row['Cognome']} {row['Nome']}")

print()
print("=" * 80)
print("TEST RIPOSO GENERICO")
print("=" * 80)
print()

# Test generico con riposo
test_data = {
    'Nome': 'Test',
    'Cognome': 'Riposo',
    'ID_SAP': 'TEST',
    'Ora_Inizio_Turno': '00:00',
    'Ora_Fine_Turno': '00:00'
}

op_riposo = Operatore(**test_data)

print("Operatore di test con riposo (00:00-00:00):")
print(f"  Turno: {op_riposo.ora_inizio_turno} - {op_riposo.ora_fine_turno}")

# Conta ore
ore = 0
for h in range(24):
    for m in [0, 15, 30, 45]:
        t = time(h, m)
        if op_riposo.is_presente(t):
            ore += 0.25

print(f"  Ore produzione calcolate: {ore:.2f}h")

if ore > 0:
    print(f"  ❌ ERRORE: Il riposo viene conteggiato!")
    print()
    print("  Debug is_presente() per alcuni orari:")
    for h in [0, 8, 12, 18]:
        t = time(h, 0)
        presente = op_riposo.is_presente(t)
        print(f"    {t}: is_presente = {presente}")
else:
    print(f"  ✓ OK: Il riposo NON viene conteggiato")

conn.close()
