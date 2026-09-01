ZYNOVEA — Autonomous Clinical Voice AI Engine

ZYNOVEA is a low-latency, real-time voice-AI clinical assistant designed to handle patient inquiries, appointment scheduling, and administrative clinic workflows. Built with a deterministic safety firewall, ZYNOVEA immediately intercepts medical emergencies and clinical advice requests, escalating them to human physicians before reaching the LLM layer.

.

🌟 Key Features
Real-Time Voice Pipeline: Bi-directional streaming with sub-second response times using WebSockets and the Web Speech API.

Deterministic Safety Firewall: Zero-latency regex triage layer that intercepts acute emergencies (e.g., chest pain, respiratory distress) and clinical advice requests (e.g., medication, diagnoses), routing them directly to human physicians.

Semantic RAG Memory: Vector search powered by Qdrant (with embedded in-memory fallback) to retrieve clinic operating hours, doctor schedules, and patient context.

High-Speed Inference: Ultra-fast LLM completion via Groq for conversational responses.

Vocal Synthesis: Lifelike voice synthesis powered by Rime TTS.

Unified Single-File UI: Embedded frontend served directly via FastAPI static mounting.

🏗️ Architecture Overview
[ Browser / Web Speech API ]
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

    📂 Project Structure
    ZYNOVEA/
├── backend/
│   ├── main.py              # FastAPI application, WebSocket server, safety filters
│   └── qdrant_helper.py     # Qdrant vector retrieval, embeddings, and in-memory fallback
├── frontend/
│   └── index.html           # Single-file frontend (HTML, CSS, Web Speech JS)
├── .env                     # API keys and environment variables (ignored in Git)
├── .gitignore               # Ignored files and directories
└── requirements.txt         # Project dependencies