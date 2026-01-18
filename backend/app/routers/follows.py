from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from .. import models, schemas
from ..database import get_db
from ..auth import get_current_user

router = APIRouter(prefix="/follows", tags=["Suivis"])


@router.post("/{user_id}", response_model=schemas.FollowResponse)
def follow_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Suivre un agent de santé"""
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Vous ne pouvez pas vous suivre vous-même"
        )

    user_to_follow = db.query(models.User).filter(models.User.id == user_id).first()
    if not user_to_follow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Utilisateur non trouvé"
        )

    # Vérifier si déjà suivi
    existing_follow = db.query(models.Follow).filter(
        models.Follow.follower_id == current_user.id,
        models.Follow.following_id == user_id
    ).first()

    if existing_follow:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Vous suivez déjà cet utilisateur"
        )

    follow = models.Follow(follower_id=current_user.id, following_id=user_id)
    db.add(follow)
    db.commit()
    db.refresh(follow)

    return schemas.FollowResponse.model_validate(follow)


@router.delete("/{user_id}")
def unfollow_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Ne plus suivre un agent de santé"""
    follow = db.query(models.Follow).filter(
        models.Follow.follower_id == current_user.id,
        models.Follow.following_id == user_id
    ).first()

    if not follow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vous ne suivez pas cet utilisateur"
        )

    db.delete(follow)
    db.commit()
    return {"message": "Vous ne suivez plus cet utilisateur"}


@router.get("/followers", response_model=List[schemas.UserResponse])
def get_my_followers(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Liste de mes followers"""
    follows = db.query(models.Follow).filter(
        models.Follow.following_id == current_user.id
    ).offset(skip).limit(limit).all()

    follower_ids = [f.follower_id for f in follows]
    users = db.query(models.User).filter(models.User.id.in_(follower_ids)).all()
    return users


@router.get("/following", response_model=List[schemas.UserResponse])
def get_my_following(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Liste des utilisateurs que je suis"""
    follows = db.query(models.Follow).filter(
        models.Follow.follower_id == current_user.id
    ).offset(skip).limit(limit).all()

    following_ids = [f.following_id for f in follows]
    users = db.query(models.User).filter(models.User.id.in_(following_ids)).all()
    return users


@router.get("/followers/{user_id}", response_model=List[schemas.UserResponse])
def get_user_followers(
    user_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Followers d'un utilisateur"""
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Utilisateur non trouvé"
        )

    follows = db.query(models.Follow).filter(
        models.Follow.following_id == user_id
    ).offset(skip).limit(limit).all()

    follower_ids = [f.follower_id for f in follows]
    users = db.query(models.User).filter(models.User.id.in_(follower_ids)).all()
    return users


@router.get("/following/{user_id}", response_model=List[schemas.UserResponse])
def get_user_following(
    user_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Utilisateurs suivis par un utilisateur"""
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Utilisateur non trouvé"
        )

    follows = db.query(models.Follow).filter(
        models.Follow.follower_id == user_id
    ).offset(skip).limit(limit).all()

    following_ids = [f.following_id for f in follows]
    users = db.query(models.User).filter(models.User.id.in_(following_ids)).all()
    return users
