from sqladmin.authentication import AuthenticationBackend
from starlette.requests import Request

from app.core.db import AsyncSessionLocal
from app.core.security import verify_password
from app.repositories.users import UserRepository


class AdminAuth(AuthenticationBackend):
    async def login(self, request: Request) -> bool:
        form = await request.form()
        email = str(form.get("username") or "").strip().lower()  # sqladmin так называет поле
        password = str(form.get("password") or "")

        if not email or not password:
            return False

        async with AsyncSessionLocal() as session:
            repo = UsersRepository()
            user = await repo.get_by_email(session, email)

            if not user:
                return False
            if not getattr(user, "is_admin", False):
                return False
            if not verify_password(password, user.password_hash):
                return False

        request.session["admin_email"] = email
        return True

    async def logout(self, request: Request) -> bool:
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        return bool(request.session.get("admin_email"))