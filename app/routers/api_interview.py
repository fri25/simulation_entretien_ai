from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.interview import InterviewSession, InterviewQuestion
from app.schemas.interview import InterviewCreate, InterviewResponse, AnswerSubmit
from app.services.ai_service import ai_service
from app.services.interview_service import create_interview_session

router = APIRouter(prefix="/api/interviews", tags=["interviews"])

@router.post("/create", response_model=int)
def create_interview(
    data: InterviewCreate,
    db: Session = Depends(get_db)
):
    """
    Crée une nouvelle simulation d'entretien et pré-programme/génère automatiquement
    les questions d'entretien grâce à l'intelligence artificielle.
    """
    if not data.job_title.strip():
        raise HTTPException(status_code=400, detail="L'intitulé du poste ne peut pas être vide.")

    try:
        session = create_interview_session(
            job_title=data.job_title,
            job_description=data.job_description or "",
            db=db,
            count=5
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la génération automatique des questions : {str(e)}"
        )

    return session.id

@router.get("/{session_id}", response_model=InterviewResponse)
def get_interview(
    session_id: int,
    db: Session = Depends(get_db)
):
    """
    Récupère les détails complets d'une session de simulation d'entretien.
    """
    session = db.query(InterviewSession).filter(
        InterviewSession.id == session_id
    ).first()

    if not session:
        raise HTTPException(status_code=404, detail="Simulation d'entretien introuvable.")
    
    return session

@router.post("/{session_id}/answer")
def submit_answer(
    session_id: int,
    data: AnswerSubmit,
    db: Session = Depends(get_db)
):
    """
    Soumet la réponse du candidat pour une question spécifique de l'entretien.
    """
    # Vérifier que la session existe
    session = db.query(InterviewSession).filter(
        InterviewSession.id == session_id
    ).first()

    if not session:
        raise HTTPException(status_code=404, detail="Simulation d'entretien introuvable.")

    if session.status == "completed":
        raise HTTPException(status_code=400, detail="Cet entretien est déjà terminé.")

    # Récupérer la question correspondante
    question = db.query(InterviewQuestion).filter(
        InterviewQuestion.session_id == session_id,
        InterviewQuestion.id == data.question_id
    ).first()

    if not question:
        raise HTTPException(status_code=404, detail="Question introuvable dans cette session.")

    # Enregistrer la réponse
    question.answer_text = data.answer_text.strip()
    db.commit()

    # Déterminer s'il y a d'autres questions
    next_question = db.query(InterviewQuestion).filter(
        InterviewQuestion.session_id == session_id,
        InterviewQuestion.question_index == question.question_index + 1
    ).first()

    return {
        "message": "Réponse enregistrée.",
        "has_next": next_question is not None,
        "next_question_id": next_question.id if next_question else None
    }

@router.post("/{session_id}/evaluate")
def evaluate_interview(
    session_id: int,
    db: Session = Depends(get_db)
):
    """
    Termine l'entretien et lance l'évaluation par l'IA de l'ensemble de l'échange.
    """
    session = db.query(InterviewSession).filter(
        InterviewSession.id == session_id
    ).first()

    if not session:
        raise HTTPException(status_code=404, detail="Simulation d'entretien introuvable.")

    if session.status == "completed":
        return {"message": "Entretien déjà évalué.", "session_id": session.id}

    # Récupérer toutes les questions et réponses
    questions = session.questions
    
    # Vérifier que toutes les questions ont reçu une réponse
    qa_list = []
    for q in questions:
        if not q.answer_text or not q.answer_text.strip():
            # Si le candidat termine l'entretien prématurément, on met une réponse par défaut
            q.answer_text = "[Non répondu ou passé par le candidat]"
            
        qa_list.append({
            "question_index": q.question_index,
            "question": q.question_text,
            "answer": q.answer_text
        })

    # Lancer l'évaluation par l'IA
    try:
        evaluation = ai_service.evaluate_interview(session.job_title, qa_list)
        
        # Enregistrer l'évaluation globale
        session.overall_score = evaluation.get("overall_score", 50)
        session.feedback_summary = evaluation.get("feedback_summary", "")
        session.feedback_strengths = evaluation.get("strengths", "")
        session.feedback_improvements = evaluation.get("improvements", "")
        session.status = "completed"

        # Enregistrer les évaluations par question
        for q_fb in evaluation.get("question_feedbacks", []):
            idx = q_fb.get("question_index")
            q_row = next((q for q in questions if q.question_index == idx), None)
            if q_row:
                q_row.score = q_fb.get("score", 50)
                q_row.feedback = q_fb.get("feedback", "")

        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de l'évaluation finale de l'entretien par l'IA : {str(e)}"
        )

    return {"message": "Évaluation complétée avec succès.", "score": session.overall_score}
