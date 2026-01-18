# Réseau Social Santé Poro

Application mobile de connexion pour les agents de santé de la région du Poro (Côte d'Ivoire).

## Fonctionnalités

- Inscription et connexion des agents de santé
- Profil avec informations professionnelles (district, centre de santé, rôle)
- Publications avec texte et images
- Likes et commentaires
- Suivre/déconner d'autres agents
- Recherche par nom, district ou rôle

## Stack Technologique

### Backend (API)
- **FastAPI** (Python) - API moderne et rapide
- **SQLite** (développement) / **PostgreSQL** (production)
- **JWT** pour l'authentification
- **SQLAlchemy** pour la base de données

### Frontend (Mobile)
- **Expo** (React Native)
- **TypeScript**
- **React Navigation** (onglets + pile)
- **Axios** pour les requêtes HTTP

## Installation

### Prérequis

- Python 3.9+
- Node.js 18+
- npm ou yarn

### 1. Backend

```bash
cd backend

# Créer un environnement virtuel
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou: venv\Scripts\activate  # Windows

# Installer les dépendances
pip install -r requirements.txt

# Lancer le serveur
uvicorn app.main:app --reload
```

L'API sera accessible sur `http://localhost:8000`
- Documentation: `http://localhost:8000/docs`

### 2. Application Mobile

```bash
cd mobile

# Installer les dépendances
npm install

# Lancer Expo (mode développement)
npx expo start
```

## Utilisation

### Sur iPhone (avec Expo Go)

1. Télécharger **Expo Go** depuis l'App Store
2. Scanner le QR code affiché par `npx expo start`
3. L'application se charge instantanément !

### Sur le Web

```bash
cd mobile
npm run web
```

L'application s'ouvre dans votre navigateur.

## Hébergement (Production)

### Backend

**Option 1: Railway (Recommandé)**
1. Créer un compte sur [railway.app](https://railway.app)
2. Connecter votre repo GitHub
3. Ajouter un service PostgreSQL
4. Déployer - l'URL de l'API sera automatique

**Option 2: Render**
1. Créer un compte sur [render.com](https://render.com)
2. Créer un Web Service avec votre repo
3. Configurer les variables d'environnement

**Option 3: VPS (DigitalOcean, AWS, etc.)**
```bash
# Sur le serveur
sudo apt update
sudo apt install python3-pip nginx

# Cloner le projet
git clone <votre-repo>
cd backend

# Configuration nginx pour l'API
sudo nano /etc/nginx/sites-available/sante-poro-api
```

### Mobile (Web)

**Vercel ou Netlify (Gratuit)**
```bash
cd mobile
npm install -g vercel
vercel deploy
```

## Structure du Projet

```
mon-reseau-social/
├── backend/
│   ├── app/
│   │   ├── main.py          # Point d'entrée FastAPI
│   │   ├── models.py        # Modèles SQLAlchemy
│   │   ├── schemas.py       # Schémas Pydantic
│   │   ├── database.py      # Configuration DB
│   │   ├── auth.py          # Authentification JWT
│   │   └── routers/         # Routes API
│   │       ├── auth.py
│   │       ├── users.py
│   │       ├── posts.py
│   │       └── follows.py
│   ├── requirements.txt
│   └── tests/
├── mobile/
│   ├── App.tsx              # Navigation principale
│   ├── src/
│   │   ├── components/
│   │   ├── screens/
│   │   │   ├── LoginScreen.tsx
│   │   │   ├── RegisterScreen.tsx
│   │   │   ├── HomeScreen.tsx
│   │   │   ├── ProfileScreen.tsx
│   │   │   └── PostDetailScreen.tsx
│   │   ├── services/
│   │   │   └── api.ts       # Appels API
│   │   ├── context/
│   │   │   └── AuthContext.tsx
│   │   └── types/
│   │       └── index.ts
│   └── package.json
└── README.md
```

## Configuration pour la Production

### Backend

Dans `app/main.py`, modifier:
```python
# Pour PostgreSQL
SQLALCHEMY_DATABASE_URL = "postgresql://user:password@hostname/dbname"

# Pour JWT (utiliser des variables d'environnement!)
SECRET_KEY = "votre-clé-secrète-complexe"
```

### Mobile

Dans `src/services/api.ts`:
```typescript
const API_URL = 'https://votre-api-production.com/api/v1';
```

## Districts Supportés

- Dikodougou
- Ferkessédougou
- Korhogo
- Sinématiali

## Licence

MIT
