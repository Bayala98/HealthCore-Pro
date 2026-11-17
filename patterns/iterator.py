class User:
    """
    MODELO CENTRAL DEL SISTEMA HEALTHCORE
    Contiene toda la información del usuario
    """

    def __init__(self):
        self.name = ""
        self.last_name = ""
        self.age = 0
        self.height = 0.0
        self.weight = 0.0
        self.gender = ""
        self.pet_name = ""
        self.profile_image = None

        # datos de salud
        self.mood_history = []
        self.food_history = []
        self.sleep_history = []