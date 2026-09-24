from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from app.services.image_service import (
    ImageValidationError,
    validate_image,
)
from app.services.vision_service import (
    VisionService,
    VisionServiceError,
)


router = APIRouter(
    prefix="/ai/vision",
    tags=["vision"],
)


@router.post("/analyze")
async def analyze_image(
    image: UploadFile = File(...),
    question: str | None = Form(default=None),
):
    try:
        image_bytes, width, height = validate_image(
            image
        )

        service = VisionService()

        result = service.analyze(
            image_bytes=image_bytes,
            content_type=image.content_type or "",
            question=question,
        )

        if result.image_metadata is None:
            result.image_metadata = {
                "filename": image.filename or "unknown",
                "content_type": (
                    image.content_type or ""
                ),
                "size_bytes": len(image_bytes),
                "width": width,
                "height": height,
            }

        return {
            "success": True,
            "status_code": 200,
            "data": result.model_dump(),
        }

    except ImageValidationError as exc:
        raise HTTPException(
            status_code=400,
            detail={
                "error": str(exc),
                "error_category": "invalid_image",
            },
        ) from exc

    except VisionServiceError as exc:
        raise HTTPException(
            status_code=502,
            detail={
                "error": str(exc),
                "error_category": "vision_service_error",
            },
        ) from exc


@router.post("/compare")
async def compare_images(
    image1: UploadFile = File(...),
    image2: UploadFile = File(...),
):
    try:
        first_bytes, _, _ = validate_image(
            image1
        )

        second_bytes, _, _ = validate_image(
            image2
        )

        service = VisionService()

        result = service.compare(
            first_bytes=first_bytes,
            first_content_type=(
                image1.content_type or ""
            ),
            second_bytes=second_bytes,
            second_content_type=(
                image2.content_type or ""
            ),
        )

        return {
            "success": True,
            "status_code": 200,
            "data": result.model_dump(),
        }

    except ImageValidationError as exc:
        raise HTTPException(
            status_code=400,
            detail={
                "error": str(exc),
                "error_category": "invalid_image",
            },
        ) from exc

    except VisionServiceError as exc:
        raise HTTPException(
            status_code=502,
            detail={
                "error": str(exc),
                "error_category": "vision_service_error",
            },
        ) from exc