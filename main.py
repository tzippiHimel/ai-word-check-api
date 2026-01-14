from fastapi import FastAPI
from pydantic import BaseModel
import requests
import os

app = FastAPI()

HF_API_KEY = os.getenv("HF_API_KEY")

MODEL_URL = "https://api-inference.huggingface.co/models/google/flan-t5-small"

HEADERS = {
    "Authorization": f"Bearer {HF_API_KEY}"
}


class AIRequest(BaseModel):
    text_to_ai: str
    word_to_check: str


@app.post("/ai-check")
def ai_check(data: AIRequest):
    payload = {
        "inputs": data.text_to_ai
    }

    response = requests.post(
        MODEL_URL,
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
            "error": "Invalid response from AI service"
        }

    # Handle model loading or errors
    if isinstance(result, dict) and "error" in result:
        return {
            "ai_response": None,
            "found": False,
            "ai_status": result["error"]
        }

    # Expected format: list of generated_text
    if isinstance(result, list) and len(result) > 0:
        ai_text = result[0].get("generated_text", "")
    else:
        ai_text = ""

    found = data.word_to_check.lower() in ai_text.lower()

    return {
        "ai_response": ai_text,
        "word_to_check": data.word_to_check,
        "found": found
    }
