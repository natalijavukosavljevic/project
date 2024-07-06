"""Module provides functions to interact with AWS S3, including uploading,
deleting, and downloading files.

It uses the boto3 library to interface with S3 and FastAPI's UploadFile for
handling file uploads in an asynchronous context.
"""  # noqa: D205


from __future__ import annotations

import boto3
from fastapi import UploadFile  # noqa: TCH002

s3_client = boto3.client(
    "s3",
)


async def upload_to_s3(
    file: UploadFile,
    bucket_name: str,
    s3_key: str | None = None,
    doc_type: str | None = None,
) -> str | None:
    """Upload a file to an S3 bucket.

    Args:
    ----
        file (UploadFile): The file to upload.
        bucket_name (str): The name of the S3 bucket.
        s3_key (str, optional): The key of the object in the S3 bucket.
            If not specified, defaults to the file's filename.
        doc_type (str, optional): The type of document.
            If specified as "image", a "-resized.jpg" suffix will be appended
            to the s3_key.

    Returns:
    -------
        str | None: The key of the uploaded object if successful,
        otherwise None.

    """
    if s3_key is None:
        s3_key = file.filename

    try:
        s3_client.upload_fileobj(file.file, bucket_name, s3_key)
    except:  # noqa: E722
        return None

    if doc_type == "image":
        return s3_key.split(".")[0] + "-resized.jpg"

    return s3_key



async def delete_from_s3(bucket_name: str, s3_key: str) -> bool:
    """Delete an object from an S3 bucket.

    Args:
    ----
        bucket_name (str): The name of the S3 bucket.
        s3_key (str): The key of the object to delete.

    Returns:
    -------
        bool: True if the object was deleted successfully, otherwise False.

    """
    try:
        s3_client.delete_object(Bucket=bucket_name, Key=s3_key)
    except:  # noqa: E722
        return False

    return True



async def download_from_s3(bucket_name: str, s3_key: str) -> bytes | None:
    """Download an object from an S3 bucket.

    Args:
    ----
        bucket_name (str): The name of the S3 bucket.
        s3_key (str): The key of the object to download.

    Returns:
    -------
        bytes | None: The content of the object if successful, otherwise None.

    """
    try:
        response = s3_client.get_object(Bucket=bucket_name, Key=s3_key)
        content = response["Body"].read()
    except:  # noqa: E722
        return None

    return content

