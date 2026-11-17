# Explicación de HealthCore y de lo agregado

Esta guía recorre lo que hace el programa y relaciona cada requisito solicitado con los archivos que lo implementan. Las pantallas y el diseño no se modificaron.

## Cómo funciona la aplicación

Al iniciar `main.py`, se crea la ventana principal `App`, se configuran los temas y se muestra el login. Las vistas están en `auth/` y `ui/`. Las vistas dibujan la interfaz y recogen lo que escribe el usuario; no deberían contener reglas de conexión ni credenciales de la base.

La ruta usual de una operación es:

```text
Vista (auth/ o ui/) -> servicio (services/) -> Database -> SQLite o PostgreSQL
```

Por ejemplo, al registrarse, `auth/register.py` reúne los campos del formulario, `services/auth_service.py` prepara y valida los datos de cuenta, y `core/database.py` ejecuta el INSERT. Al iniciar sesión se repite el flujo en sentido contrario: servicio consulta la cuenta, verifica la clave y devuelve el perfil sin la contraseña.

## ¿Qué significa “modelo” aquí?

`core/models/user.py` es una clase sencilla para representar algunos atributos de una persona (nombre, apellido, edad, peso y estatura). No es quien crea ni consulta las tablas. El esquema de datos se define en SQL: para SQLite se crea desde `core/database.py`; para PostgreSQL se declara en `database/postgresql_schema.sql`.

Las tablas principales son:

- `users`: cuenta, datos del perfil, preferencias y hash de contraseña.
- `health_records`: mediciones o eventos de salud. `user_id` relaciona cada fila con una cuenta.
- `audit_log`: bitácora técnica de ciertas operaciones, no una pantalla de historial médico.

## Cómo trabaja `core/database.py`

`Database` mantiene una instancia compartida para que las pantallas reutilicen una conexión. Si existe `HEALTHCORE_DATABASE_URL`, conecta a PostgreSQL usando el `sslmode` indicado en la URL (por ejemplo, `disable` para localhost sin TLS y `require` para un servidor remoto con TLS). Si no existe, abre `healthcore.db` con SQLite y crea las tablas y triggers locales. Para conectar a PostgreSQL primero hay que instalar y preparar el servidor; la variable por sí sola no crea el servidor ni importa datos.

- `execute_query(...)`: ejecuta una consulta parametrizada. Los parámetros evitan concatenar directamente texto ingresado en SQL. Para PostgreSQL adapta `?` a `%s` y los filtros de fecha usados por las pantallas.
- `transaction()`: agrupa consultas; ante una excepción se revierten los cambios del grupo.
- `replace_daily_records(...)`: borra ciertos tipos de hoy e inserta sus nuevos valores en una transacción. Si uno de los pasos falla, también se deshace el borrado.
- `register_health_record(...)`: ejemplo de operación de inserción. En PostgreSQL llama al procedimiento; en SQLite hace el INSERT equivalente. En ambos casos el trigger registra el cambio.
- `backup(...)`: con SQLite crea una copia coherente en `backups/` (o en la ruta que se indique). No implementa una agenda automática.

Los formularios de sueño (`ui/sleep_view.py`), salud mental (`ui/mental_health_view.py`) y agua (`ui/nutrition_view.py`) ahora usan `replace_daily_records` para que sus guardados agrupados no queden a medias.

## Inicio de sesión y contraseñas

En `services/auth_service.py`, `_hash_password` calcula un hash PBKDF2-HMAC-SHA256 con salt aleatorio. El salt no es una clave secreta: permite que dos contraseñas iguales no produzcan el mismo hash. `_verify_password` compara el hash al iniciar sesión. Si detecta una cuenta antigua con clave de texto plano y la persona entra correctamente, guarda un hash nuevo. El perfil devuelto a la aplicación no incluye la columna `password`.

`auth/login.py` solo recoge los campos, llama a `AuthService` y decide si muestra un error o abre el panel. Se quitó el mensaje de depuración que imprimía la contraseña.

## Requisitos que pidió el profesor

| Requisito | Qué se agregó | Estado y límite práctico |
|---|---|---|
| Triggers | SQLite crea triggers para altas, cambios y borrados de `health_records`, y altas de usuario. PostgreSQL tiene un trigger de auditoría para las tres operaciones sobre registros de salud. | Funcionan automáticamente al cambiar esas tablas. Los de usuarios registran solo el alta, no actualización ni borrado. |
| Procedimientos almacenados | PostgreSQL incluye `register_health_record`. El esquema local SQLite no soporta procedimientos; `Database.register_health_record` ofrece la operación equivalente en Python. | El procedimiento está disponible y lo llama ese método. Los formularios usan operaciones de servicio/SQL agrupadas, no todos llaman el procedimiento individual. |
| Triggers combinados con procedimientos | El procedimiento PostgreSQL inserta en `health_records`; el trigger AFTER INSERT de esa tabla añade automáticamente la auditoría. | La combinación ocurre cuando se llama `Database.register_health_record` en modo PostgreSQL. En SQLite, el INSERT equivalente también activa su trigger. |
| Funciones y transacciones | `calculate_bmi` está definida como función SQL en PostgreSQL. `transaction` y `replace_daily_records` agrupan cambios; sueño, salud mental y agua usan el reemplazo atómico. | La función SQL del IMC está creada, pero la interfaz actual no la invoca; el IMC que ya mostraba la aplicación sigue su lógica existente. |
| Usuarios y permisos | El SQL incluye ejemplos comentados para crear `healthcore_app` y concederle permisos. | No se crea ese usuario automáticamente. Un administrador debe ejecutar las instrucciones, cambiar la contraseña de ejemplo y usar el rol limitado en los equipos cliente. SQLite no tiene roles GRANT/REVOKE. |
| Login remoto | `Database` puede conectar al PostgreSQL configurado en `HEALTHCORE_DATABASE_URL`, manteniendo el login de usuario de HealthCore. TLS se exige en la conexión. | Hace falta instalar/configurar el servidor, crear el esquema, abrir acceso de red restringido y definir el secreto en cada equipo. Sin URL se usa SQLite local. |
| Backups | `Database.backup()` crea una copia en caliente de SQLite. La guía documenta `pg_dump`/`pg_restore` para PostgreSQL. | El respaldo SQLite se ejecuta llamando al método; no hay botón ni programación automática. PostgreSQL requiere ejecutar o programar sus herramientas de respaldo. |
| Migración de motor | `database/migrate_sqlite_to_postgresql.py` copia usuarios y registros, conservando IDs. | Primero se aplica `database/postgresql_schema.sql`; la migración debe correrse con una conexión propietaria/administradora. Luego los clientes usan el rol limitado. |

## Preparar PostgreSQL y migrar

1. Instalar dependencias del proyecto (`psycopg` está añadido a `requirements.txt`).
2. Crear la base y ejecutar `database/postgresql_schema.sql` como administrador.
3. Habilitar las instrucciones comentadas de rol/permisos con una contraseña propia y restringir el acceso de red.
4. Hacer una copia del archivo SQLite. Definir temporalmente `HEALTHCORE_DATABASE_URL` con el usuario propietario y ejecutar `python database/migrate_sqlite_to_postgresql.py healthcore.db`.
5. Comprobar conteos y login. Luego configurar en los clientes la URL con el rol `healthcore_app`, nunca con la cuenta administrativa.

Las contraseñas antiguas se copian tal cual durante la migración; se transforman en hash cuando su dueño inicia sesión correctamente. La migración no automatiza la creación del servidor, el firewall, los respaldos ni la verificación funcional final.

## Archivos clave

- `main.py`: crea la ventana y navega entre vistas.
- `auth/login.py`, `auth/register.py`: interfaz de acceso y registro.
- `services/auth_service.py`: registro y verificación de cuentas.
- `core/database.py`: conexión, consultas, triggers SQLite, transacciones y respaldo SQLite.
- `core/models/user.py`: representación simple de algunos datos de usuario.
- `database/postgresql_schema.sql`: tablas, trigger, función, procedimiento y ejemplos de permisos PostgreSQL.
- `database/migrate_sqlite_to_postgresql.py`: copia datos desde SQLite al esquema PostgreSQL preparado.
- `docs/DATABASE.md`: instrucciones operativas para conexión remota, migración y respaldos.
