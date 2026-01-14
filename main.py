from fastapi import FastAPI
from pydantic import BaseModel
import requests
import os

app = FastAPI()

# Gemini API key (מוגדר ב-Render כ-Environment Variable)
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
    # פרומפט שמכריח החזרת טקסט
    prompt_text = (
        "Answer in plain text. "
        "Return a clear textual answer.\n\n"
        f"{data.text_to_ai}"
    )

    payload = {
        "contents": [
            {
                "parts": [
                    {"text": prompt_text}
                ]
            }
        ],
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
        # הגנה מוחלטת – אף פעם לא מחזיר 500
        ai_text = "The AI service is currently unavailable."
        found = data.word_to_check.lower() in ai_text.lower()
        return {
            "ai_response": ai_text,
            "word_to_check": data.word_to_check,
            "found": found
        }

    # שליפה יציבה של הטקסט מג'מיני
    ai_text = ""
    try:
        candidates = result.get("candidates", [])
        if candidates:
            parts = candidates[0].get("content", {}).get("parts", [])
            texts = [
                p.get("text", "")
                for p in parts
                if isinstance(p, dict) and p.get("text")
            ]
            ai_text = " ".join(texts).strip()
    except Exception:
        ai_text = ""

    # Fallback אם המודל החזיר תשובה ריקה
    if not ai_text:
        ai_text = "The AI did not generate textual output for this request."

    found = data.word_to_check.lower() in ai_text.lower()

    return {
        "ai_response": ai_text,
        "word_to_check": data.word_to_check,
        "found": found
    }
