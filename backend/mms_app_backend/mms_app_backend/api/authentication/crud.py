from sqlalchemy.orm import Session

from .helpers import get_password_hash
from .models import User
from .schemas import UserCreate
from ..account_management.models import Mentor, MentorManager


def create_user(db: Session, user: UserCreate):
    hashed_password = get_password_hash(user.password)
    db_user = User(email=user.email, hashed_password=hashed_password, username=user.username,
                   first_name=user.first_name, last_name=user.last_name)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()


def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()

def change_password_crud(db: Session,user,new_password):
    user.hashed_password = get_password_hash(new_password)
    db.commit()
    db.refresh(user)
    return True

def get_mentor(db: Session, mentor_id: int):
    return db.query(Mentor).filter(Mentor.id == mentor_id).first()

def get_mentor_manager(db: Session, mentor_manager_id: int):
    return db.query(MentorManager).filter(MentorManager.id == mentor_manager_id).first()
