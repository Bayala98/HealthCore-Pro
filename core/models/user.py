class User:

    def __init__(self, data):

        self.nombre = data.get("nombre")
        self.apellido = data.get("apellido")
        self.edad = data.get("edad")
        self.peso = data.get("peso")
        self.estatura = data.get("estatura")