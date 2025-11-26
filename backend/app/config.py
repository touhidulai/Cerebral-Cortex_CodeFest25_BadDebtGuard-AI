import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get OpenAI API key from environment variable
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# Legacy: HuggingFace token (if needed for fallback)
HF_TOKEN = os.getenv("HF_TOKEN", "")
