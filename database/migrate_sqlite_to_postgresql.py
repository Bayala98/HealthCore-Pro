"""Copia datos SQLite a una base PostgreSQL que ya tenga el esquema instalado.

Uso: definir HEALTHCORE_DATABASE_URL y pasar la ruta a healthcore.db.
"""
import os
import sqlite3
import sys

import psycopg


def migrate(source_path, database_url):
    # Abre ambas bases; psycopg confirma la copia completa o revierte si falla.
    source = sqlite3.connect(source_path)
    source.row_factory = sqlite3.Row
    target = psycopg.connect(database_url)
    try:
        with target:
            with target.cursor() as cur:
                for table, columns in (
                    ("users", "id, usuario, correo, password, nombre, apellido, edad, genero, estatura, peso, meta_tipo, meta_kg, avatar_path, avatar_category, avatar_name, theme"),
                    ("health_records", "id, user_id, tipo, valor, detalle, fecha"),
                ):
                    # Mantiene IDs originales; ON CONFLICT permite reanudar la copia.
                    rows = source.execute(f"SELECT {columns} FROM {table}").fetchall()
                    if rows:
                        names = columns.split(", ")
                        placeholders = ",".join("%s" for _ in names)
                        cur.executemany(
                            f"INSERT INTO {table} ({columns}) VALUES ({placeholders}) ON CONFLICT (id) DO NOTHING",
                            [tuple(row[name] for name in names) for row in rows],
                        )
                    cur.execute(
                        # Alinea el siguiente ID automático con el máximo importado.
                        f"SELECT setval(pg_get_serial_sequence('{table}','id'), GREATEST(COALESCE((SELECT MAX(id) FROM {table}), 1), 1), EXISTS(SELECT 1 FROM {table}))"
                    )
        return {table: source.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
                for table in ("users", "health_records")}
    finally:
        source.close()
        target.close()


if __name__ == "__main__":
    if len(sys.argv) != 2 or not os.environ.get("HEALTHCORE_DATABASE_URL"):
        raise SystemExit("Uso: python database/migrate_sqlite_to_postgresql.py healthcore.db (defina HEALTHCORE_DATABASE_URL)")
    print(migrate(sys.argv[1], os.environ["HEALTHCORE_DATABASE_URL"]))
