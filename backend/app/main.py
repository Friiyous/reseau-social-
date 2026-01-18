from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from .database import engine, Base
import websockets
import asyncio
import json
from fastapi import WebSocket, WebSocketDisconnect

# Import des routers
from .routers import auth, users, posts, follows, polls, health_articles, emergency, protocols, admin, events, upload, notifications


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Créer les tables au démarrage
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="Réseau Social Santé Poro",
    description="Plateforme de connexion pour les agents de santé de la région du Poro",
    version="1.0.0",
    lifespan=lifespan,
    redirect_slashes=False
)

# ============ CORS FIX START ============
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8081"],  # Frontend web
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# ============ CORS FIX END ============

# Inclure les routes API
app.include_router(auth.router, prefix="/api/v1")
app.include_router(users.router, prefix="/api/v1")
app.include_router(posts.router, prefix="/api/v1")
app.include_router(follows.router, prefix="/api/v1")
app.include_router(polls.router, prefix="/api/v1")
app.include_router(health_articles.router, prefix="/api/v1")
app.include_router(emergency.router, prefix="/api/v1")
app.include_router(protocols.router, prefix="/api/v1")
app.include_router(admin.router, prefix="/api/v1")
app.include_router(events.router, prefix="/api/v1")
app.include_router(upload.router, prefix="/api/v1")
app.include_router(notifications.router, prefix="/api/v1")


@app.get("/")
def root():
    return {
        "message": "Bienvenue sur le Réseau Social Santé Poro",
        "version": "1.0.0",
        "districts": ["Dikodougou", "Ferkessédougou", "Korhogo", "Sinématiali"]
    }


@app.get("/health")
def health_check():
    return {"status": "ok"}

# WebSocket connections storage
active_connections = {}

# WebSocket endpoint for real-time messaging
@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: int):
    await websocket.accept()
    active_connections[user_id] = websocket

    try:
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)

            # Handle different message types
            if message_data["type"] == "message":
                # Broadcast message to recipient
                recipient_id = message_data["recipient_id"]
                if recipient_id in active_connections:
                    await active_connections[recipient_id].send_text(json.dumps({
                        "type": "new_message",
                        "data": message_data["data"]
                    }))

            elif message_data["type"] == "typing":
                # Broadcast typing status
                recipient_id = message_data["recipient_id"]
                if recipient_id in active_connections:
                    await active_connections[recipient_id].send_text(json.dumps({
                        "type": "typing_status",
                        "sender_id": user_id,
                        "is_typing": message_data["is_typing"]
                    }))

            elif message_data["type"] == "read_receipt":
                # Send read receipt
                sender_id = message_data["sender_id"]
                if sender_id in active_connections:
                    await active_connections[sender_id].send_text(json.dumps({
                        "type": "message_read",
                        "message_id": message_data["message_id"]
                    }))

    except WebSocketDisconnect:
        del active_connections[user_id]