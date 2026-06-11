"""Database access layer - intentionally large to trigger real god-object / oversized risk."""

from models.user import User
import sqlite3
from typing import Optional, List

class Database:
    def __init__(self, db_path: str = ":memory:"):
        self.conn = sqlite3.connect(db_path)
        self._create_tables()

    def _create_tables(self):
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                username TEXT UNIQUE,
                password_hash TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY,
                user_id INTEGER,
                token TEXT,
                expires_at TIMESTAMP
            )
        """)
        self.conn.commit()

    def get_user_by_username(self, username: str) -> Optional[User]:
        cursor = self.conn.execute(
            "SELECT id, username, password_hash FROM users WHERE username = ?", (username,)
        )
        row = cursor.fetchone()
        if row:
            return User(id=row[0], username=row[1], password_hash=row[2])
        return None

    def create_user(self, username: str, password_hash: str) -> User:
        cursor = self.conn.execute(
            "INSERT INTO users (username, password_hash) VALUES (?, ?)",
            (username, password_hash)
        )
        self.conn.commit()
        return User(id=cursor.lastrowid, username=username, password_hash=password_hash)

    def get_user(self, user_id: int) -> Optional[User]:
        cursor = self.conn.execute(
            "SELECT id, username, password_hash FROM users WHERE id = ?", (user_id,)
        )
        row = cursor.fetchone()
        if row:
            return User(id=row[0], username=row[1], password_hash=row[2])
        return None

    def save_session(self, user_id: int, token: str):
        self.conn.execute(
            "INSERT INTO sessions (user_id, token) VALUES (?, ?)",
            (user_id, token)
        )
        self.conn.commit()

    def close(self):
        self.conn.close()

    # Extra methods to make it realistically "large" (real god object risk)
    def query_users(self, limit: int = 100):
        cursor = self.conn.execute("SELECT * FROM users LIMIT ?", (limit,))
        return cursor.fetchall()

    def delete_user(self, user_id: int):
        self.conn.execute("DELETE FROM users WHERE id = ?", (user_id,))
        self.conn.commit()

    def count_users(self) -> int:
        cursor = self.conn.execute("SELECT COUNT(*) FROM users")
        return cursor.fetchone()[0]

    def vacuum(self):
        self.conn.execute("VACUUM")

    def backup(self, target_path: str):
        # Pretend backup logic
        pass

    def migrate_schema(self, version: int):
        pass
