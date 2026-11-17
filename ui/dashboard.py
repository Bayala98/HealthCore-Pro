import customtkinter as ctk
import datetime
from PIL import Image
import os
import random
from core.database import Database

class DashboardView:
    def __init__(self, app):
        self.app = app
        self.user = self.app.current_user
        self.db = Database()
        
        # --- ESTADOS DINÁMICOS ACUMULADOS DESDE LA BD ---
        self.agua_hoy = 0
        self.calorias_hoy = 0
        self.sueno_hoy = "--"
        self.tareas_semanales_bd = []

        tema_elegido = self.user.get("theme", "Dark") 
        if hasattr(self.app, 'set_theme'):
            self.app.set_theme(tema_elegido)
        self.theme = self.app.current_theme

        # Forzamos la lectura fresca de datos antes de pintar los elementos
        self.consultar_metricas_reales_hoy()
        self.build_ui()

    def consultar_metricas_reales_hoy(self):
        """Consume datos de SQLite para sincronizar las pastillas del header y las tareas."""
        try:
            user_id = self.user.get("id")
            
            # 1. Pastilla Agua
            c_agua = self.db.execute_query("SELECT valor FROM health_records WHERE user_id=? AND tipo='Agua' AND date(fecha)=date('now')", (user_id,))
            row_a = c_agua.fetchone()
            self.agua_hoy = int(row_a[0]) if row_a else 0

            # 2. Pastilla Calorías (Nutrición)
            c_cal = self.db.execute_query("SELECT SUM(valor) FROM health_records WHERE user_id=? AND tipo IN ('Desayuno','Almuerzo','Merienda','Cena','Postres/Snacks') AND date(fecha)=date('now')", (user_id,))
            row_c = c_cal.fetchone()
            self.calorias_hoy = int(row_c[0]) if row_c and row_c[0] else 0

            # 3. Pastilla Sueño
            c_sleep = self.db.execute_query("SELECT valor FROM health_records WHERE user_id=? AND tipo='Sueño_Total' AND date(fecha)=date('now')", (user_id,))
            row_s = c_sleep.fetchone()
            self.sueno_hoy = f"{row_s[0]}" if row_s else "--"

            # 4. Cargar Tareas dinámicas desde el calendario de Universidad
            c_tasks = self.db.execute_query("SELECT detalle FROM health_records WHERE user_id=? AND tipo LIKE 'Cal_%'", (user_id,))
            self.tareas_semanales_bd = [r[0] for r in c_tasks.fetchall()]
        except Exception as e:
            print(f"Error sincronizando Dashboard: {e}")

    def build_ui(self):
        self.app.clear_screen()
        self.app.configure(fg_color=self.theme["bg"])

        self.main_scroll = ctk.CTkScrollableFrame(
            self.app, fg_color="transparent",
            scrollbar_button_color=self.theme["primary"],
            scrollbar_button_hover_color=self.theme["btn_hover"]
        )
        self.main_scroll.pack(fill="both", expand=True, padx=20, pady=20)

        # HEADER FRAME
        header_frame = ctk.CTkFrame(self.main_scroll, fg_color=self.theme["card"], corner_radius=20, border_width=1, border_color=self.theme["border"])
        header_frame.pack(fill="x", pady=(0, 20), ipady=15)

        self.render_quick_stats(header_frame) 
        self.render_mascota(header_frame)

        
        #  ALERTA PUSH INTELIGENTE FEMTECH (SÓLO MUJERES)
        
        if self.user.get("genero") == "Mujer":
            # Consultamos el estado FemTech actual en SQLite
            c_fem = self.db.execute_query("SELECT detalle FROM health_records WHERE user_id=? AND tipo='Fem_Modo' ORDER BY id DESC LIMIT 1", (self.user.get("id"),))
            row_f = c_fem.fetchone()
            modo_f = row_f[0] if row_f else "Menstrual"

            push_card = ctk.CTkFrame(self.main_scroll, fg_color="#2D1217", corner_radius=15, border_width=1, border_color="#ED64A6")
            push_card.pack(fill="x", pady=(0, 15), ipady=6)
            
            if modo_f == "Embarazo":
                txt_push = f"🤰 Alerta Gestacional Inteligente de {self.user.get('avatar_name', 'Jaina')}: Tu periodo se encuentra suspendido por gestación activa. Hoy completas una nueva semana según tu FUR. Evita cafeína antes de tus clases de ingeniería para regular tus pulsaciones."
            else:
                txt_push = f"🌸 Nota Predictiva de {self.user.get('avatar_name', 'Jaina')}: Tu periodo menstrual está previsto para dentro de 5 días. He ajustado tu planificador semanal reduciendo las cargas del gimnasio para mitigar dolores lumbares prematuros."
            
            ctk.CTkLabel(push_card, text=txt_push, font=("Roboto", 12, "italic"), text_color=self.theme["text"], wraplength=700, justify="left").pack(padx=20, pady=8, anchor="w")

        # LAYOUT SPLIT REPOSITORIO
        main_layout_split = ctk.CTkFrame(self.main_scroll, fg_color="transparent")
        main_layout_split.pack(fill="both", expand=True, pady=10)
        main_layout_split.grid_columnconfigure(0, weight=7)
        main_layout_split.grid_columnconfigure(1, weight=3)

        modules_frame = ctk.CTkFrame(main_layout_split, fg_color="transparent")
        modules_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        modulos = [
            {"nombre": "Perfil", "icono": "👤", "comando": self.mod_perfil},
            {"nombre": "Nutrición", "icono": "🥗", "comando": self.mod_nutricion},
            {"nombre": "Descanso", "icono": "😴", "comando": self.mod_descanso},
            {"nombre": "Salud Mental", "icono": "🧘‍♀️", "comando": self.mod_salud_mental},
            {"nombre": "Ejercicio", "icono": "🏃‍♀️", "comando": self.mod_ejercicio},
            {"nombre": "Universidad", "icono": "📚", "comando": self.mod_universidad},
            {"nombre": "Estadísticas", "icono": "📊", "comando": self.mod_estadisticas}
        ]

        if self.user.get("genero") == "Mujer":
            modulos.append({"nombre": "Ciclo Menstrual", "icono": "🌸", "comando": self.mod_ciclo_menstrual})

        col, row = 0, 0
        for mod in modulos:
            self.create_module_card(modules_frame, mod["nombre"], mod["icono"], mod["comando"], row, col)
            col += 1
            if col >= 3: col, row = 0, row + 1

        # =========================================================
        # 📋 PANEL LATERAL DINÁMICO: OBJETIVOS REALES ACADÉMICOS
        # =========================================================
        side_panel = ctk.CTkFrame(main_layout_split, fg_color=self.theme["card"], corner_radius=20, border_width=1, border_color=self.theme["border"])
        side_panel.grid(row=0, column=1, sticky="nsew", padx=(10, 0), pady=15)
        
        ctk.CTkLabel(side_panel, text="🎯 Pendientes de la Agenda", font=("Roboto", 16, "bold"), text_color=self.theme["primary"]).pack(anchor="w", padx=20, pady=(20, 10))

        # Si no hay tareas en Universidad, muestra hábitos base
        if not self.tareas_semanales_bd:
            lista_mostrar = ["Tomar 2 Litros de Agua 💧", "Registrar comidas del día", "Completar rutina física"]
        else:
            lista_mostrar = self.tareas_semanales_bd

        for item in lista_mostrar[:6]: # Mostramos máximo 6 para evitar desbordes
            cb = ctk.CTkCheckBox(side_panel, text=item, font=("Roboto", 12), text_color=self.theme["text"], border_color=self.theme["border"], fg_color=self.theme["primary"])
            cb.pack(anchor="w", padx=20, pady=6)

        ctk.CTkFrame(side_panel, height=2, fg_color=self.theme["border"]).pack(fill="x", padx=20, pady=15)
        ctk.CTkLabel(side_panel, text=f"💡 Recordatorio de {self.user.get('avatar_name', 'Jaina')}:", font=("Roboto", 12, "bold"), text_color=self.theme["text_secondary"]).pack(anchor="w", padx=20)
        ctk.CTkLabel(side_panel, text='"Revisa tu planificador en el módulo Universidad para no acumular entregas de última hora. ¡Tú puedes!"', font=("Roboto", 12, "italic"), text_color=self.theme["text"], wraplength=200, justify="left").pack(anchor="w", padx=20, pady=(5, 20))

        ctk.CTkButton(self.main_scroll, text="Cerrar Sesión", fg_color="transparent", border_width=2, border_color="#ff4c4c", text_color="#ff4c4c", hover_color="#331414", command=self.logout).pack(pady=30)

    def render_mascota(self, parent_frame):
        img_size = 90
        avatar_path = self.user.get("avatar_path", "")
        nombre_mascota = self.user.get("avatar_name", "Jaina")
        nombre_usuario = self.user.get("nombre", "Usuario").split()[0]

        img_frame = ctk.CTkFrame(parent_frame, width=img_size+10, height=img_size+10, corner_radius=15, fg_color=self.theme["input_bg"])
        img_frame.pack(side="left", padx=20, pady=10)
        img_frame.pack_propagate(False)

        if avatar_path and os.path.exists(avatar_path):
            pil_img = Image.open(avatar_path)
            ctk_img = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(img_size, img_size))
            ctk.CTkLabel(img_frame, image=ctk_img, text="").place(relx=0.5, rely=0.5, anchor="center")
        else:
            ctk.CTkLabel(img_frame, text="🐾", font=("Arial", 40)).place(relx=0.5, rely=0.5, anchor="center")

        text_frame = ctk.CTkFrame(parent_frame, fg_color="transparent")
        text_frame.pack(side="left", fill="both", expand=True, padx=10, pady=20)
        ctk.CTkLabel(text_frame, text=nombre_mascota, font=("Roboto", 16, "bold"), text_color=self.theme["primary"]).pack(anchor="w")
        
        bubble = ctk.CTkFrame(text_frame, fg_color=self.theme["input_bg"], corner_radius=15)
        bubble.pack(anchor="w", pady=5, fill="x", padx=(0, 20))
        
        diag = f"¡Hola {nombre_usuario}! He sincronizado tus métricas. Tus tareas activas están listas en el panel derecho. 💕"
        ctk.CTkLabel(bubble, text=f'"{diag}"', font=("Roboto", 14, "italic"), text_color=self.theme["text"], justify="left", wraplength=450).pack(padx=15, pady=10, anchor="w")

    def render_quick_stats(self, parent_frame):
        stats_frame = ctk.CTkFrame(parent_frame, fg_color="transparent")
        stats_frame.pack(side="right", padx=30, pady=10, fill="y")

        ahora = datetime.datetime.now()
        dias = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
        meses = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
        fecha_str = f"{dias[ahora.weekday()]} {ahora.day} de {meses[ahora.month-1]}"
        ctk.CTkLabel(stats_frame, text=fecha_str, font=("Roboto", 14, "bold"), text_color=self.theme["text_secondary"]).pack(anchor="e")

        meta = self.user.get("meta_tipo", "Mantenerme")
        ctk.CTkLabel(stats_frame, text=f"Objetivo: {meta}", font=("Roboto", 18, "bold"), text_color=self.theme["primary"]).pack(anchor="e", pady=(5, 10))

        mini_grid = ctk.CTkFrame(stats_frame, fg_color="transparent")
        mini_grid.pack(anchor="e")

        def create_mini_stat(parent, icon, text):
            f = ctk.CTkFrame(parent, fg_color=self.theme["input_bg"], corner_radius=10)
            f.pack(side="left", padx=5)
            ctk.CTkLabel(f, text=f"{icon} {text}", font=("Roboto", 12, "bold"), text_color=self.theme["text"]).pack(padx=10, pady=4)

        # 🔥 REAL Y CRUCIAL: Las pastillas leen directamente los estados calculados de SQLite
        create_mini_stat(mini_grid, "💧", f"{self.agua_hoy}/8")
        create_mini_stat(mini_grid, "🔥", f"{self.calorias_hoy} kcal")
        create_mini_stat(mini_grid, "💤", f"{self.sueno_hoy} hrs")    

    def create_module_card(self, parent, nombre, icono, comando, row, col):
        card = ctk.CTkButton(parent, text="", width=200, height=180, corner_radius=20, fg_color=self.theme["card"], hover_color=self.theme["card_hover"], border_width=1, border_color=self.theme["border"], command=comando)
        card.grid(row=row, column=col, padx=15, pady=15, sticky="nsew")
        ctk.CTkLabel(card, text=icono, font=("Arial", 60)).place(relx=0.5, rely=0.4, anchor="center")
        ctk.CTkLabel(card, text=nombre, font=("Roboto", 16, "bold"), text_color=self.theme["text"]).place(relx=0.5, rely=0.75, anchor="center")

    def mod_perfil(self): self.app.show_profile()
    def mod_nutricion(self): self.app.show_nutrition()
    def mod_descanso(self): self.app.show_sleep()
    def mod_salud_mental(self): self.app.show_mental_health()
    def mod_ejercicio(self): self.app.show_exercise()
    def mod_universidad(self): 
        print("Abriendo ecosistema central: Universidad")
        self.app.show_university() # Conexión al planificador centralizado
        
    def mod_estadisticas(self): 
        print("Abriendo módulo: Estadísticas")
        self.app.show_statistics() # <-- ¡Conexión exitosa!

    def mod_ciclo_menstrual(self): 
        print("Abriendo módulo: Ciclo Menstrual")
        self.app.show_period() # <-- ¡Conexión en caliente completada!

    def logout(self):
        self.app.current_user = None
        self.app.show_login()