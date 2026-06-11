"""User domain model."""

from dataclasses import dataclass

@dataclass
class User:
    id: int
    username: str
    password_hash: str

    def is_active(self) -> bool:
        return True

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "username": self.username,
        }
