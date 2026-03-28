from __future__ import annotations

from app.auth.security import hash_password, verify_password
from app.db.models import User
from app.repositories.users import UserRepository


class AuthService:
    def __init__(self, user_repository: UserRepository) -> None:
        self.user_repository = user_repository

    def signup(self, *, email: str, password: str, display_name: str) -> User:
        existing = self.user_repository.get_by_email(email)
        if existing is not None:
            raise ValueError("Email is already registered.")

        return self.user_repository.create(
            email=email,
            password_hash=hash_password(password),
            display_name=display_name,
            email_verified=False,
        )

    def login(self, *, email: str, password: str) -> User:
        user = self.user_repository.get_by_email(email)
        if user is None or not user.password_hash or not verify_password(password, user.password_hash):
            raise ValueError("Invalid email or password.")
        return user

    def get_current_user(self, user_id: int) -> User | None:
        return self.user_repository.get_by_id(user_id)

    def find_or_create_google_user(self, profile: dict) -> User:
        email = str(profile.get("email", "")).lower()
        if not email:
            raise ValueError("Google account did not provide an email address.")

        google_sub = str(profile.get("sub", "")).strip()
        if not google_sub:
            raise ValueError("Google account did not provide a subject identifier.")

        user = self.user_repository.get_by_google_sub(google_sub)
        if user:
            user.display_name = profile.get("name") or user.display_name
            user.avatar_url = profile.get("picture") or user.avatar_url
            user.email_verified = bool(profile.get("email_verified", True))
            return self.user_repository.save(user)

        user = self.user_repository.get_by_email(email)
        if user:
            user.google_sub = google_sub
            user.display_name = profile.get("name") or user.display_name
            user.avatar_url = profile.get("picture") or user.avatar_url
            user.email_verified = user.email_verified or bool(profile.get("email_verified", True))
            return self.user_repository.save(user)

        display_name = profile.get("name") or email.split("@")[0]
        return self.user_repository.create(
            email=email,
            password_hash=None,
            display_name=display_name,
            google_sub=google_sub,
            avatar_url=profile.get("picture"),
            email_verified=bool(profile.get("email_verified", True)),
        )
