from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from uuid import uuid4

class ProcessingStatus(str):
    PENDING = "PENDING"
    PARSING = "PARSING"
    SUMMARIZING = "SUMMARIZING"
    EMBEDDING = "EMBEDDING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

class DocumentBase(BaseModel):
    filename: str
    mime_type: str
    file_size_bytes: int

class DocumentCreate(DocumentBase):
    pass

class DocumentResponse(DocumentBase):
    id: str
    global_context: Optional[str] = None
    uploaded_at: str
    processing_status: str
    error_message: Optional[str] = None
    chunk_count: int = 0

class DocumentChunk(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    document_id: str
    chunk_index: int
    raw_content: str
    contextualized_content: str
    dense_embedding: Optional[List[float]] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

class TaskStatusResponse(BaseModel):
    task_id: str
    status: str
    progress: int
    message: str
    document_id: Optional[str] = None
    error: Optional[str] = None
