from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class InterviewSession(Base):
    __tablename__ = "interview_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    job_title = Column(String, nullable=False)
    job_description = Column(Text, nullable=True)
    status = Column(String, default="in_progress")  # in_progress, completed
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Évaluation globale (calculée à la fin)
    overall_score = Column(Integer, nullable=True)
    feedback_summary = Column(Text, nullable=True)
    feedback_strengths = Column(Text, nullable=True)
    feedback_improvements = Column(Text, nullable=True)

    # Relations
    user = relationship("User", back_populates="sessions")
    questions = relationship("InterviewQuestion", back_populates="session", cascade="all, delete-orphan", order_by="InterviewQuestion.question_index")

class InterviewQuestion(Base):
    __tablename__ = "interview_questions"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("interview_sessions.id"), nullable=False)
    question_index = Column(Integer, nullable=False)  # 0, 1, 2...
    question_text = Column(Text, nullable=False)
    answer_text = Column(Text, nullable=True)          # Réponse du candidat
    feedback = Column(Text, nullable=True)             # Évaluation spécifique de la réponse
    score = Column(Integer, nullable=True)             # Note sur 100 de la réponse

    # Relations
    session = relationship("InterviewSession", back_populates="questions")
