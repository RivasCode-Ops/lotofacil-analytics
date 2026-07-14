from sqlalchemy import Boolean, Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Draw(Base):
    """Um concurso da Lotofácil (15 dezenas sorteadas de 1 a 25)."""

    __tablename__ = "draws"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    contest: Mapped[int] = mapped_column(Integer, unique=True, index=True)
    draw_date: Mapped[str] = mapped_column(String(10))
    numbers: Mapped[str] = mapped_column(String(64))  # "1,2,3,...,25" ordenado


class SavedGame(Base):
    """Um jogo gerado e anotado pelo usuário ('jogo do dia'), pra conferir
    depois contra o resultado real do concurso alvo."""

    __tablename__ = "saved_games"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    numbers: Mapped[str] = mapped_column(String(64))
    score: Mapped[float] = mapped_column(Float)
    target_contest: Mapped[int] = mapped_column(Integer, index=True)
    created_at: Mapped[str] = mapped_column(String(32))
    checked: Mapped[bool] = mapped_column(Boolean, default=False)
    hits: Mapped[int | None] = mapped_column(Integer, nullable=True)
