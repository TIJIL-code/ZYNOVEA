import os
import sys
from pathlib import Path

# Ensure the backend directory is in sys.path before local imports
BACKEND_DIR = Path(__file__).resolve().parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

import re
import json
import asyncio
import httpx
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
from groq import AsyncGroq
from qdrant_helper import search_memory

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
RIME_API_KEY = os.getenv("RIME_API_KEY")

groq_client = AsyncGroq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

app = FastAPI(title="ZYNOVEA Voice AI Engine")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Emergency & Clinical Safety Filters
EMERGENCY_TRIGGERS = [
    r"can't breathe", r"cannot breathe", r"shortness of breath", r"hard to breathe",
    r"chest pain", r"heart attack", r"stroke", r"fainted", r"unconscious",
    r"severe pain", r"bleeding", r"dying", r"emergency", r"help me breathe"
]

CLINICAL_TRIGGERS = [
    r"medicine", r"medication", r"prescribe", r"dosage", r"pill", r"cough",
    r"drug", r"treatment", r"side effect", r"symptom", r"diagnosis",
    r"what should i take", r"recommend a drug"
]

def evaluate_safety_firewall(text: str) -> str:
    lowered = text.lower()
    for pattern in EMERGENCY_TRIGGERS:
        if re.search(pattern, lowered):
            return "EMERGENCY"
    for pattern in CLINICAL_TRIGGERS:
        if re.search(pattern, lowered):
            return "CLINICAL"
    return "SAFE"

async def synthesize_rime_tts(text: str) -> bytes:
    if not RIME_API_KEY or RIME_API_KEY == "your_rime_api_key_here":
        return b""
    try:
        async with httpx.AsyncClient(timeout=4.0) as client:
            response = await client.post(
                "https://users.rime.ai/v1/rime-tts",
                json={"speaker": "eva", "text": text, "modelId": "mistv3", "audioFormat": "mp3"},
                headers={"Authorization": f"Bearer {RIME_API_KEY}"}
            )
            if response.status_code == 200:
                return response.content
    except Exception as e:
        print(f"Rime TTS Warning: {e}")
    return b""

@app.websocket("/ws/call")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("⚡ Client connected over WebSocket")

    greeting_text = "Welcome to ZYNOVEA Clinic! How can I help you today?"
    audio_bytes = await synthesize_rime_tts(greeting_text)

    await websocket.send_json({
        "type": "bot_response",
        "text": greeting_text,
        "escalated": False,
        "has_audio": len(audio_bytes) > 0
    })

    if audio_bytes:
        await websocket.send_bytes(audio_bytes)

    try:
        while True:
            data = await websocket.receive_text()
            try:
                message = json.loads(data)
            except Exception:
                message = {"type": "user_transcript", "text": data}

            if message.get("type") in ("user_transcript", "transcript"):
                user_text = message.get("text", "").strip()
                if not user_text:
                    continue

                print(f"🎙️ User said: {user_text}")

                safety_status = evaluate_safety_firewall(user_text)

                if safety_status == "EMERGENCY":
                    alert_text = "Emergency detected! Stay on the line while I transfer your call directly to emergency response."
                    audio_bytes = await synthesize_rime_tts(alert_text)
                    
                    await websocket.send_json({
                        "type": "bot_response",
                        "text": alert_text,
                        "escalated": True,
                        "doctor_name": "🚨 EMERGENCY TRIAGE & ATTENDING PHYSICIAN",
                        "has_audio": len(audio_bytes) > 0
                    })
                    if audio_bytes:
                        await websocket.send_bytes(audio_bytes)
                    continue

                elif safety_status == "CLINICAL":
                    clinical_text = "I am an administrative assistant. Transferring your call to our attending physician for medical advice."
                    audio_bytes = await synthesize_rime_tts(clinical_text)
                    
                    await websocket.send_json({
                        "type": "bot_response",
                        "text": clinical_text,
                        "escalated": True,
                        "doctor_name": "Dr. Sarah Harrison (Attending Physician)",
                        "has_audio": len(audio_bytes) > 0
                    })
                    if audio_bytes:
                        await websocket.send_bytes(audio_bytes)
                    continue

                context = await asyncio.to_thread(search_memory, user_text)

                system_prompt = (
                    "You are ZYNOVEA, a concise administrative receptionist for a medical clinic. "
                    "Assist with clinic hours, location, and appointment booking based on the context. "
                    "Respond directly in 1 to 2 clear, helpful sentences.\n"
                    f"Clinic Context:\n{context}"
                )

                if not groq_client:
                    bot_text = "Groq API key is not configured. Please add GROQ_API_KEY to your .env file."
                else:
                    try:
                        completion = await groq_client.chat.completions.create(
                            model="openai/gpt-oss-20b",
                            messages=[
                                {"role": "system", "content": system_prompt},
                                {"role": "user", "content": user_text}
                            ],
                            temperature=0.3,
                            max_tokens=250
                        )
                        raw_content = completion.choices[0].message.content
                        bot_text = raw_content.strip() if raw_content else ""
                    except Exception as err:
                        print(f"Groq API call failed: {err}")
                        bot_text = "We are open Monday to Friday from 8:00 AM to 6:00 PM. How can I assist you with scheduling?"

                if not bot_text:
                    bot_text = "We are open Monday to Friday from 8:00 AM to 6:00 PM. How can I help you today?"

                print(f"🤖 ZYNOVEA: {bot_text}")
                audio_bytes = await synthesize_rime_tts(bot_text)

                await websocket.send_json({
                    "type": "bot_response",
                    "text": bot_text,
                    "escalated": False,
                    "has_audio": len(audio_bytes) > 0
                })

                if audio_bytes:
                    await websocket.send_bytes(audio_bytes)

    except WebSocketDisconnect:
        print("🔌 Client disconnected")
    except Exception as e:
        print(f"❌ Error: {e}")

# Mount static frontend directory
FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"
if FRONTEND_DIR.exists():
    app.mount("/", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="frontend")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)