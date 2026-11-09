from fastapi import HTTPException, status


def validate_file_content(content: bytes) -> str:
    """
    Validate uploaded file bytes and decode them as UTF-8.
    """

    if not content:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is empty."
        )

    # Reject binary content containing null bytes
    if b"\x00" in content:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Binary files are not supported."
        )

    # Validate UTF-8 encoding
    try:
        decoded_content = content.decode("utf-8-sig")

    except UnicodeDecodeError:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="File must use UTF-8 encoding."
        )

    return decoded_content