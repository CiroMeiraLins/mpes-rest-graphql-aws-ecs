import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Integer, Boolean, Numeric, Text, DateTime
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY

from db import Base  # mesmo Base usado no create_all do app.py


class Registro(Base):
    __tablename__ = "registros"
    __table_args__ = {"schema": "api_experimento"}

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    nome: Mapped[str | None] = mapped_column(String(100))
    email: Mapped[str | None] = mapped_column(String(150))
    idade: Mapped[int | None] = mapped_column(Integer)
    ativo: Mapped[bool | None] = mapped_column(Boolean)

    criado_em: Mapped[datetime | None] = mapped_column(DateTime, default=datetime.utcnow)
    atualizado_em: Mapped[datetime | None] = mapped_column(DateTime)

    salario: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))
    score_credito: Mapped[Decimal | None] = mapped_column(Numeric(5, 2))

    endereco: Mapped[dict | None] = mapped_column(JSONB)
    preferencias: Mapped[dict | None] = mapped_column(JSONB)

    descricao: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str | None] = mapped_column(String(20))

    tags: Mapped[list[str] | None] = mapped_column(ARRAY(String))

    empresa_id: Mapped[int | None] = mapped_column(Integer)

    latitude: Mapped[Decimal | None] = mapped_column(Numeric(9, 6))
    longitude: Mapped[Decimal | None] = mapped_column(Numeric(9, 6))
