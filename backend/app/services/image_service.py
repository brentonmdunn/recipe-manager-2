import uuid
from pathlib import Path

from fastapi import HTTPException, UploadFile, status
from PIL import Image as PILImage

from app.config import settings
from app.models.image import Image
from app.repositories.recipe_repository import SqlAlchemyRecipeRepository

ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif"}
MAX_THUMBNAIL_SIZE = (800, 800)


class ImageService:
    def __init__(self, recipe_repo: SqlAlchemyRecipeRepository) -> None:
        self._recipe_repo = recipe_repo

    async def upload_image(
        self,
        recipe_id: str,
        file: UploadFile,
        is_primary: bool = False,
        alt_text: str | None = None,
    ) -> Image:
        recipe = await self._recipe_repo.get_by_id(recipe_id)
        if not recipe:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Recipe not found",
            )

        if file.content_type not in ALLOWED_TYPES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File type not allowed. Allowed: {', '.join(ALLOWED_TYPES)}",
            )

        content = await file.read()
        if len(content) > settings.max_upload_size_mb * 1024 * 1024:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File too large. Max: {settings.max_upload_size_mb}MB",
            )

        file_id = str(uuid.uuid4())
        ext = Path(file.filename).suffix if file.filename else ".jpg"
        relative_path = f"recipes/{recipe_id}/{file_id}{ext}"
        full_path = settings.upload_path / relative_path
        full_path.parent.mkdir(parents=True, exist_ok=True)

        with open(full_path, "wb") as f:
            f.write(content)

        try:
            img = PILImage.open(full_path)
            img.thumbnail(MAX_THUMBNAIL_SIZE)
            thumb_name = f"{file_id}_thumb{ext}"
            thumb_path = (
                settings.upload_path / f"recipes/{recipe_id}/{thumb_name}"
            )
            img.save(thumb_path)
        except Exception:
            pass

        if is_primary:
            for existing_img in recipe.images:
                existing_img.is_primary = False

        image = Image(
            recipe_id=recipe_id,
            file_path=relative_path,
            is_primary=is_primary,
            alt_text=alt_text,
        )

        return await self._recipe_repo.add_image(image)

    async def delete_image(self, image_id: str) -> None:
        image = await self._recipe_repo.delete_image(image_id)
        if not image:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Image not found",
            )

        full_path = settings.upload_path / image.file_path
        if full_path.exists():
            full_path.unlink()

        thumb_path = full_path.with_name(
            full_path.stem + "_thumb" + full_path.suffix
        )
        if thumb_path.exists():
            thumb_path.unlink()
