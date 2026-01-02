import requests
import os
from datetime import datetime

class TelegramNotifier:
    def __init__(self, token, chat_id):
        self.token = token
        self.chat_id = chat_id
        
    def send_alert(self, message, image_path=None):
        """
        Envía una alerta a Telegram con texto y opcionalmente una imagen.
        """
        if not self.token or not self.chat_id:
            print("[Notifications] Telegram credentials missing. Skipping alert.")
            return

        # Enviar Mensaje
        url_msg = f"https://api.telegram.org/bot{self.token}/sendMessage"
        try:
            payload = {'chat_id': self.chat_id, 'text': message}
            requests.post(url_msg, data=payload)
            
            # Enviar Imagen (opcional)
            if image_path and os.path.exists(image_path):
                url_img = f"https://api.telegram.org/bot{self.token}/sendPhoto"
                with open(image_path, 'rb') as photo:
                    requests.post(url_img, data={'chat_id': self.chat_id}, files={'photo': photo})
            
            print("      [Telegram] Alert sent successfully.")
            
        except Exception as e:
            print(f"      [!] Telegram Error: {e}")
