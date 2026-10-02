from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from backend.routes.common import db
from backend.services import leads

bp = Blueprint("leads", __name__, url_prefix="/api/leads")


@bp.get("")
@jwt_required()
def index():
    scope = request.args.get("scope")
    if scope == "all":
        return jsonify(leads.list_all_leads(db()))
    if scope == "contacted":
        return jsonify(
            leads.list_contacted(
                db(),
                date_from=request.args.get("from"),
                date_to=request.args.get("to"),
                by=request.args.get("by", "contact"),
            )
        )
    return jsonify(leads.list_today_queue(db()))


@bp.get("/<int:lead_id>")
@jwt_required()
def show(lead_id: int):
    return jsonify(leads.get_lead(db(), lead_id))


@bp.post("/<int:lead_id>/contacts")
@jwt_required()
def log_contact(lead_id: int):
    body = request.get_json(silent=True) or {}
    result = leads.log_contact(
        db(),
        lead_id,
        outcome=body.get("outcome"),
        user_id=int(get_jwt_identity()),
        channel=body.get("channel"),
        note=body.get("note"),
        follow_up_on=body.get("follow_up_on"),
    )
    db().commit()
    return jsonify(result), 201


@bp.delete("/<int:lead_id>/contacts/<int:attempt_id>")
@jwt_required()
def undo_contact(lead_id: int, attempt_id: int):
    """Undo the last logged attempt (safety net for a wrong click or key)."""
    result = leads.undo_contact(db(), lead_id, attempt_id)
    db().commit()
    return jsonify(result)


@bp.post("")
def intake():
    """Simulates the course landing form (the public site is out of scope).
    Draft courses reject new leads."""
    body = request.get_json(silent=True) or {}
    lead = leads.create_lead(
        db(), body.get("name"), body.get("email"), body.get("course_slug"), body.get("phone")
    )
    db().commit()
    return jsonify(lead), 201
