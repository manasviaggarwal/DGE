
AI-Driven Social Support Eligibility & Enablement System
Overview
This project implements an AI-driven, agentic decision support system for evaluating applications for economic social support and economic enablement programs. It combines classical ML, GenAI, and agent-based orchestration to provide transparent, auditable decisions.
Key Capabilities
- Application assessment based on income, employment history, family size, wealth, and demographics.
- Decisions: APPROVE, SOFT_DECLINE, REJECT.
- Economic enablement recommendations (training, job matching, counseling).
- Transparent AI explanations for every decision.
Architecture
The system follows a modular agentic pipeline:
User Input → Document Ingestion → GenAI Extraction → Validation → Readiness Check → ML Eligibility Model → Enablement Recommendation → LLM Reasoning.
Technology Stack
- Scikit-learn (Random Forest)
- Generative AI (LLM)
- Streamlit UI
- Agent-based orchestration
Running the Application
1.	Clone the repository
2.	Create and activate virtual environment
3.	Install requirements
4.	Configure .env
5.	Run: streamlit run main.py

Local GenAI Setup (Ollama)
This system uses a locally hosted Large Language Model (LLM) via Ollama for: 
- Structured information extraction from text and documents
- Identifying missing application details
- Generating transparent, human-readable decision explanations
Step 1: Install Ollama
Download and install Ollama from: https://ollama.com
Step 2: Pull the required model via terminal
ollama pull llama3.1:8b
Step 3: Start Ollama
Ollama runs automatically in the background after installation. By default, it exposes a local API at: http://localhost:11434/api/generate
Step 4: Verify Ollama is running
ollama list

How to Run the Application
1.	Clone the Repository
      git clone <repo-url> cd ai-social-support-system
2.	Create a Virtual Environment
python -m venv venv
source venv/bin/activate        # macOS/Linux
venv\Scripts\activate           # Windows
3.	Install Dependencies
      pip install -r requirements.txt
4.	Start the local GenAI backend (Ollama)
               ollama pull llama3.1:8b
5.	Run the App
      streamlit run main.py

The application will open in your browser.

Security & Privacy
The system runs fully locally, with no external API calls, ensuring applicant data privacy.
Future Improvements
- Policy rule engine
- Fairness audits
- Multilingual support
- Human-in-the-loop review
Submission Notes
This solution fulfills all stated requirements including ML + GenAI integration, multimodal data handling, transparent decisions, and economic enablement support.
