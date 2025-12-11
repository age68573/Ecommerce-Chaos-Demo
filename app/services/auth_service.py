from typing import Optional

from werkzeug.security import generate_password_hash, check_password_hash

from app.database import db
from app.models.user import User


def create_user(username: str, email: str, password: str, is_admin: bool = False) -> User:
    user = User(
        username=username,
        email=email,
        password_hash=generate_password_hash(password),
        is_admin=is_admin,
    )
    db.session.add(user)
    db.session.commit()
    return user


def authenticate(username_or_email: str, password: str) -> Optional[User]:
    q = User.query.filter(
        (User.username == username_or_email) | (User.email == username_or_email)
    )
    user = q.first()
    if user and check_password_hash(user.password_hash, password):
        return user
    return None
