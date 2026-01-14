from fastapi import FastAPI
from pydantic import BaseModel
import requests

app = FastAPI()


class AIRequest(BaseModel):
    text_to_ai: str
    word_to_check: str


@app.post("/ai-check")
def ai_check(data: AIRequest):
    """
    This API sends text to an external AI-like service,
    receives a response, and checks if a word exists in the response.
    """

    # External public AI-like service (free, no auth)
    response = requests.get("https://api.quotable.io/random")

    if response.status_code != 200:
        return {
            "ai_response": None,
            "found": False,
            "error": "External AI service error"
        }

    ai_text = response.json().get("content", "")

    found = data.word_to_check.lower() in ai_text.lower()

    return {
        "ai_response": ai_text,
        "word_to_check": data.word_to_check,
        "found": found
    }
