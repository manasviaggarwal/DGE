from typing import Dict, Any, List
import logging
import io

import streamlit as st
import fitz  # PyMuPDF
import pandas as pd
from PIL import Image
import pytesseract

logger = logging.getLogger("DocumentIngestionAgent")

# --------------------------------------------------
# Cancellation helper (SAFE)
# --------------------------------------------------
def check_cancel(state: Dict[str, Any]):
    current = state.get("agent_run_id")
    active = st.session_state.get("agent_run_id")

    if current is None or active is None:
        return

    if current != active:
        raise RuntimeError("Agent execution cancelled")


from typing import Dict, Any, List
import streamlit as st
import fitz
import pandas as pd
from PIL import Image
import pytesseract
import io

def document_ingestion_agent(state: Dict[str, Any]) -> Dict[str, Any]:
    docs = []
    for f in state.get("uploaded_files", []):
        text, tables = None, None

        if f.type == "application/pdf":
            pdf = fitz.open(stream=f.read(), filetype="pdf")
            text = "\n".join(p.get_text() for p in pdf)

        elif f.type.startswith("image"):
            image = Image.open(io.BytesIO(f.read()))
            text = pytesseract.image_to_string(image)

        elif f.name.endswith(".xlsx"):
            df = pd.read_excel(f)
            tables = df.to_dict(orient="records")

        docs.append({"raw_text": text, "tables": tables})

    state["documents"] = docs
    return state


# --------------------------------------------------
# MAIN INGESTION AGENT
# --------------------------------------------------
def document_ingestion_agent_old(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Ingest uploaded documents and extract content in a uniform format.
    """

    check_cancel(state)
    logger.info("=== DOCUMENT INGESTION AGENT ===")

    uploaded_files = state.get("uploaded_files") or []
    documents: List[Dict[str, Any]] = []

    for file in uploaded_files:
        try:
            doc_type = infer_document_type(file.name)
            extracted = extract_file_content(file)

            documents.append({
                "file_name": file.name,
                "file_type": doc_type,
                "mime_type": file.type,
                "size_kb": round(file.size / 1024, 2),
                "raw_text": extracted.get("text"),
                "tables": extracted.get("tables"),
            })

        except Exception as e:
            logger.exception(f"Failed to process file: {file.name}")
            documents.append({
                "file_name": file.name,
                "file_type": "error",
                "mime_type": file.type,
                "size_kb": round(file.size / 1024, 2),
                "raw_text": None,
                "tables": None,
                "error": str(e),
            })

    state["documents"] = documents
    logger.info(f"Ingested {len(documents)} documents")

    return state


# --------------------------------------------------
# FILE TYPE DISPATCH
# --------------------------------------------------
def extract_file_content(file) -> Dict[str, Any]:
    """
    Extract text or tables depending on file type.
    """

    if file.type == "application/pdf":
        return extract_pdf(file)

    if file.type in {"image/png", "image/jpeg", "image/jpg"}:
        return extract_image(file)

    if file.name.lower().endswith(".xlsx"):
        return extract_excel(file)

    return {"text": None, "tables": None}


# --------------------------------------------------
# PDF EXTRACTION
# --------------------------------------------------
def extract_pdf(file) -> Dict[str, Any]:
    text_pages = []

    # IMPORTANT: read bytes once
    file_bytes = file.read()
    pdf = fitz.open(stream=file_bytes, filetype="pdf")

    for page in pdf:
        text_pages.append(page.get_text())

    return {
        "text": "\n".join(text_pages).strip() or None,
        "tables": None,
    }


# --------------------------------------------------
# IMAGE OCR
# --------------------------------------------------
def extract_image(file) -> Dict[str, Any]:
    image_bytes = file.read()
    image = Image.open(io.BytesIO(image_bytes))
    text = pytesseract.image_to_string(image)

    return {
        "text": text.strip() or None,
        "tables": None,
    }


# --------------------------------------------------
# EXCEL EXTRACTION
# --------------------------------------------------
def extract_excel(file) -> Dict[str, Any]:
    df = pd.read_excel(file)

    return {
        "text": None,
        "tables": df.to_dict(orient="records") if not df.empty else None,
    }


# --------------------------------------------------
# DOCUMENT TYPE HEURISTICS
# --------------------------------------------------
def infer_document_type(filename: str) -> str:
    name = filename.lower()

    if "emirates" in name or "id" in name:
        return "emirates_id"
    if "bank" in name:
        return "bank_statement"
    if "credit" in name:
        return "credit_report"
    if "asset" in name:
        return "assets_liabilities"
    if "resume" in name or "cv" in name:
        return "resume"

    return "unknown"


# --------------------------------------------------
# OPTIONAL: MOCK EXTRACTION (NOT USED IN PIPELINE)
# --------------------------------------------------
def mock_extract_fields(doc_type: str) -> Dict[str, Any]:
    """
    For testing only. Not used by ingestion or extraction pipeline.
    """
    return {
        "emirates_id": {"name": "John Doe", "dob": "1990-01-01"},
        "bank_statement": {"monthly_income": 4500},
        "credit_report": {"credit_score": 680},
        "assets_liabilities": {"assets": 15000, "liabilities": 5000},
        "resume": {"employment_status": "employed"},
    }.get(doc_type, {})
