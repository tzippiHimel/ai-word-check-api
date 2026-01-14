from fastapi import FastAPI
from pydantic import BaseModel
import requests
import os

app = FastAPI()

HF_API_KEY = os.getenv("HF_API_KEY")

# ✅ NEW Hugging Face router endpoint
MODEL_URL = "https://router.huggingface.co/v1/models/bigscience/bloom-560m"

HEADERS = {
    "Authorization": f"Bearer {HF_API_KEY}",
    "Content-Type": "application/json"
}


class AIRequest(BaseModel):
    text_to_ai: str
    word_to_check: str


@app.post("/ai-check")
def ai_check(data: AIRequest):
    payload = {
        "inputs": data.text_to_ai
    }

    try:
        response = requests.post(
            MODEL_URL,
            headers=HEADERS,
            json=payload,
            timeout=30
        )
    except Exception as e:
        return {
            "ai_response": None,
            "found": False,
            "error": str(e)
        }

    try:
        result = response.json()
    except Exception:
        return {
            "ai_response": None,
            "found": False,
            "error": "Invalid JSON from Hugging Face"
        }

    # Hugging Face error / model loading
    if response.status_code != 200:
        return {
            "ai_response": None,
            "found": False,
            "hf_response": result
        }

    # Extract generated text safely
    if isinstance(result, list) and len(result) > 0:
        ai_text = result[0].get("generated_text", "")
    elif isinstance(result, dict):
        ai_text = result.get("generated_text", "")
    else:
        ai_text = ""

    found = data.word_to_check.lower() in ai_text.lower()

    return {
        "ai_response": ai_text,
        "word_to_check": data.word_to_check,
        "found": found
    }
