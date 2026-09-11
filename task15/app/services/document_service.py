from app.utils.file_parser import extract_text_from_file
from app.services.summarizer_service import summarize_text


def summarize_document(file_content, filename, summary_type):

    text = extract_text_from_file(
        file_content,
        filename,
    )

    result = summarize_text(
        text,
        summary_type,
    )

    return result