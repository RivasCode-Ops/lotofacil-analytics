from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Draw(Base):
    """Um concurso da Lotofácil (15 dezenas sorteadas de 1 a 25)."""

    __tablename__ = "draws"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    contest: Mapped[int] = mapped_column(Integer, unique=True, index=True)
    draw_date: Mapped[str] = mapped_column(String(10))
    numbers: Mapped[str] = mapped_column(String(64))  # "1,2,3,...,25" ordenado
