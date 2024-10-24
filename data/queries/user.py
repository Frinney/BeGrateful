from sqlalchemy.sql import select, exists
from sqlalchemy.orm import selectinload
from sqlalchemy.engine.result import Sequence

from werkzeug.security import generate_password_hash, check_password_hash


from ..tables import BaseEngine, User, Gratitude, Friendship


from typing   import Optional
from datetime import datetime, timedelta


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
    is_friend: bool, 
    user_id:   int
) -> None:
    kw = {
        Gratitude.content.key:   content,
        Gratitude.image_url.key: image_url,
        Gratitude.is_public.key: is_public,
        Gratitude.is_friend.key: is_friend,
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

async def get_todays_gratitudes(user_id: int) -> Optional[tuple[Sequence[Gratitude], User]]:
    async with BaseEngine.async_session() as db_session:
        user_result = await db_session.execute(
            select(User)
            .filter_by(id=user_id)
        )
        user = user_result.scalar()

        if user is None:
            return None

        # Получаем начало и конец текущего дня
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        tomorrow = today + timedelta(days=1)

        # Выбираем и сортируем подяки по убыванию даты
        gratitude_entries = await db_session.execute(
            select(Gratitude)
            .filter_by(user_id=user_id)
            .filter(Gratitude.created_at >= today)
            .filter(Gratitude.created_at < tomorrow)
            .order_by(Gratitude.created_at.desc())  # Сортируем по убыванию
        )
        return gratitude_entries.scalars().all(), user




async def get_gratitudes_by_method(method: str, current_user_id: int, user_id: int) -> tuple[User, Sequence[Gratitude], str | None] | str:
    async with BaseEngine.async_session() as db_session:
        user = await db_session.execute(
            select(User)
            .filter_by(id = user_id)
        )
        user = user.scalar()

        if user is None:
            return 'Користувача не знайдено!'

        gratitudes = await db_session.execute(
            select(Gratitude)
            .options(
                selectinload(Gratitude.user)
            )
            .filter_by(user_id = user_id)
        )
        gratitudes = gratitudes.scalars().all()

        info = None
        if method != 'POST':
            return user, gratitudes, info

        if current_user_id == user.id:
            info = 'Ви не можете додати себе в друзі!'
            return user, gratitudes, info

        existing_friendship = await db_session.execute(
            select(Friendship)
            .filter_by(
                user_id = current_user_id, 
                friend_user_id = user.id
            )
        )
        if existing_friendship.scalar():
            info = 'Користувач вже є у вашому списку друзів!'
        else:
            new_friendship = Friendship(user_id = current_user_id, friend_user_id=user.id)
            db_session.add(new_friendship)
            await db_session.commit()

            info = 'Користувача додано до друзів!'

        return user, gratitudes, info

async def get_search_users(query: str) -> Sequence[User]:
    async with BaseEngine.async_session() as db_session:
        results = await db_session.execute(
            select(User).filter(User.login.ilike(f'%{query}%'))
        )
        return results.scalars().all()
    
async def get_gratitudes_by_user_id(user_id: int) -> Sequence[Gratitude]:
    async with BaseEngine.async_session() as db_session:
        friendships = await db_session.execute(
            select(Friendship)
            .filter_by(user_id=user_id)
        )
        friend_ids = [
            friendship.friend_user_id 
            for friendship in friendships.scalars().all()
        ]

        result = await db_session.execute(
            select(Gratitude)
            .filter(Gratitude.user_id.in_(friend_ids))
            .filter(Gratitude.is_public == True)
            .options(selectinload(Gratitude.user))
            .order_by(Gratitude.created_at.desc())
        )
        return result.scalars().all()

async def get_todays_gratitudes_by_user_id(user_id: int, selected_date: datetime) -> Sequence[Gratitude]:
    async with BaseEngine.async_session() as db_session:

        gratitude_entries = await db_session.execute(
            select(Gratitude).filter_by(user_id=user_id).filter(
                Gratitude.created_at >= selected_date,
                Gratitude.created_at < selected_date + timedelta(days=1) 
            )
        )
        return gratitude_entries.scalars().all()