#!/usr/bin/env python3
"""
Script per popolare la tabella Skills dagli operatori esistenti

Estrae skill unici dalla colonna Etichetta_Skill degli operatori
e li inserisce nella tabella Skills se non esistono già.

Uso:
    python scripts/populate_skills_from_operatori.py
"""

import sys
import os
from pathlib import Path

# Aggiungi path per import
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from database.db_manager import DatabaseManager


def populate_skills(db_path='data/operator_overtime.db'):
    """
    Popola tabella Skills estraendo skill unici dagli operatori
    """

    print(f"\n{'='*70}")
    print(f"  POPOLAMENTO TABELLA SKILLS DA OPERATORI")
    print(f"{'='*70}\n")
    print(f"Database: {db_path}\n")

    if not Path(db_path).exists():
        print(f"[ERROR] Database non trovato: {db_path}")
        return False

    db_manager = DatabaseManager(db_path)

    try:
        db_manager.connect()

        # Estrai skill unici dagli operatori
        print("[1/3] Estrazione skill unici dalla colonna Etichetta_Skill...")
        result = db_manager.execute_query("""
            SELECT DISTINCT Etichetta_Skill
            FROM Anagrafica_Operatori
            WHERE Etichetta_Skill IS NOT NULL
            AND TRIM(Etichetta_Skill) != ''
            ORDER BY Etichetta_Skill
        """)

        if not result or len(result) == 0:
            print("    [WARN] Nessuno skill trovato nella colonna Etichetta_Skill")
            print("    [INFO] Assicurati che gli operatori abbiano il campo Etichetta_Skill compilato")
            db_manager.close()
            return False

        skills_trovate = [row[0].strip() for row in result]
        print(f"    [OK] Trovati {len(skills_trovate)} skill unici:\n")
        for skill in skills_trovate:
            print(f"      - {skill}")
        print()

        # Conta skill già esistenti in tabella Skills
        print("[2/3] Verifica skill già presenti in tabella Skills...")
        existing = db_manager.execute_query("SELECT Codice_Skill FROM Skills")
        existing_skills = set([row[0] for row in existing]) if existing else set()

        if existing_skills:
            print(f"    [INFO] Skill già presenti: {len(existing_skills)}")
            for skill in existing_skills:
                print(f"      - {skill}")
            print()

        # Inserisci skill mancanti
        print("[3/3] Inserimento skill nella tabella Skills...")
        inserted = 0
        skipped = 0

        for skill in skills_trovate:
            if skill in existing_skills:
                print(f"    [SKIP] '{skill}' - già presente")
                skipped += 1
            else:
                # Inserisci nuovo skill
                query = """
                    INSERT INTO Skills (Codice_Skill, Descrizione, Produttivita_Default)
                    VALUES (?, ?, ?)
                """
                db_manager.execute_update(query, (skill, f"Skill {skill}", 1.0))
                print(f"    [OK] '{skill}' - inserita")
                inserted += 1

        # Riepilogo
        print(f"\n{'='*70}")
        print(f"  RIEPILOGO")
        print(f"{'='*70}")
        print(f"[OK] Skill inserite:        {inserted}")
        print(f"[SKIP] Skill già presenti:  {skipped}")
        print(f"[INFO] Totale skill:        {len(existing_skills) + inserted}")
        print(f"{'='*70}\n")

        db_manager.close()
        return True

    except Exception as e:
        print(f"[ERROR] Errore: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main function"""

    # Path database
    db_path = 'data/operator_overtime.db'

    if not os.path.exists(db_path):
        print(f"[ERROR] Database non trovato: {db_path}")
        print("\nAssicurati di eseguire lo script dalla directory principale del progetto")
        return 1

    # Popola skills
    success = populate_skills(db_path)

    if success:
        print("\n[INFO] Skills popolate con successo!")
        print("[INFO] Ora riavvia l'applicazione e vedrai gli skill nelle dropdown")
        return 0
    else:
        print("\n[ERROR] Popolamento fallito. Verifica gli errori sopra.")
        return 1


if __name__ == '__main__':
    sys.exit(main())
