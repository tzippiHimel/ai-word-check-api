from fastapi import FastAPI
from pydantic import BaseModel
import requests
import os

app = FastAPI()

HF_API_KEY = os.getenv("HF_API_KEY")

API_URL = "https://router.huggingface.co/v1/completions"

HEADERS = {
    "Authorization": f"Bearer {HF_API_KEY}",
    "Content-Type": "application/json"
}

MODEL_NAME = "google/flan-t5-small"


class AIRequest(BaseModel):
    text_to_ai: str
    word_to_check: str


@app.post("/ai-check")
def ai_check(data: AIRequest):
    payload = {
        "model": MODEL_NAME,
        "prompt": data.text_to_ai,
        "max_tokens": 200,
        "temperature": 0.7
    }

    response = requests.post(
        API_URL,
        headers=HEADERS,
        json=payload,
        timeout=30
    )

    try:
        result = response.json()
    except Exception:
        return {
            "ai_response": None,
            "found": False,
            "error": "Invalid response from Hugging Face Router"
        }

    if response.status_code != 200:
        return {
            "ai_response": None,
            "found": False,
            "hf_response": result
        }

    try:
        ai_text = result["choices"][0]["text"]
    except Exception:
        return {
            "ai_response": None,
            "found": False,
            "hf_response": result
        }

    found = data.word_to_check.lower() in ai_text.lower()

    return {
        "ai_response": ai_text,
        "word_to_check": data.word_to_check,
        "found": found
    }
