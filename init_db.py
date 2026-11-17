import sqlite3

conn = sqlite3.connect("healthcore.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario TEXT UNIQUE,
    correo TEXT UNIQUE,
    password TEXT,
    nombre TEXT,
    apellido TEXT,
    edad INTEGER,
    genero TEXT,
    estatura REAL,
    peso REAL,
    meta_tipo TEXT,
    meta_kg REAL,
    avatar_path TEXT,
    avatar_category TEXT,
    avatar_name TEXT,
    theme TEXT
)
""")

conn.commit()
conn.close()

print("✔ Base de datos creada correctamente")