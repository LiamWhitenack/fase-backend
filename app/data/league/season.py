from sqlalchemy import Column, Float, Integer
from sqlalchemy.orm import Mapped, declarative_base, mapped_column

from app.base import Base


class Season(Base):
    __tablename__ = "seasons"

    # Financial attributes (all nullable)
    id: Mapped[int] = mapped_column(primary_key=True)

    max_salary_cap = Column(Float, nullable=True)
    inflation_adjusted_cap = Column(Float, nullable=True)
    luxury_tax_threshold = Column(Float, nullable=True)
    first_apron = Column(Float, nullable=True)
    second_apron = Column(Float, nullable=True)

    def __repr__(self) -> str:
        return (
            f"<Season(year={self.id}, max_salary_cap={self.max_salary_cap}, "
            f"luxury_tax_threshold={self.luxury_tax_threshold}, "
            f"first_apron={self.first_apron}, second_apron={self.second_apron})>"
        )
