# sms_server.py
# Denna fil innehåller en webbtjänst (Flask) som tar emot förfrågningar för att skicka SMS.
# Den ansvarar för validering, loggning, hastighetsbegränsning och vidarebefordran till sms_client.
#
# Exempel på hur man testar tjänsten via webbläsare eller curl:
# http://localhost:5000/send?telnr=46XXXXXXXXX&subject=Test&message=Hej&action=sms&id=tester

# Hur andra system kopplar till denna tjänst:
# 1. När ett meddelande ska skickas (t.ex. en trafikincident), gör systemet ett HTTP-anrop till denna endpoint.
# 2. Exempel i Python:
#
# import requests
# def skicka_sms():
#     response = requests.get("http://localhost:5000/send", params={
#         "telnr": "46XXXXXXXXX",
#         "subject": "Trafikhändelse",
#         "message": "Olycka på E4 i Uppsala",
#         "action": "sms",
#         "id": "trafik_api"
#     })
#     print(response.json())
#
# 3. Det andra systemet (t.ex. API/databas) behöver bara anropa denna tjänst med rätt parametrar – din tjänst sköter resten.

# Parametrar:
# - telnr: Telefonnummer i internationellt format (t.ex. 46XXXXXXXXX)
# - subject: Ämnesrad (valfri)
# - message: Själva SMS-innehållet
# - action: Måste vara "sms"
# - id: Identifierare för kunden (valfri)

# Importerar moduler för filhantering, tid, loggning och webbtjänst
import os
import time
import logging
from datetime import datetime
from typing import Dict, Any, List, Union
from flask import Flask, request, jsonify # Flask-biblioteket för att skapa en webbtjänst
from sms_client import SMSClient # Importerar SMSClient för att skicka SMS

app = Flask(__name__)  # Skapar en instans av webbapplikationen
sms = SMSClient()  # Initierar SMS-klienten

# Ser till att loggar sparas i en undermapp "logs" nära filens plats
log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
os.makedirs(log_dir, exist_ok=True)
# Konfigurerar loggfil som uppdateras med dagens datum
logging.basicConfig(
    filename=os.path.join(log_dir, f'sms_log_{datetime.now().strftime("%Y%m%d")}.txt'),
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s'
)

# Listan håller reda på tidpunkter för förfrågningar (för rate limiting)
request_times: List[float] = []
RATE_WINDOW = 60   # Fönster på 60 sekunder för att mäta max antal SMS
# RATE_LIMIT = sms.config["rate_limit"]  # Max antal SMS som kan skickas under fönstret
def check_rate_limit() -> bool:
    """
    Check if the current request exceeds the rate limit.

    Returns:
        bool: True if request is within rate limit, False otherwise
    """
    current_time = time.time()
    request_times[:] = [t for t in request_times if current_time - t < RATE_WINDOW]
    if len(request_times) >= sms.config["rate_limit"]:
        return False
    request_times.append(current_time)
    return True
# Kontrollerar om ett telefonnummer är giltigt (börjar med + och är numeriskt)
def validate_phone(phone: str) -> bool:
    """
    Validate phone number format and add + prefix if missing.

    Args:
        phone (str): Phone number to validate

    Returns:
        bool: True if phone number is valid, False otherwise
    """
    if not phone:
        return False
    if not phone.startswith('+'):
        phone = '+' + phone
    return phone[1:].isdigit()
# HTTP-endpoint som hanterar SMS-utskick
@app.route('/send', methods=['GET'])
def send_sms() -> Union[tuple[Dict[str, Any], int], Dict[str, Any]]:
    """
    Handle SMS send requests via GET endpoint.
    
    Query Parameters:
        telnr (str): Recipient phone number
        subject (str, optional): SMS subject. Defaults to 'Meddelande'
        message (str): SMS content
        action (str): Must be 'sms'
        id (str, optional): Sender identifier. Defaults to 'unknown'
    
    Returns:
        JSON response with status and request_id
        HTTP 400 for invalid requests
        HTTP 429 for rate limit exceeded
    """    # Om maxgränsen för SMS är nådd returneras ett felmeddelande
    if not check_rate_limit():
        return jsonify({"status": "error", "error": "Rate limit exceeded"}), 429
   # Hämtar parametrar från URL:en
    phone = request.args.get('telnr', '').strip()
    if not phone.startswith('+'):
        phone = '+' + phone
    subject = request.args.get('subject', 'Meddelande')
    message = request.args.get('message')
    action = request.args.get('action')
    sender_id = request.args.get('id', 'unknown')
    # Kontrollerar att alla nödvändiga parametrar finns
    if not sms.validate_request(phone, message) or action != 'sms':
        logging.warning("Invalid request | Sender: %s | Phone: %s | Message: %s | Action: %s", sender_id, phone, message, action)
        return jsonify({
            "status": "error",
            "error": "Ogiltiga eller saknade parametrar",
            "request_id": datetime.now().strftime("%Y%m%d%H%M%S")
        }), 400

    # Kontrollerar att telefonnumret är giltigt
    
    logging.info("Sending SMS | Sender: %s | Phone: %s | Subject: %s | Message: %s", sender_id, phone, subject, message)
    # Skickar SMS via SMS-klienten
    result = sms.send_notification(phone, message, subject)
    # Loggar resultatet av SMS-utskicket
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "sender_id": sender_id,
        "recipient": phone,
        "subject": subject,
        "status": result["status"],
        "request_id": datetime.now().strftime("%Y%m%d%H%M%S")
    }
    #Loggar hela meddelandet till en fil
    logging.info("NOTIFICATION | %s", log_entry)
     # Returnerar svaret som JSON inklusive request_id
    return jsonify({**result, "request_id": log_entry["request_id"]})
# Startar Flask-servern
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)