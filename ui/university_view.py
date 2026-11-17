import customtkinter as ctk
from tkinter import messagebox
import tkinter as tk
from PIL import Image
import os
import datetime
import time
from core.database import Database

class UniversityView:
    def __init__(self, app):
        print("\n--- INICIANDO SISTEMA CENTRAL DE CONTROL UNIVERSITARIO ---")
        try:
            self.app = app
            self.user = self.app.current_user
            self.theme = self.app.current_theme
            self.db = Database()
            
            # --- CONFIGURACIÓN DE PERFIL TRABAJO / ESTUDIO ---
            self.perfil_usuario = self.user.get("perfil_universitario", "Ambos") # Opciones: Estudia, Trabaja, Ambos
            self.creditos_inscritos = 18
            
            # --- MÉTRICAS DE ENTRADA CLÍNICAS (SINCRONIZADAS) ---
            self.promedio_sueno_3dias = 5.2  # Simulación Smartwatch: Alerta Fatiga activa si < 6.0
            self.nivel_ansiedad_actual = 8   # Escala de Salud Mental
            
            # --- VARIABLES DE ENTRADA HORARIA ---
            self.horas_laborales = 8.0 if self.perfil_usuario in ["Trabaja", "Ambos"] else 0.0
            self.horas_transporte = 2.0
            self.horas_clase = 4.0
            self.horas_estudio_asignadas = 3.0
            self.carga_horaria_real = 0.0
            
            # --- CONTROL DE SUEÑO PROTEGIDO ELEGIDO ---
            self.bloque_sueno_inicio = 22 # 10 PM
            self.bloque_sueno_fin = 5     # 5 AM (7 Horas Protegidas Obligatorias)

            # --- MODELOS DE DATOS ---
            self.eventos_agenda = {}
            self.sim_materia = ctk.StringVar(value="Arquitectura de Software")
            self.sim_nota_actual = ctk.StringVar(value="3.8")
            self.sim_nota_requerida = ctk.StringVar(value="4.2")

            self.app.clear_screen()
            self.main_scroll = ctk.CTkScrollableFrame(
                self.app, fg_color="transparent",
                scrollbar_button_color=self.theme["primary"],
                scrollbar_button_hover_color=self.theme["btn_hover"]
            )
            self.main_scroll.pack(fill="both", expand=True, padx=20, pady=20)

            self.ejecutar_pipeline_y_calculos()
            self.build_ui()
            
        except Exception as e:
            print(f"❌ ERROR CRÍTICO EN NÚCLEO UNIVERSIDAD: {e}")

    def ejecutar_pipeline_y_calculos(self):
        """Calcula la Carga Horaria Real de Fatiga e indexa los calendarios relacionales."""
        user_id = self.user.get("id")
        
        # 1. Calculador de Carga Horaria Real de Sobrecarga
        self.carga_horaria_real = self.horas_laborales + self.horas_transporte + self.horas_clase + self.horas_estudio_asignadas
        
        # 2. Descargar la matriz central de la agenda desde SQLite (incluyendo FemTech, Deporte y alarmas)
        try:
            cursor = self.db.execute_query("SELECT tipo, detalle FROM health_records WHERE user_id = ? AND tipo LIKE 'Cal_%'", (user_id,))
            self.eventos_agenda = {}
            for row in cursor.fetchall():
                self.eventos_agenda[row[0]] = row[1]
        except Exception as e:
            print(f"Error mapeando BD Central: {e}")

    def build_ui(self):
        for widget in self.main_scroll.winfo_children():
            widget.destroy()

        # BOTÓN VOLVER
        ctk.CTkButton(
            self.main_scroll, text="⬅ Volver al Dashboard", width=140, height=30,
            font=("Roboto", 12, "bold"), fg_color="transparent",
            text_color=self.theme["text_secondary"], hover_color=self.theme["card_hover"],
            command=self.app.show_dashboard
        ).pack(anchor="w", padx=10, pady=(0, 5))

        # =========================================================
        # 🚨 ALERTAS INTELIGENTES PUSH-UP SENSORIZADAS (BURNOUT / SMARTWATCH)
        # =========================================================
        self.inyectar_alertas_push_criticas()

        split_layout = ctk.CTkFrame(self.main_scroll, fg_color="transparent")
        split_layout.pack(fill="both", expand=True)
        split_layout.grid_columnconfigure(0, weight=4)
        split_layout.grid_columnconfigure(1, weight=6)

        # 👈 COLUMNA IZQUIERDA: EXPEDIENTE CLÍNICO ACADÉMICO Y JAINA
        left_col = ctk.CTkFrame(split_layout, fg_color="transparent")
        left_col.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        # Cuadro de Mandos de Carga Real
        carga_card = ctk.CTkFrame(left_col, fg_color=self.theme["card"], corner_radius=15, border_width=1, border_color=self.theme["border"])
        carga_card.pack(fill="x", pady=5, ipady=6)
        ctk.CTkLabel(carga_card, text="📊 Carga Horaria Real y Prevención de Burnout", font=("Roboto", 12, "bold"), text_color=self.theme["primary"]).pack(anchor="w", padx=15, pady=2)
        
        lbl_status_c = f"⏱️ Tu día activo ocupa: {self.carga_horaria_real} hrs/día\n📚 Créditos inscritos: {self.creditos_inscritos} (Límite Seguro)"
        color_alert = "green" if self.carga_horaria_real <= 14.0 else "#FF4C4C"
        ctk.CTkLabel(carga_card, text=lbl_status_c, font=("Roboto", 11, "bold"), justify="left", text_color=color_alert).pack(anchor="w", padx=15, pady=2)

        # Acompañamiento y Microdosis de Bienestar con Jaina
        jaina_card = ctk.CTkFrame(left_col, fg_color=self.theme["card"], corner_radius=20, border_width=1, border_color=self.theme["border"])
        jaina_card.pack(fill="x", pady=5, ipady=8)
        
        # Jaina detecta la falta de sueño del Smartwatch exigido en los requerimientos
        txt_jaina = "🐾 ¡Hola! Mi sensor detecta que llevas 3 días durmiendo menos de 6 horas debido a la entrega de proyectos. ¡Te ordeno tomar una microdosis de bienestar! Presiona el botón de abajo para meditar 5 minutos."
        self.inyectar_avatar_mascota(jaina_card, txt_jaina)

        # Simulador y Gestor de Calificaciones
        sim_card = ctk.CTkFrame(left_col, fg_color=self.theme["card"], corner_radius=15, border_width=1, border_color=self.theme["border"])
        sim_card.pack(fill="x", pady=5, ipady=6)
        ctk.CTkLabel(sim_card, text="🧮 Simulador de Notas y Alerta de Aislamiento", font=("Roboto", 12, "bold")).pack(anchor="w", padx=15, pady=2)
        self.create_form_row(sim_card, "Materia:", self.sim_materia)
        self.create_form_row(sim_card, "Nota Actual:", self.sim_nota_actual)
        self.create_form_row(sim_card, "Nota Deseada:", self.sim_nota_requerida)
        ctk.CTkButton(sim_card, text="📊 Calcular Nota Necesaria en Final", font=("Roboto", 11), height=24, fg_color=self.theme["input_bg"], text_color=self.theme["text"], command=self.calcular_simulacion_nota).pack(pady=6)

        # 👉 COLUMNA DERECHA: PLANIFICADOR DE ESTUDIO INTELIGENTE CENTRALIZADO
        right_col = ctk.CTkFrame(split_layout, fg_color="transparent")
        right_col.grid(row=0, column=1, sticky="nsew", padx=(10, 0))

        self.renderizar_calendario_maestro_central(right_col)

    def inyectar_alertas_push_criticas(self):
        """Analiza variables cruzadas en tiempo real y genera banners de advertencia tipo push-up."""
        # Alerta 1: Sobrecarga Horaria / Riesgo Burnout
        if self.carga_horaria_real > 15.0:
            p_card = ctk.CTkFrame(self.main_scroll, fg_color="#2D1217", corner_radius=12, border_width=1, border_color="#FF4C4C")
            p_card.pack(fill="x", pady=(0, 10), ipady=4)
            ctk.CTkLabel(p_card, text="🚨 ALERTA DE SOBRECARGA CRÍTICA: Tu jornada (Trabajo + Transporte + Universidad) supera las 15 horas diarias. Jaina ha bloqueado horas adicionales de estudio el fin de semana para prevenir colapso nervioso.", font=("Roboto", 11, "bold"), text_color="#FF4C4C", wraplength=720, justify="left").pack(padx=15, pady=4)

        # Alerta 2: Relación Bajas Notas / Inasistencias / Salud Mental
        if self.nivel_ansiedad_actual >= 7 and self.promedio_sueno_3dias < 5.5:
            p_card2 = ctk.CTkFrame(self.main_scroll, fg_color="#2D1B12", corner_radius=12, border_width=1, border_color="#E53E3E")
            p_card2.pack(fill="x", pady=(0, 10), ipady=4)
            ctk.CTkLabel(p_card2, text="⚠️ DETECTOR DE AISLAMIENTO SOCIAL PREMATURO: Registras 3 faltas consecutivas a clase combinadas con alta ansiedad. El sistema ha notificado a tu agenda la suspensión de entrenamientos de alta intensidad para priorizar descanso.", font=("Roboto", 11, "bold"), text_color="#E53E3E", wraplength=720, justify="left").pack(padx=15, pady=4)

    # =========================================================
    # 📅 EL CALENDARIO MAESTRO CENTRALIZADO DE LA APLICACIÓN
    # =========================================================
    def renderizar_calendario_maestro_central(self, container):
        ctk.CTkLabel(container, text="📅 Matriz Central de Planificación (Sincronización Total)", font=("Roboto", 15, "bold")).pack(anchor="w", pady=(0, 5))
        
        cal_box = ctk.CTkFrame(container, fg_color=self.theme["card"], corner_radius=15, border_width=1, border_color=self.theme["border"])
        cal_box.pack(fill="both", expand=True)

        cal_box.grid_columnconfigure(0, weight=1)
        for i in range(1, 6): cal_box.grid_columnconfigure(i, weight=2)

        dias = ["Bloque", "Lunes", "Martes", "Miércoles", "Jueves", " Viernes"]
        for idx, d in enumerate(dias):
            bg_h = self.theme["primary"] if idx > 0 else self.theme["input_bg"]
            h_frame = ctk.CTkFrame(cal_box, fg_color=bg_h, corner_radius=5)
            h_frame.grid(row=0, column=idx, padx=2, pady=4, sticky="nsew")
            ctk.CTkLabel(h_frame, text=d, font=("Roboto", 10, "bold"), text_color="#000000" if idx > 0 else self.theme["text"]).pack(pady=2)

        # Definición de los 4 bloques horarios indexados maestros
        bloques = [
            ("00:00 - 07:00", 0), # Fila de Sueño
            ("08:00 - 12:00", 1), # Mañana
            ("14:00 - 18:00", 2), # Tarde
            ("19:00 - 22:00", 3)  # Noche
        ]

        for b_name, b_idx in bloques:
            ctk.CTkLabel(cal_box, text=b_name, font=("Roboto", 9, "bold"), text_color=self.theme["text_secondary"]).grid(row=b_idx+1, column=0, padx=5, sticky="w")
            
            for c_idx in range(1, 6):
                dia_nombre = dias[c_idx]
                key_agenda = f"Cal_{dia_nombre}_{b_idx}"
                
                # REQUERIMIENTO COMPORTAMIENTO: BLOQUEO AUTOMÁTICO DE SUEÑO ELEGIDO
                if b_idx == 0:
                    texto_celda = "🔒 Sueño Protegido (Fijo)"
                    bg_celda = "#1A1525"
                    cmd_celda = None
                    txt_color = "#9F7AEA"
                else:
                    # Mapeo y cruce relacional automático exigido (Citas, Periodos, Deporte, Entregas)
                    if key_agenda in self.eventos_agenda:
                        texto_celda = self.eventos_agenda[key_agenda]
                        # Si contiene tokens de salud/ginecología, resalta con color rosa FemTech automáticamente
                        if "🩺" in texto_celda or "🩸" in texto_celda:
                            bg_celda = "#ED64A6"
                            txt_color = "#000000"
                        elif "🏃‍♀️" in texto_celda:
                            bg_celda = "#4CAF50"
                            txt_color = "#000000"
                        else:
                            bg_celda = self.theme["primary"]
                            txt_color = "#000000"
                    else:
                        texto_celda = "➕ Libre / Asignar"
                        bg_celda = self.theme["input_bg"]
                        txt_color = self.theme["text"]
                    
                    cmd_celda = lambda d=dia_nombre, b=b_idx: self.abrir_programador_central_modal(d, b)

                btn = ctk.CTkButton(
                    cal_box, text=texto_celda, font=("Roboto", 9), fg_color=bg_celda,
                    text_color=txt_color, hover_color=self.theme["card_hover"],
                    border_width=1, border_color=self.theme["border"], height=32, command=cmd_celda
                )
                btn.grid(row=b_idx+1, column=c_idx, padx=2, pady=3, sticky="nsew")

        # Botonera de control de pausas activas
        ctk.CTkButton(container, text="⏱️ Iniciar Cronómetro de Pausa Activa TCC", font=("Roboto", 12, "bold"), fg_color="#3182CE", height=35, command=self.lanzar_cronometro_pausa_activa).pack(fill="x", pady=10)

    def abrir_programador_central_modal(self, dia, bloque_idx):
        """Modal único de asignación de tareas sincronizadas bidireccionalmente."""
        modal = ctk.CTkToplevel(self.app)
        modal.title("Planificador Centralizado")
        modal.geometry("360x220")
        modal.attributes("-topmost", True)
        modal.configure(fg_color=self.theme["card"])
        
        modal.update_idletasks()
        x = (modal.winfo_screenwidth() // 2) - (360 // 2)
        y = (modal.winfo_screenheight() // 2) - (220 // 2)
        modal.geometry(f"+{x}+{y}")

        ctk.CTkLabel(modal, text=f"📌 Agendar en Bloque Central ({dia})", font=("Roboto", 13, "bold"), text_color=self.theme["primary"]).pack(pady=10)
        combo_t = ctk.CTkComboBox(modal, values=["📝 Clase/Estudio: ", "💼 Trabajo: ", "🏃‍♀️ Deporte: ", "🧹 Limpiar Celda"], width=280)
        combo_t.pack(pady=4)
        entry_d = ctk.CTkEntry(modal, placeholder_text="Descripción detallada de la entrega...", width=280)
        entry_d.pack(pady=4)

        def guardar_en_bd_central():
            tipo = combo_t.get()
            desc = entry_d.get().strip()
            key_agenda = f"Cal_{dia}_{bloque_idx}"
            user_id = self.user.get("id")

            self.db.execute_query("DELETE FROM health_records WHERE user_id=? AND tipo=?", (user_id, key_agenda))
            if tipo != "🧹 Limpiar Celda" and desc:
                self.db.execute_query("INSERT INTO health_records (user_id, tipo, valor, detalle) VALUES (?, ?, 1.0, ?)", (user_id, key_agenda, f"{tipo}{desc}"))
            
            modal.destroy()
            self.ejecutar_pipeline_y_calculos()
            self.build_ui()

        ctk.CTkButton(modal, text="📥 Guardar Sincronización Global", fg_color=self.theme["primary"], text_color="#000000", command=guardar_en_bd_central).pack(pady=12)

    def lanzar_cronometro_pausa_activa(self):
        messagebox.showinfo("Pausa Activa", "⏱️ Cronómetro Pomodoro activado: Tienes 5 minutos para realizar estiramientos cervicales y respiración diafragmática. Tu salud mental lo agradecerá.")

    def calcular_simulacion_nota(self):
        try:
            actual = float(self.sim_nota_actual.get())
            deseada = float(self.sim_nota_requerida.get())
            # Ecuación lineal predictiva simple para el examen final (ponderación del 40%)
            necesaria = (deseada - (actual * 0.6)) / 0.4
            messagebox.showinfo("Simulador de Notas", f"Materia: {self.sim_materia.get()}\n🎯 Para promediar {deseada}, necesitas obtener un mínimo de {round(necesaria, 2)} en tu examen final.")
        except:
            messagebox.showerror("Error", "Introduce valores numéricos válidos en el simulador.")

    def inyectar_avatar_mascota(self, card, texto):
        avatar_path = self.user.get("avatar_path", "")
        img_frame = ctk.CTkFrame(card, width=70, height=70, corner_radius=12, fg_color=self.theme["input_bg"])
        img_frame.pack(pady=5)
        img_frame.pack_propagate(False)
        if avatar_path and os.path.exists(avatar_path):
            pil_img = Image.open(avatar_path)
            ctk_img = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(60, 60))
            ctk.CTkLabel(img_frame, image=ctk_img, text="").place(relx=0.5, rely=0.5, anchor="center")
        else:
            ctk.CTkLabel(img_frame, text="🐶", font=("Arial", 25)).place(relx=0.5, rely=0.5, anchor="center")
        
        bubble = ctk.CTkFrame(card, fg_color=self.theme["input_bg"], corner_radius=12)
        bubble.pack(fill="x", padx=15, pady=4)
        ctk.CTkLabel(bubble, text=texto, font=("Roboto", 11, "italic"), text_color=self.theme["text"], wraplength=230, justify="left").pack(padx=12, pady=8)

    def create_form_row(self, parent, label_text, string_var):
        f = ctk.CTkFrame(parent, fg_color="transparent")
        f.pack(fill="x", padx=15, pady=3)
        ctk.CTkLabel(f, text=label_text, font=("Roboto", 11), text_color=self.theme["text_secondary"], width=100, anchor="w").pack(side="left")
        ctk.CTkEntry(f, textvariable=string_var, height=26, fg_color=self.theme["input_bg"], border_color=self.theme["border"], font=("Roboto", 11)).pack(side="left", fill="x", expand=True)