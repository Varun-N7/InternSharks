from fastapi import APIRouter, File, UploadFile
from fastapi.responses import JSONResponse

from app.models.rag import (
    RAGAskRequest,
    RAGAskResponse,
    RAGDocumentResponse,
    RAGUploadResponse,
)
from app.services.ai_service import (
    AIServiceError,
    InvalidAPIKeyError,
    RateLimitError,
)
from app.services.rag_service import (
    ask_question,
    get_document,
    upload_document,
)


router = APIRouter(prefix="/rag", tags=["RAG"])


@router.post(
    "/documents",
    response_model=RAGUploadResponse,
)
async def upload_rag_document(
    file: UploadFile = File(...),
):
    try:
        file_name = file.filename or ""
        file_content = await file.read()

        data = upload_document(
            file_name=file_name,
            file_content=file_content,
        )

        return {
            "success": True,
            "status_code": 201,
            "data": data,
        }

    except ValueError as error:
        return JSONResponse(
            status_code=400,
            content={
                "success": False,
                "status_code": 400,
                "message": str(error),
            },
        )

    except Exception:
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "status_code": 500,
                "message": "Document processing failed",
            },
        )


@router.post(
    "/ask",
    response_model=RAGAskResponse,
)
async def ask_rag_question(request: RAGAskRequest):
    try:
        question = request.question.strip()
        document_id = request.document_id.strip()

        if not question:
            return JSONResponse(
                status_code=400,
                content={
                    "success": False,
                    "status_code": 400,
                    "message": "Question cannot be empty",
                },
            )

        if not document_id:
            return JSONResponse(
                status_code=400,
                content={
                    "success": False,
                    "status_code": 400,
                    "message": "Document ID cannot be empty",
                },
            )

        data = ask_question(
            document_id=document_id,
            question=question,
            top_k=request.top_k,
        )

        return {
            "success": True,
            "status_code": 200,
            "data": data,
        }

    except ValueError as error:
        return JSONResponse(
            status_code=404,
            content={
                "success": False,
                "status_code": 404,
                "message": str(error),
            },
        )

    except InvalidAPIKeyError as error:
        return JSONResponse(
            status_code=401,
            content={
                "success": False,
                "status_code": 401,
                "message": str(error),
            },
        )

    except RateLimitError as error:
        return JSONResponse(
            status_code=429,
            content={
                "success": False,
                "status_code": 429,
                "message": str(error),
            },
        )

    except AIServiceError as error:
        return JSONResponse(
            status_code=502,
            content={
                "success": False,
                "status_code": 502,
                "message": str(error),
            },
        )

    except Exception:
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "status_code": 500,
                "message": "Unable to process the question",
            },
        )


@router.get(
    "/documents/{document_id}",
    response_model=RAGDocumentResponse,
)
async def get_rag_document(document_id: str):
    try:
        document_id = document_id.strip()

        if not document_id:
            return JSONResponse(
                status_code=400,
                content={
                    "success": False,
                    "status_code": 400,
                    "message": "Document ID cannot be empty",
                },
            )

        data = get_document(document_id)

        return {
            "success": True,
            "status_code": 200,
            "data": data,
        }

    except ValueError as error:
        return JSONResponse(
            status_code=404,
            content={
                "success": False,
                "status_code": 404,
                "message": str(error),
            },
        )

    except Exception:
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "status_code": 500,
                "message": "Unable to retrieve document",
            },
        )