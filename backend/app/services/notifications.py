from typing import List, Dict, Any
from ..models import User, Notification
from ..database import get_db
from sqlalchemy.orm import Session
import logging
import firebase_admin
from firebase_admin import credentials, messaging
import json
import os

logger = logging.getLogger(__name__)

# Initialize Firebase Admin SDK
def initialize_firebase():
    try:
        # Check if Firebase is already initialized
        if not firebase_admin._apps:
            # Load Firebase credentials from environment variable or file
            firebase_cred_path = os.getenv('FIREBASE_CREDENTIALS_PATH', 'firebase-credentials.json')

            if os.path.exists(firebase_cred_path):
                cred = credentials.Certificate(firebase_cred_path)
                firebase_admin.initialize_app(cred)
                logger.info("Firebase Admin SDK initialized successfully")
            else:
                logger.warning(f"Firebase credentials file not found at {firebase_cred_path}")
                logger.warning("Firebase notifications will not be available")
    except Exception as e:
        logger.error(f"Error initializing Firebase: {str(e)}")

# Initialize Firebase when module is imported
initialize_firebase()

class NotificationService:
    @staticmethod
    def create_notification(
        db: Session,
        user_id: int,
        title: str,
        message: str,
        type: str = "info",
        data: Dict[str, Any] = None
    ) -> Notification:
        """Créer une notification pour un utilisateur"""
        notification = Notification(
            user_id=user_id,
            title=title,
            message=message,
            type=type,
            data=data or {},
            is_read=False
        )
        db.add(notification)
        db.commit()
        db.refresh(notification)
        return notification

    @staticmethod
    def create_bulk_notifications(
        db: Session,
        user_ids: List[int],
        title: str,
        message: str,
        type: str = "info",
        data: Dict[str, Any] = None
    ) -> List[Notification]:
        """Créer des notifications pour plusieurs utilisateurs"""
        notifications = []
        for user_id in user_ids:
            notification = NotificationService.create_notification(
                db, user_id, title, message, type, data
            )
            notifications.append(notification)
        return notifications

    @staticmethod
    def create_notification_for_all_users(
        db: Session,
        title: str,
        message: str,
        type: str = "info",
        data: Dict[str, Any] = None
    ) -> List[Notification]:
        """Créer une notification pour tous les utilisateurs actifs"""
        users = db.query(User).filter(User.is_active == True).all()
        user_ids = [user.id for user in users]
        return NotificationService.create_bulk_notifications(
            db, user_ids, title, message, type, data
        )

    @staticmethod
    def get_user_notifications(
        db: Session,
        user_id: int,
        skip: int = 0,
        limit: int = 50
    ) -> List[Notification]:
        """Récupérer les notifications d'un utilisateur"""
        return db.query(Notification).filter(
            Notification.user_id == user_id
        ).order_by(
            Notification.created_at.desc()
        ).offset(skip).limit(limit).all()

    @staticmethod
    def get_unread_notifications_count(
        db: Session,
        user_id: int
    ) -> int:
        """Compter les notifications non lues"""
        return db.query(Notification).filter(
            Notification.user_id == user_id,
            Notification.is_read == False
        ).count()

    @staticmethod
    def mark_notification_as_read(
        db: Session,
        notification_id: int,
        user_id: int
    ) -> bool:
        """Marquer une notification comme lue"""
        notification = db.query(Notification).filter(
            Notification.id == notification_id,
            Notification.user_id == user_id
        ).first()

        if notification:
            notification.is_read = True
            db.commit()
            return True
        return False

    @staticmethod
    def mark_all_notifications_as_read(
        db: Session,
        user_id: int
    ) -> int:
        """Marquer toutes les notifications comme lues"""
        result = db.query(Notification).filter(
            Notification.user_id == user_id,
            Notification.is_read == False
        ).update({"is_read": True}, synchronize_session=False)

        db.commit()
        return result

    @staticmethod
    def delete_notification(
        db: Session,
        notification_id: int,
        user_id: int
    ) -> bool:
        """Supprimer une notification"""
        notification = db.query(Notification).filter(
            Notification.id == notification_id,
            Notification.user_id == user_id
        ).first()

        if notification:
            db.delete(notification)
            db.commit()
            return True
        return False

    @staticmethod
    def send_push_notification(
        user_id: int,
        title: str,
        body: str,
        data: Dict[str, Any] = None
    ) -> bool:
        """
        Envoyer une notification push via Firebase Cloud Messaging
        """
        from ..database import get_db
        from sqlalchemy.orm import Session

        try:
            db: Session = next(get_db())

            # Get user's device token from database
            user = db.query(models.User).filter(models.User.id == user_id).first()
            if not user or not user.device_token:
                logger.warning(f"User {user_id} has no device token registered")
                return False

            # Check if Firebase is initialized
            if not firebase_admin._apps:
                logger.warning("Firebase not initialized, cannot send push notifications")
                return False

            # Prepare the message
            message = messaging.Message(
                notification=messaging.Notification(
                    title=title,
                    body=body,
                ),
                data=data or {},
                token=user.device_token,
            )

            # Send the message
            response = messaging.send(message)
            logger.info(f"Firebase push notification sent to user {user_id}: {response}")

            return True

        except Exception as e:
            logger.error(f"Error sending Firebase push notification: {str(e)}")
            return False

    @staticmethod
    def send_bulk_push_notifications(
        user_ids: List[int],
        title: str,
        body: str,
        data: Dict[str, Any] = None
    ) -> bool:
        """Envoyer des notifications push à plusieurs utilisateurs"""
        from ..database import get_db
        from sqlalchemy.orm import Session

        try:
            db: Session = next(get_db())

            # Check if Firebase is initialized
            if not firebase_admin._apps:
                logger.warning("Firebase not initialized, cannot send bulk push notifications")
                return False

            # Get device tokens for all users
            users = db.query(models.User).filter(
                models.User.id.in_(user_ids),
                models.User.device_token.isnot(None)
            ).all()

            if not users:
                logger.warning("No users with device tokens found for bulk notification")
                return False

            # Prepare messages for each user
            messages = []
            for user in users:
                message = messaging.Message(
                    notification=messaging.Notification(
                        title=title,
                        body=body,
                    ),
                    data=data or {},
                    token=user.device_token,
                )
                messages.append(message)

            # Send all messages as a batch
            response = messaging.send_all(messages)
            logger.info(f"Firebase bulk push notification sent to {len(users)} users: {response}")

            return True

        except Exception as e:
            logger.error(f"Error sending bulk Firebase push notifications: {str(e)}")
            return False

# Types de notifications courants
class NotificationTypes:
    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"
    MESSAGE = "message"
    EVENT = "event"
    FOLLOW = "follow"
    LIKE = "like"
    COMMENT = "comment"
    SYSTEM = "system"