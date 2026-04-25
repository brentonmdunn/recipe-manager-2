import uuid

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin


class ShareLink(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "share_links"

    token: Mapped[str] = mapped_column(
        String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4())
    )
    recipe_id: Mapped[str] = mapped_column(
        String, ForeignKey("recipes.id", ondelete="CASCADE"), nullable=False
    )

    recipe: Mapped["Recipe"] = relationship(back_populates="share_links")  # noqa: F821
