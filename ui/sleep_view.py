import customtkinter as ctk
from tkinter import messagebox
from PIL import Image
import os
import random
import time
import threading
import datetime
from core.database import Database

class SleepView:
    def __init__(self, app):
        print("\n--- INICIANDO SISTEMA DE SUEÑO AVANZADO BIOMETRIC ---")
        try:
            self.app = app
            self.user = self.app.current_user
            self.theme = self.app.current_theme
            self.db = Database()
            
            # API Key de tu cuenta personal para desarrollo 🔑
            self.gemini_key = "AIzaSyCCPX1ZENUvzQxLNBoMHMNADOzHt2n-2hs" 
            
            # --- ESTADOS BIOMÉTRICOS DEL SMARTWATCH ---
            self.smartwatch_conectado = False
            self.horas_profundo = 0.0
            self.horas_ligero = 0.0
            self.horas_rem = 0.0
            self.horas_totales = 0.0
            self.score_descanso = 0
            self.bpm_promedio = 0
            
            # --- FACTORES DE ESTILO DE VIDA DIARIOS ---
            self.tazas_cafe = 0
            self.nivel_estres = "Bajo"
            self.ruido_ambiente = "Silencioso"
            
            # --- REPRODUCTOR DE AUDIO SIMULADO ---
            self.audio_reproduciendo = False
            self.sonido_actual = None

            self.app.clear_screen()
            self.main_scroll = ctk.CTkScrollableFrame(
                self.app, fg_color="transparent",
                scrollbar_button_color=self.theme["primary"],
                scrollbar_button_hover_color=self.theme["btn_hover"]
            )
            self.main_scroll.pack(fill="both", expand=True, padx=20, pady=20)

            self.cargar_datos_descanso_bd()
            self.build_ui()
            
        except Exception as e:
            print(f"❌ ERROR CRÍTICO EN DESCANSO PRO: {e}")

    def cargar_datos_descanso_bd(self):
        try:
            user_id = self.user.get("id")
            cursor = self.db.execute_query(
                "SELECT id, tipo, valor, detalle FROM health_records WHERE user_id = ? AND (tipo LIKE 'Sueño_%' OR tipo='Hidratacion_Cafe' OR tipo='Estres_Ruido') AND date(fecha) = date('now')",
                (user_id,)
            )
            for row in cursor.fetchall():
                _, tipo, valor, detalle = row
                if tipo == "Sueño_Total":
                    self.horas_totales = float(valor)
                    self.smartwatch_conectado = True
                elif tipo == "Sueño_Fases":
                    partes = detalle.split("|")
                    if len(partes) >= 5:
                        self.horas_profundo = float(partes[0])
                        self.horas_ligero = float(partes[1])
                        self.horas_rem = float(partes[2])
                        self.score_descanso = int(partes[3])
                        self.bpm_promedio = int(partes[4])
                elif tipo == "Hidratacion_Cafe":
                    self.tazas_cafe = int(valor)
                elif tipo == "Estres_Ruido":
                    partes_e = detalle.split("|")
                    if len(partes_e) >= 2:
                        self.nivel_estres = partes_e[0]
                        self.ruido_ambiente = partes_e[1]
        except Exception as e:
            print(f"Error leyendo BD Descanso: {e}")

    def calcular_score_descanso(self):
        if self.horas_totales == 0:
            self.score_descanso = 0
            return
        score = int((self.horas_profundo / 2.5) * 40 + (self.horas_rem / 2.0) * 40 + (10 if self.bpm_promedio < 65 else 0))
        self.score_descanso = max(40, min(100, score))

    def obtener_dieta_personalizada_dia(self):
        dias_semana = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
        dia_actual = dias_semana[datetime.datetime.now().weekday()]
        meta_tipo = self.user.get("meta_tipo", "Mantenerme")

        dietas = {
            "Lunes": {"D": "Huevos revueltos con espinaca y pan tostado", "A": "Pechuga de pollo a la plancha, arroz integral y ensalada verde", "C": "Filete de pescado al horno con espárragos"},
            "Martes": {"D": "Yogurt griego con fresas y avena en hojuelas", "A": "Carne molida magra, puré de papa y brócoli al vapor", "C": "Ensalada césar ligera con tiras de pollo"},
            "Miércoles": {"D": "Arepa integral con queso cuajada y café sin azúcar", "A": "Filete de salmón o pescado blanco, quinoa y calabacín", "C": "Tortilla de claras de huevo con champiñones y tomate"},
            "Jueves": {"D": "Batido de proteína con banano y leche de almendras", "A": "Bowl de pollo texturizado, frijoles negros, aguacate y arroz", "C": "Pechuga desmechada con vegetales salteados al wok"},
            "Viernes": {"D": "Sándwich de jamón de pavo, queso bajo en grasa y rúgula", "A": "Pasta integral con atún en agua y salsa de tomate natural", "C": "Sopa de verduras casera con dados de pechuga"},
            "Sábado": {"D": "Pancakes de avena y clara de huevo con miel de abejas", "A": "Cerdo magro a la plancha, yuca cocida y ensalada mixta", "C": "Wraps de pollo en tortilla integral con lechuga"},
            "Domingo": {"D": "Porción de fruta variada con queso cottage", "A": "Asado de pollo o res magra con papa al horno y aguacate", "C": "Porción ligera de galletas integrales con atún"}
        }

        menu = dietas.get(dia_actual, dietas["Lunes"])
        ajuste_porciones = "Porciones de déficit calórico." if "Bajar" in meta_tipo else "Porciones de superávit muscular." if "Aumentar" in meta_tipo else "Porciones de mantenimiento."

        texto_dieta = (
            f"📅 Menú del {dia_actual}:\n"
            f"• Desayuno: {menu['D']}\n"
            f"• Almuerzo: {menu['A']}\n"
            f"• Cena: {menu['C']}\n"
            f"💡 Ajuste: {ajuste_porciones}"
        )
        return texto_dieta

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

        split_layout = ctk.CTkFrame(self.main_scroll, fg_color="transparent")
        split_layout.pack(fill="both", expand=True)
        split_layout.grid_columnconfigure(0, weight=4)
        split_layout.grid_columnconfigure(1, weight=6)

        # =========================================================
        # 👈 COLUMNA IZQUIERDA: SMARTWATCH, FASES E HIGIENE (CORREGIDA)
        # =========================================================
        left_column = ctk.CTkFrame(split_layout, fg_color="transparent")
        left_column.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        # Tarjeta 1: Sincronización Smartwatch
        watch_card = ctk.CTkFrame(left_column, fg_color=self.theme["card"], corner_radius=20, border_width=1, border_color=self.theme["border"])
        watch_card.pack(fill="x", pady=5, ipady=8)
        
        ctk.CTkLabel(watch_card, text="⌚ Sincronización Smartwatch", font=("Roboto", 14, "bold"), text_color=self.theme["primary"]).pack(pady=2)
        
        estado_watch = "🟢 Sincronizado | Wearable Activo" if self.smartwatch_conectado else "🔴 Desconectado"
        self.lbl_watch_status = ctk.CTkLabel(watch_card, text=estado_watch, font=("Roboto", 11, "bold"), text_color="gray" if not self.smartwatch_conectado else self.theme["primary"])
        self.lbl_watch_status.pack()

        self.btn_sync = ctk.CTkButton(watch_card, text="🔄 Sincronizar Reloj Inteligente", font=("Roboto", 12, "bold"), height=30, command=self.simular_sincronizacion_reloj)
        self.btn_sync.pack(pady=8)

        # Tarjeta 2: Monitoreo de Fases del Sueño
        fases_card = ctk.CTkFrame(left_column, fg_color=self.theme["card"], corner_radius=20, border_width=1, border_color=self.theme["border"])
        fases_card.pack(fill="x", pady=5, ipady=8)
        
        ctk.CTkLabel(fases_card, text=f"📊 Score de Sueño: {self.score_descanso} pts", font=("Roboto", 14, "bold")).pack(pady=2)
        
        self.render_fase_bar(fases_card, f"😴 Profundo: {self.horas_profundo} hrs", self.horas_profundo, 3.0, "#3182CE")
        self.render_fase_bar(fases_card, f"💤 Ligero: {self.horas_ligero} hrs", self.horas_ligero, 5.0, "#4CAF50")
        self.render_fase_bar(fases_card, f"✨ Fase REM: {self.horas_rem} hrs", self.horas_rem, 2.5, "#FFA500")
        
        if self.bpm_promedio > 0:
            ctk.CTkLabel(fases_card, text=f"❤️ Ritmo Cardíaco Promedio: {self.bpm_promedio} BPM", font=("Roboto", 11, "bold"), text_color="#FF4C4C").pack(pady=4)

        # Tarjeta 3: 🔥 RENDERIZADO REAL DE LA MASCOTA JAINA Y SU CONSEJO INTERACTIVO
        jaina_card = ctk.CTkFrame(left_column, fg_color=self.theme["card"], corner_radius=20, border_width=1, border_color=self.theme["border"])
        jaina_card.pack(fill="x", pady=5, ipady=8)
        
        avatar_path = self.user.get("avatar_path", "")
        nombre_mascota = self.user.get("avatar_name", "Jaina")
        
        img_size = 80
        img_frame = ctk.CTkFrame(jaina_card, width=img_size+10, height=img_size+10, corner_radius=15, fg_color=self.theme["input_bg"])
        img_frame.pack(pady=5)
        img_frame.pack_propagate(False)

        # 🔥 SOLUCIÓN: Renderizado físico de la foto de la mascota en el label
        if avatar_path and os.path.exists(avatar_path):
            pil_img = Image.open(avatar_path)
            ctk_img = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(img_size, img_size))
            ctk.CTkLabel(img_frame, image=ctk_img, text="").place(relx=0.5, rely=0.5, anchor="center")
        else:
            ctk.CTkLabel(img_frame, text="🐾", font=("Arial", 35)).place(relx=0.5, rely=0.5, anchor="center")

        bubble = ctk.CTkFrame(jaina_card, fg_color=self.theme["input_bg"], corner_radius=12)
        bubble.pack(fill="x", padx=15, pady=5)
        
        # 🔥 SOLUCIÓN: Diálogos personalizados de Jaina (adiós Nakama)
        consejo = f"¡Hola! Muevo mi colita de felicidad por verte. 🥰 Sincroniza tu reloj inteligente para que podamos ver cómo durmió tu corazoncito anoche. 🐾"
        if self.score_descanso > 0 and self.score_descanso < 65:
            consejo = f"🐶 ¡Guau! Noto que estás un poquito cansado. Tu fase profunda fue muy corta debido al estrés o las {self.tazas_cafe} tazas de café. ¡Hoy vamos a descansar temprano juntos!"
        elif self.score_descanso >= 75:
            consejo = f"🌟 ¡Increíble! Tu score de {self.score_descanso}% indica que recuperaste toda tu energía. Tu cerebro está súper listo para tus clases en la universidad hoy. ¡Vamos con toda!"
            
        ctk.CTkLabel(bubble, text=consejo, font=("Roboto", 11, "italic"), text_color=self.theme["text"], wraplength=230, justify="left").pack(padx=12, pady=10)

        # =========================================================
        # 👉 COLUMNA DERECHA: ALARMAS, AUDIO, DIARIO DE HÁBITOS
        # =========================================================
        right_column = ctk.CTkFrame(split_layout, fg_color="transparent")
        right_column.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        
        ctk.CTkLabel(right_column, text="Registro de Ciclos de Sueño", font=("Roboto", 18, "bold"), text_color=self.theme["text"]).pack(anchor="w", pady=5)

        # 1. Sub-módulo: Alarmas Inteligentes
        alarm_card = ctk.CTkFrame(right_column, fg_color=self.theme["card"], corner_radius=15, border_width=1, border_color=self.theme["border"])
        alarm_card.pack(fill="x", pady=4, ipady=5)
        ctk.CTkLabel(alarm_card, text="⏰ Alarma Inteligente Circadiana", font=("Roboto", 14, "bold")).pack(anchor="w", padx=15, pady=2)
        
        f_alarm = ctk.CTkFrame(alarm_card, fg_color="transparent")
        f_alarm.pack(fill="x", padx=15)
        self.combo_alarma = ctk.CTkComboBox(f_alarm, values=["05:30 AM (Fase Ligera)", "06:15 AM (Óptimo)", "07:00 AM (Ciclo REM)", "Desactivada"], width=200)
        self.combo_alarma.pack(side="left", padx=5)
        ctk.CTkButton(f_alarm, text="Configurar", width=80, height=28, command=lambda: messagebox.showinfo("Alarma", "¡Alarma inteligente programada en tu ventana de sueño ligero!")).pack(side="left", padx=5)

        # 2. Sub-módulo: Biblioteca de Sonidos Relajantes
        sound_card = ctk.CTkFrame(right_column, fg_color=self.theme["card"], corner_radius=15, border_width=1, border_color=self.theme["border"])
        sound_card.pack(fill="x", pady=4, ipady=5)
        ctk.CTkLabel(sound_card, text="🎵 Sonidos Blancos y Ruido Relajante", font=("Roboto", 14, "bold")).pack(anchor="w", padx=15, pady=2)
        
        f_sound = ctk.CTkFrame(sound_card, fg_color="transparent")
        f_sound.pack(fill="x", padx=15)
        self.combo_sonido = ctk.CTkComboBox(f_sound, values=["Lluvia Torrencial 🌧️", "Olas del Mar 🌊", "Bosque Zen 🎋", "Ruido Blanco 🎛️"], width=200)
        self.combo_sonido.pack(side="left", padx=5)
        
        self.btn_audio = ctk.CTkButton(f_sound, text="▶ Play", width=80, height=28, fg_color=self.theme["primary"], command=self.toggle_reproductor_audio)
        self.btn_audio.pack(side="left", padx=5)

        # 3. Sub-módulo: Diario de Hábitos y Entorno
        habitos_card = ctk.CTkFrame(right_column, fg_color=self.theme["card"], corner_radius=15, border_width=1, border_color=self.theme["border"])
        habitos_card.pack(fill="x", pady=4, ipady=5)
        ctk.CTkLabel(habitos_card, text="📝 Registro de Estilo de Vida y Entorno", font=("Roboto", 14, "bold")).pack(anchor="w", padx=15, pady=2)

        f_cafe = ctk.CTkFrame(habitos_card, fg_color="transparent")
        f_cafe.pack(fill="x", padx=15, pady=4)
        ctk.CTkLabel(f_cafe, text="Tazas de café hoy:", font=("Roboto", 12), width=150, anchor="w").pack(side="left")
        ctk.CTkButton(f_cafe, text="➖", width=30, height=24, command=self.restar_cafe).pack(side="left", padx=2)
        ctk.CTkLabel(f_cafe, text=f"☕ {self.tazas_cafe}", font=("Roboto", 12, "bold"), width=50).pack(side="left")
        ctk.CTkButton(f_cafe, text="➕", width=30, height=24, command=self.sumar_cafe).pack(side="left", padx=2)

        f_estres = ctk.CTkFrame(habitos_card, fg_color="transparent")
        f_estres.pack(fill="x", padx=15, pady=4)
        ctk.CTkLabel(f_estres, text="Nivel de Estrés Mental:", font=("Roboto", 12), width=150, anchor="w").pack(side="left")
        self.combo_estres = ctk.CTkComboBox(f_estres, values=["Bajo", "Moderado", "Alto"], width=160, height=28)
        self.combo_estres.set(self.nivel_estres)
        self.combo_estres.pack(side="left")

        f_ruido = ctk.CTkFrame(habitos_card, fg_color="transparent")
        f_ruido.pack(fill="x", padx=15, pady=4)
        ctk.CTkLabel(f_ruido, text="Ruido en el Dormitorio:", font=("Roboto", 12), width=150, anchor="w").pack(side="left")
        self.combo_ruido = ctk.CTkComboBox(f_ruido, values=["Silencioso", "Moderado", "Ruidoso (Calle)"], width=160, height=28)
        self.combo_ruido.set(self.ruido_ambiente)
        self.combo_ruido.pack(side="left")

        # BOTONERA DOBLE
        botones_frame = ctk.CTkFrame(right_column, fg_color="transparent")
        botones_frame.pack(fill="x", pady=15)
        botones_frame.grid_columnconfigure(0, weight=1)
        botones_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkButton(botones_frame, text="💾 Guardar Métricas de Descanso", font=("Roboto", 13, "bold"), height=38, fg_color=self.theme["primary"], hover_color=self.theme["btn_hover"], command=self.guardar_descanso_completo_bd).grid(row=0, column=0, padx=5, sticky="ew")
        ctk.CTkButton(botones_frame, text="🧹 Vaciar todo el Registro", font=("Roboto", 13, "bold"), height=38, fg_color="transparent", border_width=2, border_color="#ff4c4c", text_color="#ff4c4c", hover_color="#331414", command=self.vaciar_descanso_diario_bd).grid(row=0, column=1, padx=5, sticky="ew")

    def render_fase_bar(self, parent, label, valor, ideal, color):
        f = ctk.CTkFrame(parent, fg_color="transparent")
        f.pack(fill="x", padx=15, pady=2)
        ctk.CTkLabel(f, text=label, font=("Roboto", 12), text_color=self.theme["text_secondary"]).pack(anchor="w")
        porcentaje = max(0.0, min(1.0, valor / ideal if ideal > 0 else 0))
        p = ctk.CTkProgressBar(f, width=220, height=8, progress_color=color, fg_color="#333333")
        p.set(porcentaje)
        p.pack(anchor="w", pady=2)

    def simular_sincronizacion_reloj(self):
        self.btn_sync.configure(state="disabled", text="⚡ Leyendo Sensores IoT...")
        threading.Thread(target=self.hilo_reloj_iot).start()

    def hilo_reloj_iot(self):
        time.sleep(1.2)
        self.horas_profundo = round(random.uniform(1.5, 3.2), 1)
        self.horas_ligero = round(random.uniform(3.5, 5.5), 1)
        self.horas_rem = round(random.uniform(1.2, 2.6), 1)
        self.horas_totales = round(self.horas_profundo + self.horas_ligero + self.horas_rem, 1)
        self.bpm_promedio = random.randint(58, 68)
        
        self.smartwatch_conectado = True
        self.calcular_score_descanso()
        self.app.after(0, self.finalizar_sincronizacion_ui)

    def finalizar_sincronizacion_ui(self):
        self.btn_sync.configure(state="normal", text="🔄 Sincronizar Reloj Inteligente")
        messagebox.showinfo("Smartwatch Sincronizado", "¡Métricas circadianas extraídas con éxito del acelerómetro y sensor fotopletismógrafo (PPG)! ⌚")
        self.build_ui()

    def toggle_reproductor_audio(self):
        if not self.audio_reproduciendo:
            self.audio_reproduciendo = True
            self.sonido_actual = self.combo_sonido.get()
            self.btn_audio.configure(text="⏸ Stop", fg_color="#ff4c4c")
        else:
            self.audio_reproduciendo = False
            self.btn_audio.configure(text="▶ Play", fg_color=self.theme["primary"])

    def sumar_cafe(self):
        self.tazas_cafe += 1
        self.build_ui()

    def disminuir_cafe_logica(self):
        if self.tazas_cafe > 0:
            self.tazas_cafe -= 1
            self.build_ui()

    def restar_cafe(self):
        self.disminuir_cafe_logica()

    def guardar_descanso_completo_bd(self):
        try:
            user_id = self.user.get("id")
            estres = self.combo_estres.get()
            ruido = self.combo_ruido.get()
            
            fases_str = f"{self.horas_profundo}|{self.horas_ligero}|{self.horas_rem}|{self.score_descanso}|{self.bpm_promedio}"
            estres_ruido_str = f"{estres}|{ruido}"

            # Reemplaza juntos los cuatro datos; no deja un guardado parcial.
            self.db.replace_daily_records(user_id,
                ("Sueño_Total", "Sueño_Fases", "Hidratacion_Cafe", "Estres_Ruido"),
                (("Sueño_Total", float(self.horas_totales), "Horas reloj"),
                 ("Sueño_Fases", float(self.score_descanso), fases_str),
                 ("Hidratacion_Cafe", float(self.tazas_cafe), "Tazas consumidas"),
                 ("Estres_Ruido", 0.0, estres_ruido_str)))
            
            messagebox.showinfo("Registro Consolidado", "¡Todas las variables de descanso, entorno y estilo de vida se han guardado con éxito! 🚀")
            self.app.show_dashboard()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar: {e}")

    def vaciar_descanso_diario_bd(self):
        confirmar = messagebox.askyesno("Vaciar Registro", "⚠ ¿Deseas restablecer a cero las métricas de descanso de hoy?")
        if confirmar:
            try:
                user_id = self.user.get("id")
                self.db.execute_query("DELETE FROM health_records WHERE user_id = ? AND (tipo='Sueño_Total' OR tipo='Sueño_Fases' OR tipo='Hidratacion_Cafe' OR tipo='Estres_Ruido') AND date(fecha) = date('now')", (user_id,))
                self.horas_totales = 0.0
                self.horas_profundo = 0.0
                self.horas_ligero = 0.0
                self.horas_rem = 0.0
                self.score_descanso = 0
                self.bpm_promedio = 0
                self.tazas_cafe = 0
                self.nivel_estres = "Bajo"
                self.ruido_ambiente = "Silencioso"
                self.smartwatch_conectado = False
                self.build_ui()
            except Exception as e:
                messagebox.showerror("Error", str(e))
