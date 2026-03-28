from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.orm import Session

from app.auth.dependencies import build_auth_cookie_kwargs, get_current_user
from app.auth.google import create_google_authorize_url, exchange_google_code
from app.auth.security import create_auth_token
from app.config import get_settings
from app.db.models import User
from app.db.session import get_db
from app.repositories.users import UserRepository
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


class SignUpRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    display_name: str = Field(min_length=1, max_length=150)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


def _serialize_user(user: User) -> dict:
    auth_methods = []
    if user.password_hash:
        auth_methods.append("password")
    if user.google_sub:
        auth_methods.append("google")

    return {
        "id": user.id,
        "email": user.email,
        "display_name": user.display_name,
        "avatar_url": user.avatar_url,
        "auth_methods": auth_methods,
    }


def _set_auth_cookie(response: Response, user: User) -> None:
    settings = get_settings()
    response.set_cookie(
        settings.jwt_cookie_name,
        create_auth_token(user.id),
        **build_auth_cookie_kwargs(),
    )


@router.post("/signup")
def signup(payload: SignUpRequest, response: Response, db: Session = Depends(get_db)) -> dict:
    auth_service = AuthService(UserRepository(db))

    try:
        user = auth_service.signup(
            email=payload.email,
            password=payload.password,
            display_name=payload.display_name,
        )
    except ValueError as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    db.commit()
    db.refresh(user)
    _set_auth_cookie(response, user)
    return {"user": _serialize_user(user)}


@router.post("/login")
def login(payload: LoginRequest, response: Response, db: Session = Depends(get_db)) -> dict:
    auth_service = AuthService(UserRepository(db))
    try:
        user = auth_service.login(email=payload.email, password=payload.password)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc

    _set_auth_cookie(response, user)
    return {"user": _serialize_user(user)}


@router.post("/logout")
def logout(response: Response) -> dict:
    settings = get_settings()
    response.delete_cookie(settings.jwt_cookie_name, path="/")
    response.delete_cookie(settings.google_oauth_state_cookie, path="/")
    return {"status": "ok"}


@router.get("/me")
def me(user: User = Depends(get_current_user)) -> dict:
    return {"user": _serialize_user(user)}


@router.get("/google/login")
def google_login() -> RedirectResponse:
    settings = get_settings()
    if not settings.google_client_id or not settings.google_client_secret or not settings.google_redirect_uri:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Google OAuth is not configured.")

    authorize_url, state = create_google_authorize_url()
    response = RedirectResponse(authorize_url, status_code=status.HTTP_307_TEMPORARY_REDIRECT)
    response.set_cookie(
        settings.google_oauth_state_cookie,
        state,
        httponly=True,
        samesite="lax",
        secure=settings.cookie_secure,
        max_age=600,
        path="/",
    )
    return response


@router.get("/google/callback")
def google_callback(
    code: str,
    state: str,
    request: Request,
    db: Session = Depends(get_db),
):
    settings = get_settings()
    oauth_state = request.cookies.get(settings.google_oauth_state_cookie)
    if not oauth_state or oauth_state != state:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid Google OAuth state.")

    profile = exchange_google_code(code)
    auth_service = AuthService(UserRepository(db))
    user = auth_service.find_or_create_google_user(profile)
    db.commit()
    db.refresh(user)

    response = RedirectResponse(settings.frontend_url, status_code=status.HTTP_307_TEMPORARY_REDIRECT)
    _set_auth_cookie(response, user)
    response.delete_cookie(settings.google_oauth_state_cookie, path="/")
    return response
