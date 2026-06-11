"""API routes module."""

from auth import AuthService
from models.user import User
from flask import Flask, request, jsonify

def create_app(auth_service: AuthService) -> Flask:
    app = Flask(__name__)

    @app.route("/login", methods=["POST"])
    def login():
        data = request.get_json() or {}
        result = auth_service.login(data.get("username", ""), data.get("password", ""))
        return jsonify(result)

    @app.route("/register", methods=["POST"])
    def register():
        data = request.get_json() or {}
        user = auth_service.register_user(data.get("username", ""), data.get("password", ""))
        return jsonify({"status": "created", "user": user.to_dict()})

    @app.route("/health", methods=["GET"])
    def health():
        return {"status": "ok"}

    return app
