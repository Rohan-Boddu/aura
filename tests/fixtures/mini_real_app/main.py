#!/usr/bin/env python3
"""Main application entry point."""

from api.routes import create_app
from database import Database
from auth import AuthService

def main():
    db = Database()
    auth = AuthService(db)
    app = create_app(auth)
    print("AURA Mini Real App started")
    return app

if __name__ == "__main__":
    main()
