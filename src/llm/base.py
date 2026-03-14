from __future__ import annotations
from dataclasses import dataclass
from typing import Optional

@dataclass
class LLMResponse:
    text: str

class LLMClient:
    def complete(self, system: str, user: str, temperature: float = 0.2) -> LLMResponse:
        raise NotImplementedError
