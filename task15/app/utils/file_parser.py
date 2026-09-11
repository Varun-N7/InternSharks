from io import BytesIO

from pypdf import PdfReader


MAX_FILE_SIZE = 5 * 1024 * 1024


def extract_text_from_file(file_content, filename):

    file_size = len(file_content)

    if file_size == 0:
        raise ValueError("File is empty")

    if file_size > MAX_FILE_SIZE:
        raise ValueError("File size exceeds the 5 MB limit")

    if filename.lower().endswith(".txt"):

        try:
            text = file_content.decode("utf-8")
        except UnicodeDecodeError:
            raise ValueError("Unable to decode text file")

    elif filename.lower().endswith(".pdf"):

        try:
            reader = PdfReader(BytesIO(file_content))

            text = ""

            for page in reader.pages:
                page_text = page.extract_text()

                if page_text:
                    text += page_text + "\n"

        except Exception:
            raise ValueError("Unable to extract text from PDF")

    else:
        raise ValueError("Unsupported file type")

    text = text.strip()

    if not text:
        raise ValueError("File contains no extractable text")

    return text