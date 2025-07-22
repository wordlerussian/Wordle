from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, Boolean, Integer, BigInteger
from app.database.base import Base

class Game(Base):
    __tablename__ = "games"
    user_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    word: Mapped[str] = mapped_column(String(5))
    lifes: Mapped[int] = mapped_column(Integer)
    infinity: Mapped[bool] = mapped_column(default=False)
    is_playing: Mapped[bool] = mapped_column(default=False)
