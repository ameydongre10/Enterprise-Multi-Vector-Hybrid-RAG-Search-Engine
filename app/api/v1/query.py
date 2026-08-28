import time
from fastapi import APIRouter
from app.models.query import QueryRequest, QueryResponse, ChunkSearchResult, SearchMode
from app.services.hybrid_retriever import retriever_service
from app.services.reranker import reranker_service
from app.services.llm_generator import llm_generator_service

router = APIRouter(prefix="/query", tags=["query"])

@router.post("", response_model=QueryResponse)
async def execute_query(req: QueryRequest):
    start = time.time()
    dual_res = retriever_service.dual_path_search(query=req.query, document_ids=req.document_ids, top_k=req.top_k, rrf_k=req.rrf_k)
    candidates = dual_res["fused_results"]
    reranked = reranker_service.rerank(query=req.query, candidate_chunks=candidates, top_n=req.top_n, threshold=req.rerank_threshold)
    answer, citations = llm_generator_service.generate_grounded_answer(query=req.query, chunks=reranked)
    exec_time = round((time.time() - start) * 1000, 2)

    return QueryResponse(
        query=req.query,
        search_mode=req.search_mode,
        answer=answer,
        citations=citations,
        retrieved_chunks=[ChunkSearchResult(**c) for c in reranked],
        execution_time_ms=exec_time,
        rrf_stats={"search_mode": req.search_mode, "rrf_k": req.rrf_k}
    )
