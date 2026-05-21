from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from fastapi.security import OAuth2PasswordBearer
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Optional

from app.database import get_db
from app.config import settings
from app.models.user import User
from app.schemas.user import UserCreate, UserLogin

router = APIRouter(prefix="/auth", tags=["auth"])

# Hachage des mots de passe
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

# JWT & Cookies
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

# Obtenir l'utilisateur connecté via le Cookie
def get_current_user(request: Request, db: Session = Depends(get_db)) -> Optional[User]:
    token = request.cookies.get("access_token")
    if not token:
        return None
    
    # Le cookie commence par "Bearer " si configuré ainsi
    if token.startswith("Bearer "):
        token = token[7:]

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            return None
    except JWTError:
        return None
        
    user = db.query(User).filter(User.username == username).first()
    return user

# Middleware optionnel pour forcer la connexion
def get_current_user_required(request: Request, db: Session = Depends(get_db)) -> User:
    user = get_current_user(request, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Non authentifié. Veuillez vous connecter.",
        )
    return user

@router.post("/register")
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    # Vérifier si l'utilisateur existe déjà
    existing_user = db.query(User).filter(
        (User.username == user_data.username) | (User.email == user_data.email)
    ).first()
    
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Le nom d'utilisateur ou l'adresse email est déjà utilisé."
        )

    try:
        hashed_password = get_password_hash(user_data.password)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    new_user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hashed_password
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return {"message": "Inscription réussie !", "username": new_user.username}

@router.post("/login")
def login(login_data: UserLogin, response: Response, db: Session = Depends(get_db)):
    # Recherche par nom d'utilisateur ou par email
    user = db.query(User).filter(
        (User.username == login_data.username_or_email) | (User.email == login_data.username_or_email)
    ).first()

    if not user or not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=400,
            detail="Nom d'utilisateur/email ou mot de passe incorrect."
        )

    # Création du Token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )

    # Définition du Cookie HTTP-Only pour sécuriser la session
    response.set_cookie(
        key="access_token",
        value=f"Bearer {access_token}",
        httponly=True,
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        expires=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        samesite="lax",
        secure=False  # Mettre à True en production avec HTTPS
    )

    return {"message": "Connexion réussie !", "username": user.username}

@router.get("/logout")
def logout(response: Response):
    # Supprimer le cookie de session
    response.delete_cookie("access_token")
    return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
