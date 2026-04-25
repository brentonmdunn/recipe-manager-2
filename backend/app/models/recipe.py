from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Table, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin

recipe_tags = Table(
    "recipe_tags",
    Base.metadata,
    Column("recipe_id", String, ForeignKey("recipes.id", ondelete="CASCADE")),
    Column("tag_id", String, ForeignKey("tags.id", ondelete="CASCADE")),
)


class Recipe(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "recipes"

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(280), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    prep_time_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    cook_time_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    total_time_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    servings: Mapped[int | None] = mapped_column(Integer, nullable=True)
    servings_unit: Mapped[str | None] = mapped_column(String(50), nullable=True)
    source_url: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    nutrition_info: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_public: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_favorite: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    rating: Mapped[int | None] = mapped_column(Integer, nullable=True)

    user_id: Mapped[str] = mapped_column(
        String, ForeignKey("users.id"), nullable=False
    )
    category_id: Mapped[str | None] = mapped_column(
        String, ForeignKey("categories.id", ondelete="SET NULL"), nullable=True
    )

    user: Mapped["User"] = relationship(back_populates="recipes")  # noqa: F821
    category: Mapped["Category | None"] = relationship(  # noqa: F821
        back_populates="recipes"
    )
    tags: Mapped[list["Tag"]] = relationship(  # noqa: F821
        secondary=recipe_tags, lazy="selectin"
    )
    ingredients: Mapped[list["Ingredient"]] = relationship(  # noqa: F821
        back_populates="recipe",
        cascade="all, delete-orphan",
        order_by="Ingredient.position",
    )
    steps: Mapped[list["RecipeStep"]] = relationship(  # noqa: F821
        back_populates="recipe",
        cascade="all, delete-orphan",
        order_by="RecipeStep.step_number",
    )
    images: Mapped[list["Image"]] = relationship(  # noqa: F821
        back_populates="recipe", cascade="all, delete-orphan"
    )
