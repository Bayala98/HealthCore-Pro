import customtkinter as ctk
from tkinter import messagebox
from PIL import Image
import os
import random
import time
import threading
import webbrowser
from core.database import Database

class ExerciseView:
    def __init__(self, app):
        print("\n--- INICIANDO MOTOR DE DEPORTE & MULTIMEDIA AVANZADO ---")
        try:
            self.app = app
            self.user = self.app.current_user
            self.theme = self.app.current_theme
            self.db = Database()
            
            # --- ESTADOS DE ACTIVIDAD FÍSICA ---
            self.smartwatch_activo = False
            self.calorias_quemadas = 0
            self.bpm_ejercicio = 0
            self.minutos_entrenados = 0
            
            # --- CONTROL DEL TEMPORIZADOR ---
            self.cronometro_corriendo = False
            self.segundos_crono = 0
            
            # --- ESTADO DE SPOTIFY SIMULADO / REAL ---
            self.spotify_conectado = False
            self.cancion_actual = "Ninguna - Desconectado"
            self.reproduciendo_spotify = False
            self.lista_canciones = [
                "Lose Yourself - Eminem 🏃‍♂️",
                "Eye of the Tiger - Survivor 🐯",
                "Till I Collapse - Eminem 🔥",
                "Stronger - Kanye West ⚡",
                "Harder, Better, Faster, Stronger - Daft Punk 🤖"
            ]
            
            # --- VARIABLES REACTIVAS PARA BITÁCORA DE CARGAS ---
            self.sv_series = ctk.StringVar(value="4")
            self.sv_reps = ctk.StringVar(value="12")
            self.sv_peso = ctk.StringVar(value="20") 

            self.app.clear_screen()
            self.main_scroll = ctk.CTkScrollableFrame(
                self.app, fg_color="transparent",
                scrollbar_button_color=self.theme["primary"],
                scrollbar_button_hover_color=self.theme["btn_hover"]
            )
            self.main_scroll.pack(fill="both", expand=True, padx=20, pady=20)

            self.cargar_datos_deporte_bd()
            self.build_ui()
            print("✅ MÓDULO DE DEPORTE MULTIMEDIA DESPLEGADO")
        except Exception as e:
            print(f"❌ ERROR CRÍTICO EN DEPORTE V2: {e}")

    def cargar_datos_deporte_bd(self):
        try:
            user_id = self.user.get("id")
            cursor = self.db.execute_query(
                "SELECT tipo, valor FROM health_records WHERE user_id = ? AND tipo IN ('Deporte_Mins', 'Deporte_Calorias') AND date(fecha) = date('now')",
                (user_id,)
            )
            for row in cursor.fetchall():
                tipo, valor = row
                if tipo == "Deporte_Mins": self.minutos_entrenados = int(valor)
                if tipo == "Deporte_Calorias": self.calorias_quemadas = int(valor)
        except Exception as e:
            print(f"Error leyendo BD Deporte: {e}")

    def build_ui(self):
        for widget in self.main_scroll.winfo_children():
            widget.destroy()

        self.app.configure(fg_color=self.theme["bg"])

        # BOTÓN VOLVER
        ctk.CTkButton(
            self.main_scroll, text="⬅ Volver al Menú", width=120, height=30,
            font=("Roboto", 12, "bold"), fg_color="transparent",
            text_color=self.theme["text_secondary"], hover_color=self.theme["card_hover"],
            command=self.app.show_dashboard
        ).pack(anchor="w", padx=10, pady=(0, 10))

        # LAYOUT SPLIT
        split_layout = ctk.CTkFrame(self.main_scroll, fg_color="transparent")
        split_layout.pack(fill="both", expand=True)
        split_layout.grid_columnconfigure(0, weight=4)
        split_layout.grid_columnconfigure(1, weight=6)

        # =========================================================
        # 👈 COLUMNA IZQUIERDA: HARDWARE, SPOTIFY Y MASCOTA
        # =========================================================
        left_column = ctk.CTkFrame(split_layout, fg_color="transparent")
        left_column.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        # Tarjeta 1: Smartwatch
        iot_card = ctk.CTkFrame(left_column, fg_color=self.theme["card"], corner_radius=20, border_width=1, border_color=self.theme["border"])
        iot_card.pack(fill="x", pady=5, ipady=6)
        ctk.CTkLabel(iot_card, text="⌚ Monitor Smartwatch", font=("Roboto", 14, "bold"), text_color=self.theme["primary"]).pack()
        self.lbl_calorias = ctk.CTkLabel(iot_card, text=f"🔥 {self.calorias_quemadas} kcal | ⏳ {self.minutos_entrenados} mins", font=("Roboto", 12, "bold"))
        self.lbl_calorias.pack()
        self.lbl_bpm = ctk.CTkLabel(iot_card, text=f"❤️ Ritmo Cardíaco: {self.bpm_ejercicio} BPM", font=("Roboto", 11), text_color="gray" if self.bpm_ejercicio == 0 else "#FF4C4C")
        self.lbl_bpm.pack()
        self.btn_sensor = ctk.CTkButton(iot_card, text="⚡ Vincular Pulso", height=24, command=self.toggle_sensores_smartwatch)
        self.btn_sensor.pack(pady=4)

        # 🎵 TARJETA 2: INTEGRACIÓN DE SPOTIFY MULTIMEDIA (NUEVO)
        spot_card = ctk.CTkFrame(left_column, fg_color="#1DB954" if self.spotify_conectado else self.theme["card"], corner_radius=20, border_width=1, border_color="#1DB954")
        spot_card.pack(fill="x", pady=5, ipady=8)
        
        text_color_spot = "#000000" if self.spotify_conectado else self.theme["text"]
        ctk.CTkLabel(spot_card, text="🎵 Spotify Workout Integration", font=("Roboto", 13, "bold"), text_color=text_color_spot).pack(pady=2)
        
        self.lbl_spot_track = ctk.CTkLabel(spot_card, text=f"📻 {self.cancion_actual}", font=("Roboto", 11, "italic"), text_color=text_color_spot)
        self.lbl_spot_track.pack()

        f_spot_ctrls = ctk.CTkFrame(spot_card, fg_color="transparent")
        f_spot_ctrls.pack(pady=4)
        
        self.btn_spot_play = ctk.CTkButton(f_spot_ctrls, text="▶ Play", width=60, height=24, fg_color="#111111", text_color="#1DB954", command=self.toggle_play_spotify)
        self.btn_spot_play.pack(side="left", padx=2)
        ctk.CTkButton(f_spot_ctrls, text="⏭ Sig", width=60, height=24, fg_color="#111111", text_color="#FFFFFF", command=self.siguiente_cancion_spotify).pack(side="left", padx=2)
        
        self.btn_spot_link = ctk.CTkButton(spot_card, text="🔗 Vincular Cuenta Spotify", font=("Roboto", 11, "bold"), height=24, fg_color="#111111", text_color="#FFFFFF", command=self.vincular_spotify_web)
        self.btn_spot_link.pack(pady=4, padx=20, fill="x")

        # Tarjeta 3: Jaina
        jaina_card = ctk.CTkFrame(left_column, fg_color=self.theme["card"], corner_radius=20, border_width=1, border_color=self.theme["border"])
        jaina_card.pack(fill="x", pady=5, ipady=6)
        avatar_path = self.user.get("avatar_path", "")
        img_frame = ctk.CTkFrame(jaina_card, width=70, height=70, corner_radius=15, fg_color=self.theme["input_bg"])
        img_frame.pack(pady=4)
        img_frame.pack_propagate(False)
        if avatar_path and os.path.exists(avatar_path):
            pil_img = Image.open(avatar_path)
            ctk_img = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(60, 60))
            ctk.CTkLabel(img_frame, image=ctk_img, text="").place(relx=0.5, rely=0.5, anchor="center")
        else:
            ctk.CTkLabel(img_frame, text="🐶", font=("Arial", 25)).place(relx=0.5, rely=0.5, anchor="center")
        bubble = ctk.CTkFrame(jaina_card, fg_color=self.theme["input_bg"], corner_radius=12)
        bubble.pack(fill="x", padx=15, pady=2)
        ctk.CTkLabel(bubble, text="¡Guau! Pon play a Spotify y activemos el cronómetro. Al terminar, tu rutina se guardará en la base de datos de la Universidad automáticamente. 🐾", font=("Roboto", 11, "italic"), text_color=self.theme["text"], wraplength=230, justify="left").pack(padx=10, pady=6)

        # =========================================================
        # 👉 COLUMNA DERECHA: PLANES MULTIMEDIA Y DIARIO DESPLEGABLE
        # =========================================================
        right_column = ctk.CTkFrame(split_layout, fg_color="transparent")
        right_column.grid(row=0, column=1, sticky="nsew", padx=(10, 0))

        ctk.CTkLabel(right_column, text="Planes de Entrenamiento Adaptables", font=("Roboto", 16, "bold"), text_color=self.theme["text"]).pack(anchor="w", pady=2)
        
        # Cada plan de entrenamiento tiene su propio video asignado de forma independiente
        self.render_routine_card(right_column, "🔥 Circuito Quema Grasa (Cardio)", "⏱️ 15 Mins | Sin Equipo", "https://www.youtube.com/watch?v=Mco6xFm7vXw")
        self.render_routine_card(right_column, "💪 Hipertrofia de Pierna (Fuerza)", "⏱️ 30 Mins | Mancuernas y Bandas", "https://www.youtube.com/watch?v=D78U_S-ZfS8")
        self.render_routine_card(right_column, "🧘‍♀️ Flexibilidad Integral y Postura", "⏱️ 10 Mins | Tapete Básico", "https://www.youtube.com/watch?v=EkaM9P66p8w")

        ctk.CTkLabel(right_column, text="Diario de Cargas (Lista Desplegable)", font=("Roboto", 16, "bold"), text_color=self.theme["text"]).pack(anchor="w", pady=(10, 2))
        
        form_card = ctk.CTkFrame(right_column, fg_color=self.theme["card"], corner_radius=15, border_width=1, border_color=self.theme["border"])
        form_card.pack(fill="x", pady=2, ipady=6)

        # 🔥 CAMBIO SOLICITADO: El campo de Ejercicio ahora es una lista desplegable (CTkComboBox)
        f_combo = ctk.CTkFrame(form_card, fg_color="transparent")
        f_combo.pack(fill="x", padx=20, pady=4)
        ctk.CTkLabel(f_combo, text="Seleccionar Ejercicio:", font=("Roboto", 12), text_color=self.theme["text_secondary"], width=150, anchor="w").pack(side="left")
        self.combo_ejercicios = ctk.CTkComboBox(f_combo, values=["Sentadillas", "Press de Banca", "Peso Muerto", "Zancadas", "Flexiones de Pecho", "Plancha Abdominal", "Curl de Bíceps"], height=30, border_color=self.theme["border"])
        self.combo_ejercicios.pack(side="left", fill="x", expand=True)

        self.create_form_row(form_card, "Series Realizadas:", self.sv_series)
        self.create_form_row(form_card, "Repeticiones:", self.sv_reps)
        self.create_form_row(form_card, "Peso / Carga (Kg):", self.sv_peso)

        botones_frame = ctk.CTkFrame(right_column, fg_color="transparent")
        botones_frame.pack(fill="x", pady=15)
        botones_frame.grid_columnconfigure(0, weight=1)
        botones_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkButton(botones_frame, text="💾 Registrar en Base de Datos", font=("Roboto", 13, "bold"), height=38, fg_color=self.theme["primary"], command=self.guardar_volumen_ejercicio_bd).grid(row=0, column=0, padx=5, sticky="ew")
        ctk.CTkButton(botones_frame, text="🧹 Limpiar", font=("Roboto", 13, "bold"), height=38, fg_color="transparent", border_width=2, border_color="#ff4c4c", text_color="#ff4c4c", command=self.vaciar_deporte_diario_bd).grid(row=0, column=1, padx=5, sticky="ew")

    def render_routine_card(self, container, titulo, detalles, url_video):
        card = ctk.CTkFrame(container, fg_color=self.theme["card"], corner_radius=12, border_width=1, border_color=self.theme["border"])
        card.pack(fill="x", pady=3, ipady=4)
        info = ctk.CTkFrame(card, fg_color="transparent")
        info.pack(side="left", padx=15, pady=4)
        ctk.CTkLabel(info, text=titulo, font=("Roboto", 13, "bold")).pack(anchor="w")
        ctk.CTkLabel(info, text=detalles, font=("Roboto", 11), text_color="gray").pack(anchor="w")
        
        # Botón con redirección multimedia dedicada
        ctk.CTkButton(
            card, text="📺 Abrir Video", font=("Roboto", 11, "bold"), width=100, height=26,
            fg_color=self.theme["input_bg"], text_color=self.theme["text"], border_width=1, border_color=self.theme["border"],
            command=lambda: webbrowser.open(url_video)
        ).pack(side="right", padx=15)

    def create_form_row(self, parent, label_text, string_var):
        f = ctk.CTkFrame(parent, fg_color="transparent")
        f.pack(fill="x", padx=20, pady=4)
        ctk.CTkLabel(f, text=label_text, font=("Roboto", 12), text_color=self.theme["text_secondary"], width=150, anchor="w").pack(side="left")
        ctk.CTkEntry(f, textvariable=string_var, height=30, fg_color=self.theme["input_bg"], border_color=self.theme["border"]).pack(side="left", fill="x", expand=True)

    # =========================================================
    # 🎵 LÓGICA DE CONTROL MULTIMEDIA DE SPOTIFY INTEGRADO
    # =========================================================
    def vincular_spotify_web(self):
        """Simulación y enlace de handshake de autenticación OAuth de Spotify."""
        self.btn_spot_link.configure(text="⚡ Autenticando Token API...", fg_color="#1DB954", text_color="#000000")
        
        def hilo_link():
            time.sleep(1.5)
            # Abre el reproductor web de Spotify oficial en tu navegador como integración real
            webbrowser.open("https://open.spotify.com")
            self.spotify_conectado = True
            self.cancion_actual = self.lista_canciones[0]
            self.app.after(0, self.finalizar_vinculacion_spotify_ui)
            
        threading.Thread(target=hilo_link).start()

    def finalizar_vinculacion_spotify_ui(self):
        messagebox.showinfo("Spotify Link", "¡Cuenta vinculada con éxito! El túnel de audio cruzado se encuentra activo. 📻")
        self.build_ui()

    def toggle_play_spotify(self):
        if not self.spotify_conectado:
            messagebox.showwarning("Spotify", "Por favor vincula tu cuenta primero usando el botón inferior.")
            return
        self.reproduciendo_spotify = not self.reproduciendo_spotify
        if self.reproduciendo_spotify:
            self.btn_spot_play.configure(text="⏸ Pausa", fg_color="#FFFFFF", text_color="#000000")
        else:
            self.btn_spot_play.configure(text="▶ Play", fg_color="#111111", text_color="#1DB954")

    def siguiente_cancion_spotify(self):
        if not self.spotify_conectado: return
        self.cancion_actual = random.choice(self.lista_canciones)
        self.lbl_spot_track.configure(text=f"📻 {self.cancion_actual}")

    # =========================================================
    # CONTROLADORES DE SENSORES Y PERSISTENCIA DE DATOS
    # =========================================================
    def toggle_sensores_smartwatch(self):
        if not self.smartwatch_activo:
            self.smartwatch_activo = True
            self.btn_sensor.configure(text="⏸ Parar Capture", fg_color="#ff4c4c")
            threading.Thread(target=self.hilo_sensores, daemon=True).start()
        else:
            self.smartwatch_activo = False
            self.btn_sensor.configure(text="⚡ Vincular Pulso", fg_color=self.theme["primary"])

    def hilo_sensores(self):
        while self.smartwatch_activo:
            self.bpm_ejercicio = random.randint(130, 165)
            self.calorias_quemadas += random.randint(2, 4)
            self.minutos_entrenados += 1
            self.app.after(0, lambda: self.lbl_bpm.configure(text=f"❤️ Ritmo Cardíaco: {self.bpm_ejercicio} BPM", text_color="#FF4C4C"))
            self.app.after(0, lambda: self.lbl_calorias.configure(text=f"🔥 {self.calorias_quemadas} kcal | ⏳ {self.minutos_entrenados} mins"))
            time.sleep(3.0)

    def guardar_volumen_ejercicio_bd(self):
        try:
            ejercicio = self.combo_ejercicios.get() # Captura directa del ComboBox desplegable
            series = int(self.sv_series.get())
            reps = int(self.sv_reps.get())
            peso = float(self.sv_peso.get())
            user_id = self.user.get("id")
            
            # Formato indexado para las grillas analíticas centrales
            self.db.execute_query(
                "INSERT INTO health_records (user_id, tipo, valor, detalle) VALUES (?, 'Deporte_Carga', ?, ?)",
                (user_id, float(series * reps), f"🏃‍♀️ {ejercicio}|{series}x{reps}|{peso}Kg")
            )
            
            # Inyección simultánea en la agenda central de la Universidad (Bloque Tarde por defecto)
            self.db.execute_query("DELETE FROM health_records WHERE user_id=? AND tipo='Cal_Martes_2'", (user_id,))
            self.db.execute_query("INSERT INTO health_records (user_id, tipo, valor, detalle) VALUES (?, 'Cal_Martes_2', 1.0, ?)", (user_id, f"🏃‍♀️ {ejercicio} ({peso}kg)"))

            messagebox.showinfo("Carga Guardada", f"💪 ¡Volumen de {ejercicio} guardado! Sincronizado con la agenda central de la Universidad.")
            self.app.show_dashboard()
        except Exception as e:
            messagebox.showerror("Error", "Introduce valores numéricos válidos en las casillas.")

    def vaciar_deporte_diario_bd(self):
        self.sv_series.set("4")
        self.sv_reps.set("12")
        self.sv_peso.set("0")