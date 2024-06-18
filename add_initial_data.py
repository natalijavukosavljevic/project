import asyncio

from sqlalchemy import select
from sqlalchemy.ext.asyncio import (
    AsyncSession,
)

from main.main import SessionLocal  # Import your SQLAlchemy SessionLocal
from main.models import User  # Import your SQLAlchemy models
from main.utilis import get_hashed_password

# Function to add toy data

async def add_toy_data(db: AsyncSession):
    # Check if data already exists to avoid duplicate entrie

    # Add toy data
    user = User(email="john@example.com",
                hashed_password = get_hashed_password("123443"))

    user = User(email="anne@example.com",
                hashed_password = get_hashed_password("123443"))
    db.add(user)
    await db.commit()

async def main():
    async with SessionLocal() as session:
        await add_toy_data(session)

# Run the async function
asyncio.run(main())
