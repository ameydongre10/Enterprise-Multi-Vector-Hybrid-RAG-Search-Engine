import os
import pandas as pd
from typing import List, Dict, Any, Tuple
import logging

logger = logging.getLogger("hybrid_rag.parser")

class DocumentParserService:
    def parse_file(self, file_path: str, filename: str, mime_type: str) -> Tuple[str, List[Dict[str, Any]]]:
        ext = os.path.splitext(filename)[1].lower()
        if ext == ".pdf":
            return self._parse_pdf(file_path)
        elif ext in [".docx", ".doc"]:
            return self._parse_docx(file_path)
        elif ext in [".csv", ".tsv", ".xlsx"]:
            return self._parse_tabular(file_path, ext)
        else:
            return self._parse_text(file_path)

    def _parse_pdf(self, file_path: str) -> Tuple[str, List[Dict[str, Any]]]:
        page_structures = []
        full_text_parts = []
        try:
            import pdfplumber
            with pdfplumber.open(file_path) as pdf:
                for idx, page in enumerate(pdf.pages, start=1):
                    tables = page.extract_tables()
                    tables_md = []
                    for tbl in tables:
                        if tbl and len(tbl) > 0:
                            df = pd.DataFrame(tbl[1:], columns=tbl[0]).dropna(how='all')
                            tables_md.append(df.to_markdown(index=False))
                    page_text = page.extract_text() or ""
                    combined = page_text
                    if tables_md:
                        combined += "\n\n### Extracted Tables:\n" + "\n\n".join(tables_md)
                    page_structures.append({"page": idx, "text": combined, "has_tables": len(tables_md) > 0})
                    full_text_parts.append(f"--- Page {idx} ---\n{combined}")
            return "\n\n".join(full_text_parts), page_structures
        except Exception as e:
            logger.warning(f"pdfplumber failed: {e}")

        import pypdf
        reader = pypdf.PdfReader(file_path)
        for idx, page in enumerate(reader.pages, start=1):
            text = page.extract_text() or ""
            page_structures.append({"page": idx, "text": text, "has_tables": False})
            full_text_parts.append(f"--- Page {idx} ---\n{text}")
        return "\n\n".join(full_text_parts), page_structures

    def _parse_docx(self, file_path: str) -> Tuple[str, List[Dict[str, Any]]]:
        try:
            import docx
            doc = docx.Document(file_path)
            paragraphs = [p.text.strip() for p in doc.paragraphs if p.text.strip()]
            combined = "\n\n".join(paragraphs)
            return combined, [{"page": 1, "text": combined, "has_tables": False}]
        except Exception as e:
            return self._parse_text(file_path)

    def _parse_tabular(self, file_path: str, ext: str) -> Tuple[str, List[Dict[str, Any]]]:
        df = pd.read_csv(file_path) if ext == ".csv" else pd.read_excel(file_path)
        text = f"Tabular Data ({len(df)} rows x {len(df.columns)} cols)\n\n" + df.to_markdown(index=False)
        return text, [{"page": 1, "text": text, "has_tables": True}]

    def _parse_text(self, file_path: str) -> Tuple[str, List[Dict[str, Any]]]:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            c = f.read()
        return c, [{"page": 1, "text": c, "has_tables": False}]

parser_service = DocumentParserService()
