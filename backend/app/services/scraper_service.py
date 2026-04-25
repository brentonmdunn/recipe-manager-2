import json
import logging

from fastapi import HTTPException, status
from recipe_scrapers import scrape_html
from slugify import slugify

from app.models.ingredient import Ingredient
from app.models.recipe import Recipe
from app.models.recipe_step import RecipeStep
from app.repositories.recipe_repository import SqlAlchemyRecipeRepository

logger = logging.getLogger(__name__)


def _parse_ingredient(raw: str) -> dict:
    """Parse an ingredient string into components. Falls back to raw string as name."""
    try:
        from ingredient_parser import parse_ingredient

        parsed = parse_ingredient(raw)
        return {
            "name": parsed.name.text if parsed.name else raw,
            "quantity": (
                float(parsed.amount[0].quantity)
                if parsed.amount and parsed.amount[0].quantity
                else None
            ),
            "unit": (
                parsed.amount[0].unit if parsed.amount and parsed.amount[0].unit
                else None
            ),
            "notes": parsed.comment.text if parsed.comment else None,
        }
    except Exception:
        logger.debug("ingredient_parser failed for '%s', using raw string", raw)
        return {"name": raw, "quantity": None, "unit": None, "notes": None}


class ScraperService:
    def __init__(self, recipe_repo: SqlAlchemyRecipeRepository) -> None:
        self._recipe_repo = recipe_repo

    async def _generate_unique_slug(self, title: str) -> str:
        base_slug = slugify(title)
        slug = base_slug
        counter = 1
        while await self._recipe_repo.slug_exists(slug):
            slug = f"{base_slug}-{counter}"
            counter += 1
        return slug

    async def import_from_url(self, url: str, user_id: str) -> Recipe:
        try:
            import httpx

            async with httpx.AsyncClient(
                follow_redirects=True, timeout=15.0
            ) as client:
                response = await client.get(url)
                response.raise_for_status()
                html = response.text

            scraper = scrape_html(html=html, org_url=url)
        except Exception as e:
            logger.error("Failed to scrape %s: %s", url, e)
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Could not scrape recipe from URL: {e}",
            ) from e

        title = scraper.title() or "Imported Recipe"
        slug = await self._generate_unique_slug(title)

        prep_time = _safe_int(scraper.prep_time)
        cook_time = _safe_int(scraper.cook_time)
        total_time = _safe_int(scraper.total_time)
        servings = _safe_int(scraper.yields)

        nutrition = None
        try:
            nutrients = scraper.nutrients()
            if nutrients:
                nutrition = json.dumps(nutrients)
        except Exception:
            pass

        raw_ingredients = []
        try:
            raw_ingredients = scraper.ingredients()
        except Exception:
            pass

        ingredients = []
        for i, raw in enumerate(raw_ingredients):
            parsed = _parse_ingredient(raw)
            ingredients.append(
                Ingredient(
                    name=parsed["name"],
                    quantity=parsed["quantity"],
                    unit=parsed["unit"],
                    notes=parsed["notes"],
                    position=i,
                    recipe_id="temp",
                )
            )

        steps = []
        try:
            instructions = scraper.instructions_list()
            for i, instruction in enumerate(instructions):
                steps.append(
                    RecipeStep(
                        step_number=i + 1,
                        instruction=instruction,
                        recipe_id="temp",
                    )
                )
        except Exception:
            pass

        recipe = Recipe(
            title=title,
            slug=slug,
            description=_safe_str(scraper.description),
            prep_time_minutes=prep_time,
            cook_time_minutes=cook_time,
            total_time_minutes=total_time,
            servings=servings,
            source_url=url,
            nutrition_info=nutrition,
            is_public=True,
            user_id=user_id,
            ingredients=ingredients,
            steps=steps,
        )

        return await self._recipe_repo.create(recipe)


def _safe_int(func) -> int | None:
    try:
        val = func()
        if val is None:
            return None
        s = str(val)
        digits = "".join(c for c in s if c.isdigit())
        return int(digits) if digits else None
    except Exception:
        return None


def _safe_str(func) -> str | None:
    try:
        val = func()
        return str(val) if val else None
    except Exception:
        return None
