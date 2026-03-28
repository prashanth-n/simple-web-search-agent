from __future__ import annotations

from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.auth.security import decode_auth_token
from app.repositories.users import UserRepository
from app.services.auth_service import AuthService
from app.config import get_settings
from app.db.models import User
from app.db.session import get_db


def get_current_user(
    request: Request,
    db: Session = Depends(get_db),
) -> User:
    settings = get_settings()
    auth_token = request.cookies.get(settings.jwt_cookie_name)
    if not auth_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required.")

    payload = decode_auth_token(auth_token)
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required.")

    auth_service = AuthService(UserRepository(db))
    user = auth_service.get_current_user(int(user_id))
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required.")

    return user


def build_auth_cookie_kwargs() -> dict:
    settings = get_settings()
    return {
        "httponly": True,
        "samesite": "lax",
        "secure": settings.cookie_secure,
        "max_age": settings.auth_token_ttl_days * 24 * 60 * 60,
        "path": "/",
    }
