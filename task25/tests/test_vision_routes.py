from io import BytesIO

from PIL import Image
from fastapi.testclient import TestClient

from app.main import app
from app.services.vision_service import VisionServiceError


client = TestClient(app)


def make_test_image():
    image = Image.new("RGB", (100, 100), "white")
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    buffer.seek(0)
    return buffer


def test_vision_service_error():
    def failing_analyze(*args, **kwargs):
        raise VisionServiceError("test vision failure")

    from app.routes import vision

    original_analyze = vision.VisionService.analyze
    vision.VisionService.analyze = failing_analyze

    try:
        response = client.post(
            "/ai/vision/analyze",
            files={
                "image": (
                    "test.png",
                    make_test_image(),
                    "image/png",
                )
            },
        )

        assert response.status_code == 502

        body = response.json()

        assert body["detail"]["error"] == (
            "test vision failure"
        )

        assert body["detail"]["error_category"] == (
            "vision_service_error"
        )

    finally:
        vision.VisionService.analyze = original_analyze
def test_vision_image_metadata():
    from app.routes import vision

    def fake_analyze(*args, **kwargs):
        from app.models.vision import VisionAnalysis

        return VisionAnalysis(
            summary="Test image",
            visual_elements=[],
            document_analysis=None,
            product_analysis=None,
            ui_analysis=None,
            answer=None,
            uncertainty=[],
            image_metadata=None,
        )

    original_analyze = vision.VisionService.analyze
    vision.VisionService.analyze = fake_analyze

    try:
        response = client.post(
            "/ai/vision/analyze",
            files={
                "image": (
                    "test.png",
                    make_test_image(),
                    "image/png",
                )
            },
        )

        assert response.status_code == 200

        data = response.json()["data"]

        metadata = data["image_metadata"]

        assert metadata["filename"] == "test.png"
        assert metadata["content_type"] == "image/png"
        assert metadata["size_bytes"] > 0
        assert metadata["width"] == 100
        assert metadata["height"] == 100

    finally:
        vision.VisionService.analyze = original_analyze