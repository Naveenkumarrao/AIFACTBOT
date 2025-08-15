import os
from dotenv import load_dotenv

load_dotenv()

PROVIDER = os.getenv("PROVIDER", "noop").lower()

# OpenAI / Anthropic / Ollama config (optional)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.1")
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")

# Search
MAX_SEARCH_RESULTS = int(os.getenv("MAX_SEARCH_RESULTS", "6"))
REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "12"))
USER_AGENT = os.getenv("USER_AGENT", "AI-FactCheckerBot/1.0")
