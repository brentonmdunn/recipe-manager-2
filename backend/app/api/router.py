from fastapi import APIRouter

from app.api.v1.auth import router as auth_router
from app.api.v1.categories import router as categories_router
from app.api.v1.recipes import router as recipes_router
from app.api.v1.share_links import router as share_links_router
from app.api.v1.tags import router as tags_router

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(auth_router)
api_router.include_router(recipes_router)
api_router.include_router(share_links_router)
api_router.include_router(tags_router)
api_router.include_router(categories_router)
