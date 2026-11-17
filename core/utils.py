# =====================================================
# UTILS - HEALTHCORE
# Funciones reutilizables globales
# =====================================================

from datetime import datetime


# =====================================================
# VALIDAR NÚMEROS (evita crashes en inputs)
# =====================================================
def safe_float(value, default=0.0):

    try:
        return float(value)
    except:
        return default


def safe_int(value, default=0):

    try:
        return int(value)
    except:
        return default


# =====================================================
# FORMATEO DE FECHA
# =====================================================
def now_time():

    return datetime.now().strftime("%Y-%m-%d %H:%M")


def now_date():

    return datetime.now().strftime("%Y-%m-%d")


# =====================================================
# CALCULAR IMC (UTILIDAD BASE, NO LÓGICA DE DECISIÓN)
# =====================================================
def calculate_imc(weight, height):

    try:
        weight = float(weight)
        height = float(height)

        if height <= 0:
            return None

        return weight / (height ** 2)

    except:
        return None


# =====================================================
# CLASIFICAR IMC (SOLO TEXTO, NO DECISIONES MÉDICAS)
# =====================================================
def imc_label(imc):

    if imc is None:
        return "No disponible"

    if imc < 18.5:
        return "Bajo peso"

    elif imc < 25:
        return "Normal"

    elif imc < 30:
        return "Sobrepeso"

    else:
        return "Obesidad"


# =====================================================
# LIMPIAR TEXTO DE INPUTS
# =====================================================
def clean_text(text):

    if not text:
        return ""

    return text.strip()