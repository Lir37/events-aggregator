from datetime import datetime
from typing import Any


class EventMapper:
    
    def _parse_datetime(
            self,
            value: str | None
        ) -> datetime | None:
        """Преобразует строку с датой в формате ISO 8601 в объект datetime."""
        if not value:
            return None
        try:
            # Пробуем распарсить ISO 8601 с часовым поясом
            return datetime.fromisoformat(value)
        except (ValueError, TypeError):
            return None

    
    def from_provider(
            self,
            data: dict
        ) -> dict[str, Any]:
        """Преобразует ответ Provider в плоский словарь для БД с правильными типами."""
        place = data.get("place", {})
        return {
            "id": data["id"],
            "name": data["name"],
            "place_id": place.get("id"),
            "place_name": place.get("name"),
            "place_city": place.get("city"),
            "place_address": place.get("address"),
            "seats_pattern": place.get("seats_pattern"),
            "event_time": self._parse_datetime(data.get("event_time")),
            "registration_deadline": self._parse_datetime(data.get("registration_deadline")),
            "status": data.get("status"),
            "number_of_visitors": data.get("number_of_visitors", 0),
            "changed_at": self._parse_datetime(data.get("changed_at")),
            "created_at": self._parse_datetime(data.get("created_at")),
            "status_changed_at": self._parse_datetime(data.get("status_changed_at")),
        }