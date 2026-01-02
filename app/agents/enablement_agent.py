def enablement_agent(state):
    v = state["validated_data"]
    decision = state["eligibility"]["decision"]

    enablement = {
        "training": False,
        "job_matching": False,
        "career_counseling": False,
        "reasons": []
    }

    if decision in {"SOFT_DECLINE", "REJECT"}:
        if v["employment_status"] != "employed":
            enablement["job_matching"] = True
            enablement["reasons"].append("Unstable or no employment")

        if v["education_level"] in {"unknown", "high_school"}:
            enablement["training"] = True
            enablement["reasons"].append("Low education level")

        enablement["career_counseling"] = True
        enablement["reasons"].append("Needs long-term economic support")

    state["enablement"] = enablement
    return state
