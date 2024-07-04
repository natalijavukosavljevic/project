"""User endpoints."""
from __future__ import annotations

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm  # noqa: TCH002
from sqlalchemy.ext.asyncio import AsyncSession  # noqa: TCH002

from app.crud.user import create_new_user, login_user
from app.db.session import get_db
from app.schemas.token import TokenSchema
from app.schemas.user import UserAuth, UserOut

router = APIRouter()


@router.post("/auth", summary="Create new user", response_model=UserOut)
async def create_user(
    user_data: UserAuth,
    db: AsyncSession = Depends(get_db),  # noqa: B008
) -> UserOut:
    """Create a new user.

    Parameters
    ----------
    user_data : UserAuth
        The user authentication data including email and password.

    db : AsyncSession, optional
        The asynchronous database session (default is obtained from get_db).

    Returns
    -------
    UserOut
        Details of the created user.

    """
    return await create_new_user(db, user_data)


@router.post(
    "/login",
    summary="Create access token for user",
    response_model=TokenSchema,
)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),  # noqa: B008
    db: AsyncSession = Depends(get_db),  # noqa: B008
) -> TokenSchema:
    """Create access and refresh tokens for user login.

    Parameters
    ----------
    form_data : OAuth2PasswordRequestForm, optional
        OAuth2 password request form containing username and password
        (default is obtained from the request body).

    db : AsyncSession, optional
        The asynchronous database session (default is obtained from get_db).

    Returns
    -------
    dict[str, str]
        A dictionary containing access_token and token_type.

    """
    return await login_user(db, form_data)

