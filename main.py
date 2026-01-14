from fastapi import FastAPI
from pydantic import BaseModel
import requests
import os

app = FastAPI()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

API_URL = (
    "https://generativelanguage.googleapis.com/v1beta/models/"
    "gemini-pro:generateContent"
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

    response = requests.post(
        f"{API_URL}?key={GEMINI_API_KEY}",
        json=payload,
        timeout=30
    )

    result = response.json()

    try:
        ai_text = result["candidates"][0]["content"]["parts"][0]["text"]
    except Exception:
        ai_text = ""

    found = data.word_to_check.lower() in ai_text.lower()

    return {
        "ai_response": ai_text,
        "word_to_check": data.word_to_check,
        "found": found
    }
