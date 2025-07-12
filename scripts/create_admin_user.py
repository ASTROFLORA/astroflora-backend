import asyncio
from src.db.database import async_session
from src.models.users import User
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def create_user():
    async with async_session() as session:
        user = User(
            username="tester",
            hashed_password=pwd_context.hash("tester123")
        )
        session.add(user)
        await session.commit()
        print("Usuario creado: tester / tester123")

asyncio.run(create_user())
