from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from .. import models, schemas
from ..database import get_db
from ..auth import get_current_user

router = APIRouter(prefix="/emergency", tags=["Numéros d'urgence"])


@router.get("/", response_model=List[schemas.EmergencyContactResponse])
def get_emergency_contacts(
    type: str = None,
    district: str = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Liste des contacts d'urgence"""
    query = db.query(models.EmergencyContact)

    if type:
        query = query.filter(models.EmergencyContact.type == type)
    if district:
        query = query.filter(models.EmergencyContact.district == district)

    contacts = query.order_by(
        models.EmergencyContact.type,
        models.EmergencyContact.name
    ).offset(skip).limit(limit).all()

    return contacts


@router.get("/{contact_id}", response_model=schemas.EmergencyContactResponse)
def get_emergency_contact(
    contact_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Détails d'un contact d'urgence"""
    contact = db.query(models.EmergencyContact).filter(
        models.EmergencyContact.id == contact_id
    ).first()

    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact non trouvé"
        )

    return contact


# ============ ADMIN ENDPOINTS ============

@router.post("/", response_model=schemas.EmergencyContactResponse)
def create_emergency_contact(
    contact_data: schemas.EmergencyContactCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Créer un contact d'urgence (admin uniquement)"""
    # Vérifier si c'est un admin (à implémenter avec un système de roles)
    contact = models.EmergencyContact(
        name=contact_data.name,
        phone=contact_data.phone,
        type=contact_data.type,
        district=contact_data.district,
        address=contact_data.address or None,
        available24h=contact_data.available24h,
        description=contact_data.description or None,
    )
    db.add(contact)
    db.commit()
    db.refresh(contact)
    return contact


@router.put("/{contact_id}", response_model=schemas.EmergencyContactResponse)
def update_emergency_contact(
    contact_id: int,
    contact_data: schemas.EmergencyContactUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Modifier un contact d'urgence (admin uniquement)"""
    contact = db.query(models.EmergencyContact).filter(
        models.EmergencyContact.id == contact_id
    ).first()

    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact non trouvé"
        )

    update_data = contact_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(contact, field, value)

    db.commit()
    db.refresh(contact)
    return contact


@router.delete("/{contact_id}")
def delete_emergency_contact(
    contact_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Supprimer un contact d'urgence (admin uniquement)"""
    contact = db.query(models.EmergencyContact).filter(
        models.EmergencyContact.id == contact_id
    ).first()

    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact non trouvé"
        )

    db.delete(contact)
    db.commit()
    return {"message": "Contact supprimé"}
