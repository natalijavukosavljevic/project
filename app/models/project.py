"""ORM Classes for FASTapi app."""

from datetime import datetime, timezone

from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Table,
    Text,
)
from sqlalchemy.orm import relationship

from app.db.base import Base

# Define association tables outside of models to avoid redefining them


participant_project = Table(
    "participant_project",
    Base.metadata,
    Column(
        "project_id",
        Integer,
        ForeignKey("projects.project_id"),
        primary_key=True,
    ),
    Column("user_id", Integer, ForeignKey("users.user_id"), primary_key=True),
)


class Image(Base):
    """Represents an image in the database.

    Attributes
    ----------
        image_id (int): The primary key of the image.
        s3_key (str): The S3 key for the image.
        image_name (str): The original name of the image file.
        uploaded_at (datetime): The timestamp when the image was uploaded.
        project (Project): Relationship for the one-to-one
        association with a project.

    """

    __tablename__ = "images"

    image_id = Column(Integer, primary_key=True, index=True)
    s3_key = Column(String, nullable=False, unique=True)
    image_name = Column(String, nullable=False)
    uploaded_at = Column(DateTime(timezone=True),
                         default=datetime.now(timezone.utc))

    # Relationship for the one-to-one association with project
    project = relationship("Project", back_populates="logo", uselist=False)


class Project(Base):
    """Represents a project in the database.

    Attributes
    ----------
        project_id (int): The primary key of the project.
        owner_id (int): The foreign key of the project owner (User).
        name (str): The name of the project.
        description (str): The description of the project.
        logo_id (int): The foreign key of the project's logo (Image).
        owner (User): Relationship with the owner of the project.
        logo (Image): Relationship with the logo image of the project.
        documents (List[Document]): Relationship with documents
        associated with the project.
        participants (List[User]): Relationship with users
        participating in the project.

    """

    __tablename__ = "projects"

    project_id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(
        Integer, ForeignKey("users.user_id"), nullable=True,
    )
    name = Column(String(255), nullable=False)
    description = Column(Text)
    logo_id = Column(
        Integer, ForeignKey("images.image_id"), unique=True, nullable=True,
    )

    owner = relationship("User", back_populates="projects")
    logo = relationship("Image", back_populates="project", uselist=False,
                        cascade="all")
    documents = relationship(
        "Document", back_populates="project", cascade="all, delete-orphan",
    )
    participants = relationship(
        "User", secondary="participant_project", back_populates="projects",
        cascade="all",
    )


class User(Base):
    """Represents a user in the database.

    Attributes
    ----------
        user_id (int): The primary key of the user.
        email (str): The email address of the user.
        hashed_password (str): The hashed password of the user.
        projects (List[Project]): Relationship with projects
        associated with the user.

    """

    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), nullable=False, unique=True)
    hashed_password = Column(Text, nullable=False)

    # Relationship for the many-to-many association with projects
    projects = relationship(
        "Project", secondary=participant_project,
        back_populates="participants",
    )


class Document(Base):
    """Represents a document in the database.

    Attributes
    ----------
        document_id (int): The primary key of the document.
        document_name (str): The name of the document.
        content (str): The content of the document.
        projects (List[Project]): Relationship with projects associated
        with the document.

    """

    __tablename__ = "documents"

    document_id = Column(Integer, primary_key=True, index=True)
    document_name = Column(String(255), nullable=False)
    s3_key = Column(String(255), nullable=False)
    project_id = Column(Integer, ForeignKey("projects.project_id"))
    uploaded_at = Column(DateTime(timezone=True),
                         default=datetime.now(timezone.utc))
    # Relationship for the one-to-many association with project
    project = relationship("Project", back_populates="documents")




