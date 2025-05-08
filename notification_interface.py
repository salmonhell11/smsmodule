#Importerar nödvändiga bibliotek
# och moduler för att skapa ett gränssnitt för notifieringstjänster.
from abc import ABC, abstractmethod
# Används för att ange returtyper och argumenttyper i funktioner.
from typing import Dict, Any

# Denna klass definierar ett gränssnitt för notifieringstjänster.
# Den ärver från ABC (Abstract Base Class) för att möjliggöra skapandet av abstrakta metoder.
# Abstrakt metod som måste implementeras av alla underklasser.
class NotificationService(ABC):
    @abstractmethod
    def send_notification(self, recipient: str, message: str, subject: str = None, **kwargs) -> Dict[str, Any]:
        pass

    @abstractmethod
    def validate_request(self, recipient: str, message: str, subject: str = None, **kwargs) -> bool:
        pass
