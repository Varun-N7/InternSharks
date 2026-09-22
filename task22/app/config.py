import os
from dotenv import load_dotenv

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL")

MAX_AGENT_STEPS = int(os.getenv("MAX_AGENT_STEPS", "10"))

DATABASE_PATH = os.getenv("DATABASE_PATH", "agent_state.db")

MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))
RETRY_BASE_DELAY = float(os.getenv("RETRY_BASE_DELAY", "1"))

EXTERNAL_TOOL_TIMEOUT = float(
    os.getenv("EXTERNAL_TOOL_TIMEOUT", "5")
)

OPENROUTER_TIMEOUT = float(
    os.getenv("OPENROUTER_TIMEOUT", "30")
)