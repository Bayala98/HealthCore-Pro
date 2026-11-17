# Base de datos, seguridad y operación remota

La aplicación mantiene SQLite como configuración predeterminada. El diseño de la interfaz no cambia. Para una instalación multiusuario o acceso remoto, usa PostgreSQL: SQLite no ofrece usuarios de base de datos, procedimientos almacenados ni un servidor de conexiones remoto.

## Lo que se incorporó

- Triggers de SQLite y PostgreSQL que registran INSERT, UPDATE y DELETE en `health_records` en `audit_log`.
- Operaciones atómicas con rollback (`Database.transaction`) y helpers para insertar y reemplazar lotes diarios.
- Procedimiento PostgreSQL `register_health_record`, llamado por la aplicación cuando se conecta a PostgreSQL; en SQLite el helper Python ofrece la misma operación transaccional y activa el trigger.
- Función PostgreSQL `calculate_bmi`.
- Contraseñas almacenadas con PBKDF2-HMAC-SHA256. Las cuentas antiguas se actualizan al hash al iniciar sesión correctamente. SQLite no cifra el archivo de datos; limita su acceso a nivel de sistema operativo.
- Copias SQLite consistentes en caliente con `Database().backup()`, guardadas por defecto en `backups/`.

## Configurar PostgreSQL para acceso remoto

1. Instala dependencias: `python -m pip install -r requirements.txt`.
2. Crea una base de datos PostgreSQL y ejecuta `database/postgresql_schema.sql` como administrador.
3. Crea el rol de aplicación con permisos mínimos usando las instrucciones comentadas al final del SQL. Define una contraseña larga y única.
4. Configura PostgreSQL y su firewall para aceptar conexiones únicamente desde las IP de los equipos cliente. Activa TLS en el servidor.
5. En cada equipo cliente configura la variable de entorno `HEALTHCORE_DATABASE_URL` con una URL que incluya `sslmode=require`, por ejemplo `postgresql://healthcore_app:SECRETO@servidor:5432/healthcore?sslmode=require`. En PowerShell puedes definirla para la sesión actual con `$env:HEALTHCORE_DATABASE_URL = 'postgresql://healthcore_app:SECRETO@servidor:5432/healthcore?sslmode=require'`. No guardes la contraseña en el repositorio.
6. Inicia la aplicación normalmente. Sin esa variable, usa el archivo local `healthcore.db`.

En una instalación local sin SSL, usa `sslmode=disable` en la URL administrativa durante la migración y en la URL de `healthcore_app` para probar en localhost. Para acceso remoto con TLS habilitado, usa `sslmode=require`. El proyecto toma sslmode de la URL. PostgreSQL no sustituye la autenticación de HealthCore: el rol `healthcore_app` es una identidad técnica compartida por la aplicación. Cada usuario final sigue autenticándose con sus credenciales de HealthCore. No expongas PostgreSQL directamente a Internet; restringe red, usa TLS y secretos administrados.

## Migrar los datos SQLite a PostgreSQL

1. Detén la aplicación y conserva una copia del archivo `healthcore.db`.
2. Prepara PostgreSQL y ejecuta `database/postgresql_schema.sql`.
3. Define `HEALTHCORE_DATABASE_URL` apuntando a la base destino con el usuario administrador/propietario para el paso de migración (el script ajusta las secuencias de IDs).
4. Ejecuta `python database/migrate_sqlite_to_postgresql.py healthcore.db`.
5. Comprueba los conteos de usuarios y registros, prueba inicio de sesión y datos de salud; luego deja configurada la URL en los clientes.

La migración conserva IDs y credenciales almacenadas. Las contraseñas heredadas en texto plano se convierten a hash al primer inicio de sesión correcto. La migración es idempotente por ID; revisa duplicados de usuario/correo si la base destino ya tenía datos. Después de migrar, configura los clientes con el rol limitado `healthcore_app`, nunca con la URL administrativa.

## Backups y restauración

SQLite: invoca `Database().backup()` desde una tarea administrativa. Restaura con la aplicación cerrada, copiando el archivo de respaldo sobre `healthcore.db`.

PostgreSQL: agenda `pg_dump --format=custom --file=healthcore.dump "$env:HEALTHCORE_DATABASE_URL"` en el servidor de respaldo. Restaura con `pg_restore --clean --if-exists --dbname="$env:HEALTHCORE_DATABASE_URL" healthcore.dump`. Guarda las copias cifradas, limita quién puede leerlas y practica restauraciones periódicas.

## Límites

Las cuentas y permisos son propios de PostgreSQL; SQLite no implementa GRANT/REVOKE. La aplicación de escritorio con PostgreSQL remoto es adecuada para una red controlada. Para clientes distribuidos por Internet, lo recomendado es interponer una API con autenticación por usuario y no distribuir credenciales de base de datos en los equipos.
