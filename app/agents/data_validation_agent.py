from typing import Dict, Any
import logging

logger = logging.getLogger("DataValidationAgent")

def data_validation_agent(state: Dict[str, Any]) -> Dict[str, Any]:
    extracted = state.get("extracted_data", {})
    validated = {}

    def val(k):
        v = extracted.get(k, {}).get("value")
        return v if v is not None else None

    validated["income"] = val("income")
    validated["family_size"] = val("family_size")
    validated["employment_years"] = val("employment_years")
    validated["employment_status"] = val("employment_status")
    validated["education_level"] = val("education_level")
    validated["assets"] = val("assets")
    validated["liabilities"] = val("liabilities")

    state["validated_data"] = validated
    logger.info(f"Validated data (preserving missing): {validated}")
    return state
