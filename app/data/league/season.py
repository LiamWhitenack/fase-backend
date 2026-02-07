from sqlalchemy import Column, Float, Integer
from sqlalchemy.orm import Mapped, declarative_base, mapped_column

from app.base import Base


class Season(Base):
    __tablename__ = "seasons"

    # Financial attributes (all nullable)
    id: Mapped[int] = mapped_column(primary_key=True)

    max_salary_cap: Mapped[int | None] = mapped_column(Integer, nullable=True)
    inflation_adjusted_cap: Mapped[int | None] = mapped_column(Integer, nullable=True)
    luxury_tax_threshold: Mapped[int | None] = mapped_column(Integer, nullable=True)
    first_apron: Mapped[int | None] = mapped_column(Integer, nullable=True)
    second_apron: Mapped[int | None] = mapped_column(Integer, nullable=True)
    expected_cap: Mapped[int | None] = mapped_column(Integer, nullable=True)

    def __repr__(self) -> str:
        return (
            f"<Season(year={self.id}, max_salary_cap={self.max_salary_cap}, "
            f"luxury_tax_threshold={self.luxury_tax_threshold}, "
            f"first_apron={self.first_apron}, second_apron={self.second_apron})>"
        )

    @property
    def cap(self) -> int:
        if self.max_salary_cap:
            return self.max_salary_cap
        elif self.expected_cap:
            return self.expected_cap
        raise Exception(f"No cap data for {self.__repr__()}")
