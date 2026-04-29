from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db_session
from app.core.security import decode_token
from app.repositories.users import UserRepository

security_required = HTTPBearer()
security_optional = HTTPBearer(auto_error=False)

users_repo = UserRepository()


async def _get_user_from_token(token: str, session: AsyncSession):
    try:
        payload = decode_token(token)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")

    if payload.get("type") != "access":
        raise HTTPException(status_code=401, detail="Invalid token type")

    user_id = int(payload["sub"])
    user = await users_repo.get_by_id(session, user_id)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user


def _extract_token_from_authorization_header(raw: str | None) -> str | None:
    if not raw:
        return None

    parts = raw.split(" ", 1)
    if len(parts) != 2:
        return None

    scheme, token = parts[0].strip(), parts[1].strip()
    if scheme.lower() in {"bearer", "token"} and token:
        return token

    return None


async def get_current_user(
    creds: HTTPAuthorizationCredentials = Depends(security_required),
    session: AsyncSession = Depends(get_db_session),
):
    return await _get_user_from_token(creds.credentials, session)


async def get_optional_user(
    creds: HTTPAuthorizationCredentials | None = Depends(security_optional),
    session: AsyncSession = Depends(get_db_session),
):
    if creds is None:
        return None

    try:
        return await _get_user_from_token(creds.credentials, session)
    except HTTPException:
        return None


async def get_current_user_token(
    request: Request,
    session: AsyncSession = Depends(get_db_session),
):
    token = _extract_token_from_authorization_header(
        request.headers.get("Authorization")
    )
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    return await _get_user_from_token(token, session)


async def get_optional_user_token(
    request: Request,
    session: AsyncSession = Depends(get_db_session),
):
    token = _extract_token_from_authorization_header(
        request.headers.get("Authorization")
    )
    if not token:
        return None

    try:
        return await _get_user_from_token(token, session)
    except HTTPException:
        return None


async def require_admin(user=Depends(get_current_user)):
    if not user.is_admin:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return user