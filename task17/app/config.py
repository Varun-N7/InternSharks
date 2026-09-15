import os

from dotenv import load_dotenv


load_dotenv()


OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL")

EMBEDDING_MODEL = os.getenv(
    "EMBEDDING_MODEL",
    "sentence-transformers/all-MiniLM-L6-v2",
)


if not OPENROUTER_API_KEY:
    raise ValueError("OPENROUTER_API_KEY is not set")

if not OPENROUTER_MODEL:
    raise ValueError("OPENROUTER_MODEL is not set")