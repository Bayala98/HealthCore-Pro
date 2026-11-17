"""SQLite persistence, transactional operations, audit triggers and backups."""
from contextlib import contextmanager
from datetime import datetime
import os
import sqlite3


class Database:
    # Singleton: durante la ejecución, todas las pantallas comparten la conexión.
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.database_url = os.environ.get("HEALTHCORE_DATABASE_URL")
            cls._instance.is_postgres = bool(cls._instance.database_url)
            if cls._instance.is_postgres:
                # El modo TLS lo determina sslmode en la URL: disable en local sin TLS; require en remoto con TLS.
                import psycopg
                cls._instance.connection = psycopg.connect(cls._instance.database_url, autocommit=True)
                cls._instance.db_path = None
            else:
                # Sin URL, el modo habitual sigue siendo el archivo local SQLite.
                base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                cls._instance.db_path = os.path.join(base_dir, "healthcore.db")
                cls._instance.connection = sqlite3.connect(
                    cls._instance.db_path, check_same_thread=False, timeout=30
                )
                cls._instance.connection.execute("PRAGMA foreign_keys = ON")
                cls._instance.connection.execute("PRAGMA busy_timeout = 30000")
                cls._instance.create_tables()
        return cls._instance

    def create_tables(self):
        # Esquema local. El equivalente para PostgreSQL está en
        # database/postgresql_schema.sql y se instala en el servidor por separado.
        with self.connection:
            self.connection.execute('''CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario TEXT UNIQUE, correo TEXT UNIQUE, password TEXT,
                nombre TEXT, apellido TEXT, edad INTEGER, genero TEXT,
                estatura REAL, peso REAL, meta_tipo TEXT, meta_kg REAL,
                avatar_path TEXT, avatar_category TEXT, avatar_name TEXT, theme TEXT
            )''')
            self.connection.execute('''CREATE TABLE IF NOT EXISTS health_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL, tipo TEXT NOT NULL, valor REAL,
                detalle TEXT, fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
            )''')
            self.connection.execute('''CREATE TABLE IF NOT EXISTS audit_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                table_name TEXT NOT NULL, operation TEXT NOT NULL,
                record_id INTEGER, user_id INTEGER, occurred_at TEXT NOT NULL,
                summary TEXT
            )''')
            # Triggers auditan cambios sin guardar datos sensibles de usuarios.
            for event in ("INSERT", "UPDATE", "DELETE"):
                ref = "NEW" if event != "DELETE" else "OLD"
                self.connection.execute(f'''CREATE TRIGGER IF NOT EXISTS trg_health_{event.lower()}
                    AFTER {event} ON health_records BEGIN
                    INSERT INTO audit_log(table_name, operation, record_id, user_id, occurred_at, summary)
                    VALUES ('health_records', '{event}', {ref}.id, {ref}.user_id,
                    CURRENT_TIMESTAMP, {ref}.tipo);
                END''')
            self.connection.execute('''CREATE TRIGGER IF NOT EXISTS trg_users_insert_audit
                AFTER INSERT ON users BEGIN
                INSERT INTO audit_log(table_name, operation, record_id, occurred_at, summary)
                VALUES ('users', 'INSERT', NEW.id, CURRENT_TIMESTAMP, 'Cuenta creada');
            END''')

    @contextmanager
    def transaction(self):
        """Atomic unit of work; any exception rolls back all its statements."""
        if self.is_postgres:
            with self.connection.transaction():
                yield self.connection
            return
        with self.connection:
            yield self.connection

    def execute_query(self, query, params=()):
        if self.is_postgres:
            # Adapta los marcadores y filtros de fecha que ya usa la interfaz
            # para PostgreSQL sin cambiar el código de las pantallas.
            query = query.replace("date(fecha)=date('now')", "fecha::date=CURRENT_DATE")
            query = query.replace("date(fecha) = date('now')", "fecha::date = CURRENT_DATE")
            query = query.replace("?", "%s")
            return self.connection.execute(query, params)
        with self.connection:
            return self.connection.execute(query, params)

    def register_health_record(self, user_id, tipo, valor=None, detalle=None):
        """Guarda un registro: llama al procedimiento en PostgreSQL y realiza
        la operación equivalente en SQLite. En ambos casos el trigger audita."""
        if not tipo or not str(tipo).strip():
            raise ValueError("El tipo de registro es obligatorio")
        with self.transaction() as conn:
            if self.is_postgres:
                conn.execute(
                    "CALL register_health_record(%s,%s,%s,%s)",
                    (user_id, str(tipo).strip(), valor, detalle),
                )
                return conn.execute("SELECT currval(pg_get_serial_sequence('health_records','id'))").fetchone()[0]
            cursor = conn.execute(
                "INSERT INTO health_records(user_id,tipo,valor,detalle) VALUES(?,?,?,?)",
                (user_id, str(tipo).strip(), valor, detalle),
            )
            return cursor.lastrowid

    def replace_daily_records(self, user_id, record_types, records):
        """Reemplaza registros del día en una transacción; si algo falla,
        también se revierte el borrado inicial."""
        if not record_types:
            raise ValueError("Se requiere al menos un tipo de registro")
        placeholder = "%s" if self.is_postgres else "?"
        marks = ",".join(placeholder for _ in record_types)
        with self.transaction() as conn:
            if self.is_postgres:
                with conn.cursor() as cur:
                    cur.execute(
                        f"DELETE FROM health_records WHERE user_id=%s AND fecha::date=CURRENT_DATE AND tipo IN ({marks})",
                        (user_id, *record_types),
                    )
                    cur.executemany(
                        "INSERT INTO health_records(user_id,tipo,valor,detalle) VALUES(%s,%s,%s,%s)",
                        [(user_id, tipo, valor, detalle) for tipo, valor, detalle in records],
                    )
            else:
                conn.execute(
                    f"DELETE FROM health_records WHERE user_id=? AND date(fecha)=date('now') AND tipo IN ({marks})",
                    (user_id, *record_types),
                )
                conn.executemany(
                    "INSERT INTO health_records(user_id,tipo,valor,detalle) VALUES(?,?,?,?)",
                    [(user_id, tipo, valor, detalle) for tipo, valor, detalle in records],
                )

    def backup(self, destination=None):
        """Crea una copia consistente de SQLite aunque la app esté abierta.
        Para PostgreSQL, la guía indica usar pg_dump."""
        if self.is_postgres:
            raise RuntimeError("Para PostgreSQL use pg_dump según docs/DATABASE.md")
        if destination is None:
            root = os.path.dirname(self.db_path)
            folder = os.path.join(root, "backups")
            os.makedirs(folder, exist_ok=True)
            destination = os.path.join(folder, f"healthcore_{datetime.now():%Y%m%d_%H%M%S}.db")
        target = sqlite3.connect(destination)
        try:
            self.connection.backup(target)
        finally:
            target.close()
        return destination