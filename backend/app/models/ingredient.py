from sqlalchemy import Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, UUIDMixin


class Ingredient(Base, UUIDMixin):
    __tablename__ = "ingredients"

    recipe_id: Mapped[str] = mapped_column(
        String, ForeignKey("recipes.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    quantity: Mapped[float | None] = mapped_column(Float, nullable=True)
    unit: Mapped[str | None] = mapped_column(String(50), nullable=True)
    notes: Mapped[str | None] = mapped_column(String(255), nullable=True)
    group_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    position: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    recipe: Mapped["Recipe"] = relationship(back_populates="ingredients")  # noqa: F821
