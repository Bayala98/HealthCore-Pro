import customtkinter as ctk
from tkinter import messagebox, filedialog
from PIL import Image
import os

class ProfileView:
    def __init__(self, app):
        print("\n--- INICIANDO CARGA DE PERFIL ---")
        try:
            self.app = app
            self.user = self.app.current_user
            self.theme = self.app.current_theme
            
            # Persistencia de la foto de perfil en el estado local
            self.user_pfp_path = self.user.get("user_pfp_path", "")
            
            print("1. Cargando variables reactivas...")
            self.sv_nombre = ctk.StringVar(value=self.user.get("nombre", ""))
            self.sv_apellido = ctk.StringVar(value=self.user.get("apellido", ""))
            self.sv_edad = ctk.StringVar(value=str(self.user.get("edad", "")))
            self.sv_estatura = ctk.StringVar(value=str(self.user.get("estatura", "")))
            self.sv_peso = ctk.StringVar(value=str(self.user.get("peso", "")))
            self.sv_meta_kg = ctk.StringVar(value=str(self.user.get("meta_kg", "")))
            self.sv_meta_tipo = ctk.StringVar(value=self.user.get("meta_tipo", "Mantenerme"))
            
            # 🔥 SOLUCIÓN ARQUITECTURA: El contenedor principal se inicializa UNA sola vez aquí
            self.app.clear_screen()
            self.main_scroll = ctk.CTkScrollableFrame(
                self.app, fg_color="transparent",
                scrollbar_button_color=self.theme["primary"],
                scrollbar_button_hover_color=self.theme["btn_hover"]
            )
            self.main_scroll.pack(fill="both", expand=True, padx=20, pady=20)

            print("2. Construyendo interfaz gráfica...")
            self.build_ui()
            print("✅ PERFIL CARGADO EXITOSAMENTE")
            
        except Exception as e:
            print(f"❌ ERROR CRÍTICO AL CARGAR PERFIL: {e}")

    def build_ui(self):
        # 🔥 SOLUCIÓN AL DESPLAZAMIENTO: Limpiamos los hijos INTERNOS del scroll, no el scroll entero
        for widget in self.main_scroll.winfo_children():
            widget.destroy()

        self.app.configure(fg_color=self.theme["bg"])

        # BOTÓN REGRESAR AL DASHBOARD (Empaquetado dentro del scroll limpio)
        ctk.CTkButton(
            self.main_scroll, text="⬅ Volver al Menú", width=120, height=30,
            font=("Roboto", 12, "bold"), fg_color="transparent",
            text_color=self.theme["text_secondary"], hover_color=self.theme["card_hover"],
            command=self.app.show_dashboard
        ).pack(anchor="w", padx=10, pady=(0, 15))

        # CONTENEDOR SPLIT: IZQUIERDA (Mascota e IMC) | DERECHA (Campos editables)
        split_frame = ctk.CTkFrame(self.main_scroll, fg_color="transparent")
        split_frame.pack(fill="both", expand=True)
        split_frame.grid_columnconfigure(0, weight=4) 
        split_frame.grid_columnconfigure(1, weight=5) 

        # =========================================================
        # 👈 SECCIÓN IZQUIERDA: COMPAÑERO E IMC VISUAL
        # =========================================================
        left_card = ctk.CTkFrame(split_frame, fg_color=self.theme["card"], corner_radius=20, border_width=1, border_color=self.theme["border"])
        left_card.grid(row=0, column=0, padx=15, pady=15, sticky="nsew")

        avatar_path = self.user.get("avatar_path", "")
        nombre_mascota = self.user.get("avatar_name", "Tu compañero")
        
        img_size_avatar = 140
        img_frame = ctk.CTkFrame(left_card, width=img_size_avatar+15, height=img_size_avatar+15, corner_radius=20, fg_color=self.theme["input_bg"])
        img_frame.pack(pady=(25, 10))
        img_frame.pack_propagate(False)

        if avatar_path and os.path.exists(avatar_path):
            try:
                pil_img = Image.open(avatar_path)
                ctk_img = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(img_size_avatar, img_size_avatar))
                ctk.CTkLabel(img_frame, image=ctk_img, text="").place(relx=0.5, rely=0.5, anchor="center")
            except:
                ctk.CTkLabel(img_frame, text="✨", font=("Arial", 60)).place(relx=0.5, rely=0.5, anchor="center")
        else:
            ctk.CTkLabel(img_frame, text="👤", font=("Arial", 60)).place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(left_card, text=nombre_mascota, font=("Roboto", 18, "bold"), text_color=self.theme["primary"]).pack()

        # Cálculos de IMC
        try:
            peso = float(self.user.get("peso", 70.0))
            estatura = float(self.user.get("estatura", 1.70))
            meta_tipo = self.user.get("meta_tipo", "Mantenerme")
            meta_kg = float(self.user.get("meta_kg", 0.0))

            imc_actual = peso / (estatura ** 2)
            
            if meta_tipo == "Bajar de Peso": peso_proyectado = peso - meta_kg
            elif meta_tipo == "Aumentar peso": peso_proyectado = peso + meta_kg
            else: peso_proyectado = peso
            imc_proyectado = peso_proyectado / (estatura ** 2)
        except:
            imc_actual, imc_proyectado = 22.0, 22.0

        estado, color_barra = self.obtener_estado_imc(imc_actual)
        dialogo_mascota = self.obtener_dialogo_perfil(avatar_path, nombre_mascota, estado)

        bubble = ctk.CTkFrame(left_card, fg_color=self.theme["input_bg"], corner_radius=15)
        bubble.pack(pady=15, padx=20, fill="x")
        ctk.CTkLabel(bubble, text=f'"{dialogo_mascota}"', font=("Roboto", 12, "italic"), text_color=self.theme["text"], wraplength=280).pack(padx=15, pady=10)

        ctk.CTkLabel(left_card, text=f"Tu IMC Actual: {imc_actual:.1f} ({estado})", font=("Roboto", 14, "bold"), text_color=self.theme["text"]).pack(pady=(10, 2))
        
        progreso_porcentaje = max(0.0, min(1.0, (imc_actual - 15) / (40 - 15)))
        barra_imc = ctk.CTkProgressBar(left_card, width=280, height=15, corner_radius=10, progress_color=color_barra, fg_color="#333333")
        barra_imc.set(progreso_porcentaje)
        barra_imc.pack(pady=5)

        ctk.CTkLabel(left_card, text=f"🏁 Si cumples tu meta, tu IMC será: {imc_proyectado:.1f}", font=("Roboto", 12), text_color=self.theme["text_secondary"]).pack(pady=(5, 20))

        # =========================================================
        # 👉 SECCIÓN DERECHA: FORMULARIO + FOTO DE PERFIL PERSONAL
        # =========================================================
        right_card = ctk.CTkFrame(split_frame, fg_color=self.theme["card"], corner_radius=20, border_width=1, border_color=self.theme["border"])
        right_card.grid(row=0, column=1, padx=15, pady=15, sticky="nsew")

        # --- SUB-MÓDULO: SELECCIÓN DE FOTO DE PERFIL ---
        pfp_container = ctk.CTkFrame(right_card, fg_color="transparent")
        pfp_container.pack(pady=20, padx=30, fill="x")

        pfp_size = 90
        pfp_frame = ctk.CTkFrame(pfp_container, width=pfp_size, height=pfp_size, corner_radius=45, fg_color=self.theme["input_bg"])
        pfp_frame.pack(side="left")
        pfp_frame.pack_propagate(False)

        if self.user_pfp_path and os.path.exists(self.user_pfp_path):
            try:
                pil_pfp = Image.open(self.user_pfp_path)
                ctk_pfp = ctk.CTkImage(light_image=pil_pfp, dark_image=pil_pfp, size=(pfp_size, pfp_size))
                ctk.CTkLabel(pfp_frame, image=ctk_pfp, text="").place(relx=0.5, rely=0.5, anchor="center")
            except:
                ctk.CTkLabel(pfp_frame, text="📸", font=("Arial", 30)).place(relx=0.5, rely=0.5, anchor="center")
        else:
            ctk.CTkLabel(pfp_frame, text="📸", font=("Arial", 30)).place(relx=0.5, rely=0.5, anchor="center")

        pfp_text_frame = ctk.CTkFrame(pfp_container, fg_color="transparent")
        pfp_text_frame.pack(side="left", padx=20)
        ctk.CTkLabel(pfp_text_frame, text="Foto de Perfil Personal", font=("Roboto", 16, "bold"), text_color=self.theme["text"]).pack(anchor="w")
        
        ctk.CTkButton(
            pfp_text_frame, text="Subir Imagen", font=("Roboto", 12),
            height=28, fg_color=self.theme["input_bg"], border_width=1, border_color=self.theme["border"],
            text_color=self.theme["text"], hover_color=self.theme["card_hover"],
            command=self.seleccionar_foto_perfil
        ).pack(anchor="w", pady=(5, 0))

        # --- CAMPOS DEL FORMULARIO ---
        self.create_input_field(right_card, "Nombre:", self.sv_nombre)
        self.create_input_field(right_card, "Apellido:", self.sv_apellido)
        self.create_input_field(right_card, "Edad (Años):", self.sv_edad)
        self.create_input_field(right_card, "Estatura (Metros con punto):", self.sv_estatura)
        self.create_input_field(right_card, "Peso Actual (kg):", self.sv_peso)
        self.create_input_field(right_card, f"Kilos para {meta_tipo}:", self.sv_meta_kg)

        # BOTÓN GUARDAR CAMBIOS
        ctk.CTkButton(
            right_card, text="💾 Guardar Cambios", font=("Roboto", 14, "bold"),
            height=40, width=250, fg_color=self.theme["primary"], hover_color=self.theme["btn_hover"],
            command=self.guardar_cambios
        ).pack(pady=25)

    def create_input_field(self, parent, label_text, string_var):
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x", padx=30, pady=6)
        ctk.CTkLabel(frame, text=label_text, font=("Roboto", 13), text_color=self.theme["text_secondary"], width=180, anchor="w").pack(side="left")
        entry = ctk.CTkEntry(frame, textvariable=string_var, height=35, fg_color=self.theme["input_bg"], border_color=self.theme["border"], text_color=self.theme["text"])
        entry.pack(side="left", fill="x", expand=True)

    def obtener_estado_imc(self, imc):
        if imc < 18.5: return "Bajo Peso", "#3182CE" 
        elif imc < 25.0: return "Peso Normal", "#4CAF50" 
        elif imc < 30.0: return "Sobrepeso", "#FFA500" 
        else: return "Obesidad", "#FF4C4C" 

    def obtener_dialogo_perfil(self, path, nombre_mascota, estado):
        personaje = os.path.basename(path).split(".")[0].lower() if path else ""
        nombre_usuario = self.user.get("nombre", "Nakama").split()[0]
        
        if "luffy" in personaje:
            if estado == "Peso Normal": return f"¡Eso es Nakama {nombre_usuario}! Estás fuerte y listo para pelear. ¡A comer carne! 🍖"
            return f"¡Oye {nombre_usuario}! Tu salud es importante si quieres navegar conmigo. ¡Hay que ajustar esa comida! 🗺️"
        elif "zoro" in personaje:
            if estado == "Peso Normal": return f"Tu condición es óptima, {nombre_usuario}. Tu cuerpo resistirá las katanas hoy. ⚔️"
            return f"No descuides tu estado físico, {nombre_usuario}. ¡A entrenar más duro!"
        elif "gojo" in personaje:
            return f"Tranquilo {nombre_usuario}, conmigo estás a salvo, pero mantén tu balance biométrico. 😎"
        
        frases = {
            "Bajo Peso": "¡Oh! Noto que estás un poquito bajito de peso. Déjame acompañarte a planear comidas nutritivas. 🍎",
            "Peso Normal": "¡Guau! ¡Estás en tu punto perfecto! Tu IMC está genial. ¡Sigue así! 🌟",
            "Sobrepeso": "¡Vamos a movernos un poquito más! Juntos podemos equilibrar las caminatas. 🐾",
            "Obesidad": "Tu salud es lo que más me importa. Vamos paso a paso a cuidar tu corazoncito. ❤️"
        }
        return frases.get(estado, "¡Estoy muy orgulloso de estar aquí cuidando de ti!")

    def seleccionar_foto_perfil(self):
        ruta_archivo = filedialog.askopenfilename(
            title="Selecciona tu Foto de Perfil",
            filetypes=[("Archivos de Imagen", "*.png *.jpg *.jpeg *.bmp *.webp")]
        )
        if ruta_archivo:
            self.user_pfp_path = ruta_archivo
            self.user["user_pfp_path"] = ruta_archivo
            # Refresca la UI limpia sin alterar el scroll
            self.build_ui()

    def guardar_cambios(self):
        try:
            nuevo_peso = float(self.sv_peso.get().replace(",", "."))
            nueva_estatura = float(self.sv_estatura.get().replace(",", "."))
            nueva_edad = int(self.sv_edad.get())
            nueva_meta_kg = float(self.sv_meta_kg.get().replace(",", ".")) if self.sv_meta_kg.get() else 0.0
            
            updated_data = dict(self.user)
            updated_data["nombre"] = self.sv_nombre.get().strip()
            updated_data["apellido"] = self.sv_apellido.get().strip()
            updated_data["edad"] = nueva_edad
            updated_data["estatura"] = nueva_estatura
            updated_data["peso"] = nuevo_peso
            updated_data["meta_kg"] = nueva_meta_kg
            updated_data["user_pfp_path"] = self.user_pfp_path
            
            self.app.current_user = updated_data
            self.user = self.app.current_user
            
            messagebox.showinfo("Perfil Actualizado", "¡Los cambios se guardaron con éxito! 🚀")
            
            # Refresca los cálculos en la misma interfaz alineada
            self.build_ui()
            
        except ValueError:
            messagebox.showerror("Error de entrada", "Por favor introduce valores numéricos válidos en Edad, Estatura y Peso.")