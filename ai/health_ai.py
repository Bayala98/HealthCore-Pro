class HealthAI:

    def __init__(self, gemini_client):
        self.ai = gemini_client

    def chat(self, user_message: str) -> str:
        prompt = f"""
Eres HealthCore AI, un asistente de salud y bienestar.

Tu función:
- Dar consejos de nutrición
- Recomendar ejercicios
- Apoyo emocional
- Motivación diaria
- Acompañamiento tipo mascota virtual

Usuario: {user_message}

Responde de forma clara, humana y motivadora.
"""
        return self.ai.ask(prompt)

    def nutrition_tip(self) -> str:
        return self.ai.ask("Dame un consejo corto de nutrición saludable diario.")

    def workout_tip(self) -> str:
        return self.ai.ask("Recomienda un ejercicio sencillo para hoy en casa.")

    def emotional_support(self) -> str:
        return self.ai.ask("Dame un mensaje de apoyo emocional motivador y humano.")