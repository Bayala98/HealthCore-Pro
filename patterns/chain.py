# =====================================================
# CHAIN OF RESPONSIBILITY
# CHAT EMOCIONAL
# =====================================================

class ChatHandler:

    def __init__(self, next_handler=None):

        self.next_handler = next_handler

    def handle(self, message):

        if self.next_handler:

            return self.next_handler.handle(message)

        return "Estoy aquí contigo 💖"

# =====================================================
# SALUDOS
# =====================================================

class GreetingHandler(ChatHandler):

    def handle(self, message):

        if "hola" in message.lower():

            return "¡Hola! Me alegra verte 💖"

        return super().handle(message)

# =====================================================
# TRISTEZA
# =====================================================

class SadHandler(ChatHandler):

    def handle(self, message):

        if "triste" in message.lower():

            return "Respira profundo. Estoy contigo 🫂"

        return super().handle(message)

# =====================================================
# CADENA
# =====================================================

chat_chain = GreetingHandler(
    SadHandler()
)