from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required

from backend.models import User
from backend.routes.common import db
from backend.services.users import authenticate

bp = Blueprint("auth", __name__, url_prefix="/api/auth")


@bp.post("/login")
def login():
    body = request.get_json(silent=True) or {}
    user = authenticate(db(), body.get("email"), body.get("password"))
    token = create_access_token(identity=str(user.id))
    return jsonify(token=token, user={"email": user.email, "name": user.name})


@bp.get("/me")
@jwt_required()
def me():
    user = db().get(User, int(get_jwt_identity()))
    if user is None:
        return jsonify(error="Your session expired. Sign in again."), 401
    return jsonify(email=user.email, name=user.name)
