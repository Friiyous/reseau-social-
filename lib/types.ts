export interface Profile {
    id: string;
    email: string;
    full_name: string;
    avatar_url?: string;
    phone?: string;
    district: string;
    created_at: string;
    updated_at?: string;
}

export interface HealthProfessional {
    user_id: string;
    specialty: string;
    structure?: string;
    professional_id?: string;
    created_at: string;
}

export interface Post {
    id: string;
    author_id: string;
    content: string;
    image_url?: string;
    created_at: string;
    author?: Profile;
    likes_count?: number;
    comments_count?: number;
    is_liked?: boolean;
}

export interface PostLike {
    post_id: string;
    user_id: string;
    created_at: string;
}

export interface Comment {
    id: string;
    post_id: string;
    author_id: string;
    content: string;
    created_at: string;
    author?: Profile;
}

export interface Notification {
    id: string;
    user_id: string;
    type: 'like' | 'comment' | 'message' | 'mention';
    content: string;
    read: boolean;
    related_id?: string;
    created_at: string;
}

export interface Conversation {
    id: string;
    created_at: string;
    updated_at: string;
    last_message?: Message;
    participants?: Profile[];
    unread_count?: number;
}

export interface ConversationParticipant {
    conversation_id: string;
    user_id: string;
    joined_at: string;
}

export interface Message {
    id: string;
    conversation_id: string;
    sender_id: string;
    content: string;
    created_at: string;
    sender?: Profile;
}
