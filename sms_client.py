#Importerar gränssnittet för notifieringstjänster
# och konfigurationsinställningar för HelloSMS API.

from notification_interface import NotificationService
# Används för att skicka HTTP-anrop till HelloSMS API.
import requests
from requests.adapters import HTTPAdapter
# Används för att skapa autentisering med HelloSMS i Base64-format
import base64
# Används för att specificera typer på argument och returvärden
from typing import Dict, Any, Optional
# Importerar konfigurationsdata för HelloSMS
from config import HELLOSMS_CONFIG

# Klass som ansvarar för att skicka SMS via HelloSMS API
# Den ärver från NotificationService och implementerar de abstrakta metoderna
class SMSClient(NotificationService):
    def __init__(self, config=None):
          # Hämtar inställningar från HELLOSMS_CONFIG eller ett externt konfigobjekt
        self.config = config or HELLOSMS_CONFIG
        self.username = self.config["username"]
        self.password = self.config["password"]
        self.sender = self.config["sender"]
        self.base_url = self.config["api_url"]
        self.timeout = self.config["default_timeout"]
      # Skapar autentiseringsträng i Base64-format för HelloSMS API
        self.auth = base64.b64encode(f"{self.username}:{self.password}".encode()).decode()
     # Skapar en HTTP-session med återförsök (t.ex. vid timeout eller 500-fel)
        self.session = requests.Session()
        adapter = HTTPAdapter(max_retries=self.config["max_retries"])
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)

    def validate_request(self, recipient: str, message: str, subject: Optional[str] = None, **kwargs) -> bool:
        # Kontrollerar att mottagare och meddelande finns
        if not recipient or not message:
            return False
                # Kontrollerar att meddelandet inte är längre än tillåtet
        if len(message) > self.config["max_message_length"]:
            return False
               # Kontrollerar att telefonnumret börjar med + och bara innehåller siffror efteråt
        return bool(recipient.startswith('+') and recipient[1:].isdigit())

    def send_notification(self, recipient: str, message: str, subject: Optional[str] = None, **kwargs) -> Dict[str, Any]:
               # Validerar först förfrågan innan SMS skickas.
        if not self.validate_request(recipient, message, subject):
            return {"status": "error", "error": "Invalid phone number format"}
                # Om allt är giltigt, så skickas SMS.
        return self.send_sms(recipient, message, subject)

    def send_sms(self, phone, message, subject="Meddelande"):
             # Skapar HTTP-header och data enligt HelloSMS krav
        headers = {
            "Authorization": f"Basic {self.auth}",
            "Content-Type": "application/json"
        }
        data = {
            "to": [phone], # Mottagarens telefonnummer
            "from": self.sender, # Avsändarnamnet för SMS
            "subject": subject, # Ämnet för SMS
            "message": message, # Meddelandetexten
            "priority": "high" # Markerar meddelandet som viktigt
        }

        try:
                   # Försöker skicka POST-anrop till HelloSMS API
            response = self.session.post(self.base_url, json=data, headers=headers, timeout=self.timeout)
            response.raise_for_status() # Kontrollerar om svaret är framgångsrikt (statuskod 200-299)
            return {
                "status": "success",
                "response": response.json() # Omvandlar svaret till JSON-format
            }
        except requests.RequestException as e:
                  # Hanterar eventuella fel vid HTTP-anropet
            # Loggar felmeddelandet och returnerar en felstatus
            return {
                "status": "error",
                "error": str(e),
                "response": getattr(e.response, "json", lambda: {})() # Försöker hämta JSON-svaret från felmeddelandet
            }