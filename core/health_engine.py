# =====================================================
# HEALTH ENGINE - HEALTHCORE
# Módulo central de inteligencia del sistema
# =====================================================


class HealthEngine:

    def __init__(self, app):

        self.app = app
        self.user = app.current_user

        # almacén global de datos
        self.data = {
            "nutrition": [],
            "sports": [],
            "sleep": [],
            "mood": []
        }


    # =====================================================
    # REGISTRO DE DATOS (ENTRY POINTS)
    # =====================================================

    def log_nutrition(self, item):
        self.data["nutrition"].append(item)

    def log_sport(self, item):
        self.data["sports"].append(item)

    def log_sleep(self, item):
        self.data["sleep"].append(item)

    def log_mood(self, item):
        self.data["mood"].append(item)


    # =====================================================
    # CALCULAR IMC GLOBAL
    # =====================================================
    def get_imc(self):

        try:
            peso = float(self.user.get("peso", 0))
            estatura = float(self.user.get("estatura", 0))

            if peso <= 0 or estatura <= 0:
                return None

            return peso / (estatura ** 2)

        except:
            return None


    # =====================================================
    # CALORÍAS NETAS
    # =====================================================
    def get_calories_balance(self):

        intake = sum([i.get("calories", 0) for i in self.data["nutrition"]])
        burn = sum([i.get("calories", 0) for i in self.data["sports"]])

        return intake - burn


    # =====================================================
    # PROMEDIO DE SUEÑO
    # =====================================================
    def get_sleep_avg(self):

        if not self.data["sleep"]:
            return 0

        total = 0
        count = 0

        for s in self.data["sleep"]:
            try:
                total += float(s.get("hours", 0))
                count += 1
            except:
                pass

        return total / count if count > 0 else 0


    # =====================================================
    # ESTADO GENERAL DE SALUD (CORE INTELIGENTE)
    # =====================================================
    def get_global_status(self):

        imc = self.get_imc()
        calories = self.get_calories_balance()
        sleep = self.get_sleep_avg()

        status = {
            "risk": [],
            "score": 100
        }

        # =========================
        # IMC ANALYSIS
        # =========================
        if imc:

            if imc < 18.5:
                status["risk"].append("Bajo peso")
                status["score"] -= 10

            elif imc > 30:
                status["risk"].append("Obesidad")
                status["score"] -= 20


        # =========================
        # CALORÍAS
        # =========================
        if calories > 3000:
            status["risk"].append("Exceso calórico")
            status["score"] -= 15

        elif calories < 1200:
            status["risk"].append("Déficit energético")
            status["score"] -= 10


        # =========================
        # SUEÑO
        # =========================
        if sleep < 5:
            status["risk"].append("Falta de sueño")
            status["score"] -= 15

        elif sleep < 7:
            status["score"] -= 5


        # =========================
        # SCORE FINAL
        # =========================
        status["score"] = max(0, status["score"])

        return status


    # =====================================================
    # RECOMENDACIONES INTELIGENTES
    # =====================================================
    def get_recommendations(self):

        status = self.get_global_status()

        rec = []

        if "Falta de sueño" in status["risk"]:
            rec.append("😴 Intenta dormir entre 7-8 horas diarias")

        if "Exceso calórico" in status["risk"]:
            rec.append("🍎 Reduce bebidas azucaradas y ultraprocesados")

        if "Déficit energético" in status["risk"]:
            rec.append("🍗 Aumenta ingesta de proteínas y carbohidratos")

        if "Bajo peso" in status["risk"]:
            rec.append("🏋️ Considera entrenamiento de fuerza")

        if "Obesidad" in status["risk"]:
            rec.append("🏃 Incrementa actividad cardiovascular")

        if not rec:
            rec.append("✔️ Mantienes un buen equilibrio general de salud")

        return rec