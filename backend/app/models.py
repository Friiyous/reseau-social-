from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

# Districts de la région du Poro
DISTRICTS = ["Dikodougou", "Ferkessédougou", "Korhogo", "Sinématiali"]


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    unique_id = Column(String(20), unique=True, index=True, nullable=False)  # SP-XXXXX
    # Removed unique=True from nullable columns to avoid NULL constraint issues
    email = Column(String(255), index=True, nullable=True)
    username = Column(String(100), index=True, nullable=True)
    password_hash = Column(String(255), nullable=True)  # Nullable pour inscription rapide

    # Informations spécifiques aux agents de santé
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    district = Column(String(50), nullable=False)  # Dikodougou, Ferkessédougou, Korhogo, Sinématiali
    health_center = Column(String(200), nullable=True)  # Centre de santé
    professional_id = Column(String(100), nullable=True)  # Matricule professionnel (sans unique pour l'instant)

    role = Column(String(100), default="agent_sante")  # Infirmier, médecin, sage-femme, etc.
    specialty = Column(String(100), nullable=True)  # Spécialité médicale
    department = Column(String(100), nullable=True)  # Département

    # Permissions administratives
    is_admin = Column(Boolean, default=False)  # Accès au panel d'administration

    bio = Column(Text, nullable=True)
    avatar_url = Column(String(500), nullable=True)
    device_token = Column(String(255), nullable=True)  # OneSignal device token

    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relations
    posts = relationship("Post", back_populates="author", cascade="all, delete-orphan")
    comments = relationship("Comment", back_populates="author", cascade="all, delete-orphan")
    likes = relationship("Like", back_populates="user", cascade="all, delete-orphan")
    following = relationship("Follow", foreign_keys="Follow.follower_id", back_populates="follower", cascade="all, delete-orphan")
    followers = relationship("Follow", foreign_keys="Follow.following_id", back_populates="following", cascade="all, delete-orphan")


class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=False)
    image_url = Column(String(500), nullable=True)

    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relations
    author = relationship("User", back_populates="posts")
    comments = relationship("Comment", back_populates="post", cascade="all, delete-orphan")
    likes = relationship("Like", back_populates="post", cascade="all, delete-orphan")


class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=False)

    post_id = Column(Integer, ForeignKey("posts.id"), nullable=False)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relations
    post = relationship("Post", back_populates="comments")
    author = relationship("User", back_populates="comments")


class Like(Base):
    __tablename__ = "likes"

    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey("posts.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relations
    post = relationship("Post", back_populates="likes")
    user = relationship("User", back_populates="likes")

    # Contrainte unique pour éviter les doubles likes
    __table_args__ = ({"sqlite_autoincrement": True},)


class Follow(Base):
    __tablename__ = "follows"

    id = Column(Integer, primary_key=True, index=True)
    follower_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    following_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relations
    follower = relationship("User", foreign_keys=[follower_id], back_populates="following")
    following = relationship("User", foreign_keys=[following_id], back_populates="followers")

    # Contrainte unique pour éviter les doubles follows
    __table_args__ = (
        {"sqlite_autoincrement": True},
    )


class Poll(Base):
    __tablename__ = "polls"

    id = Column(Integer, primary_key=True, index=True)
    question = Column(Text, nullable=False)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relations
    author = relationship("User")
    options = relationship("PollOption", back_populates="poll", cascade="all, delete-orphan")
    votes = relationship("PollVote", back_populates="poll", cascade="all, delete-orphan")


class PollOption(Base):
    __tablename__ = "poll_options"

    id = Column(Integer, primary_key=True, index=True)
    poll_id = Column(Integer, ForeignKey("polls.id"), nullable=False)
    text = Column(String(200), nullable=False)
    votes = Column(Integer, default=0)

    # Relations
    poll = relationship("Poll", back_populates="options")


class PollVote(Base):
    __tablename__ = "poll_votes"

    id = Column(Integer, primary_key=True, index=True)
    poll_id = Column(Integer, ForeignKey("polls.id"), nullable=False)
    option_id = Column(Integer, ForeignKey("poll_options.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relations
    poll = relationship("Poll", back_populates="votes")

    # Contrainte unique pour éviter les doubles votes
    __table_args__ = (
        {"sqlite_autoincrement": True},
    )


class HealthArticle(Base):
    __tablename__ = "health_articles"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    summary = Column(Text, nullable=False)
    content = Column(Text, nullable=False)
    category = Column(String(50), nullable=False)  # prevention, treatment, nutrition, maternal, hygiene, vaccination
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    read_time = Column(Integer, default=5)  # en minutes
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relations
    author = relationship("User")
    likes = relationship("HealthArticleLike", back_populates="article", cascade="all, delete-orphan")
    bookmarks = relationship("HealthArticleBookmark", back_populates="article", cascade="all, delete-orphan")


class HealthArticleLike(Base):
    __tablename__ = "health_article_likes"

    id = Column(Integer, primary_key=True, index=True)
    article_id = Column(Integer, ForeignKey("health_articles.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relations
    article = relationship("HealthArticle", back_populates="likes")

    __table_args__ = ({"sqlite_autoincrement": True},)


class HealthArticleBookmark(Base):
    __tablename__ = "health_article_bookmarks"

    id = Column(Integer, primary_key=True, index=True)
    article_id = Column(Integer, ForeignKey("health_articles.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relations
    article = relationship("HealthArticle", back_populates="bookmarks")

    __table_args__ = ({"sqlite_autoincrement": True},)


# ============ Static Content Models ============

class EmergencyContact(Base):
    __tablename__ = "emergency_contacts"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    phone = Column(String(50), nullable=False)
    type = Column(String(50), nullable=False)  # emergency, hospital, police, fire, poison, psychological, other
    district = Column(String(50), nullable=False)
    address = Column(String(500), nullable=True)
    available24h = Column(Boolean, default=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class HealthProtocol(Base):
    """Protocoles de santé - documents保存 par les agents"""
    __tablename__ = "health_protocols"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    category = Column(String(50), nullable=False)  # prevention, treatment, emergency, etc.
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    is_public = Column(Boolean, default=False)  # Partagé avec tous ou personnel
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relations
    author = relationship("User")


class Event(Base):
    """Événements (formations, réunions, séminaires, ateliers)"""
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    category = Column(String(50), nullable=False)  # formation, reunion, seminaire, workshop
    date = Column(String(50), nullable=False)  # YYYY-MM-DD
    time = Column(String(50), nullable=False)  # HH:MM - HH:MM
    location = Column(String(500), nullable=False)
    district = Column(String(50), nullable=False)
    organizer = Column(String(200), nullable=False)
    max_participants = Column(Integer, nullable=True)
    image_url = Column(String(500), nullable=True)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relations
    author = relationship("User")
    registrations = relationship("EventRegistration", back_populates="event", cascade="all, delete-orphan")


class EventRegistration(Base):
    """Inscriptions aux événements"""
    __tablename__ = "event_registrations"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("events.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relations
    event = relationship("Event", back_populates="registrations")
    user = relationship("User")

    # Contrainte unique pour éviter les doubles inscriptions
    __table_args__ = (
        {"sqlite_autoincrement": True},
    )


class Message(Base):
    """Messages directs entre utilisateurs"""
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=False)
    sender_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    receiver_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relations
    sender = relationship("User", foreign_keys=[sender_id])
    receiver = relationship("User", foreign_keys=[receiver_id])


class Conversation(Base):
    """Conversations entre utilisateurs"""
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    user1_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user2_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    last_message_id = Column(Integer, ForeignKey("messages.id"), nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relations
    user1 = relationship("User", foreign_keys=[user1_id])
    user2 = relationship("User", foreign_keys=[user2_id])
    last_message = relationship("Message", foreign_keys=[last_message_id])
    messages = relationship("Message", 
                          primaryjoin="or_(Conversation.user1_id == Message.sender_id, Conversation.user2_id == Message.sender_id)",
                          order_by="Message.created_at.desc()")