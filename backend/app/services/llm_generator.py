import logging
from typing import List, Dict, Any, Tuple
from app.config import settings
from app.models.query import Citation

logger = logging.getLogger("hybrid_rag.generator")

class LLMGeneratorService:
    def generate_grounded_answer(self, query: str, chunks: List[Dict[str, Any]]) -> Tuple[str, List[Citation]]:
        if not chunks:
            return "No relevant document content was found to answer your query.", []
        citations = []
        c_blocks = []
        for idx, chunk in enumerate(chunks, start=1):
            fn = chunk.get("filename", "Document")
            doc_id = chunk.get("document_id", "")
            cid = chunk.get("chunk_id", str(idx))
            page = chunk.get("metadata", {}).get("page_number", 1)
            raw = chunk.get("raw_content", "")
            citations.append(Citation(citation_id=idx, document_id=doc_id, filename=fn, chunk_id=cid, page_number=page, snippet=raw[:200]))
            c_blocks.append(f"--- [CITATION [{idx}]] ---\nSource: {fn} (Page {page})\nContent:\n{raw}\n")
        
        context_str = "\n\n".join(c_blocks)
        if settings.GEMINI_API_KEY:
            try:
                from google import genai
                client = genai.Client(api_key=settings.GEMINI_API_KEY)
                sys_prompt = "Answer the question strictly using the provided context blocks. Cite statements inline like [Citation [1]], [Citation [2]]."
                user_prompt = f"CONTEXT:\n{context_str}\n\nQUERY: {query}\nAnswer:"
                res = client.models.generate_content(model=settings.LLM_MODEL, contents=sys_prompt + "\n\n" + user_prompt)
                if res and res.text:
                    return res.text.strip(), citations
            except Exception as e:
                logger.warning(f"Gemini LLM failed: {e}")

        lines = [f"Based on retrieved document records for '{query}':\n"]
        for c in citations:
            lines.append(f"- According to **{c.filename}** (Page {c.page_number}) [Citation [{c.citation_id}]]:\n  > \"{c.snippet}\"\n")
        return "\n".join(lines), citations

llm_generator_service = LLMGeneratorService()
