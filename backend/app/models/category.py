from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, UUIDMixin


class Category(Base, UUIDMixin):
    __tablename__ = "categories"

    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    slug: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)

    recipes: Mapped[list["Recipe"]] = relationship(  # noqa: F821
        back_populates="category"
    )
