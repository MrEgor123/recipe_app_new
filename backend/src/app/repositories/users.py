from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User


class UserRepository:
    async def get_by_id(self, session: AsyncSession, user_id: int) -> User | None:
        res = await session.execute(select(User).where(User.id == user_id))
        return res.scalars().first()
    
    async def get_by_username(self, session: AsyncSession, username: str) -> User | None:
        res = await session.execute(select(User).where(User.username == username))
        return res.scalars().first()
    
    async def get_by_email(self, session: AsyncSession, email: str) -> User | None:
        res = await session.execute(select(User).where(User.email == email))
        return res.scalars().first()
    
    async def create(
        self, 
        session: AsyncSession, 
        *, 
        email: str, 
        username: str, 
        password_hash: str, 
        first_name: str = "",
        last_name: str = "",
        avatar: str | None = None,
        is_admin: bool = False
    ) -> User:
        user = User(
            email = email, 
            username = username, 
            first_name=first_name,
            last_name=last_name,
            avatar=avatar,
            password_hash = password_hash, 
            is_admin = is_admin
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user

    async def count(self, session: AsyncSession) -> int:
        res = await session.execute(select(func.count(User.id)))
        return int(res.scalar_one())

    async def list(self, session: AsyncSession, *, limit: int, offset: int):
        res = await session.execute(select(User).order_by(User.id.asc()).limit(limit).offset(offset))
        return list(res.scalars().all())

    async def update_password_hash(self, session: AsyncSession, *, user: User, password_hash: str) -> User:
        user.password_hash = password_hash
        await session.commit()
        await session.refresh(user)
        return user

    async def update_avatar(self, session: AsyncSession, *, user: User, avatar: str | None) -> User:
        user.avatar = avatar
        await session.commit()
        await session.refresh(user)
        return user
