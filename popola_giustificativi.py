#!/usr/bin/env python3
"""
Popola la tabella Giustificativi con i codici standard
"""
import sqlite3

db_path = 'data/operator_overtime.db'

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("=" * 80)
print("POPOLAMENTO TABELLA GIUSTIFICATIVI")
print("=" * 80)
print()

# Giustificativi standard
giustificativi = [
    ('Ferie', 'Ferie', 'Assenza retribuita per ferie'),
    ('Malattia', 'Malattia', 'Assenza per malattia'),
    ('Permesso', 'Permessi', 'Permesso retribuito'),
    ('ROL', 'ROL', 'Riduzione Orario di Lavoro'),
    ('Form', 'Form', 'Formazione'),
    ('Congedo', 'Congedo', 'Congedo parentale/matrimoniale'),
    ('Assenza', 'Assenza', 'Assenza generica'),
    ('Aspettativa', 'Aspettativa', 'Aspettativa non retribuita'),
    ('Infortunio', 'Malattia', 'Infortunio sul lavoro'),
    ('Maternita', 'Maternita', 'Congedo maternità'),
    ('Lutto', 'Permessi', 'Permesso per lutto'),
    ('Donazione', 'Permessi', 'Permesso per donazione sangue'),
]

inserted = 0
skipped = 0

for codice, tipologia, descrizione in giustificativi:
    try:
        cursor.execute("""
            INSERT INTO Giustificativi (Codice_Giustificativo, Tipologia, Descrizione)
            VALUES (?, ?, ?)
        """, (codice, tipologia, descrizione))
        print(f"✓ Inserito: {codice:15s} → Tipologia: {tipologia}")
        inserted += 1
    except sqlite3.IntegrityError:
        print(f"  Saltato: {codice:15s} (già esistente)")
        skipped += 1

conn.commit()

print()
print(f"Inseriti: {inserted}, Saltati: {skipped}")
print()

# Verifica
cursor.execute("SELECT COUNT(*) FROM Giustificativi")
total = cursor.fetchone()[0]

print(f"Totale giustificativi in tabella: {total}")
print()

if total > 0:
    print("✓ Tabella Giustificativi popolata correttamente!")
    print()
    print("Adesso i report dovrebbero funzionare!")
    print()
    print("PROSSIMI PASSI:")
    print("1. Riavvia l'app Matrici")
    print("2. Genera il report per vedere se le Ferie vengono riconosciute")
else:
    print("✗ Problema nell'inserimento")

conn.close()
