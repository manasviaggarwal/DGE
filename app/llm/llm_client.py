import requests
import json
import logging

logger = logging.getLogger("LLMClient")

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "llama3.1:8b"  # or 


import json
import re
import requests

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "llama3.1:8b"

def extract_json_block(text: str) -> str:
    """Extract the first JSON object from text."""
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        raise ValueError("No JSON object found")
    return match.group(0)

def repair_json(text: str) -> str:
    """Fix common LLM JSON issues."""
    # Quote unquoted keys
    text = re.sub(r"(\w+)\s*:", r'"\1":', text)
    # Remove trailing commas
    text = re.sub(r",\s*}", "}", text)
    text = re.sub(r",\s*]", "]", text)
    return text

def call_llm_json(prompt: str) -> dict:
    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0,
            "num_ctx": 4096,
        }
    }

    r = requests.post(OLLAMA_URL, json=payload, timeout=180)
    r.raise_for_status()

    raw_text = r.json().get("response", "")
    print(raw_text, '8********************************************')

    try:
        json_text = extract_json_block(raw_text)
        json_text = repair_json(json_text)
        return json.loads(json_text)
    except Exception as e:
        raise ValueError(f"Invalid JSON from LLM: {raw_text}") from e


def call_llm_json_old(prompt: str, timeout: int = 180) -> dict:
    """
    Calls local Ollama LLM and safely extracts JSON.
    """

    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.1,
            "num_predict": 1024
        }
    }

    try:
        response = requests.post(
            OLLAMA_URL,
            json=payload,
            timeout=timeout
        )
        response.raise_for_status()

        raw_text = response.json().get("response", "")
        logger.debug(f"Raw LLM output: {raw_text}")

        # Extract first JSON block
        start = raw_text.find("{")
        end = raw_text.rfind("}")

        if start == -1 or end == -1:
            raise ValueError("No JSON detected in LLM output")

        return json.loads(raw_text[start:end + 1])

    except Exception as e:
        logger.error(f"LLM JSON call failed: {e}")
        return {}

        
def call_llm(prompt: str, timeout: int = 300) -> str:
    """
    Call Ollama local LLM and return plain text response.
    """

    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.3,
            "num_predict": 512
        }
    }

    try:
        response = requests.post(
            OLLAMA_URL,
            json=payload,
            timeout=timeout
        )
        response.raise_for_status()

        return response.json().get("response", "").strip()

    except Exception as e:
        logger.error(f"LLM text call failed: {e}")
        return "Explanation unavailable due to LLM service issue."


# import json
# import logging
# import requests

# logger = logging.getLogger("LLMClient")

# OLLAMA_URL = "http://localhost:11434/api/generate"
# MODEL_NAME = "llama3.1:8b"


# def repair_json_fallback(text: str) -> str:
#     start = text.find("{")
#     if start == -1:
#         raise ValueError("No JSON found")

#     snippet = text[start:]

#     # Balance braces
#     open_braces = snippet.count("{")
#     close_braces = snippet.count("}")

#     if close_braces < open_braces:
#         snippet += "}" * (open_braces - close_braces)

#     # Remove trailing commas
#     snippet = snippet.replace(",}", "}").replace(",]", "]")

#     return snippet


# def extract_json_block(text: str) -> str:
#     """Extract JSON by tracking brace depth (no regex)"""
#     start = text.find("{")
#     if start == -1:
#         raise ValueError("No JSON start found")

#     depth = 0
#     for i in range(start, len(text)):
#         if text[i] == "{":
#             depth += 1
#         elif text[i] == "}":
#             depth -= 1
#             if depth == 0:
#                 return text[start:i + 1]

#     raise ValueError("Unclosed JSON object")


# def call_llm_json(prompt: str, timeout: int = 90) -> dict:
#     """
#     Call Ollama's generate endpoint and extract JSON.
#     Fixed: Using 'prompt' parameter instead of 'messages'.
#     """
    
#     # Build the complete prompt with system instructions
#     full_prompt = f"""You are a strict information extraction system.
# Return ONLY one valid JSON object.
# No explanations. No extra text. No markdown.

# {prompt}"""

#     payload = {
#         "model": MODEL_NAME,
#         "prompt": full_prompt,  # ✅ Fixed: use 'prompt' not 'messages'
#         "stream": False,
#         "options": {
#             "temperature": 0,
#             "num_ctx": 2048,
#             "num_predict": 300
#         }
#     }

#     try:
#         response = requests.post(
#             OLLAMA_URL,
#             json=payload,
#             timeout=timeout
#         )
#         response.raise_for_status()

#         data = response.json()
#         raw_text = data.get("response", "").strip()
        
#         logger.debug(f"Raw LLM output: {raw_text[:200]}...")

#         # Try primary parse
#         try:
#             json_text = extract_json_block(raw_text)
#             return json.loads(json_text)
#         except Exception:
#             # Fallback repair
#             repaired = repair_json_fallback(raw_text)
#             return json.loads(repaired)

#     except Exception as e:
#         logger.error(f"LLM JSON call failed: {e}", exc_info=True)
#         return {}


def call_llm(prompt: str, timeout: int = 300) -> str:
    """
    Call Ollama local LLM and return plain text response.
    """

    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.3,
            "num_predict": 512
        }
    }

    try:
        response = requests.post(
            OLLAMA_URL,
            json=payload,
            timeout=timeout
        )
        response.raise_for_status()

        return response.json().get("response", "").strip()

    except Exception as e:
        logger.error(f"LLM text call failed: {e}")
        return "Explanation unavailable due to LLM service issue."

