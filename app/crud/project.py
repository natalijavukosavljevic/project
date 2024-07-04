"""CRUD operations for projects."""

from __future__ import annotations

from fastapi import HTTPException, Response, UploadFile
from sqlalchemy import event, insert
from sqlalchemy.ext.asyncio import AsyncSession  # noqa: TCH002
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app.core.config import BUCKET_NAME, BUCKET_NAME_LOGOS, BUCKET_RESIZE
from app.db.buckets import delete_from_s3, download_from_s3, upload_to_s3
from app.models.project import (
    Document,
    Image,
    Project,
    User,
    participant_project,
)
from app.schemas.document import DocumentName
from app.schemas.image import LogoOut
from app.schemas.project import DocumentOut, ProjectBase, ProjectBaseUpdate


async def is_participant(
    user_id: int,
    project_id: int,
    session: AsyncSession,
) -> bool:
    """Check if a user is a participant in a project.

    Args:
    ----
        user_id (int): The ID of the user to check.
        project_id (int): The ID of the project to check.
        session (AsyncSession): The asynchronous database session.

    Returns:
    -------
        bool: True if the user is a participant in the project,
              False otherwise.

    """
    participant_query = select(participant_project).where(
        participant_project.c.user_id == user_id,
        participant_project.c.project_id == project_id,
    )
    result = await session.execute(participant_query)
    return result.scalar_one_or_none() is not None


async def create_project(
    db: AsyncSession,
    project: ProjectBase,
    user_obj: User,
) -> Project:
    """Create a new project.

    Args:
    ----
        db (AsyncSession): The asynchronous database session.
        project (ProjectBase): The data model representing the new project.
        user_obj (User): The authenticated user object creating the project.

    Returns:
    -------
        Project: The created project object.

    """
    async with db.begin():
        db_project = Project(
            name=project.name,
            description=project.description,
            owner_id=user_obj.user_id,
        )
        db.add(db_project)

    await db.refresh(db_project)
    return db_project


async def get_project(
    db: AsyncSession,
    project_id: int,
    user_obj: User,
) -> Project:
    """Retrieve project information by project ID.

    Args:
    ----
        db (AsyncSession): The asynchronous database session.
        project_id (int): The ID of the project to retrieve.
        user_obj (User): The authenticated user object.

    Returns:
    -------
        Project: The project object if the user is authorized.

    Raises:
    ------
        HTTPException: If the project is not found or the user
                      is not authorized

    """
    async with db.begin():
        db_project = await db.get(Project, project_id)
        if db_project is None:
            raise HTTPException(status_code=404, detail="Project not found")

        if user_obj.user_id == db_project.owner_id or await is_participant(
            user_obj.user_id,
            project_id,
            db,
        ):
            return db_project

        raise HTTPException(
            status_code=403,
            detail="User is not authorized for this project",
        )


async def update_project(
    db: AsyncSession,
    project_id: int,
    user_obj: User,
    project_data: ProjectBaseUpdate,
) -> Project:
    """Update project information.

    Args:
    ----
        db (AsyncSession): The asynchronous database session.
        project_id (int): The ID of the project to update.
        user_obj (User): The authenticated user object.
        project_data (ProjectBaseUpdate): The updated project data.

    Returns:
    -------
        Project: The updated project object.

    """
    # get_project will check if user is authorized
    db_project = await get_project(db, project_id, user_obj)
    async with db.begin():
        if project_data.name is not None:
            db_project.name = project_data.name
        if project_data.description is not None:
            db_project.description = project_data.description

    await db.refresh(db_project)
    return db_project


async def delete_project(
    db: AsyncSession,
    project_id: int,
    user_obj: User,
) -> dict[str, str]:
    """Delete a project.

    Args:
    ----
        db (AsyncSession): The asynchronous database session.
        project_id (int): The ID of the project to delete.
        user_obj (User): The authenticated user object.

    Returns:
    -------
        dict[str, str]: A message indicating the success of deletion.

    Raises:
    ------
        HTTPException: If the user is not authorized to delete the project.

    """
    # get_project will check if user is authorized
    db_project = await get_project(db, project_id, user_obj)
    async with db.begin():
        if user_obj.user_id == db_project.owner_id:
            await db.delete(db_project)
            return {"message": "Project deleted successfully"}

        raise HTTPException(
            status_code=403,
            detail="User is not authorized for this project",
        )


async def get_projects(db: AsyncSession, user_obj: User) -> list[Project]:
    """Retrieve projects associated with the authenticated user.

    Args:
    ----
        db (AsyncSession): The asynchronous database session.
        user_obj (User): The authenticated user object.

    Returns:
    -------
        List[ProjectOutWithDocuments]: A list of project objects associated
        with the authenticated user.

    Raises:
    ------
        HTTPException: If the user is not authenticated.

    """
    async with db.begin():
        owner_projects_query = (
            select(Project)
            .options(selectinload(Project.documents))
            .where(Project.owner_id == user_obj.user_id)
        )
        owner_results = await db.execute(owner_projects_query)
        owner_projects = owner_results.scalars().all()

        participant_projects_query = (
            select(Project)
            .join(
                participant_project,
                Project.project_id == participant_project.c.project_id,
            )
            .where(participant_project.c.user_id == user_obj.user_id)
            .options(selectinload(Project.documents))
        )
        participant_results = await db.execute(participant_projects_query)
        participant_projects = participant_results.scalars().all()

        user_projects = {
            project.project_id: project
            for project in owner_projects + participant_projects
        }

    return list(user_projects.values())


async def invite(
    db: AsyncSession,
    user_email: str,
    user_obj: User,
    project_id: int,
) -> dict[str, str]:
    """Invite a user to join a project.

    Args:
    ----
        db (AsyncSession): The asynchronous database session.
        user_email (str): The email address of the user to invite.
        user_obj (User): The authenticated user object.
        project_id (int): The ID of the project to invite the user to.

    Returns:
    -------
        dict[str, str]: A message indicating the success of the invitation.

    Raises:
    ------
        HTTPException: If the current user is not the owner of the project
                       or the invited user does not exist.

    """
    current_user_email = user_obj.email
    project = await get_project(db, project_id, user_obj)

    async with db.begin():
        user = await db.execute(
            select(User).filter(User.user_id == project.owner_id),
        )
        owner = user.scalar()

        if owner.email != current_user_email:
            raise HTTPException(
                status_code=403,
                detail="Only the project owner can invite users",
            )

        invited_user_result = await db.execute(
            select(User).filter(User.email == user_email),
        )
        invited_user_obj = invited_user_result.scalar()

        if not invited_user_obj:
            raise HTTPException(
                status_code=404,
                detail="Invited user doesn't exist",
            )

        if await is_participant(invited_user_obj.user_id, project_id, db):
            raise HTTPException(
                status_code=400,
                detail="User is already participating in the project",
            )

        await db.execute(
            insert(participant_project).values(
                project_id=project_id,
                user_id=invited_user_obj.user_id,
            ),
        )

        return {"message": "Participant added to project successfully"}


async def upload_documents(
    db: AsyncSession,
    files: list[UploadFile],
    user_obj: User,
    project_id: int,
) -> list[DocumentName]:
    """Upload multiple documents to a specified project.

    Args:
    ----
        db (AsyncSession): The asynchronous database session.
        files (list[UploadFile]): A list of files to upload.
        user_obj (User): The authenticated user object.
        project_id (int): The ID of the project to upload documents to.

    Returns:
    -------
        list[DocumentOut]: A list of DocumentOut objects representing
                           the uploaded documents.

    Raises:
    ------
        HTTPException: If the project is not found or the user
        is not authorized to upload documents.

    """
    project = await get_project(db, project_id, user_obj)

    async with db.begin():  # Begin a new transaction
        documents_out = []
        for file in files:
            # Check if the document with the same name already exists
            existing_document = await db.execute(
                select(Document).filter_by(
                    document_name=file.filename,
                    project_id=project.project_id,
                ),
            )
            existing_document = existing_document.scalars().first()

            if existing_document:
                # Throw an exception if the document already exists
                raise HTTPException(
                    status_code=400,
                    detail=(
                        f"Document with name '{file.filename}' "
                        f"already exists in the project."
                    ),
                )

            s3_key = await upload_to_s3(
                file,
                BUCKET_NAME,
                s3_key=str(project_id) + "/" + file.filename,
            )
            if not s3_key:
                raise HTTPException(
                    status_code=500,
                    detail="Failed to upload to S3",
                )
            document = Document(
                document_name=file.filename,
                s3_key=s3_key,
                project_id=project.project_id,
            )
            db.add(document)

            documents_out.append(
                DocumentName(
                    document_name=document.document_name,
                ),
            )
        await db.commit()  # Commit the transaction

    return documents_out


async def get_documents(
    db: AsyncSession,
    project_id: int,
    user_obj: User | None = None,
) -> list[Document] | list[DocumentOut]:
    """Retrieve documents associated with a specified project.

    Args:
    ----
        db (AsyncSession): The asynchronous database session.
        user_obj (User): The authenticated user object.
        project_id (int): The ID of the project to retrieve documents from.

    Returns:
    -------
        list[DocumentOut]: A list of DocumentOut objects representing
                           the documents associated with the project.

    """
    async with db.begin():
        result = await db.execute(
            select(Document).where(Document.project_id == project_id),
        )
        documents = result.scalars().all()

    if not user_obj:
        return documents

    #checking autorization
    await get_project(db, project_id, user_obj)

    return [
        DocumentOut(
            document_id=document.document_id,
            document_name=document.document_name,
        )
        for document in documents
    ]


async def get_image(db: AsyncSession, image_id: int) -> Image:
    """Retrieve image information by image ID.

    Args:
    ----
        db (AsyncSession): The asynchronous database session.
        image_id (int): The ID of the image to retrieve.
        user_obj (User): The authenticated user object.

    Returns:
    -------
        Image: The image object if the user is authorized.

    Raises:
    ------
        HTTPException: If the image is not found or the user is not authorized.

    """
    async with db.begin():
        result = await db.execute(
            select(Image).where(Image.image_id == image_id),
        )
        db_image = result.scalars().first()
        if db_image is None:
            raise HTTPException(status_code=404, detail="Image not found")

        return db_image


async def download_logo(
    project_id: int,
    db: AsyncSession,
    user_obj: User,
) -> Response:
    """Download project logo.

    Args:
    ----
        project_id (int): The ID of the project to download the logo from.
        db (AsyncSession): The asynchronous database session.
        user_obj (User): The authenticated user object.

    Returns:
    -------
        Response: The HTTP response containing the downloaded logo.

    Raises:
    ------
        HTTPException: If the project or logo is not found or if there is
                       an issue with downloading the logo.

    """
    #check if user is authorized
    project = await get_project(db, project_id, user_obj)
    logo = await get_image(db, project.logo_id)
    #download resized image
    logo_content = await download_from_s3(BUCKET_RESIZE, logo.s3_key)
    if not logo_content:
        raise HTTPException(
            status_code=500,
            detail="Failed to download logo from S3",
        )

    return Response(
        content=logo_content,
        headers={
            "Content-Disposition": f"attachment;filename={logo.image_name}",
            "Content-Type": "image/jpeg",
        },
    )


async def upload_logo(
    project_id: int,
    file: UploadFile,
    user_obj: User,
    db: AsyncSession,
) -> LogoOut:
    """Upload project logo.

    Args:
    ----
        project_id (int): The ID of the project to upload the logo to.
        file (UploadFile): The file object representing the logo.
        user_obj (User): The authenticated user object.
        db (AsyncSession): The asynchronous database session.

    Returns:
    -------
        LogoOut: The uploaded logo information.

    Raises:
    ------
        HTTPException: If the project is not found or the user is
        not authorized to upload the logo.

    """
    #check if user is authorized
    project = await get_project(db, project_id, user_obj)
    #if logo already exists delete it and then add new one
    try:
        logo = await get_image(db, project.logo_id)
        await delete_logo(project_id, db, user_obj)
    except HTTPException:
        pass

    s3_key = await upload_to_s3(
            file,
            BUCKET_NAME_LOGOS,
            s3_key=str(project_id) + "/" + file.filename,
                doc_type="image",
        )
    if not s3_key:
        raise HTTPException(
            status_code=500,
            detail="Failed to upload logo to S3",
        )

    async with db.begin():

        logo = Image(
            s3_key=s3_key,
            image_name=file.filename,
            project=project,
        )
        db.add(logo)

    return LogoOut(image_id=logo.image_id, image_name=logo.image_name)


async def delete_logo(
    project_id: int,
    db: AsyncSession,
    user_obj: User,
) -> dict[str, str]:
    """Delete project logo.

    Args:
    ----
        project_id (int): The ID of the project to delete the logo from.
        db (AsyncSession): The asynchronous database session.
        user_obj (User): The authenticated user object.

    Returns:
    -------
        dict[str, str]: A message indicating the success of deletion.

    Raises:
    ------
        HTTPException: If the project or logo is not found or if there is
                       an issue with deleting the logo.

    """
    project = await get_project(db, project_id, user_obj)
    logo = await get_image(db, project.logo_id)
    #delete from bucket where are images of orignal size
    #and where images are resized
    success = await delete_from_s3(
            BUCKET_NAME_LOGOS,
            str(project_id) + "/" + logo.image_name,
        )
    success_resize = await delete_from_s3(BUCKET_RESIZE, logo.s3_key)
    if not (success and success_resize):
        raise HTTPException(
            status_code=500,
            detail="Failed to delete logo from S3",
        )
    async with db.begin():
        await db.delete(logo)
    return {"message": "Logo deleted successfully"}


async def delete_images_from_s3(target:Image) -> None:
    """Event listener to delete images associated with a Project from S3 after
    deletion of the Project.

    Args:
    ----
        target (Image): The Image object associated with the Project
          being deleted.

    Notes:
    -----
        This function listens to the 'after_delete' event on the Project model.
        If the Project's
        associated Image has a logo, it deletes the logo from two S3 buckets:
        BUCKET_NAME_LOGOS
        and BUCKET_RESIZE.

    """  # noqa: D205
    if target.logo:
        await delete_from_s3(BUCKET_NAME_LOGOS, target.logo.s3_key)
        await delete_from_s3(BUCKET_RESIZE, target.logo.s3_key)

event.listen(Project, "after_delete", delete_images_from_s3)
