from sqlalchemy.sql import select, exists
from sqlalchemy.orm import selectinload
from sqlalchemy.engine.result import Sequence

from werkzeug.security import generate_password_hash, check_password_hash


from ..tables import BaseEngine, User, Gratitude


from typing import Optional


async def register_user(login: str, password: str, first_name: str, last_name: str, email: str) -> bool:
    stmt = select(
        exists(1).
        where(User.login == login)
    )
    async with BaseEngine.async_session() as session:
        async with session.begin():
            result   = await session.execute(stmt)
            is_exist = result.scalar()

            if is_exist:
                return True

            kw = {
                User.first_name.key: first_name,
                User.last_name.key:  last_name,
                User.login.key:      login,
                User.email.key:      email,
                User.password.key:   generate_password_hash(password),
            }
            session.add(User(**kw))
            await session.commit()

    return False

async def get_user_id(login: str, password: str) -> Optional[int]:
    stmt = (
        select(User)
        .where(User.login == login)
    )
    async with BaseEngine.async_session() as db_session:
        async with db_session.begin():
            result = await db_session.execute(stmt)
            user = result.scalar()

    if user is not None and check_password_hash(user.password, password):
        return user.id

async def add_gratitude(
    content:   Optional[str],
    image_url: Optional[str],
    is_public: bool, 
    user_id:   int
) -> None:
    kw = {
        Gratitude.content.key:   content,
        Gratitude.image_url.key: image_url,
        Gratitude.is_public.key: is_public,
        Gratitude.user_id.key:   user_id,
    }
    async with BaseEngine.async_session() as session:
        async with session.begin():
            session.add(Gratitude(**kw))
            await session.commit()

async def get_gratitudes() -> Sequence[Gratitude]:
    async with BaseEngine.async_session() as db_session:
        async with db_session.begin():
            result = await db_session.execute(
                select(Gratitude)
                .filter_by(is_public=True)
                .options(selectinload(Gratitude.user))
                .order_by(Gratitude.created_at.desc()) 
            )
            return result.scalars().all()
