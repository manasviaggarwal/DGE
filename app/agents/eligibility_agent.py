from app.models.eligibility_model import predict_eligibility

def eligibility_agent(state):
    readiness = state["eligibility_readiness"]
    v = state["validated_data"]

    if readiness["status"] != "ready":
        state["eligibility"] = {
            "decision": "MANUAL_REVIEW",
            "reason": "Missing critical information",
        }
        return state

    # -------------------------------
    # MODEL INPUT (safe defaults)
    # -------------------------------
    model_input = {
        "income": v.get("income") if v.get("income") is not None else 0,
        "family_size": v.get("family_size") if v.get("family_size") is not None else 1,
        "employment_years": v.get("employment_years") if v.get("employment_years") is not None else 0,
        "employment_status": v.get("employment_status") or "unknown",
        "education_level": v.get("education_level") or "unknown",
        "assets": v.get("assets") if v.get("assets") is not None else 0,
        "liabilities": v.get("liabilities") if v.get("liabilities") is not None else 0,
    }

    decision, prob = predict_eligibility(model_input)

    # -------------------------------
    # MODEL SIGNALS (truthful)
    # -------------------------------
    income_pc = (
        v["income"] / v["family_size"]
        if v.get("income") is not None and v.get("family_size") not in (None, 0)
        else None
    )

    net_worth = (
        v["assets"] - v["liabilities"]
        if v.get("assets") is not None and v.get("liabilities") is not None
        else None
    )

    state["eligibility"] = {
        "decision": decision,
        "probability": round(prob, 3),
        "reason": "ML-based eligibility assessment",
    }

    state["eligibility_signals"] = {
        "income": v.get("income"),
        "family_size": v.get("family_size"),
        "income_per_capita": income_pc,
        "employment_status": v.get("employment_status"),
        "employment_years": v.get("employment_years"),
        "education_level": v.get("education_level"),
        "assets": v.get("assets"),
        "liabilities": v.get("liabilities"),
        "net_worth": net_worth,

        # Explicit model logic exposure
        "rule_low_income_pc": income_pc is not None and income_pc < 12000,
        "rule_unemployed_low_income": (
            income_pc is not None
            and income_pc < 18000
            and v.get("employment_status") != "employed"
        ),
        "rule_negative_net_worth_unemployed": (
            net_worth is not None
            and net_worth < 0
            and v.get("employment_status") != "employed"
        ),
    }

    return state
