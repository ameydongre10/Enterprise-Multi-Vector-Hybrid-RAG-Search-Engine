import os
import shutil
from uuid import uuid4
from fastapi import APIRouter, UploadFile, File, BackgroundTasks, HTTPException, status
from typing import List
from app.config import settings
from app.database import db
from app.models.document import DocumentResponse, TaskStatusResponse
from app.tasks.task_manager import task_tracker
from app.tasks.worker import process_document_pipeline

router = APIRouter(prefix="/documents", tags=["documents"])

@router.post("/upload", response_model=TaskStatusResponse, status_code=status.HTTP_202_ACCEPTED)
async def upload_document(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    doc_id = str(uuid4())
    task_id = f"task_{uuid4().hex[:12]}"
    file_path = os.path.join(settings.UPLOAD_DIR, f"{doc_id}_{file.filename}")
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    file_size = os.path.getsize(file_path)

    doc_dict = {"id": doc_id, "filename": file.filename, "mime_type": file.content_type or "application/octet-stream", "file_size_bytes": file_size, "processing_status": "PENDING"}
    db.insert_document(doc_dict)
    task_tracker.create_task(task_id, doc_id)
    background_tasks.add_task(process_document_pipeline, task_id, doc_id, file_path, file.filename, file.content_type)

    return TaskStatusResponse(task_id=task_id, status="PENDING", progress=5, message="Upload completed. Ingestion initiated.", document_id=doc_id)

@router.get("/tasks/{task_id}", response_model=TaskStatusResponse)
async def get_task_status(task_id: str):
    return TaskStatusResponse(**task_tracker.get_task(task_id))

@router.get("", response_model=List[DocumentResponse])
async def list_documents():
    return [DocumentResponse(**d) for d in db.list_documents()]

@router.delete("/{doc_id}")
async def delete_document(doc_id: str):
    if not db.delete_document(doc_id):
        raise HTTPException(status_code=404, detail="Document not found.")
    return {"message": "Deleted successfully."}
