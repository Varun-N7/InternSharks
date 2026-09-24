from io import BytesIO

from fastapi import UploadFile
from PIL import Image
from starlette.datastructures import Headers

from app.services.image_service import (
    ImageValidationError,
    validate_image,
)


def make_image() -> BytesIO:
    image = Image.new(
        "RGB",
        (100, 100),
        "white",
    )

    buffer = BytesIO()

    image.save(
        buffer,
        format="PNG",
    )

    buffer.seek(0)

    return buffer


def test_valid_image():
    upload = UploadFile(
        filename="test.png",
        file=make_image(),
        headers=Headers(
            {
                "content-type": "image/png",
            }
        ),
    )

    content, width, height = validate_image(
        upload
    )

    assert len(content) > 0
    assert width == 100
    assert height == 100


def test_invalid_content_type():
    upload = UploadFile(
        filename="test.txt",
        file=BytesIO(b"not an image"),
        headers=Headers(
            {
                "content-type": "text/plain",
            }
        ),
    )

    try:
        validate_image(upload)
        assert False
    except ImageValidationError as exc:
        assert "Unsupported image type" in str(exc)