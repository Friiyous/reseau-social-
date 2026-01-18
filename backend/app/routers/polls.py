from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from .. import models, schemas
from ..database import get_db
from ..auth import get_current_user

router = APIRouter(prefix="/polls", tags=["Sondages"])


def calculate_total_votes(db: Session, poll_id: int) -> int:
    return db.query(models.PollOption).filter(
        models.PollOption.poll_id == poll_id
    ).sum(models.PollOption.votes) or 0


@router.get("/", response_model=List[schemas.PollResponse])
def get_polls(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Liste de tous les sondages"""
    polls = db.query(models.Poll).order_by(
        models.Poll.created_at.desc()
    ).offset(skip).limit(limit).all()

    result = []
    for poll in polls:
        # Vérifier si l'utilisateur a déjà voted
        has_voted = db.query(models.PollVote).filter(
            models.PollVote.poll_id == poll.id,
            models.PollVote.user_id == current_user.id
        ).first() is not None

        options = []
        for opt in poll.options:
            options.append({
                "id": opt.id,
                "text": opt.text,
                "votes": opt.votes
            })

        result.append({
            "id": poll.id,
            "question": poll.question,
            "options": options,
            "total_votes": calculate_total_votes(db, poll.id),
            "has_voted": has_voted,
            "author_id": poll.author_id,
            "author_name": f"{poll.author.first_name} {poll.author.last_name}" if poll.author else "Inconnu",
            "created_at": poll.created_at
        })

    return result


@router.post("/", response_model=schemas.PollResponse)
def create_poll(
    poll_data: schemas.PollCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Créer un nouveau sondage"""
    if not poll_data.options or len(poll_data.options) < 2:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Un sondage doit avoir au moins 2 options"
        )

    # Créer le sondage
    poll = models.Poll(
        question=poll_data.question,
        author_id=current_user.id
    )
    db.add(poll)
    db.flush()

    # Créer les options
    for option_text in poll_data.options:
        option = models.PollOption(
            poll_id=poll.id,
            text=option_text,
            votes=0
        )
        db.add(option)

    db.commit()
    db.refresh(poll)

    return {
        "id": poll.id,
        "question": poll.question,
        "options": [{"id": o.id, "text": o.text, "votes": 0} for o in poll.options],
        "total_votes": 0,
        "has_voted": False,
        "author_id": poll.author_id,
        "author_name": f"{current_user.first_name} {current_user.last_name}",
        "created_at": poll.created_at
    }


@router.post("/{poll_id}/vote", response_model=schemas.PollResponse)
def vote_poll(
    poll_id: int,
    vote_data: schemas.PollVote,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Voter pour une option d'un sondage"""
    poll = db.query(models.Poll).filter(models.Poll.id == poll_id).first()
    if not poll:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sondage non trouvé"
        )

    # Vérifier si l'option existe
    option = db.query(models.PollOption).filter(
        models.PollOption.id == vote_data.option_id,
        models.PollOption.poll_id == poll_id
    ).first()
    if not option:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Option non trouvée"
        )

    # Vérifier si l'utilisateur a déjà voted
    existing_vote = db.query(models.PollVote).filter(
        models.PollVote.poll_id == poll_id,
        models.PollVote.user_id == current_user.id
    ).first()
    if existing_vote:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Vous avez déjà voted à ce sondage"
        )

    # Enregistrer le vote
    vote = models.PollVote(
        poll_id=poll_id,
        option_id=vote_data.option_id,
        user_id=current_user.id
    )
    db.add(vote)

    # Incrémenter le compteur de l'option
    option.votes += 1

    db.commit()
    db.refresh(poll)

    # Retourner le sondage mis à jour
    options = []
    for opt in poll.options:
        options.append({
            "id": opt.id,
            "text": opt.text,
            "votes": opt.votes
        })

    return {
        "id": poll.id,
        "question": poll.question,
        "options": options,
        "total_votes": calculate_total_votes(db, poll.id),
        "has_voted": True,
        "author_id": poll.author_id,
        "author_name": f"{poll.author.first_name} {poll.author.last_name}" if poll.author else "Inconnu",
        "created_at": poll.created_at
    }


@router.delete("/{poll_id}")
def delete_poll(
    poll_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Supprimer un sondage (auteur uniquement)"""
    poll = db.query(models.Poll).filter(models.Poll.id == poll_id).first()
    if not poll:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sondage non trouvé"
        )

    if poll.author_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vous ne pouvez pas supprimer ce sondage"
        )

    db.delete(poll)
    db.commit()
    return {"message": "Sondage supprimé"}
