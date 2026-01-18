from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from .. import models, schemas
from ..database import get_db
from ..auth import get_current_user

router = APIRouter(prefix="/events", tags=["Events"])


# ============ EVENTS ============

@router.get("/", response_model=List[schemas.EventResponse])
def get_events(
    category: str = None,
    district: str = None,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Liste des événements"""
    query = db.query(models.Event)

    if category:
        query = query.filter(models.Event.category == category)
    if district:
        query = query.filter(models.Event.district == district)

    events = query.order_by(models.Event.date.asc()).offset(skip).limit(limit).all()

    result = []
    for event in events:
        # Vérifier si l'utilisateur est inscrit
        is_registered = db.query(models.EventRegistration).filter(
            models.EventRegistration.event_id == event.id,
            models.EventRegistration.user_id == current_user.id
        ).first() is not None

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
            "is_registered": is_registered,
            "created_at": event.created_at,
            "updated_at": event.updated_at
        })

    return result


@router.get("/{event_id}", response_model=schemas.EventResponse)
def get_event(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Détails d'un événement"""
    event = db.query(models.Event).filter(models.Event.id == event_id).first()
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Événement non trouvé"
        )

    # Vérifier si l'utilisateur est inscrit
    is_registered = db.query(models.EventRegistration).filter(
        models.EventRegistration.event_id == event.id,
        models.EventRegistration.user_id == current_user.id
    ).first() is not None

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
        "is_registered": is_registered,
        "created_at": event.created_at,
        "updated_at": event.updated_at
    }


@router.post("/", response_model=schemas.EventResponse)
def create_event(
    event_data: schemas.EventCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Créer un événement"""
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
        "is_registered": False,
        "created_at": event.created_at,
        "updated_at": event.updated_at
    }


@router.put("/{event_id}", response_model=schemas.EventResponse)
def update_event(
    event_id: int,
    event_data: schemas.EventUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Modifier un événement"""
    event = db.query(models.Event).filter(models.Event.id == event_id).first()
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Événement non trouvé"
        )

    # Vérifier que l'utilisateur est l'auteur ou admin
    if event.author_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vous n'avez pas la permission de modifier cet événement"
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

    # Vérifier si l'utilisateur est inscrit
    is_registered = db.query(models.EventRegistration).filter(
        models.EventRegistration.event_id == event.id,
        models.EventRegistration.user_id == current_user.id
    ).first() is not None

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
        "is_registered": is_registered,
        "created_at": event.created_at,
        "updated_at": event.updated_at
    }


@router.delete("/{event_id}")
def delete_event(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Supprimer un événement"""
    event = db.query(models.Event).filter(models.Event.id == event_id).first()
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Événement non trouvé"
        )

    # Vérifier que l'utilisateur est l'auteur ou admin
    if event.author_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vous n'avez pas la permission de supprimer cet événement"
        )

    db.delete(event)
    db.commit()
    return {"message": "Événement supprimé avec succès"}


# ============ INSCRIPTIONS ============

@router.post("/{event_id}/register", response_model=schemas.EventRegistrationResponse)
def register_to_event(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """S'inscrire à un événement"""
    event = db.query(models.Event).filter(models.Event.id == event_id).first()
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Événement non trouvé"
        )

    # Vérifier si déjà inscrit
    existing_registration = db.query(models.EventRegistration).filter(
        models.EventRegistration.event_id == event_id,
        models.EventRegistration.user_id == current_user.id
    ).first()
    if existing_registration:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Vous êtes déjà inscrit à cet événement"
        )

    # Vérifier la capacité maximale
    if event.max_participants:
        registered_count = db.query(models.EventRegistration).filter(
            models.EventRegistration.event_id == event_id
        ).count()
        if registered_count >= event.max_participants:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="L'événement est complet"
            )

    # Créer l'inscription
    registration = models.EventRegistration(
        event_id=event_id,
        user_id=current_user.id
    )
    db.add(registration)
    db.commit()
    db.refresh(registration)

    return registration


@router.delete("/{event_id}/unregister")
def unregister_from_event(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Annuler son inscription à un événement"""
    registration = db.query(models.EventRegistration).filter(
        models.EventRegistration.event_id == event_id,
        models.EventRegistration.user_id == current_user.id
    ).first()
    if not registration:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Inscription non trouvée"
        )

    db.delete(registration)
    db.commit()
    return {"message": "Inscription annulée avec succès"}


@router.get("/{event_id}/registrations", response_model=List[schemas.EventRegistrationResponse])
def get_event_registrations(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Liste des inscriptions à un événement (admin ou auteur uniquement)"""
    event = db.query(models.Event).filter(models.Event.id == event_id).first()
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Événement non trouvé"
        )

    # Vérifier que l'utilisateur est l'auteur ou admin
    if event.author_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vous n'avez pas la permission de voir les inscriptions"
        )

    registrations = db.query(models.EventRegistration).filter(
        models.EventRegistration.event_id == event_id
    ).all()

    return registrations


# ============ MESSAGES ============

@router.get("/conversations", response_model=List[schemas.ConversationResponse])
def get_conversations(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Liste des conversations de l'utilisateur"""
    conversations = db.query(models.Conversation).filter(
        (models.Conversation.user1_id == current_user.id) |
        (models.Conversation.user2_id == current_user.id)
    ).order_by(models.Conversation.updated_at.desc()).all()

    result = []
    for conv in conversations:
        # Déterminer l'autre utilisateur
        other_user = conv.user1 if conv.user2_id == current_user.id else conv.user2

        # Obtenir le dernier message
        last_message = conv.last_message

        result.append({
            "id": conv.id,
            "user1_id": conv.user1_id,
            "user2_id": conv.user2_id,
            "user1": conv.user1,
            "user2": conv.user2,
            "last_message": last_message,
            "updated_at": conv.updated_at
        })

    return result


@router.get("/conversations/{conversation_id}", response_model=schemas.ConversationWithMessages)
def get_conversation(
    conversation_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Détails d'une conversation avec tous les messages"""
    conversation = db.query(models.Conversation).filter(models.Conversation.id == conversation_id).first()
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation non trouvée"
        )

    # Vérifier que l'utilisateur fait partie de la conversation
    if conversation.user1_id != current_user.id and conversation.user2_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vous n'avez pas accès à cette conversation"
        )

    # Obtenir les messages
    messages = db.query(models.Message).filter(
        (models.Message.sender_id == current_user.id) |
        (models.Message.receiver_id == current_user.id)
    ).order_by(models.Message.created_at.asc()).all()

    # Marquer les messages comme lus
    for message in messages:
        if message.receiver_id == current_user.id and not message.is_read:
            message.is_read = True
    db.commit()

    return {
        "id": conversation.id,
        "user1_id": conversation.user1_id,
        "user2_id": conversation.user2_id,
        "user1": conversation.user1,
        "user2": conversation.user2,
        "last_message": conversation.last_message,
        "updated_at": conversation.updated_at,
        "messages": messages
    }


@router.post("/messages", response_model=schemas.MessageResponse)
def send_message(
    message_data: schemas.MessageCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Envoyer un message"""
    # Vérifier que le destinataire existe
    receiver = db.query(models.User).filter(models.User.id == message_data.receiver_id).first()
    if not receiver:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Destinataire non trouvé"
        )

    # Créer ou récupérer la conversation
    conversation = db.query(models.Conversation).filter(
        ((models.Conversation.user1_id == current_user.id) & (models.Conversation.user2_id == message_data.receiver_id)) |
        ((models.Conversation.user1_id == message_data.receiver_id) & (models.Conversation.user2_id == current_user.id))
    ).first()

    if not conversation:
        conversation = models.Conversation(
            user1_id=min(current_user.id, message_data.receiver_id),
            user2_id=max(current_user.id, message_data.receiver_id)
        )
        db.add(conversation)
        db.commit()
        db.refresh(conversation)

    # Créer le message
    message = models.Message(
        content=message_data.content,
        sender_id=current_user.id,
        receiver_id=message_data.receiver_id
    )
    db.add(message)
    db.commit()
    db.refresh(message)

    # Mettre à jour le dernier message de la conversation
    conversation.last_message_id = message.id
    conversation.updated_at = datetime.utcnow()
    db.commit()

    return {
        "id": message.id,
        "content": message.content,
        "sender_id": message.sender_id,
        "receiver_id": message.receiver_id,
        "is_read": message.is_read,
        "created_at": message.created_at,
        "sender": current_user,
        "receiver": receiver
    }