from fastapi import APIRouter

from app.dependencies import AuthServiceDep, CurrentUser, SessionDep
from app.schemas.auth import (
    LoginRequest,
    RefreshRequest,
    RegisterRequest,
    TokenResponse,
)
from app.schemas.user import UserResponse

router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/setup-status")
async def setup_status(auth_service: AuthServiceDep) -> dict:
    needs_setup = await auth_service.needs_setup()
    return {"needs_setup": needs_setup}


@router.post("/register", response_model=UserResponse, status_code=201)
async def register(
    data: RegisterRequest,
    auth_service: AuthServiceDep,
    session: SessionDep,
) -> UserResponse:
    user = await auth_service.register(data)
    await session.commit()
    return UserResponse.model_validate(user)


@router.post("/login", response_model=TokenResponse)
async def login(
    data: LoginRequest,
    auth_service: AuthServiceDep,
) -> TokenResponse:
    return await auth_service.login(data)


@router.post("/refresh", response_model=TokenResponse)
async def refresh(
    data: RefreshRequest,
    auth_service: AuthServiceDep,
) -> TokenResponse:
    return await auth_service.refresh(data.refresh_token)


@router.get("/me", response_model=UserResponse)
async def me(current_user: CurrentUser) -> UserResponse:
    return UserResponse.model_validate(current_user)
