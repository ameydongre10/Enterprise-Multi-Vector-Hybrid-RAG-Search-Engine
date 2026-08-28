import re
from typing import List, Dict, Any
from app.config import settings

class CrossEncoderRerankerService:
    def rerank(self, query: str, candidate_chunks: List[Dict[str, Any]], top_n: int = settings.DEFAULT_TOP_N, threshold: float = settings.RERANK_THRESHOLD) -> List[Dict[str, Any]]:
        if not candidate_chunks:
            return []
        q_terms = set(re.findall(r'\b\w+\b', query.lower()))
        reranked = []
        for item in candidate_chunks:
            content = item.get("contextualized_content", item.get("raw_content", ""))
            c_terms = set(re.findall(r'\b\w+\b', content.lower()))
            overlap = len(q_terms.intersection(c_terms)) / max(1, len(q_terms))
            score = float(item.get("rrf_score", 0.0) * 50.0 + overlap * 0.5)
            ic = dict(item)
            ic["rerank_score"] = round(score, 4)
            reranked.append(ic)
        reranked.sort(key=lambda x: x["rerank_score"], reverse=True)
        filtered = [c for c in reranked if c["rerank_score"] >= threshold] or reranked[:1]
        return filtered[:top_n]

reranker_service = CrossEncoderRerankerService()
