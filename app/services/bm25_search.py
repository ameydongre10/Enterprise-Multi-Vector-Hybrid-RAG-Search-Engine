import re
from typing import List, Dict, Any
from rank_bm25 import BM25Okapi

class BM25SearchService:
    def tokenize(self, text: str) -> List[str]:
        return re.findall(r'\b[\w\-]+\b', text.lower())

    def search(self, query: str, chunks: List[Dict[str, Any]], top_k: int = 10) -> List[Dict[str, Any]]:
        if not chunks:
            return []
        tokenized_corpus = [self.tokenize(c.get("contextualized_content", c.get("raw_content", ""))) for c in chunks]
        tokenized_query = self.tokenize(query)
        if not tokenized_query or not any(tokenized_corpus):
            return []
        bm25 = BM25Okapi(tokenized_corpus)
        scores = bm25.get_scores(tokenized_query)
        results = []
        for idx, score in enumerate(scores):
            if score > 0.001:
                results.append({"chunk_id": chunks[idx]["id"], "score": float(score), "chunk": dict(chunks[idx])})
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:top_k]

bm25_service = BM25SearchService()
