from sqlalchemy.orm import Session

from app.models.user import User
from app.models.interview import InterviewSession, InterviewQuestion
from app.services.ai_service import ai_service

ANONYMOUS_USERNAME = "anonymous"
ANONYMOUS_EMAIL = "anonymous@example.com"


def get_anonymous_user(db: Session) -> User:
    user = db.query(User).filter(User.username == ANONYMOUS_USERNAME).first()
    if not user:
        user = User(
            username=ANONYMOUS_USERNAME,
            email=ANONYMOUS_EMAIL,
            hashed_password="anonymous"
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    return user


def create_interview_session(job_title: str, job_description: str, db: Session, count: int = 5) -> InterviewSession:
    if not job_title or not job_title.strip():
        raise ValueError("L'intitulé du poste ne peut pas être vide.")

    anonymous_user = get_anonymous_user(db)
    session = InterviewSession(
        user_id=anonymous_user.id,
        job_title=job_title.strip(),
        job_description=job_description.strip() if job_description else "",
        status="in_progress"
    )
    db.add(session)
    db.commit()
    db.refresh(session)

    questions_text = ai_service.generate_questions(
        job_title=session.job_title,
        job_description=session.job_description,
        count=count
    )

    for index, text in enumerate(questions_text):
        q = InterviewQuestion(
            session_id=session.id,
            question_index=index,
            question_text=text
        )
        db.add(q)

    db.commit()
    db.refresh(session)
    return session
