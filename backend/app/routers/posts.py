from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from .. import models, schemas
from ..database import get_db
from ..auth import get_current_user

router = APIRouter(prefix="/posts", tags=["Publications"])


def get_post_with_details(db: Session, post_id: int, current_user_id: int = None):
    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if not post:
        return None

    # Vérifier si l'utilisateur actuel a liké
    is_liked = False
    if current_user_id:
        like = db.query(models.Like).filter(
            models.Like.post_id == post_id,
            models.Like.user_id == current_user_id
        ).first()
        is_liked = like is not None

    # Compter les likes et comments
    likes_count = db.query(models.Like).filter(models.Like.post_id == post_id).count()
    comments_count = db.query(models.Comment).filter(models.Comment.post_id == post_id).count()

    post_data = schemas.PostResponse.model_validate(post)
    post_data.likes_count = likes_count
    post_data.comments_count = comments_count
    post_data.is_liked_by_me = is_liked
    return post_data


@router.get("/", response_model=List[schemas.PostResponse])
def get_posts(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Récupérer le fil d'actualité (tous les posts)"""
    posts = db.query(models.Post).order_by(
        models.Post.created_at.desc()
    ).offset(skip).limit(limit).all()

    result = []
    for post in posts:
        post_data = get_post_with_details(db, post.id, current_user.id)
        result.append(post_data)
    return result


@router.get("/user/{user_id}/", response_model=List[schemas.PostResponse])
def get_user_posts(
    user_id: int,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Posts d'un utilisateur spécifique"""
    posts = db.query(models.Post).filter(
        models.Post.author_id == user_id
    ).order_by(models.Post.created_at.desc()).offset(skip).limit(limit).all()

    result = []
    for post in posts:
        post_data = get_post_with_details(db, post.id, current_user.id)
        result.append(post_data)
    return result


@router.get("/{post_id}", response_model=schemas.PostWithComments)
def get_post_details(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Détails d'un post avec tous les commentaires"""
    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post non trouvé"
        )

    post_data = get_post_with_details(db, post_id, current_user.id)

    # Récupérer les commentaires
    comments = db.query(models.Comment).filter(
        models.Comment.post_id == post_id
    ).order_by(models.Comment.created_at.asc()).all()

    post_data.comments = [
        schemas.CommentResponse.model_validate(c) for c in comments
    ]
    return post_data


@router.post("/", response_model=schemas.PostResponse)
def create_post(
    post_data: schemas.PostCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Créer une nouvelle publication"""
    post = models.Post(
        content=post_data.content,
        image_url=post_data.image_url,
        author_id=current_user.id
    )
    db.add(post)
    db.commit()
    db.refresh(post)

    return get_post_with_details(db, post.id, current_user.id)


@router.delete("/{post_id}")
def delete_post(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Supprimer une de ses publications"""
    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post non trouvé"
        )

    if post.author_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vous ne pouvez pas supprimer ce post"
        )

    db.delete(post)
    db.commit()
    return {"message": "Post supprimé avec succès"}


# ============ PUT Post ============

@router.put("/{post_id}", response_model=schemas.PostResponse)
def update_post(
    post_id: int,
    post_data: schemas.PostCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Modifier une de ses publications"""
    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post non trouvé"
        )

    if post.author_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vous ne pouvez pas modifier ce post"
        )

    post.content = post_data.content
    post.image_url = post_data.image_url
    db.commit()
    db.refresh(post)

    return get_post_with_details(db, post.id, current_user.id)


# ============ Likes ============

@router.post("/{post_id}/like", response_model=schemas.LikeResponse)
def like_post(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Liker un post"""
    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post non trouvé"
        )

    # Vérifier si déjà liké
    existing_like = db.query(models.Like).filter(
        models.Like.post_id == post_id,
        models.Like.user_id == current_user.id
    ).first()

    if existing_like:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Vous avez déjà liké ce post"
        )

    like = models.Like(post_id=post_id, user_id=current_user.id)
    db.add(like)
    db.commit()
    db.refresh(like)
    return schemas.LikeResponse.model_validate(like)


@router.delete("/{post_id}/like")
def unlike_post(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Retirer son like d'un post"""
    like = db.query(models.Like).filter(
        models.Like.post_id == post_id,
        models.Like.user_id == current_user.id
    ).first()

    if not like:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Like non trouvé"
        )

    db.delete(like)
    db.commit()
    return {"message": "Like retiré"}


# ============ Comments ============

@router.post("/{post_id}/comments", response_model=schemas.CommentResponse)
def create_comment(
    post_id: int,
    comment_data: schemas.CommentCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Commenter un post"""
    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post non trouvé"
        )

    comment = models.Comment(
        content=comment_data.content,
        post_id=post_id,
        author_id=current_user.id
    )
    db.add(comment)
    db.commit()
    db.refresh(comment)

    return schemas.CommentResponse.model_validate(comment)


@router.delete("/{post_id}/comments/{comment_id}")
def delete_comment(
    post_id: int,
    comment_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Supprimer un de ses commentaires"""
    comment = db.query(models.Comment).filter(
        models.Comment.id == comment_id,
        models.Comment.post_id == post_id
    ).first()

    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Commentaire non trouvé"
        )

    if comment.author_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vous ne pouvez pas supprimer ce commentaire"
        )

    db.delete(comment)
    db.commit()
    return {"message": "Commentaire supprimé"}


# ============ PUT Comment ============

@router.put("/{post_id}/comments/{comment_id}", response_model=schemas.CommentResponse)
def update_comment(
    post_id: int,
    comment_id: int,
    comment_data: schemas.CommentCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Modifier un de ses commentaires"""
    comment = db.query(models.Comment).filter(
        models.Comment.id == comment_id,
        models.Comment.post_id == post_id
    ).first()

    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Commentaire non trouvé"
        )

    if comment.author_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vous ne pouvez pas modifier ce commentaire"
        )

    comment.content = comment_data.content
    db.commit()
    db.refresh(comment)

    return schemas.CommentResponse.model_validate(comment)
