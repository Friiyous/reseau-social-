from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from .. import models, schemas
from ..database import get_db
from ..auth import get_current_user

router = APIRouter(prefix="/health-articles", tags=["Articles de santé"])


@router.get("/", response_model=List[schemas.HealthArticleResponse])
def get_articles(
    category: str = None,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Liste de tous les articles de santé"""
    query = db.query(models.HealthArticle)

    if category:
        query = query.filter(models.HealthArticle.category == category)

    articles = query.order_by(
        models.HealthArticle.created_at.desc()
    ).offset(skip).limit(limit).all()

    result = []
    for article in articles:
        # Vérifier si l'utilisateur a liké
        has_liked = db.query(models.HealthArticleLike).filter(
            models.HealthArticleLike.article_id == article.id,
            models.HealthArticleLike.user_id == current_user.id
        ).first() is not None

        # Vérifier si l'utilisateur a sauvegardé
        has_bookmarked = db.query(models.HealthArticleBookmark).filter(
            models.HealthArticleBookmark.article_id == article.id,
            models.HealthArticleBookmark.user_id == current_user.id
        ).first() is not None

        result.append({
            "id": article.id,
            "title": article.title,
            "summary": article.summary,
            "content": article.content,
            "category": article.category,
            "author_id": article.author_id,
            "author_name": f"{article.author.first_name} {article.author.last_name}" if article.author else "Inconnu",
            "read_time": article.read_time,
            "likes_count": len(article.likes),
            "is_bookmarked": has_bookmarked,
            "created_at": article.created_at
        })

    return result


@router.get("/{article_id}", response_model=schemas.HealthArticleResponse)
def get_article(
    article_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Détails d'un article"""
    article = db.query(models.HealthArticle).filter(
        models.HealthArticle.id == article_id
    ).first()

    if not article:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Article non trouvé"
        )

    # Vérifier si l'utilisateur a liké
    has_liked = db.query(models.HealthArticleLike).filter(
        models.HealthArticleLike.article_id == article.id,
        models.HealthArticleLike.user_id == current_user.id
    ).first() is not None

    # Vérifier si l'utilisateur a sauvegardé
    has_bookmarked = db.query(models.HealthArticleBookmark).filter(
        models.HealthArticleBookmark.article_id == article.id,
        models.HealthArticleBookmark.user_id == current_user.id
    ).first() is not None

    return {
        "id": article.id,
        "title": article.title,
        "summary": article.summary,
        "content": article.content,
        "category": article.category,
        "author_id": article.author_id,
        "author_name": f"{article.author.first_name} {article.author.last_name}" if article.author else "Inconnu",
        "read_time": article.read_time,
        "likes_count": len(article.likes),
        "is_bookmarked": has_bookmarked,
        "created_at": article.created_at
    }


@router.post("/", response_model=schemas.HealthArticleResponse)
def create_article(
    article_data: schemas.HealthArticleCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Créer un nouvel article (admin ou personnel autorisé)"""
    article = models.HealthArticle(
        title=article_data.title,
        summary=article_data.summary,
        content=article_data.content,
        category=article_data.category.value if hasattr(article_data.category, 'value') else article_data.category,
        author_id=current_user.id,
        read_time=article_data.read_time
    )
    db.add(article)
    db.commit()
    db.refresh(article)

    return {
        "id": article.id,
        "title": article.title,
        "summary": article.summary,
        "content": article.content,
        "category": article.category,
        "author_id": article.author_id,
        "author_name": f"{current_user.first_name} {current_user.last_name}",
        "read_time": article.read_time,
        "likes_count": 0,
        "is_bookmarked": False,
        "created_at": article.created_at
    }


@router.post("/{article_id}/like")
def like_article(
    article_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Liker un article"""
    article = db.query(models.HealthArticle).filter(
        models.HealthArticle.id == article_id
    ).first()

    if not article:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Article non trouvé"
        )

    # Vérifier si déjà liké
    existing_like = db.query(models.HealthArticleLike).filter(
        models.HealthArticleLike.article_id == article_id,
        models.HealthArticleLike.user_id == current_user.id
    ).first()

    if existing_like:
        # Unlike
        db.delete(existing_like)
        db.commit()
        return {"message": "Like retiré", "liked": False}
    else:
        # Like
        like = models.HealthArticleLike(
            article_id=article_id,
            user_id=current_user.id
        )
        db.add(like)
        db.commit()
        return {"message": "Article liké", "liked": True}


@router.post("/{article_id}/bookmark")
def bookmark_article(
    article_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Sauvegarder un article"""
    article = db.query(models.HealthArticle).filter(
        models.HealthArticle.id == article_id
    ).first()

    if not article:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Article non trouvé"
        )

    # Vérifier si déjà sauvegardé
    existing_bookmark = db.query(models.HealthArticleBookmark).filter(
        models.HealthArticleBookmark.article_id == article_id,
        models.HealthArticleBookmark.user_id == current_user.id
    ).first()

    if existing_bookmark:
        # Remove bookmark
        db.delete(existing_bookmark)
        db.commit()
        return {"message": "Sauvegarde retirée", "bookmarked": False}
    else:
        # Add bookmark
        bookmark = models.HealthArticleBookmark(
            article_id=article_id,
            user_id=current_user.id
        )
        db.add(bookmark)
        db.commit()
        return {"message": "Article sauvegardé", "bookmarked": True}


@router.get("/bookmarked/", response_model=List[schemas.HealthArticleResponse])
def get_bookmarked_articles(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Récupérer les articles sauvegardés"""
    bookmarks = db.query(models.HealthArticleBookmark).filter(
        models.HealthArticleBookmark.user_id == current_user.id
    ).all()

    result = []
    for bookmark in bookmarks:
        article = bookmark.article
        if article:
            result.append({
                "id": article.id,
                "title": article.title,
                "summary": article.summary,
                "content": article.content,
                "category": article.category,
                "author_id": article.author_id,
                "author_name": f"{article.author.first_name} {article.author.last_name}" if article.author else "Inconnu",
                "read_time": article.read_time,
                "likes_count": len(article.likes),
                "is_bookmarked": True,
                "created_at": article.created_at
            })

    return result
