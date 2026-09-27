from datetime import datetime
from typing import Optional, List
from sqlalchemy import String, Integer, Float, ForeignKey, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

class Base(DeclarativeBase):
    pass

class Person(Base):
    __tablename__ = "persons"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    full_name: Mapped[str] = mapped_column(String, index=True)
    country: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    participations: Mapped[List["Participation"]] = relationship(
        "Participation", back_populates="person", cascade="all, delete-orphan"
    )

    __table_args__ = (
        UniqueConstraint("full_name", "country", name="uix_person_name_country"),
    )

class Participation(Base):
    __tablename__ = "participations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    person_id: Mapped[int] = mapped_column(ForeignKey("persons.id"), index=True)
    competition: Mapped[str] = mapped_column(String, index=True)  # IMO, IOI, IMC, ICPC
    year: Mapped[int] = mapped_column(Integer, index=True)
    score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    rank: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    award: Mapped[str] = mapped_column(String, default="Participant") # Gold, Silver, Bronze, Honorable Mention, etc.

    person: Mapped["Person"] = relationship("Person", back_populates="participations")