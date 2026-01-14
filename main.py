from fastapi import FastAPI
from pydantic import BaseModel
import requests
import os

app = FastAPI()

# Hugging Face settings
HUGGINGFACE_API_KEY = os.getenv("HF_API_KEY")
MODEL_URL = "https://api-inference.huggingface.co/models/google/flan-t5-base"

headers = {
    "Authorization": f"Bearer {HUGGINGFACE_API_KEY}"
}

# Request body schema
class AIRequest(BaseModel):
    text_to_ai: str
    word_to_check: str


@app.post("/ai-check")
def ai_check(data: AIRequest):
    payload = {
        "inputs": data.text_to_ai
    }

    response = requests.post(MODEL_URL, headers=headers, json=payload)

    # Try to parse response as JSON
    try:
        result = response.json()
    except Exception:
        return {
            "ai_response": None,
            "word_to_check": data.word_to_check,
            "found": False,
            "error": "Invalid response from AI service"
        }

    # Handle non-200 responses (model loading / errors)
    if response.status_code != 200:
        return {
            "ai_response": None,
            "word_to_check": data.word_to_check,
            "found": False,
            "error": result
        }

    # Handle different Hugging Face response formats
    if isinstance(result, list) and len(result) > 0 and "generated_text" in result[0]:
        ai_text = result[0]["generated_text"]
    elif isinstance(result, dict) and "generated_text" in result:
        ai_text = result["generated_text"]
    else:
        return {
            "ai_response": None,
            "word_to_check": data.word_to_check,
            "found": False,
            "error": result
        }

    # Check if the word exists in AI response
    found = data.word_to_check.lower() in ai_text.lower()

    return {
        "ai_response": ai_text,
        "word_to_check": data.word_to_check,
        "found": found
    }
