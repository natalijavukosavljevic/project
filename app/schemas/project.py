"""Project schemas."""
from __future__ import annotations

from typing import Optional

from pydantic import BaseModel

from app.schemas.document import DocumentOut  # noqa: TCH001


class ProjectBase(BaseModel):
    """Base model for project data.

    Attributes
    ----------
    name : str
        The name of the project.
    description : str
        The description of the project.

    """

    name: str
    description: str

    class Config:
        """Configuration for Pydantic BaseModel.

        orm_mode (bool): Whether to interpret and return all
        fields in ORM mode, which allows accessing model attributes
        and database columns directly.
        """

        orm_mode = True


class ProjectBaseUpdate(BaseModel):
    """Model for updating project data.

    Attributes
    ----------
    name : Optional[str], optional
        The new name of the project, by default None.
    description : Optional[str], optional
        The new description of the project, by default None.

    """

    name: Optional[str] = None  # noqa: UP007
    description: Optional[str] = None  # noqa: UP007

    class Config:
        """Configuration for Pydantic BaseModel.

        orm_mode (bool): Whether to interpret and return all
        fields in ORM mode, which allows accessing model attributes
        and database columns directly.
        """

        orm_mode = True


class ProjectOut(BaseModel):
    """Output model for project data.

    Attributes
    ----------
    project_id : int
        The unique identifier of the project.
    name : str
        The name of the project.
    description : str
        The description of the project.
    owner_id : int
        The identifier of the project owner.
    logo_id : Optional[int], optional
        The identifier of the project's logo, if any.

    """

    project_id: int
    name: str
    description: str
    owner_id: int
    logo_id: Optional[int]  # noqa: UP007

    class Config:
        """Configuration for Pydantic BaseModel.

        orm_mode (bool): Whether to interpret and return all
        fields in ORM mode, which allows accessing model attributes
        and database columns directly.
        """

        orm_mode = True


class ProjectOutWithDocuments(BaseModel):
    """Output model for project data including associated documents.

    Attributes
    ----------
    project_id : int
        The unique identifier of the project.
    owner_id : int
        The identifier of the project owner.
    name : str
        The name of the project.
    description : str
        The description of the project.
    logo_id : Optional[int], optional
        The identifier of the project's logo, if any.
    documents : List[DocumentOut], optional
        List of documents associated with the project.

    """

    project_id: int
    owner_id: int
    name: str
    description: str
    logo_id: Optional[int]    # noqa: UP007
    documents: list[DocumentOut] = []

    class Config:
        """Configuration for Pydantic BaseModel.

        orm_mode (bool): Whether to interpret and return all
        fields in ORM mode, which allows accessing model attributes
        and database columns directly.
        """

        orm_mode = True


class ResponseMessage(BaseModel):
    """Model for response messages.

    Attributes
    ----------
    message : str
        The message content.

    """

    message: str
