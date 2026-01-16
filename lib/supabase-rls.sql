-- =============================================
-- Le District - Politiques RLS (Row Level Security)
-- =============================================

-- Activer RLS sur toutes les tables
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE health_professionals ENABLE ROW LEVEL SECURITY;
ALTER TABLE posts ENABLE ROW LEVEL SECURITY;
ALTER TABLE post_likes ENABLE ROW LEVEL SECURITY;
ALTER TABLE comments ENABLE ROW LEVEL SECURITY;
ALTER TABLE notifications ENABLE ROW LEVEL SECURITY;
ALTER TABLE conversations ENABLE ROW LEVEL SECURITY;
ALTER TABLE conversation_participants ENABLE ROW LEVEL SECURITY;
ALTER TABLE messages ENABLE ROW LEVEL SECURITY;

-- =============================================
-- PROFILS
-- =============================================

-- Tout le monde peut voir les profils
CREATE POLICY "Profiles are viewable by everyone"
  ON profiles FOR SELECT
  USING (true);

-- Les utilisateurs peuvent mettre à jour leur propre profil
CREATE POLICY "Users can update own profile"
  ON profiles FOR UPDATE
  USING (auth.uid() = id);

-- Les utilisateurs peuvent insérer leur propre profil
CREATE POLICY "Users can insert own profile"
  ON profiles FOR INSERT
  WITH CHECK (auth.uid() = id);

-- =============================================
-- PROFESSIONNELS DE SANTÉ
-- =============================================

-- Tout le monde peut voir les professionnels
CREATE POLICY "Health professionals are viewable by everyone"
  ON health_professionals FOR SELECT
  USING (true);

-- Les utilisateurs peuvent insérer leurs propres informations professionnelles
CREATE POLICY "Users can insert own health professional info"
  ON health_professionals FOR INSERT
  WITH CHECK (auth.uid() = user_id);

-- Les utilisateurs peuvent mettre à jour leurs propres informations professionnelles
CREATE POLICY "Users can update own health professional info"
  ON health_professionals FOR UPDATE
  USING (auth.uid() = user_id);

-- =============================================
-- POSTS
-- =============================================

-- Tout le monde peut voir les posts
CREATE POLICY "Posts are viewable by everyone"
  ON posts FOR SELECT
  USING (true);

-- Les utilisateurs authentifiés peuvent créer des posts
CREATE POLICY "Authenticated users can create posts"
  ON posts FOR INSERT
  WITH CHECK (auth.uid() = author_id);

-- Les utilisateurs peuvent supprimer leurs propres posts
CREATE POLICY "Users can delete own posts"
  ON posts FOR DELETE
  USING (auth.uid() = author_id);

-- =============================================
-- LIKES
-- =============================================

-- Tout le monde peut voir les likes
CREATE POLICY "Likes are viewable by everyone"
  ON post_likes FOR SELECT
  USING (true);

-- Les utilisateurs peuvent liker des posts
CREATE POLICY "Users can like posts"
  ON post_likes FOR INSERT
  WITH CHECK (auth.uid() = user_id);

-- Les utilisateurs peuvent retirer leurs likes
CREATE POLICY "Users can unlike posts"
  ON post_likes FOR DELETE
  USING (auth.uid() = user_id);

-- =============================================
-- COMMENTAIRES
-- =============================================

-- Tout le monde peut voir les commentaires
CREATE POLICY "Comments are viewable by everyone"
  ON comments FOR SELECT
  USING (true);

-- Les utilisateurs peuvent créer des commentaires
CREATE POLICY "Users can create comments"
  ON comments FOR INSERT
  WITH CHECK (auth.uid() = author_id);

-- Les utilisateurs peuvent supprimer leurs propres commentaires
CREATE POLICY "Users can delete own comments"
  ON comments FOR DELETE
  USING (auth.uid() = author_id);

-- =============================================
-- NOTIFICATIONS
-- =============================================

-- Les utilisateurs peuvent voir uniquement leurs propres notifications
CREATE POLICY "Users can view own notifications"
  ON notifications FOR SELECT
  USING (auth.uid() = user_id);

-- Les utilisateurs peuvent mettre à jour leurs propres notifications
CREATE POLICY "Users can update own notifications"
  ON notifications FOR UPDATE
  USING (auth.uid() = user_id);

-- Le système peut créer des notifications
CREATE POLICY "System can create notifications"
  ON notifications FOR INSERT
  WITH CHECK (true);

-- =============================================
-- CONVERSATIONS
-- =============================================

-- Les utilisateurs peuvent voir les conversations dont ils sont participants
CREATE POLICY "Users can view own conversations"
  ON conversations FOR SELECT
  USING (
    EXISTS (
      SELECT 1 FROM conversation_participants
      WHERE conversation_id = conversations.id
      AND user_id = auth.uid()
    )
  );

-- Les utilisateurs authentifiés peuvent créer des conversations
CREATE POLICY "Authenticated users can create conversations"
  ON conversations FOR INSERT
  WITH CHECK (auth.role() = 'authenticated');

-- =============================================
-- PARTICIPANTS AUX CONVERSATIONS
-- =============================================

-- Les participants peuvent voir les participants de leurs conversations
CREATE POLICY "Participants can view conversation participants"
  ON conversation_participants FOR SELECT
  USING (
    EXISTS (
      SELECT 1 FROM conversation_participants cp
      WHERE cp.conversation_id = conversation_participants.conversation_id
      AND cp.user_id = auth.uid()
    )
  );

-- Les utilisateurs peuvent s'ajouter aux conversations
CREATE POLICY "Users can join conversations"
  ON conversation_participants FOR INSERT
  WITH CHECK (auth.uid() = user_id);

-- =============================================
-- MESSAGES
-- =============================================

-- Les participants peuvent voir les messages de leurs conversations
CREATE POLICY "Participants can view messages"
  ON messages FOR SELECT
  USING (
    EXISTS (
      SELECT 1 FROM conversation_participants
      WHERE conversation_id = messages.conversation_id
      AND user_id = auth.uid()
    )
  );

-- Les participants peuvent envoyer des messages
CREATE POLICY "Participants can send messages"
  ON messages FOR INSERT
  WITH CHECK (
    auth.uid() = sender_id
    AND EXISTS (
      SELECT 1 FROM conversation_participants
      WHERE conversation_id = messages.conversation_id
      AND user_id = auth.uid()
    )
  );
