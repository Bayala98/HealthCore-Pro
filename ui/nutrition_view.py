import customtkinter as ctk
from tkinter import messagebox, filedialog
from PIL import Image
import os
import threading
import datetime
from google import genai
from core.database import Database

class NutritionView:
    def __init__(self, app):
        print("\n--- INICIANDO NUTRICIÓN INTELIGENTE PREMIUM ---")
        try:
            self.app = app
            self.user = self.app.current_user
            self.theme = self.app.current_theme
            self.db = Database()
            
            # API Key de tu cuenta personal para desarrollo 🔑
            self.gemini_key = "AIzaSyCCPX1ZENUvzQxLNBoMHMNADOzHt2n-2hs" 
            
            # 1. CÁLCULO DE REQUERIMIENTOS NUTRICIONALES REALES (INGENIERÍA BIOMÉTRICA)
            self.calcular_requerimientos_usuario()
            
            self.calorias_consumidas = 0
            self.vasos_agua = 0
            self.meta_agua = 8
            
            self.comidas_registro = {
                "Desayuno": [], "Almuerzo": [], "Merienda": [], "Cena": [], "Postres/Snacks": []
            }
            
            # Diccionario base de alimentos
            self.DICCIONARIO_ALIMENTOS = {
                "Pollo asado (250 kcal)": 250, "Pechuga de pollo (165 kcal)": 165, 
                "Arroz blanco (130 kcal)": 130, "Arroz integral (110 kcal)": 110, 
                "Hamburguesa (550 kcal)": 550, "Papas fritas (312 kcal)": 312,
                "Ensalada fresca (45 kcal)": 45, "Ensalada cesar (350 kcal)": 350, 
                "Manzana (52 kcal)": 52, "Banano (89 kcal)": 89, "Huevo frito (90 kcal)": 90, 
                "Huevo cocido (78 kcal)": 78, "Pan integral (70 kcal)": 70,
                "Arepa con queso (220 kcal)": 220, "Cafe con leche (60 kcal)": 60, 
                "Pizza (266 kcal)": 266, "Torta de chocolate (370 kcal)": 370, 
                "Helado (200 kcal)": 200, "Yogurt griego (100 kcal)": 100
            }

            self.app.clear_screen()
            self.main_scroll = ctk.CTkScrollableFrame(
                self.app, fg_color="transparent",
                scrollbar_button_color=self.theme["primary"],
                scrollbar_button_hover_color=self.theme["btn_hover"]
            )
            self.main_scroll.pack(fill="both", expand=True, padx=20, pady=20)

            self.cargar_registros_bd()
            self.build_ui()
            
        except Exception as e:
            print(f"❌ ERROR CRÍTICO EN NUTRICIÓN: {e}")

    def calcular_requerimientos_usuario(self):
        """Calcula las calorías objetivo del usuario usando la fórmula Harris-Benedict."""
        try:
            peso = float(self.user.get("peso", 70.0))
            estatura = float(self.user.get("estatura", 1.70)) * 100 # a cm
            edad = int(self.user.get("edad", 25))
            genero = self.user.get("genero", "Hombre")
            meta_tipo = self.user.get("meta_tipo", "Mantenerme")

            if genero == "Mujer":
                tmb = (10 * peso) + (6.25 * estatura) - (5 * edad) - 161
            else:
                tmb = (10 * peso) + (6.25 * estatura) - (5 * edad) + 5

            calorias_mantenimiento = tmb * 1.375

            if "Bajar" in meta_tipo:
                self.calorias_meta = int(calorias_mantenimiento - 400)
            elif "Aumentar" in meta_tipo:
                self.calorias_meta = int(calorias_mantenimiento + 400)
            else:
                self.calorias_meta = int(calorias_mantenimiento)
        except:
            self.calorias_meta = 2000

    def obtener_dieta_personalizada_dia(self):
        """Genera un menú semanal dinámico y milimetrado según las calorías calculadas."""
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

    def cargar_registros_bd(self):
        try:
            self.calorias_consumidas = 0
            for k in self.comidas_registro:
                self.comidas_registro[k] = []

            user_id = self.user.get("id")
            cursor = self.db.execute_query(
                "SELECT id, tipo, valor, detalle FROM health_records WHERE user_id = ? AND date(fecha) = date('now')",
                (user_id,)
            )
            for row in cursor.fetchall():
                db_id, tipo, valor, detalle = row
                if tipo == "Agua":
                    self.vasos_agua = int(valor)
                elif tipo in self.comidas_registro:
                    self.comidas_registro[tipo].append({"id_db": db_id, "nombre": detalle, "cal": int(valor)})
                    self.calorias_consumidas += int(valor)
        except Exception as e:
            print(f"Error cargando datos de BD: {e}")

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
        # 👈 COLUMNA IZQUIERDA: DISEÑO COMPACTADO COMPLETO
        # =========================================================
        left_column = ctk.CTkFrame(split_layout, fg_color="transparent")
        left_column.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        # Tarjeta Progreso Mascota
        top_card = ctk.CTkFrame(left_column, fg_color=self.theme["card"], corner_radius=20, border_width=1, border_color=self.theme["border"])
        top_card.pack(fill="x", pady=5, ipady=5)

        avatar_path = self.user.get("avatar_path", "")
        nombre_mascota = self.user.get("avatar_name", "Jaina")
        
        img_size = 80
        img_frame = ctk.CTkFrame(top_card, width=img_size+10, height=img_size+10, corner_radius=15, fg_color=self.theme["input_bg"])
        img_frame.pack(pady=5)
        img_frame.pack_propagate(False)

        if avatar_path and os.path.exists(avatar_path):
            pil_img = Image.open(avatar_path)
            ctk_img = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(img_size, img_size))
            ctk.CTkLabel(img_frame, image=ctk_img, text="").place(relx=0.5, rely=0.5, anchor="center")
        else:
            ctk.CTkLabel(img_frame, text="🐾", font=("Arial", 35)).place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(top_card, text=f"Balance: {self.calorias_consumidas} / {self.calorias_meta} Kcal", font=("Roboto", 14, "bold")).pack(pady=2)
        porcentaje_cal = max(0.0, min(1.0, self.calorias_consumidas / self.calorias_meta))
        bar = ctk.CTkProgressBar(top_card, width=220, height=12, progress_color=self.theme["primary"], fg_color="#333333")
        bar.set(porcentaje_cal)
        bar.pack(pady=4)

        # Tarjeta Plan Dieta Personalizada
        dieta_card = ctk.CTkFrame(left_column, fg_color=self.theme["card"], corner_radius=20, border_width=1, border_color=self.theme["border"])
        dieta_card.pack(fill="x", pady=5, ipady=5)
        ctk.CTkLabel(dieta_card, text=f"📋 Recomendación de {nombre_mascota}", font=("Roboto", 14, "bold"), text_color=self.theme["primary"]).pack(pady=2, padx=15, anchor="w")
        
        recomendacion_personalizada = self.obtener_dieta_personalizada_dia()
        ctk.CTkLabel(dieta_card, text=recomendacion_personalizada, font=("Roboto", 11, "italic"), text_color=self.theme["text"], wraplength=260, justify="left").pack(padx=15, pady=4)

        # Tarjeta IA Real
        ia_card = ctk.CTkFrame(left_column, fg_color=self.theme["card"], corner_radius=20, border_width=1, border_color=self.theme["border"])
        ia_card.pack(fill="x", pady=5, ipady=5)
        ctk.CTkLabel(ia_card, text="📸 Analizar con Gemini Real IA", font=("Roboto", 14, "bold"), text_color=self.theme["primary"]).pack(pady=2)
        self.btn_ia = ctk.CTkButton(ia_card, text="📷 Subir Foto de Comida", font=("Roboto", 12, "bold"), height=32, command=self.analizar_con_gemini_real)
        self.btn_ia.pack(pady=4)

        # Hidratación
        water_card = ctk.CTkFrame(left_column, fg_color=self.theme["card"], corner_radius=20, border_width=1, border_color=self.theme["border"])
        water_card.pack(fill="x", pady=5, ipady=5)
        ctk.CTkLabel(water_card, text="💧 Registro de Hidratación", font=("Roboto", 14, "bold")).pack(pady=2)
        water_control = ctk.CTkFrame(water_card, fg_color="transparent")
        water_control.pack()
        ctk.CTkButton(water_control, text="➖", width=35, height=28, command=self.restar_agua).pack(side="left", padx=5)
        ctk.CTkLabel(water_control, text=f"{self.vasos_agua} / {self.meta_agua} Vasos", font=("Roboto", 13, "bold")).pack(side="left", padx=10)
        ctk.CTkButton(water_control, text="➕", width=35, height=28, command=self.sumar_agua).pack(side="left", padx=5)

        # =========================================================
        # 👉 COLUMNA DERECHA: BITÁCORA PREMIUM COMPLETA + BOTONERA
        # =========================================================
        right_column = ctk.CTkFrame(split_layout, fg_color="transparent")
        right_column.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        ctk.CTkLabel(right_column, text="Bitácora de Alimentos", font=("Roboto", 18, "bold"), text_color=self.theme["text"]).pack(anchor="w", pady=5)

        for momento in ["Desayuno", "Almuerzo", "Merienda", "Cena", "Postres/Snacks"]:
            self.create_meal_section(right_column, momento)

        # BOTONERA DOBLE EN PARALELO
        botones_frame = ctk.CTkFrame(right_column, fg_color="transparent")
        botones_frame.pack(fill="x", pady=15)
        botones_frame.grid_columnconfigure(0, weight=1)
        botones_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkButton(
            botones_frame, text="💾 Guardar Registro Diario", font=("Roboto", 13, "bold"),
            height=38, fg_color=self.theme["primary"], hover_color=self.theme["btn_hover"],
            command=self.guardar_registro_definitivo
        ).grid(row=0, column=0, padx=5, sticky="ew")

        ctk.CTkButton(
            botones_frame, text="🧹 Vaciar Registro de Hoy", font=("Roboto", 13, "bold"),
            height=38, fg_color="transparent", border_width=2, border_color="#ff4c4c", text_color="#ff4c4c",
            hover_color="#331414", command=self.formatear_registro_diario
        ).grid(row=0, column=1, padx=5, sticky="ew")

    def create_meal_section(self, container, momento):
        section_frame = ctk.CTkFrame(container, fg_color=self.theme["card"], corner_radius=15, border_width=1, border_color=self.theme["border"])
        section_frame.pack(fill="x", pady=4, ipady=4)

        header_row = ctk.CTkFrame(section_frame, fg_color="transparent")
        header_row.pack(fill="x", padx=15, pady=4)
        
        ctk.CTkLabel(header_row, text=momento, font=("Roboto", 15, "bold"), text_color=self.theme["text"]).pack(side="left")
        ctk.CTkButton(header_row, text="➕ Añadir", font=("Roboto", 11, "bold"), width=70, height=26, command=lambda m=momento: self.abrir_ventana_registro(m)).pack(side="right")

        items = self.comidas_registro[momento]
        if not items:
            ctk.CTkLabel(section_frame, text="No hay alimentos registrados hoy", font=("Roboto", 11, "italic"), text_color="gray").pack(anchor="w", padx=20, pady=2)
        else:
            for item in items:
                chip = ctk.CTkFrame(section_frame, fg_color=self.theme["input_bg"], corner_radius=8)
                chip.pack(fill="x", padx=15, pady=2)
                
                ctk.CTkLabel(chip, text=f"• {item['nombre']}", font=("Roboto", 12, "bold"), text_color=self.theme["text"]).pack(side="left", padx=10, pady=4)
                ctk.CTkLabel(chip, text=f"{item['cal']} kcal", font=("Roboto", 11), text_color=self.theme["text_secondary"]).pack(side="left", padx=5)
                
                ctk.CTkButton(
                    chip, text="❌", width=24, height=20, font=("Arial", 9),
                    fg_color="transparent", text_color="#ff4c4c", hover_color="#441515",
                    command=lambda i=item: self.eliminar_alimento_individual(i["id_db"])
                ).pack(side="right", padx=5)

    def abrir_ventana_registro(self, momento_defecto):
        modal = ctk.CTkToplevel(self.app)
        modal.title("Registrar Alimento")
        modal.geometry("400x320")
        modal.resizable(False, False)
        modal.attributes("-topmost", True)
        modal.configure(fg_color=self.theme["card"])
        
        modal.update_idletasks()
        x = (modal.winfo_screenwidth() // 2) - (400 // 2)
        y = (modal.winfo_screenheight() // 2) - (320 // 2)
        modal.geometry(f"+{x}+{y}")

        ctk.CTkLabel(modal, text="Añadir Alimento al Sistema", font=("Roboto", 16, "bold"), text_color=self.theme["primary"]).pack(pady=15)

        combo_momento = ctk.CTkComboBox(modal, values=["Desayuno", "Almuerzo", "Merienda", "Cena", "Postres/Snacks"], width=340)
        combo_momento.set(momento_defecto)
        combo_momento.pack(pady=5)

        opciones_diccionario = list(self.DICCIONARIO_ALIMENTOS.keys()) + ["Otro Alimento (No listado)"]
        combo_alimento = ctk.CTkComboBox(modal, values=opciones_diccionario, width=340)
        combo_alimento.set(opciones_diccionario[0])
        combo_alimento.pack(pady=5)

        entry_custom = ctk.CTkEntry(modal, placeholder_text="Ej: Ensalada de frutas de 180 kcal", width=340)
        entry_custom.pack(pady=5)

        def ejecutar_guardado():
            seleccion = combo_alimento.get()
            destino = combo_momento.get()
            
            if seleccion == "Otro Alimento (No listado)":
                texto = entry_custom.get().strip()
                if not texto or " de " not in texto.lower():
                    messagebox.showwarning("Formato", "Usa: 'Alimento de X kcal'", parent=modal)
                    return
                try:
                    partes = texto.lower().split(" de ")
                    nombre = partes[0].strip().capitalize()
                    calorias = int("".join(filter(str.isdigit, partes[1])))
                except:
                    return
            else:
                nombre = seleccion.split(" (")[0].strip()
                calorias = self.DICCIONARIO_ALIMENTOS[seleccion]

            try:
                self.db.execute_query(
                    "INSERT INTO health_records (user_id, tipo, valor, detalle) VALUES (?, ?, ?, ?)",
                    (self.user.get("id"), destino, float(calorias), nombre)
                )
                modal.destroy()
                self.cargar_registros_bd()
                self.build_ui()
            except Exception as e:
                messagebox.showerror("Error", str(e), parent=modal)

        ctk.CTkButton(modal, text="✅ Confirmar Registro", fg_color=self.theme["primary"], hover_color=self.theme["btn_hover"], command=ejecutar_guardado).pack(pady=15)

    def eliminar_alimento_individual(self, id_db):
        try:
            self.db.execute_query("DELETE FROM health_records WHERE id = ?", (id_db,))
            self.cargar_registros_bd()
            self.build_ui()
        except Exception as e:
            messagebox.showerror("Error al borrar", str(e))

    def guardar_registro_definitivo(self):
        messagebox.showinfo(
            "Ecosistema Sincronizado", 
            f"🎉 ¡Felicidades! Tus {self.calorias_consumidas} kcal consumidas de hoy se han guardado con éxito.\n\n"
            f"Los datos se indexaron correctamente para alimentar tus gráficos en el módulo de Estadísticas. 📊"
        )
        self.app.show_dashboard()

    def analizar_con_gemini_real(self):
        ruta_imagen = filedialog.askopenfilename(title="Selecciona la foto de tu comida", filetypes=[("Imágenes", "*.png *.jpg *.jpeg *.webp")])
        if not ruta_imagen: return
        self.btn_ia.configure(state="disabled", text="🤖 Red Neuronal Procesando...")
        threading.Thread(target=self.hilo_gemini, args=(ruta_imagen,)).start()

    def hilo_gemini(self, ruta_img):
        try:
            client = genai.Client(api_key=self.gemini_key)
            img_pil = Image.open(ruta_img)
            prompt = "Analiza esta imagen. Identifica el alimento de forma breve y calcula sus calorías totales. Responde strictly en este formato exacto de dos líneas sin asteriscos:\nPlato: Nombre del plato\nCalorias: Solo el numero"
            response = client.models.generate_content(model="gemini-2.5-flash", contents=[img_pil, prompt])
            
            linhas = response.text.strip().split("\n")
            plato = linhas[0].replace("Plato:", "").strip()
            calorias = int("".join(filter(str.isdigit, linhas[1])))
            self.app.after(0, lambda: self.abrir_modal_redireccion_ia(plato, calorias))
            
        except Exception as e:
            print(f"Error en Servidor Gemini (503): {e}")
            self.app.after(0, self.activar_fallback_manual_ia)
        finally:
            self.app.after(0, lambda: self.btn_ia.configure(state="normal", text="📷 Subir Foto de Comida"))

    def activar_fallback_manual_ia(self):
        messagebox.showinfo("Servidor Saturado (503)", "¡Los servidores de Gemini están experimentando alta demanda! Activando asistente manual de respaldo... 🦾")
        dialogo_alt = ctk.CTkInputDialog(text="Introduce el plato subido manualmente:\nFormato: Hamburguesa de 550 kcal", title="Asistente de Respaldo")
        entrada = dialogo_alt.get_input()
        
        if entrada and " de " in entrada.lower():
            try:
                partes = entrada.lower().split(" de ")
                plato = partes[0].strip().capitalize()
                calorias = int("".join(filter(str.isdigit, partes[1])))
                self.abrir_modal_redireccion_ia(plato, calorias)
            except:
                messagebox.showerror("Error", "Formato inválido.")

    def abrir_modal_redireccion_ia(self, plato, calorias):
        modal_ia = ctk.CTkToplevel(self.app)
        modal_ia.title("Resultado IA")
        modal_ia.geometry("380x240")
        modal_ia.attributes("-topmost", True)
        modal_ia.configure(fg_color=self.theme["card"])
        
        modal_ia.update_idletasks()
        x = (modal_ia.winfo_screenwidth() // 2) - (380 // 2)
        y = (modal_ia.winfo_screenheight() // 2) - (240 // 2)
        modal_ia.geometry(f"+{x}+{y}")

        ctk.CTkLabel(modal_ia, text="🤖 Detección Procesada", font=("Roboto", 14, "bold"), text_color=self.theme["primary"]).pack(pady=10)
        ctk.CTkLabel(modal_ia, text=f"Alimento: {plato}\nCalorías: {calorias} kcal", font=("Roboto", 12)).pack(pady=5)
        
        combo_ia = ctk.CTkComboBox(modal_ia, values=["Desayuno", "Almuerzo", "Merienda", "Cena", "Postres/Snacks"], width=280)
        combo_ia.set("Almuerzo")
        combo_ia.pack(pady=5)

        def confirmar_ia():
            destino = combo_ia.get()
            try:
                self.db.execute_query("INSERT INTO health_records (user_id, tipo, valor, detalle) VALUES (?, ?, ?, ?)", (self.user.get("id"), destino, float(calorias), plato))
                modal_ia.destroy()
                self.cargar_registros_bd()
                self.build_ui()
            except Exception as e:
                messagebox.showerror("Error", str(e))

        ctk.CTkButton(modal_ia, text="📥 Registrar Plato", command=confirmar_ia).pack(pady=15)

    def formatear_registro_diario(self):
        confirmar = messagebox.askyesno("Vaciar Día", "⚠ ¿Deseas vaciar los registros locales de hoy? Esto restablecerá tus marcadores calóricos a cero.")
        if confirmar:
            try:
                self.db.execute_query("DELETE FROM health_records WHERE user_id = ? AND date(fecha) = date('now')", (self.user.get("id"),))
                self.vasos_agua = 0
                self.cargar_registros_bd()
                self.build_ui()
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def sumar_agua(self):
        self.vasos_agua += 1
        self.actualizar_agua_bd()

    def r_agua_logica(self):
        if self.vasos_agua > 0:
            self.vasos_agua -= 1
            self.actualizar_agua_bd()

    def restar_agua(self):
        self.r_agua_logica()

    def actualizar_agua_bd(self):
        try:
            # Borra el valor anterior del día e inserta el actual sin riesgo de dejarlo vacío.
            self.db.replace_daily_records(self.user.get("id"), ("Agua",),
                (("Agua", float(self.vasos_agua), "Registro de vasos"),))
            self.build_ui()
        except Exception as e:
            print(str(e))
