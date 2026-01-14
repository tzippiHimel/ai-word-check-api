from fastapi import FastAPI
from pydantic import BaseModel
import requests
import os

app = FastAPI()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

API_URL = (
    "https://generativelanguage.googleapis.com/v1beta/models/"
    "gemini-flash-2.5:generateContent"
)

class AIRequest(BaseModel):
    text_to_ai: str
    word_to_check: str


@app.post("/ai-check")
def ai_check(data: AIRequest):
    payload = {
        "contents": [
            {
                "parts": [
                    {"text": data.text_to_ai}
                ]
            }
        ],
        # חשוב: כופה יצירת טקסט
        "generationConfig": {
            "temperature": 0.7,
            "maxOutputTokens": 256
        }
    }

    try:
        response = requests.post(
            f"{API_URL}?key={GEMINI_API_KEY}",
            json=payload,
            timeout=30
        )
        result = response.json()
    except Exception:
        return {
            "ai_response": "",
            "word_to_check": data.word_to_check,
            "found": False
        }

    # שליפה יציבה של הטקסט
    ai_text = ""
    try:
        candidates = result.get("candidates", [])
        if candidates:
            candidate = candidates[0]
            parts = candidate.get("content", {}).get("parts", [])
            texts = [p.get("text", "") for p in parts if isinstance(p, dict) and p.get("text")]
            ai_text = " ".join(texts).strip()

            # אם המודל סיים בלי טקסט (safety / empty)
            finish_reason = candidate.get("finishReason", "")
            if not ai_text and finish_reason:
                ai_text = ""
    except Exception:
        ai_text = ""

    # Fallback ברור – מבטיח שלא תקבלי מחרוזת ריקה
    if not ai_text:
        ai_text = "The AI did not generate textual output for this request."

    found = data.word_to_check.lower() in ai_text.lower()

    return {
        "ai_response": ai_text,
        "word_to_check": data.word_to_check,
        "found": found
    }
