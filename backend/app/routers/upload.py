from fastapi import APIRouter, UploadFile, File, HTTPException, status, Depends
from sqlalchemy.orm import Session
import uuid
import os
from datetime import datetime
from typing import Optional
from .. import models
from ..database import get_db
from ..auth import get_current_user

router = APIRouter(prefix="/upload", tags=["Upload"])

# Configuration du dossier de stockage
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Extensions autorisées
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB


def get_file_extension(filename: str) -> str:
    """Extrait l'extension du fichier"""
    return os.path.splitext(filename)[1].lower()


def validate_file(file: UploadFile):
    """Valide le fichier uploadé"""
    # Vérifier l'extension
    extension = get_file_extension(file.filename)
    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Extension non autorisée. Extensions autorisées: {', '.join(ALLOWED_EXTENSIONS)}"
        )

    # Vérifier la taille
    file.file.seek(0, os.SEEK_END)
    size = file.file.tell()
    file.file.seek(0)
    
    if size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Fichier trop volumineux. Taille maximale: {MAX_FILE_SIZE // 1024 // 1024} MB"
        )
    
    # Remettre le curseur au début pour la lecture
    file.file.seek(0)


async def save_file(file: UploadFile, folder: str = "images") -> str:
    """Sauvegarde le fichier et retourne le chemin relatif"""
    # Générer un nom de fichier unique
    extension = get_file_extension(file.filename)
    filename = f"{uuid.uuid4().hex}{extension}"
    
    # Créer le dossier si nécessaire
    folder_path = os.path.join(UPLOAD_DIR, folder)
    os.makedirs(folder_path, exist_ok=True)
    
    # Sauvegarder le fichier
    file_path = os.path.join(folder_path, filename)
    with open(file_path, "wb") as buffer:
        # Lire le contenu du fichier
        content = await file.read()
        buffer.write(content)
    
    # Retourner le chemin relatif pour l'API
    return f"/{folder}/{filename}"


@router.post("/image", status_code=status.HTTP_201_CREATED)
async def upload_image(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Upload une image pour une publication
    - Taille maximale: 10 MB
    - Extensions autorisées: jpg, jpeg, png, gif, webp
    """
    try:
        # Valider le fichier
        validate_file(file)
        
        # Sauvegarder le fichier
        image_path = await save_file(file, "posts")
        
        # Créer une entrée dans la base de données (optionnel)
        # Vous pouvez créer un modèle Image si nécessaire
        
        return {
            "filename": file.filename,
            "image_url": image_path,
            "message": "Image uploadée avec succès"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de l'upload: {str(e)}"
        )


@router.post("/avatar", status_code=status.HTTP_201_CREATED)
async def upload_avatar(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Upload une image de profil (avatar)
    - Taille maximale: 10 MB
    - Extensions autorisées: jpg, jpeg, png, gif, webp
    """
    try:
        # Valider le fichier
        validate_file(file)
        
        # Sauvegarder le fichier
        avatar_path = await save_file(file, "avatars")
        
        # Mettre à jour l'avatar de l'utilisateur
        current_user.avatar_url = avatar_path
        db.commit()
        db.refresh(current_user)
        
        return {
            "filename": file.filename,
            "avatar_url": avatar_path,
            "message": "Avatar mis à jour avec succès"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de l'upload: {str(e)}"
        )


@router.post("/event", status_code=status.HTTP_201_CREATED)
async def upload_event_image(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Upload une image pour un événement
    - Taille maximale: 10 MB
    - Extensions autorisées: jpg, jpeg, png, gif, webp
    """
    try:
        # Valider le fichier
        validate_file(file)
        
        # Sauvegarder le fichier
        image_path = await save_file(file, "events")
        
        return {
            "filename": file.filename,
            "image_url": image_path,
            "message": "Image d'événement uploadée avec succès"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de l'upload: {str(e)}"
        )


@router.get("/files/{folder}/{filename}")
async def get_file(
    folder: str,
    filename: str,
    current_user: models.User = Depends(get_current_user)
):
    """
    Récupérer un fichier uploadé
    """
    try:
        file_path = os.path.join(UPLOAD_DIR, folder, filename)
        
        if not os.path.exists(file_path):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Fichier non trouvé"
            )
        
        # En production, vous devriez utiliser un serveur de fichiers (S3, Cloudinary, etc.)
        # Pour le développement, on retourne le chemin
        return {
            "folder": folder,
            "filename": filename,
            "path": file_path,
            "url": f"/upload/files/{folder}/{filename}"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur: {str(e)}"
        )


@router.delete("/files/{folder}/{filename}")
async def delete_file(
    folder: str,
    filename: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Supprimer un fichier uploadé
    """
    try:
        file_path = os.path.join(UPLOAD_DIR, folder, filename)
        
        if not os.path.exists(file_path):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Fichier non trouvé"
            )
        
        # Supprimer le fichier
        os.remove(file_path)
        
        return {
            "message": "Fichier supprimé avec succès",
            "filename": filename,
            "folder": folder
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la suppression: {str(e)}"
        )