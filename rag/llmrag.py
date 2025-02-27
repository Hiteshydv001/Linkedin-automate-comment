import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

def get_llm_response(prompt):
    """Generate response from Gemini API."""
    headers = {
        "Content-Type": "application/json"
    }
    # Using gemini-1.5-pro, a valid model for generateContent
    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-pro:generateContent?key={GEMINI_API_KEY}"
    data = {
        "contents": [{
            "parts": [{"text": prompt}]
        }],
        "generationConfig": {
            "maxOutputTokens": 150,
            "temperature": 0.7,
            "topP": 1.0
        }
    }
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        return response.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
    else:
        raise Exception(f"Error: {response.status_code}, {response.text}")