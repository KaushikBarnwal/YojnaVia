from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class BaseNotificationProvider(ABC):
    """Abstract interface for all notification channel delivery providers."""

    @abstractmethod
    def send(
        self,
        recipient: str,
        title: str,
        body: str,
        template_name: str,
        context: Dict[str, Any],
        language: str = 'en'
    ) -> Dict[str, Any]:
        """
        Transmits the notification.
        Returns a dict containing:
        - success: bool
        - provider_message_id: str
        - status: str ('SENT', 'DELIVERED', 'FAILED', 'SIMULATED')
        - raw_response: dict
        - error_message: str (if failed)
        - is_simulated: bool
        """
        pass
