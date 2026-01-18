from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from .. import models, schemas
from ..database import get_db
from ..auth import get_current_user

router = APIRouter(prefix="/users", tags=["Utilisateurs"])


def count_posts(db: Session, user_id: int) -> int:
    return db.query(models.Post).filter(models.Post.author_id == user_id).count()


def count_followers(db: Session, user_id: int) -> int:
    return db.query(models.Follow).filter(models.Follow.following_id == user_id).count()


def count_following(db: Session, user_id: int) -> int:
    return db.query(models.Follow).filter(models.Follow.follower_id == user_id).count()


@router.get("/", response_model=List[schemas.UserResponse])
def get_all_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Liste de tous les agents de santé"""
    users = db.query(models.User).offset(skip).limit(limit).all()
    return users


@router.get("/district/{district}", response_model=List[schemas.UserResponse])
def get_users_by_district(
    district: str,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Agents de santé d'un district spécifique"""
    users = db.query(models.User).filter(
        models.User.district == district
    ).offset(skip).limit(limit).all()
    return users


@router.get("/{user_id}", response_model=schemas.UserWithStats)
def get_user_profile(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Profil d'un agent de santé avec statistiques"""
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Utilisateur non trouvé"
        )

    user_data = schemas.UserWithStats.model_validate(user)
    user_data.posts_count = count_posts(db, user_id)
    user_data.followers_count = count_followers(db, user_id)
    user_data.following_count = count_following(db, user_id)
    return user_data


@router.put("/me", response_model=schemas.UserResponse)
def update_current_user(
    user_update: schemas.UserUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Modifier son propre profil"""
    update_data = user_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(current_user, field, value)
    db.commit()
    db.refresh(current_user)
    return schemas.UserResponse.model_validate(current_user)


@router.get("/search/{query}", response_model=List[schemas.UserResponse])
def search_users(
    query: str,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Rechercher des agents de santé par nom ou username"""
    users = db.query(models.User).filter(
        (models.User.first_name.contains(query)) |
        (models.User.last_name.contains(query)) |
        (models.User.username.contains(query)) |
        (models.User.district.contains(query))
    ).offset(skip).limit(limit).all()
    return users