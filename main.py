from dotenv import load_dotenv
load_dotenv()

import streamlit as st
import uuid

from app.agents.document_ingestion_agent import document_ingestion_agent
from app.agents.data_extraction_agent import data_extraction_agent
from app.agents.data_validation_agent import data_validation_agent
from app.agents.eligibility_readiness_agent import eligibility_readiness_agent
from app.orchestrator.master_agent import run_application_flow

st.set_page_config(
    page_title="AI Social Support Assessment",
    layout="wide"
)

# --------------------------------------------------
# Session Initialization
# --------------------------------------------------
def init():
    defaults = {
        "phase": "INTRO",
        "chat_history": [],
        "text_buffer": [],
        "validated_data": None,
        "readiness": None,
        "uploader_key": uuid.uuid4().hex,
        "assessment_started": False,
        "processing_done": False,  # NEW: prevents re-running agents
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init()

# --------------------------------------------------
# HEADER
# --------------------------------------------------
st.title("🤖 AI Social Support Assessment")

st.markdown("""
This service helps assess eligibility for **financial assistance** and recommends
**economic enablement support** such as training, job matching, or career counseling.

### You can provide information in two ways:
- 📄 Upload documents (ID, payslips, bank statements, resume)
- ✍️ Type information in plain language

**Example:**
> *salary 6000, employed, 2 dependents*
""")

st.divider()

# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------
with st.sidebar:
    if st.button("🚀 Start New Application"):
        st.session_state.clear()
        st.rerun()

# --------------------------------------------------
# FILE UPLOAD
# --------------------------------------------------
uploaded_files = st.file_uploader(
    "Upload documents (PDF, Image, Excel)",
    accept_multiple_files=True,
    key=st.session_state.uploader_key
)

# --------------------------------------------------
# CHAT INPUT
# --------------------------------------------------
msg = st.chat_input("Add information (optional)")

if msg:
    st.session_state.chat_history.append({
        "role": "user",
        "content": msg
    })
    st.session_state.text_buffer.append(msg)
    st.session_state.processing_done = False  # Need to reprocess with new info

# --------------------------------------------------
# RENDER CHAT FIRST (before buttons)
# --------------------------------------------------
for m in st.session_state.chat_history:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

# --------------------------------------------------
# START ASSESSMENT BUTTON
# --------------------------------------------------
if st.session_state.phase == "INTRO" and not st.session_state.assessment_started:
    if st.button("▶ Start Assessment"):
        st.session_state.assessment_started = True
        st.session_state.phase = "COLLECT"
        st.session_state.processing_done = False
        st.rerun()

# --------------------------------------------------
# COLLECT & PROCESS (only once per input)
# --------------------------------------------------
if st.session_state.phase == "COLLECT" and not st.session_state.processing_done:
    
    # Show processing message
    with st.chat_message("assistant"):
        st.markdown("We're reviewing the information you provided. This usually takes a few seconds.")
    
    st.session_state.chat_history.append({
        "role": "assistant",
        "content": "We're reviewing the information you provided. This usually takes a few seconds."
    })
    
    # Run agents
    state = {
        "user_input": "\n".join(st.session_state.text_buffer),
        "uploaded_files": uploaded_files,
    }

    state = document_ingestion_agent(state)
    state = data_extraction_agent(state)
    state = data_validation_agent(state)
    state = eligibility_readiness_agent(state)

    st.session_state.validated_data = state["validated_data"]
    st.session_state.readiness = state["eligibility_readiness"]

    if state["eligibility_readiness"]["status"] == "ready":
        # Ready for decision - run it automatically
        result = run_application_flow(state) 
        #     validated_data=st.session_state.validated_data,
        #     readiness=st.session_state.readiness
        # )

        st.session_state.chat_history.append({
            "role": "assistant",
            "content": "We have sufficient information to evaluate your application."
        })
        
        st.session_state.chat_history.append({
            "role": "assistant",
            "content": result["chat_response"]
        })

        if result.get("llm_explanation"):
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": "### 🧠 Decision Explanation\n\n" + result["llm_explanation"]
            })

        st.session_state.phase = "DONE"
        st.session_state.processing_done = True

    else:
        # Need more info
        missing = state["eligibility_readiness"]["missing_fields"]
        st.session_state.chat_history.append({
            "role": "assistant",
            "content": (
                "We need a bit more information to continue.\n\n"
                "Please provide the following:\n"
                + "\n".join(f"• {m.replace('_',' ').title()}" for m in missing)
                + "\n\nYou can type it or upload another document."
            )
        })
        st.session_state.processing_done = True
        # Stay in COLLECT phase for next input
    
    st.rerun()