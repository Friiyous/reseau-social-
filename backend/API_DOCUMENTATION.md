# 📱 Documentation API - Réseau Social Santé Poro

**Version** : 1.0.0
**Base URL** : `http://localhost:8000/api/v1`

---

## 📋 Table des Matières

1. [Authentification](#-authentification)
2. [Utilisateurs](#-utilisateurs)
3. [Publications](#-publications)
4. [Commentaires](#-commentaires)
5. [Likes](#-likes)
6. [Follows](#-follows)
7. [Sondages](#-sondages)
8. [Articles de Santé](#-articles-de-santé)
9. [Urgences](#-urgences)
10. [Protocoles](#-protocoles)
11. [Événements](#-événements)
12. [Upload](#-upload)
13. [Admin](#-admin)

---

## 🔐 Authentification

### Login
```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "username": "string",
  "password": "string"
}
```

**Réponse** :
```json
{
  "access_token": "string",
  "token_type": "bearer",
  "user": {
    "id": 0,
    "username": "string",
    "first_name": "string",
    "last_name": "string",
    "email": "string",
    "role": "string",
    "district": "string",
    "health_center": "string",
    "specialty": "string",
    "department": "string",
    "is_admin": false,
    "avatar_url": "string"
  }
}
```

### Register
```http
POST /api/v1/auth/register
Content-Type: application/json

{
  "username": "string",
  "password": "string",
  "first_name": "string",
  "last_name": "string",
  "email": "string",
  "district": "string",
  "health_center": "string",
  "specialty": "string",
  "department": "string"
}
```

**Réponse** : Même que login

### Quick Register
```http
POST /api/v1/auth/quick-register
Content-Type: application/json

{
  "first_name": "string",
  "last_name": "string",
  "district": "string",
  "specialty": "string",
  "department": "string",
  "health_center": "string"
}
```

**Réponse** : Même que login

### Me (Current User)
```http
GET /api/v1/auth/me
Authorization: Bearer {token}
```

**Réponse** :
```json
{
  "id": 0,
  "username": "string",
  "first_name": "string",
  "last_name": "string",
  "email": "string",
  "role": "string",
  "district": "string",
  "health_center": "string",
  "specialty": "string",
  "department": "string",
  "is_admin": false,
  "avatar_url": "string"
}
```

### Change Password
```http
POST /api/v1/auth/change-password
Authorization: Bearer {token}
Content-Type: application/json

{
  "old_password": "string",
  "new_password": "string"
}
```

**Réponse** :
```json
{
  "message": "Mot de passe changé avec succès"
}
```

---

## 👥 Utilisateurs

### Get Profile
```http
GET /api/v1/users/me
Authorization: Bearer {token}
```

**Réponse** : Même que `/auth/me`

### Update Profile
```http
PUT /api/v1/users/me/
Authorization: Bearer {token}
Content-Type: application/json

{
  "first_name": "string",
  "last_name": "string",
  "bio": "string",
  "health_center": "string",
  "avatar_url": "string"
}
```

**Réponse** : Même que `/auth/me`

### Get User Profile
```http
GET /api/v1/users/{user_id}/
Authorization: Bearer {token}
```

**Réponse** : Même que `/auth/me`

### Search Users
```http
GET /api/v1/users/search/{query}/
Authorization: Bearer {token}
```

**Réponse** :
```json
[
  {
    "id": 0,
    "username": "string",
    "first_name": "string",
    "last_name": "string",
    "role": "string",
    "district": "string",
    "health_center": "string"
  }
]
```

### Get Users by District
```http
GET /api/v1/users/district/{district}/
Authorization: Bearer {token}
```

**Réponse** : Même que search

### Get All Users (Admin)
```http
GET /api/v1/users/
Authorization: Bearer {token}
```

**Réponse** : Même que search

---

## 📝 Publications

### Get Posts
```http
GET /api/v1/posts/?skip=0&limit=50
Authorization: Bearer {token}
```

**Réponse** :
```json
[
  {
    "id": 0,
    "content": "string",
    "image_url": "string",
    "created_at": "datetime",
    "author": {
      "id": 0,
      "first_name": "string",
      "last_name": "string",
      "role": "string",
      "avatar_url": "string"
    },
    "likes_count": 0,
    "comments_count": 0,
    "is_liked_by_me": false
  }
]
```

### Get User Posts
```http
GET /api/v1/posts/user/{user_id}/?skip=0&limit=50
Authorization: Bearer {token}
```

**Réponse** : Même que get posts

### Get Post Details
```http
GET /api/v1/posts/{post_id}
Authorization: Bearer {token}
```

**Réponse** :
```json
{
  "id": 0,
  "content": "string",
  "image_url": "string",
  "created_at": "datetime",
  "author": {
    "id": 0,
    "first_name": "string",
    "last_name": "string",
    "role": "string",
    "avatar_url": "string"
  },
  "likes_count": 0,
  "comments_count": 0,
  "is_liked_by_me": false,
  "comments": [
    {
      "id": 0,
      "content": "string",
      "created_at": "datetime",
      "author": {
        "id": 0,
        "first_name": "string",
        "last_name": "string",
        "role": "string"
      }
    }
  ]
}
```

### Create Post
```http
POST /api/v1/posts/
Authorization: Bearer {token}
Content-Type: application/json

{
  "content": "string",
  "image_url": "string"
}
```

**Réponse** : Même que get posts (single)

### Update Post
```http
PUT /api/v1/posts/{post_id}
Authorization: Bearer {token}
Content-Type: application/json

{
  "content": "string",
  "image_url": "string"
}
```

**Réponse** : Même que get posts (single)

### Delete Post
```http
DELETE /api/v1/posts/{post_id}
Authorization: Bearer {token}
```

**Réponse** :
```json
{
  "message": "Post supprimé avec succès"
}
```

---

## 💬 Commentaires

### Create Comment
```http
POST /api/v1/posts/{post_id}/comments
Authorization: Bearer {token}
Content-Type: application/json

{
  "content": "string"
}
```

**Réponse** :
```json
{
  "id": 0,
  "content": "string",
  "created_at": "datetime",
  "post_id": 0,
  "author": {
    "id": 0,
    "first_name": "string",
    "last_name": "string",
    "role": "string"
  }
}
```

### Update Comment
```http
PUT /api/v1/posts/{post_id}/comments/{comment_id}
Authorization: Bearer {token}
Content-Type: application/json

{
  "content": "string"
}
```

**Réponse** : Même que create comment

### Delete Comment
```http
DELETE /api/v1/posts/{post_id}/comments/{comment_id}
Authorization: Bearer {token}
```

**Réponse** :
```json
{
  "message": "Commentaire supprimé"
}
```

---

## ❤️ Likes

### Like Post
```http
POST /api/v1/posts/{post_id}/like
Authorization: Bearer {token}
```

**Réponse** :
```json
{
  "id": 0,
  "post_id": 0,
  "user_id": 0,
  "created_at": "datetime"
}
```

### Unlike Post
```http
DELETE /api/v1/posts/{post_id}/like
Authorization: Bearer {token}
```

**Réponse** :
```json
{
  "message": "Like retiré"
}
```

---

## 👥 Follows

### Follow User
```http
POST /api/v1/follows/{user_id}/
Authorization: Bearer {token}
```

**Réponse** :
```json
{
  "id": 0,
  "follower_id": 0,
  "following_id": 0,
  "created_at": "datetime"
}
```

### Unfollow User
```http
DELETE /api/v1/follows/{user_id}/
Authorization: Bearer {token}
```

**Réponse** :
```json
{
  "message": "Follow retiré"
}
```

### Get Followers
```http
GET /api/v1/follows/followers/{user_id}/
Authorization: Bearer {token}
```

**Réponse** :
```json
[
  {
    "id": 0,
    "username": "string",
    "first_name": "string",
    "last_name": "string",
    "role": "string",
    "district": "string",
    "health_center": "string"
  }
]
```

### Get Following
```http
GET /api/v1/follows/following/{user_id}/
Authorization: Bearer {token}
```

**Réponse** : Même que get followers

---

## 📊 Sondages

### Get Polls
```http
GET /api/v1/polls/
Authorization: Bearer {token}
```

**Réponse** :
```json
[
  {
    "id": 0,
    "question": "string",
    "options": [
      {
        "id": 0,
        "text": "string",
        "votes": 0
      }
    ],
    "total_votes": 0,
    "has_voted": false,
    "author_id": 0,
    "author_name": "string",
    "created_at": "datetime"
  }
]
```

### Create Poll
```http
POST /api/v1/polls/
Authorization: Bearer {token}
Content-Type: application/json

{
  "question": "string",
  "options": ["string", "string"]
}
```

**Réponse** : Même que get polls (single)

### Vote Poll
```http
POST /api/v1/polls/{poll_id}/vote
Authorization: Bearer {token}
Content-Type: application/json

{
  "option_id": 0
}
```

**Réponse** : Même que get polls (single)

### Delete Poll
```http
DELETE /api/v1/polls/{poll_id}
Authorization: Bearer {token}
```

**Réponse** :
```json
{
  "message": "Sondage supprimé"
}
```

---

## 📚 Articles de Santé

### Get Articles
```http
GET /api/v1/health-articles/?category={category}
Authorization: Bearer {token}
```

**Réponse** :
```json
[
  {
    "id": 0,
    "title": "string",
    "summary": "string",
    "content": "string",
    "category": "string",
    "author_id": 0,
    "author_name": "string",
    "read_time": 0,
    "likes_count": 0,
    "is_bookmarked": false,
    "created_at": "datetime"
  }
]
```

### Get Article
```http
GET /api/v1/health-articles/{article_id}
Authorization: Bearer {token}
```

**Réponse** : Même que get articles (single)

### Like Article
```http
POST /api/v1/health-articles/{article_id}/like
Authorization: Bearer {token}
```

**Réponse** :
```json
{
  "message": "Article liké"
}
```

### Bookmark Article
```http
POST /api/v1/health-articles/{article_id}/bookmark
Authorization: Bearer {token}
```

**Réponse** :
```json
{
  "message": "Article ajouté aux favoris"
}
```

### Get Bookmarked
```http
GET /api/v1/health-articles/bookmarked/
Authorization: Bearer {token}
```

**Réponse** : Même que get articles

---

## 🚨 Urgences

### Get Emergency Contacts
```http
GET /api/v1/emergency/?type={type}
Authorization: Bearer {token}
```

**Réponse** :
```json
[
  {
    "id": 0,
    "name": "string",
    "phone": "string",
    "type": "string",
    "district": "string",
    "description": "string"
  }
]
```

---

## 📄 Protocoles

### Get Protocols
```http
GET /api/v1/protocols/?category={category}
Authorization: Bearer {token}
```

**Réponse** :
```json
[
  {
    "id": 0,
    "title": "string",
    "content": "string",
    "category": "string",
    "author_id": 0,
    "author_name": "string",
    "created_at": "datetime"
  }
]
```

---

## 📅 Événements

### Get Events
```http
GET /api/v1/events/?category={category}
Authorization: Bearer {token}
```

**Réponse** :
```json
[
  {
    "id": 0,
    "title": "string",
    "description": "string",
    "category": "string",
    "date": "date",
    "time": "string",
    "location": "string",
    "district": "string",
    "organizer": "string",
    "max_participants": 0,
    "image_url": "string",
    "author_id": 0,
    "author_name": "string",
    "registered_count": 0,
    "is_registered": false,
    "created_at": "datetime",
    "updated_at": "datetime"
  }
]
```

### Create Event
```http
POST /api/v1/events/
Authorization: Bearer {token}
Content-Type: application/json

{
  "title": "string",
  "description": "string",
  "category": "string",
  "date": "date",
  "time": "string",
  "location": "string",
  "district": "string",
  "organizer": "string",
  "max_participants": 0,
  "image_url": "string"
}
```

**Réponse** : Même que get events (single)

### Register Event
```http
POST /api/v1/events/{event_id}/register
Authorization: Bearer {token}
```

**Réponse** :
```json
{
  "message": "Inscription confirmée"
}
```

### Unregister Event
```http
DELETE /api/v1/events/{event_id}/unregister
Authorization: Bearer {token}
```

**Réponse** :
```json
{
  "message": "Inscription annulée"
}
```

### Update Event
```http
PUT /api/v1/events/{event_id}
Authorization: Bearer {token}
Content-Type: application/json

{
  "title": "string",
  "description": "string",
  "category": "string",
  "date": "date",
  "time": "string",
  "location": "string",
  "district": "string",
  "organizer": "string",
  "max_participants": 0,
  "image_url": "string"
}
```

**Réponse** : Même que get events (single)

### Delete Event
```http
DELETE /api/v1/events/{event_id}
Authorization: Bearer {token}
```

**Réponse** :
```json
{
  "message": "Événement supprimé"
}
```

---

## 📤 Upload

### Upload Image
```http
POST /api/v1/upload/image
Authorization: Bearer {token}
Content-Type: multipart/form-data

file: [binary]
```

**Réponse** :
```json
{
  "filename": "string",
  "image_url": "string",
  "message": "Image uploadée avec succès"
}
```

### Upload Avatar
```http
POST /api/v1/upload/avatar
Authorization: Bearer {token}
Content-Type: multipart/form-data

file: [binary]
```

**Réponse** :
```json
{
  "filename": "string",
  "avatar_url": "string",
  "message": "Avatar uploadé avec succès"
}
```

### Upload Event Image
```http
POST /api/v1/upload/event
Authorization: Bearer {token}
Content-Type: multipart/form-data

file: [binary]
```

**Réponse** :
```json
{
  "filename": "string",
  "image_url": "string",
  "message": "Image d'événement uploadée avec succès"
}
```

---

## 👑 Admin

### Get Stats
```http
GET /api/v1/admin/stats
Authorization: Bearer {token}
```

**Réponse** :
```json
{
  "users_count": 0,
  "posts_count": 0,
  "comments_count": 0,
  "polls_count": 0,
  "events_count": 0,
  "articles_count": 0
}
```

### Get All Users
```http
GET /api/v1/admin/users
Authorization: Bearer {token}
```

**Réponse** : Même que `/users/`

### Delete User
```http
DELETE /api/v1/admin/users/{user_id}
Authorization: Bearer {token}
```

**Réponse** :
```json
{
  "message": "Utilisateur supprimé"
}
```

### Get All Posts
```http
GET /api/v1/admin/posts
Authorization: Bearer {token}
```

**Réponse** : Même que `/posts/`

### Delete Post
```http
DELETE /api/v1/admin/posts/{post_id}
Authorization: Bearer {token}
```

**Réponse** :
```json
{
  "message": "Post supprimé"
}
```

---

## 📊 Codes de Statut

- `200` : Succès
- `201` : Créé
- `400` : Requête invalide
- `401` : Non autorisé
- `403` : Interdit
- `404` : Non trouvé
- `500` : Erreur serveur

---

## 🎯 Bonnes Pratiques

1. **Authentification** : Toujours inclure le token JWT dans l'en-tête `Authorization: Bearer {token}`
2. **Pagination** : Utiliser `skip` et `limit` pour les listes
3. **Gestion des erreurs** : Toujours vérifier les codes de statut et les messages d'erreur
4. **Validation** : Tous les champs requis doivent être fournis

---

## 📝 Notes

- Tous les endpoints nécessitent une authentification sauf `/auth/login`, `/auth/register`, `/auth/quick-register`
- Les IDs dans les URLs doivent être des entiers valides
- Les dates doivent être au format ISO 8601 (YYYY-MM-DD)
- Les images uploadées doivent être au format JPEG ou PNG

---

**Documentation complète et à jour - 18/01/2026**