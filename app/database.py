import os
import json
import sqlite3
import logging
import numpy as np
from datetime import datetime
from typing import List, Dict, Any, Optional
from uuid import uuid4
from app.config import settings

logger = logging.getLogger("hybrid_rag.database")

USE_POSTGRES = False
pg_pool = None

try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    conn = psycopg2.connect(settings.DATABASE_URL, connect_timeout=2)
    conn.close()
    USE_POSTGRES = True
    logger.info("Successfully connected to PostgreSQL with pgvector support!")
except Exception as e:
    logger.warning(f"PostgreSQL connection not available ({e}). Using local SQLite + Vector Engine fallback.")

class LocalDatabase:
    def __init__(self, db_path: str = None):
        if db_path is None:
            db_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "storage")
            os.makedirs(db_dir, exist_ok=True)
            db_path = os.path.join(db_dir, "local_rag.db")
        self.db_path = db_path
        self._init_sqlite()

    def _get_conn(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_sqlite(self):
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS documents (
                id TEXT PRIMARY KEY,
                filename TEXT NOT NULL,
                mime_type TEXT NOT NULL,
                file_size_bytes INTEGER NOT NULL,
                global_context TEXT,
                uploaded_at TEXT NOT NULL,
                processing_status TEXT NOT NULL,
                error_message TEXT
            );
            """)
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS document_chunks (
                id TEXT PRIMARY KEY,
                document_id TEXT NOT NULL,
                chunk_index INTEGER NOT NULL,
                raw_content TEXT NOT NULL,
                contextualized_content TEXT NOT NULL,
                dense_embedding TEXT,
                metadata TEXT,
                FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE
            );
            """)
            conn.commit()

    def insert_document(self, doc_dict: Dict[str, Any]) -> str:
        doc_id = doc_dict.get("id", str(uuid4()))
        uploaded_at = doc_dict.get("uploaded_at", datetime.utcnow().isoformat())
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO documents (id, filename, mime_type, file_size_bytes, global_context, uploaded_at, processing_status, error_message)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                doc_id,
                doc_dict["filename"],
                doc_dict["mime_type"],
                doc_dict["file_size_bytes"],
                doc_dict.get("global_context"),
                uploaded_at,
                doc_dict.get("processing_status", "PENDING"),
                doc_dict.get("error_message")
            ))
            conn.commit()
        return doc_id

    def update_document_status(self, doc_id: str, status: str, global_context: Optional[str] = None, error_message: Optional[str] = None):
        with self._get_conn() as conn:
            cursor = conn.cursor()
            if global_context is not None:
                cursor.execute("""
                    UPDATE documents SET processing_status = ?, global_context = ?, error_message = ? WHERE id = ?
                """, (status, global_context, error_message, doc_id))
            else:
                cursor.execute("""
                    UPDATE documents SET processing_status = ?, error_message = ? WHERE id = ?
                """, (status, error_message, doc_id))
            conn.commit()

    def get_document(self, doc_id: str) -> Optional[Dict[str, Any]]:
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM documents WHERE id = ?", (doc_id,))
            row = cursor.fetchone()
            if not row:
                return None
            res = dict(row)
            cursor.execute("SELECT COUNT(*) as cnt FROM document_chunks WHERE document_id = ?", (doc_id,))
            res["chunk_count"] = cursor.fetchone()["cnt"]
            return res

    def list_documents(self) -> List[Dict[str, Any]]:
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM documents ORDER BY uploaded_at DESC")
            rows = cursor.fetchall()
            result = []
            for row in rows:
                doc = dict(row)
                cursor.execute("SELECT COUNT(*) as cnt FROM document_chunks WHERE document_id = ?", (doc["id"],))
                doc["chunk_count"] = cursor.fetchone()["cnt"]
                result.append(doc)
            return result

    def delete_document(self, doc_id: str) -> bool:
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM document_chunks WHERE document_id = ?", (doc_id,))
            cursor.execute("DELETE FROM documents WHERE id = ?", (doc_id,))
            conn.commit()
            return cursor.rowcount > 0

    def insert_chunks(self, chunks: List[Dict[str, Any]]):
        with self._get_conn() as conn:
            cursor = conn.cursor()
            for c in chunks:
                chunk_id = c.get("id", str(uuid4()))
                embedding_json = json.dumps(c.get("dense_embedding")) if c.get("dense_embedding") is not None else None
                metadata_json = json.dumps(c.get("metadata", {}))
                cursor.execute("""
                    INSERT INTO document_chunks (id, document_id, chunk_index, raw_content, contextualized_content, dense_embedding, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    chunk_id,
                    c["document_id"],
                    c["chunk_index"],
                    c["raw_content"],
                    c["contextualized_content"],
                    embedding_json,
                    metadata_json
                ))
            conn.commit()

    def get_all_chunks(self, document_ids: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        with self._get_conn() as conn:
            cursor = conn.cursor()
            if document_ids:
                placeholders = ",".join(["?"] * len(document_ids))
                query = f"""
                    SELECT c.*, d.filename FROM document_chunks c
                    JOIN documents d ON c.document_id = d.id
                    WHERE c.document_id IN ({placeholders})
                """
                cursor.execute(query, document_ids)
            else:
                query = """
                    SELECT c.*, d.filename FROM document_chunks c
                    JOIN documents d ON c.document_id = d.id
                """
                cursor.execute(query)
            
            rows = cursor.fetchall()
            chunks = []
            for row in rows:
                item = dict(row)
                item["dense_embedding"] = json.loads(item["dense_embedding"]) if item["dense_embedding"] else None
                item["metadata"] = json.loads(item["metadata"]) if item["metadata"] else {}
                chunks.append(item)
            return chunks

db = LocalDatabase()
