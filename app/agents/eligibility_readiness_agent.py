REQUIRED_FIELDS = [
    "income",
    "employment_status",
    "family_size",
]

def eligibility_readiness_agent(state):
    validated = state.get("validated_data", {})
    missing = [f for f in REQUIRED_FIELDS if validated.get(f) is None]

    state["eligibility_readiness"] = {
        "status": "ready" if not missing else "insufficient_data",
        "missing_fields": missing,
    }
    return state
