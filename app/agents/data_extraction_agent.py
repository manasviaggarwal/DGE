# import json
# from typing import Dict, Any, List
# from app.llm.llm_client import call_llm_json
# import logging

# logger = logging.getLogger("DataExtractionAgent")

# # -----------------------------
# # EXTRACTION SCHEMA
# # -----------------------------
# SCHEMA = {
#     "income": "Monthly income (number)",
#     "family_size": "Number of dependents (number)",
#     "employment_years": "Total years of work experience (number)",
#     "employment_status": "employed | unemployed | self-employed | student | retired",
#     "education_level": "high_school | bachelor | masters | phd | unknown",
#     "age": "Age in years (number)",
#     "assets": "Total assets amount (number)",
#     "liabilities": "Total liabilities amount (number)",
# }

# MAX_CHARS = 1800   # 🔑 safe for Ollama JSON

# # -----------------------------
# # Utilities
# # -----------------------------
# def chunk_text(text: str, size: int = MAX_CHARS) -> List[str]:
#     return [text[i:i + size] for i in range(0, len(text), size)]

# def safe_number(v):
#     try:
#         return float(v)
#     except Exception:
#         return None

# def merge_results(results: List[dict]) -> dict:
#     """First non-null value wins"""
#     merged = {k: None for k in SCHEMA}
#     for r in results:
#         if not isinstance(r, dict):
#             continue
#         for k in SCHEMA:
#             if merged[k] is None and r.get(k) is not None:
#                 merged[k] = r.get(k)
#     return merged

# # -----------------------------
# # MAIN AGENT
# # -----------------------------
# def data_extraction_agent(state: Dict[str, Any]) -> Dict[str, Any]:
#     texts: List[str] = []

#     if state.get("user_input"):
#         texts.append(state["user_input"])

#     for d in state.get("documents", []):
#         if d.get("raw_text"):
#             texts.append(d["raw_text"])

#     full_text = "\n\n".join(texts).strip()

#     if not full_text:
#         state["extracted_data"] = {k: {"value": None} for k in SCHEMA}
#         return state

#     chunks = chunk_text(full_text)

#     partial_results = []

#     for i, chunk in enumerate(chunks):
#         prompt = f"""
#             You are a strict information extraction system.

#             Return EXACTLY one valid JSON object.
#             - Use double quotes for all keys and values.
#             - Do NOT add explanations.
#             - Do NOT add comments.
#             - Do NOT include markdown.
#             - If a value is missing, return null.

#             Schema:
#             {json.dumps(SCHEMA, indent=2)}

#             Input:
#             \"\"\"
#             {chunk}
#             \"\"\"
#         """

#         try:
#             raw = call_llm_json(prompt)
#             partial_results.append(raw)
#         except Exception as e:
#             logger.warning(f"Extraction failed on chunk {i}: {e}")

#     merged = merge_results(partial_results)

#     extracted = {}
#     for k in SCHEMA:
#         v = merged.get(k)
#         if k in {"income", "family_size", "employment_years", "age", "assets", "liabilities"}:
#             v = safe_number(v)
#         extracted[k] = {"value": v}

#     state["extracted_data"] = extracted
#     return state


import json
import logging
from typing import Dict, Any, List

from app.llm.llm_client import call_llm_json

logger = logging.getLogger("DataExtractionAgent")

# --------------------------------------------------
# Extraction schema
# --------------------------------------------------
SCHEMA = {
    "income": "Monthly income (number)",
    "family_size": "Number of dependents (number)",
    "employment_years": "Total years of work experience (number)",
    "employment_status": "employed | unemployed | self-employed | student | retired",
    "education_level": "high_school | bachelor | masters | phd | unknown",
    "age": "Age in years (number)",
    "assets": "Total assets amount (number)",
    "liabilities": "Total liabilities amount (number)",
}

KEYWORDS = [
    "income", "salary", "earn", "wage",
    "dependent", "family",
    "employed", "employment", "experience",
    "asset", "liability", "loan",
    "education", "degree", "age"
]


MAX_CHARS = 1000   # 🔑 safe for Ollama

import re

def preprocess_text(text: str) -> str:
    """
    Aggressively clean noisy user/OCR input before LLM extraction
    """

    # Normalize whitespace
    text = text.replace("\x00", " ")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)

    # Remove common OCR junk
    text = re.sub(r"[|_]{2,}", " ", text)
    text = re.sub(r"[^\x20-\x7E\n]", " ", text)  # non-ASCII except newline

    # Remove page headers / footers
    text = re.sub(r"Page \d+ of \d+", "", text, flags=re.I)
    text = re.sub(r"Confidential.*", "", text, flags=re.I)

    # Normalize currency
    # text = re.sub(r"(INR|Rs\.?|₹)", " INR ", text, flags=re.I)
    # text = re.sub(r"(USD|\$)", " USD ", text, flags=re.I)

    # Normalize numbers
    # text = re.sub(r"(\d)[,](\d)", r"\1\2", text)  # 1,000 → 1000

    # Kill long IDs (Aadhaar, account numbers)
    text = re.sub(r"\b\d{10,}\b", "[LONG_NUMBER]", text)

    return text.strip()


def compress_to_signal(text: str, max_lines: int = 40) -> str:
    lines = [l.strip() for l in text.splitlines() if len(l.strip()) > 5]

    scored = []
    for l in lines:
        score = sum(1 for k in KEYWORDS if k in l.lower())
        if score > 0:
            scored.append((score, l))

    scored.sort(reverse=True)
    selected = [l for _, l in scored[:max_lines]]

    # Fallback if nothing matched
    if not selected:
        selected = lines[:max_lines]

    return "\n".join(selected)

# --------------------------------------------------
# Utilities
# --------------------------------------------------
def chunk_text(text: str, size: int = MAX_CHARS) -> List[str]:
    return [text[i:i + size] for i in range(0, len(text), size)]


def safe_number(v):
    try:
        return float(v)
    except Exception:
        return None


def merge_results(results: List[dict]) -> dict:
    """
    First non-null value wins
    """
    merged = {k: None for k in SCHEMA}

    for r in results:
        if not isinstance(r, dict):
            continue
        for k in SCHEMA:
            if merged[k] is None and r.get(k) is not None:
                merged[k] = r.get(k)

    return merged


# --------------------------------------------------
# MAIN AGENT
# --------------------------------------------------
def data_extraction_agent(state: Dict[str, Any]) -> Dict[str, Any]:
    texts: List[str] = []

    if state.get("user_input"):
        texts.append(state["user_input"])

    for d in state.get("documents", []):
        if d.get("raw_text"):
            texts.append(d["raw_text"])

    full_text = "\n\n".join(texts).strip()



    if not full_text:
        state["extracted_data"] = {k: {"value": None} for k in SCHEMA}
        return state

    clean_text = preprocess_text(full_text)
    signal_text = compress_to_signal(clean_text)
    # print(signal_text)

    chunks = chunk_text(signal_text)
    # print(chunks)
    partial_results = []

    for i, chunk in enumerate(chunks):
        prompt = f"""
You are a strict information extraction system.

Return EXACTLY one valid JSON object.
Rules:
- Use double quotes only
- No explanations
- No comments
- No markdown
- Missing values must be null

Schema:
{json.dumps(SCHEMA, indent=2)}

Input:
\"\"\"
{chunk}
\"\"\"
""".strip()

        try:
            result = call_llm_json(prompt)
            partial_results.append(result)
        except Exception as e:
            logger.error(f"Extraction failed on chunk {i}", exc_info=True)
            partial_results.append({})   # 🔑 never stall pipeline

    merged = merge_results(partial_results)

    extracted = {}
    for k in SCHEMA:
        v = merged.get(k)
        if k in {
            "income",
            "family_size",
            "employment_years",
            "age",
            "assets",
            "liabilities"
        }:
            v = safe_number(v)
        extracted[k] = {"value": v}

    state["extracted_data"] = extracted
    user_text = state.get("user_input", "")

    # print('9999999999999999999999999')
    # print(clean_text)

    state["llm_context"] = clean_text #user_text[:500] if user_text else None
    print("STATE KEYS AFTER EXTRACTION:", state['llm_context'])

    return state
