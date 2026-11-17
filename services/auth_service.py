import hashlib
import hmac
import secrets
from core.database import Database


def _hash_password(password, salt=None):
    # PBKDF2 ralentiza intentos masivos y el salt hace distinto el hash por usuario.
    salt = salt or secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 310_000)
    return f"pbkdf2_sha256${salt.hex()}${digest.hex()}"


def _verify_password(password, stored):
    # Retorna también si la cuenta usa el formato viejo para migrarla al entrar.
    if stored.startswith("pbkdf2_sha256$"):
        try:
            _, salt_hex, expected = stored.split("$", 2)
            actual = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), bytes.fromhex(salt_hex), 310_000).hex()
            return hmac.compare_digest(actual, expected), False
        except (ValueError, TypeError):
            return False, False
    # Cuenta antigua: se compara una última vez en texto plano y luego se actualiza.
    return hmac.compare_digest(password, stored), True

class AuthService:
    @staticmethod
    def register_user(user_data):
        # El servicio recibe el formulario y almacena el hash, nunca la clave directa.
        db = Database()
        query = '''INSERT INTO users (
            usuario, correo, password, nombre, apellido, edad, genero, 
            estatura, peso, meta_tipo, meta_kg, avatar_path, avatar_category, avatar_name, theme
        ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)'''
        
        # Extraemos 'theme' (que es el nombre que usamos en la tabla)
        params = (
            user_data['usuario'], user_data['correo'], _hash_password(user_data['password']),
            user_data['nombre'], user_data['apellido'], user_data['edad'], 
            user_data['genero'], user_data['estatura'], user_data['peso'], 
            user_data['meta_tipo'], user_data['meta_kg'], user_data['avatar_path'], 
            user_data['avatar_category'], user_data['avatar_name'], user_data['theme']
        )
        
        try:
            db.execute_query(query, params)
            return True, "Registrado"
        except Exception as e:
            return False, str(e)

    @staticmethod
    def login_user(u, p):
        db = Database()
        # 1. Limpiamos espacios accidentales
        u_clean = u.strip()
        p_clean = p.strip()
        
        # Busca por usuario o correo; la contraseña se verifica en Python con PBKDF2.
        cursor = db.execute_query("SELECT * FROM users WHERE usuario=? OR correo=?", (u_clean, u_clean))
        
        # 3. AQUÍ ESTÁ LA CORRECCIÓN: fetchone() todo pegado y sobre el cursor
        row = cursor.fetchone()
        
        if row:
            # Convertimos la fila en un diccionario para la app
            columns = [desc[0] for desc in cursor.description]
            user = dict(zip(columns, row))
            valid, was_legacy = _verify_password(p_clean, user.get("password") or "")
            if not valid:
                return False, None
            if was_legacy:
                # Actualización silenciosa de cuentas creadas antes del cambio.
                db.execute_query("UPDATE users SET password=? WHERE id=?", (_hash_password(p_clean), user["id"]))
            # La contraseña no se envía a la sesión de interfaz.
            user.pop("password", None)
            return True, user
        return False, None

    @staticmethod
    def get_user_by_email(correo):
        """Función necesaria para los botones de Olvidé mi contraseña"""
        db = Database()
        cursor = db.execute_query("SELECT * FROM users WHERE correo=?", (correo.strip(),))
        row = cursor.fetchone()
        
        if row:
            columns = [desc[0] for desc in cursor.description]
            user = dict(zip(columns, row))
            user.pop("password", None)
            return user
        return None
