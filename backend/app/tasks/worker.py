import logging
from app.config import settings
from app.database import db
from app.services.document_parser import parser_service
from app.services.global_summarizer import summarizer_service
from app.services.chunker import chunker_service
from app.services.embedder import embedder_service
from app.tasks.task_manager import task_tracker

logger = logging.getLogger("hybrid_rag.worker")

def process_document_pipeline(task_id: str, document_id: str, file_path: str, filename: str, mime_type: str):
    try:
        task_tracker.update_task(task_id, "PARSING", 20, "Extracting text and tables...")
        db.update_document_status(document_id, "PARSING")
        full_text, page_structures = parser_service.parse_file(file_path, filename, mime_type)

        task_tracker.update_task(task_id, "SUMMARIZING", 45, "Generating global summary...")
        db.update_document_status(document_id, "SUMMARIZING")
        global_context = summarizer_service.generate_global_context(filename, full_text)

        task_tracker.update_task(task_id, "CHUNKING", 65, "Executing contextual chunking...")
        raw_chunks = chunker_service.chunk_document(document_id, global_context, page_structures)

        task_tracker.update_task(task_id, "EMBEDDING", 85, "Generating dense vectors...")
        db.update_document_status(document_id, "EMBEDDING")
        texts = [c["contextualized_content"] for c in raw_chunks]
        embeddings = embedder_service.embed_batch(texts)

        for chunk_dict, emb in zip(raw_chunks, embeddings):
            chunk_dict["dense_embedding"] = emb

        db.insert_chunks(raw_chunks)
        db.update_document_status(document_id, "COMPLETED", global_context=global_context)
        task_tracker.update_task(task_id, "COMPLETED", 100, f"Successfully processed {len(raw_chunks)} chunks.")
    except Exception as e:
        err = str(e)
        logger.error(f"Task {task_id} failed: {err}")
        db.update_document_status(document_id, "FAILED", error_message=err)
        task_tracker.update_task(task_id, "FAILED", 0, "Ingestion failed.", error=err)
