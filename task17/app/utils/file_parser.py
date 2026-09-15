from io import BytesIO

from pypdf import PdfReader


MAX_FILE_SIZE = 5 * 1024 * 1024


def extract_text(file_name: str, file_content: bytes) -> str:
    if not file_name:
        raise ValueError("File name is required")

    if len(file_content) > MAX_FILE_SIZE:
        raise ValueError("File size must not exceed 5MB")

    extension = file_name.lower().split(".")[-1]

    if extension == "txt":
        text = file_content.decode("utf-8", errors="ignore")

    elif extension == "pdf":
        reader = PdfReader(BytesIO(file_content))

        pages = []

        for page in reader.pages:
            page_text = page.extract_text()

            if page_text:
                pages.append(page_text)

        text = "\n".join(pages)

    else:
        raise ValueError("Only TXT and PDF files are supported")

    text = text.strip()

    if not text:
        raise ValueError("No extractable text found in the document")

    return text