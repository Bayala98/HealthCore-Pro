import customtkinter as ctk


class MascotPanel:

    def __init__(self, app, container):

        self.app = app
        self.container = container

        self.build()


    # ==========================================
    # OBTENER MASCOTA (SIN MODIFICAR VALORES)
    # ==========================================
    def get_mascot(self):

        if not self.app.current_user:
            return "🐾"

        # 🔥 IMPORTANTE: usamos lo que ya existe
        return self.app.current_user.get("mascota", "🐾")


    # ==========================================
    # IA BASADA EN HEALTH ENGINE
    # ==========================================
    def get_message(self):

        engine = self.app.engine
        status = engine.get_global_status()

        name = self.app.current_user.get("nombre", "usuario")

        score = status["score"]

        # 🧠 comportamiento inteligente
        if score >= 80:
            mood = "Todo va excelente hoy, sigue así 💚"
        elif score >= 60:
            mood = "Vas bien, pero podemos mejorar algunos hábitos 💛"
        elif score >= 40:
            mood = "Ojo, tu cuerpo necesita más atención ⚠️"
        else:
            mood = "Necesito ayudarte a recuperar tu salud urgente 🚨"

        return f"""
{self.get_mascot()} {name}

{mood}

📊 Score de salud: {score}/100
"""


    # ==========================================
    # UI
    # ==========================================
    def build(self):

        frame = self.container

        ctk.CTkLabel(
            frame,
            text="Compañero IA",
            font=("Arial", 16, "bold")
        ).pack(pady=10)

        self.label = ctk.CTkLabel(
            frame,
            text=self.get_message(),
            wraplength=220,
            justify="left"
        )
        self.label.pack(pady=20)

        ctk.CTkButton(
            frame,
            text="💡 Consejo IA",
            command=self.show_tip
        ).pack(pady=5)

        ctk.CTkButton(
            frame,
            text="🔄 Actualizar",
            command=self.refresh
        ).pack(pady=5)


    # ==========================================
    # CONSEJOS DEL ENGINE
    # ==========================================
    def show_tip(self):

        recs = self.app.engine.get_recommendations()

        self.label.configure(text="💡 " + recs[0])


    def refresh(self):

        self.label.configure(text=self.get_message())