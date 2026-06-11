"""Payment service - cross cutting concern that touches multiple areas (real coupling)."""

from database import Database
from auth import AuthService
from models.user import User

class PaymentService:
    def __init__(self, db: Database, auth: AuthService):
        self.db = db
        self.auth = auth

    def process_payment(self, user_id: int, amount: float, token: str) -> dict:
        verification = self.auth.verify_token(token)
        if not verification.get("valid"):
            return {"status": "unauthorized"}

        user = self.db.get_user(user_id)
        if not user:
            return {"status": "user_not_found"}

        # Simulate charging + recording
        return {
            "status": "success",
            "user": user.username,
            "amount": amount,
            "transaction_id": f"txn_{user_id}_{int(amount)}"
        }
