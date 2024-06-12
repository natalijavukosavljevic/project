"""ORM Clases for FASTapi app."""

from sqlalchemy import (
    Column,
    ForeignKey,
    Integer,
    LargeBinary,
    String,
    Table,
    Text,
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

# Define association tables outside of models to avoid redefining them
project_documents = Table(
    "project_documents",
    Base.metadata,
    Column(
        "project_id",
        Integer,
        ForeignKey("projects.project_id"),
        primary_key=True,
    ),
    Column(
        "document_id",
        Integer,
        ForeignKey("documents.document_id"),
        primary_key=True,
    ),
)

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
        image_data (bytes): The binary data of the image.
        project (Project): Relationship for the one-to-one
        association with a project.

    """

    __tablename__ = "images"

    image_id = Column(Integer, primary_key=True, index=True)
    image_data = Column(LargeBinary, nullable=False)

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
    )  # temporaly
    name = Column(String(255), nullable=False)
    description = Column(Text)
    logo_id = Column(
        Integer, ForeignKey("images.image_id"), unique=True, nullable=True,
    )

    owner = relationship("User", back_populates="projects")
    logo = relationship("Image", back_populates="project", uselist=False)
    documents = relationship(
        "Document", secondary=project_documents, back_populates="projects",
    )
    participants = relationship(
        "User", secondary=participant_project, back_populates="projects",
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
    content = Column(Text)

    # Relationship for the many-to-many association with projects
    projects = relationship(
        "Project", secondary=project_documents, back_populates="documents",
    )
