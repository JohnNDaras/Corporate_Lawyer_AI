# src/llm/hf_client.py

import os
from dataclasses import dataclass
from typing import Optional

from huggingface_hub import InferenceClient

from .base import LLMClient, LLMResponse


@dataclass
class HuggingFaceClient(LLMClient):
    """
    Hugging Face LLM client using huggingface_hub.InferenceClient.
    This avoids hardcoding deprecated endpoints and lets HF handle routing/providers.

    Notes:
    - provider="hf-inference" uses HF's serverless inference (not all models are available there).
    - If you want HF to choose any available provider, set provider="auto" (may require billing/provider access).
    """
    model_id: str = "HuggingFaceTB/SmolLM3-3B"
    provider: str = "hf-inference"
    timeout: int = 90
    max_tokens: int = 900

    def __post_init__(self):
        token = os.getenv("HUGGINGFACEHUB_API_TOKEN")
        if not token:
            raise ValueError("HUGGINGFACEHUB_API_TOKEN not set")

        self.client = InferenceClient(
            provider=self.provider,
            token=token,
            timeout=float(self.timeout),
        )

    def complete(self, system: str, user: str, temperature: float = 0.2) -> LLMResponse:
        # Prefer chat-completion API (OpenAI-compatible), which many instruction models support.
        # Docs: InferenceClient.chat_completion / client.chat.completions.create
        # https://huggingface.co/docs/huggingface_hub/en/package_reference/inference_client
        try:
            out = self.client.chat_completion(
                model=self.model_id,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
                max_tokens=int(self.max_tokens),
                temperature=float(temperature),
            )
            text = out.choices[0].message.content or ""
            return LLMResponse(text=text.strip())
        except Exception as e_chat:
            # Fallback to text_generation (some models only expose this)
            try:
                prompt = self._format_prompt(system, user)
                text = self.client.text_generation(
                    prompt=prompt,
                    model=self.model_id,
                    max_new_tokens=int(self.max_tokens),
                    temperature=float(temperature),
                    return_full_text=False,
                )
                return LLMResponse(text=str(text).strip())
            except Exception as e_tg:
                # Raise a clean combined error for Streamlit to display
                raise RuntimeError(
                    f"HF inference failed for model='{self.model_id}', provider='{self.provider}'. "
                    f"chat_completion error: {e_chat} | text_generation error: {e_tg}"
                )

    @staticmethod
    def _format_prompt(system: str, user: str) -> str:
        # Simple instruct-style prompt for text_generation fallback.
        return f"""<s>[INST] <<SYS>>
{system}
<</SYS>>

{user}
[/INST]"""
