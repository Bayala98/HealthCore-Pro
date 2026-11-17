import customtkinter as ctk
from tkinter import messagebox
from services.auth_service import AuthService

class LoginView:
    def __init__(self, app):
        """
        Constructor de la vista de Login.
        Recibe la instancia principal de la app para poder navegar entre pantallas.
        """
        self.app = app
        # Forzamos el tema oscuro para darle un toque premium y tecnológico
        ctk.set_appearance_mode("dark")
        
        # Paleta de colores local para el login (Azul médico moderno)
        self.color_primary = "#1f6aa5"
        self.color_secondary = "#2a2d2e"
        self.color_text = "#ffffff"
        
        self.build_ui()

    def build_ui(self):
        """
        Construye y renderiza toda la interfaz de usuario del Login.
        """
        # Limpiamos cualquier widget anterior en la pantalla principal
        self.app.clear_screen()

        # 🔥 CONTENEDOR PRINCIPAL (Root)
        self.root = ctk.CTkFrame(self.app, fg_color="#1a1a1a")
        self.root.pack(fill="both", expand=True)

        # =========================================================
        # TARJETA CENTRAL (LOGIN CARD)
        # =========================================================
        self.card = ctk.CTkFrame(
            self.root,
            width=420,
            height=520,
            corner_radius=20,
            fg_color="#242424",
            border_width=1,
            border_color="#333333" 
        )
        self.card.place(relx=0.5, rely=0.5, anchor="center")
        self.card.pack_propagate(False) 

        # =========================================================
        # ELEMENTOS DE LA UI (WIDGETS)
        # =========================================================
        
        ctk.CTkLabel(self.card, text="🏥", font=("Arial", 55)).pack(pady=(30, 10))
        ctk.CTkLabel(self.card, text="Health Core", font=("Roboto", 28, "bold"), text_color=self.color_text).pack()
        ctk.CTkLabel(self.card, text="Tu ecosistema de salud inteligente", font=("Roboto", 12), text_color="gray").pack(pady=(0, 30))

        self.user_entry = ctk.CTkEntry(
            self.card, 
            width=300, 
            height=40,
            placeholder_text="Usuario o Correo Electrónico",
            corner_radius=8
        )
        self.user_entry.pack(pady=(0, 15))

        self.pass_entry = ctk.CTkEntry(
            self.card, 
            width=300, 
            height=40,
            placeholder_text="Contraseña", 
            show="*", 
            corner_radius=8
        )
        self.pass_entry.pack(pady=(0, 25))

        # Botón Primario: Iniciar Sesión
        ctk.CTkButton(
            self.card, 
            text="Iniciar Sesión", 
            width=300, 
            height=40,
            font=("Roboto", 14, "bold"),
            fg_color=self.color_primary,
            hover_color="#144870",
            corner_radius=8,
            command=self.login
        ).pack(pady=(0, 15))

        # Botón Secundario: Crear Cuenta
        ctk.CTkButton(
            self.card, 
            text="Crear Cuenta Nueva", 
            width=300, 
            height=40,
            font=("Roboto", 14),
            fg_color="transparent",
            border_width=2,
            text_color=self.color_text,
            hover_color="#333333",
            corner_radius=8,
            command=self.app.show_register 
        ).pack(pady=(0, 20))

        # Enlaces de Recuperación
        links_frame = ctk.CTkFrame(self.card, fg_color="transparent")
        links_frame.pack()

        ctk.CTkButton(
            links_frame, 
            text="¿Olvidaste tu usuario?", 
            font=("Roboto", 12, "underline"), 
            text_color="#a3a3a3",
            fg_color="transparent",
            hover_color="#242424",
            width=140,
            command=self.forgot_user
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            links_frame, 
            text="¿Olvidaste tu contraseña?", 
            font=("Roboto", 12, "underline"), 
            text_color="#a3a3a3",
            fg_color="transparent",
            hover_color="#242424",
            width=140,
            command=self.forgot_password
        ).pack(side="left", padx=5)

    # =========================================================
    # FUNCIONES LÓGICAS (MODO DEBUG ACTIVADO)
    # =========================================================
    def login(self):
        try:
            u = self.user_entry.get().strip()
            p = self.pass_entry.get().strip()

            if not u or not p:
                messagebox.showwarning("Campos vacíos", "Por favor ingresa usuario y contraseña.")
                return

            ok, user = AuthService.login_user(u, p)

            if not ok:
                messagebox.showerror("Error de autenticación", "Credenciales incorrectas. Inténtalo de nuevo.")
                return

            self.app.current_user = user
            self.app.show_dashboard()
        except Exception:
            messagebox.showerror("Error de conexión", "No fue posible iniciar sesión. Verifica la conexión con la base de datos.")

    def forgot_user(self):
        """Muestra un diálogo moderno para recuperar el usuario."""
        dialog = ctk.CTkInputDialog(text="Ingresa el correo registrado:", title="Recuperar Usuario")
        correo = dialog.get_input()

        if not correo:
            return 
            
        try:
            user = AuthService.get_user_by_email(correo)
            if not user:
                messagebox.showerror("Error", "El correo ingresado no pertenece a ninguna cuenta.")
                return
            messagebox.showinfo("Recuperación exitosa", f"Tu usuario es: {user['usuario']}")
        except Exception:
            messagebox.showwarning("Aviso", "Función en desarrollo.")

    def forgot_password(self):
        """Muestra un diálogo moderno para recuperar la contraseña."""
        dialog = ctk.CTkInputDialog(text="Ingresa tu correo para enviarte el enlace:", title="Recuperar Contraseña")
        correo = dialog.get_input()

        if not correo:
            return

        try:
            user = AuthService.get_user_by_email(correo)
            if not user:
                messagebox.showerror("Error", "El correo ingresado no pertenece a ninguna cuenta.")
                return
            messagebox.showinfo("Correo Enviado", "Te hemos enviado un correo con las instrucciones para restablecer tu contraseña.\n\nPor favor, revisa tu bandeja de entrada.")
        except Exception:
            messagebox.showwarning("Aviso", "Función en desarrollo.")
