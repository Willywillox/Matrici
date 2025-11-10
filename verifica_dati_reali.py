#!/usr/bin/env python3
"""
Verifica i tuoi dati reali per capire il problema riposi/giustificativi
"""
import sqlite3

db_path = 'data/operator_overtime.db'

conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

print("=" * 80)
print("DIAGNOSTICA DATI REALI - RIPOSI E GIUSTIFICATIVI")
print("=" * 80)
print()

# 1. Conta operatori totali
cursor.execute("SELECT COUNT(*) FROM Anagrafica_Operatori")
total = cursor.fetchone()[0]
print(f"Totale record nel database: {total}")
print()

# 2. Cerca operatrice Inserra
print("-" * 80)
print("1. RICERCA OPERATRICE INSERRA")
print("-" * 80)
print()

cursor.execute("""
    SELECT DISTINCT ID_SAP, Nome, Cognome
    FROM Anagrafica_Operatori
    WHERE LOWER(Cognome) LIKE '%inserra%'
""")

inserra_list = cursor.fetchall()

if inserra_list:
    for op in inserra_list:
        print(f"Trovata: {op['Cognome']} {op['Nome']} (ID: {op['ID_SAP']})")

        # Mostra i suoi giorni
        cursor.execute("""
            SELECT Data_Riferimento,
                   Ora_Inizio_Turno, Ora_Fine_Turno,
                   Tipo_Giust_1, Inizio_Giust_1, Fine_Giust_1,
                   Tipo_Giust_2, Inizio_Giust_2, Fine_Giust_2
            FROM Anagrafica_Operatori
            WHERE ID_SAP = ?
            ORDER BY Data_Riferimento
        """, (op['ID_SAP'],))

        giorni = cursor.fetchall()
        print(f"  Giorni trovati: {len(giorni)}")
        print()

        for g in giorni:
            data = g['Data_Riferimento']
            turno = f"{g['Ora_Inizio_Turno']} - {g['Ora_Fine_Turno']}"
            giust1 = g['Tipo_Giust_1']
            giust2 = g['Tipo_Giust_2']

            tipo = "LAVORO"
            if g['Ora_Inizio_Turno'] == '00:00' and g['Ora_Fine_Turno'] == '00:00':
                if giust1:
                    tipo = f"ASSENZA ({giust1})"
                else:
                    tipo = "RIPOSO"

            print(f"  {data}: {tipo} - Turno: {turno}")
            if giust1:
                print(f"    Giust1: {giust1} ({g['Inizio_Giust_1']}-{g['Fine_Giust_1']})")
            if giust2:
                print(f"    Giust2: {giust2} ({g['Inizio_Giust_2']}-{g['Fine_Giust_2']})")

        print()
else:
    print("  Operatrice 'Inserra' NON trovata")
    print()

# 3. Mostra tutti gli operatori disponibili
print("-" * 80)
print("2. TUTTI GLI OPERATORI NEL DATABASE")
print("-" * 80)
print()

cursor.execute("""
    SELECT DISTINCT ID_SAP, Cognome, Nome
    FROM Anagrafica_Operatori
    ORDER BY Cognome, Nome
""")

operatori = cursor.fetchall()
print(f"Operatori unici: {len(operatori)}")
print()

for i, op in enumerate(operatori, 1):
    print(f"{i:2d}. {op['Cognome']:20s} {op['Nome']:15s} (ID: {op['ID_SAP']})")

print()

# 4. Analisi riposi
print("-" * 80)
print("3. ANALISI RIPOSI (00:00-00:00)")
print("-" * 80)
print()

cursor.execute("""
    SELECT ID_SAP, Cognome, Nome, Data_Riferimento,
           Tipo_Giust_1, Tipo_Giust_2
    FROM Anagrafica_Operatori
    WHERE Ora_Inizio_Turno = '00:00'
      AND Ora_Fine_Turno = '00:00'
    ORDER BY Cognome, Data_Riferimento
    LIMIT 20
""")

riposi = cursor.fetchall()

print(f"Record con turno 00:00-00:00: {len(riposi)}")
print()

if riposi:
    for r in riposi:
        tipo = "RIPOSO"
        if r['Tipo_Giust_1']:
            tipo = f"ASSENZA ({r['Tipo_Giust_1']})"

        print(f"{r['Cognome']:15s} {r['Nome']:10s} - {r['Data_Riferimento']:12s} - {tipo}")

    print()
    print("⚠️  IMPORTANTE:")
    print("Se vedi ore di produzione per questi giorni, il problema è che:")
    print("1. Il calcolo NON esclude correttamente i turni 00:00-00:00")
    print("2. Oppure ci sono record DUPLICATI per la stessa data")

print()

# 5. Cerca duplicati
print("-" * 80)
print("4. VERIFICA DUPLICATI")
print("-" * 80)
print()

cursor.execute("""
    SELECT ID_SAP, Data_Riferimento, COUNT(*) as count
    FROM Anagrafica_Operatori
    GROUP BY ID_SAP, Data_Riferimento
    HAVING COUNT(*) > 1
    LIMIT 10
""")

duplicati = cursor.fetchall()

if duplicati:
    print(f"⚠️  TROVATI {len(duplicati)} DUPLICATI!")
    print()
    for d in duplicati:
        print(f"  {d['ID_SAP']} - {d['Data_Riferimento']} : {d['count']} record")
    print()
    print("QUESTO È IL PROBLEMA! Ogni giorno viene contato più volte!")
else:
    print("✓ Nessun duplicato trovato")

print()

# 6. Analisi giustificativi
print("-" * 80)
print("5. ANALISI GIUSTIFICATIVI")
print("-" * 80)
print()

cursor.execute("""
    SELECT Cognome, Nome, Data_Riferimento, Tipo_Giust_1,
           Ora_Inizio_Turno, Ora_Fine_Turno
    FROM Anagrafica_Operatori
    WHERE Tipo_Giust_1 IS NOT NULL
    ORDER BY Cognome, Data_Riferimento
    LIMIT 15
""")

giust = cursor.fetchall()

print(f"Record con giustificativi: {len(giust)}")
print()

if giust:
    for g in giust:
        print(f"{g['Cognome']:15s} {g['Nome']:10s} - {g['Data_Riferimento']:12s}")
        print(f"  Giustificativo: {g['Tipo_Giust_1']}")
        print(f"  Turno: {g['Ora_Inizio_Turno']} - {g['Ora_Fine_Turno']}")
        print()

conn.close()

print("=" * 80)
print("FINE DIAGNOSTICA")
print("=" * 80)
print()
print("PROSSIMI PASSI:")
print("1. Se trovi DUPLICATI, devi pulire il database")
print("2. Se Inserra ha ferie solo un giorno ma le vedi su tutti,")
print("   verifica che il Tipo_Giust_1 sia impostato solo sul giorno corretto")
print("3. Esegui: python check_duplicati.py per verificare duplicati")
