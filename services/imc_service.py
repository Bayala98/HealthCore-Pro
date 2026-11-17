# =====================================================
# IMC SERVICE - HEALTHCORE
# Cálculo puro (sin lógica de decisión)
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