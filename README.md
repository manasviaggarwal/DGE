# AI-Driven Social Support Eligibility & Enablement System

## Overview
This project implements an **AI-driven, agentic decision support system** for evaluating applications for **economic social support** and **economic enablement programs**.  
It combines **classical machine learning**, **Generative AI**, and **agent-based orchestration** to deliver **transparent, auditable, and explainable decisions**.

---

## Key Capabilities
- Application assessment based on:
  - Income
  - Employment history
  - Family size
  - Wealth indicators
  - Demographic attributes
- Decision outcomes:
  - **APPROVE**
  - **SOFT_DECLINE**
  - **REJECT**
- Economic enablement recommendations:
  - Upskilling and training programs
  - Job matching
  - Career counseling
- Transparent, human-readable AI explanations for every decision

---

## System Architecture
The system follows a **modular agentic pipeline**:
**User Input**
→ Document Ingestion
→ GenAI Extraction
→ Data Validation
→ Readiness Check
→ ML Eligibility Model
→ Enablement Recommendation
→ LLM-Based Reasoning & Explanation


---

## Technology Stack
- **Machine Learning**: Scikit-learn (Random Forest)
- **Generative AI**: Locally hosted LLM
- **Frontend**: Streamlit
- **Orchestration**: Agent-based pipeline
- **Backend**: Python

---

# Local GenAI Setup (Ollama)

This system uses a locally hosted Large Language Model (LLM) via **Ollama** for:

- Structured information extraction from text and documents
- Detection of missing or inconsistent application details
- Generation of transparent, human-readable decision explanations

## Step 1: Install Ollama

Download and install Ollama from:

https://ollama.com

## Step 2: Pull the Required Model

ollama pull llama3.1:8b

## Step 3: Start Ollama

Ollama runs automatically in the background after installation.

By default, it exposes a local API at:

http://localhost:11434/api/generate

## Step 4: Verify Ollama is Running
ollama list

---

## Running the Application

# 1. Clone the Repository
git clone <repo-url> cd DGE

# 2. Create and Activate a Virtual Environment
To set up a Python virtual environment, run: python -m venv venv

### macOS / Linux:
source venv/bin/activate
### Windows
venv\Scripts\activate

## 3. Install Dependencies
pip install -r requirements.txt

## 4.	Start the local GenAI backend (Ollama)
ollama pull llama3.1:8b

## 5. Run the Application
streamlit run main.py

The application will open automatically in your browser.
---

## Security & Privacy

- The system runs fully locally
- No external API calls are made
- Applicant data remains private and secure


## Submission Notes

This solution fulfills all stated requirements, including:

- Integration of ML and Generative AI
- Multimodal data handling
- Agentic orchestration
- Transparent and explainable decision-making
- Economic enablement recommendations
