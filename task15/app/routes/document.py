from fastapi import APIRouter
from fastapi import File, Form, UploadFile
from fastapi import HTTPException

from app.services.document_service import summarize_document


router = APIRouter(
    prefix="/ai",
    tags=["AI"],
)


@router.post("/summarize-document")
async def summarize_document_route(
    file: UploadFile = File(...),
    summary_type: str = Form(...),
):

    if summary_type not in ["brief", "detailed", "bullet_points"]:
        raise HTTPException(
            status_code=422,
            detail="Invalid summary type",
        )

    try:
        file_content = await file.read()

        result = summarize_document(
            file_content,
            file.filename,
            summary_type,
        )

        return {
            "success": True,
            "status_code": 200,
            "data": {
                "file_name": file.filename,
                "summary_type": summary_type,
                "summary": result["summary"],
                "main_topic": result["main_topic"],
                "keywords": result["keywords"],
            },
        }

    except ValueError as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc),
        )

    except Exception:
        raise HTTPException(
            status_code=502,
            detail="Document summarization failed",
        )