import re
from typing import List, Dict, Any
from app.config import settings

class ContextualizedChunkerService:
    def __init__(self, chunk_size: int = settings.DEFAULT_CHUNK_SIZE, overlap: int = settings.DEFAULT_CHUNK_OVERLAP):
        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk_document(self, document_id: str, global_context: str, page_structures: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        chunks = []
        chunk_index = 0
        for page_data in page_structures:
            page_num = page_data.get("page", 1)
            text = page_data.get("text", "").strip()
            if not text:
                continue
            paras = [p.strip() for p in re.split(r'\n\s*\n', text) if p.strip()]
            buf = []
            words_cnt = 0
            for para in paras:
                p_words = para.split()
                if words_cnt + len(p_words) > self.chunk_size and buf:
                    raw = "\n\n".join(buf)
                    ctx = f"Document Context: {global_context}\n\nChunk Text:\n{raw}"
                    chunks.append({
                        "document_id": document_id,
                        "chunk_index": chunk_index,
                        "raw_content": raw,
                        "contextualized_content": ctx,
                        "metadata": {"page_number": page_num, "is_table": page_data.get("has_tables", False)}
                    })
                    chunk_index += 1
                    buf = buf[-1:] if len(buf) > 1 else []
                    words_cnt = len(buf[0].split()) if buf else 0
                buf.append(para)
                words_cnt += len(p_words)

            if buf:
                raw = "\n\n".join(buf)
                ctx = f"Document Context: {global_context}\n\nChunk Text:\n{raw}"
                chunks.append({
                    "document_id": document_id,
                    "chunk_index": chunk_index,
                    "raw_content": raw,
                    "contextualized_content": ctx,
                    "metadata": {"page_number": page_num, "is_table": page_data.get("has_tables", False)}
                })
                chunk_index += 1
        return chunks

chunker_service = ContextualizedChunkerService()
