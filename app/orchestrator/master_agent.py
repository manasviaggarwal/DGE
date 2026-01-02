from langgraph.graph import StateGraph, END

from app.agents.eligibility_agent import eligibility_agent
from app.agents.enablement_agent import enablement_agent
from app.agents.llm_reasoning_agent import llm_reasoning_agent


# --------------------------------------------------
# Master Orchestrator
# --------------------------------------------------
def build_master_agent():
    """
    Orchestrates the final decision-making pipeline:
    1. Eligibility decision (ML-based)
    2. Economic enablement recommendation (policy-based)
    3. Human-readable explanation (LLM)
    """

    g = StateGraph(dict)

    # -------------------------
    # Nodes
    # -------------------------
    g.add_node("eligibility", eligibility_agent)
    g.add_node("enablement", enablement_agent)
    g.add_node("reasoning", llm_reasoning_agent)

    # -------------------------
    # Flow
    # -------------------------
    g.set_entry_point("eligibility")
    g.add_edge("eligibility", "enablement")
    g.add_edge("enablement", "reasoning")
    g.add_edge("reasoning", END)

    return g.compile()


# --------------------------------------------------
# Public API
# --------------------------------------------------

def run_application_flow(state):
    agent = build_master_agent()
    final_state = agent.invoke(state)

    eligibility = final_state.get("eligibility", {})
    enablement = final_state.get("enablement", {})

    return {
        "chat_response": (
            f"### Eligibility Decision\n"
            f"**Status:** {eligibility.get('decision', 'MANUAL_REVIEW')}\n\n"
            f"**Reason:** {eligibility.get('reason', 'N/A')}"
        ),
        "enablement": enablement,
        "llm_explanation": final_state.get("llm_explanation"),
    }



def run_application_flow_old(state):#validated_data, readiness):
    """
    Entry point used by Streamlit UI.
    """

    agent = build_master_agent()

    final_state = agent.invoke({
        "validated_data": validated_data,
        "eligibility_readiness": readiness,
    })

    eligibility = final_state.get("eligibility", {})
    enablement = final_state.get("enablement", {})

    return {
        "chat_response": (
            f"### Eligibility Decision\n"
            f"**Status:** {eligibility.get('decision', 'MANUAL_REVIEW')}\n\n"
            f"**Reason:** {eligibility.get('reason', 'N/A')}"
        ),
        "enablement": enablement,
        "llm_explanation": final_state.get("llm_explanation"),
    }
