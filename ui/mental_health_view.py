import customtkinter as ctk
from tkinter import messagebox
from PIL import Image
import os
import threading
import time
import datetime
from google import genai
from core.database import Database

class MentalHealthView:
    def __init__(self, app):
        print("\n--- INICIANDO SISTEMA DE SALUD MENTAL PRO ---")
        try:
            self.app = app
            self.user = self.app.current_user
            self.theme = self.app.current_theme
            self.db = Database()
            
            # Tu API Key para el chat interactivo en tiempo real con Jaina 🔑
            self.gemini_key = "AIzaSyCCPX1ZENUvzQxLNBoMHMNADOzHt2n-2hs"
            
            # --- ESTADOS DE SALUD MENTAL ---
            self.animo_actual = "Neutral"
            self.nivel_estres = 5
            self.sintoma_fisico = "Ninguno"
            
            # --- MOTOR DE RESPIRACIÓN Y CRONÓMETRO ---
            self.respirando = False
            self.segundos_restantes = 0
            self.fase_respiracion = "Inhala"
            
            # --- HISTORIAL LOCAL DEL CHAT CON JAINA ---
            self.historial_chat = []

            self.app.clear_screen()
            self.main_scroll = ctk.CTkScrollableFrame(
                self.app, fg_color="transparent",
                scrollbar_button_color=self.theme["primary"],
                scrollbar_button_hover_color=self.theme["btn_hover"]
            )
            self.main_scroll.pack(fill="both", expand=True, padx=20, pady=20)

            self.cargar_datos_salud_mental_bd()
            self.build_ui()
            print("✅ MÓDULO DE SALUD MENTAL DESPLEGADO")
        except Exception as e:
            print(f"❌ ERROR CRÍTICO EN SALUD MENTAL: {e}")

    def cargar_datos_salud_mental_bd(self):
        try:
            user_id = self.user.get("id")
            cursor = self.db.execute_query(
                "SELECT tipo, valor, detalle FROM health_records WHERE user_id = ? AND tipo LIKE 'Mente_%' AND date(fecha) = date('now')",
                (user_id,)
            )
            for row in cursor.fetchall():
                tipo, valor, detalle = row
                if tipo == "Mente_Animo":
                    self.animo_actual = detalle
                elif tipo == "Mente_Estres":
                    self.nivel_estres = int(valor)
                elif tipo == "Mente_Sintomas":
                    self.sintoma_fisico = detalle
        except Exception as e:
            print(f"Error leyendo BD Salud Mental: {e}")

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

        # LAYOUT SPLIT PRINCIPAL
        split_layout = ctk.CTkFrame(self.main_scroll, fg_color="transparent")
        split_layout.pack(fill="both", expand=True)
        split_layout.grid_columnconfigure(0, weight=5)
        split_layout.grid_columnconfigure(1, weight=5)

        # =========================================================
        # 👈 COLUMNA IZQUIERDA: SEGUIMIENTO, MASCOTA Y CHAT IA
        # =========================================================
        left_column = ctk.CTkFrame(split_layout, fg_color="transparent")
        left_column.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        # Tarjeta 1: Seguimiento Emocional y Biométrico
        tracking_card = ctk.CTkFrame(left_column, fg_color=self.theme["card"], corner_radius=20, border_width=1, border_color=self.theme["border"])
        tracking_card.pack(fill="x", pady=5, ipady=10)
        
        ctk.CTkLabel(tracking_card, text="📊 Registro Emocional Diario", font=("Roboto", 14, "bold"), text_color=self.theme["primary"]).pack(anchor="w", padx=20, pady=5)

        # Selector de Ánimo
        f_animo = ctk.CTkFrame(tracking_card, fg_color="transparent")
        f_animo.pack(fill="x", padx=20, pady=4)
        ctk.CTkLabel(f_animo, text="Estado de Ánimo:", font=("Roboto", 12), width=130, anchor="w").pack(side="left")
        self.combo_animo = ctk.CTkComboBox(f_animo, values=["Feliz ✨", "Calmado 🍃", "Neutral 😐", "Estresado 🧠", "Triste 🌧️"], height=28, width=160)
        self.combo_animo.set(self.animo_actual)
        self.combo_animo.pack(side="left")

        # Control Deslizante de Estrés
        f_estres = ctk.CTkFrame(tracking_card, fg_color="transparent")
        f_estres.pack(fill="x", padx=20, pady=4)
        ctk.CTkLabel(f_estres, text="Nivel de Estrés:", font=("Roboto", 12), width=130, anchor="w").pack(side="left")
        self.slider_estres = ctk.CTkSlider(f_estres, from_=1, to=10, number_of_steps=9, width=160, button_color=self.theme["primary"])
        self.slider_estres.set(self.nivel_estres)
        self.slider_estres.pack(side="left")

        # Síntomas Físicos
        f_sintoma = ctk.CTkFrame(tracking_card, fg_color="transparent")
        f_sintoma.pack(fill="x", padx=20, pady=4)
        ctk.CTkLabel(f_sintoma, text="Tensión Física:", font=("Roboto", 12), width=130, anchor="w").pack(side="left")
        self.combo_sintoma = ctk.CTkComboBox(f_sintoma, values=["Ninguno", "Dolor de Cabeza 🤕", "Cuello Rígido 🧣", "Presión Pecho 🫁", "Fatiga General 🔋"], height=28, width=160)
        self.combo_sintoma.set(self.sintoma_fisico)
        self.combo_sintoma.pack(side="left")

        # Tarjeta 2: Teleterapia / Chat en Tiempo Real con Jaina IA
        chat_card = ctk.CTkFrame(left_column, fg_color=self.theme["card"], corner_radius=20, border_width=1, border_color=self.theme["border"])
        chat_card.pack(fill="x", pady=5, ipady=10)

        # Encabezado con imagen de la mascota
        chat_header = ctk.CTkFrame(chat_card, fg_color="transparent")
        chat_header.pack(fill="x", padx=15, pady=5)
        
        avatar_path = self.user.get("avatar_path", "")
        nombre_mascota = self.user.get("avatar_name", "Jaina")
        
        img_size = 50
        img_frame = ctk.CTkFrame(chat_header, width=img_size, height=img_size, corner_radius=25, fg_color=self.theme["input_bg"])
        img_frame.pack(side="left")
        img_frame.pack_propagate(False)

        if avatar_path and os.path.exists(avatar_path):
            pil_img = Image.open(avatar_path)
            ctk_img = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(img_size, img_size))
            ctk.CTkLabel(img_frame, image=ctk_img, text="").place(relx=0.5, rely=0.5, anchor="center")
        else:
            ctk.CTkLabel(img_frame, text="🐾", font=("Arial", 22)).place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(chat_header, text=f"💬 Teleterapia con {nombre_mascota}", font=("Roboto", 14, "bold"), text_color=self.theme["primary"]).pack(side="left", padx=10)

        # Caja de Texto del Chat (Logs)
        self.txt_chat_logs = ctk.CTkTextbox(chat_card, height=160, width=340, fg_color=self.theme["input_bg"], border_width=1, border_color=self.theme["border"], font=("Roboto", 12))
        self.txt_chat_logs.pack(padx=15, pady=5)
        self.txt_chat_logs.insert("0.0", f"🐾 {nombre_mascota}: ¡Hola! Estoy aquí para escucharte sin juzgarte. ¿Cómo te sientes el día de hoy con la universidad o tus metas? ❤️\n\n")
        self.txt_chat_logs.configure(state="disabled")

        # Entrada del Chat
        f_chat_input = ctk.CTkFrame(chat_card, fg_color="transparent")
        f_chat_input.pack(fill="x", padx=15, pady=5)
        self.entry_msg = ctk.CTkEntry(f_chat_input, placeholder_text="Desahógate aquí...", height=32)
        self.entry_msg.pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        self.btn_send = ctk.CTkButton(f_chat_input, text="✈", width=40, height=32, font=("Arial", 14), command=self.enviar_mensaje_chat_ia)
        self.btn_send.pack(side="right")

        # =========================================================
        # 👉 COLUMNA DERECHA: INTERVENCIÓN TCC, ALARMAS Y CRISIS
        # =========================================================
        right_column = ctk.CTkFrame(split_layout, fg_color="transparent")
        right_column.grid(row=0, column=1, sticky="nsew", padx=(10, 0))

        # Tarjeta 3: Ejercicios Validadores TCC y Meditación Guiada
        tcc_card = ctk.CTkFrame(right_column, fg_color=self.theme["card"], corner_radius=15, border_width=1, border_color=self.theme["border"])
        tcc_card.pack(fill="x", pady=5, ipady=8)
        
        ctk.CTkLabel(tcc_card, text="🧘‍♀️ Intervención TCC y Respiración", font=("Roboto", 14, "bold")).pack(anchor="w", padx=15, pady=2)
        
        # Caja de instrucción TCC dinámica
        self.lbl_tcc_instruccion = ctk.CTkLabel(tcc_card, text="🌬️ Ejercicio del Ritmo 4-4-4:\nInhala paz, retén un instante y exhala toda la tensión acumulada.", font=("Roboto", 11, "italic"), text_color=self.theme["text_secondary"], wraplength=340, justify="left")
        self.lbl_tcc_instruccion.pack(anchor="w", padx=15, pady=4)

        # Cronómetro e indicador de respiración
        self.lbl_timer = ctk.CTkLabel(tcc_card, text="Fase: Inhala | 4s", font=("Roboto", 13, "bold"), text_color=self.theme["primary"])
        self.lbl_timer.pack(pady=4)

        self.btn_respirar = ctk.CTkButton(tcc_card, text="▶ Iniciar Sesión de Respiración", font=("Roboto", 12, "bold"), height=28, command=self.toggle_sesion_respiracion)
        self.btn_respirar.pack(pady=4, padx=15, fill="x")

        # Tarjeta 4: Diario de Medicación y Recordatorios de Pausas
        reminders_card = ctk.CTkFrame(right_column, fg_color=self.theme["card"], corner_radius=15, border_width=1, border_color=self.theme["border"])
        reminders_card.pack(fill="x", pady=4, ipady=5)
        ctk.CTkLabel(reminders_card, text="🔔 Alertas y Recordatorios Clínicos", font=("Roboto", 14, "bold")).pack(anchor="w", padx=15, pady=2)

        cb_pausa = ctk.CTkCheckBox(reminders_card, text="Avisos automáticos para Pausas Activas (Cada 2h) 🧘‍♂️", font=("Roboto", 11))
        cb_pausa.pack(anchor="w", padx=15, pady=4)
        cb_pausa.select()

        cb_meds = ctk.CTkCheckBox(reminders_card, text="Recordatorio de Medicamentos / Suplementos Diarios 💊", font=("Roboto", 11))
        cb_meds.pack(anchor="w", padx=15, pady=4)

        # 🚨 TARJETA 5: PROTOCOLO DE CRISIS (BOTÓN DE ALTO CONTRASTE PREMIUM)
        crisis_card = ctk.CTkFrame(right_column, fg_color="#2A1418", corner_radius=15, border_width=1, border_color="#FF4C4C")
        crisis_card.pack(fill="x", pady=4, ipady=8)
        
        ctk.CTkLabel(crisis_card, text="🚨 Protocolo de Emergencia y Soporte", font=("Roboto", 13, "bold"), text_color="#FF4C4C").pack(anchor="w", padx=15, pady=2)
        ctk.CTkLabel(crisis_card, text="Si estás experimentando un momento crítico, no estás solo. Cuentas con apoyo profesional inmediato.", font=("Roboto", 11), text_color="#E9B0B7", wraplength=340, justify="left").pack(anchor="w", padx=15)
        
        ctk.CTkButton(
            crisis_card, text="📞 Línea de Prevención al Suicidio (Marcación 106 / WhatsApp)", font=("Roboto", 12, "bold"),
            fg_color="#FF4C4C", hover_color="#B33636", text_color="#FFFFFF", height=32,
            command=lambda: messagebox.showinfo("Líneas de Atención", "🇨🇴 Conexión de Emergencia (Colombia):\n\n• Línea Nacional: 106\n• Línea Salvavidas: 300 754 8933\n\nTu vida es valiosa. Profesionales de la salud te atienden 24/7.")
        ).pack(fill="x", padx=15, pady=6)

        # BOTONERA DOBLE DE REGISTRO
        botones_frame = ctk.CTkFrame(right_column, fg_color="transparent")
        botones_frame.pack(fill="x", pady=10)
        botones_frame.grid_columnconfigure(0, weight=1)
        botones_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkButton(botones_frame, text="💾 Guardar Estado Emocional", font=("Roboto", 13, "bold"), height=38, fg_color=self.theme["primary"], hover_color=self.theme["btn_hover"], command=self.guardar_salud_mental_bd).grid(row=0, column=0, padx=5, sticky="ew")
        ctk.CTkButton(botones_frame, text="🧹 Vaciar Registro", font=("Roboto", 13, "bold"), height=38, fg_color="transparent", border_width=2, border_color="#ff4c4c", text_color="#ff4c4c", hover_color="#331414", command=self.vaciar_salud_mental_bd).grid(row=0, column=1, padx=5, sticky="ew")

    # =========================================================
    # 🤖 CHAT CON LA MASCOTA EN TIEMPO REAL USANDO GEMINI IA
    # =========================================================
    def enviar_mensaje_chat_ia(self):
        msg = self.entry_msg.get().strip()
        if not msg: return

        # Imprimimos tu mensaje en la bitácora del log
        self.txt_chat_logs.configure(state="normal")
        self.txt_chat_logs.insert(ctk.END, f"👤 Tú: {msg}\n\n")
        self.txt_chat_logs.configure(state="disabled")
        self.txt_chat_logs.see(ctk.END)
        self.entry_msg.delete(0, ctk.END)

        self.btn_send.configure(state="disabled")
        threading.Thread(target=self.hilo_chat_gemini, args=(msg,)).start()

    def hilo_chat_gemini(self, msg_usuario):
        nombre_mascota = self.user.get("avatar_name", "Jaina")
        try:
            client = genai.Client(api_key=self.gemini_key)
            
            prompt_contexto = (
                f"Actúa como un tierno, cariñoso y empático perrito de apoyo emocional llamado {nombre_mascota}. "
                f"Estás hablando con tu dueño universitario. Escucha sus quejas, dale mucho amor de mascota, "
                f"mueve la colita de forma escrita y usa técnicas sutiles de Terapia Cognitivo-Conductual "
                f"para validar sus sentimientos sin dar diagnósticos médicos rígidos. Responde de forma amorosa y breve. "
                f"Mensaje del usuario: {msg_usuario}"
            )

            response = client.models.generate_content(model="gemini-2.5-flash", contents=[prompt_contexto])
            respuesta_ia = response.text.strip()
            
            self.app.after(0, lambda: self.inyectar_respuesta_chat(respuesta_ia))
            
        except Exception as e:
            # Fallback local amigable por si la API satura
            self.app.after(0, lambda: self.inyectar_respuesta_chat(f"🐾 *Mueve la colita y pone su cabecita en tu rodilla* Te escucho perfectamente y estoy aquí contigo. No estás solo en esto. 💕"))
        finally:
            self.app.after(0, lambda: self.btn_send.configure(state="normal"))

    def inyectar_respuesta_chat(self, texto):
        nombre_mascota = self.user.get("avatar_name", "Jaina")
        self.txt_chat_logs.configure(state="normal")
        self.txt_chat_logs.insert(ctk.END, f"🐾 {nombre_mascota}: {texto}\n\n")
        self.txt_chat_logs.configure(state="disabled")
        self.txt_chat_logs.see(ctk.END)

    # =========================================================
    # 🌬️ CRONÓMETRO DE RESPIRACIÓN CIRCADIANA GUIADA
    # =========================================================
    def toggle_sesion_respiracion(self):
        if not self.respirando:
            self.respirando = True
            self.btn_respirar.configure(text="⏸ Detener Sesión", fg_color="#ff4c4c")
            threading.Thread(target=self.hilo_respiracion_bucle).start()
        else:
            self.respirando = False
            self.btn_respirar.configure(text="▶ Iniciar Sesión de Respiración", fg_color=self.theme["primary"])
            self.lbl_timer.configure(text="Fase: Inhala | 4s")

    def hilo_respiracion_bucle(self):
        fases = [("Inhala 🌌", 4), ("Retén 🧘‍♂️", 4), ("Exhala 🍃", 4)]
        idx = 0
        while self.respirando:
            fase_nombre, secs = fases[idx]
            for s in range(secs, 0, -1):
                if not self.respirando: return
                self.app.after(0, lambda f=fase_nombre, sec=s: self.lbl_timer.configure(text=f"Fase: {f} | {sec}s"))
                time.sleep(1.0)
            idx = (idx + 1) % len(fases)

    # =========================================================
    # 💾 GUARDA Y VACIADO FÍSICO SQLITE
    # =========================================================
    def guardar_salud_mental_bd(self):
        try:
            user_id = self.user.get("id")
            animo = self.combo_animo.get()
            estres = self.slider_estres.get()
            sintoma = self.combo_sintoma.get()

            # Estado de ánimo, estrés y síntomas se guardan como una sola unidad.
            self.db.replace_daily_records(user_id, ("Mente_Animo", "Mente_Estres", "Mente_Sintomas"),
                (("Mente_Animo", 0.0, animo),
                 ("Mente_Estres", float(estres), "Escala 1-10"),
                 ("Mente_Sintomas", 0.0, sintoma)))
            
            messagebox.showinfo("Métricas Sincronizadas", "¡Tus variables emocionales e indicadores de tensión física se han guardado con éxito! 🚀")
            self.app.show_dashboard()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def vaciar_salud_mental_bd(self):
        confirmar = messagebox.askyesno("Vaciar Registro", "¿Deseas restablecer las métricas de salud mental de hoy?")
        if confirmar:
            try:
                user_id = self.user.get("id")
                self.db.execute_query("DELETE FROM health_records WHERE user_id = ? AND tipo LIKE 'Mente_%' AND date(fecha) = date('now')", (user_id,))
                self.animo_actual = "Neutral"
                self.nivel_estres = 5
                self.sintoma_fisico = "Ninguno"
                self.build_ui()
            except Exception as e:
                messagebox.showerror("Error", str(e))
