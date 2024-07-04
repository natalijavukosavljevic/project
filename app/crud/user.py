"""CRUD operations for users."""

from fastapi import Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.core.jwt import create_access_token
from app.core.security import get_hashed_password, verify_password
from app.db.session import get_db
from app.models.project import User
from app.schemas.token import TokenSchema
from app.schemas.user import UserAuth, UserOut


def request_user(request: Request) -> str:
    """Retrieve the authenticated user's sub (subject) from the request state.

    Parameters
    ----------
    request : Request
        The incoming request object.

    Returns
    -------
    str
        The user's sub (subject) identifier.

    Raises
    ------
    HTTPException
        If user authentication fails (user not authenticated).

    """
    user = request.state.user
    if not user:
        raise HTTPException(status_code=401, detail="User not authenticated")

    return user.get("sub")


async def get_authenticated_user(
    request: Request,
    db: AsyncSession = Depends(get_db),  # noqa: B008
) -> User:
    """Retrieve the authenticated user object from the database.

    Parameters
    ----------
    request : Request
        The incoming request object.

    db : AsyncSession, optional
        The asynchronous database session (default is obtained from get_db).

    Returns
    -------
    User
        The authenticated user object fetched from the database.

    Raises
    ------
    HTTPException
        If the authenticated user is not found in the database.

    """
    async with db.begin():
        # Start transaction
        user_email = request_user(request=request)

        # Query the user from the database
        user_db = await db.execute(
            select(User).where(User.email == user_email),
        )
        user_obj = user_db.scalars().first()

        if not user_obj:
            raise HTTPException(status_code=404, detail="User not found")

    return user_obj


async def create_new_user(
    db: AsyncSession, user_data: UserAuth,
) -> UserOut:
    """Create a new user in the database.

    Parameters
    ----------
    db : AsyncSession
        The asynchronous database session.

    user_data : UserAuth
        The user authentication data including email and password.

    Returns
    -------
    UserOut
        Details of the newly created user.

    Raises
    ------
    HTTPException
        If a user with the same email already exists or passwords do not match.

    """
    async with db.begin():
        # Check if user already exists
        result = await db.execute(
            select(User).where(User.email == user_data.email),
        )
        existing_user = result.scalars().first()
        if existing_user:
            raise HTTPException(
                status_code=400,
                detail="User with this email already exists",
            )

        # Check if passwords match
        if user_data.password != user_data.repeat_password:
            raise HTTPException(
                status_code=400,
                detail="Passwords do not match",
            )

        # Create new user
        hashed_password = get_hashed_password(user_data.password)
        new_user = User(
            email=user_data.email,
            hashed_password=hashed_password,
        )
        db.add(new_user)

    await db.refresh(new_user)

    # Return the newly created user details
    return {
        "user_id": new_user.user_id,
        "email": new_user.email,
    }



async def login_user(
    db: AsyncSession, form_data: OAuth2PasswordRequestForm,
) -> TokenSchema:
    """Log in user and generate access and refresh tokens.

    Args:
    ----
        form_data (OAuth2PasswordRequestForm): Form data
        containing the username (email) and password.
        db (AsyncSession): The asynchronous database session.

    Returns:
    -------
        dict[str, str]: A dictionary containing the access_token.

    Raises:
    ------
        HTTPException: If the provided email or password is incorrect.

    """
    async with db.begin():
        # Query the user from the database
        result = await db.execute(
            select(User).where(User.email == form_data.username),
        )
        user = result.scalars().first()

        # Check if user exists and password is correct
        if user is None or not verify_password(
            form_data.password,
            user.hashed_password,
        ):
            raise HTTPException(
                status_code=400,
                detail="Incorrect email or password",
            )

        # Create tokens
        access_token = create_access_token(user.email)

        return {
            "access_token": access_token,
        }
