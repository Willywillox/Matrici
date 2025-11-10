import sqlite3
import sys
import os

# Trova il database
db_paths = [
    'data/operator_overtime.db',
    'data/operator_overtime.accdb',
    'operator_overtime.db'
]

db_path = None
for path in db_paths:
    if os.path.exists(path):
        db_path = path
        break

if not db_path:
    print("❌ Database non trovato!")
    print("\nPercorsi cercati:")
    for path in db_paths:
        print(f"  - {path}")
    sys.exit(1)

print(f"✓ Database trovato: {db_path}\n")

# Connetti al database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Controlla se esiste la tabella Forecast
try:
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='Forecast'")
    if not cursor.fetchone():
        print("❌ Tabella 'Forecast' non trovata nel database!")
        conn.close()
        sys.exit(1)
except:
    print("❌ Errore accesso database")
    conn.close()
    sys.exit(1)

# Controlla quanti record forecast ci sono
cursor.execute("SELECT COUNT(*) FROM Forecast")
total = cursor.fetchone()[0]
print(f"📊 Totale record forecast: {total}")

if total == 0:
    print("\n⚠️  ATTENZIONE: Nessun record forecast trovato!")
    print("Devi importare il file forecast_novembre.xlsx dall'interfaccia GUI")
    conn.close()
    sys.exit(0)

# Controlla date disponibili
cursor.execute("SELECT DISTINCT Data_Riferimento FROM Forecast ORDER BY Data_Riferimento")
dates = cursor.fetchall()
print(f"\n📅 Date disponibili nel forecast ({len(dates)}):")
for d in dates:
    print(f"  - {d[0]}")

# Controlla skill disponibili
cursor.execute("SELECT DISTINCT Skill FROM Forecast ORDER BY Skill")
skills = cursor.fetchall()
print(f"\n🎯 Skill disponibili nel forecast:")
for s in skills:
    print(f"  - {s[0]}")

# Cerca specificamente lo skill CMB
print(f"\n🔍 Controllo skill CMB:")
cursor.execute("SELECT COUNT(*) FROM Forecast WHERE Skill = 'CMB'")
cmb_count = cursor.fetchone()[0]
print(f"  Record con skill CMB: {cmb_count}")

if cmb_count > 0:
    cursor.execute("""
        SELECT Data_Riferimento, Fascia_Oraria, Volumi_Attesi
        FROM Forecast
        WHERE Skill = 'CMB' AND Volumi_Attesi > 0
        ORDER BY Data_Riferimento, Fascia_Oraria
        LIMIT 5
    """)
    rows = cursor.fetchall()
    print(f"\n  Primi 5 record CMB con volumi > 0:")
    for row in rows:
        print(f"    {row[0]} {row[1]}: {row[2]} volumi")

# Mostra alcuni record con volumi > 0 (qualsiasi skill)
cursor.execute("""
    SELECT Data_Riferimento, Fascia_Oraria, Skill, Volumi_Attesi
    FROM Forecast
    WHERE Volumi_Attesi > 0
    ORDER BY Data_Riferimento, Fascia_Oraria
    LIMIT 10
""")
rows = cursor.fetchall()
print(f"\n📈 Primi 10 record con volumi > 0 (qualsiasi skill):")
for row in rows:
    print(f"  {row[0]} {row[1]} - {row[2]}: {row[3]} volumi")

conn.close()

print("\n" + "="*60)
print("✅ Controllo completato!")
print("="*60)
