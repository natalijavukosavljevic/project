"""Security utilities."""

from passlib.context import CryptContext

password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_hashed_password(password: str) -> str:
    """Hashes a plain text password."""
    return password_context.hash(password)


def verify_password(password: str, hashed_pass: str) -> bool:
    """Verify a plain text password against a hashed password."""
    return password_context.verify(password, hashed_pass)
