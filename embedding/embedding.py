import os
import requests

def get_gemini_embedding(text):
    API_KEY = os.environ["GEMINI_API_KEY"]
    MODEL = "models/embedding-001"
    ENDPOINT = f"https://generativelanguage.googleapis.com/v1beta/{MODEL}:embedContent?key={API_KEY}"

    payload = {
        "content": {"parts": [{"text": text}]},
        "taskType": "RETRIEVAL_DOCUMENT"
    }
    response = requests.post(ENDPOINT, json=payload)
    response.raise_for_status()
    return response.json()['embedding']['values']
