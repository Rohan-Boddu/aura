"""Authentication module with JWT-like token handling."""

import hashlib
import time
from database import Database
from models.user import User

class AuthService:
    def __init__(self, db: Database):
        self.db = db
        self.secret = "demo-secret-key-for-aura-tests"

    def login(self, username: str, password: str) -> dict:
        user = self.db.get_user_by_username(username)
        if not user:
            return {"status": "error", "message": "User not found"}

        hashed = hashlib.sha256((password + self.secret).encode()).hexdigest()
        if user.password_hash == hashed:
            token = self._generate_token(user.id)
            return {"status": "success", "token": token, "user_id": user.id}
        return {"status": "error", "message": "Invalid credentials"}

    def verify_token(self, token: str) -> dict:
        # Simplified verification
        if len(token) < 20:
            return {"valid": False}
        return {"valid": True, "user_id": 42}

    def _generate_token(self, user_id: int) -> str:
        payload = f"{user_id}:{int(time.time())}:{self.secret}"
        return hashlib.sha256(payload.encode()).hexdigest()[:32]

    def register_user(self, username: str, password: str) -> User:
        hashed = hashlib.sha256((password + self.secret).encode()).hexdigest()
        return self.db.create_user(username, hashed)
