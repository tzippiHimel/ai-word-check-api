import os
import requests
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv

# load environment variables
load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise RuntimeError("GEMINI_API_KEY is not set")

GEMINI_MODEL = "gemini-1.5-flash"
GEMINI_URL = (
    f"https://generativelanguage.googleapis.com/v1beta/models/"
    f"{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}"
)

app = FastAPI(title="AI Word Check API")

class AIRequest(BaseModel):
    text_to_ai: str
    word_to_check: str

class AIResponse(BaseModel):
    ai_response: str
    word_to_check: str
    found: bool


def call_gemini(prompt: str) -> str:
    response = requests.post(
        GEMINI_URL,
        json={
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": prompt}]
                }
            ]
        },
        timeout=30
    )

    if response.status_code != 200:
        raise HTTPException(
            status_code=500,
            detail=f"Gemini API error: {response.text}"
        )

    data = response.json()

    try:
        text = data["candidates"][0]["content"]["parts"][0]["text"]
    except (KeyError, IndexError):
        raise HTTPException(
            status_code=500,
            detail="Invalid response from Gemini"
        )

    return text.strip()


@app.post("/ai-check", response_model=AIResponse)
def ai_check(payload: AIRequest):
    ai_text = call_gemini(payload.text_to_ai)

    found = payload.word_to_check.lower() in ai_text.lower()

    return AIResponse(
        ai_response=ai_text,
        word_to_check=payload.word_to_check,
        found=found
    )
