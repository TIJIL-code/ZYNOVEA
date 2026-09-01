ZYNOVEA — Autonomous Clinical Voice AI EngineZYNOVEA is a low-latency, real-time voice-AI clinical assistant designed to handle patient inquiries, appointment scheduling, and administrative clinic workflows. Built with a deterministic safety firewall, ZYNOVEA immediately intercepts medical emergencies and clinical advice requests, escalating them to human physicians before reaching the LLM layer.🌟 Key FeaturesReal-Time Voice Pipeline: Bi-directional streaming with sub-second response times using WebSockets and the Web Speech API.Deterministic Safety Firewall: Zero-latency regex triage layer that intercepts acute emergencies (e.g., chest pain, respiratory distress) and clinical advice requests (e.g., medication, diagnoses), routing them directly to human physicians.Semantic RAG Memory: Vector search powered by Qdrant (with embedded in-memory fallback) to retrieve clinic operating hours, doctor schedules, and patient context.High-Speed Inference: Ultra-fast LLM completion via Groq for conversational responses.Vocal Synthesis: Lifelike voice synthesis powered by Rime TTS.Unified Single-File UI: Embedded frontend served directly via FastAPI static mounting.
🏗️ Architecture OverviewPlaintext[ Browser / Web Speech API ]
            │ (WebSocket)
            ▼
   [ FastAPI Backend ]
            │
   [ Safety Firewall ] ──(Emergency/Clinical Trigger)──► [ Immediate Escalation UI ]
            │ (Safe Admin Query)
            ▼
  [ Qdrant Vector DB ] ──(Clinic Schedule / Context)
            │
            ▼
      [ Groq LLM ]
            │
            ▼
    [ Rime Voice TTS ] ──(Audio Stream)──► [ User Audio Playback ]


📂 Project StructurePlaintextZYNOVEA/
├── backend/
│   ├── main.py              # FastAPI application, WebSocket server, safety filters
│   └── qdrant_helper.py     # Qdrant vector retrieval, embeddings, and in-memory fallback
├── frontend/
│   └── index.html           # Single-file frontend (HTML, CSS, Web Speech JS)
├── .env                     # API keys and environment variables (ignored in Git)
├── .gitignore               # Ignored files and directories
└── requirements.txt         # Project dependencies
🚀 Getting Started1. PrerequisitesPython 3.10+Google Chrome or Microsoft Edge (for Web Speech API support)A Groq API key (Groq Console)(Optional) A Rime TTS API key (Rime AI)2. InstallationClone the repository:Bashgit clone https://github.com/TIJIL-code/ZYNOVEA.git
cd ZYNOVEA
Create and activate a virtual environment:PowerShell# Windows (PowerShell)
python -m venv venv
.\venv\Scripts\Activate.ps1

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
Install dependencies:Bashpip install -r requirements.txt
3. Environment ConfigurationCreate a .env file in the root directory:Code snippetGROQ_API_KEY=your_groq_api_key_here
RIME_API_KEY=your_rime_api_key_here
(Note: If RIME_API_KEY is not provided, the assistant will seamlessly operate in text-transcript mode without vocal synthesis).4. Running the ServerStart the FastAPI application with Uvicorn:Bashuvicorn backend.main:app --reload --port 8000
5. Accessing the Web InterfaceOpen your browser and navigate to:Plaintexthttp://127.0.0.1:8000
Click Start Call and grant microphone permissions when prompted.Begin speaking into your microphone.🧪 Example Test ScenariosUser PromptSystem BehaviorExpected Result"What are your clinic hours?"Safe Administrative QueryQdrant retrieves hours; Groq returns concise answer."Can I schedule an appointment with Dr. Smith?"Safe Scheduling QueryContextual answer based on doctor availability."I am having severe chest pain."EMERGENCY Firewall TriggerImmediate red escalation banner and triage transfer alert."Can you prescribe me medication for a cough?"CLINICAL Firewall TriggerImmediate transfer to attending physician.🛠️ Tech StackBackend: FastAPI, Uvicorn, WebSockets, HTTPXVector Store & Embeddings: Qdrant Client, sentence-transformers (all-MiniLM-L6-v2)LLM Inference: Groq SDKSpeech Synthesis: Rime TTS APIClient Interface: HTML5, CSS3, Web Speech API (webkitSpeechRecognition), Web Audio API