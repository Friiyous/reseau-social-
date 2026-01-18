from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
import random
import string
from .. import models, schemas
from ..database import get_db
from ..auth import (
    authenticate_user,
    create_access_token,
    get_password_hash,
    get_current_user,
    ACCESS_TOKEN_EXPIRE_MINUTES,
)

router = APIRouter(prefix="/auth", tags=["Authentification"])


def generate_unique_id(db: Session) -> str:
    """Génère un identifiant unique SP-XXXXX"""
    while True:
        # Générer un numéro aléatoire à 5 chiffres
        number = ''.join(random.choices(string.digits, k=5))
        unique_id = f"SP-{number}"
        # Vérifier que cet ID n'existe pas déjà
        existing = db.query(models.User).filter(
            models.User.unique_id == unique_id
        ).first()
        if not existing:
            return unique_id


@router.post("/register", response_model=schemas.TokenResponse)
def register(user_data: schemas.UserCreate, db: Session = Depends(get_db)):
    """Inscription d'un nouvel agent de santé"""
    # Vérifier si l'email existe déjà
    existing_user = db.query(models.User).filter(
        models.User.email == user_data.email
    ).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cet email est déjà enregistré"
        )

    # Vérifier si le username existe déjà
    existing_username = db.query(models.User).filter(
        models.User.username == user_data.username
    ).first()
    if existing_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ce nom d'utilisateur est déjà pris"
        )

    # Créer l'utilisateur
    user = models.User(
        email=user_data.email,
        username=user_data.username,
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        district=user_data.district,
        health_center=user_data.health_center,
        role=user_data.role,
        professional_id=user_data.professional_id,
        password_hash=get_password_hash(user_data.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # Générer le token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.id}, expires_delta=access_token_expires
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": schemas.UserResponse.model_validate(user)
    }


@router.post("/login", response_model=schemas.TokenResponse)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """Connexion d'un agent de santé"""
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou mot de passe incorrect",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.id}, expires_delta=access_token_expires
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": schemas.UserResponse.model_validate(user)
    }


@router.get("/me", response_model=schemas.UserWithStats)
def get_current_user_info(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Récupérer les informations de l'utilisateur connecté avec statistiques"""
    from sqlalchemy import func

    user_data = schemas.UserWithStats.model_validate(current_user)

    # Compter les posts
    user_data.posts_count = db.query(func.count(models.Post.id)).filter(
        models.Post.author_id == current_user.id
    ).scalar() or 0

    # Compter les followers
    user_data.followers_count = db.query(func.count(models.Follow.id)).filter(
        models.Follow.following_id == current_user.id
    ).scalar() or 0

    # Compter les following
    user_data.following_count = db.query(func.count(models.Follow.id)).filter(
        models.Follow.follower_id == current_user.id
    ).scalar() or 0

    return user_data


# ============ QUICK-REGISTER ERROR HANDLING START ============
@router.post("/quick-register", response_model=schemas.TokenResponse)
def quick_register(user_data: schemas.QuickRegisterRequest, db: Session = Depends(get_db)):
    """Inscription rapide sans mot de passe pour les agents de santé"""
    try:
        # Validation des champs requis
        if not user_data.first_name or not user_data.last_name:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Prénom et nom sont requis"
            )
        if not user_data.health_center:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Le centre de santé est requis"
            )

        # Générer un identifiant unique
        unique_id = generate_unique_id(db)

        # Créer l'utilisateur
        user = models.User(
            unique_id=unique_id,
            email=None,
            username=None,
            password_hash=None,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            district=user_data.district,
            health_center=user_data.health_center,
            role="agent_sante",
            specialty=user_data.specialty,
            department=user_data.department,
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        # Générer le token
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.id}, expires_delta=access_token_expires
        )

        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": schemas.UserResponse.model_validate(user)
        }

    except HTTPException:
        raise
    except Exception as e:
        # Logger l'erreur complète
        import traceback
        print(f"=== QuickRegister Error ===")
        print(f"Error: {e}")
        traceback.print_exc()
        print(f"============================")

        # Gérer les erreurs de contrainte unique sur unique_id
        error_str = str(e).lower()
        if "unique_id" in error_str or "duplicate column value" in error_str:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Erreur de génération d'ID, veuillez réessayer"
            )

        # Retourner une erreur générique
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de l'inscription"
        )
# ============ QUICK-REGISTER ERROR HANDLING END ============


@router.post("/logout")
def logout(current_user: models.User = Depends(get_current_user)):
    """Déconnexion (côté client uniquement pour JWT)"""
    return {"message": "Déconnexion réussie"}


@router.post("/change-password")
def change_password(
    data: schemas.ChangePasswordRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Changer le mot de passe"""
    # Vérifier si l'utilisateur a un mot de passe
    if not current_user.password_hash:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Les comptes créés avec inscription rapide n'ont pas de mot de passe"
        )

    # Vérifier l'ancien mot de passe
    if not verify_password(data.old_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ancien mot de passe incorrect"
        )

    # Mettre à jour le mot de passe
    current_user.password_hash = get_password_hash(data.new_password)
    db.commit()

    return {"message": "Mot de passe modifié avec succès"}


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Vérifier un mot de passe (exporté pour usage dans auth.py)"""
    import bcrypt
    return bcrypt.checkpw(
        plain_password.encode('utf-8'),
        hashed_password.encode('utf-8')
    )
