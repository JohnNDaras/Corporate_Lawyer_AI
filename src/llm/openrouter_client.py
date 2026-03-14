import os
import requests
from dataclasses import dataclass
from .base import LLMClient


@dataclass
class ORResponse:
    text: str


class OpenRouterClient(LLMClient):

    def __init__(self, model_id="meta-llama/llama-3-8b-instruct"):

        api_key = os.environ.get("OPENROUTER_API_KEY")

        if not api_key:
            raise ValueError("OPENROUTER_API_KEY not set")

        self.model_id = model_id
        self.api_key = api_key
        self.url = "https://openrouter.ai/api/v1/chat/completions"

    def complete(self, system: str, user: str, temperature: float = 0.2):

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": self.model_id,
            "temperature": temperature,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user}
            ],
        }

        response = requests.post(self.url, headers=headers, json=payload)

        if response.status_code != 200:
            raise RuntimeError(f"OpenRouter error: {response.text}")

        data = response.json()

        text = data["choices"][0]["message"]["content"]

        return ORResponse(text=text)