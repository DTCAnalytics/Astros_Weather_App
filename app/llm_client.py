import os
from typing import Optional

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover
    load_dotenv = None

try:
    from google import genai
except ImportError:  # pragma: no cover
    genai = None


class LLMClient:
    def __init__(self, model: str = "gemini-2.5-flash"):
        if load_dotenv:
            load_dotenv()

        self.model = os.getenv("GEMINI_MODEL", model)
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.enabled = bool(self.api_key and genai)
        self.client = genai.Client(api_key=self.api_key) if self.enabled else None

    def generate(self, prompt: str) -> Optional[str]:
        if not self.enabled:
            return "LLM unavailable: missing GEMINI_API_KEY or google-genai package. Falling back to rule-based advice."

        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
            )
            return response.text.strip() if response.text else "LLM returned no text. Falling back to rule-based advice."
        except Exception as exc:
            return f"LLM unavailable ({exc}). Falling back to rule-based advice."
