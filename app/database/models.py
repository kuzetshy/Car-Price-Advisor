from datetime import datetime
from sqlalchemy import BigInteger, Integer, String, Text, DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class Base(DeclarativeBase):
    """Базовый класс для всех моделей базы данных"""
    pass

class CarModel(Base):
    __tablename__ = "cars"

    # Используем BigInteger для ID, так как ID объявлений могут быть очень большими
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    brand: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    model_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    details: Mapped[str | None] = mapped_column(Text, nullable=True)
    price: Mapped[int] = mapped_column(Integer, nullable=False)
    year: Mapped[int | None] = mapped_column(Integer, nullable=True)
    mileage: Mapped[int | None] = mapped_column(Integer, nullable=True)
    fuel: Mapped[str | None] = mapped_column(String(30), nullable=True)
    gearbox: Mapped[str | None] = mapped_column(String(30), nullable=True)
    power: Mapped[int | None] = mapped_column(Integer, nullable=True)  # Мощность в кВт
    url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    
    # server_default=func.now() заставляет сам Postgres выставлять время при вставке
    parsed_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    def __repr__(self) -> str:
        return f"<Car {self.brand} {self.model_name} - {self.price} CZK>"