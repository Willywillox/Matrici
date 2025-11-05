"""
Script automatico per setup SQL Server
"""
import pyodbc
import sys
import os


def test_sqlserver_connection(server='localhost\\SQLEXPRESS'):
    """Testa connessione a SQL Server"""
    print(f"Testing connessione a {server}...")

    try:
        conn_str = (
            f"DRIVER={{ODBC Driver 17 for SQL Server}};"
            f"SERVER={server};"
            f"Trusted_Connection=yes;"
        )
        conn = pyodbc.connect(conn_str, timeout=5)
        conn.close()
        print("✓ Connessione SQL Server OK")
        return True
    except pyodbc.Error as e:
        print(f"✗ Errore connessione: {e}")
        print("\nVerifica:")
        print("1. SQL Server Express installato")
        print("2. Servizio SQL Server avviato")
        print("3. TCP/IP abilitato")
        print("4. Nome server corretto")
        return False


def create_database(server='localhost\\SQLEXPRESS'):
    """Crea database Matrici"""
    print(f"\nCreazione database Matrici su {server}...")

    script_path = os.path.join(os.path.dirname(__file__), 'create_sqlserver_database.sql')

    if not os.path.exists(script_path):
        print(f"✗ Script SQL non trovato: {script_path}")
        return False

    try:
        # Connessione a master per creare database
        conn_str = (
            f"DRIVER={{ODBC Driver 17 for SQL Server}};"
            f"SERVER={server};"
            f"DATABASE=master;"
            f"Trusted_Connection=yes;"
        )

        conn = pyodbc.connect(conn_str, autocommit=True)
        cursor = conn.cursor()

        # Leggi script SQL
        with open(script_path, 'r', encoding='utf-8') as f:
            sql_script = f.read()

        # Separa in batch (dividi per GO)
        batches = sql_script.split('GO')

        for i, batch in enumerate(batches, 1):
            batch = batch.strip()
            if batch and not batch.startswith('--'):
                try:
                    cursor.execute(batch)
                    print(f"  Batch {i}/{len(batches)} eseguito")
                except pyodbc.Error as e:
                    # Ignora errori "già esiste"
                    if 'already exists' not in str(e).lower():
                        print(f"  Warning batch {i}: {e}")

        conn.close()
        print("✓ Database Matrici creato con successo!")
        return True

    except pyodbc.Error as e:
        print(f"✗ Errore creazione database: {e}")
        return False


def create_config_file(server='localhost\\SQLEXPRESS'):
    """Crea file di configurazione"""
    print("\nCreazione file configurazione...")

    config_content = f"""# Configurazione Database Multi-Utente
# Generato automaticamente

[database]
type = sqlserver
server = {server}
database = Matrici
trusted_connection = yes

[multiuser]
auto_refresh = yes
refresh_interval = 30
show_notifications = yes
user_id =
"""

    config_path = 'database_config.ini'

    try:
        with open(config_path, 'w') as f:
            f.write(config_content)

        print(f"✓ File configurazione creato: {config_path}")
        return True

    except Exception as e:
        print(f"✗ Errore creazione config: {e}")
        return False


def verify_setup(server='localhost\\SQLEXPRESS'):
    """Verifica setup completato correttamente"""
    print("\nVerifica setup...")

    try:
        conn_str = (
            f"DRIVER={{ODBC Driver 17 for SQL Server}};"
            f"SERVER={server};"
            f"DATABASE=Matrici;"
            f"Trusted_Connection=yes;"
        )

        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()

        # Conta tabelle
        cursor.execute("""
            SELECT COUNT(*)
            FROM INFORMATION_SCHEMA.TABLES
            WHERE TABLE_TYPE = 'BASE TABLE'
        """)

        table_count = cursor.fetchone()[0]

        # Conta skills
        cursor.execute("SELECT COUNT(*) FROM Skills")
        skills_count = cursor.fetchone()[0]

        conn.close()

        print(f"✓ Database verificato:")
        print(f"  - Tabelle create: {table_count}")
        print(f"  - Skills precaricate: {skills_count}")

        return True

    except pyodbc.Error as e:
        print(f"✗ Errore verifica: {e}")
        return False


def main():
    """Main setup"""
    print("="*60)
    print("MATRICI - Setup SQL Server Multi-Utente")
    print("="*60)

    # Input server
    print("\nInserisci nome server SQL (default: localhost\\SQLEXPRESS)")
    server = input("Server: ").strip()

    if not server:
        server = 'localhost\\SQLEXPRESS'

    print(f"\nUsando server: {server}")

    # Step 1: Test connessione
    if not test_sqlserver_connection(server):
        print("\n⚠️  Setup interrotto: impossibile connettersi a SQL Server")
        print("\nVedi docs/MULTIUSER_SETUP.md per istruzioni installazione SQL Server")
        sys.exit(1)

    # Step 2: Crea database
    if not create_database(server):
        print("\n⚠️  Setup interrotto: errore creazione database")
        sys.exit(1)

    # Step 3: Crea config
    if not create_config_file(server):
        print("\n⚠️  Warning: errore creazione file configurazione")
        print("Crea manualmente database_config.ini")

    # Step 4: Verifica
    if not verify_setup(server):
        print("\n⚠️  Warning: errore verifica setup")
        print("Verifica manualmente il database")

    # Successo
    print("\n" + "="*60)
    print("✓ SETUP COMPLETATO CON SUCCESSO!")
    print("="*60)
    print("\nProssimi passi:")
    print("1. Copia database_config.ini su tutti i PC client")
    print("2. Modifica 'server' in database_config.ini se necessario")
    print("3. Installa ODBC Driver 17 su tutti i PC")
    print("4. Avvia Matrici e testa connessione")
    print("\nVedi docs/MULTIUSER_SETUP.md per dettagli completi")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nSetup interrotto dall'utente")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n✗ Errore imprevisto: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
