from datetime import timedelta

from flask import Flask, g, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager

from backend import config
from backend.routes.auth import bp as auth_bp
from backend.routes.courses import bp as courses_bp
from backend.routes.leads import bp as leads_bp
from backend.seed import seed_if_empty
from backend.services.errors import ServiceError

SESSION_EXPIRED = "Your session expired. Sign in again."


def create_app() -> Flask:
    app = Flask(__name__)
    app.config["JWT_SECRET_KEY"] = config.JWT_SECRET_KEY
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=config.JWT_HOURS)
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    jwt = JWTManager(app)

    @jwt.expired_token_loader
    def _expired(_header, _payload):
        return jsonify(error=SESSION_EXPIRED), 401

    @jwt.invalid_token_loader
    def _invalid(_reason):
        return jsonify(error=SESSION_EXPIRED), 401

    @jwt.unauthorized_loader
    def _missing(_reason):
        return jsonify(error="Sign in to continue."), 401

    @app.errorhandler(ServiceError)
    def _service_error(err: ServiceError):
        session = g.get("db")
        if session is not None:
            session.rollback()
        return jsonify(error=err.message), err.status

    @app.errorhandler(404)
    def _not_found(_err):
        return jsonify(error="Not found."), 404

    @app.teardown_appcontext
    def _close_session(exc):
        session = g.pop("db", None)
        if session is not None:
            if exc is None:
                session.commit()
            else:
                session.rollback()
            session.close()

    app.register_blueprint(auth_bp)
    app.register_blueprint(courses_bp)
    app.register_blueprint(leads_bp)

    seed_if_empty()
    return app


if __name__ == "__main__":
    create_app().run(port=config.API_PORT, debug=True)
