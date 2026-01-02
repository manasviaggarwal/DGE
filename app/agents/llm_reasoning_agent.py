# from app.llm.llm_client import call_llm

# def llm_reasoning_agent(state):
#     signals = state["eligibility_signals"]
#     eligibility = state["eligibility"]
#     recommendation = state.get("recommendation", {})

#     prompt = f"""
# You are generating a factual explanation for a government eligibility decision for Economic Social Support. 
# Assess applications based on criteria such as income level, employment history,
# family size, wealth assessment and demographic profile to determine eligibility for
# financial support and economic enablement support. Also, suggest economic enablement support (e.g., upskilling and
# training opportunities, job matching, career counseling).
# Interpret the model signals and explain in simple terms to the user. If the decision cannot be made due to insufficient information, you can mention that. 
# But interpret properly.

# IMPORTANT:
# - You are EXPLAINING a decision, not re-evaluating it.
# - You must reflect the model's logic exactly.
# STRICT RULES:
# - You must NOT invent reasons.
# - You must NOT assume financial sufficiency.
# - You must explain ONLY using the signals provided.
# - You must reflect the model's logic exactly.
# - If something is unknown, say so explicitly.
# - Do not hallucinate the outcome.


# MODEL SIGNALS:
# {signals}

# FINAL DECISION:
# {eligibility}

# Explain in this structure:

# Decision Summary:
# - State the decision clearly.

# Key Signals:
# - List which signals were relevant.

# Decision Logic:
# - Explicitly explain which rule was triggered.

# Enablement Support:
# - ONLY describe enablement support if it is explicitly present in the recommendation object.
# - If no enablement support is present, explicitly state that no enablement support was recommended.
# - You MUST NOT suggest or infer any enablement actions.


# Next Steps:
# - Neutral guidance.

# Do NOT add any new criteria.
# """

#     state["llm_explanation"] = call_llm(prompt)
#     return state


# def llm_reasoning_agentold(state):
#     validated = state["validated_data"]
#     eligibility = state["eligibility"]
#     recommendation = state.get("recommendation", {})

#     prompt = f"""
# You are an AI system that explains decisions made by an ML eligibility system. Please explain if the candidate is eligible for Economic Social Support. Also, suggest Enablement Recommendation.
# Also always show the actual Economic Social Support Decision.
# IMPORTANT RULES:
# - Do NOT invent policy reasons.
# - Do NOT introduce new criteria.
# - Explain ONLY using the data and outcomes provided.
# - If something is unknown, say so explicitly.
# - Do not hallucinate the outcome.

# Validated Applicant Data:
# {validated}

# Economic Social Support Decision:
# {eligibility}

# Enablement Recommendation:
# {recommendation}

# Write a clear, neutral explanation covering:

# 1. What decision was made
# 2. Which input factors were considered
# 3. Why the decision outcome followed from those factors
# 4. What enablement support (if any) is suggested
# 5. What the applicant can do next

# Keep the explanation factual and transparent.
# """

#     state["llm_explanation"] = call_llm(prompt)
#     return state


from app.llm.llm_client import call_llm


def dedupe_lines(text, max_lines=20):
    seen = set()
    unique = []

    for l in text.splitlines():
        sig = hash(l.lower()[:40])
        if sig not in seen:
            seen.add(sig)
            unique.append(l.strip())
        if len(unique) >= max_lines:
            break

    return "\n".join(unique)


from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np

def tfidf_compact(text, max_sentences=10, max_chars=800):
    sentences = [s.strip() for s in text.splitlines() if len(s.strip()) > 10]

    if len(sentences) <= max_sentences:
        return "\n".join(sentences)

    vectorizer = TfidfVectorizer(stop_words="english")
    X = vectorizer.fit_transform(sentences)

    scores = np.asarray(X.sum(axis=1)).ravel()
    top_idx = scores.argsort()[::-1][:max_sentences]

    selected = [sentences[i] for i in sorted(top_idx)]
    return "\n".join(selected)[:max_chars]


def llm_reasoning_agent(state):
    signals = state["eligibility_signals"]
    eligibility = state["eligibility"]
    recommendation = state.get("recommendation", {})
    context = state.get("llm_context", {})
    # clean = preprocess_text(context)
    clean = dedupe_lines(context)
    context = tfidf_compact(clean)


    # print('999999/999999999999999999999999999999999999999999999999999')
    # print(context)

    prompt = f"""
You are generating a factual explanation for a government eligibility decision
for Economic Social Support.

You are NOT deciding eligibility.
You are NOT re-evaluating the application.

Your task:
1. Explain the eligibility decision using model signals.
2. If the decision is APPROVE or SOFT_DECLINE, recommend economic enablement
   support using the provided applicant context.

IMPORTANT RULES:
- You must reflect the model logic exactly.
- Do NOT invent facts.
- Do NOT assume missing information.
- Use applicant context ONLY for enablement suggestions.
- If context is insufficient, explicitly say so.

MODEL SIGNALS:
{signals}

FINAL DECISION:
{eligibility}

APPLICANT CONTEXT (for enablement only):
{context}

Explain in this structure:

Decision Summary:
- State the decision clearly.

Key Signals:
- List which signals were relevant.

Decision Logic:
- Explicitly explain which rule was triggered.

Enablement Support:
- Suggest up to 3 actions (training, job matching, counseling)
- ONLY if decision allows it
- Ground suggestions in applicant context
- If insufficient info, say so explicitly

Next Steps:
- Neutral guidance.

Do NOT add new criteria.
"""

    state["llm_explanation"] = call_llm(prompt)
    return state
