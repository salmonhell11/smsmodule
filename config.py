import os # Pythons bibliotek möjjliggörs i koden och dess funktioner går att använda 

HELLOSMS_CONFIG = {
    # Användarnamn för HelloSMS.
    # Varje kund måste ange sitt eget användarnamn som de fått från HelloSMS.
    "username": os.getenv("HELLOSMS_USERNAME", "n6560t812a89486qq3ynzjr0"),
    #Varje kund byter sitt lösenord till dett som tilldelats av HelloSMS
    "password": os.getenv("HELLOSMS_PASSWORD", "agYPySU5ynEQYty6YJy6"),
    #Varje kund byter sitt  avsändarnamn till det som passar för dem.
    # Om inget anges används "TrafikInfo" som standard.
    "sender": os.getenv("HELLOSMS_SENDER", "TrafikInfo"),
    # Timeout för API-anrop i sekunder.
    # Om inget anges används 10 sekunder som standard.
    "default_timeout": int(os.getenv("HELLOSMS_TIMEOUT", "10")),
    # Max antal försök för att skicka ett meddelande.
    # Om inget anges används 3 försök som standard.
    "max_retries": int(os.getenv("HELLOSMS_MAX_RETRIES", "3")),
    # URL för HelloSMS API.
    # Om inget anges används standard-URL:en som HelloSMS tillhandahållit.
    "api_url": os.getenv("HELLOSMS_API_URL", "https://api.hellosms.se/api/v1/sms/send"),
    # Max längd på meddelandet i tecken.
    # Om inget anges används 160 tecken som standard.
    "max_message_length": int(os.getenv("HELLOSMS_MAX_LENGTH", "160")),
    # Max antal meddelanden som kan skickas per minut.
    # Om inget anges används 100 meddelanden som standard.
    "rate_limit": int(os.getenv("HELLOSMS_RATE_LIMIT", "100")),
    # Retry-koder för att hantera fel.
    # Om inget anges används 408, 500, 502, 503 och 504 som standard.
    "retry_codes": [408, 500, 502, 503, 504]
}