from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests
import os

app = FastAPI()

HUGGINGFACE_API_KEY = os.getenv("HF_API_KEY")
MODEL_URL = "https://api-inference.huggingface.co/models/google/flan-t5-base"

headers = {
    "Authorization": f"Bearer {HUGGINGFACE_API_KEY}"
}

class AIRequest(BaseModel):
    text_to_ai: str
    word_to_check: str


@app.post("/ai-check")
def ai_check(data: AIRequest):
    payload = {
        "inputs": data.text_to_ai
    }

    response = requests.post(MODEL_URL, headers=headers, json=payload)

    if response.status_code != 200:
        raise HTTPException(status_code=500, detail="AI service error")

    ai_text = response.json()[0]["generated_text"]

    found = data.word_to_check.lower() in ai_text.lower()

    return {
        "ai_response": ai_text,
        "word_to_check": data.word_to_check,
        "found": found
    }
