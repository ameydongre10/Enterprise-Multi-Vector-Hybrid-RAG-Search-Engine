from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class SearchMode(str):
    HYBRID_RRF = "HYBRID_RRF"
    VECTOR_ONLY = "VECTOR_ONLY"
    LEXICAL_ONLY = "LEXICAL_ONLY"

class QueryRequest(BaseModel):
    query: str
    search_mode: str = Field(default=SearchMode.HYBRID_RRF)
    top_k: int = Field(default=10, ge=1, le=50)
    top_n: int = Field(default=5, ge=1, le=20)
    rrf_k: int = Field(default=60, ge=1, le=200)
    rerank_threshold: float = Field(default=0.3, ge=0.0, le=1.0)
    document_ids: Optional[List[str]] = None

class ChunkSearchResult(BaseModel):
    chunk_id: str
    document_id: str
    filename: str
    chunk_index: int
    raw_content: str
    contextualized_content: str
    vector_score: Optional[float] = None
    vector_rank: Optional[int] = None
    lexical_score: Optional[float] = None
    lexical_rank: Optional[int] = None
    rrf_score: Optional[float] = None
    rerank_score: Optional[float] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

class Citation(BaseModel):
    citation_id: int
    document_id: str
    filename: str
    chunk_id: str
    page_number: Optional[int] = None
    section: Optional[str] = None
    snippet: str

class QueryResponse(BaseModel):
    query: str
    search_mode: str
    answer: str
    citations: List[Citation]
    retrieved_chunks: List[ChunkSearchResult]
    execution_time_ms: float
    rrf_stats: Dict[str, Any] = Field(default_factory=dict)

class EvaluationRequest(BaseModel):
    test_cases: Optional[List[Dict[str, Any]]] = None

class MetricResult(BaseModel):
    metric_name: str
    score: float
    description: str

class EvaluationResponse(BaseModel):
    timestamp: str
    sample_count: int
    metrics: List[MetricResult]
    details: List[Dict[str, Any]]
