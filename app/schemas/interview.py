from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class QuestionResponse(BaseModel):
    id: int
    question_index: int
    question_text: str
    answer_text: Optional[str] = None
    feedback: Optional[str] = None
    score: Optional[int] = None

    class Config:
        from_attributes = True

class InterviewCreate(BaseModel):
    job_title: str
    job_description: Optional[str] = ""

class InterviewResponse(BaseModel):
    id: int
    job_title: str
    job_description: Optional[str] = None
    status: str
    created_at: datetime
    overall_score: Optional[int] = None
    feedback_summary: Optional[str] = None
    feedback_strengths: Optional[Optional[str]] = None
    feedback_improvements: Optional[Optional[str]] = None
    questions: List[QuestionResponse] = []

    class Config:
        from_attributes = True

class AnswerSubmit(BaseModel):
    question_id: int
    answer_text: str
