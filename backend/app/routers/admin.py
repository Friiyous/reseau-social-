from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from .. import models, schemas
from ..database import get_db
from ..auth import get_current_user

router = APIRouter(prefix="/admin", tags=["Administration"])


def require_admin(current_user: models.User = Depends(get_current_user)):
    """Vérifier que l'utilisateur est administrateur"""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Accès réservé aux administrateurs"
        )
    return current_user


# ============ HEALTH ARTICLES ADMIN ============

@router.get("/health-articles/", response_model=List[schemas.HealthArticleResponse])
def get_all_articles_admin(
    category: str = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_admin)
):
    """Liste complète des articles pour admin (avec stats)"""
    query = db.query(models.HealthArticle)

    if category:
        query = query.filter(models.HealthArticle.category == category)

    articles = query.order_by(
        models.HealthArticle.created_at.desc()
    ).offset(skip).limit(limit).all()

    result = []
    for article in articles:
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
            "bookmarks_count": len(article.bookmarks),
            "created_at": article.created_at
        })

    return result


@router.post("/health-articles/", response_model=schemas.HealthArticleResponse)
def create_article_admin(
    article_data: schemas.HealthArticleCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_admin)
):
    """Créer un article en tant qu'admin"""
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
        "bookmarks_count": 0,
        "created_at": article.created_at
    }


@router.put("/health-articles/{article_id}", response_model=schemas.HealthArticleResponse)
def update_article_admin(
    article_id: int,
    article_data: schemas.HealthArticleCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_admin)
):
    """Modifier un article (admin seulement)"""
    article = db.query(models.HealthArticle).filter(models.HealthArticle.id == article_id).first()
    if not article:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Article non trouvé"
        )

    article.title = article_data.title
    article.summary = article_data.summary
    article.content = article_data.content
    article.category = article_data.category.value if hasattr(article_data.category, 'value') else article_data.category
    article.read_time = article_data.read_time

    db.commit()
    db.refresh(article)

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
        "bookmarks_count": len(article.bookmarks),
        "created_at": article.created_at
    }


@router.delete("/health-articles/{article_id}")
def delete_article_admin(
    article_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_admin)
):
    """Supprimer un article (admin seulement)"""
    article = db.query(models.HealthArticle).filter(models.HealthArticle.id == article_id).first()
    if not article:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Article non trouvé"
        )

    db.delete(article)
    db.commit()
    return {"message": "Article supprimé avec succès"}


# ============ EMERGENCY CONTACTS ADMIN ============

@router.get("/emergency-contacts/", response_model=List[dict])
def get_emergency_contacts_admin(
    district: str = None,
    contact_type: str = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_admin)
):
    """Liste des contacts d'urgence pour admin"""
    query = db.query(models.EmergencyContact)

    if district:
        query = query.filter(models.EmergencyContact.district == district)
    if contact_type:
        query = query.filter(models.EmergencyContact.type == contact_type)

    contacts = query.order_by(models.EmergencyContact.district, models.EmergencyContact.type).all()

    return [{
        "id": contact.id,
        "name": contact.name,
        "phone": contact.phone,
        "type": contact.type,
        "district": contact.district,
        "address": contact.address,
        "available24h": contact.available24h,
        "description": contact.description,
        "created_at": contact.created_at
    } for contact in contacts]


@router.post("/emergency-contacts/", response_model=dict)
def create_emergency_contact_admin(
    contact_data: dict,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_admin)
):
    """Créer un contact d'urgence (admin seulement)"""
    contact = models.EmergencyContact(
        name=contact_data["name"],
        phone=contact_data["phone"],
        type=contact_data["type"],
        district=contact_data["district"],
        address=contact_data.get("address"),
        available24h=contact_data.get("available24h", True),
        description=contact_data.get("description")
    )
    db.add(contact)
    db.commit()
    db.refresh(contact)

    return {
        "id": contact.id,
        "name": contact.name,
        "phone": contact.phone,
        "type": contact.type,
        "district": contact.district,
        "address": contact.address,
        "available24h": contact.available24h,
        "description": contact.description,
        "created_at": contact.created_at
    }


@router.put("/emergency-contacts/{contact_id}", response_model=dict)
def update_emergency_contact_admin(
    contact_id: int,
    contact_data: dict,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_admin)
):
    """Modifier un contact d'urgence"""
    contact = db.query(models.EmergencyContact).filter(models.EmergencyContact.id == contact_id).first()
    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact non trouvé"
        )

    contact.name = contact_data["name"]
    contact.phone = contact_data["phone"]
    contact.type = contact_data["type"]
    contact.district = contact_data["district"]
    contact.address = contact_data.get("address")
    contact.available24h = contact_data.get("available24h", True)
    contact.description = contact_data.get("description")

    db.commit()
    db.refresh(contact)

    return {
        "id": contact.id,
        "name": contact.name,
        "phone": contact.phone,
        "type": contact.type,
        "district": contact.district,
        "address": contact.address,
        "available24h": contact.available24h,
        "description": contact.description,
        "created_at": contact.created_at
    }


@router.delete("/emergency-contacts/{contact_id}")
def delete_emergency_contact_admin(
    contact_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_admin)
):
    """Supprimer un contact d'urgence"""
    contact = db.query(models.EmergencyContact).filter(models.EmergencyContact.id == contact_id).first()
    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact non trouvé"
        )

    db.delete(contact)
    db.commit()
    return {"message": "Contact d'urgence supprimé avec succès"}


# ============ POLLS ADMIN ============

@router.get("/polls/", response_model=List[dict])
def get_polls_admin(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_admin)
):
    """Liste des sondages pour admin (avec stats détaillées)"""
    polls = db.query(models.Poll).order_by(models.Poll.created_at.desc()).all()

    result = []
    for poll in polls:
        total_votes = sum(len(option.votes) for option in poll.options)
        result.append({
            "id": poll.id,
            "question": poll.question,
            "author_id": poll.author_id,
            "author_name": f"{poll.author.first_name} {poll.author.last_name}" if poll.author else "Inconnu",
            "total_votes": total_votes,
            "options_count": len(poll.options),
            "created_at": poll.created_at,
            "options": [{
                "id": option.id,
                "text": option.text,
                "votes": len(option.votes)
            } for option in poll.options]
        })

    return result


@router.post("/polls/", response_model=dict)
def create_poll_admin(
    poll_data: dict,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_admin)
):
    """Créer un sondage (admin seulement)"""
    poll = models.Poll(
        question=poll_data["question"],
        author_id=current_user.id
    )
    db.add(poll)
    db.commit()
    db.refresh(poll)

    # Créer les options
    for option_text in poll_data["options"]:
        option = models.PollOption(
            poll_id=poll.id,
            text=option_text
        )
        db.add(option)

    db.commit()

    return {
        "id": poll.id,
        "question": poll.question,
        "author_id": poll.author_id,
        "author_name": f"{current_user.first_name} {current_user.last_name}",
        "total_votes": 0,
        "options_count": len(poll_data["options"]),
        "created_at": poll.created_at,
        "options": [{"id": opt.id, "text": opt.text, "votes": 0} for opt in poll.options]
    }


@router.delete("/polls/{poll_id}")
def delete_poll_admin(
    poll_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_admin)
):
    """Supprimer un sondage (admin seulement)"""
    poll = db.query(models.Poll).filter(models.Poll.id == poll_id).first()
    if not poll:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sondage non trouvé"
        )

    db.delete(poll)
    db.commit()
    return {"message": "Sondage supprimé avec succès"}


# ============ USER MANAGEMENT ============

@router.get("/users/", response_model=List[dict])
def get_users_admin(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_admin)
):
    """Liste des utilisateurs pour admin"""
    users = db.query(models.User).order_by(models.User.created_at.desc()).offset(skip).limit(limit).all()

    return [{
        "id": user.id,
        "unique_id": user.unique_id,
        "email": user.email,
        "username": user.username,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "district": user.district,
        "health_center": user.health_center,
        "role": user.role,
        "is_admin": user.is_admin,
        "is_active": user.is_active,
        "posts_count": len(user.posts),
        "followers_count": len(user.followers),
        "created_at": user.created_at
    } for user in users]


@router.put("/users/{user_id}/admin")
def toggle_admin_status(
    user_id: int,
    is_admin: bool,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_admin)
):
    """Changer le statut admin d'un utilisateur"""
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Utilisateur non trouvé"
        )

    user.is_admin = is_admin
    db.commit()

    return {"message": f"Statut admin {'activé' if is_admin else 'désactivé'} pour {user.first_name} {user.last_name}"}


@router.put("/users/{user_id}/status")
def toggle_user_status(
    user_id: int,
    is_active: bool,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_admin)
):
    """Activer/désactiver un compte utilisateur"""
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Utilisateur non trouvé"
        )

    user.is_active = is_active
    db.commit()

    return {"message": f"Compte {'activé' if is_active else 'désactivé'} pour {user.first_name} {user.last_name}"}


# ============ STATISTICS DASHBOARD ============

@router.get("/stats/")
def get_admin_stats(
    days: int = 7,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_admin)
):
    """Statistiques globales pour le dashboard admin"""
    from datetime import datetime, timedelta
    from sqlalchemy import func, cast, Date

    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)

    # Statistiques globales
    total_users = db.query(models.User).count()
    active_users = db.query(models.User).filter(models.User.is_active == True).count()
    total_posts = db.query(models.Post).count()
    total_articles = db.query(models.HealthArticle).count()
    total_events = db.query(models.Event).count()
    total_polls = db.query(models.Poll).count()
    total_emergency_contacts = db.query(models.EmergencyContact).count()
    total_conversations = db.query(models.Conversation).count()

    # Activité récente par jour
    activity_query = (
        db.query(
            cast(func.date(models.Post.created_at), Date).label('date'),
            func.count(models.Post.id).label('count')
        )
        .filter(models.Post.created_at >= start_date)
        .group_by(cast(func.date(models.Post.created_at), Date))
        .order_by(cast(func.date(models.Post.created_at), Date))
    )

    activity = []
    current_date = start_date
    while current_date <= end_date:
        date_str = current_date.strftime('%Y-%m-%d')
        count = 0

        # Trouver le count pour cette date dans les résultats
        for row in activity_query:
            if row.date.strftime('%Y-%m-%d') == date_str:
                count = row.count
                break

        activity.append({
            "date": date_str,
            "count": count
        })

        current_date += timedelta(days=1)

    return {
        "stats": {
            "total_users": total_users,
            "active_users": active_users,
            "total_posts": total_posts,
            "total_articles": total_articles,
            "total_events": total_events,
            "total_polls": total_polls,
            "total_emergency_contacts": total_emergency_contacts,
            "total_conversations": total_conversations,
        },
        "activity": activity
    }

# ============ EVENTS ADMIN ============

@router.get("/events/", response_model=List[dict])
def get_all_events_admin(
    category: str = None,
    district: str = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_admin)
):
    """Liste complète des événements pour admin (avec stats)"""
    query = db.query(models.Event)

    if category:
        query = query.filter(models.Event.category == category)
    if district:
        query = query.filter(models.Event.district == district)

    events = query.order_by(
        models.Event.date.asc()
    ).offset(skip).limit(limit).all()

    result = []
    for event in events:
        # Compter les inscriptions
        registered_count = db.query(models.EventRegistration).filter(
            models.EventRegistration.event_id == event.id
        ).count()

        result.append({
            "id": event.id,
            "title": event.title,
            "description": event.description,
            "category": event.category,
            "date": event.date,
            "time": event.time,
            "location": event.location,
            "district": event.district,
            "organizer": event.organizer,
            "max_participants": event.max_participants,
            "image_url": event.image_url,
            "author_id": event.author_id,
            "author_name": f"{event.author.first_name} {event.author.last_name}" if event.author else "Inconnu",
            "registered_count": registered_count,
            "created_at": event.created_at
        })

    return result


@router.post("/events/", response_model=dict)
def create_event_admin(
    event_data: schemas.EventCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_admin)
):
    """Créer un événement en tant qu'admin"""
    event = models.Event(
        title=event_data.title,
        description=event_data.description,
        category=event_data.category.value if hasattr(event_data.category, 'value') else event_data.category,
        date=event_data.date,
        time=event_data.time,
        location=event_data.location,
        district=event_data.district,
        organizer=event_data.organizer,
        max_participants=event_data.max_participants,
        image_url=event_data.image_url,
        author_id=current_user.id
    )
    db.add(event)
    db.commit()
    db.refresh(event)

    return {
        "id": event.id,
        "title": event.title,
        "description": event.description,
        "category": event.category,
        "date": event.date,
        "time": event.time,
        "location": event.location,
        "district": event.district,
        "organizer": event.organizer,
        "max_participants": event.max_participants,
        "image_url": event.image_url,
        "author_id": event.author_id,
        "author_name": f"{current_user.first_name} {current_user.last_name}",
        "registered_count": 0,
        "created_at": event.created_at
    }


@router.put("/events/{event_id}", response_model=dict)
def update_event_admin(
    event_id: int,
    event_data: schemas.EventUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_admin)
):
    """Modifier un événement (admin seulement)"""
    event = db.query(models.Event).filter(models.Event.id == event_id).first()
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Événement non trouvé"
        )

    if event_data.title is not None:
        event.title = event_data.title
    if event_data.description is not None:
        event.description = event_data.description
    if event_data.category is not None:
        event.category = event_data.category.value if hasattr(event_data.category, 'value') else event_data.category
    if event_data.date is not None:
        event.date = event_data.date
    if event_data.time is not None:
        event.time = event_data.time
    if event_data.location is not None:
        event.location = event_data.location
    if event_data.district is not None:
        event.district = event_data.district
    if event_data.organizer is not None:
        event.organizer = event_data.organizer
    if event_data.max_participants is not None:
        event.max_participants = event_data.max_participants
    if event_data.image_url is not None:
        event.image_url = event_data.image_url

    db.commit()
    db.refresh(event)

    # Compter les inscriptions
    registered_count = db.query(models.EventRegistration).filter(
        models.EventRegistration.event_id == event.id
    ).count()

    return {
        "id": event.id,
        "title": event.title,
        "description": event.description,
        "category": event.category,
        "date": event.date,
        "time": event.time,
        "location": event.location,
        "district": event.district,
        "organizer": event.organizer,
        "max_participants": event.max_participants,
        "image_url": event.image_url,
        "author_id": event.author_id,
        "author_name": f"{event.author.first_name} {event.author.last_name}" if event.author else "Inconnu",
        "registered_count": registered_count,
        "created_at": event.created_at
    }


@router.delete("/events/{event_id}")
def delete_event_admin(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_admin)
):
    """Supprimer un événement (admin seulement)"""
    event = db.query(models.Event).filter(models.Event.id == event_id).first()
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Événement non trouvé"
        )

    db.delete(event)
    db.commit()
    return {"message": "Événement supprimé avec succès"}