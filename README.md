<div align="center">

# 🩺 ZYNOVEA
### *Autonomous Voice-AI Clinical Assistant with Zero-Latency Safety Triage*

[![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Groq](https://img.shields.io/badge/Groq-Fast_Inference-f55036?style=for-the-badge)](https://groq.com)
[![Qdrant](https://img.shields.io/badge/Qdrant-Vector_RAG-dc2626?style=for-the-badge&logo=qdrant&logoColor=white)](https://qdrant.tech)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)

<p align="center">
  A real-time, bi-directional voice agent tailored for healthcare clinics.<br>
  Equipped with a deterministic safety firewall that intercepts critical emergencies and clinical inquiries instantly.
</p>

---

</div>

## 📌 Key Highlights

* ⚡ **Ultra-Low Latency Voice Pipeline:** Full-duplex WebSocket architecture integrated with the browser Web Speech API.
* 🛡️ **Deterministic Safety Firewall:** Zero-latency regex interception for critical emergencies (*e.g., chest pain, respiratory distress*) and clinical inquiries (*e.g., drug prescriptions, symptom triage*).
* 🧠 **Semantic Vector Memory (RAG):** Powered by **Qdrant** with automatic in-memory fallback for retrieving operating hours, doctor schedules, and patient context.
* 🚀 **Fast LLM Generation:** Ultra-fast sub-second token streaming powered by **Groq**.
* 🗣️ **Vocal Synthesis:** Embedded text-to-speech rendering powered by **Rime TTS**.
* 🌐 **Self-Contained UI:** Zero-build single-file web client served natively via FastAPI static mounting.

---

## 🏗️ System Architecture

```text
       ┌──────────────────────────────┐
       │ Browser Web Speech Interface │
       └──────────────┬───────────────┘
                      │ (WebSocket /ws/call)
                      ▼
             ┌─────────────────┐
             │ FastAPI Backend │
             └────────┬────────┘
                      │
       ┌──────────────┴──────────────┐
       │  Deterministic Safety Gate  │
       └──────┬───────────────┬──────┘
              │               │
     [Emergency/Clinical]  [Safe Admin Query]
              │               │
              ▼               ▼
     ┌─────────────────┐     ┌──────────────────────┐
     │ Instant Physician│    │ Qdrant Vector Search │
     │  Escalation UI  │     └──────────┬───────────┘
     └─────────────────┘                │
                                        ▼
                             ┌──────────────────────┐
                             │    Groq Inference    │
                             └──────────┬───────────┘
                                        │
                                        ▼
                             ┌──────────────────────┐
                             │    Rime Voice TTS    │
                             └──────────┬───────────┘
                                        │ (MP3 Stream)
                                        ▼
                             ┌──────────────────────┐
                             │ Audio Playback to UI │
                             └──────────────────────┘

🧰 Technology Stack
Server Framework: FastAPI + Uvicorn

Real-Time Transport: WebSockets + HTTPX

Embeddings & Search: Qdrant + Sentence-Transformers (all-MiniLM-L6-v2)

LLM Engine: Groq Cloud

Speech Synthesis: Rime TTS