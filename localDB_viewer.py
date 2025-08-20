import sqlite3

DB_FILE = "inventory.db"

def show_table(table_name):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    try:
        cursor.execute(f"SELECT * FROM {table_name}")
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        print(f"\n--- {table_name.upper()} ---")
        print(" | ".join(columns))
        print("-" * 40)
        for row in rows:
            print(" | ".join(str(val) for val in row))
    except Exception as e:
        print(f"Error reading table {table_name}: {e}")
    finally:
        conn.close()

for table in ["empleado", "dispositivo", "registro"]:
    show_table(table)
