import logging
from app.config import settings

logger = logging.getLogger("hybrid_rag.summarizer")

class GlobalSummarizerService:
    def generate_global_context(self, filename: str, full_text: str) -> str:
        if settings.GEMINI_API_KEY:
            try:
                from google import genai
                client = genai.Client(api_key=settings.GEMINI_API_KEY)
                prompt = (
                    f"Summarize the global context of this document in 2-3 concise sentences.\n"
                    f"Filename: {filename}\nContent:\n{full_text[:3000]}"
                )
                res = client.models.generate_content(model=settings.LLM_MODEL, contents=prompt)
                if res and res.text:
                    return res.text.strip()
            except Exception as e:
                logger.warning(f"Gemini summary failed: {e}")
        return f"[Global Document Context | File: {filename} | Topic: {full_text[:200]}...]"

summarizer_service = GlobalSummarizerService()
