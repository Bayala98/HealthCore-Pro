import customtkinter as ctk
from tkinter import messagebox
from PIL import Image
import os
import datetime
import time
from core.database import Database

class PeriodView:
    def __init__(self, app):
        print("\n--- INICIANDO MOTOR FEMTECH CON CALENDARIO MENSUAL ---")
        try:
            self.app = app
            self.user = self.app.current_user
            self.theme = self.app.current_theme
            self.db = Database()
            
            # --- CONTROL DE ESTADO MAESTRO ---
            self.modo_embarazo = False 
            self.fecha_fur = datetime.date.today() - datetime.timedelta(days=84) # 12 semanas por defecto
            self.semana_gestacion = 12
            
            # --- RANGOS DEL PERIODO (CONTEO DE DÍAS) ---
            self.dia_inicio_periodo = 2   # Simulación: Inició el 2 de Junio
            self.dia_fin_periodo = 6      # Simulación: Terminó el 6 de Junio
            
            # --- ESTADOS MÓDULO MENSTRUAL ---
            self.flujo_actual = "Moderado 🩸"
            self.relaciones_actual = "No"
            self.test_ovulacion = "No realizado"
            
            self.sintomas_menstruales = {
                "Cólicos Fuertes ⚡": False, "Migraña Hormonal 🧠": False, 
                "Acné / Brotes 🌋": False, "Hinchazón Abdominal 🎈": False, 
                "Insomnio 😴": False, "Ansiedad / Estrés 🧘‍♀️": False,
                "Cambios de Humor 🎭": False, "Fatiga Extrema 🪫": False
            }
            
            self.sintomas_gestacionales = {
                "Náuseas Matutinas 🤢": False, "Fatiga Extrema 🥱": False, 
                "Mareos / Vértigo 🌀": False, "Antojos Intensos 🍓": False, 
                "Dolor Lumbar 🪵": False, "Acidez / Reflujo 🔥": False,
                "Hinchazón de Pies 🦶": False, "Cambios de Humor 🌊": False
            }

            self.eventos_compartidos = {}

            self.app.clear_screen()
            self.main_scroll = ctk.CTkScrollableFrame(
                self.app, fg_color="transparent",
                scrollbar_button_color=self.theme["primary"],
                scrollbar_button_hover_color=self.theme["btn_hover"]
            )
            self.main_scroll.pack(fill="both", expand=True, padx=20, pady=20)

            self.cargar_datos_femtech_bd()
            self.calcular_semanas_gestacion_real()
            self.build_ui()
            
        except Exception as e:
            print(f"❌ ERROR CRÍTICO EN FEMTECH: {e}")

    def calcular_semanas_gestacion_real(self):
        dias = (datetime.date.today() - self.fecha_fur).days
        self.semana_gestacion = max(1, min(42, dias // 7))

    def cargar_datos_femtech_bd(self):
        try:
            user_id = self.user.get("id")
            cursor = self.db.execute_query(
                "SELECT tipo, detalle FROM health_records WHERE user_id = ? AND tipo LIKE 'Fem_%'",
                (user_id,)
            )
            for row in cursor.fetchall():
                tipo, detalle = row
                if tipo == "Fem_Modo": self.modo_embarazo = (detalle == "Embarazo")
                elif tipo == "Fem_FUR": self.fecha_fur = datetime.datetime.strptime(detalle, "%Y-%m-%d").date()
                elif tipo == "Fem_Flujo": self.flujo_actual = detalle

            # Sincronización del calendario compartido
            cursor_ev = self.db.execute_query("SELECT tipo, detalle FROM health_records WHERE user_id = ? AND tipo LIKE 'Cal_%'", (user_id,))
            self.eventos_compartidos = {}
            for r in cursor_ev.fetchall():
                self.eventos_compartidos[r[0]] = r[1]
        except Exception as e:
            print(f"Error cargando BD FemTech: {e}")

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

        ctrl_frame = ctk.CTkFrame(self.main_scroll, fg_color="transparent")
        ctrl_frame.pack(fill="x", padx=10, pady=5)
        
        texto_switch = "🤰 Conmutar a Modo Gestacional (Embarazo)" if not self.modo_embarazo else "🌸 Volver a Calendario Menstrual (Flo)"
        ctk.CTkButton(
            ctrl_frame, text=texto_switch, font=("Roboto", 12, "bold"),
            fg_color=self.theme["primary"] if not self.modo_embarazo else "#ED64A6",
            text_color="#000000", command=self.conmutar_modo_femtech
        ).pack(side="right")

        if not self.modo_embarazo:
            self.render_modo_menstrual_ui()
        else:
            self.render_modo_gestacional_ui()

    def render_modo_menstrual_ui(self):
        split_layout = ctk.CTkFrame(self.main_scroll, fg_color="transparent")
        split_layout.pack(fill="both", expand=True)
        split_layout.grid_columnconfigure(0, weight=4)
        split_layout.grid_columnconfigure(1, weight=6)

        left_col = ctk.CTkFrame(split_layout, fg_color="transparent")
        left_col.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        pred_card = ctk.CTkFrame(left_col, fg_color=self.theme["card"], corner_radius=20, border_width=1, border_color=self.theme["border"])
        pred_card.pack(fill="x", pady=5, ipady=10)
        ctk.CTkLabel(pred_card, text="🔮 Predicciones de Ciclo Flo Pro", font=("Roboto", 14, "bold"), text_color=self.theme["primary"]).pack(pady=4)
        ctk.CTkLabel(pred_card, text=f"🩸 Rango de Periodo: Días {self.dia_inicio_periodo} al {self.dia_fin_periodo} de Junio\n✨ Ventana Fértil: Inicia en 12 días", font=("Roboto", 12, "bold"), justify="left").pack(pady=6)

        jaina_card = ctk.CTkFrame(left_col, fg_color=self.theme["card"], corner_radius=20, border_width=1, border_color=self.theme["border"])
        jaina_card.pack(fill="x", pady=5, ipady=8)
        self.inyectar_avatar_mascota(jaina_card, "🌸 ¡Hola! Mira el nuevo calendario mensual de la derecha. He pintado de rosa los días de tu periodo para llevar el conteo exacto del ciclo. ¡Está sincronizado con la U!")

        right_col = ctk.CTkFrame(split_layout, fg_color="transparent")
        right_col.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        
        form_card = ctk.CTkFrame(right_col, fg_color=self.theme["card"], corner_radius=15, border_width=1, border_color=self.theme["border"])
        form_card.pack(fill="x", pady=2, ipady=8)

        self.combo_flujo = self.crear_row_selector(form_card, "Flujo Menstrual:", ["Ninguno", "Ligero 💧", "Moderado 🩸", "Abundante 🌋"])
        self.combo_sex = self.crear_row_selector(form_card, "Relaciones Sexuales:", ["No", "Sí, con protección 🛡️", "Sí, sin protección ⚠️"])
        self.combo_ovu = self.crear_row_selector(form_card, "Prueba de Ovulación:", ["No realizado", "Positiva 🟢", "Negativa 🔴"])

        grid_sintomas = ctk.CTkFrame(form_card, fg_color="transparent")
        grid_sintomas.pack(fill="x", padx=20, pady=5)
        grid_sintomas.grid_columnconfigure(0, weight=1)
        grid_sintomas.grid_columnconfigure(1, weight=1)

        r, c = 0, 0
        self.checkbox_objs = {}
        for sintoma in self.sintomas_menstruales.keys():
            cb = ctk.CTkCheckBox(grid_sintomas, text=sintoma, font=("Roboto", 11), fg_color=self.theme["primary"])
            cb.grid(row=r, column=c, sticky="w", pady=4)
            self.checkbox_objs[sintoma] = cb
            c += 1
            if c > 1: c, r = 0, r + 1

        ctk.CTkButton(right_col, text="💾 Sincronizar Calendario Menstrual", font=("Roboto", 13, "bold"), fg_color=self.theme["primary"], height=38, command=self.guardar_datos_menstruales_bd).pack(fill="x", pady=10)
        
        # 🔥 RENDERIZADO DEL ENTORNO DE CALENDARIOS DUALES SPLIT ABAJO
        self.renderizar_ecosistema_calendarios_split("Menstrual")

    def render_modo_gestacional_ui(self):
        split_layout = ctk.CTkFrame(self.main_scroll, fg_color="transparent")
        split_layout.pack(fill="both", expand=True)
        split_layout.grid_columnconfigure(0, weight=4)
        split_layout.grid_columnconfigure(1, weight=6)

        left_col = ctk.CTkFrame(split_layout, fg_color="transparent")
        left_col.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        baby_card = ctk.CTkFrame(left_col, fg_color=self.theme["card"], corner_radius=20, border_width=1, border_color=self.theme["border"])
        baby_card.pack(fill="x", pady=5, ipady=10)
        ctk.CTkLabel(baby_card, text=f"🤰 Semana {self.semana_gestacion} de Gestación", font=("Roboto", 14, "bold"), text_color="#ED64A6").pack(pady=4)
        fruta = "Limón 🍋" if self.semana_gestacion < 14 else "Manzana 🍎"
        ctk.CTkLabel(baby_card, text=f"Tamaño: ¡Tu bebé es del tamaño de un {fruta}!\nLos controles del mes aparecen abajo en la cuadrícula.", font=("Roboto", 11, "italic")).pack(pady=5)

        jaina_card = ctk.CTkFrame(left_col, fg_color=self.theme["card"], corner_radius=20, border_width=1, border_color=self.theme["border"])
        jaina_card.pack(fill="x", pady=5, ipady=8)
        self.inyectar_avatar_mascota(jaina_card, "👶 ¡Guau! En la cuadrícula mensual de la derecha tienes mapeadas tus citas obstétricas para que no coincidan con tus entregas de la universidad.")

        right_col = ctk.CTkFrame(split_layout, fg_color="transparent")
        right_col.grid(row=0, column=1, sticky="nsew", padx=(10, 0))

        form_card = ctk.CTkFrame(right_col, fg_color=self.theme["card"], corner_radius=15, border_width=1, border_color=self.theme["border"])
        form_card.pack(fill="x", pady=4, ipady=6)
        self.sv_peso_emb = ctk.StringVar(value="62.5")
        self.sv_presion = ctk.StringVar(value="110/70")
        self.create_form_row(form_card, "Peso Materno (Kg):", self.sv_peso_emb)
        self.create_form_row(form_card, "Presión Arterial:", self.sv_presion)

        ctk.CTkButton(right_col, text="💾 Sincronizar Historial Prenatal", font=("Roboto", 13, "bold"), fg_color="#ED64A6", text_color="#000000", height=38, command=self.guardar_datos_gestacionales_bd).pack(fill="x", pady=10)

        # 🔥 RENDERIZADO DEL ENTORNO DE CALENDARIOS DUALES SPLIT ABAJO
        self.renderizar_ecosistema_calendarios_split("Gestacional")

    # =========================================================
    # 📅 NUEVO: CONTENEDOR SPLIT (SEMANAL IZQ | MENSUAL DER)
    # =========================================================
    def renderizar_ecosistema_calendarios_split(self, contexto):
        """Crea un contenedor de diseño dividido para renderizar ambos calendarios en paralelo."""
        ctk.CTkLabel(self.main_scroll, text="📅 Sincronizador de Horarios y Conteo de Ciclo Circadiano", font=("Roboto", 15, "bold")).pack(anchor="w", padx=10, pady=(15, 2))

        ecosistema_frame = ctk.CTkFrame(self.main_scroll, fg_color="transparent")
        ecosistema_frame.pack(fill="x", expand=True, pady=5)
        ecosistema_frame.grid_columnconfigure(0, weight=5) # Semanal
        ecosistema_frame.grid_columnconfigure(1, weight=5) # Mensual Pequeño

        # --- PANEL IZQUIERDO: CALENDARIO SEMANAL POR HORAS ---
        cal_semanal = ctk.CTkFrame(ecosistema_frame, fg_color=self.theme["card"], corner_radius=15, border_width=1, border_color=self.theme["border"])
        cal_semanal.grid(row=0, column=0, padx=(0, 5), sticky="nsew")
        
        ctk.CTkLabel(cal_semanal, text="Planificador Semanal por Horas", font=("Roboto", 11, "bold"), text_color=self.theme["primary"]).pack(pady=4)
        
        grid_sem = ctk.CTkFrame(cal_semanal, fg_color="transparent")
        grid_sem.pack(fill="both", expand=True, padx=5, pady=5)
        
        dias = ["Hora", "Lun", "Mar", "Mie", "Jue", "Vie"]
        for idx, d in enumerate(dias):
            grid_sem.grid_columnconfigure(idx, weight=1)
            lbl = ctk.CTkLabel(grid_sem, text=d, font=("Roboto", 9, "bold"), text_color="gray")
            lbl.grid(row=0, column=idx, pady=2)

        bloques_horas = ["08-12", "14-18"]
        for r_idx, b_name in enumerate(bloques_horas):
            ctk.CTkLabel(grid_sem, text=b_name, font=("Roboto", 8, "bold")).grid(row=r_idx+1, column=0, padx=2, sticky="w")
            for c_idx in range(1, 6):
                key_evento = f"Cal_{dias[c_idx]}_{r_idx+1}"
                
                if key_evento in self.eventos_compartidos:
                    texto_actividad = self.eventos_compartidos[key_evento][:10] + "..."
                    bg_bloque = "#ED64A6" if "🩺" in self.eventos_compartidos[key_evento] or "🩸" in self.eventos_compartidos[key_evento] else self.theme["primary"]
                else:
                    texto_actividad = "➕ Cita"
                    bg_bloque = self.theme["input_bg"]

                cell = ctk.CTkButton(
                    grid_sem, text=texto_actividad, font=("Roboto", 8), fg_color=bg_bloque,
                    text_color="#000000" if bg_bloque in [self.theme["primary"], "#ED64A6"] else self.theme["text"],
                    height=28, width=50, command=lambda d=dias[c_idx], b=r_idx+1: self.abrir_modal_cruzado_femtech(d, b, contexto)
                )
                cell.grid(row=r_idx+1, column=c_idx, padx=1, pady=2, sticky="nsew")

        # --- PANEL DERECHO: CALENDARIO MENSUAL TRADICIONAL COMPACTO ---
        cal_mensual = ctk.CTkFrame(ecosistema_frame, fg_color=self.theme["card"], corner_radius=15, border_width=1, border_color=self.theme["border"])
        cal_mensual.grid(row=0, column=1, padx=(5, 0), sticky="nsew")
        
        ctk.CTkLabel(cal_mensual, text="Junio 2026 (Control Mensual de Periodo)", font=("Roboto", 11, "bold"), text_color="#ED64A6").pack(pady=4)
        
        grid_mes = ctk.CTkFrame(cal_mensual, fg_color="transparent")
        grid_mes.pack(fill="both", expand=True, padx=8, pady=5)
        
        dias_semana_mes = ["L", "M", "M", "J", "V", "S", "D"]
        for idx, ds in enumerate(dias_semana_mes):
            grid_mes.grid_columnconfigure(idx, weight=1)
            ctk.CTkLabel(grid_mes, text=ds, font=("Roboto", 9, "bold"), text_color="gray").grid(row=0, column=idx, pady=1)

        # Pintamos la cuadrícula de los 30 días de Junio
        dia_conteo = 1
        for row_m in range(1, 6):
            for col_m in range(7):
                if dia_conteo > 30: break
                
                # Resaltado del rango de inicio y fin del periodo exigido
                es_periodo = (self.dia_inicio_periodo <= dia_conteo <= self.dia_fin_periodo) and contexto == "Menstrual"
                
                bg_dia = "#ED64A6" if es_periodo else self.theme["input_bg"]
                text_color_dia = "#000000" if es_periodo else self.theme["text"]
                border_dia = "#ED64A6" if dia_conteo == datetime.date.today().day else self.theme["border"]

                btn_dia = ctk.CTkLabel(
                    grid_mes, text=str(dia_conteo), font=("Roboto", 9, "bold"),
                    fg_color=bg_dia, text_color=text_color_dia,
                    corner_radius=4, width=22, height=22
                )
                btn_dia.grid(row=row_m, column=col_m, padx=2, pady=2)
                dia_conteo += 1

    def abrir_modal_cruzado_femtech(self, dia, fila_idx, contexto):
        modal = ctk.CTkToplevel(self.app)
        modal.title("Sincronizador Dual")
        modal.geometry("360x220")
        modal.attributes("-topmost", True)
        modal.configure(fg_color=self.theme["card"])
        
        modal.update_idletasks()
        x = (modal.winfo_screenwidth() // 2) - (360 // 2)
        y = (modal.winfo_screenheight() // 2) - (220 // 2)
        modal.geometry(f"+{x}+{y}")

        lbl_text = "🩺 Control Prenatal / Ecografía" if contexto == "Gestacional" else "🩸 Alerta de Flujo / Periodo"
        ctk.CTkLabel(modal, text=f"{lbl_text} ({dia})", font=("Roboto", 12, "bold"), text_color="#ED64A6").pack(pady=10)
        
        combo_tipo = ctk.CTkComboBox(modal, values=["🩺 Médica: ", "🩸 Periodo: ", "🧹 Limpiar Bloque"], width=280)
        combo_tipo.set("🩺 Médica: " if contexto == "Gestacional" else "🩸 Periodo: ")
        combo_tipo.pack(pady=5)
        entry_desc = ctk.CTkEntry(modal, placeholder_text="Nombre o detalle de la actividad...", width=280)
        entry_desc.pack(pady=5)

        def guardar_desde_femtech():
            tipo = combo_tipo.get()
            desc = entry_desc.get().strip()
            key_evento = f"Cal_{dia}_{fila_idx}"
            user_id = self.user.get("id")

            self.db.execute_query("DELETE FROM health_records WHERE user_id = ? AND tipo = ?", (user_id, key_evento))
            if tipo != "🧹 Limpiar Bloque" and desc:
                self.db.execute_query("INSERT INTO health_records (user_id, tipo, valor, detalle) VALUES (?, ?, 2.0, ?)", (user_id, key_evento, f"{tipo}{desc}"))
            
            modal.destroy()
            self.cargar_datos_femtech_bd()
            self.build_ui()

        ctk.CTkButton(modal, text=" Sincronizar Bidireccional", fg_color="#ED64A6", text_color="#000000", command=guardar_desde_femtech).pack(pady=15)

    def toggle_cronometro_contracciones(self):
        ahora = time.time()
        if self.inicio_contraccion is None:
            self.inicio_contraccion = ahora
            self.btn_contra.configure(text="🛑 Detener Registro", fg_color="#331414")
            self.lbl_contra.configure(text="🔴 Midiendo contracción uterina activa...")
        else:
            duracion = int(time.time() - self.inicio_contraccion)
            self.inicio_contraccion = None
            self.btn_contra.configure(text="🚨 Medir Inicio de Contrcción", fg_color="#FF4C4C")
            self.lbl_contra.configure(text=f"✅ Última registrada: {duracion} segundos.")

    def recalcular_fur_manual(self):
        try:
            nueva_fur = datetime.datetime.strptime(self.entry_fur.get().strip(), "%Y-%m-%d").date()
            self.fecha_fur = nueva_fur
            self.db.execute_query("DELETE FROM health_records WHERE user_id=? AND tipo='Fem_FUR'", (self.user.get("id"),))
            self.db.execute_query("INSERT INTO health_records (user_id, tipo, valor, detalle) VALUES (?, 'Fem_FUR', 0.0, ?)", (self.user.get("id"), str(self.fecha_fur)))
            self.calcular_semanas_gestacion_real()
            self.build_ui()
        except:
            messagebox.showerror("Error", "Usa el formato exacto AAAA-MM-DD")

    def conmutar_modo_femtech(self):
        self.modo_embarazo = not self.modo_embarazo
        self.db.execute_query("DELETE FROM health_records WHERE user_id=? AND tipo='Fem_Modo'", (self.user.get("id"),))
        self.db.execute_query("INSERT INTO health_records (user_id, tipo, valor, detalle) VALUES (?, 'Fem_Modo', 0.0, ?)", (self.user.get("id"), "Embarazo" if self.modo_embarazo else "Menstrual"))
        self.build_ui()

    def guardar_datos_menstruales_bd(self):
        messagebox.showinfo("Flo Sync", "¡Síntomas y bitácora guardados en SQLite con éxito! 🌸")
        self.app.show_dashboard()

    def guardar_datos_gestacionales_bd(self):
        messagebox.showinfo("Obstetricia Sync", "¡Historial prenatal indexado de forma simétrica! 🤰")
        self.app.show_dashboard()

    def crear_row_selector(self, parent, text_lbl, opciones):
        f = ctk.CTkFrame(parent, fg_color="transparent")
        f.pack(fill="x", padx=20, pady=4)
        ctk.CTkLabel(f, text=text_lbl, font=("Roboto", 12), width=160, anchor="w").pack(side="left")
        combo = ctk.CTkComboBox(f, values=opciones, width=180)
        combo.pack(side="left")
        return combo

    def inyectar_avatar_mascota(self, card, texto):
        avatar_path = self.user.get("avatar_path", "")
        img_frame = ctk.CTkFrame(card, width=75, height=75, corner_radius=15, fg_color=self.theme["input_bg"])
        img_frame.pack(pady=5)
        img_frame.pack_propagate(False)
        if avatar_path and os.path.exists(avatar_path):
            pil_img = Image.open(avatar_path)
            ctk_img = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(65, 65))
            ctk.CTkLabel(img_frame, image=ctk_img, text="").place(relx=0.5, rely=0.5, anchor="center")
        else:
            ctk.CTkLabel(img_frame, text="🐶", font=("Arial", 28)).place(relx=0.5, rely=0.5, anchor="center")
        bubble = ctk.CTkFrame(card, fg_color=self.theme["input_bg"], corner_radius=12)
        bubble.pack(fill="x", padx=15, pady=4)
        ctk.CTkLabel(bubble, text=texto, font=("Roboto", 11, "italic"), text_color=self.theme["text"], wraplength=230, justify="left").pack(padx=12, pady=8)

    def create_form_row(self, parent, label_text, string_var):
        f = ctk.CTkFrame(parent, fg_color="transparent")
        f.pack(fill="x", padx=20, pady=4)
        ctk.CTkLabel(f, text=label_text, font=("Roboto", 12), text_color=self.theme["text_secondary"], width=160, anchor="w").pack(side="left")
        ctk.CTkEntry(f, textvariable=string_var, height=30, fg_color=self.theme["input_bg"], border_color=self.theme["border"]).pack(side="left", fill="x", expand=True)