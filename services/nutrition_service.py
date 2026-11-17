# =====================================================
# NUTRITION SERVICE - HEALTHCORE
# Manejo básico de datos de alimentación
# =====================================================


def format_meal(name, calories, type_food):

    return {
        "name": name,
        "calories": float(calories),
        "type": type_food
    }