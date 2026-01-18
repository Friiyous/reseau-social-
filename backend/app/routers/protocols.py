from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from .. import models, schemas
from ..database import get_db
from ..auth import get_current_user

router = APIRouter(prefix="/protocols", tags=["Protocoles de santé"])


@router.get("/", response_model=List[schemas.HealthProtocolResponse])
def get_my_protocols(
    category: str = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Récupérer mes protocoles de santé (personnels ou publics)"""
    query = db.query(models.HealthProtocol).filter(
        (models.HealthProtocol.author_id == current_user.id) |
        (models.HealthProtocol.is_public == True)
    )

    if category:
        query = query.filter(models.HealthProtocol.category == category)

    protocols = query.order_by(
        models.HealthProtocol.updated_at.desc()
    ).offset(skip).limit(limit).all()

    result = []
    for p in protocols:
        result.append({
            "id": p.id,
            "title": p.title,
            "content": p.content,
            "category": p.category,
            "author_id": p.author_id,
            "author_name": f"{p.author.first_name} {p.author.last_name}" if p.author else "Inconnu",
            "is_public": p.is_public,
            "created_at": p.created_at,
            "updated_at": p.updated_at
        })

    return result


@router.post("/", response_model=schemas.HealthProtocolResponse)
def create_protocol(
    protocol_data: schemas.HealthProtocolCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Créer un nouveau protocole de santé"""
    protocol = models.HealthProtocol(
        title=protocol_data.title,
        content=protocol_data.content,
        category=protocol_data.category,
        author_id=current_user.id,
        is_public=protocol_data.is_public
    )
    db.add(protocol)
    db.commit()
    db.refresh(protocol)

    return {
        "id": protocol.id,
        "title": protocol.title,
        "content": protocol.content,
        "category": protocol.category,
        "author_id": protocol.author_id,
        "author_name": f"{current_user.first_name} {current_user.last_name}",
        "is_public": protocol.is_public,
        "created_at": protocol.created_at,
        "updated_at": protocol.updated_at
    }


@router.get("/{protocol_id}", response_model=schemas.HealthProtocolResponse)
def get_protocol(
    protocol_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Détails d'un protocole"""
    protocol = db.query(models.HealthProtocol).filter(
        models.HealthProtocol.id == protocol_id
    ).first()

    if not protocol:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Protocole non trouvé"
        )

    # Vérifier l'accès
    if protocol.author_id != current_user.id and not protocol.is_public:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vous n'avez pas accès à ce protocole"
        )

    return {
        "id": protocol.id,
        "title": protocol.title,
        "content": protocol.content,
        "category": protocol.category,
        "author_id": protocol.author_id,
        "author_name": f"{protocol.author.first_name} {protocol.author.last_name}" if protocol.author else "Inconnu",
        "is_public": protocol.is_public,
        "created_at": protocol.created_at,
        "updated_at": protocol.updated_at
    }


@router.put("/{protocol_id}", response_model=schemas.HealthProtocolResponse)
def update_protocol(
    protocol_id: int,
    protocol_data: schemas.HealthProtocolUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Modifier un protocole (auteur uniquement)"""
    protocol = db.query(models.HealthProtocol).filter(
        models.HealthProtocol.id == protocol_id
    ).first()

    if not protocol:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Protocole non trouvé"
        )

    if protocol.author_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vous ne pouvez pas modifier ce protocole"
        )

    update_data = protocol_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(protocol, field, value)

    db.commit()
    db.refresh(protocol)

    return {
        "id": protocol.id,
        "title": protocol.title,
        "content": protocol.content,
        "category": protocol.category,
        "author_id": protocol.author_id,
        "author_name": f"{current_user.first_name} {current_user.last_name}",
        "is_public": protocol.is_public,
        "created_at": protocol.created_at,
        "updated_at": protocol.updated_at
    }


@router.delete("/{protocol_id}")
def delete_protocol(
    protocol_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Supprimer un protocole (auteur uniquement)"""
    protocol = db.query(models.HealthProtocol).filter(
        models.HealthProtocol.id == protocol_id
    ).first()

    if not protocol:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Protocole non trouvé"
        )

    if protocol.author_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vous ne pouvez pas supprimer ce protocole"
        )

    db.delete(protocol)
    db.commit()
    return {"message": "Protocole supprimé"}
