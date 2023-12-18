from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import and_
import models
import logging
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from exception import CustomExceptionsClass
from typing import Union
from sqlalchemy.exc import NoResultFound
from sqlalchemy import func
from geoalchemy2.types import Geography

logger = logging.getLogger(__name__)


# GENERAL
def update(
    db: Session,
    tourist_user: models.TouristUser = None,
    host_user: models.HostUser = None,
    popup_msg: models.HostUser = None,
):
    try:
        if tourist_user:
            tourist_user = db.merge(tourist_user)
        if host_user:
            host_user = db.merge(host_user)
        if popup_msg:
            host_user = db.merge(popup_msg)

        db.commit()
        if tourist_user:
            db.refresh(tourist_user)
        if host_user:
            db.refresh(host_user)
        if popup_msg:
            db.refresh(popup_msg)

    except (IntegrityError, SQLAlchemyError) as e:
        CustomExceptionsClass(db, e).handle()
    return True


# TOURISTS - CRUD
def get_tourist_user(db: Session, user_id: int):
    try:
        return (
            db.query(models.TouristUser)
            .filter(models.TouristUser.id == user_id)
            .first()
        )
    except SQLAlchemyError as e:
        CustomExceptionsClass(db, e).handle()


def get_tourist_user_by_email(db: Session, email: str):
    try:
        return (
            db.query(models.TouristUser)
            .filter(models.TouristUser.email == email)
            .first()
        )
    except SQLAlchemyError as e:
        CustomExceptionsClass(db, e).handle()


def create_tourist_user(db: Session, tourist_user: models.TouristUser):
    try:
        db.add(tourist_user)
        db.commit()
        db.refresh(tourist_user)
    except (IntegrityError, SQLAlchemyError) as e:
        CustomExceptionsClass(db, e).handle()
    return True


def delete_tourist(db: Session, tourist_to_remove: models.TouristUser):
    try:
        db.delete(tourist_to_remove)
        db.commit()
    except SQLAlchemyError as e:
        CustomExceptionsClass(db, e).handle()
    return True


# HOST - CRUD
def get_host_user(db: Session, user_id: int):
    try:
        return db.query(models.HostUser).filter(models.HostUser.id == user_id).first()
    except SQLAlchemyError as e:
        CustomExceptionsClass(db, e).handle()


def get_host_user_by_email(db: Session, email: str):
    try:
        return db.query(models.HostUser).filter(models.HostUser.email == email).first()
    except SQLAlchemyError as e:
        CustomExceptionsClass(db, e).handle()


def create_host_user(db: Session, host_user: models.HostUser):
    try:
        db.add(host_user)
        db.commit()
        db.refresh(host_user)
    except (IntegrityError, SQLAlchemyError) as e:
        CustomExceptionsClass(db, e).handle()
    return True


def delete_host(db: Session, host_to_remove: models.HostUser):
    try:
        db.delete(host_to_remove)
        db.commit()
    except SQLAlchemyError as e:
        CustomExceptionsClass(db, e).handle()
    return True


# EXPERIENCE - CRUD
def get_experience(db: Session, experience_id: int):
    try:
        return (
            db.query(models.Experiences)
            .filter(models.Experiences.id == experience_id)
            .first()
        )
    except NoResultFound:
        raise


def get_experiences(db: Session, cursor: Union[int, None] = None, limit: int = 20):
    try:
        if cursor is None:
            return (
                db.query(models.Experiences)
                .filter(models.Experiences.state_id == 1)
                .order_by(models.Experiences.id)
                .limit(limit + 1)
                .all()
            )
        else:
            return (
                db.query(models.Experiences)
                .filter(models.Experiences.state_id == 1)
                .order_by(models.Experiences.id)
                .offset(cursor)
                .limit(limit + 1)
                .all()
            )
    except SQLAlchemyError as e:
        CustomExceptionsClass(db, e).handle()


def create_experience(db: Session, new_experience: models.Experiences):
    try:
        db.add(new_experience)
        db.commit()
        db.refresh(new_experience)
    except SQLAlchemyError as e:
        CustomExceptionsClass(db, e).handle()
    return True


def delete_experience(db: Session, experience_to_remove: models.Experiences):
    try:
        db.delete(experience_to_remove)
        db.commit()
    except SQLAlchemyError as e:
        CustomExceptionsClass(db, e).handle()
    return True


# DISCOVERY - CRUD
def get_discovery(db: Session, discovery_id: int):
    try:
        return (
            db.query(models.Discovery)
            .filter(models.Discovery.id == discovery_id)
            .first()
        )
    except SQLAlchemyError as e:
        CustomExceptionsClass(db, e).handle()


def get_discoveries(
    db: Session,
    cursor: Union[int, None] = None,
    limit: int = 20,
    category: int = 0,
    all: bool = True,
):
    # Seleziona tutte le categorie
    list_category = [1, 2, 3, 4]
    if not all:
        # Seleziona solo la categoria desiderata
        list_category = [category]

    try:
        if cursor is None:
            return (
                db.query(models.Discovery)
                .filter(
                    and_(
                        models.Discovery.state_id == 1,
                        models.Discovery.kind_id.in_(list_category),
                    )
                )
                .order_by(models.Discovery.id)
                .limit(limit + 1)
                .all()
            )
        else:
            return (
                db.query(models.Discovery)
                .filter(
                    and_(
                        models.Discovery.state_id == 1,
                        models.Discovery.kind_id.in_(list_category),
                    )
                )
                .order_by(models.Discovery.id)
                .offset(cursor)
                .limit(limit + 1)
                .all()
            )
    except SQLAlchemyError as e:
        CustomExceptionsClass(db, e).handle()


def create_discovery(db: Session, new_discovery: models.Discovery):
    try:
        db.add(new_discovery)
        db.commit()
        db.refresh(new_discovery)
    except SQLAlchemyError as e:
        CustomExceptionsClass(db, e).handle()
    return True


def delete_discovery(db: Session, discovery_to_remove: models.Discovery):
    try:
        db.delete(discovery_to_remove)
        db.commit()
    except SQLAlchemyError as e:
        CustomExceptionsClass(db, e).handle()
    return True


def distance_from_discoveries(
    db: Session,
    my_position: str,
):
    try:
        return db.query(
            models.Discovery.id,
            func.ST_Distance(
                models.Discovery.coordinate_gps,
                func.ST_GeomFromText(my_position, type_=Geography),
            ).label("distance"),
        ).all()

    except SQLAlchemyError as e:
        CustomExceptionsClass(db, e).handle()


# CRUD LIKES


def get_like(db: Session, user_id: int, experience_id: int):
    try:
        return (
            db.query(models.TouristUserLikes)
            .filter(
                and_(
                    models.TouristUserLikes.tourist_user_id == user_id,
                    models.TouristUserLikes.experience_id == experience_id,
                )
            )
            .first()
        )
    except SQLAlchemyError as e:
        CustomExceptionsClass(db, e).handle()


def get_likes(db: Session, user_id: int):
    try:
        return (
            db.query(models.TouristUserLikes.experience_id)
            .filter(models.TouristUserLikes.tourist_user_id == user_id)
            .all()
        )
    except SQLAlchemyError as e:
        CustomExceptionsClass(db, e).handle()


def create_like(db: Session, new_like: models.TouristUserLikes):
    try:
        db.add(new_like)
        db.commit()
        db.refresh(new_like)
    except SQLAlchemyError as e:
        CustomExceptionsClass(db, e).handle()
    return True


def delete_like(db: Session, like_to_remove: models.TouristUserLikes):
    try:
        db.delete(like_to_remove)
        db.commit()

    except SQLAlchemyError as e:
        CustomExceptionsClass(db, e).handle()
    return True


# Popup
def get_single_popup(db: Session, popup_id: int):
    try:
        return db.query(models.PopupMsg).filter(models.PopupMsg.id == popup_id).first()
    except SQLAlchemyError as e:
        CustomExceptionsClass(db, e).handle()


def get_popup_msg(db: Session, cursor: Union[int, None] = None, limit: int = 20):
    try:
        if cursor is None:
            return (
                db.query(models.PopupMsg)
                .order_by(models.PopupMsg.id)
                .limit(limit + 1)
                .all()
            )
        else:
            return (
                db.query(models.PopupMsg)
                .order_by(models.PopupMsg.id)
                .offset(cursor)
                .limit(limit + 1)
                .all()
            )
    except SQLAlchemyError as e:
        CustomExceptionsClass(db, e).handle()


def create_popup_msg(db: Session, popup: models.PopupMsg):
    try:
        db.add(popup)
        db.commit()
        db.refresh(popup)

    except SQLAlchemyError as e:
        CustomExceptionsClass(db, e).handle()
    return True


def delete_popup_msg(db: Session, popup_to_delete: models.PopupMsg):
    try:
        db.delete(popup_to_delete)
        db.commit()

    except SQLAlchemyError as e:
        CustomExceptionsClass(db, e).handle()
    return True
