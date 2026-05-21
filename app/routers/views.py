from typing import Optional

from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
import os
from urllib.parse import quote_plus

from app.database import get_db
from app.models.interview import InterviewSession, InterviewQuestion
from app.services.ai_service import ai_service
from app.services.interview_service import create_interview_session

router = APIRouter(tags=["views"])

# Déterminer le dossier absolu ou relatif des templates
templates = Jinja2Templates(directory="app/templates")

@router.get("/", response_class=HTMLResponse)
def page_home(request: Request):
    return templates.TemplateResponse(request, "index.html", {"user": None})

@router.get("/dashboard", response_class=HTMLResponse)
def page_dashboard(request: Request, db: Session = Depends(get_db)):
    # Récupérer l'historique des entretiens
    sessions = db.query(InterviewSession).order_by(InterviewSession.created_at.desc()).all()

    # Calcul des statistiques
    total_completed = sum(1 for s in sessions if s.status == "completed")
    avg_score = 0
    if total_completed > 0:
        avg_score = int(sum(s.overall_score for s in sessions if s.overall_score is not None) / total_completed)

    # Récupérer l'état de la clé API pour l'afficher sur le dashboard (si en mode démo ou réel)
    is_demo = ai_service.is_mock

    return templates.TemplateResponse(request, "dashboard.html", {
        "user": None,
        "sessions": sessions,
        "total_completed": total_completed,
        "avg_score": avg_score,
        "is_demo": is_demo
    })

@router.get("/launch")
def launch_service(
    request: Request,
    service: str = Query(..., description="Nom du service à activer depuis Laravel (ex: interview, dashboard)."),
    job_title: Optional[str] = Query(None, description="Titre du poste pour lancer la simulation d'entretien."),
    job_description: Optional[str] = Query(None, description="Description ou contexte du poste à utiliser pour la génération."),
    callback_url: Optional[str] = Query(None, description="URL de retour optionnelle après utilisation du service."),
    db: Session = Depends(get_db)
):
    service_key = service.strip().lower()
    if service_key == "interview":
        if not job_title or not job_title.strip():
            return RedirectResponse(url=f"/interview/new?job_title={quote_plus(job_title or '')}&job_description={quote_plus(job_description or '')}")
        try:
            session = create_interview_session(job_title=job_title, job_description=job_description or "", db=db)
            return RedirectResponse(url=f"/interview/{session.id}")
        except Exception:
            # Si la création échoue, redirige sur la page de configuration
            return RedirectResponse(url=f"/interview/new?job_title={quote_plus(job_title or '')}&job_description={quote_plus(job_description or '')}")

    if service_key == "dashboard":
        return RedirectResponse(url="/dashboard")

    # Autres services possibles (CV, scoring, ATS...) renvoient vers l'accueil ou vers une future page dédiée
    return RedirectResponse(url="/")

@router.get("/interview/new", response_class=HTMLResponse)
def page_new_interview(
    request: Request,
    job_title: Optional[str] = None,
    job_description: Optional[str] = None
):
    return templates.TemplateResponse(request, "new_interview.html", {
        "user": None,
        "job_title": job_title,
        "job_description": job_description
    })

@router.get("/interview/{session_id}", response_class=HTMLResponse)
def page_interview_chat(
    session_id: int, 
    request: Request, 
    db: Session = Depends(get_db)
):
    # Récupérer la session
    session = db.query(InterviewSession).filter(
        InterviewSession.id == session_id
    ).first()

    if not session:
        return RedirectResponse(url="/dashboard")

    # Si l'entretien est déjà fini, on va directement aux résultats
    if session.status == "completed":
        return RedirectResponse(url=f"/interview/{session_id}/results")

    # Récupérer les questions de l'entretien
    questions = session.questions

    return templates.TemplateResponse(request, "interview.html", {
        "user": None,
        "session": session,
        "questions": questions
    })

@router.get("/interview/{session_id}/results", response_class=HTMLResponse)
def page_results(
    session_id: int, 
    request: Request, 
    db: Session = Depends(get_db)
):
    # Récupérer la session
    session = db.query(InterviewSession).filter(
        InterviewSession.id == session_id
    ).first()

    if not session:
        return RedirectResponse(url="/dashboard")

    # Si l'entretien n'est pas encore fini, on redirige vers le chat
    if session.status == "in_progress":
        return RedirectResponse(url=f"/interview/{session_id}")

    return templates.TemplateResponse(request, "results.html", {
        "user": None,
        "session": session,
        "is_demo": ai_service.is_mock
    })
