from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required

from backend.routes.common import db
from backend.services.courses import list_courses

bp = Blueprint("courses", __name__, url_prefix="/api/courses")


@bp.get("")
@jwt_required()
def index():
    return jsonify(courses=list_courses(db()))
