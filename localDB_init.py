import sqlite3

DB_FILE = "inventory.db"

def initialize_database():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Enable foreign key constraints
    cursor.execute("PRAGMA foreign_keys = ON")
    
    # Create employees table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS empleado (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        apellido TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Create devices table for barcode information
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS dispositivo (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        barcode TEXT UNIQUE NOT NULL,
        nombre TEXT NOT NULL,
        propietario TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Create registers table with foreign keys to both employees and devices
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS registro (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        id_empleado INTEGER NOT NULL,
        id_dispositivo INTEGER NOT NULL,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (id_empleado) REFERENCES empleado (id),
        FOREIGN KEY (id_dispositivo) REFERENCES dispositivo (id)
    )
    ''')
    
    conn.commit()
    conn.close()


def initialize_employees():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Verificar si la tabla empleado está vacía
    cursor.execute("SELECT COUNT(*) FROM empleado")
    count = cursor.fetchone()[0]
    
    if count == 0:
        # Insertar empleados iniciales
        empleados_iniciales = [
            ("Pedro", "González"),
            ("María", "López"),
            ("Juan", "Pérez"),
            ("Ana", "Martínez")
        ]
        
        cursor.executemany(
            "INSERT INTO empleado (nombre, apellido) VALUES (?, ?)",
            empleados_iniciales
        )
        conn.commit()
        
    conn.close()

def initialize_devices():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Verificar si la tabla dispositivo está vacía
    cursor.execute("SELECT COUNT(*) FROM dispositivo")
    count = cursor.fetchone()[0]
    
    if count == 0:
        # Insertar dispositivos iniciales
        dispositivos_iniciales = [
            ("123456789", "Escáner de Código de Barras", "Pedro"),
            ("987654321", "Impresora Térmica", "María"),
            ("456789123", "Lector RFID", "Juan"),
            ("789123456", "Balanza Electrónica", "Ana")
        ]
        
        cursor.executemany(
            "INSERT INTO dispositivo (barcode, nombre, propietario) VALUES (?, ?, ?)",
            dispositivos_iniciales
        )
        conn.commit()
    
    conn.close()

if __name__ == "__main__":
    initialize_database()
    initialize_employees()
    initialize_devices()