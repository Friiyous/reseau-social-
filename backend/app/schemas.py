from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional, List
from enum import Enum

# ============ User Schemas ============

class UserBase(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    first_name: str
    last_name: str
    district: str
    health_center: Optional[str] = None
    role: Optional[str] = "agent_sante"
    specialty: Optional[str] = None
    department: Optional[str] = None


class UserCreate(UserBase):
    password: str
    professional_id: Optional[str] = None


class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    bio: Optional[str] = None
    health_center: Optional[str] = None
    role: Optional[str] = None
    avatar_url: Optional[str] = None


class UserResponse(UserBase):
    id: int
    unique_id: str  # Identifiant unique SP-XXXXX
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    professional_id: Optional[str] = None
    device_token: Optional[str] = None  # OneSignal device token
    is_active: bool
    created_at: datetime

    model_config = {
        "from_attributes": True
    }


class QuickRegisterRequest(BaseModel):
    """Inscription rapide sans mot de passe"""
    first_name: str
    last_name: str
    district: str
    specialty: str
    department: str
    health_center: str


class QuickRegisterResponse(BaseModel):
    """Réponse après inscription rapide"""
    unique_id: str  # L'identifiant unique généré
    message: str
    user: UserResponse


class UserWithStats(UserResponse):
    posts_count: int = 0
    followers_count: int = 0
    following_count: int = 0


# ============ Auth Schemas ============

class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


# ============ Post Schemas ============

class PostBase(BaseModel):
    content: str


class PostCreate(PostBase):
    image_url: Optional[str] = None


class PostResponse(PostBase):
    id: int
    image_url: Optional[str] = None
    author_id: int
    author: UserResponse
    created_at: datetime
    likes_count: int = 0
    comments_count: int = 0
    is_liked_by_me: bool = False

    model_config = {
        "from_attributes": True
    }


class PostWithComments(PostResponse):
    comments: List["CommentResponse"] = []


# ============ Comment Schemas ============

class CommentCreate(BaseModel):
    content: str


class CommentResponse(BaseModel):
    id: int
    content: str
    post_id: int
    author_id: int
    author: UserResponse
    created_at: datetime

    model_config = {
        "from_attributes": True
    }


# ============ Like Schemas ============

class LikeResponse(BaseModel):
    id: int
    post_id: int
    user_id: int
    created_at: datetime


# ============ Follow Schemas ============

class FollowResponse(BaseModel):
    id: int
    follower_id: int
    following_id: int
    created_at: datetime
    follower: UserResponse
    following: UserResponse


class FollowRequest(BaseModel):
    user_id: int


# ============ Message Schemas ============

class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str


# ============ Poll Schemas ============

class PollOption(BaseModel):
    id: int
    text: str
    votes: int = 0


class PollCreate(BaseModel):
    question: str
    options: list[str]


class PollResponse(BaseModel):
    id: int
    question: str
    options: list[PollOption]
    total_votes: int
    has_voted: bool
    author_id: int
    author_name: str
    created_at: datetime

    model_config = {
        "from_attributes": True
    }


class PollVote(BaseModel):
    option_id: int


# ============ Health Article Schemas ============

class HealthArticleCategory(str, Enum):
    prevention = "prevention"
    treatment = "treatment"
    nutrition = "nutrition"
    maternal = "maternal"
    hygiene = "hygiene"
    vaccination = "vaccination"


class HealthArticleCreate(BaseModel):
    title: str
    summary: str
    content: str
    category: HealthArticleCategory
    read_time: int


class HealthArticleResponse(BaseModel):
    id: int
    title: str
    summary: str
    content: str
    category: str
    author_id: int
    author_name: str
    read_time: int
    likes_count: int = 0
    is_bookmarked: bool = False
    created_at: datetime

    model_config = {
        "from_attributes": True
    }


# Mise à jour des forward references
PostWithComments.model_rebuild()


# ============ Emergency Contact Schemas ============

class EmergencyContactType(str, Enum):
    emergency = "emergency"
    hospital = "hospital"
    police = "police"
    fire = "fire"
    poison = "poison"
    psychological = "psychological"
    other = "other"


class EmergencyContactCreate(BaseModel):
    name: str
    phone: str
    type: EmergencyContactType
    district: str
    address: Optional[str] = None
    available24h: bool = True
    description: Optional[str] = None


class EmergencyContactUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    type: Optional[EmergencyContactType] = None
    district: Optional[str] = None
    address: Optional[str] = None
    available24h: Optional[bool] = None
    description: Optional[str] = None


class EmergencyContactResponse(BaseModel):
    id: int
    name: str
    phone: str
    type: str
    district: str
    address: Optional[str] = None
    available24h: bool
    description: Optional[str] = None
    created_at: datetime

    model_config = {
        "from_attributes": True
    }


# ============ Health Protocol Schemas ============

class HealthProtocolCreate(BaseModel):
    title: str
    content: str
    category: str
    is_public: bool = False


class HealthProtocolUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    category: Optional[str] = None
    is_public: Optional[bool] = None


class HealthProtocolResponse(BaseModel):
    id: int
    title: str
    content: str
    category: str
    author_id: int
    author_name: str
    is_public: bool
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }


# ============ Event Schemas ============

class EventCategory(str, Enum):
    formation = "formation"
    reunion = "reunion"
    seminaire = "seminaire"
    workshop = "workshop"


class EventCreate(BaseModel):
    title: str
    description: str
    category: EventCategory
    date: str  # YYYY-MM-DD
    time: str  # HH:MM - HH:MM
    location: str
    district: str
    organizer: str
    max_participants: Optional[int] = None
    image_url: Optional[str] = None


class EventUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[EventCategory] = None
    date: Optional[str] = None
    time: Optional[str] = None
    location: Optional[str] = None
    district: Optional[str] = None
    organizer: Optional[str] = None
    max_participants: Optional[int] = None
    image_url: Optional[str] = None


class EventResponse(BaseModel):
    id: int
    title: str
    description: str
    category: str
    date: str
    time: str
    location: str
    district: str
    organizer: str
    max_participants: Optional[int] = None
    image_url: Optional[str] = None
    author_id: int
    author_name: str
    registered_count: int = 0
    is_registered: bool = False
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }


class EventRegistrationResponse(BaseModel):
    id: int
    event_id: int
    user_id: int
    created_at: datetime

    model_config = {
        "from_attributes": True
    }


# ============ Message Schemas ============

class MessageCreate(BaseModel):
    content: str
    receiver_id: int


class MessageResponse(BaseModel):
    id: int
    content: str
    sender_id: int
    receiver_id: int
    is_read: bool
    created_at: datetime
    sender: UserResponse
    receiver: UserResponse

    model_config = {
        "from_attributes": True
    }


class ConversationResponse(BaseModel):
    id: int
    user1_id: int
    user2_id: int
    user1: UserResponse
    user2: UserResponse
    last_message: Optional[MessageResponse] = None
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }


class ConversationWithMessages(ConversationResponse):
    messages: List[MessageResponse] = []

# ============ Notification Schemas ============

class NotificationType(str, Enum):
    info = "info"
    success = "success"
    warning = "warning"
    error = "error"
    message = "message"
    event = "event"
    follow = "follow"
    like = "like"
    comment = "comment"
    system = "system"


class NotificationCreate(BaseModel):
    user_id: int
    title: str
    message: str
    type: NotificationType = NotificationType.info
    data: Dict[str, Any] = {}


class BulkNotificationCreate(BaseModel):
    user_ids: List[int]
    title: str
    message: str
    type: NotificationType = NotificationType.info
    data: Dict[str, Any] = {}


class NotificationResponse(BaseModel):
    id: int
    title: str
    message: str
    type: str
    data: Dict[str, Any] = {}
    is_read: bool
    created_at: datetime

    model_config = {
        "from_attributes": True
    }