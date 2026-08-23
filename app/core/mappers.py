class EventMapper:
    @staticmethod
    def from_provider(data: dict) -> dict:
        """Преобразует ответ Provider в плоский словарь для БД"""
        place = data.get("place", {})
        return {
            "id": data["id"],
            "name": data["name"],
            "place_id": place.get("id"),
            "place_name": place.get("name"),
            "place_city": place.get("city"),
            "place_address": place.get("address"),
            "seats_pattern": place.get("seats_pattern"),
            "event_time": data.get("event_time"),
            "registration_deadline": data.get("registration_deadline"),
            "status": data.get("status"),
            "number_of_visitors": data.get("number_of_visitors", 0),
            "changed_at": data.get("changed_at"),
            "created_at": data.get("created_at"),
            "status_changed_at": data.get("status_changed_at"),
        }

class SyncMetaDTO:
    @classmethod
    def from_db(cls, row):
        return cls(...)  # если нужно