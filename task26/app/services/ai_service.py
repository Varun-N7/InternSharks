import asyncio


class AIServiceError(Exception):
    pass


class AIService:
    async def analyze_document(
        self,
        document_text: str,
    ) -> dict:
        if not document_text.strip():
            raise AIServiceError(
                "Document text cannot be empty"
            )

        # Simulated AI processing.
        await asyncio.sleep(1)

        return {
            "summary": (
                f"Document contains "
                f"{len(document_text.split())} words."
            ),
            "word_count": len(
                document_text.split()
            ),
            "status": "analyzed",
        }