import os
import sys
from dotenv import load_dotenv

# Calcula dónde está ubicado el programa (funciona tanto en Python como en .exe)
if getattr(sys, "frozen", False):
    ruta_base = os.path.dirname(sys.executable)
else:
    ruta_base = os.path.dirname(os.path.abspath(__file__))

# Carga las variables del archivo .env al sistema operativo
load_dotenv(os.path.join(ruta_base, ".env"), override=True)

import customtkinter as ctk
from tkinter import messagebox

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        # ==========================================
        # 1. CONFIGURACIÓN DE VENTANA (UX PREMIUM)
        # ==========================================
        self.title("Health Core Pro - Ecosistema de Salud")
        
        # Dimensiones iniciales y mínimas para proteger el layout responsivo
        app_width = 1100
        app_height = 700
        self.minsize(900, 600)

        # Magia UX: Centrar la ventana matemáticamente en la pantalla del usuario
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = int((screen_width / 2) - (app_width / 2))
        y = int((screen_height / 2) - (app_height / 2))
        self.geometry(f"{app_width}x{app_height}+{x}+{y}")

        # ==========================================
        # 2. ESTADO GLOBAL DE LA APLICACIÓN
        # ==========================================
        self.current_user = None
        self.current_view = None

        # DICCIONARIO MAESTRO DE TEMAS
        self.THEMES = {
            "Dark": {
                "bg": "#121212", "card": "#1E1E1E", "card_hover": "#2C2C2C",
                "primary": "#4CAF50", "btn_hover": "#388E3C",
                "text": "#FFFFFF", "text_secondary": "#B3B3B3",
                "input_bg": "#2C2C2C", "border": "#333333"
            },
            "Light": {
                "bg": "#F5F5F5", "card": "#FFFFFF", "card_hover": "#E0E0E0",
                "primary": "#4CAF50", "btn_hover": "#388E3C",
                "text": "#000000", "text_secondary": "#666666",
                "input_bg": "#F0F0F0", "border": "#CCCCCC"
            },
            "Morado": {
                "bg": "#1D1A27", "card": "#262335", "card_hover": "#322E45",
                "primary": "#9D4EDD", "btn_hover": "#7B2CBF",
                "text": "#FFFFFF", "text_secondary": "#C8B6FF",
                "input_bg": "#322E45", "border": "#5A189A"
            },
            "Azul": {
                "bg": "#0B192C", "card": "#1A365D", "card_hover": "#2A4365",
                "primary": "#3182CE", "btn_hover": "#2B6CB0",
                "text": "#FFFFFF", "text_secondary": "#A0AEC0",
                "input_bg": "#2D3748", "border": "#4A5568"
            },
            "Verde": {
                "bg": "#0F1A14", "card": "#162A1F", "card_hover": "#1E3D2F",
                "primary": "#2ECC71", "btn_hover": "#27AE60",
                "text": "#FFFFFF", "text_secondary": "#A9DFBF",
                "input_bg": "#1E3D2F", "border": "#27AE60"
            },
            "Rosado": {
                "bg": "#1A1016", "card": "#2A1822", "card_hover": "#3D2030",
                "primary": "#E91E63", "btn_hover": "#C2185B",
                "text": "#FFFFFF", "text_secondary": "#F8BBD0",
                "input_bg": "#3D2030", "border": "#C2185B"
            }
        }
        
        # Iniciar la aplicación con el tema por defecto
        self.set_theme("Dark")

        # 3. Arrancar la aplicación mostrando la vista de Login
        self.show_login()

    # ==========================================
    # LÓGICA DE TEMAS
    # ==========================================
    def set_theme(self, theme_name):
        """Actualiza la paleta de colores global de la aplicación."""
        if theme_name in self.THEMES:
            self.current_theme = self.THEMES[theme_name]
            # Sincronizamos con el motor interno de CustomTkinter
            if theme_name == "Light":
                ctk.set_appearance_mode("light")
            else:
                ctk.set_appearance_mode("dark")

    # ==========================================
    # RUTEO Y LIMPIEZA DE PANTALLA
    # ==========================================
    def clear_screen(self):
        """Destruye todos los widgets para pintar la nueva vista limpiamente."""
        for widget in self.winfo_children():
            widget.destroy()

    # ==========================================
    # VISTAS (ENRUTADOR CENTRAL)
    # ==========================================
    def show_login(self):
        self.clear_screen()
        # Importación local para evitar dependencias circulares
        from auth.login import LoginView
        self.current_view = LoginView(self)

    def show_register(self):
        self.clear_screen()
        from auth.register import RegisterView
        self.current_view = RegisterView(self)

    def show_dashboard(self):
        self.clear_screen()
        
        # Buscador automático de rutas
        try:
            from dashboard import DashboardView  # Intenta buscarlo junto a main.py
        except ModuleNotFoundError:
            try:
                from ui.dashboard import DashboardView # Intenta buscarlo en la carpeta 'ui'
            except ModuleNotFoundError:
                from auth.dashboard import DashboardView # Intenta buscarlo en la carpeta 'auth'
                
        self.current_view = DashboardView(self)

    def show_profile(self):
        self.clear_screen()
        
        # Buscador automático de rutas para el perfil
        try:
            from profile_view import ProfileView  # Si está en la raíz
        except ModuleNotFoundError:
            try:
                from ui.profile_view import ProfileView  # Si está en la carpeta 'ui'
            except ModuleNotFoundError:
                from auth.profile_view import ProfileView  # Si está en la carpeta 'auth'
                
        self.current_view = ProfileView(self)

    def show_nutrition(self):
        self.clear_screen()
        
        # Buscador automático de rutas para nutrición
        try:
            from nutrition_view import NutritionView  # Si está en la raíz
        except ModuleNotFoundError:
            try:
                from ui.nutrition_view import NutritionView  # Si está en la carpeta 'ui'
            except ModuleNotFoundError:
                from auth.nutrition_view import NutritionView  # Si está en la carpeta 'auth'
                
        self.current_view = NutritionView(self)

    def show_sleep(self):
        self.clear_screen()
        
        try:
            from sleep_view import SleepView  # Si está en la raíz
        except ModuleNotFoundError:
            from ui.sleep_view import SleepView  # Si está en ui/
            
        self.current_view = SleepView(self)

    def show_mental_health(self):
        self.clear_screen()
        try:
            from mental_health_view import MentalHealthView
        except ModuleNotFoundError:
            from ui.mental_health_view import MentalHealthView
        self.current_view = MentalHealthView(self)

    def show_exercise(self):
        self.clear_screen()
        try:
            from exercise_view import ExerciseView
        except ModuleNotFoundError:
            from ui.exercise_view import ExerciseView
        self.current_view = ExerciseView(self)
    
    def show_university(self):
        self.clear_screen()
        try:
            from university_view import UniversityView
        except ModuleNotFoundError:
            from ui.university_view import UniversityView
        self.current_view = UniversityView(self)

    def show_statistics(self):
        self.clear_screen()
        try:
            from statistics_view import StatisticsView
        except ModuleNotFoundError:
            from ui.statistics_view import StatisticsView
        self.current_view = StatisticsView(self)

    def show_period(self):
        self.clear_screen()
        try:
            from period_view import PeriodView
        except ModuleNotFoundError:
            from ui.period_view import PeriodView
        self.current_view = PeriodView(self)

if __name__ == "__main__":
    app = App()
    app.mainloop()