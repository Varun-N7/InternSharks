from io import BytesIO

from fastapi import UploadFile
from PIL import Image

from app.config import settings


ALLOWED_IMAGE_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp",
}


class ImageValidationError(Exception):
    pass


def validate_image(
    image: UploadFile,
) -> tuple[bytes, int, int]:
    if image.content_type not in ALLOWED_IMAGE_TYPES:
        raise ImageValidationError(
            "Unsupported image type"
        )

    content = image.file.read()

    max_size = (
        settings.max_image_size_mb
        * 1024
        * 1024
    )

    if len(content) > max_size:
        raise ImageValidationError(
            "Image exceeds maximum allowed size"
        )

    try:
        with Image.open(BytesIO(content)) as img:
            img.verify()

        with Image.open(BytesIO(content)) as img:
            width, height = img.size

    except Exception as exc:
        raise ImageValidationError(
            "Invalid or corrupted image"
        ) from exc

    return content, width, height