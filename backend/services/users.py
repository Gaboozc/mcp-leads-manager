from sqlalchemy import func, select
from sqlalchemy.orm import Session
from werkzeug.security import check_password_hash

from backend.models import User
from backend.services.errors import ServiceError


def authenticate(session: Session, email: str, password: str) -> User:
    email = (email or "").strip().lower()
    user = session.scalars(select(User).where(func.lower(User.email) == email)).first()
    if user is None or not check_password_hash(user.password_hash, password or ""):
        raise ServiceError("Wrong email or password.", 401)
    return user


def get_by_email(session: Session, email: str) -> User | None:
    return session.scalars(select(User).where(func.lower(User.email) == email.strip().lower())).first()
