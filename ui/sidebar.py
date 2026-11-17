import customtkinter as ctk


class SidebarView:

    def __init__(self, app):

        self.app = app
        self.theme = app.current_theme

        self.build_ui()


    # ==========================================
    # SIDEBAR PRINCIPAL
    # ==========================================
    def build_ui(self):

        self.frame = ctk.CTkFrame(
            self.app,
            width=200,
            fg_color=self.theme["primary"]
        )
        self.frame.pack(side="left", fill="y")

        # título
        ctk.CTkLabel(
            self.frame,
            text="HealthCore",
            font=("Verdana", 18, "bold"),
            text_color="white"
        ).pack(pady=20)

        # botones navegación
        self.create_btn("🏠 Home", self.app.show_home)
        self.create_btn("👤 Perfil", self.app.show_profile)
        self.create_btn("🍎 Nutrición", self.app.show_nutrition)
        self.create_btn("🏃 Deportes", self.app.show_sports)
        self.create_btn("💙 Salud Mental", self.app.show_mental_health)
        self.create_btn("📊 Estadísticas", self.app.show_stats)
        self.create_btn("🩷 Ciclo", self.app.show_cycle)
        self.create_btn("😴 Sueño", self.app.show_sleep)


    # ==========================================
    # BOTÓN REUTILIZABLE
    # ==========================================
    def create_btn(self, text, command):

        ctk.CTkButton(
            self.frame,
            text=text,
            fg_color="transparent",
            hover_color="#444",
            command=command
        ).pack(fill="x", pady=5, padx=10)