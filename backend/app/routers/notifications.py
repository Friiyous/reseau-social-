from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from .. import models, schemas
from ..database import get_db
from ..auth import get_current_user
from ..services.notifications import NotificationService, NotificationTypes

router = APIRouter(prefix="/notifications", tags=["Notifications"])

@router.get("/", response_model=List[schemas.NotificationResponse])
def get_notifications(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Récupérer les notifications de l'utilisateur"""
    notifications = NotificationService.get_user_notifications(
        db, current_user.id, skip, limit
    )

    return [{
        "id": notif.id,
        "title": notif.title,
        "message": notif.message,
        "type": notif.type,
        "data": notif.data,
        "is_read": notif.is_read,
        "created_at": notif.created_at
    } for notif in notifications]

@router.get("/unread-count", response_model=Dict[str, int])
def get_unread_notifications_count(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Compter les notifications non lues"""
    count = NotificationService.get_unread_notifications_count(db, current_user.id)
    return {"unread_count": count}

@router.post("/mark-read/{notification_id}", response_model=Dict[str, str])
def mark_notification_as_read(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Marquer une notification comme lue"""
    success = NotificationService.mark_notification_as_read(
        db, notification_id, current_user.id
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification non trouvée"
        )

    return {"message": "Notification marquée comme lue"}

@router.post("/mark-all-read", response_model=Dict[str, str])
def mark_all_notifications_as_read(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Marquer toutes les notifications comme lues"""
    count = NotificationService.mark_all_notifications_as_read(db, current_user.id)
    return {"message": f"{count} notifications marquées comme lues"}

@router.delete("/{notification_id}", response_model=Dict[str, str])
def delete_notification(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Supprimer une notification"""
    success = NotificationService.delete_notification(
        db, notification_id, current_user.id
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification non trouvée"
        )

    return {"message": "Notification supprimée avec succès"}

# ============ ADMIN NOTIFICATIONS ============

@router.post("/admin/send/", response_model=Dict[str, str])
def send_admin_notification(
    notification_data: schemas.NotificationCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Envoyer une notification à un utilisateur spécifique (admin seulement)"""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Accès réservé aux administrateurs"
        )

    notification = NotificationService.create_notification(
        db,
        notification_data.user_id,
        notification_data.title,
        notification_data.message,
        notification_data.type,
        notification_data.data
    )

    # Envoyer également une notification push si possible
    NotificationService.send_push_notification(
        notification_data.user_id,
        notification_data.title,
        notification_data.message,
        notification_data.data
    )

    return {"message": "Notification envoyée avec succès"}

@router.post("/admin/send-bulk/", response_model=Dict[str, str])
def send_bulk_notifications(
    notification_data: schemas.BulkNotificationCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Envoyer des notifications à plusieurs utilisateurs (admin seulement)"""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Accès réservé aux administrateurs"
        )

    notifications = NotificationService.create_bulk_notifications(
        db,
        notification_data.user_ids,
        notification_data.title,
        notification_data.message,
        notification_data.type,
        notification_data.data
    )

    # Envoyer également des notifications push
    NotificationService.send_bulk_push_notifications(
        notification_data.user_ids,
        notification_data.title,
        notification_data.message,
        notification_data.data
    )

    return {"message": f"{len(notifications)} notifications envoyées avec succès"}

@router.post("/admin/send-all/", response_model=Dict[str, str])
def send_notification_to_all_users(
    notification_data: schemas.NotificationCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Envoyer une notification à tous les utilisateurs (admin seulement)"""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Accès réservé aux administrateurs"
        )

    notifications = NotificationService.create_notification_for_all_users(
        db,
        notification_data.title,
        notification_data.message,
        notification_data.type,
        notification_data.data
    )

    # Envoyer également des notifications push à tous les utilisateurs
    # TODO: En production, récupérer tous les tokens de device et envoyer via Firebase
    logger.info(f"Broadcast notification to all users: {notification_data.title}")

    return {"message": f"{len(notifications)} notifications envoyées à tous les utilisateurs"}

# ============ SYSTEM NOTIFICATIONS ============

@router.post("/system/test/", response_model=Dict[str, str])
def send_test_notification(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Envoyer une notification de test à l'utilisateur actuel"""
    notification = NotificationService.create_notification(
        db,
        current_user.id,
        "Notification de test",
        "Ceci est une notification de test pour vérifier le système de notifications.",
        NotificationTypes.INFO,
        {"test": True}
    )

    return {"message": "Notification de test envoyée avec succès"}