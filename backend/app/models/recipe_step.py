from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, UUIDMixin


class RecipeStep(Base, UUIDMixin):
    __tablename__ = "recipe_steps"

    recipe_id: Mapped[str] = mapped_column(
        String, ForeignKey("recipes.id", ondelete="CASCADE"), nullable=False
    )
    step_number: Mapped[int] = mapped_column(Integer, nullable=False)
    instruction: Mapped[str] = mapped_column(Text, nullable=False)
    image_id: Mapped[str | None] = mapped_column(
        String, ForeignKey("images.id", ondelete="SET NULL"), nullable=True
    )

    recipe: Mapped["Recipe"] = relationship(back_populates="steps")  # noqa: F821
