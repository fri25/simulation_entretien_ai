from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
import os

from app.database import engine, Base
# Importation importante pour enregistrer les modèles sur la metadata SQLAlchemy
import app.models
from app.routers import api_interview, views

# Création des tables de la base de données SQLite si elles n'existent pas encore
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Digi'innova. Simulation d'Entretien",
    description="Plateforme moderne de simulation d'entretien d'embauche assistée par IA",
    version="1.0.0"
)

# Configuration du dossier des fichiers statiques (CSS, JS, Images)
# S'assure que le dossier existe au cas où
os.makedirs("app/static/css", exist_ok=True)
os.makedirs("app/static/js", exist_ok=True)
os.makedirs("app/templates", exist_ok=True)

app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Enregistrement des routes de l'application
app.include_router(api_interview.router)
app.include_router(views.router)

@app.exception_handler(404)
async def custom_404_handler(request: Request, exc):
    # En cas de route introuvable, redirige vers la page d'accueil ou tableau de bord
    return RedirectResponse(url="/")
