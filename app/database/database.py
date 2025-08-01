from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from app.database.models import Base
from dotenv import load_dotenv
import os
load_dotenv()

engine = create_async_engine(os.getenv("DATABASE_URL"), echo=False)
async_session = async_sessionmaker(engine, expire_on_commit=False)

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
