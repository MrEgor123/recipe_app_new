from pydantic import BaseModel, Field
from fastapi import APIRouter, Depends, status
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db_session


router = APIRouter(prefix="/api/support", tags=["support"])


class SupportRequestCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=150)
    email: str = Field(..., min_length=3, max_length=255)
    message: str = Field(..., min_length=5, max_length=3000)


@router.post("/requests/", status_code=status.HTTP_201_CREATED)
async def create_support_request(
    payload: SupportRequestCreate,
    session: AsyncSession = Depends(get_db_session),
):
    name = payload.name.strip()
    email = payload.email.strip().lower()
    message = payload.message.strip()

    result = await session.execute(
        text("""
            INSERT INTO support_requests (name, email, message, status)
            VALUES (:name, :email, :message, 'new')
            RETURNING id
        """),
        {
            "name": name,
            "email": email,
            "message": message,
        },
    )

    request_id = result.scalar_one()

    await session.commit()

    return {
        "id": request_id,
        "status": "new",
    }