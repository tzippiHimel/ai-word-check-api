from fastapi import FastAPI
from pydantic import BaseModel
import requests
import os

app = FastAPI()

# Gemini API key (להגדיר ב-Render כ-Environment Variable)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Gemini Flash 2.5 endpoint
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
        ]
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

    # שליפה יציבה של הטקסט (Gemini יכול להחזיר כמה parts)
    ai_text = ""
    try:
        candidates = result.get("candidates", [])
        if candidates:
            parts = candidates[0].get("content", {}).get("parts", [])
            texts = [p.get("text", "") for p in parts if "text" in p]
            ai_text = " ".join(texts)
    except Exception:
        ai_text = ""

    found = data.word_to_check.lower() in ai_text.lower()

    return {
        "ai_response": ai_text,
        "word_to_check": data.word_to_check,
        "found": found
    }
