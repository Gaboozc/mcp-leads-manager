from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend.models import Course, Lead


def list_courses(session: Session) -> list[dict]:
    open_counts = dict(
        session.execute(
            select(Lead.course_id, func.count(Lead.id)).where(Lead.status == "open").group_by(Lead.course_id)
        ).all()
    )
    courses = session.scalars(select(Course).order_by(Course.status.desc(), Course.name)).all()
    return [
        {
            "id": c.id,
            "name": c.name,
            "slug": c.slug,
            "area": c.area,
            "status": c.status,
            "open_leads": open_counts.get(c.id, 0),
        }
        for c in courses
    ]
