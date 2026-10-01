from datetime import date, datetime, timezone

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.db import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


# --- Base (defined by the brief) -------------------------------------------


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)


class Course(Base):
    __tablename__ = "courses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    slug: Mapped[str] = mapped_column(String(160), unique=True, nullable=False)
    area: Mapped[str] = mapped_column(String(80), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False)  # published | draft

    leads: Mapped[list["Lead"]] = relationship(back_populates="course")


class Lead(Base):
    __tablename__ = "leads"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    phone: Mapped[str | None] = mapped_column(String(40), nullable=True)
    course_id: Mapped[int] = mapped_column(ForeignKey("courses.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=utcnow)  # UTC

    # --- Added by the invented feature («Log contact») ---------------------
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="open")  # open | closed
    next_contact_on: Mapped[date | None] = mapped_column(Date, nullable=True)  # NULL = due now
    closed_reason: Mapped[str | None] = mapped_column(String(40), nullable=True)
    phone_invalid: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    email_invalid: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    course: Mapped[Course] = relationship(back_populates="leads")
    attempts: Mapped[list["ContactAttempt"]] = relationship(
        back_populates="lead", order_by="ContactAttempt.created_at", cascade="all, delete-orphan"
    )


class ContactAttempt(Base):
    """One row per logged contact attempt (added by the invented feature)."""

    __tablename__ = "contact_attempts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    lead_id: Mapped[int] = mapped_column(ForeignKey("leads.id"), nullable=False, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    channel: Mapped[str] = mapped_column(String(10), nullable=False)  # phone | email
    outcome: Mapped[str] = mapped_column(String(30), nullable=False)
    note: Mapped[str | None] = mapped_column(Text, nullable=True)
    follow_up_on: Mapped[date | None] = mapped_column(Date, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=utcnow)  # UTC

    lead: Mapped[Lead] = relationship(back_populates="attempts")
    user: Mapped[User] = relationship()
