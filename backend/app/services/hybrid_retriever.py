import numpy as np
from concurrent.futures import ThreadPoolExecutor
from typing import List, Dict, Any, Optional
from app.config import settings
from app.database import db
from app.services.embedder import embedder_service
from app.services.bm25_search import bm25_service

class HybridRetrievalService:
    def __init__(self, rrf_k: int = settings.RRF_K):
        self.rrf_k = rrf_k

    def reciprocal_rank_fusion(self, vector_results: List[Dict[str, Any]], lexical_results: List[Dict[str, Any]], top_k: int = 10) -> List[Dict[str, Any]]:
        rrf_scores: Dict[str, float] = {}
        chunk_map: Dict[str, Dict[str, Any]] = {}
        ranks: Dict[str, Dict[str, Any]] = {}

        for rank, item in enumerate(vector_results, start=1):
            cid = item["chunk_id"]
            if cid not in rrf_scores:
                rrf_scores[cid] = 0.0
                chunk_map[cid] = item.get("chunk", {})
                ranks[cid] = {"vector_rank": None, "lexical_rank": None, "vector_score": None, "lexical_score": None}
            rrf_scores[cid] += 1.0 / (self.rrf_k + rank)
            ranks[cid]["vector_rank"] = rank
            ranks[cid]["vector_score"] = item.get("score", 0.0)

        for rank, item in enumerate(lexical_results, start=1):
            cid = item["chunk_id"]
            if cid not in rrf_scores:
                rrf_scores[cid] = 0.0
                chunk_map[cid] = item.get("chunk", {})
                ranks[cid] = {"vector_rank": None, "lexical_rank": None, "vector_score": None, "lexical_score": None}
            rrf_scores[cid] += 1.0 / (self.rrf_k + rank)
            ranks[cid]["lexical_rank"] = rank
            ranks[cid]["lexical_score"] = item.get("score", 0.0)

        sorted_ids = sorted(rrf_scores.keys(), key=lambda x: rrf_scores[x], reverse=True)
        fused = []
        for cid in sorted_ids[:top_k]:
            cinfo = chunk_map[cid]
            rinfo = ranks[cid]
            fused.append({
                "chunk_id": cid,
                "document_id": cinfo.get("document_id", ""),
                "filename": cinfo.get("filename", ""),
                "chunk_index": cinfo.get("chunk_index", 0),
                "raw_content": cinfo.get("raw_content", ""),
                "contextualized_content": cinfo.get("contextualized_content", ""),
                "vector_score": rinfo["vector_score"],
                "vector_rank": rinfo["vector_rank"],
                "lexical_score": rinfo["lexical_score"],
                "lexical_rank": rinfo["lexical_rank"],
                "rrf_score": float(rrf_scores[cid]),
                "metadata": cinfo.get("metadata", {})
            })
        return fused

    def search_dense(self, query_vec: List[float], candidate_chunks: List[Dict[str, Any]], top_k: int = 10) -> List[Dict[str, Any]]:
        if not candidate_chunks: return []
        q = np.array(query_vec, dtype=np.float32)
        q_norm = np.linalg.norm(q)
        if q_norm > 0: q = q / q_norm
        res = []
        for c in candidate_chunks:
            emb = c.get("dense_embedding")
            if not emb: continue
            c_arr = np.array(emb, dtype=np.float32)
            c_norm = np.linalg.norm(c_arr)
            if c_norm > 0: c_arr = c_arr / c_norm
            res.append({"chunk_id": c["id"], "score": float(np.dot(q, c_arr)), "chunk": c})
        res.sort(key=lambda x: x["score"], reverse=True)
        return res[:top_k]

    def dual_path_search(self, query: str, document_ids: Optional[List[str]] = None, top_k: int = 10, rrf_k: int = 60) -> Dict[str, Any]:
        self.rrf_k = rrf_k
        query_vec = embedder_service.embed_text(query)
        all_chunks = db.get_all_chunks(document_ids=document_ids)
        with ThreadPoolExecutor(max_workers=2) as ex:
            f_vec = ex.submit(self.search_dense, query_vec, all_chunks, top_k * 2)
            f_lex = ex.submit(bm25_service.search, query, all_chunks, top_k * 2)
            vec_res = f_vec.result()
            lex_res = f_lex.result()
        fused = self.reciprocal_rank_fusion(vec_res, lex_res, top_k=top_k)
        return {"vector_results": vec_res[:top_k], "lexical_results": lex_res[:top_k], "fused_results": fused}

retriever_service = HybridRetrievalService()
