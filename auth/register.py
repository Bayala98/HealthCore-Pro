import customtkinter as ctk
from tkinter import messagebox
from PIL import Image
import os
# IMPORTACIÓN CLAVE: Traemos el servicio de autenticación
from services.auth_service import AuthService

class RegisterView:
    def __init__(self, app):
        self.app = app
        self.theme = self.app.current_theme
        
        # =========================================================
        # 🔥 ARQUITECTURA: RESERVA DE ESTADO PERSISTENTE
        # =========================================================
        self.sv_usuario = ctk.StringVar()
        self.sv_correo = ctk.StringVar()
        self.sv_password = ctk.StringVar()
        self.sv_confirm_pass = ctk.StringVar()
        self.sv_nombre = ctk.StringVar()
        self.sv_apellido = ctk.StringVar()
        self.sv_edad = ctk.StringVar()
        self.sv_genero = ctk.StringVar(value="Seleccionar")
        self.sv_estatura = ctk.StringVar()
        self.sv_peso = ctk.StringVar()
        self.sv_meta_tipo = ctk.StringVar(value="Seleccionar")
        self.sv_meta_kg = ctk.StringVar()
        self.sv_theme = ctk.StringVar()
        self.sv_nombre_mascota = ctk.StringVar()

        self.selected_avatar_path = None
        self.avatar_category = None 
        self.images_refs = {}

        self.build_ui()

    def build_ui(self):
        self.app.clear_screen()
        self.app.configure(fg_color=self.theme["bg"])

        self.main_scroll = ctk.CTkScrollableFrame(
            self.app, 
            fg_color=self.theme["bg"],
            scrollbar_button_color=self.theme["primary"],
            scrollbar_button_hover_color=self.theme["btn_hover"]
        )
        self.main_scroll.pack(fill="both", expand=True)

        ctk.CTkButton(
            self.main_scroll, 
            text="⬅ Volver al Login", 
            width=120, height=30,
            font=("Roboto", 12, "bold"),
            fg_color="transparent",
            text_color=self.theme["text_secondary"],
            hover_color=self.theme["card_hover"],
            command=self.app.show_login
        ).pack(anchor="w", padx=20, pady=(15, 0))

        self.card = ctk.CTkFrame(
            self.main_scroll, 
            width=850, corner_radius=20,
            fg_color=self.theme["card"],
            border_width=1, border_color=self.theme["border"]
        )
        self.card.pack(pady=20, padx=20, expand=True)

        ctk.CTkLabel(
            self.card, text="Crea tu Cuenta HealthCore", 
            font=("Roboto", 32, "bold"), text_color=self.theme["text"]
        ).pack(pady=(30, 5))
        
        ctk.CTkLabel(
            self.card, text="Únete al ecosistema de salud más completo", 
            font=("Roboto", 14), text_color=self.theme["text_secondary"]
        ).pack(pady=(0, 30))

        # =========================================================
        # SECCIÓN 1: DATOS DE ACCESO
        # =========================================================
        self.create_section_title(self.card, "1. Datos de Acceso")
        
        acc_frame = ctk.CTkFrame(self.card, fg_color="transparent")
        acc_frame.pack(pady=10, padx=40, fill="x")
        acc_frame.grid_columnconfigure((0, 1), weight=1, pad=20)

        self.create_input(acc_frame, "Usuario*", self.sv_usuario, 0, 0)
        self.create_input(acc_frame, "Correo Electrónico*", self.sv_correo, 0, 1)
        self.create_input(acc_frame, "Contraseña*", self.sv_password, 1, 0, show="*")
        self.create_input(acc_frame, "Confirmar Contraseña*", self.sv_confirm_pass, 1, 1, show="*")

        # =========================================================
        # SECCIÓN 2: PERFIL BIOMÉTRICO
        # =========================================================
        self.create_section_title(self.card, "2. Perfil Biométrico y Meta")
        
        phys_frame = ctk.CTkFrame(self.card, fg_color="transparent")
        phys_frame.pack(pady=10, padx=40, fill="x")
        phys_frame.grid_columnconfigure((0, 1), weight=1, pad=20)

        self.create_input(phys_frame, "Nombre*", self.sv_nombre, 0, 0)
        self.create_input(phys_frame, "Apellido*", self.sv_apellido, 0, 1)
        self.create_input(phys_frame, "Edad*", self.sv_edad, 1, 0)

        gen_container = ctk.CTkFrame(phys_frame, fg_color="transparent")
        gen_container.grid(row=1, column=1, pady=(0, 15), sticky="ew")
        self.create_label_with_asterisk(gen_container, "Género*")
        
        self.genero_menu = ctk.CTkOptionMenu(
            gen_container,
            values=["Mujer", "Hombre", "No binario", "Disidencias", "Transgenero", "No define"],
            variable=self.sv_genero, height=40,
            fg_color=self.theme["input_bg"], button_color=self.theme["input_bg"],
            button_hover_color=self.theme["card_hover"], text_color=self.theme["text"],
            dropdown_fg_color=self.theme["card"], dropdown_text_color=self.theme["text"],
            command=self.on_gender_change 
        )
        self.genero_menu.pack(fill="x", pady=(2, 0))

        self.create_input(phys_frame, "Estatura (Metros)*", self.sv_estatura, 2, 0)
        self.create_input(phys_frame, "Peso Actual (kg)*", self.sv_peso, 2, 1)

        self.create_meta_section(phys_frame)

        # =========================================================
        # SECCIÓN 3: MASCOTA Y ESTILO
        # =========================================================
        self.create_section_title(self.card, "3. Tu Compañero y Estilo")
        
        self.mascota_container = ctk.CTkFrame(self.card, fg_color="transparent")
        self.mascota_container.pack(pady=10, padx=40, fill="x")

        color_frame = ctk.CTkFrame(self.card, fg_color="transparent")
        color_frame.pack(pady=20, padx=40, fill="x")
        
        ctk.CTkLabel(color_frame, text="Paleta de color de interfaz:", font=("Roboto", 14, "bold"), text_color=self.theme["text"]).pack(side="left", padx=10)
        
        current_theme_name = "Dark"
        for name, data in self.app.THEMES.items():
            if data == self.theme:
                current_theme_name = name
                break
        self.sv_theme.set(current_theme_name)

        self.theme_menu = ctk.CTkOptionMenu(
            color_frame, values=list(self.app.THEMES.keys()), variable=self.sv_theme,
            width=150, fg_color=self.theme["input_bg"], button_color=self.theme["primary"],
            command=self.on_theme_change 
        )
        self.theme_menu.pack(side="left", padx=10)

        self.restore_dynamic_sections()

        self.btn_register = ctk.CTkButton(
            self.card, text="Crear Mi Cuenta HealthCore 🚀",
            font=("Roboto", 16, "bold"), height=50, width=400, corner_radius=10,
            fg_color=self.theme["primary"], hover_color=self.theme["btn_hover"],
            command=self.register
        )
        self.btn_register.pack(pady=40)

    # =========================================================
    # HELPERS DE ELEMENTOS VISUALES
    # =========================================================
    def create_section_title(self, parent, text):
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x", padx=30, pady=(20, 10))
        ctk.CTkLabel(frame, text=text, font=("Roboto", 16, "bold"), text_color=self.theme["primary"]).pack(side="left")
        ctk.CTkFrame(frame, height=2, fg_color=self.theme["border"]).pack(side="left", fill="x", expand=True, padx=10)

    def create_label_with_asterisk(self, parent, text):
        lbl_frame = ctk.CTkFrame(parent, fg_color="transparent")
        lbl_frame.pack(anchor="w", padx=5)
        clean_text = text.replace("*", "")
        ctk.CTkLabel(lbl_frame, text=clean_text, font=("Roboto", 12), text_color=self.theme["text_secondary"]).pack(side="left")
        if "*" in text:
            ctk.CTkLabel(lbl_frame, text=" *", text_color="red", font=("Roboto", 12)).pack(side="left")

    def create_input(self, parent, placeholder, string_var, row, col, show=None):
        container = ctk.CTkFrame(parent, fg_color="transparent")
        container.grid(row=row, column=col, pady=(0, 15), sticky="ew")
        self.create_label_with_asterisk(container, placeholder)

        entry = ctk.CTkEntry(
            container, width=300, height=40, placeholder_text=placeholder,
            textvariable=string_var, show=show, corner_radius=8,
            fg_color=self.theme["input_bg"], border_color=self.theme["border"], text_color=self.theme["text"]
        )
        entry.pack(fill="x", pady=(2, 0))
        return entry

    # =========================================================
    # LÓGICA DE ACTUALIZACIÓN DEL ENTORNO
    # =========================================================
    def create_meta_section(self, parent):
        meta_container = ctk.CTkFrame(parent, fg_color="transparent")
        meta_container.grid(row=3, column=0, pady=(0, 15), sticky="ew")
        self.create_label_with_asterisk(meta_container, "Tu Meta Principal*")
        
        self.meta_menu = ctk.CTkOptionMenu(
            meta_container, values=["Bajar de Peso", "Mantenerme", "Aumentar peso"],
            variable=self.sv_meta_tipo, height=40,
            fg_color=self.theme["input_bg"], button_color=self.theme["input_bg"],
            text_color=self.theme["text"], command=self.on_meta_change 
        )
        self.meta_menu.pack(fill="x", pady=(2, 0))

        self.dyn_meta_frame = ctk.CTkFrame(parent, fg_color="transparent")
        self.entry_meta_kg = ctk.CTkEntry(
            self.dyn_meta_frame, width=300, height=40,
            placeholder_text="¿Cuántos kg? (ej. 5)", textvariable=self.sv_meta_kg,
            corner_radius=8, fg_color=self.theme["input_bg"], border_color=self.theme["border"], text_color=self.theme["text"]
        )
        self.entry_meta_kg.pack(fill="x", pady=(22, 0))

    def on_meta_change(self, choice):
        if choice in ["Bajar de Peso", "Aumentar peso"]:
            self.dyn_meta_frame.grid(row=3, column=1, pady=(0, 15), sticky="ew")
        else:
            self.dyn_meta_frame.grid_forget()
            self.sv_meta_kg.set("")

    def on_theme_change(self, choice):
        self.app.set_theme(choice)
        self.theme = self.app.current_theme
        self.build_ui()

    def restore_dynamic_sections(self):
        self.on_meta_change(self.sv_meta_tipo.get())
        self.render_avatar_selection(self.sv_genero.get())

    # =========================================================
    # PROCESAMIENTO DINÁMICO DE AVATARES Y MASCOTAS
    # =========================================================
    def on_gender_change(self, genero):
        self.selected_avatar_path = None 
        self.render_avatar_selection(genero)

    def render_avatar_selection(self, genero):
        for w in self.mascota_container.winfo_children(): w.destroy()
        self.images_refs = {} 

        if genero == "Seleccionar" or not genero:
            ctk.CTkLabel(self.mascota_container, text="Primero selecciona tu género en la sección de arriba...", font=("Roboto", 14, "italic"), text_color="gray").pack(pady=20)
            return

        pets_list = ["caballito", "perro", "gato", "panda", "mapache", "conejo"]
        anime_list = ["luffy", "zoro", "tanjiro", "goku", "gojo"]

        show_pets = genero in ["Mujer", "Disidencias", "No binario", "Transgenero", "No define"]
        show_anime = genero in ["Hombre", "No binario", "Transgenero", "No define"]

        grid_frame = ctk.CTkFrame(self.mascota_container, fg_color="transparent")
        grid_frame.pack(pady=10, fill="x")
        
        current_col = 0
        current_row = 0
        max_cols = 5 

        def add_avatar_buttons(name_list, category):
            nonlocal current_col, current_row
            for name in name_list:
                self.create_avatar_button(grid_frame, name, category, current_row, current_col)
                current_col += 1
                if current_col >= max_cols:
                    current_col = 0
                    current_row += 1
            if current_col != 0: 
                current_row += 1
                current_col = 0

        if show_pets:
            ctk.CTkLabel(grid_frame, text="Elige tu Mascota (Animalito):", font=("Roboto", 13, "bold"), text_color=self.theme["text"]).grid(row=current_row, column=0, columnspan=max_cols, sticky="w", pady=(10,5))
            current_row += 1
            add_avatar_buttons(pets_list, "pets")

        if show_anime:
            pady_val = (20, 5) if show_pets else (10, 5)
            ctk.CTkLabel(grid_frame, text="Elige tu Personaje (Anime):", font=("Roboto", 13, "bold"), text_color=self.theme["text"]).grid(row=current_row, column=0, columnspan=max_cols, sticky="w", pady=pady_val)
            current_row += 1
            add_avatar_buttons(anime_list, "anime")

        self.preview_info_frame = ctk.CTkFrame(self.mascota_container, fg_color="transparent")
        self.preview_info_frame.pack(pady=15, fill="x")

        if self.selected_avatar_path:
            self.update_avatar_preview(self.selected_avatar_path, self.avatar_category)

    def create_avatar_button(self, parent, name, category, row, col):
        img_size = 70
        img_path = os.path.join("assets", "avatars", category, f"{name}.png")
        
        is_selected = (self.selected_avatar_path == img_path)
        border_w = 3 if is_selected else 0
        border_c = self.theme["primary"] if is_selected else ""

        btn_frame = ctk.CTkFrame(
            parent, width=img_size+10, height=img_size+10, corner_radius=10, 
            fg_color=self.theme["input_bg"], border_width=border_w, border_color=border_c
        )
        btn_frame.grid(row=row, column=col, padx=10, pady=10)
        btn_frame.pack_propagate(False)

        try:
            pil_img = Image.open(img_path)
            ctk_img = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(img_size, img_size))
            img_btn = ctk.CTkButton(
                btn_frame, image=ctk_img, text="", width=img_size, height=img_size,
                fg_color="transparent", hover_color=self.theme["card_hover"],
                command=lambda p=img_path, c=category, f=btn_frame: self.on_avatar_selected(p, c, f)
            )
            img_btn.place(relx=0.5, rely=0.5, anchor="center")
            self.images_refs[f"{category}_{name}_thumb"] = ctk_img
        except Exception:
            ctk.CTkButton(
                btn_frame, text=name.capitalize(), width=img_size, height=img_size,
                fg_color=self.theme["border"], text_color=self.theme["text"],
                command=lambda p=img_path, c=category, f=btn_frame: self.on_avatar_selected(p, c, f)
            ).place(relx=0.5, rely=0.5, anchor="center")

        self.images_refs[f"frame_{img_path}"] = btn_frame

    def on_avatar_selected(self, path, category, frame_widget):
        self.selected_avatar_path = path
        self.avatar_category = category

        for key, widget in self.images_refs.items():
            if key.startswith("frame_"):
                widget.configure(border_width=0, border_color="")
                
        frame_widget.configure(border_width=3, border_color=self.theme["primary"])
        self.update_avatar_preview(path, category)

    def update_avatar_preview(self, path, category):
        for w in self.preview_info_frame.winfo_children(): w.destroy()
        
        raw_name = os.path.splitext(os.path.basename(path))[0]
        display_name = raw_name.capitalize()

        preview_card = ctk.CTkFrame(self.preview_info_frame, fg_color=self.theme["input_bg"], corner_radius=15)
        preview_card.pack(pady=10, padx=20, fill="x")

        img_size_big = 120
        img_frame_big = ctk.CTkFrame(preview_card, width=img_size_big+20, height=img_size_big+20, fg_color="transparent")
        img_frame_big.pack(side="left", padx=20, pady=20)
        img_frame_big.pack_propagate(False)

        try:
            pil_img_big = Image.open(path)
            ctk_img_big = ctk.CTkImage(light_image=pil_img_big, dark_image=pil_img_big, size=(img_size_big, img_size_big))
            ctk.CTkLabel(img_frame_big, image=ctk_img_big, text="").place(relx=0.5, rely=0.5, anchor="center")
            self.images_refs["big_preview"] = ctk_img_big 
        except Exception:
            ctk.CTkLabel(img_frame_big, text="[Foto]", font=("Arial", 20), text_color="gray").place(relx=0.5, rely=0.5, anchor="center")

        info_frame = ctk.CTkFrame(preview_card, fg_color="transparent")
        info_frame.pack(side="left", fill="both", expand=True, padx=(0, 20), pady=20)

        tipo_texto = "Mascota Interactiva" if category == "pets" else "Personaje Acompañante"
        ctk.CTkLabel(info_frame, text=tipo_texto, font=("Roboto", 12), text_color="gray").pack(anchor="w")
        ctk.CTkLabel(info_frame, text=display_name, font=("Roboto", 24, "bold"), text_color=self.theme["text"]).pack(anchor="w", pady=(0, 15))
        
        if category == "pets":
            ctk.CTkLabel(info_frame, text=f"Ponle un nombre a tu {display_name}:*", font=("Roboto", 13, "bold"), text_color=self.theme["text_secondary"]).pack(anchor="w")
            self.entry_nombre_mascota = ctk.CTkEntry(
                info_frame, placeholder_text=f"Ej. Firulais", 
                textvariable=self.sv_nombre_mascota, width=250, height=35,
                fg_color=self.theme["bg"], border_color=self.theme["border"], text_color=self.theme["text"]
            )
            self.entry_nombre_mascota.pack(anchor="w", pady=(5, 0))
        else:
            ctk.CTkLabel(info_frame, text=f"{display_name} te acompañará en tu proceso.", font=("Roboto", 13, "italic"), text_color="gray").pack(anchor="w")
            self.sv_nombre_mascota.set(display_name) 

    # =========================================================
    # ACCIÓN: SUBMIT DE REGISTRO (CONECTADO A LA BD)
    # =========================================================
    # =========================================================
    # ACCIÓN: SUBMIT DE REGISTRO (MODO DEBUG ACTIVADO)
    # =========================================================
    def register(self):
        print("\n--- INICIANDO PROCESO DE REGISTRO ---")
        
        p_original = self.sv_password.get().strip()
        p_confirm = self.sv_confirm_pass.get().strip()
        
        campos_obligatorios = {
            "Usuario": self.sv_usuario.get(), "Correo": self.sv_correo.get(),
            "Contraseña": p_original, "Nombre": self.sv_nombre.get(),
            "Apellido": self.sv_apellido.get(), "Edad": self.sv_edad.get(),
            "Estatura": self.sv_estatura.get(), "Peso": self.sv_peso.get()
        }

        print("1. Verificando campos obligatorios...")
        for nombre, valor in campos_obligatorios.items():
            if not valor.strip():
                print(f"❌ DETENIDO: Falta el campo '{nombre}'")
                messagebox.showwarning("Faltan datos", f"El campo '{nombre}' es obligatorio.")
                return

        print("2. Verificando Género y Meta...")
        if self.sv_genero.get() == "Seleccionar":
            print("❌ DETENIDO: Falta seleccionar género")
            messagebox.showwarning("Género", "Por favor selecciona tu género.")
            return
            
        if self.sv_meta_tipo.get() == "Seleccionar":
            print("❌ DETENIDO: Falta seleccionar meta")
            messagebox.showwarning("Meta", "Selecciona tu meta principal de salud.")
            return

        print("3. Verificando Contraseñas...")
        if p_original != p_confirm:
            print("❌ DETENIDO: Las contraseñas no coinciden")
            messagebox.showerror("Error", "Las contraseñas no coinciden.")
            return

        print("4. Verificando Mascota/Avatar...")
        if not self.selected_avatar_path:
            print("❌ DETENIDO: No se seleccionó avatar")
            messagebox.showwarning("Compañero", "¡Debes elegir a tu compañero interactivo!")
            return
        
        final_pet_name = self.sv_nombre_mascota.get().strip()
        if self.avatar_category == "pets" and not final_pet_name:
            print("❌ DETENIDO: Falta nombre de la mascota")
            self.entry_nombre_mascota.focus()
            messagebox.showwarning("Nombre Mascota", "Por favor ponle un nombre a tu mascota.")
            return

        print("5. Convirtiendo números...")
        try:
            edad_int = int(self.sv_edad.get())
            peso_float = float(self.sv_peso.get().replace(",", "."))
            estatura_float = float(self.sv_estatura.get().replace(",", "."))
            kg_meta = float(self.sv_meta_kg.get().replace(",", ".")) if self.sv_meta_kg.get() else 0.0
        except ValueError as e:
            print(f"❌ DETENIDO: Error en números -> {e}")
            messagebox.showerror("Error de formato", "Edad, Peso y Estatura deben ser números.")
            return

        print("6. Construyendo paquete de datos...")
        user_data = {
            "usuario": self.sv_usuario.get().strip(), "correo": self.sv_correo.get().strip(),
            "password": p_original, 
            "nombre": self.sv_nombre.get().strip(), "apellido": self.sv_apellido.get().strip(),
            "edad": edad_int, "genero": self.sv_genero.get(), "peso": peso_float,
            "estatura": estatura_float, "meta_tipo": self.sv_meta_tipo.get(),
            "meta_kg": kg_meta, "avatar_path": self.selected_avatar_path,
            "avatar_category": self.avatar_category, "avatar_name": final_pet_name,
            "theme": self.sv_theme.get(),       # <-- ¡AQUÍ ESTÁ LA MAGIA!
            "theme_name": self.sv_theme.get()   # <-- Lo dejamos también por si acaso
        }

        print("7. Enviando datos a AuthService...")
        try:
            success, msg = AuthService.register_user(user_data)
            
            if success:
                print("✅ REGISTRO EXITOSO EN BASE DE DATOS")
                messagebox.showinfo("¡Bienvenido!", f"¡Registro exitoso, {user_data['nombre']}!")
                self.app.show_login()
            else:
                print(f"❌ ERROR EN BASE DE DATOS: {msg}")
                messagebox.showerror("Error de Base de Datos", f"Hubo un problema al guardar:\n{msg}")
        except Exception as e:
            print(f"❌ ERROR CRÍTICO AL LLAMAR A AUTHSESSION: {e}")